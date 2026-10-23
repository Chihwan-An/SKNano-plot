#!/usr/bin/env python3
"""Study 21: unit-area dilepton pT shape of the DY MC in slices of m_ll, one plot per (channel, jet category).
1-jet (nJet == 1, dR(ll) > 0.4) and 2-jet SR topology (nJet >= 2, passResolved, m_lljj > 800), OS. Input: data/zpt_zeta_transfer_events.npz.
    ./condor/in_container.sh python3 studies/chargeflip/scripts/zpt_shape_vs_mll.py"""
import json, sys
from pathlib import Path
import numpy as np
BASE = Path(__file__).resolve().parents[1]; PC = Path(__file__).resolve().parents[3]; OUT = BASE / "AN_rawcharge/21_zpt_shape_vs_mll"; OUT.mkdir(parents=True, exist_ok=True)
z = np.load(BASE / "data/zpt_zeta_transfer_events.npz"); dy = z["grp"] == "DY"
d = {k: z[k][dy].astype("float64") for k in ("channel", "m_l1l2", "pt_l1l2", "weight", "l1_eta", "l2_eta", "l1_phi", "l2_phi")}; two = z["topo2j"][dy].astype(bool)
dphi = np.abs(d["l1_phi"] - d["l2_phi"]); dphi = np.where(dphi > np.pi, 2 * np.pi - dphi, dphi); keep = two | (np.hypot(d["l1_eta"] - d["l2_eta"], dphi) > 0.4)
MLL = [(60, 80), (80, 100), (100, 150), (150, 250), (250, 400), (400, 700), (700, 1000), (1000, 1e9)]
EDGES = np.array([0, 20, 40, 60, 80, 100, 125, 150, 175, 200, 250, 300, 400, 500, 700, 1000.])
sys.path.insert(0, str(PC)); import ROOT, config            # noqa: E402
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0); ROOT.gErrorIgnoreLevel = ROOT.kWarning
COL = [ROOT.kGray + 2, ROOT.kBlack, ROOT.kBlue + 1, ROOT.kAzure + 7, ROOT.kGreen + 2, ROOT.kOrange + 1, ROOT.kRed + 1, ROOT.kMagenta + 2]
RES = {}
for chn, code, lab in (("EE", 11, "ee"), ("MM", 13, "#mu#mu")):
    for cat, csel, clab in (("1jet", ~two & keep, "1 jet"), ("2jet", two, "#geq2 jets (SR topology)")):
        c = ROOT.TCanvas("c", "", 800, 900); p1 = ROOT.TPad("p1", "", 0, 0.3, 1, 1); p2 = ROOT.TPad("p2", "", 0, 0, 1, 0.3); p1.SetBottomMargin(0.02); p2.SetTopMargin(0.02); p2.SetBottomMargin(0.35); p1.Draw(); p2.Draw()
        p1.cd(); p1.SetLogy(); hs = []; lg = ROOT.TLegend(0.52, 0.50, 0.92, 0.86); lg.SetBorderSize(0); lg.SetFillStyle(0); lg.SetTextSize(0.030); RES[f"{chn}_{cat}"] = {}
        for k, (lo, hi) in enumerate(MLL):
            m = (d["channel"] == code) & csel & (d["m_l1l2"] >= lo) & (d["m_l1l2"] < hi); w = d["weight"][m]; x = np.clip(d["pt_l1l2"][m], 0, EDGES[-1] - 1e-6)
            n, _ = np.histogram(x, EDGES, weights=w); v, _ = np.histogram(x, EDGES, weights=w * w); tot = n.sum(); h = ROOT.TH1D(f"h{k}", "", len(EDGES) - 1, EDGES)
            for i in range(len(n)):
                bw = EDGES[i + 1] - EDGES[i]; h.SetBinContent(i + 1, n[i] / tot / bw); h.SetBinError(i + 1, np.sqrt(v[i]) / tot / bw)      # unit area, per GeV
            h.SetLineColor(COL[k]); h.SetMarkerColor(COL[k]); h.SetLineWidth(2); h.SetMarkerSize(0); hs.append(h)
            mean = float(np.average(d["pt_l1l2"][m], weights=w)); med = float(np.sort(d["pt_l1l2"][m])[np.searchsorted(np.cumsum(w[np.argsort(d["pt_l1l2"][m])]) / tot, 0.5)])
            name = f"{lo:.0f} #leq m(ll) < {hi:.0f}" if hi < 1e8 else f"m(ll) #geq {lo:.0f}"; lg.AddEntry(h, f"{name}  (<p_{{T}}> = {mean:.0f})", "l")
            RES[f"{chn}_{cat}"][f"{lo:.0f}-{hi:.0f}" if hi < 1e8 else f"{lo:.0f}-inf"] = dict(yield_=float(tot), mean_pt=mean, median_pt=med, frac_below_100=float(w[d["pt_l1l2"][m] < 100].sum() / tot), shape_per_GeV=(n / tot / np.diff(EDGES)).tolist())
        hs[0].SetMinimum(2e-6); hs[0].SetMaximum(0.3); hs[0].GetYaxis().SetTitle("1/N dN/dp_{T} (GeV^{-1})"); hs[0].GetYaxis().SetTitleSize(0.05); hs[0].GetYaxis().SetTitleOffset(1.1); hs[0].GetXaxis().SetLabelSize(0)
        hs[0].Draw("HIST E"); [h.Draw("HIST E SAME") for h in hs[1:]]; lg.Draw()
        t = ROOT.TLatex(); t.SetNDC(); t.SetTextFont(61); t.SetTextSize(0.045); t.DrawLatex(0.12, 0.93, "CMS"); t.SetTextFont(52); t.SetTextSize(0.035); t.DrawLatex(0.21, 0.93, "Simulation " + config.CMS_SUBLABEL)
        t.SetTextFont(42); t.SetTextSize(0.030); t.SetTextAlign(31); t.DrawLatex(0.90, 0.93, "2024 (13.6 TeV)"); t.SetTextAlign(11); t.SetTextFont(62); t.SetTextSize(0.06); t.DrawLatex(0.18, 0.82, lab)
        t.SetTextFont(42); t.SetTextSize(0.035); t.DrawLatex(0.18, 0.76, "DY MC, OS, " + clab)
        p2.cd(); rs = []
        for k in range(len(hs)):
            if k == 1: continue
            r = hs[k].Clone(f"r{k}"); r.Divide(hs[1]); rs.append(r)
        rs[0].SetMinimum(0); rs[0].SetMaximum(4); rs[0].GetYaxis().SetTitle("/ (80#minus100)"); rs[0].GetXaxis().SetTitle("Dilepton p_{T} (GeV)"); rs[0].GetXaxis().SetTitleSize(0.1); rs[0].GetXaxis().SetLabelSize(0.11)
        rs[0].GetYaxis().SetTitleSize(0.1); rs[0].GetYaxis().SetLabelSize(0.11); rs[0].GetYaxis().SetTitleOffset(0.45); rs[0].GetYaxis().SetNdivisions(505); rs[0].Draw("HIST E"); [r.Draw("HIST E SAME") for r in rs[1:]]
        ln = ROOT.TLine(EDGES[0], 1, EDGES[-1], 1); ln.SetLineStyle(2); ln.Draw(); c.SaveAs(str(OUT / f"zpt_shape_vs_mll_{chn}_{cat}.png")); c.SaveAs(str(OUT / f"zpt_shape_vs_mll_{chn}_{cat}.pdf")); c.Close()
        print(f"[{chn} {cat}]  " + "  ".join(f"{k}: <pT> {v['mean_pt']:.0f}, med {v['median_pt']:.0f}, <100: {100 * v['frac_below_100']:.0f}%" for k, v in RES[f"{chn}_{cat}"].items()))
(OUT / "summary.json").write_text(json.dumps(dict(pt_edges=EDGES.tolist(), **RES), indent=1) + "\n"); print("wrote", OUT)
