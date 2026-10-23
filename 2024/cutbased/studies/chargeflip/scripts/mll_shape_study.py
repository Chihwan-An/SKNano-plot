#!/usr/bin/env python3
"""Portable DY mll comparison: stored nominal weight versus weight / w_dy.

First run: --dumps PATH. Later runs use the small local histogram cache, so
the entire study directory can be moved without the original event dumps.
Only DY MC is read; no collision data or OS/SS data SR is accessed.
"""
import argparse
import json
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parents[1]
EDGES = np.array([60, 70, 80, 90, 100, 110, 120, 130, 150, 175, 200,
                  250, 300, 400, 500, 700, 1000, 1300, 1600, 2000.])
ZPT = np.array([0, 50, 100, 150, 200, 300, 500, np.inf])
CATS = ("SR", "2j", "1j", "0j")
CHANNELS = ("EE", "MM")
SIGNS = ("inclusive", "OS")
MODES = ("nominal", "noDY")
PEAK = (EDGES[:-1] >= 80) & (EDGES[1:] <= 100)
COLS = ("channel", "hasPair", "nJet", "m_l1l2", "weight", "passResolved",
        "m_lljj", "w_dy", "pt_l1l2", "isSS")


def build_cache(dumps, cache):
    files = sorted(dumps.glob("tree_Skim_HNWR_DYto2L*.npz"))
    if not files:
        raise ValueError(f"No DY dumps found in {dumps}")
    # mode, sign, channel, category, reco dilepton pT bin, mll bin
    shape = (2, 2, 2, 4, len(ZPT) - 1, len(EDGES) - 1)
    hist = np.zeros(shape)
    sumw2 = np.zeros(shape)
    entries = np.zeros(shape[1:], dtype=np.int64)
    manifest = []
    for path in files:
        with np.load(path) as z:
            missing = set(COLS) - set(z.files)
            if missing:
                raise ValueError(f"{path}: missing fields {missing}")
            pair = z["hasPair"] > 0
            d = {k: np.asarray(z[k][pair]) for k in COLS}
        if not all(np.all(np.isfinite(d[k])) for k in COLS):
            raise ValueError(f"Non-finite input: {path}")
        if np.any(d["w_dy"] <= 0) or np.any(d["pt_l1l2"] < 0):
            raise ValueError(f"Missing/invalid w_dy or dilepton pT: {path}")
        weights = (d["weight"].astype(float),
                   d["weight"].astype(float) / d["w_dy"].astype(float))
        np.testing.assert_allclose(weights[1] * d["w_dy"], weights[0], rtol=1e-12)
        cuts = ((d["nJet"] >= 2) & (d["passResolved"] > 0) & (d["m_lljj"] > 800),
                (d["nJet"] >= 2) & (d["passResolved"] > 0) & (d["m_lljj"] < 800),
                d["nJet"] == 1, d["nJet"] == 0)
        # Selection remains exactly that of the original comparison, including
        # its inclusive reconstructed charge and mlljj / dR differences.
        for si in range(2):
            charge = np.ones(len(d["weight"]), dtype=bool) if si == 0 else d["isSS"] == 0
            for ci, chid in enumerate((11, 13)):
                for ki, cut in enumerate(cuts):
                    sel = (d["channel"] == chid) & charge & cut
                    x, y = d["pt_l1l2"][sel], d["m_l1l2"][sel]
                    entries[si, ci, ki] += np.histogram2d(x, y, (ZPT, EDGES))[0].astype(np.int64)
                    for wi, w in enumerate(weights):
                        ww = w[sel]
                        hist[wi, si, ci, ki] += np.histogram2d(x, y, (ZPT, EDGES), weights=ww)[0]
                        sumw2[wi, si, ci, ki] += np.histogram2d(x, y, (ZPT, EDGES), weights=ww * ww)[0]
        manifest.append(dict(file=path.name, bytes=path.stat().st_size,
                             mtime_ns=path.stat().st_mtime_ns, pairs=int(pair.sum()),
                             w_dy_min=float(d["w_dy"].min()), w_dy_max=float(d["w_dy"].max()),
                             negative_weights=int((weights[0] < 0).sum())))
        print(f"read {path.name}: {pair.sum():,} pairs", flush=True)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache, hist=hist, sumw2=sumw2, entries=entries,
                        mll_edges=EDGES, zpt_edges=ZPT)
    cache.with_suffix(".json").write_text(json.dumps(dict(
        schema=1, modes=MODES, signs=SIGNS, channels=CHANNELS, categories=CATS,
        weight_noDY="weight / w_dy; keep MC normalization, luminosity, PU and lepton SF",
        source_directory=str(dumps.resolve()),
        source_directory_is_provenance_only=True, samples=manifest), indent=2) + "\n")
    return hist, sumw2, entries


def normalize(h, v, norm_mask=PEAK):
    """Peak-normalized shape and full covariance, including the fitted peak sum."""
    p = h[norm_mask].sum()
    if p <= 0:
        return None
    vp = v[norm_mask].sum()
    cov = (np.diag(v) / p**2 + np.outer(h, h) * vp / p**4
           - (np.outer(v * norm_mask, h) + np.outer(h, v * norm_mask)) / p**3)
    return h / p, cov


def ratio(h, v, ref, refv, norm_mask=PEAK):
    a, b = normalize(h, v, norm_mask), normalize(ref, refv, norm_mask)
    r, e = np.full(len(h), np.nan), np.full(len(h), np.nan)
    if a is not None and b is not None:
        good = b[0] > 0
        r[good] = a[0][good] / b[0][good]
        e[good] = np.sqrt(np.maximum(0, np.diag(a[1])[good] / b[0][good]**2
                                     + a[0][good]**2 * np.diag(b[1])[good] / b[0][good]**4))
    return r, e


def integrated_ratio(h, v, lo, hi, norm_mask=PEAK):
    sel = (EDGES[:-1] >= lo) & (EDGES[1:] <= hi)
    a, b = normalize(h[2], v[2], norm_mask), normalize(h[0], v[0], norm_mask)
    if a is None or b is None or b[0][sel].sum() <= 0:
        return None
    av, bv = a[0][sel].sum(), b[0][sel].sum()
    va, vb = a[1][np.ix_(sel, sel)].sum(), b[1][np.ix_(sel, sel)].sum()
    return float(av / bv), float(np.sqrt(max(0, va / bv**2 + av**2 * vb / bv**4)))


def draw(ROOT, out, ch, mode, sign, ptlabel, h, v):
    out.parent.mkdir(parents=True, exist_ok=True)
    colors = (ROOT.kBlack, ROOT.kRed + 1, ROOT.kGreen + 2, ROOT.kMagenta + 1)
    labels = ("SR: #geq2 jets, m_{lljj}>800", "#geq2 jets, m_{lljj}<800", "1 jet", "0 jets")
    use_peak = h[0, PEAK].sum() > 0
    norm_mask = PEAK if use_peak else np.ones(len(PEAK), dtype=bool)
    refpeak = h[0, norm_mask].sum() if use_peak else 1.0
    if h[0, norm_mask].sum() <= 0:
        print(f"SKIP {out}: empty SR", flush=True)
        return
    if not use_peak:
        ptlabel = ptlabel.split(";")[0] + "; unit area (60-2000 GeV), empty Z peak"
    c = ROOT.TCanvas("c", "", 850, 850)
    top = ROOT.TPad("top", "", 0, .32, 1, 1)
    bot = ROOT.TPad("bot", "", 0, 0, 1, .32)
    top.SetBottomMargin(.025); top.SetTopMargin(.12); top.SetLogx(); top.SetLogy(); top.Draw()
    bot.SetTopMargin(.025); bot.SetBottomMargin(.30); bot.SetLogx(); bot.SetLogy(); bot.Draw()
    top.cd()
    leg = ROOT.TLegend(.43, .59, .89, .84); leg.SetTextSize(.027); leg.SetBorderSize(0)
    keep = []
    shapes = []
    for ki in range(4):
        norm = normalize(h[ki], v[ki], norm_mask)
        if norm is None:
            continue
        scale = refpeak / h[ki, norm_mask].sum()
        ylabel = "events / bin (Z-peak scaled)" if use_peak else "fraction / bin (60-2000 GeV)"
        hh = ROOT.TH1D(f"h_{ki}", f";;{ylabel}", len(EDGES) - 1, EDGES)
        for i in range(len(EDGES) - 1):
            hh.SetBinContent(i + 1, h[ki, i] * scale)
            # Upper panel: raw sumw2 times fixed visual scale, as in original.
            hh.SetBinError(i + 1, np.sqrt(v[ki, i]) * scale)
        hh.SetLineColor(colors[ki]); hh.SetMarkerColor(colors[ki]); hh.SetLineWidth(3 if ki == 0 else 2)
        hh.GetXaxis().SetLabelSize(0); hh.GetYaxis().SetTitleOffset(1.3)
        hh.SetMinimum(max(refpeak * 1e-7, 1e-5))
        leg.AddEntry(hh, labels[ki] + (f" (#times{scale:.3g})" if ki and use_peak else ""), "l")
        shapes.append(hh)
    shapes[0].SetMaximum(max(hh.GetMaximum() for hh in shapes) * 80)
    for i, hh in enumerate(shapes):
        hh.Draw("hist e" + (" same" if i else ""))
    leg.Draw()
    text = ROOT.TLatex(); text.SetNDC(); text.SetTextFont(42); text.SetTextSize(.033)
    mode_label = "no DY corrections" if mode == "noDY" else "nominal DY corrections"
    text.DrawLatex(.11, .94, f"{ch} DY MC, {mode_label}, {'OS+SS' if sign == 'inclusive' else 'OS only'}")
    text.SetTextSize(.028); text.DrawLatex(.11, .895, ptlabel)
    bot.cd()
    frame = ROOT.TH1D("ratio_frame", ";m_{ll} [GeV];category / SR", len(EDGES) - 1, EDGES)
    frame.SetMinimum(.05); frame.SetMaximum(20)
    frame.GetYaxis().SetNdivisions(505); frame.GetYaxis().SetTitleSize(.095)
    frame.GetYaxis().SetTitleOffset(.48); frame.GetYaxis().SetLabelSize(.08)
    frame.GetXaxis().SetTitleSize(.11); frame.GetXaxis().SetLabelSize(.09)
    frame.Draw("axis")
    for ki in range(1, 4):
        r, e = ratio(h[ki], v[ki], h[0], v[0], norm_mask)
        g = ROOT.TGraphErrors()
        for i in np.flatnonzero(np.isfinite(r) & (r > 0)):
            j = g.GetN(); g.SetPoint(j, (EDGES[i] + EDGES[i + 1]) / 2, r[i])
            g.SetPointError(j, (EDGES[i + 1] - EDGES[i]) / 2, e[i])
        g.SetLineColor(colors[ki]); g.SetMarkerColor(colors[ki]); g.SetMarkerStyle(20); g.SetMarkerSize(.55)
        g.Draw("P SAME"); keep.append(g)
    line = ROOT.TLine(EDGES[0], 1, EDGES[-1], 1); line.SetLineStyle(2); line.Draw()
    for ext in ("png", "pdf"):
        c.SaveAs(str(out.with_suffix("." + ext)))
    c.Close()


def report(path, hist, var, counts, sign, mode, ptlabel):
    lines = [f"# DY mll: {mode}, {sign}, {ptlabel}", "",
             "Categories and mll bins match the original study. Z peak: 80 <= mll < 100 GeV.",
             "SR here means >=2 jets, passResolved, mlljj > 800, with NO mll SR threshold.",
             "Ratios include weighted MC statistics and peak-normalization uncertainty/covariance.",
             "No systematic uncertainties. Undefined reference bins are reported as nan.",
             "If the SR Z peak is empty, ALL categories use unit area over 60-2000 GeV instead; explicitly marked below.", ""]
    result = {}
    for ci, ch in enumerate(CHANNELS):
        h, v = hist[ci], var[ci]
        use_peak = h[0, PEAK].sum() > 0
        norm_mask = PEAK if use_peak else np.ones(len(PEAK), dtype=bool)
        lines += [f"## {ch}", "", "Normalization: " + ("Z peak (80-100 GeV)" if use_peak else "UNIT AREA (60-2000 GeV); empty Z peak"), "", "Peak yields: " + ", ".join(f"{k}={h[i, PEAK].sum():.6g}" for i, k in enumerate(CATS)),
                  "MC entries (60-2000): " + ", ".join(f"{k}={counts[ci,i].sum()}" for i,k in enumerate(CATS)), "",
                  "| mll [GeV] | SR yield | 2j/SR | 1j/SR | 0j/SR |", "|---|---|---|---|---|"]
        ratios = [ratio(h[k], v[k], h[0], v[0], norm_mask) for k in range(1, 4)]
        for i in range(len(EDGES) - 1):
            cells = [f"{r[i]:.4f} +/- {e[i]:.4f}" for r, e in ratios]
            lines.append(f"| {EDGES[i]:g}-{EDGES[i+1]:g} | {h[0,i]:.5g} | " + " | ".join(cells) + " |")
        result[ch] = {f"{lo}_{hi}": integrated_ratio(h, v, lo, hi, norm_mask)
                      for lo, hi in ((100, 150), (150, 200), (200, 400), (400, 1000), (1000, 2000))}
        lines += ["", "Integrated 1j / SR ratios: " + json.dumps(result[ch]), ""]
    path.write_text("\n".join(lines) + "\n")
    return result


def draw_slice_overview(ROOT, dest, ch, sign, h, v):
    """One figure comparing the 1-jet/SR ratios for all valid Z-peak slices."""
    c = ROOT.TCanvas("overview", "", 950, 750)
    c.SetLogx(); c.SetLogy(); c.SetBottomMargin(.12); c.SetTopMargin(.12)
    frame = ROOT.TH1D("overview_frame", ";m_{ll} [GeV];Z-peak normalized 1 jet / SR", len(EDGES) - 1, EDGES)
    frame.SetMinimum(.05); frame.SetMaximum(20); frame.GetYaxis().SetTitleOffset(1.25)
    frame.Draw("axis")
    legend = ROOT.TLegend(.12, .66, .76, .87); legend.SetNColumns(2)
    legend.SetBorderSize(0); legend.SetTextSize(.025)
    keep = []
    colors = (ROOT.kGray + 2, ROOT.kBlue + 1, ROOT.kAzure + 7, ROOT.kGreen + 2,
              ROOT.kOrange + 7, ROOT.kRed + 1, ROOT.kMagenta + 1)
    panels = [("All p_{T}(ll)", h.sum(axis=1), v.sum(axis=1), ROOT.kBlack)]
    for zi, (lo, hi) in enumerate(zip(ZPT[:-1], ZPT[1:])):
        if h[0, zi, PEAK].sum() > 0 and h[2, zi, PEAK].sum() > 0:
            panels.append((f"p_{{T}}(ll): {lo:g}-{hi:g} GeV", h[:, zi], v[:, zi], colors[zi]))
    for ip, (label, hh, vv, color) in enumerate(panels):
        r, e = ratio(hh[2], vv[2], hh[0], vv[0])
        g = ROOT.TGraphErrors()
        for i in np.flatnonzero(np.isfinite(r) & (r > 0)):
            j = g.GetN(); g.SetPoint(j, .5 * (EDGES[i] + EDGES[i+1]), r[i])
            g.SetPointError(j, 0, e[i])
        g.SetLineColor(color); g.SetMarkerColor(color); g.SetMarkerStyle(20 + ip % 5)
        g.SetMarkerSize(.7); g.SetLineWidth(3 if ip == 0 else 2)
        if ip == 0:
            g.SetLineStyle(2)
        g.Draw("LP SAME"); legend.AddEntry(g, label, "lp"); keep.append(g)
    line = ROOT.TLine(EDGES[0], 1, EDGES[-1], 1); line.SetLineStyle(2); line.Draw()
    legend.Draw()
    text = ROOT.TLatex(); text.SetNDC(); text.SetTextFont(42); text.SetTextSize(.031)
    text.DrawLatex(.10, .94, f"{ch} DY MC, no DY corrections, {'OS+SS' if sign == 'inclusive' else 'OS only'}")
    text.SetTextSize(.023); text.DrawLatex(.10, .90, "p_{T}(ll)<50: empty Z peak, see separate unit-area plot")
    for ext in ("png", "pdf"):
        c.SaveAs(str(dest / f"mll_ratio_zpt_overview_{ch}.{ext}"))
    c.Close()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dumps", type=Path, help="Build/replace cache from explicit DY dump directory")
    ap.add_argument("--cache", type=Path, default=BASE / "data/mll_jetbins_histograms.npz")
    ap.add_argument("--out-dir", type=Path, default=BASE / "AN_rawcharge/08_mll_jetbins_noDY")
    ap.add_argument("--zpt-slices", action="store_true", help="Also draw reconstructed dilepton pT slices")
    a = ap.parse_args()
    if a.dumps:
        hist, var, counts = build_cache(a.dumps, a.cache)
    else:
        if not a.cache.exists():
            ap.error("No local cache: supply --dumps once")
        with np.load(a.cache) as z:
            np.testing.assert_array_equal(z["mll_edges"], EDGES)
            np.testing.assert_array_equal(z["zpt_edges"], ZPT)
            hist, var, counts = z["hist"], z["sumw2"], z["entries"]
    assert np.all(np.isfinite(hist)) and np.all(var >= 0)
    assert np.all(counts[0] >= counts[1])
    import ROOT
    ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.TH1.AddDirectory(False)
    summary = {}
    for mi, mode in enumerate(MODES):
        for si, sign in enumerate(SIGNS):
            dest = a.out_dir / ("nominal_check" if mode == "nominal" else "")
            if sign == "OS":
                dest = dest / "OS"
            dest.mkdir(parents=True, exist_ok=True)
            h, v, n = hist[mi, si].sum(axis=2), var[mi, si].sum(axis=2), counts[si].sum(axis=2)
            summary[f"{mode}_{sign}"] = report(dest / "ratios.md", h, v, n, sign, mode, "inclusive reco pT(ll)")
            for ci, ch in enumerate(CHANNELS):
                draw(ROOT, dest / f"mll_shape_{ch}", ch, mode, sign,
                     "All p_{T}(ll); normalize each category in 80 #leq m_{ll} < 100 GeV", h[ci], v[ci])
            if a.zpt_slices and mode == "noDY":
                for ci, ch in enumerate(CHANNELS):
                    draw_slice_overview(ROOT, dest, ch, sign, hist[mi, si, ci], var[mi, si, ci])
                for zi, (lo, hi) in enumerate(zip(ZPT[:-1], ZPT[1:])):
                    tag = f"zpt_{lo:g}to{hi:g}"
                    sub = dest / "zpt_slices" / tag; sub.mkdir(parents=True, exist_ok=True)
                    h, v, n = hist[mi, si, :, :, zi], var[mi, si, :, :, zi], counts[si, :, :, zi]
                    label = f"{lo:g} #leq reco p_{{T}}(ll) < {hi:g} GeV; Z-peak normalization in this slice"
                    summary[f"noDY_{sign}_{tag}"] = report(sub / "ratios.md", h, v, n, sign, mode, f"{lo:g} <= reco pT(ll) < {hi:g}")
                    for ci, ch in enumerate(CHANNELS):
                        draw(ROOT, sub / f"mll_shape_{ch}", ch, mode, sign, label, h[ci], v[ci])
    (a.out_dir / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: val for k, val in summary.items() if "zpt" not in k}, indent=2), flush=True)
    print(f"Finished: {a.out_dir}", flush=True)


if __name__ == "__main__":
    main()
