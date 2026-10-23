#!/usr/bin/env python3
"""Study 22: is the m_ll shape above 150 GeV independent of the jet category once m_lljj > 800 is dropped from the 2-jet definition?
DY MC only, OS, EE / MM, m_ll >= 60. Categories: 1j (nJet == 1), ge2j (nJet >= 2), ge2j_res (+ passResolved), SRtopo (+ m_lljj > 800).
dR(l1, l2) > 0.4 is required in every category (passResolved contains it). Builds its own cache from the dumps (DY files only).
    python3 mll_shape_jetdef_compare.py [--rebuild]      (numpy only; plots need ROOT: run through condor/in_container.sh)"""
import argparse, glob, json, os, sys
from pathlib import Path
import numpy as np
BASE = Path(__file__).resolve().parents[1]; PC = Path(__file__).resolve().parents[3]; T_ = Path(__file__).resolve().parents[5] / "BDT/SR/test"
ap = argparse.ArgumentParser(); ap.add_argument("--dumps", default=str(T_ / "data/chargeflip/dumps_boost")); ap.add_argument("--cache", default=str(BASE / "data/dy_jetdef_events.npz")); ap.add_argument("--rebuild", action="store_true")
a = ap.parse_args(); OUT = BASE / "AN_rawcharge/22_mll_shape_jetdef"; OUT.mkdir(parents=True, exist_ok=True)
KEYS = ["channel", "nJet", "m_l1l2", "pt_l1l2", "m_lljj", "weight", "w_dy", "j1_pt", "j2_pt", "l1_pt", "l2_pt", "passResolved", "l1_eta", "l2_eta", "l1_phi", "l2_phi"]
if a.rebuild or not os.path.exists(a.cache):
    acc = {k: [] for k in KEYS}
    for p in sorted(glob.glob(os.path.join(a.dumps, "tree_Skim_HNWR_DYto2L*.npz"))):
        z = np.load(p); m = (z["hasPair"] > 0) & (z["isSS"] == 0) & (z["m_l1l2"] >= 60) & (z["nJet"] >= 1) & ((z["channel"] == 11) | (z["channel"] == 13))
        for k in KEYS: acc[k].append(np.asarray(z[k][m], dtype="float32"))
        print(f"  {os.path.basename(p)[15:70]:56s} {int(m.sum()):9d}", flush=True)
    np.savez_compressed(a.cache, **{k: np.concatenate(v) for k, v in acc.items()})
z = np.load(a.cache); d = {k: z[k].astype("float64") for k in KEYS}
dphi = np.abs(d["l1_phi"] - d["l2_phi"]); dphi = np.where(dphi > np.pi, 2 * np.pi - dphi, dphi); dr = np.hypot(d["l1_eta"] - d["l2_eta"], dphi) > 0.4
CATS = {"1j": (d["nJet"] == 1) & dr, "ge2j": (d["nJet"] >= 2) & dr, "ge2j_res": (d["nJet"] >= 2) & (d["passResolved"] > 0), "SRtopo": (d["nJet"] >= 2) & (d["passResolved"] > 0) & (d["m_lljj"] > 800)}
E = np.array([150, 200, 250, 300, 400, 500, 700, 1000, 2000.]); ZS = [("all Z pT", 0, 1e9), ("0-50", 0, 50), ("50-100", 50, 100), ("100-200", 100, 200), ("200-300", 200, 300), ("300-500", 300, 500), (">=500", 500, 1e9)]


def shape(m):
    x = np.clip(d["m_l1l2"][m], 150, 1999.9); n, _ = np.histogram(x, E, weights=d["weight"][m]); v, _ = np.histogram(x, E, weights=d["weight"][m] ** 2); return n / n.sum(), np.sqrt(v) / n.sum(), float(n.sum())


RES = {}
for chn, code in (("EE", 11), ("MM", 13)):
    RES[chn] = {}
    for cat in ("ge2j", "ge2j_res", "SRtopo"):
        print(f"\n[{chn}] m_ll >= 150, unit area inside the range: {cat} / 1j      m_ll bins: " + " ".join(f"{x:.0f}" for x in E)); RES[chn][cat] = {}
        for lab, lo, hi in ZS:
            b = (d["channel"] == code) & (d["m_l1l2"] >= 150) & (d["pt_l1l2"] >= lo) & (d["pt_l1l2"] < hi); s1, e1, n1 = shape(b & CATS["1j"]); s2, e2, n2 = shape(b & CATS[cat])
            r = s2 / s1; er = r * np.hypot(e1 / s1, e2 / s2); RES[chn][cat][lab] = dict(ratio=r.tolist(), err=er.tolist(), n_1j=n1, n_cat=n2)
            print(f"  Z pT {lab:9s} " + "  ".join(f"{x:5.2f}" for x in r) + f"     max |r-1| = {np.max(np.abs(r - 1)):.2f}   (N {n2:.0f} vs 1j {n1:.0f})")
(OUT / "summary.json").write_text(json.dumps(dict(mll_edges=E.tolist(), **RES), indent=1) + "\n")
try:
    sys.path.insert(0, str(PC)); import ROOT, config
except Exception as ex:
    print("no ROOT, numbers only:", ex); sys.exit(0)
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0); ROOT.gErrorIgnoreLevel = ROOT.kWarning
STY = {"1j": (ROOT.kBlack, "1 jet"), "ge2j": (ROOT.kBlue + 1, "#geq2 jets"), "ge2j_res": (ROOT.kGreen + 2, "#geq2 jets, resolved"), "SRtopo": (ROOT.kRed + 1, "#geq2 jets, resolved, m_{lljj}>800")}
for chn, code, lab in (("EE", 11, "ee"), ("MM", 13, "#mu#mu")):
    for zl, lo, hi in (("allZpt", 0, 1e9), ("Zpt0to100", 0, 100), ("Zpt100to300", 100, 300), ("Zpt300toInf", 300, 1e9)):
        c = ROOT.TCanvas("c", "", 800, 900); p1 = ROOT.TPad("p1", "", 0, 0.3, 1, 1); p2 = ROOT.TPad("p2", "", 0, 0, 1, 0.3); p1.SetBottomMargin(0.02); p2.SetTopMargin(0.02); p2.SetBottomMargin(0.35); p1.Draw(); p2.Draw()
        p1.cd(); p1.SetLogy(); p1.SetLogx(); p2.SetLogx(); hs = {}; lg = ROOT.TLegend(0.45, 0.66, 0.92, 0.88); lg.SetBorderSize(0); lg.SetFillStyle(0); lg.SetTextSize(0.035)
        for cat, (col, cl) in STY.items():
            b = (d["channel"] == code) & (d["m_l1l2"] >= 150) & (d["pt_l1l2"] >= lo) & (d["pt_l1l2"] < hi) & CATS[cat]; s, e, _ = shape(b); h = ROOT.TH1D("h" + cat, "", len(E) - 1, E)
            for i in range(len(s)): h.SetBinContent(i + 1, s[i] / (E[i + 1] - E[i])); h.SetBinError(i + 1, e[i] / (E[i + 1] - E[i]))
            h.SetLineColor(col); h.SetMarkerColor(col); h.SetLineWidth(2); h.SetMarkerSize(0); hs[cat] = h; lg.AddEntry(h, cl, "l")
        h0 = hs["1j"]; h0.SetMinimum(1e-6); h0.SetMaximum(0.1); h0.GetYaxis().SetTitle("1/N dN/dm(ll) (GeV^{-1}), m(ll) #geq 150"); h0.GetYaxis().SetTitleSize(0.045); h0.GetYaxis().SetTitleOffset(1.2); h0.GetXaxis().SetLabelSize(0)
        h0.Draw("HIST E"); [hs[k].Draw("HIST E SAME") for k in ("ge2j", "ge2j_res", "SRtopo")]; lg.Draw()
        t = ROOT.TLatex(); t.SetNDC(); t.SetTextFont(61); t.SetTextSize(0.045); t.DrawLatex(0.12, 0.93, "CMS"); t.SetTextFont(52); t.SetTextSize(0.035); t.DrawLatex(0.21, 0.93, "Simulation " + config.CMS_SUBLABEL)
        t.SetTextFont(42); t.SetTextSize(0.030); t.SetTextAlign(31); t.DrawLatex(0.90, 0.93, "2024 (13.6 TeV)"); t.SetTextAlign(11); t.SetTextFont(62); t.SetTextSize(0.06); t.DrawLatex(0.18, 0.30, lab)
        t.SetTextFont(42); t.SetTextSize(0.04); t.DrawLatex(0.18, 0.23, "DY MC, OS, " + {"allZpt": "all p_{T}(ll)", "Zpt0to100": "p_{T}(ll) < 100", "Zpt100to300": "100 #leq p_{T}(ll) < 300", "Zpt300toInf": "p_{T}(ll) #geq 300"}[zl])
        p2.cd(); rs = []
        for k in ("ge2j", "ge2j_res", "SRtopo"):
            r = hs[k].Clone("r" + k); r.Divide(h0); rs.append(r)
        rs[0].SetMinimum(0); rs[0].SetMaximum(3); rs[0].GetYaxis().SetTitle("/ 1 jet"); rs[0].GetXaxis().SetTitle("m(ll) (GeV)"); rs[0].GetXaxis().SetTitleSize(0.1); rs[0].GetXaxis().SetLabelSize(0.11); rs[0].GetXaxis().SetMoreLogLabels(); rs[0].GetXaxis().SetNoExponent()
        rs[0].GetYaxis().SetTitleSize(0.1); rs[0].GetYaxis().SetLabelSize(0.11); rs[0].GetYaxis().SetTitleOffset(0.45); rs[0].GetYaxis().SetNdivisions(505); rs[0].Draw("HIST E"); [r.Draw("HIST E SAME") for r in rs[1:]]
        ln = ROOT.TLine(E[0], 1, E[-1], 1); ln.SetLineStyle(2); ln.Draw(); c.SaveAs(str(OUT / f"mll_shape_jetdef_{chn}_{zl}.png")); c.Close()
print("wrote", OUT)
