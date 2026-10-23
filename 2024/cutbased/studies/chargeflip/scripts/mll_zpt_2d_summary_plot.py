#!/usr/bin/env python3
"""Study 24e: one-glance summary of the (m_ll, Z pT) transfer vs m_ll, from AN_rawcharge/24_mll_zpt_2d_factor_drll/slices.json (nominal binning).
  sumw_ratio_vs_mll.png  : Sum w (flip-weighted yield) data / MC  for the native 1-jet MC and for [2-jet DY MC x f + 1-jet non-DY MC]
  endcap_frac_vs_mll.png : fraction of leading electrons with |eta_SC| > 1.566 in data, native 1-jet MC, transferred MC
    ./condor/in_container.sh python3 studies/chargeflip/scripts/mll_zpt_2d_summary_plot.py"""
import json, sys
from pathlib import Path
import numpy as np
BASE = Path(__file__).resolve().parents[1]; PC = Path(__file__).resolve().parents[3]; OUT = BASE / "AN_rawcharge/24_mll_zpt_2d_factor_drll"; S = json.load(open(OUT / "slices.json"))["nominal"]
SL = ["150-200", "200-300", "300-400", "400-500", "500-700", "700-1000", ">=1000"]; E = np.array([150, 200, 300, 400, 500, 700, 1000, 2000.])
sys.path.insert(0, str(PC)); import ROOT, config            # noqa: E402
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0); ROOT.gErrorIgnoreLevel = ROOT.kWarning


def hist(name, vals, errs, col, mk):
    h = ROOT.TH1D(name, "", len(E) - 1, E)
    for i, (v, e) in enumerate(zip(vals, errs)): h.SetBinContent(i + 1, v); h.SetBinError(i + 1, e)
    h.SetLineColor(col); h.SetMarkerColor(col); h.SetMarkerStyle(mk); h.SetLineWidth(2); h.SetMarkerSize(1.2); return h


def canvas(hs, labs, ytitle, ymin, ymax, fname, line=None):
    c = ROOT.TCanvas("c", "", 800, 700); c.SetLogx(); c.SetLeftMargin(0.13); c.SetBottomMargin(0.13); h0 = hs[0]; h0.SetMinimum(ymin); h0.SetMaximum(ymax)
    h0.GetXaxis().SetTitle("m(ll) (GeV)"); h0.GetXaxis().SetMoreLogLabels(); h0.GetXaxis().SetNoExponent(); h0.GetXaxis().SetTitleSize(0.045); h0.GetYaxis().SetTitle(ytitle); h0.GetYaxis().SetTitleSize(0.045); h0.GetYaxis().SetTitleOffset(1.3)
    h0.Draw("E1"); box = ROOT.TBox(400, ymin, 2000, ymax); box.SetFillColorAlpha(ROOT.kGreen + 1, 0.10); box.Draw(); [h.Draw("E1 SAME") for h in hs]
    if line is not None: ln = ROOT.TLine(E[0], line, E[-1], line); ln.SetLineStyle(2); ln.Draw()
    lg = ROOT.TLegend(0.16, 0.70, 0.62, 0.88); lg.SetBorderSize(0); lg.SetFillStyle(0); lg.SetTextSize(0.033); [lg.AddEntry(h, l, "lp") for h, l in zip(hs, labs)]; lg.Draw()
    t = ROOT.TLatex(); t.SetNDC(); t.SetTextFont(61); t.SetTextSize(0.045); t.DrawLatex(0.13, 0.92, "CMS"); t.SetTextFont(52); t.SetTextSize(0.035); t.DrawLatex(0.22, 0.92, config.CMS_SUBLABEL)
    t.SetTextFont(42); t.SetTextSize(0.032); t.SetTextAlign(31); t.DrawLatex(0.90, 0.92, "2024 (13.6 TeV)"); t.SetTextAlign(11); t.SetTextSize(0.035); t.DrawLatex(0.64, 0.84, "ee OS, 1 jet"); t.DrawLatex(0.64, 0.79, "shaded: SR m(ll) range")
    c.SaveAs(str(OUT / (fname + ".png"))); c.SaveAs(str(OUT / (fname + ".pdf"))); c.Close()


canvas([hist("a", [S[k]["data_over_native"][0] for k in SL], [S[k]["data_over_native"][1] for k in SL], ROOT.kBlack, 20),
        hist("b", [S[k]["data_over_transferred"][0] for k in SL], [S[k]["data_over_transferred"][1] for k in SL], ROOT.kRed + 1, 21)],
       ["1-jet data / native 1-jet MC", "1-jet data / (2-jet DY MC #times f(m_{ll}, Z p_{T}) + non-DY)"], "#Sigma w (flip-weighted yield), data / MC", 0.5, 1.8, "sumw_ratio_vs_mll", line=1.0)
nd = [S[k]["n_data"] for k in SL]; fd = [S[k]["endcap"]["data"] for k in SL]
canvas([hist("d", fd, [np.sqrt(f * (1 - f) / n) for f, n in zip(fd, nd)], ROOT.kBlack, 20), hist("n", [S[k]["endcap"]["native"] for k in SL], [0] * len(SL), ROOT.kBlue + 1, 24), hist("t", [S[k]["endcap"]["transferred"] for k in SL], [0] * len(SL), ROOT.kRed + 1, 21)],
       ["1-jet data", "native 1-jet MC", "2-jet DY MC #times f + 1-jet non-DY MC"], "Fraction of leading electrons with |#eta_{SC}| > 1.566", 0.15, 0.50, "endcap_frac_vs_mll")
print("wrote", OUT)
