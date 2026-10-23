#!/usr/bin/env python3
"""Study 20: is f(Z pT, |Z eta|) = N_DY(1 jet) / N_DY(2 jet, SR topology) the same in the DY window and at m_ll >= 400?  DY MC only.
Windows: 60-150 (DY window), 150-400 (sideband), >= 400 (SR m_ll range). OS, EE and MM. The 1-jet sample also requires dR(l1,l2) > 0.4
(passResolved applies it to the 2-jet sample, study 19). Input: data/zpt_zeta_transfer_events.npz.
    ./condor/in_container.sh python3 studies/chargeflip/scripts/zpt_zeta_factor_compare.py"""
import json, sys
from pathlib import Path
import numpy as np
BASE = Path(__file__).resolve().parents[1]; PC = Path(__file__).resolve().parents[3]; OUT = BASE / "AN_rawcharge/20_factor_dywindow_vs_highmass"; OUT.mkdir(parents=True, exist_ok=True)
z = np.load(BASE / "data/zpt_zeta_transfer_events.npz"); grp = z["grp"]; dy = grp == "DY"
d = {k: z[k][dy].astype("float64") for k in ("channel", "m_l1l2", "pt_l1l2", "weight", "l1_pt", "l2_pt", "l1_eta", "l2_eta", "l1_phi", "l2_phi")}; two = z["topo2j"][dy].astype(bool)
pz = d["l1_pt"] * np.sinh(d["l1_eta"]) + d["l2_pt"] * np.sinh(d["l2_eta"]); px = d["l1_pt"] * np.cos(d["l1_phi"]) + d["l2_pt"] * np.cos(d["l2_phi"]); py = d["l1_pt"] * np.sin(d["l1_phi"]) + d["l2_pt"] * np.sin(d["l2_phi"])
aeta = np.abs(np.arcsinh(pz / np.maximum(np.hypot(px, py), 1e-9))); dphi = np.abs(d["l1_phi"] - d["l2_phi"]); dphi = np.where(dphi > np.pi, 2 * np.pi - dphi, dphi)
keep = two | (np.hypot(d["l1_eta"] - d["l2_eta"], dphi) > 0.4)
ZPT = np.array([0, 60, 80, 100, 125, 150, 175, 200, 250, 300, 400, 500, 700, 1000.]); ZETA = np.array([0, 1.0, 2.0, 3.0, 10.0])
WIN = [("DYwindow 60-150", 60, 150), ("sideband 150-400", 150, 400), ("highmass >=400", 400, 1e9)]


def fac(sel):
    out = {}
    for name, m1, m2 in (("1j", sel & ~two & keep, None), ("2j", sel & two, None)):
        x = np.stack([d["pt_l1l2"][m1], aeta[m1]], 1); w = d["weight"][m1]
        n, _ = np.histogramdd(x, [ZPT, ZETA], weights=w); v, _ = np.histogramdd(x, [ZPT, ZETA], weights=w * w); out[name] = (n, v)
    (n1, v1), (n2, v2) = out["1j"], out["2j"]
    def r(a, va, b, vb):
        ok = (a > 0) & (b > 0); f = np.where(ok, a / np.where(ok, b, 1), np.nan); e = f * np.sqrt(np.where(ok, va / np.where(ok, a, 1) ** 2 + vb / np.where(ok, b, 1) ** 2, np.nan)); return f, e
    f2, e2 = r(n1, v1, n2, v2); f1, e1 = r(n1.sum(1), v1.sum(1), n2.sum(1), v2.sum(1)); return f1, e1, f2, e2, float(n1.sum() / n2.sum())


sys.path.insert(0, str(PC)); import ROOT, config            # noqa: E402
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0); ROOT.gErrorIgnoreLevel = ROOT.kWarning
COL = [ROOT.kBlack, ROOT.kBlue + 1, ROOT.kRed + 1]; RES = {}
for chn, code, lab in (("EE", 11, "ee"), ("MM", 13, "#mu#mu")):
    F = {}
    for name, lo, hi in WIN:
        F[name] = fac((d["channel"] == code) & (d["m_l1l2"] >= lo) & (d["m_l1l2"] < hi))
    RES[chn] = {n: dict(f_zpt=np.nan_to_num(v[0]).tolist(), f_zpt_err=np.nan_to_num(v[1]).tolist(), f_2d=np.nan_to_num(v[2]).tolist(), global_ratio=v[4]) for n, v in F.items()}
    print(f"\n[{chn}] f(Z pT) = N(1j)/N(2j), DY MC, integrated over Z eta          global: " + "   ".join(f"{n}: {v[4]:.2f}" for n, v in F.items()))
    print("  Z pT bin      DYwindow          sideband          highmass       highmass/DYwindow")
    for i in range(len(ZPT) - 1):
        a, s_, h = F[WIN[0][0]], F[WIN[1][0]], F[WIN[2][0]]; rr = h[0][i] / a[0][i] if a[0][i] > 0 else np.nan
        print(f"  {ZPT[i]:4.0f}-{ZPT[i+1]:<5.0f} {a[0][i]:8.3f} +- {a[1][i]:6.3f} {s_[0][i]:8.3f} +- {s_[1][i]:6.3f} {h[0][i]:8.3f} +- {h[1][i]:6.3f}     {rr:6.3f}")
    print("  highmass / DYwindow of the 2D factor, rows = Z pT bin, columns = |Z eta| 0-1, 1-2, 2-3, >3")
    rat = F[WIN[2][0]][2] / F[WIN[0][0]][2]
    for i in range(len(ZPT) - 1): print(f"  {ZPT[i]:4.0f}-{ZPT[i+1]:<5.0f} " + "  ".join(f"{x:7.3f}" if np.isfinite(x) else "      -" for x in rat[i]))
    RES[chn]["highmass_over_DYwindow_2d"] = np.nan_to_num(rat).tolist()
    # plots: f vs Z pT for the three windows, inclusive in Z eta and per |Z eta| slice
    for ie in [-1] + list(range(len(ZETA) - 1)):
        c = ROOT.TCanvas("c", "", 800, 900); p1 = ROOT.TPad("p1", "", 0, 0.3, 1, 1); p2 = ROOT.TPad("p2", "", 0, 0, 1, 0.3); p1.SetBottomMargin(0.02); p2.SetTopMargin(0.02); p2.SetBottomMargin(0.35); p1.Draw(); p2.Draw()
        p1.cd(); p1.SetLogy(); hs = []; lg = ROOT.TLegend(0.50, 0.68, 0.92, 0.88); lg.SetBorderSize(0); lg.SetFillStyle(0); lg.SetTextSize(0.035)
        for k, (name, lo, hi) in enumerate(WIN):
            f, e = (F[name][0], F[name][1]) if ie < 0 else (F[name][2][:, ie], F[name][3][:, ie]); h = ROOT.TH1D(f"h{k}", "", len(ZPT) - 1, ZPT)
            for i in range(len(f)):
                if np.isfinite(f[i]): h.SetBinContent(i + 1, f[i]); h.SetBinError(i + 1, e[i] if np.isfinite(e[i]) else 0)
            h.SetLineColor(COL[k]); h.SetMarkerColor(COL[k]); h.SetLineWidth(2); h.SetMarkerStyle(20 + k); hs.append(h); lg.AddEntry(h, "m(ll) " + name.split()[1] + " GeV", "lp")
        hs[0].SetMinimum(0.05); hs[0].SetMaximum(5e3); hs[0].GetYaxis().SetTitle("f = N(1 jet) / N(2 jet)"); hs[0].GetYaxis().SetTitleSize(0.05); hs[0].GetYaxis().SetTitleOffset(1.1); hs[0].GetXaxis().SetLabelSize(0)
        hs[0].Draw("E1"); [h.Draw("E1 SAME") for h in hs[1:]]; lg.Draw()
        t = ROOT.TLatex(); t.SetNDC(); t.SetTextFont(61); t.SetTextSize(0.045); t.DrawLatex(0.12, 0.93, "CMS"); t.SetTextFont(52); t.SetTextSize(0.035); t.DrawLatex(0.21, 0.93, "Simulation " + config.CMS_SUBLABEL)
        t.SetTextFont(42); t.SetTextSize(0.030); t.SetTextAlign(31); t.DrawLatex(0.90, 0.93, "2024 (13.6 TeV)"); t.SetTextAlign(11); t.SetTextFont(62); t.SetTextSize(0.06); t.DrawLatex(0.18, 0.82, lab)
        t.SetTextFont(42); t.SetTextSize(0.045); t.DrawLatex(0.18, 0.76, "DY MC, OS, " + ("all Z #eta" if ie < 0 else f"{ZETA[ie]:.0f} #leq |Z #eta| < {ZETA[ie+1]:.0f}"))
        p2.cd(); rs = []
        for k in (1, 2):
            r = hs[k].Clone(f"r{k}"); r.Divide(hs[0]); rs.append(r)
        rs[0].SetMinimum(0); rs[0].SetMaximum(3); rs[0].GetYaxis().SetTitle("/ DY window"); rs[0].GetXaxis().SetTitle("Dilepton p_{T} (GeV)"); rs[0].GetXaxis().SetTitleSize(0.1); rs[0].GetXaxis().SetLabelSize(0.11)
        rs[0].GetYaxis().SetTitleSize(0.1); rs[0].GetYaxis().SetLabelSize(0.11); rs[0].GetYaxis().SetTitleOffset(0.45); rs[0].GetYaxis().SetNdivisions(505); rs[0].Draw("E1"); rs[1].Draw("E1 SAME")
        ln = ROOT.TLine(ZPT[0], 1, ZPT[-1], 1); ln.SetLineStyle(2); ln.Draw(); c.SaveAs(str(OUT / f"factor_vs_zpt_{chn}_{'allEta' if ie < 0 else 'eta%d' % ie}.png")); c.Close()
(OUT / "summary.json").write_text(json.dumps(dict(zpt_edges=ZPT.tolist(), zeta_edges=ZETA.tolist(), **RES), indent=1) + "\n"); print("\nwrote", OUT)
