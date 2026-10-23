#!/usr/bin/env python3
"""Study 23: after normalising 1-jet and 2-jet to each other inside every m_ll bin, is the Z pT ratio r(Z pT | m_ll) = shape_2j / shape_1j
the same in every m_ll bin (i.e. does the 2j/1j factor factorise as g(m_ll) x h(Z pT))?  DY MC only, OS, EE / MM.
2-jet definitions: ge2j (nJet >= 2), ge2j_res (+ passResolved), SRtopo (+ m_lljj > 800). dR(l1,l2) > 0.4 in every category.
Input: data/dy_jetdef_events.npz (study 22 cache).
    ./condor/in_container.sh python3 studies/chargeflip/scripts/zpt_ratio_vs_mll_normalised.py"""
import json, sys
from pathlib import Path
import numpy as np
BASE = Path(__file__).resolve().parents[1]; PC = Path(__file__).resolve().parents[3]; OUT = BASE / "AN_rawcharge/23_zpt_ratio_vs_mll_normalised"; OUT.mkdir(parents=True, exist_ok=True)
KEYS = ["channel", "nJet", "m_l1l2", "pt_l1l2", "m_lljj", "weight", "passResolved", "l1_eta", "l2_eta", "l1_phi", "l2_phi"]
z = np.load(BASE / "data/dy_jetdef_events.npz"); d = {k: z[k].astype("float64") for k in KEYS}
dphi = np.abs(d["l1_phi"] - d["l2_phi"]); dphi = np.where(dphi > np.pi, 2 * np.pi - dphi, dphi); dr = np.hypot(d["l1_eta"] - d["l2_eta"], dphi) > 0.4
CATS = {"1j": (d["nJet"] == 1) & dr, "ge2j": (d["nJet"] >= 2) & dr, "ge2j_res": (d["nJet"] >= 2) & (d["passResolved"] > 0), "SRtopo": (d["nJet"] >= 2) & (d["passResolved"] > 0) & (d["m_lljj"] > 800)}
ZPT = np.array([0, 50, 100, 150, 200, 250, 300, 400, 500, 700, 1000.]); MLL = [(60, 150), (150, 200), (200, 300), (300, 400), (400, 500), (500, 700), (700, 1000), (1000, 1e9)]
MLAB = [f"{lo}-{hi:.0f}" if hi < 1e8 else f">={lo}" for lo, hi in MLL]


def hist(m):
    x = np.clip(d["pt_l1l2"][m], 0, ZPT[-1] - 1e-3); n, _ = np.histogram(x, ZPT, weights=d["weight"][m]); v, _ = np.histogram(x, ZPT, weights=d["weight"][m] ** 2); return n, v


sys.path.insert(0, str(PC)); import ROOT, config            # noqa: E402
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0); ROOT.gErrorIgnoreLevel = ROOT.kWarning
COL = [ROOT.kBlack, ROOT.kBlue + 1, ROOT.kAzure + 7, ROOT.kGreen + 2, ROOT.kOrange + 1, ROOT.kRed + 1, ROOT.kMagenta + 1, ROOT.kViolet + 3]; RES = {}
for chn, code, lab in (("EE", 11, "ee"), ("MM", 13, "#mu#mu")):
    RES[chn] = {}
    for cat in ("ge2j", "ge2j_res", "SRtopo"):
        R, ER, NORM = [], [], []
        for lo, hi in MLL:
            s = (d["channel"] == code) & (d["m_l1l2"] >= lo) & (d["m_l1l2"] < hi); n1, v1 = hist(s & CATS["1j"]); n2, v2 = hist(s & CATS[cat])
            ok = (n1 > 0) & (n2 > 0); g = n2.sum() / n1.sum(); r = np.where(ok, (n2 / n2.sum()) / np.where(ok, n1 / n1.sum(), 1), np.nan)
            e = r * np.sqrt(np.where(ok, v1 / np.where(ok, n1, 1) ** 2 + v2 / np.where(ok, n2, 1) ** 2, np.nan)); R.append(r); ER.append(e); NORM.append(float(g))
        R, ER = np.array(R), np.array(ER); RES[chn][cat] = dict(norm_2j_over_1j=NORM, r=np.nan_to_num(R).tolist(), r_err=np.nan_to_num(ER).tolist())
        print(f"\n[{chn}] 2-jet def = {cat}:  r(Z pT | m_ll) = [N2j/sum N2j] / [N1j/sum N1j]   (each m_ll bin normalised separately)")
        print("  Z pT bin    " + "".join(f"{m:>11s}" for m in MLAB)); print("  g=N2j/N1j   " + "".join(f"{g:11.4f}" for g in NORM))
        for i in range(len(ZPT) - 1): print(f"  {ZPT[i]:4.0f}-{ZPT[i+1]:<6.0f} " + "".join(f"{R[k, i]:11.3f}" if np.isfinite(R[k, i]) else "          -" for k in range(len(MLL))))
        print("  r / r(m_ll 60-150):"); 
        for i in range(len(ZPT) - 1): print(f"  {ZPT[i]:4.0f}-{ZPT[i+1]:<6.0f} " + "".join(f"{R[k, i] / R[0, i]:11.3f}" if np.isfinite(R[k, i] / R[0, i]) else "          -" for k in range(len(MLL))))
        c = ROOT.TCanvas("c", "", 800, 900); p1 = ROOT.TPad("p1", "", 0, 0.3, 1, 1); p2 = ROOT.TPad("p2", "", 0, 0, 1, 0.3); p1.SetBottomMargin(0.02); p2.SetTopMargin(0.02); p2.SetBottomMargin(0.35); p1.Draw(); p2.Draw()
        p1.cd(); p1.SetLogy(); hs = []; lg = ROOT.TLegend(0.52, 0.06, 0.92, 0.40); lg.SetBorderSize(0); lg.SetFillStyle(0); lg.SetTextSize(0.032)
        for k in range(len(MLL)):
            h = ROOT.TH1D(f"h{k}", "", len(ZPT) - 1, ZPT)
            for i in range(len(ZPT) - 1):
                if np.isfinite(R[k, i]): h.SetBinContent(i + 1, R[k, i]); h.SetBinError(i + 1, ER[k, i])
            h.SetLineColor(COL[k]); h.SetMarkerColor(COL[k]); h.SetLineWidth(2); h.SetMarkerStyle(20 + k % 4); hs.append(h); lg.AddEntry(h, f"m(ll) {MLAB[k]} GeV", "lp")
        hs[0].SetMinimum(5e-3); hs[0].SetMaximum(5e2); hs[0].GetYaxis().SetTitle("shape(2 jet) / shape(1 jet)"); hs[0].GetYaxis().SetTitleSize(0.05); hs[0].GetYaxis().SetTitleOffset(1.1); hs[0].GetXaxis().SetLabelSize(0)
        hs[0].Draw("E1"); [h.Draw("E1 SAME") for h in hs[1:]]; lg.Draw()
        t = ROOT.TLatex(); t.SetNDC(); t.SetTextFont(61); t.SetTextSize(0.045); t.DrawLatex(0.12, 0.93, "CMS"); t.SetTextFont(52); t.SetTextSize(0.035); t.DrawLatex(0.21, 0.93, "Simulation " + config.CMS_SUBLABEL)
        t.SetTextFont(42); t.SetTextSize(0.030); t.SetTextAlign(31); t.DrawLatex(0.90, 0.93, "2024 (13.6 TeV)"); t.SetTextAlign(11); t.SetTextFont(62); t.SetTextSize(0.06); t.DrawLatex(0.18, 0.82, lab)
        t.SetTextFont(42); t.SetTextSize(0.040); t.DrawLatex(0.18, 0.76, "DY MC, OS, 2 jet = " + cat); t.DrawLatex(0.18, 0.71, "normalised per m(ll) bin")
        p2.cd(); rs = []
        for k in range(1, len(MLL)):
            r = hs[k].Clone(f"r{k}"); r.Divide(hs[0]); rs.append(r)
        rs[0].SetMinimum(0); rs[0].SetMaximum(3); rs[0].GetYaxis().SetTitle("/ (60-150)"); rs[0].GetXaxis().SetTitle("Dilepton p_{T} (GeV)"); rs[0].GetXaxis().SetTitleSize(0.1); rs[0].GetXaxis().SetLabelSize(0.11)
        rs[0].GetYaxis().SetTitleSize(0.1); rs[0].GetYaxis().SetLabelSize(0.11); rs[0].GetYaxis().SetTitleOffset(0.45); rs[0].GetYaxis().SetNdivisions(505); rs[0].Draw("E1"); [r.Draw("E1 SAME") for r in rs[1:]]
        ln = ROOT.TLine(ZPT[0], 1, ZPT[-1], 1); ln.SetLineStyle(2); ln.Draw(); c.SaveAs(str(OUT / f"zpt_ratio_vs_mll_{chn}_{cat}.png")); c.SaveAs(str(OUT / f"zpt_ratio_vs_mll_{chn}_{cat}.pdf")); c.Close()
(OUT / "summary.json").write_text(json.dumps(dict(zpt_edges=ZPT.tolist(), mll_bins=MLAB, **RES), indent=1) + "\n"); print("\nwrote", OUT)
