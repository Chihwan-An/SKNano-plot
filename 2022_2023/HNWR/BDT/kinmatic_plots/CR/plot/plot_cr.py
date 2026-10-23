#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
from array import array
from pathlib import Path

import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.TH1.AddDirectory(False)

INPUT_BASE = Path("/gv0/Users/achihwan/SKNanoOutput/HNWR_BDT_presel")
DEFAULT_ERAS = ("2022", "2022EE", "2023", "2023BPix")
DEFAULT_LUMI_LABEL = "62.31 fb^{-1} (13.6 TeV)"

CHANNEL_SELECTION = {
    "EE": ("channel == 0", ("EGamma",)),
    "MM": ("channel == 1", ("Muon", "SingleMuon")),
    "all": ("1", ("EGamma", "Muon", "SingleMuon")),
}

BACKGROUND_GROUPS = (
    ("DYJets", ROOT.kYellow, "Drell-Yan"),
    ("TT", ROOT.kRed, "t#bar{t}+single top"),
    ("Nonprompt", ROOT.kGreen + 2, "Nonprompt"),
    ("Others", ROOT.kBlue, "Others"),
)

PLOT_CONFIGS = {
    "mll": {
        "branch": "mll",
        "label": "m(ll) [GeV]",
        "edges": [0, 20, 40, 60, 70, 80, 90, 100, 110, 120, 140, 160, 200],
        "rmin": 0.0,
        "rmax": 2.0,
    },
    "mlljj": {
        "branch": "mlljj",
        "label": "m(lljj) [GeV]",
        "edges": [800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 4000],
        "rmin": 0.0,
        "rmax": 2.0,
    },
    "mlfatjet": {
        "branch": "ml1fatjet",
        "label": "m(lJ) [GeV]",
        "edges": [800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 4000],
        "rmin": 0.0,
        "rmax": 2.0,
    },
}

VARS_BY_CATEGORY = {
    "resolved": ("mll", "mlljj"),
    "boosted": ("mll", "mlfatjet"),
}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Draw HNWR BDT CR data/simulation comparison plots from nominal Central trees."
    )
    parser.add_argument("--input-base", type=Path, default=INPUT_BASE)
    parser.add_argument("--outdir", type=Path, default=Path(__file__).resolve().parent / "plots")
    parser.add_argument("--eras", nargs="+", default=list(DEFAULT_ERAS))
    parser.add_argument("--channel", choices=["EE", "MM", "all", "both"], default="both")
    parser.add_argument("--cr", choices=["DY", "FLV", "both"], default="both")
    parser.add_argument("--category", choices=["resolved", "boosted", "both"], default="both")
    parser.add_argument("--variables", nargs="+", default=None, help="Override variables, e.g. mll mlljj.")
    parser.add_argument("--lumi-label", default=DEFAULT_LUMI_LABEL)
    parser.add_argument("--linear", action="store_true", help="Use linear y-axis instead of log y.")
    parser.add_argument("--formats", default="png,pdf", help="Comma-separated output formats.")
    return parser.parse_args()


def sample_group(name: str) -> str:
    if name.startswith("DY"):
        return "DYJets"
    if name.startswith("TT") or name.startswith("ST"):
        return "TT"
    if name.startswith("WJet"):
        return "Nonprompt"
    return "Others"


def data_files(era_dir: Path, tags: tuple[str, ...]) -> list[Path]:
    data_dir = era_dir / "data"
    if not data_dir.exists():
        return []
    out = []
    for path in sorted(data_dir.glob("*.root")):
        if any(path.name.startswith(tag) for tag in tags):
            out.append(path)
    return out


def mc_files(era_dir: Path) -> list[Path]:
    return sorted(path for path in era_dir.glob("*.root") if not path.name.startswith("WR"))


def empty_hist(name: str, edges: list[float]) -> ROOT.TH1D:
    hist = ROOT.TH1D(name, "", len(edges) - 1, array("d", edges))
    hist.Sumw2()
    hist.SetDirectory(ROOT.gROOT)
    ROOT.SetOwnership(hist, False)
    return hist


def fold_overflow(hist: ROOT.TH1) -> None:
    nbins = hist.GetNbinsX()
    cont = hist.GetBinContent(nbins) + hist.GetBinContent(nbins + 1)
    err = math.hypot(hist.GetBinError(nbins), hist.GetBinError(nbins + 1))
    hist.SetBinContent(nbins, cont)
    hist.SetBinError(nbins, err)
    hist.SetBinContent(nbins + 1, 0.0)
    hist.SetBinError(nbins + 1, 0.0)


def draw_file_hist(
    path: Path,
    tree_name: str,
    branch: str,
    edges: list[float],
    selection: str,
    weight_expr: str,
) -> ROOT.TH1D | None:
    root_file = ROOT.TFile.Open(str(path))
    if not root_file or root_file.IsZombie():
        return None
    tree = root_file.Get(tree_name)
    if not tree or not tree.GetListOfBranches().FindObject(branch):
        root_file.Close()
        return None

    hist = empty_hist(f"h_{path.stem}_{tree_name}_{branch}_{ROOT.TUUID().AsString()[:8]}", edges)
    draw_expr = f"{branch}>>{hist.GetName()}"
    cut = f"({weight_expr}) * ({selection})"
    ROOT.gROOT.cd()
    tree.Draw(draw_expr, cut, "goff")
    fold_overflow(hist)
    hist.SetDirectory(0)
    root_file.Close()
    return hist


def add_hist(total: ROOT.TH1D | None, hist: ROOT.TH1D, name: str) -> ROOT.TH1D:
    if total is None:
        total = hist.Clone(name)
        total.SetDirectory(0)
        ROOT.SetOwnership(total, False)
    else:
        total.Add(hist)
    return total


def build_inputs(
    input_base: Path,
    eras: list[str],
    channel: str,
    cr: str,
    category: str,
    variable: str,
) -> tuple[ROOT.TH1D | None, dict[str, ROOT.TH1D | None], list[tuple[str, str, float]]]:
    cfg = PLOT_CONFIGS[variable]
    # The flavor channel is now encoded in the tree name. Same-flavor CRs (DY) use
    # the EE/MM tag directly; the opposite-flavor CR (FLV) tags by leading-lepton
    # flavor: EE -> lead electron (EM), MM -> lead muon (ME). "all" spans both
    # trees (the events are disjoint, so the per-file histograms simply add).
    if cr == "FLV":
        tag_map = {"EE": ["EM"], "MM": ["ME"], "all": ["EM", "ME"]}
    else:
        tag_map = {"EE": ["EE"], "MM": ["MM"], "all": ["EE", "MM"]}
    tree_names = [f"CR_{cr}_{tag}_BDTTree_{category}" for tag in tag_map[channel]]
    selection, data_tags = CHANNEL_SELECTION[channel]
    group_hists = {key: None for key, _, _ in BACKGROUND_GROUPS}
    h_data = None
    summary_rows = []

    def file_hist(path, weight_expr):
        """Sum the per-file histogram over all flavor-tagged trees for this bin."""
        total = None
        for tname in tree_names:
            h = draw_file_hist(path, tname, cfg["branch"], cfg["edges"], selection, weight_expr)
            if not h:
                continue
            total = add_hist(total, h, f"h_{path.stem}_{tname}")
        return total

    for era in eras:
        era_dir = input_base / era
        if not era_dir.exists():
            print(f"  ! missing era directory: {era_dir}")
            continue

        for path in data_files(era_dir, data_tags):
            hist = file_hist(path, "1.0")
            if not hist:
                continue
            h_data = add_hist(h_data, hist, "h_data")
            summary_rows.append((era, path.name, hist.Integral()))

        for path in mc_files(era_dir):
            hist = file_hist(path, "weight")
            if not hist:
                continue
            group = sample_group(path.name)
            group_hists[group] = add_hist(group_hists[group], hist, f"h_{group}")
            summary_rows.append((era, path.name, hist.Integral()))

    return h_data, group_hists, summary_rows


def total_mc(group_hists: dict[str, ROOT.TH1D | None]) -> ROOT.TH1D | None:
    total = None
    for key, _, _ in BACKGROUND_GROUPS:
        hist = group_hists.get(key)
        if not hist:
            continue
        total = add_hist(total, hist, "h_total_mc")
    return total


def stat_band(hist: ROOT.TH1D, ratio: bool = False) -> ROOT.TGraphAsymmErrors:
    graph = ROOT.TGraphAsymmErrors(hist.GetNbinsX())
    for idx in range(1, hist.GetNbinsX() + 1):
        x = hist.GetBinCenter(idx)
        y = hist.GetBinContent(idx)
        ex = hist.GetBinWidth(idx) / 2.0
        ey = hist.GetBinError(idx)
        if ratio:
            graph.SetPoint(idx - 1, x, 1.0)
            rel = ey / y if y > 0 else 0.0
            graph.SetPointError(idx - 1, ex, ex, rel, rel)
        else:
            graph.SetPoint(idx - 1, x, y)
            graph.SetPointError(idx - 1, ex, ex, ey, ey)
    graph.SetFillColorAlpha(ROOT.kGray + 2, 0.45)
    graph.SetFillStyle(3013)
    return graph


def write_tsv(out_base: Path, h_data: ROOT.TH1D | None, h_total: ROOT.TH1D, group_hists: dict[str, ROOT.TH1D | None]) -> None:
    with out_base.with_suffix(".tsv").open("w", newline="") as handle:
        columns = [
            "bin",
            "low",
            "high",
            "data",
            "mc_total",
            "data_over_mc",
            "mc_stat",
            *[key for key, _, _ in BACKGROUND_GROUPS],
        ]
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t")
        writer.writeheader()
        for idx in range(1, h_total.GetNbinsX() + 1):
            mc = h_total.GetBinContent(idx)
            data = h_data.GetBinContent(idx) if h_data else 0.0
            row = {
                "bin": idx,
                "low": h_total.GetBinLowEdge(idx),
                "high": h_total.GetBinLowEdge(idx + 1),
                "data": data,
                "mc_total": mc,
                "data_over_mc": data / mc if mc > 0 else math.nan,
                "mc_stat": h_total.GetBinError(idx),
            }
            for key, _, _ in BACKGROUND_GROUPS:
                row[key] = group_hists[key].GetBinContent(idx) if group_hists.get(key) else 0.0
            writer.writerow(row)


def draw_plot(
    outdir: Path,
    formats: list[str],
    h_data: ROOT.TH1D | None,
    group_hists: dict[str, ROOT.TH1D | None],
    h_total: ROOT.TH1D,
    channel: str,
    cr: str,
    category: str,
    variable: str,
    eras: list[str],
    lumi_label: str,
    logy: bool,
) -> Path:
    cfg = PLOT_CONFIGS[variable]
    outdir.mkdir(parents=True, exist_ok=True)
    out_base = outdir / f"CR_{cr}_{category}_{channel}_{variable}"

    stack = ROOT.THStack("stack", "")
    stack_items = []
    for key, color, label in BACKGROUND_GROUPS:
        hist = group_hists.get(key)
        if not hist:
            continue
        hist.SetFillColor(color)
        hist.SetLineColor(ROOT.kBlack)
        hist.SetLineWidth(1)
        stack_items.append((key, hist.Integral(), hist, label))
    for _, _, hist, _ in sorted(stack_items, key=lambda item: item[1]):
        stack.Add(hist)

    uid = ROOT.TUUID().AsString()[:8]
    c = ROOT.TCanvas(f"c_{uid}", f"c_{uid}", 800, 900)
    p1 = ROOT.TPad(f"p1_{uid}", f"p1_{uid}", 0, 0.30, 1, 1)
    p2 = ROOT.TPad(f"p2_{uid}", f"p2_{uid}", 0, 0, 1, 0.30)
    p1.SetBottomMargin(0.02)
    p2.SetTopMargin(0.02)
    p2.SetBottomMargin(0.35)
    p1.Draw()
    p2.Draw()

    p1.cd()
    if logy:
        p1.SetLogy()
    frame = h_total.Clone("frame")
    frame.Reset()
    frame.SetMinimum(0.5 if logy else 0.0)
    ymax = max(h_total.GetMaximum(), h_data.GetMaximum() if h_data else 0.0)
    frame.SetMaximum(ymax * (50.0 if logy else 1.6))
    frame.GetYaxis().SetTitle("Events / bin")
    frame.GetYaxis().SetTitleSize(0.050)
    frame.GetYaxis().SetTitleOffset(1.05)
    frame.GetXaxis().SetLabelSize(0)
    frame.Draw("HIST")
    stack.Draw("HIST SAME")

    band = stat_band(h_total)
    band.Draw("SAME E2")

    if h_data:
        h_data.SetMarkerStyle(20)
        h_data.SetMarkerSize(1.1)
        h_data.SetLineColor(ROOT.kBlack)
        h_data.Draw("PE SAME")

    leg = ROOT.TLegend(0.55, 0.52, 0.92, 0.88)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.035)
    for _, _, hist, label in reversed(stack_items):
        leg.AddEntry(hist, label, "f")
    if h_data:
        leg.AddEntry(h_data, "Data", "pe")
    leg.AddEntry(band, "MC stat. unc.", "f")
    leg.Draw()

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(61)
    latex.SetTextSize(0.045)
    latex.DrawLatex(0.12, 0.93, "CMS")
    latex.SetTextFont(52)
    latex.SetTextSize(0.035)
    latex.DrawLatex(0.21, 0.93, "Work in progress")
    latex.SetTextFont(42)
    latex.SetTextSize(0.030)
    latex.SetTextAlign(31)
    latex.DrawLatex(0.90, 0.93, lumi_label)
    latex.SetTextAlign(11)
    latex.SetTextFont(62)
    latex.SetTextSize(0.055)
    latex.DrawLatex(0.18, 0.82, channel if channel != "all" else "inclusive")
    latex.SetTextFont(42)
    latex.SetTextSize(0.050)
    latex.DrawLatex(0.18, 0.75, f"{category.capitalize()} {cr} CR")
    latex.SetTextSize(0.032)
    latex.DrawLatex(0.18, 0.69, ", ".join(eras))
    p1.RedrawAxis()

    p2.cd()
    ratio_frame = h_total.Clone("ratio_frame")
    ratio_frame.Reset()
    ratio_frame.SetMinimum(cfg["rmin"])
    ratio_frame.SetMaximum(cfg["rmax"])
    ratio_frame.GetYaxis().SetTitle("Data / MC")
    ratio_frame.GetXaxis().SetTitle(cfg["label"])
    ratio_frame.GetXaxis().SetTitleSize(0.10)
    ratio_frame.GetXaxis().SetLabelSize(0.11)
    ratio_frame.GetYaxis().SetTitleSize(0.10)
    ratio_frame.GetYaxis().SetLabelSize(0.10)
    ratio_frame.GetYaxis().SetTitleOffset(0.45)
    ratio_frame.GetYaxis().SetNdivisions(505)
    ratio_frame.Draw("HIST")

    ratio_band = stat_band(h_total, ratio=True)
    ratio_band.Draw("SAME E2")
    if h_data:
        h_ratio = h_data.Clone("h_ratio")
        h_ratio.Divide(h_total)
        h_ratio.SetMarkerStyle(20)
        h_ratio.SetMarkerSize(1.0)
        h_ratio.Draw("PE SAME")
    line = ROOT.TLine(h_total.GetXaxis().GetXmin(), 1.0, h_total.GetXaxis().GetXmax(), 1.0)
    line.SetLineStyle(2)
    line.Draw()
    p2.RedrawAxis()

    write_tsv(out_base, h_data, h_total, group_hists)
    for fmt in formats:
        c.SaveAs(str(out_base.with_suffix(f".{fmt}")))
    c.Close()
    print(f"Wrote {out_base}.{{{','.join(formats)}}}")
    return out_base


def expand(value: str, options: tuple[str, ...]) -> list[str]:
    return list(options) if value == "both" else [value]


def main() -> None:
    args = parse_args()
    channels = expand(args.channel, ("EE", "MM"))
    crs = expand(args.cr, ("DY", "FLV"))
    categories = expand(args.category, ("resolved", "boosted"))
    formats = [item.strip().lstrip(".") for item in args.formats.split(",") if item.strip()]

    for channel in channels:
        for cr in crs:
            for category in categories:
                variables = args.variables if args.variables else VARS_BY_CATEGORY[category]
                for variable in variables:
                    if variable not in PLOT_CONFIGS:
                        raise SystemExit(f"Unknown variable {variable}; choose one of {sorted(PLOT_CONFIGS)}")
                    print(f"\n== {channel} {cr} {category} {variable} ==")
                    h_data, group_hists, _ = build_inputs(
                        args.input_base,
                        args.eras,
                        channel,
                        cr,
                        category,
                        variable,
                    )
                    h_total = total_mc(group_hists)
                    if not h_total or h_total.Integral() <= 0:
                        print("  ! no MC histogram, skip")
                        continue
                    draw_plot(
                        args.outdir,
                        formats,
                        h_data,
                        group_hists,
                        h_total,
                        channel,
                        cr,
                        category,
                        variable,
                        args.eras,
                        args.lumi_label,
                        logy=not args.linear,
                    )


if __name__ == "__main__":
    main()
