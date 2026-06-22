#!/usr/bin/env python3
import argparse
import math
import os
import re
from pathlib import Path

import numpy as np
import ROOT


DEFAULT_DATA_PATH = Path("/gv0/Users/achihwan/SKNanoOutput/atlas/2023")
DEFAULT_HIST = "Resolved/rCROS2mu/mlljj"
DEFAULT_SIGNALS = "WR2000N1100,WR4000N2100"

BACKGROUND_GROUPS = {
    "DYJets": (ROOT.kYellow, "Drell-Yan"),
    "TT": (ROOT.kRed, "T#bar{T}+tW"),
    "Nonprompt": (ROOT.kGreen + 2, "Nonprompt"),
    "Others": (ROOT.kBlue, "Others"),
}

SIGNAL_COLORS = [
    ROOT.kMagenta,
    ROOT.kCyan + 1,
    ROOT.kOrange + 7,
    ROOT.kViolet + 2,
    ROOT.kTeal - 1,
]

KEEPER = []


def infer_channel(hist_path):
    lower = hist_path.lower()
    if "2mu" in lower or "mumu" in lower:
        return "MM"
    if "2e" in lower or "ee" in lower:
        return "EE"
    if "emu" in lower or "mue" in lower:
        return "EMU"
    return None


def data_tokens_for_channel(channel):
    if channel == "MM":
        return ("Muon", "SingleMuon")
    if channel == "EE":
        return ("EGamma", "DoubleEG", "SingleElectron")
    return ("EGamma", "Muon", "SingleMuon", "DoubleEG", "SingleElectron")


def background_group(sample_name):
    if sample_name.startswith("DY"):
        return "DYJets"
    if sample_name.startswith("TTLL") or "tW_" in sample_name:
        return "TT"
    if sample_name.startswith("TTLJ") or sample_name.startswith("WJet"):
        return "Nonprompt"
    if sample_name.startswith("ST_tch") or sample_name.startswith("ST_sch"):
        return "Nonprompt"
    return "Others"


def is_data(sample_name):
    return any(tok in sample_name for tok in ("EGamma", "Muon", "SingleMuon", "DoubleEG", "SingleElectron"))


def is_signal(sample_name):
    return sample_name.startswith("WR")


def signal_label(sample_name, scale):
    match = re.match(r"WR(\d+)N(\d+)(EE|MM)?$", sample_name)
    if not match:
        return sample_name
    wr_tev = int(match.group(1)) / 1000.0
    n_tev = int(match.group(2)) / 1000.0
    scale_label = "" if scale == 1 else f" (#times{scale:g})"
    return f"WR {wr_tev:.1f} TeV N {n_tev:.1f} TeV{scale_label}"


def wanted_signal_names(signal_arg, channel):
    if signal_arg is None:
        signal_arg = DEFAULT_SIGNALS
    items = [s.strip() for s in signal_arg.split(",") if s.strip()]
    if not items:
        return set()
    wanted = set()
    for item in items:
        if item.endswith("EE") or item.endswith("MM"):
            wanted.add(item)
        elif channel in ("EE", "MM"):
            wanted.add(f"{item}{channel}")
        else:
            wanted.add(f"{item}EE")
            wanted.add(f"{item}MM")
    return wanted


def clone_hist(path, hist_path, x_max, custom_bins=None, rebin=1):
    f = ROOT.TFile.Open(str(path))
    if not f or f.IsZombie():
        return None
    h_orig = f.Get(f"Central/{hist_path}")
    if not h_orig:
        f.Close()
        return None

    h = h_orig.Clone(f"h_{path.stem}_{ROOT.TUUID().AsString()[:8]}")
    h.SetDirectory(0)
    ROOT.SetOwnership(h, False)

    if custom_bins is not None:
        edges = np.array(custom_bins, dtype=float)
        h = h.Rebin(len(edges) - 1, h.GetName() + "_rebin", edges)
        h.SetDirectory(0)
    elif rebin > 1:
        h.Rebin(rebin)

    f.Close()

    actual_xmax = min(x_max, h.GetXaxis().GetXmax())
    last_bin = h.FindBin(actual_xmax - 1.0e-6)
    total = 0.0
    err2 = 0.0
    for ibin in range(last_bin, h.GetNbinsX() + 2):
        total += h.GetBinContent(ibin)
        err2 += h.GetBinError(ibin) ** 2
        if ibin > last_bin:
            h.SetBinContent(ibin, 0.0)
            h.SetBinError(ibin, 0.0)
    h.SetBinContent(last_bin, total)
    h.SetBinError(last_bin, math.sqrt(err2))
    return h


def add_to_total(total, hist, name):
    if hist is None:
        return total
    if total is None:
        total = hist.Clone(name)
        total.SetDirectory(0)
    else:
        total.Add(hist)
    return total


def make_ratio(data_hist, mc_hist):
    ratio = data_hist.Clone("h_ratio")
    ratio.SetDirectory(0)
    ratio.Divide(mc_hist)
    return ratio


def make_stat_band(hist, ratio=False):
    graph = ROOT.TGraphAsymmErrors(hist.GetNbinsX())
    for ibin in range(1, hist.GetNbinsX() + 1):
        y = hist.GetBinContent(ibin)
        ey = hist.GetBinError(ibin)
        x = hist.GetBinCenter(ibin)
        ex = hist.GetBinWidth(ibin) / 2.0
        if ratio:
            graph.SetPoint(ibin - 1, x, 1.0)
            rel = ey / y if y > 0.0 else 0.0
            graph.SetPointError(ibin - 1, ex, ex, rel, rel)
        else:
            graph.SetPoint(ibin - 1, x, y)
            graph.SetPointError(ibin - 1, ex, ex, ey, ey)
    return graph


def write_yields(path, total_mc, data_hist, group_hists, signal_hists, blinded):
    with open(path, "w", encoding="utf-8") as handle:
        header = ["bin", "low", "high", "mc_total", "mc_stat", "data"]
        header.extend(BACKGROUND_GROUPS)
        header.extend(sorted(signal_hists))
        handle.write("\t".join(header) + "\n")
        for ibin in range(1, total_mc.GetNbinsX() + 1):
            row = [
                ibin,
                total_mc.GetBinLowEdge(ibin),
                total_mc.GetBinLowEdge(ibin + 1),
                total_mc.GetBinContent(ibin),
                total_mc.GetBinError(ibin),
                "BLINDED" if blinded else (data_hist.GetBinContent(ibin) if data_hist else 0.0),
            ]
            for group in BACKGROUND_GROUPS:
                row.append(group_hists[group].GetBinContent(ibin) if group_hists[group] else 0.0)
            for sig in sorted(signal_hists):
                row.append(signal_hists[sig].GetBinContent(ibin))
            handle.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x) for x in row) + "\n")


def run():
    parser = argparse.ArgumentParser(description="ATLAS-region stack plotter for atlas analyzer ROOT output.")
    parser.add_argument("--data-path", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--hist", default=DEFAULT_HIST, help="Path below Central, e.g. Resolved/rCROS2mu/mlljj")
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--output", default=None)
    parser.add_argument("--channel", choices=["EE", "MM", "EMU", "auto"], default="auto")
    parser.add_argument("--signals", default=DEFAULT_SIGNALS, help="Comma-separated WRN points; empty string disables signals")
    parser.add_argument("--signal-scale", type=float, default=1.0)
    parser.add_argument("--bins", default=None, help="Comma-separated custom bin edges")
    parser.add_argument("--rebin", type=int, default=1)
    parser.add_argument("--xmin", type=float, default=None)
    parser.add_argument("--xmax", type=float, default=None)
    parser.add_argument("--ymin", type=float, default=0.1)
    parser.add_argument("--ymax", type=float, default=None)
    parser.add_argument("--xlabel", default=None)
    parser.add_argument("--label", default=None)
    parser.add_argument("--no-logy", action="store_true")
    parser.add_argument("--rmin", type=float, default=0.5)
    parser.add_argument("--rmax", type=float, default=1.5)
    args = parser.parse_args()

    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptStat(0)

    channel = infer_channel(args.hist) if args.channel == "auto" else args.channel
    data_tokens = data_tokens_for_channel(channel)
    wanted_signals = wanted_signal_names(args.signals, channel)
    custom_bins = [float(x) for x in args.bins.split(",")] if args.bins else None

    root_files = sorted(args.data_path.glob("*.root"))
    if not root_files:
        raise SystemExit(f"No ROOT files found in {args.data_path}")

    x_min_req = args.xmin if args.xmin is not None else (custom_bins[0] if custom_bins else -1.0e30)
    x_max_req = args.xmax if args.xmax is not None else (custom_bins[-1] if custom_bins else 1.0e30)

    group_hists = {group: None for group in BACKGROUND_GROUPS}
    signal_hists = {}
    h_data = None

    print(f">> data path: {args.data_path}")
    print(f">> hist: Central/{args.hist}")
    print(f">> channel: {channel or 'unfiltered'}")

    for path in root_files:
        sample = path.stem
        if is_signal(sample):
            if sample not in wanted_signals:
                continue
            h = clone_hist(path, args.hist, x_max_req, custom_bins, args.rebin)
            if h:
                signal_hists[sample] = h
                print(f"  [SIG ] {sample:<35} {h.Integral():12.3f}")
            continue

        if is_data(sample):
            if not any(tok in sample for tok in data_tokens):
                continue
            h = clone_hist(path, args.hist, x_max_req, custom_bins, args.rebin)
            h_data = add_to_total(h_data, h, "h_data")
            if h:
                print(f"  [DATA] {sample:<35} {h.Integral():12.3f}")
            continue

        h = clone_hist(path, args.hist, x_max_req, custom_bins, args.rebin)
        if not h:
            continue
        group = background_group(sample)
        group_hists[group] = add_to_total(group_hists[group], h, f"h_{group}")
        print(f"  [MC  ] {sample:<35} {group:<10} {h.Integral():12.3f}")

    h_total_mc = None
    for group in BACKGROUND_GROUPS:
        h_total_mc = add_to_total(h_total_mc, group_hists[group], "h_total_mc")

    if h_total_mc is None:
        raise SystemExit(f"No MC histogram loaded for Central/{args.hist}")

    x_min = max(x_min_req, h_total_mc.GetXaxis().GetXmin())
    x_max = min(x_max_req, h_total_mc.GetXaxis().GetXmax())
    blinded = bool(re.search(r"(^|/)[br]SR", args.hist))

    sorted_groups = sorted(
        [(group, group_hists[group].Integral()) for group in BACKGROUND_GROUPS if group_hists[group]],
        key=lambda item: item[1],
        reverse=False,
    )

    stack = ROOT.THStack("stack", "")
    for group, _ in sorted_groups:
        h = group_hists[group]
        color = BACKGROUND_GROUPS[group][0]
        h.SetFillColor(color)
        h.SetLineColor(ROOT.kBlack)
        h.SetLineWidth(1)
        stack.Add(h)

    stat_band = make_stat_band(h_total_mc, ratio=False)
    ratio_band = make_stat_band(h_total_mc, ratio=True)
    KEEPER.extend([stack, h_total_mc, h_data, stat_band, ratio_band])

    out_name = args.output or args.hist.replace("/", "_")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_base = args.output_dir / out_name
    write_yields(out_base.with_suffix(".tsv"), h_total_mc, h_data, group_hists, signal_hists, blinded)

    canvas = ROOT.TCanvas("c", "c", 800, 900)
    pad1 = ROOT.TPad("pad1", "pad1", 0.0, 0.30, 1.0, 1.0)
    pad2 = ROOT.TPad("pad2", "pad2", 0.0, 0.00, 1.0, 0.30)
    KEEPER.extend([canvas, pad1, pad2])
    pad1.SetBottomMargin(0.02)
    pad2.SetTopMargin(0.03)
    pad2.SetBottomMargin(0.35)
    pad1.Draw()
    pad2.Draw()

    pad1.cd()
    if not args.no_logy:
        pad1.SetLogy()
    ymax = args.ymax
    if ymax is None:
        maxima = [h_total_mc.GetMaximum()]
        if h_data and not blinded:
            maxima.append(h_data.GetMaximum())
        for h in signal_hists.values():
            maxima.append(h.GetMaximum() * args.signal_scale)
        ymax = max(maxima) * (100.0 if not args.no_logy else 1.5)

    frame = h_total_mc.Clone("frame")
    frame.Reset()
    frame.GetXaxis().SetRangeUser(x_min, x_max)
    frame.GetYaxis().SetTitle("Events / bin")
    frame.GetYaxis().SetTitleSize(0.050)
    frame.GetYaxis().SetTitleOffset(1.10)
    frame.GetXaxis().SetLabelSize(0)
    frame.SetMinimum(args.ymin)
    frame.SetMaximum(ymax)
    frame.Draw("HIST")

    stack.Draw("HIST SAME")
    stat_band.SetFillColorAlpha(ROOT.kOrange, 0.55)
    stat_band.SetFillStyle(1001)
    stat_band.Draw("SAME E2")

    drawn_signals = []
    for idx, (sample, h_sig) in enumerate(sorted(signal_hists.items())):
        h_draw = h_sig.Clone(f"h_draw_{sample}")
        h_draw.SetDirectory(0)
        h_draw.Scale(args.signal_scale)
        h_draw.SetLineColor(SIGNAL_COLORS[idx % len(SIGNAL_COLORS)])
        h_draw.SetLineWidth(3)
        h_draw.SetFillStyle(0)
        h_draw.Draw("HIST SAME")
        drawn_signals.append((sample, h_draw))
        KEEPER.append(h_draw)

    if h_data and not blinded:
        h_data.SetMarkerStyle(20)
        h_data.SetMarkerSize(1.0)
        h_data.SetLineColor(ROOT.kBlack)
        h_data.Draw("PE SAME")

    legend = ROOT.TLegend(0.55, 0.52, 0.92, 0.88)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.034)
    for group, _ in reversed(sorted_groups):
        legend.AddEntry(group_hists[group], BACKGROUND_GROUPS[group][1], "f")
    legend.AddEntry(stat_band, "MC stat. unc.", "f")
    if h_data and not blinded:
        legend.AddEntry(h_data, "Data", "pe")
    for sample, h_draw in drawn_signals:
        legend.AddEntry(h_draw, signal_label(sample, args.signal_scale), "l")
    legend.Draw()
    KEEPER.append(legend)

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(61)
    latex.SetTextSize(0.045)
    latex.DrawLatex(0.12, 0.93, "CMS")
    latex.SetTextFont(52)
    latex.SetTextSize(0.035)
    latex.DrawLatex(0.21, 0.93, "Work in progress")
    latex.SetTextFont(42)
    latex.SetTextSize(0.035)
    latex.DrawLatex(0.16, 0.83, args.label or args.hist)
    if blinded:
        latex.SetTextFont(62)
        latex.DrawLatex(0.16, 0.77, "SR blinded")
    KEEPER.append(latex)
    pad1.RedrawAxis()

    pad2.cd()
    ratio_frame = frame.Clone("ratio_frame")
    ratio_frame.Reset()
    ratio_frame.GetXaxis().SetRangeUser(x_min, x_max)
    ratio_frame.GetXaxis().SetTitle(args.xlabel or args.hist.split("/")[-1])
    ratio_frame.GetYaxis().SetTitle("Data / MC")
    ratio_frame.SetMinimum(args.rmin)
    ratio_frame.SetMaximum(args.rmax)
    ratio_frame.GetXaxis().SetTitleSize(0.105)
    ratio_frame.GetXaxis().SetLabelSize(0.105)
    ratio_frame.GetYaxis().SetTitleSize(0.095)
    ratio_frame.GetYaxis().SetLabelSize(0.095)
    ratio_frame.GetYaxis().SetTitleOffset(0.48)
    ratio_frame.GetYaxis().SetNdivisions(505)
    ratio_frame.Draw("HIST")

    ratio_band.SetFillColorAlpha(ROOT.kOrange, 0.55)
    ratio_band.SetFillStyle(1001)
    ratio_band.Draw("SAME E2")
    if h_data and not blinded:
        ratio = make_ratio(h_data, h_total_mc)
        ratio.SetMarkerStyle(20)
        ratio.Draw("PE SAME")
        KEEPER.append(ratio)
    else:
        blinder = ROOT.TLatex()
        blinder.SetNDC()
        blinder.SetTextAlign(22)
        blinder.SetTextFont(62)
        blinder.SetTextSize(0.16)
        blinder.DrawLatex(0.50, 0.52, "Blinded")
        KEEPER.append(blinder)
    line = ROOT.TLine(x_min, 1.0, x_max, 1.0)
    line.SetLineStyle(2)
    line.Draw()
    KEEPER.append(line)
    pad2.RedrawAxis()

    canvas.SaveAs(str(out_base.with_suffix(".png")))
    canvas.SaveAs(str(out_base.with_suffix(".pdf")))
    print(f">> saved: {out_base}.png/.pdf/.tsv")


if __name__ == "__main__":
    run()
