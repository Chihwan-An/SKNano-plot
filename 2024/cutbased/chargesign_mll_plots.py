#!/usr/bin/env python3
"""m(ll) of the resolved EE SR split by charge sign (SS e+e+, SS e-e-, OS leading e+, OS leading e-), like the
SRChargeSplit m(lljj) plots in out/Resolve/sig_chargesign/EE/other/Inclusive, but from the HNWR_ChargeFlip trees
(cfboost dumps: full background set + W_R signal points; weight = MC x lumi x PU x DY corr x lepton SF). Data blinded.
    chargesign_mll_plots.py [--dumps data/chargeflip/dumps_boost] [--out out/Resolve/sig_chargesign/EE/other] [--mm]"""
import argparse, glob, os, sys
import numpy as np
import ROOT
PC = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(PC, "../../BDT/SR/test")
sys.path.insert(0, os.path.join(T, "scripts")); import chargeflip_ddss as dd
ap = argparse.ArgumentParser()
ap.add_argument("--dumps", default=f"{T}/data/chargeflip/dumps_boost")
ap.add_argument("--out", default=f"{PC}/out/Resolve/sig_chargesign/EE/other")
ap.add_argument("--signals", default="MWR4000_N2000,MWR4000_N200,MWR6000_N200,MWR6000_N3000")
a = ap.parse_args()
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0)
KEYS = ["channel", "weight", "isSS", "passResolved", "m_l1l2", "m_lljj", "hasPair"] + [f"l{i}_{v}" for i in (1, 2) for v in ("charge", "pt", "scEta", "genCharge", "genChargeIdx")]
d = dd.load(a.dumps, keys=KEYS)
sample = np.array([os.path.basename(p) for p in sorted(glob.glob(f"{a.dumps}/tree_*.npz"))])
# dd.load concatenates per file in sorted order; rebuild the per-row sample name from the per-file row counts
counts = []
for p in sorted(glob.glob(f"{a.dumps}/tree_*.npz")):
    z = np.load(p); counts.append(int((z["channel"] == 11).sum()))
smp = np.repeat(sample, counts); assert len(smp) == len(d["channel"])
sel = (d["hasPair"] > 0) & (d["passResolved"] > 0) & (d["m_l1l2"] > 400) & (d["m_lljj"] > 800)
q1, q2 = d["l1_charge"], d["l2_charge"]
CATS = {"SSpp": (sel & (q1 > 0) & (q2 > 0), "SS e^{+}e^{+}"), "SSmm": (sel & (q1 < 0) & (q2 < 0), "SS e^{-}e^{-}"),
        "OSleadP": (sel & (q1 * q2 < 0) & (q1 > 0), "OS, leading e^{+}"), "OSleadM": (sel & (q1 * q2 < 0) & (q1 < 0), "OS, leading e^{-}")}
GROUPS = [("TT", "T#bar{T}+tW", ROOT.kRed), ("DYJets", "Drell-Yan", ROOT.kYellow), ("Others", "Others", ROOT.kBlue), ("Nonprompt", "Nonprompt", ROOT.kGreen + 2)]
grp = np.array([dd.GROUP.get(dd.group_of(s), "x") for s in smp]); issig = np.char.find(smp.astype(str), "WRtoN") >= 0; grp[issig] = "SIG"
EDGES = np.array([400, 450, 500, 600, 700, 800, 1000, 1200, 1500, 2000, 3000.])
SIGS = [(s, ["kBlack", "kMagenta+1", "kBlue+1", "kGreen+3"][i]) for i, s in enumerate(a.signals.split(","))]
lines = ["| category | TT | DY | Others | Nonprompt | total MC | " + " | ".join(s for s, _ in SIGS) + " |", "|---|---|---|---|---|---|" + "---|" * len(SIGS)]
for cat, (m, lab) in CATS.items():
    outdir = os.path.join(a.out, cat); os.makedirs(outdir, exist_ok=True)
    c = ROOT.TCanvas("c", "c", 800, 800); c.SetLogy(); c.SetLeftMargin(0.12)
    st = ROOT.THStack("st", ""); keep = []; leg = ROOT.TLegend(0.50, 0.58, 0.89, 0.89); leg.SetTextSize(0.028); leg.SetBorderSize(0)
    tot = np.zeros(len(EDGES) - 1); yields = {}
    for g, glab, col in GROUPS:
        mm = m & (grp == g); v, _ = np.histogram(d["m_l1l2"][mm], EDGES, weights=d["weight"][mm]); tot += v; yields[g] = v.sum()
        h = ROOT.TH1D(f"h_{cat}_{g}", "", len(EDGES) - 1, EDGES)
        for i in range(len(v)): h.SetBinContent(i + 1, v[i])
        h.SetFillColor(col); h.SetLineColor(ROOT.kBlack); st.Add(h); keep.append((h, glab))
    for h, glab in reversed(keep): leg.AddEntry(h, glab, "f")
    st.Draw("hist"); st.SetMinimum(0.01); st.SetMaximum(max(tot.max(), 1) * 200)
    st.GetXaxis().SetTitle(f"{lab} m(ll) (GeV)"); st.GetYaxis().SetTitle("Events / bin"); st.GetYaxis().SetTitleOffset(1.3)
    sig_yields = []
    for s, col in SIGS:
        ms = m & issig & (np.char.find(smp.astype(str), s) >= 0)
        v, _ = np.histogram(d["m_l1l2"][ms], EDGES, weights=d["weight"][ms]); sig_yields.append(v.sum())
        h = ROOT.TH1D(f"h_{cat}_{s}", "", len(EDGES) - 1, EDGES)
        for i in range(len(v)): h.SetBinContent(i + 1, v[i])
        h.SetLineColor(getattr(ROOT, col.split("+")[0]) + (int(col.split("+")[1]) if "+" in col else 0)); h.SetLineWidth(2); h.SetLineStyle(1 if "N200" not in s else 2)
        h.Draw("hist same"); keep.append((h, s)); leg.AddEntry(h, "m_{W_{R}}=%s TeV, m_{N}=%s TeV" % (s[3:7][0], str(int(s.split("_N")[1]) / 1000).rstrip("0").rstrip(".")), "l")
    leg.Draw()
    t = ROOT.TLatex(); t.SetNDC(); t.SetTextSize(0.045); t.DrawLatex(0.15, 0.84, "ee"); t.SetTextSize(0.04); t.DrawLatex(0.15, 0.79, "Resolved SR, " + lab.replace("#", "\\#") if False else "Resolved SR")
    t.SetTextSize(0.035); t.DrawLatex(0.15, 0.74, lab); t.SetTextSize(0.05); t.SetTextFont(62); t.DrawLatex(0.40, 0.25, "Blinded (MC only)")
    c.SaveAs(f"{outdir}/ResolveSREE_{cat}_Mll_plot.png")
    lines.append(f"| {lab} | " + " | ".join(f"{yields[g]:.1f}" for g, _, _ in GROUPS) + f" | {tot.sum():.1f} | " + " | ".join(f"{v:.2f}" for v in sig_yields) + " |")
    with open(f"{outdir}/ResolveSREE_{cat}_Mll.tsv", "w") as f:
        f.write("BinLow\tBinHigh\tMC_Total\t" + "\t".join(g for g, _, _ in GROUPS) + "\t" + "\t".join(s for s, _ in SIGS) + "\n")
        hs = {g: np.histogram(d["m_l1l2"][m & (grp == g)], EDGES, weights=d["weight"][m & (grp == g)])[0] for g, _, _ in GROUPS}
        ss = {s: np.histogram(d["m_l1l2"][m & issig & (np.char.find(smp.astype(str), s) >= 0)], EDGES, weights=d["weight"][m & issig & (np.char.find(smp.astype(str), s) >= 0)])[0] for s, _ in SIGS}
        for i in range(len(EDGES) - 1):
            f.write(f"{EDGES[i]:.0f}\t{EDGES[i+1]:.0f}\t{tot[i]:.4f}\t" + "\t".join(f"{hs[g][i]:.4f}" for g, _, _ in GROUPS) + "\t" + "\t".join(f"{ss[s][i]:.4f}" for s, _ in SIGS) + "\n")
print("\n".join(lines)); open(os.path.join(a.out, "chargesign_mll_yields.md"), "w").write("# Resolved SR EE m(ll) by charge sign (m_ll > 400, m_lljj > 800), MC only\n\n" + "\n".join(lines) + "\n")
print("CHARGESIGN_MLL_DONE")
