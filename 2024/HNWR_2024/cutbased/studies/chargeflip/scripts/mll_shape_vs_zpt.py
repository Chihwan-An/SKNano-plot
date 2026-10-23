#!/usr/bin/env python3
"""Study 21b: unit-area m_ll shape of the DY MC in slices of the dilepton pT (the converse of zpt_shape_vs_mll.py).
1-jet (nJet == 1, dR(ll) > 0.4) and 2-jet SR topology, OS. Input: data/zpt_zeta_transfer_events.npz.
    ./condor/in_container.sh python3 studies/chargeflip/scripts/mll_shape_vs_zpt.py"""
import json, sys
from pathlib import Path
import numpy as np
BASE = Path(__file__).resolve().parents[1]; PC = Path(__file__).resolve().parents[3]; OUT = BASE / "AN_rawcharge/21_zpt_shape_vs_mll"; OUT.mkdir(parents=True, exist_ok=True)
z = np.load(BASE / "data/zpt_zeta_transfer_events.npz"); dy = z["grp"] == "DY"
d = {k: z[k][dy].astype("float64") for k in ("channel", "m_l1l2", "pt_l1l2", "weight", "l1_eta", "l2_eta", "l1_phi", "l2_phi")}; two = z["topo2j"][dy].astype(bool)
dphi = np.abs(d["l1_phi"] - d["l2_phi"]); dphi = np.where(dphi > np.pi, 2 * np.pi - dphi, dphi); keep = two | (np.hypot(d["l1_eta"] - d["l2_eta"], dphi) > 0.4)
ZPT = [(0, 50), (50, 100), (100, 150), (150, 200), (200, 300), (300, 500), (500, 1e9)]
EDGES = np.array([60, 70, 80, 90, 100, 110, 120, 135, 150, 175, 200, 250, 300, 400, 500, 700, 1000, 2000.])
sys.path.insert(0, str(PC)); import ROOT, config            # noqa: E402
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0); ROOT.gErrorIgnoreLevel = ROOT.kWarning
COL = [ROOT.kGray + 2, ROOT.kBlack, ROOT.kBlue + 1, ROOT.kAzure + 7, ROOT.kGreen + 2, ROOT.kOrange + 1, ROOT.kRed + 1]
RES = {}
for chn, code, lab in (("EE", 11, "ee"), ("MM", 13, "#mu#mu")):
    for cat, csel, clab in (("1jet", ~two & keep, "1 jet"), ("2jet", two, "#geq2 jets (SR topology)")):
        c = ROOT.TCanvas("c", "", 800, 800); c.SetLogy(); c.SetLogx(); c.SetLeftMargin(0.13); c.SetBottomMargin(0.12); c.SetTopMargin(0.09); c.SetRightMargin(0.05)
        hs = []; lg = ROOT.TLegend(0.47, 0.58, 0.93, 0.88); lg.SetBorderSize(0); lg.SetFillStyle(0); lg.SetTextSize(0.030); RES[f"{chn}_{cat}"] = {}
        for k, (lo, hi) in enumerate(ZPT):
            m = (d["channel"] == code) & csel & (d["pt_l1l2"] >= lo) & (d["pt_l1l2"] < hi); w = d["weight"][m]; x = np.clip(d["m_l1l2"][m], EDGES[0], EDGES[-1] - 1e-6)
            n, _ = np.histogram(x, EDGES, weights=w); v, _ = np.histogram(x, EDGES, weights=w * w); tot = n.sum(); h = ROOT.TH1D(f"h{k}", "", len(EDGES) - 1, EDGES)
            for i in range(len(n)):
                bw = EDGES[i + 1] - EDGES[i]; h.SetBinContent(i + 1, n[i] / tot / bw); h.SetBinError(i + 1, np.sqrt(v[i]) / tot / bw)
            h.SetLineColor(COL[k]); h.SetMarkerColor(COL[k]); h.SetLineWidth(2); h.SetMarkerSize(0); hs.append(h)
            fz = float(w[(d["m_l1l2"][m] >= 80) & (d["m_l1l2"][m] < 100)].sum() / tot); f150 = float(w[d["m_l1l2"][m] >= 150].sum() / tot); f400 = float(w[d["m_l1l2"][m] >= 400].sum() / tot)
            name = f"{lo:.0f} #leq p_{{T}}(ll) < {hi:.0f}" if hi < 1e8 else f"p_{{T}}(ll) #geq {lo:.0f}"; lg.AddEntry(h, f"{name}  (Z peak {100 * fz:.0f}%)", "l")
            RES[f"{chn}_{cat}"][f"{lo:.0f}-{hi:.0f}" if hi < 1e8 else f"{lo:.0f}-inf"] = dict(yield_=float(tot), frac_80_100=fz, frac_ge150=f150, frac_ge400=f400, min_mll=float(d["m_l1l2"][m].min()))
        hs[0].SetMinimum(1e-7); hs[0].SetMaximum(3); hs[0].GetYaxis().SetTitle("1/N dN/dm(ll) (GeV^{-1})"); hs[0].GetXaxis().SetTitle("m(ll) (GeV)"); hs[0].GetXaxis().SetMoreLogLabels(); hs[0].GetXaxis().SetNoExponent()
        hs[0].GetYaxis().SetTitleOffset(1.3); hs[0].GetXaxis().SetTitleOffset(1.2); hs[0].Draw("HIST E"); [h.Draw("HIST E SAME") for h in hs[1:]]; lg.Draw()
        t = ROOT.TLatex(); t.SetNDC(); t.SetTextFont(61); t.SetTextSize(0.045); t.DrawLatex(0.13, 0.925, "CMS"); t.SetTextFont(52); t.SetTextSize(0.035); t.DrawLatex(0.22, 0.925, "Simulation " + config.CMS_SUBLABEL)
        t.SetTextFont(42); t.SetTextSize(0.030); t.SetTextAlign(31); t.DrawLatex(0.95, 0.925, "2024 (13.6 TeV)"); t.SetTextAlign(11); t.SetTextFont(62); t.SetTextSize(0.05); t.DrawLatex(0.17, 0.84, lab)
        t.SetTextFont(42); t.SetTextSize(0.032); t.DrawLatex(0.17, 0.79, "DY MC, OS, " + clab)
        c.SaveAs(str(OUT / f"mll_shape_vs_zpt_{chn}_{cat}.png")); c.SaveAs(str(OUT / f"mll_shape_vs_zpt_{chn}_{cat}.pdf")); c.Close()
        print(f"[{chn} {cat}]  " + "  ".join(f"pT {k}: Zpeak {100 * v['frac_80_100']:.0f}%, >=150 {100 * v['frac_ge150']:.1f}%, >=400 {100 * v['frac_ge400']:.2f}%, min m {v['min_mll']:.0f}" for k, v in RES[f"{chn}_{cat}"].items()))
(OUT / "summary_mll_vs_zpt.json").write_text(json.dumps(dict(mll_edges=EDGES.tolist(), **RES), indent=1) + "\n")
