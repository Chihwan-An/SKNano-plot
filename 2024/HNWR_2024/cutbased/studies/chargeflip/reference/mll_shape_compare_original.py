#!/usr/bin/env python3
"""DY MC m_ll shape by jet category vs the resolved SR (2026-09-18): 0 jets, 1 jet, >= 2 jets with m_lljj < 800, each scaled so its
Z-peak count (80 < m_ll < 100) equals that of the resolved-SR DY (>= 2 jets, dR cuts, m_lljj > 800); lower pad = category / SR per bin.
DY = cfboost HNWR_ChargeFlip dumps (two tight leptons pT > 60/53, cleaned AK4 jets pT > 40, lumi-weighted).
    mll_shape_compare.py [--out-dir <plots>] [--peak 80,100]"""
import argparse, glob, os
import numpy as np
import ROOT
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--dumps", default=f"{T}/data/chargeflip/dumps_boost")
ap.add_argument("--out-dir", default="/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased/out/Resolve/DY/chargeflip/AN_rawcharge/07_mll_jetbins")
ap.add_argument("--out-md", default=f"{T}/docs/mll_shape_compare_dy_2024.md")
ap.add_argument("--peak", default="80,100")
a = ap.parse_args()
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); os.makedirs(a.out_dir, exist_ok=True)
EDGES = np.array([60, 70, 80, 90, 100, 110, 120, 130, 150, 175, 200, 250, 300, 400, 500, 700, 1000, 1300, 1600, 2000.])
plo, phi = [float(x) for x in a.peak.split(",")]
dy = {}
for p in sorted(glob.glob(f"{a.dumps}/tree_Skim_HNWR_DYto2L*.npz")):
    z = np.load(p)
    for k in ("channel", "hasPair", "nJet", "m_l1l2", "weight", "passResolved", "m_lljj"): dy.setdefault(k, []).append(z[k])
dy = {k: np.concatenate(v) for k, v in dy.items()}
base = dy["hasPair"] > 0
CATS = {"SR": (lambda d: (d["nJet"] >= 2) & (d["passResolved"] > 0) & (d["m_lljj"] > 800), "resolved SR (#geq2 jets, m_{lljj} > 800)", ROOT.kBlack),
        "2j": (lambda d: (d["nJet"] >= 2) & (d["passResolved"] > 0) & (d["m_lljj"] < 800), "#geq2 jets, m_{lljj} < 800", ROOT.kRed + 1),
        "1j": (lambda d: d["nJet"] == 1, "1 jet", ROOT.kGreen + 2),
        "0j": (lambda d: d["nJet"] == 0, "0 jets", ROOT.kMagenta + 1)}
L = ["# DY MC m_ll shape by jet category vs the resolved SR (2024)", "",
     f"Each category is scaled so that its Z-peak count ({plo:.0f} < m_ll < {phi:.0f}) equals the resolved-SR DY count; ratio = scaled category / SR per bin (stat errors of both).", ""]
for ch, chid in (("EE", 11), ("MM", 13)):
    H = {}; E = {}
    for k, (cut, lab, col) in CATS.items():
        m = base & (dy["channel"] == chid) & cut(dy)
        H[k], _ = np.histogram(dy["m_l1l2"][m], EDGES, weights=dy["weight"][m]); E[k], _ = np.histogram(dy["m_l1l2"][m], EDGES, weights=dy["weight"][m] ** 2)
    pk = (EDGES[:-1] >= plo) & (EDGES[1:] <= phi)
    ref = H["SR"][pk].sum()
    scale = {k: ref / H[k][pk].sum() for k in CATS}
    L += [f"## {ch}", "", "scale (SR peak / category peak): " + ", ".join(f"{k} x{scale[k]:.4g}" for k in CATS if k != "SR"),
          "raw totals 60-2000: " + ", ".join(f"{k} {H[k].sum():.0f}" for k in CATS), "",
          "| m_ll | SR | " + " | ".join(f"{k} scaled | {k}/SR" for k in CATS if k != "SR") + " |", "|---|---|" + "---|---|" * 3]
    for i in range(len(EDGES) - 1):
        cells = []
        for k in ("2j", "1j", "0j"):
            v = H[k][i] * scale[k]; r = v / H["SR"][i] if H["SR"][i] > 0 else float("nan")
            re = r * np.sqrt((E[k][i] / H[k][i] ** 2 if H[k][i] > 0 else 0) + (E["SR"][i] / H["SR"][i] ** 2 if H["SR"][i] > 0 else 0)) if H["SR"][i] > 0 else float("nan")
            cells.append(f"{v:.1f} | {r:.2f} ± {re:.2f}")
        L.append(f"| {EDGES[i]:.0f}-{EDGES[i+1]:.0f} | {H['SR'][i]:.1f} ± {np.sqrt(E['SR'][i]):.1f} | " + " | ".join(cells) + " |")
    L.append("")
    # plot: upper shapes, lower ratios
    c = ROOT.TCanvas("c", "c", 800, 800)
    p1 = ROOT.TPad("p1", "", 0, 0.32, 1, 1); p1.SetBottomMargin(0.02); p1.SetLogx(); p1.SetLogy(); p1.Draw()
    p2 = ROOT.TPad("p2", "", 0, 0, 1, 0.32); p2.SetTopMargin(0.03); p2.SetBottomMargin(0.3); p2.SetLogx(); p2.SetLogy(); p2.Draw()
    p1.cd(); keep = []; leg = ROOT.TLegend(0.42, 0.62, 0.88, 0.88); leg.SetTextSize(0.03)
    hists = {}
    for k, (cut, lab, col) in CATS.items():
        h = ROOT.TH1D(f"h_{ch}_{k}", f"{ch} DY MC, Z-peak normalised to the resolved SR;;events / bin", len(EDGES) - 1, EDGES)
        for i in range(len(EDGES) - 1): h.SetBinContent(i + 1, H[k][i] * scale[k]); h.SetBinError(i + 1, np.sqrt(E[k][i]) * scale[k])
        h.SetLineColor(col); h.SetLineWidth(2 if k != "SR" else 3); h.SetMarkerColor(col); hists[k] = h
    hists["SR"].SetMinimum(1e-2); hists["SR"].SetMaximum(max(H[k].max() * scale[k] for k in CATS) * 50); hists["SR"].GetXaxis().SetLabelSize(0)
    hists["SR"].Draw("hist e"); leg.AddEntry(hists["SR"], CATS["SR"][1], "l")
    for k in ("2j", "1j", "0j"): hists[k].Draw("hist e same"); leg.AddEntry(hists[k], f"{CATS[k][1]} (x{scale[k]:.3g})", "l")
    leg.Draw()
    p2.cd(); first = True
    for k in ("2j", "1j", "0j"):
        r = hists[k].Clone(f"r_{ch}_{k}"); r.Divide(hists["SR"]); r.SetTitle(";m_{ll} [GeV];category / SR")
        r.GetYaxis().SetNdivisions(505); r.GetYaxis().SetTitleSize(0.1); r.GetYaxis().SetTitleOffset(0.45); r.GetYaxis().SetLabelSize(0.08)
        r.GetXaxis().SetTitleSize(0.11); r.GetXaxis().SetLabelSize(0.09); r.SetMinimum(0.05); r.SetMaximum(20)
        r.Draw("e" + ("" if first else " same")); keep.append(r); first = False
    line = ROOT.TLine(EDGES[0], 1, EDGES[-1], 1); line.SetLineStyle(2); line.Draw()
    c.SaveAs(f"{a.out_dir}/mll_shape_{ch}.png")
open(a.out_md, "w").write("\n".join(L) + "\n"); print("\n".join(L)); print("wrote", a.out_md)
