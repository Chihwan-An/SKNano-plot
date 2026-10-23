#!/usr/bin/env python3
"""make_ss_plots.py drawn in the plot/cutbased/out style (plotter._draw).

Same input (ddss_dyonly_sf.root) and the same binning, which already is the out
resolved binning (rEESR_SS has a 3132 edge in the template where out has 3200).
Band = full prefit stat (+) syst: the relative per-bin total_background error of
shapes_prefit in the combine fit (all shape + lnN nuisances + autoMCStats; free
rateParams carry no prior), applied to the template total. The v2 cards' SS
templates agree with ddss_dyonly_sf.root to ~1-2% per bin (7% in one SR bin).
Without a fitDiagnostics file it falls back to MC stat (+) the Flip variations
stored in the template file. Ratio stat band = template MC stat. The SR is drawn
blinded as in out/.

  python3 make_ss_plots_cutstyle.py [outdir] [fitDiagnostics.root]
"""
import math
import os
import sys

import ROOT

H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(H, "..", "..", "..")))
import config                                            # noqa: E402
from plotter import root_color, draw_ratio_points        # noqa: E402

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.TH1.AddDirectory(False)

GROUPS = dict(config.BACKGROUND_GROUPS)
GROUPS["DYJets"] = ("kYellow", "Drell-Yan (non-flip)")
GROUPS["Flip"] = ("kOrange", "DY charge flip")
FLIP_SYSTS = ["FlipSF_barrel_2024", "FlipSF_endcap_2024", "FlipPstat_2024"]
LABEL2 = {"rEESR_SS": "Resolved SR (SS)", "rDYEECR_SS": "Resolved DY CR (SS)"}
X_MAX = {"rEESR_SS": 8000.0, "rDYEECR_SS": 4000.0}


FITDIAG = os.path.join(H, "..", "03_combine_validation", "work_srcr_unc",
                       "cbv15_an2_ref_v2_EE_WR5000_N2500_noSSTT", "fitDiagnostics.SRCR.root")


def draw(f, reg, outdir, fd=None):
    keeper = []
    blind = "SR" in reg
    x_min, x_max = 800.0, X_MAX[reg]

    groups = {}
    for g in GROUPS:
        h = f.Get("%s/%s" % (reg, g))
        if h and h.Integral() > 0:
            groups[g] = h
    tot = None
    for h in groups.values():
        if tot is None:
            tot = h.Clone("tot_" + reg)
        else:
            tot.Add(h)
    data = f.Get("%s/data_obs" % reg).Clone("data_" + reg)
    for i in range(1, data.GetNbinsX() + 1):
        data.SetBinError(i, math.sqrt(max(data.GetBinContent(i), 0.0)))

    n = tot.GetNbinsX()
    up2, dn2 = [0.0] * (n + 2), [0.0] * (n + 2)
    flip = groups.get("Flip")
    for s in FLIP_SYSTS:
        hu, hd = f.Get("%s/Flip_%sUp" % (reg, s)), f.Get("%s/Flip_%sDown" % (reg, s))
        if not (flip and hu and hd):
            continue
        for i in range(1, n + 1):
            du, dd = hu.GetBinContent(i) - flip.GetBinContent(i), hd.GetBinContent(i) - flip.GetBinContent(i)
            up2[i] += max(0, du, dd) ** 2
            dn2[i] += max(0, -du, -dd) ** 2

    pre = fd.Get("shapes_prefit/%s/total_background" % reg) if fd else None
    if pre and pre.GetNbinsX() >= n:
        for i in range(1, n + 1):
            rel = pre.GetBinError(i) / pre.GetBinContent(i) if pre.GetBinContent(i) > 0 else 0.0
            e2 = (rel * tot.GetBinContent(i)) ** 2 - tot.GetBinError(i) ** 2
            up2[i] = dn2[i] = max(e2, 0.0)          # stat is added back below
    else:
        print("   %s: no prefit uncertainty -- band = stat (+) flip syst only" % reg)
    band_label = "Stat #oplus Syst Unc." if pre else "Stat #oplus Flip Syst Unc."

    g_syst, g_rband, g_rstat = (ROOT.TGraphAsymmErrors(n) for _ in range(3))
    for i in range(1, n + 1):
        x, w, y, st = tot.GetBinCenter(i), 0.5 * tot.GetBinWidth(i), tot.GetBinContent(i), tot.GetBinError(i)
        eu, ed = math.sqrt(st ** 2 + up2[i]), math.sqrt(st ** 2 + dn2[i])
        g_syst.SetPoint(i - 1, x, y); g_syst.SetPointError(i - 1, w, w, ed, eu)
        if y > 0:
            g_rband.SetPoint(i - 1, x, 1.0); g_rband.SetPointError(i - 1, w, w, ed / y, eu / y)
            g_rstat.SetPoint(i - 1, x, 1.0); g_rstat.SetPointError(i - 1, w, w, st / y, st / y)
    g_syst.SetFillColorAlpha(ROOT.kGray + 2, 0.8); g_syst.SetFillStyle(3013)
    g_rband.SetFillColorAlpha(ROOT.kGray + 2, 0.8); g_rband.SetFillStyle(3013)
    g_rstat.SetFillColorAlpha(ROOT.kOrange, 0.6); g_rstat.SetFillStyle(1001)
    keeper += [g_syst, g_rband, g_rstat]

    ordered = sorted(groups, key=lambda g: groups[g].Integral())
    stack = ROOT.THStack("st_" + reg, "")
    for g in ordered:
        col = root_color(GROUPS[g][0])
        groups[g].SetFillColor(col); groups[g].SetLineColor(col)
        stack.Add(groups[g])
    keeper.append(stack)

    c = ROOT.TCanvas("c_" + reg, "c", 800, 900)
    p1 = ROOT.TPad("p1", "p1", 0, 0.3, 1, 1)
    p2 = ROOT.TPad("p2", "p2", 0, 0, 1, 0.3)
    p1.SetBottomMargin(0.02); p2.SetTopMargin(0.02); p2.SetBottomMargin(0.35)
    p1.Draw(); p2.Draw()
    keeper += [c, p1, p2]

    p1.cd(); p1.SetLogy()
    h_dummy = tot.Clone("dummy_" + reg); h_dummy.Reset(); h_dummy.SetTitle("")
    h_dummy.GetYaxis().SetTitle("Events / bin")
    h_dummy.GetYaxis().SetTitleSize(0.05); h_dummy.GetYaxis().SetTitleOffset(1.1)
    h_dummy.GetXaxis().SetLabelSize(0)
    h_dummy.SetMinimum(0.1); h_dummy.SetMaximum(1e4)
    h_dummy.GetXaxis().SetRangeUser(x_min, x_max)
    h_dummy.Draw("HIST"); keeper.append(h_dummy)
    stack.Draw("HIST SAME")
    g_syst.Draw("SAME E2")
    if not blind:
        data.SetMarkerStyle(20); data.SetMarkerSize(1.2); data.SetLineColor(ROOT.kBlack)
        data.Draw("PE SAME"); keeper.append(data)

    leg = ROOT.TLegend(0.55, 0.58, 0.92, 0.88)
    leg.SetBorderSize(0); leg.SetFillStyle(0); leg.SetTextSize(0.035)
    for g in reversed(ordered):
        leg.AddEntry(groups[g], GROUPS[g][1], "f")
    if not blind:
        leg.AddEntry(data, "Data", "pe")
    leg.AddEntry(g_syst, band_label, "f")
    if not blind:
        leg.AddEntry(g_rstat, "Stat. Unc.", "f")
    leg.Draw(); keeper.append(leg)

    lt = ROOT.TLatex(); lt.SetNDC()
    lt.SetTextFont(61); lt.SetTextSize(0.045); lt.DrawLatex(0.12, 0.93, "CMS")
    lt.SetTextFont(52); lt.SetTextSize(0.035); lt.DrawLatex(0.21, 0.93, config.CMS_SUBLABEL)
    lt.SetTextFont(42); lt.SetTextSize(0.030); lt.SetTextAlign(31)
    lt.DrawLatex(0.90, 0.93, config.LUMI_LABEL)
    lt.SetTextAlign(11); lt.SetTextFont(62); lt.SetTextSize(0.06); lt.DrawLatex(0.18, 0.82, "ee")
    lt.SetTextFont(42); lt.SetTextSize(0.060); lt.DrawLatex(0.18, 0.75, LABEL2[reg])
    lt.SetTextSize(0.030); lt.DrawLatex(0.18, 0.695, "charge flip applied to DY only")
    keeper.append(lt)
    p1.RedrawAxis()

    p2.cd()
    h_frame = h_dummy.Clone("frame_" + reg); h_frame.Reset()
    h_frame.GetYaxis().SetTitle("Data / MC")
    h_frame.SetMinimum(0.7); h_frame.SetMaximum(1.3)
    h_frame.GetXaxis().SetTitle("m(lljj) (GeV)")
    h_frame.GetXaxis().SetTitleSize(0.1); h_frame.GetXaxis().SetLabelSize(0.11)
    h_frame.GetYaxis().SetTitleSize(0.1); h_frame.GetYaxis().SetLabelSize(0.11)
    h_frame.GetYaxis().SetTitleOffset(0.45); h_frame.GetYaxis().SetNdivisions(505)
    h_frame.GetXaxis().SetRangeUser(x_min, x_max)
    h_frame.Draw("HIST"); keeper.append(h_frame)
    if blind:
        bl = ROOT.TLatex(); bl.SetNDC(); bl.SetTextAlign(22); bl.SetTextSize(0.18); bl.SetTextFont(62)
        bl.DrawLatex(0.5, 0.5, "Blinded"); keeper.append(bl)
    else:
        g_rstat.Draw("SAME E2"); g_rband.Draw("SAME E2")
        r = data.Clone("ratio_" + reg); r.Divide(tot)
        for i in range(1, r.GetNbinsX() + 1):          # data-only error in the ratio
            t = tot.GetBinContent(i)
            r.SetBinError(i, data.GetBinError(i) / t if t > 0 else 0.0)
        r.SetMarkerStyle(20); r.SetMarkerSize(1.2); r.SetLineColor(ROOT.kBlack)
        draw_ratio_points(r, 0.7, 1.3, x_min, x_max, keeper)
        keeper.append(r)
        ln = ROOT.TLine(x_min, 1, x_max, 1); ln.SetLineStyle(2); ln.Draw(); keeper.append(ln)
    p2.RedrawAxis()

    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "ss_template_%s_plot.png" % reg)
    c.SaveAs(out); c.SaveAs(out.replace(".png", ".pdf"))
    c.Close()
    print("%-13s total %8.1f%s" % (reg, tot.Integral(), "" if blind else
                                   "   data %8.1f  data/pred %.3f" % (data.Integral(), data.Integral() / tot.Integral())))


if __name__ == "__main__":
    o = sys.argv[1] if len(sys.argv) > 1 else H + "/plots_cutstyle"
    fdp = sys.argv[2] if len(sys.argv) > 2 else FITDIAG
    f = ROOT.TFile.Open(H + "/ddss_dyonly_sf.root")
    fd = ROOT.TFile.Open(fdp) if os.path.isfile(fdp) else None
    for reg in ["rEESR_SS", "rDYEECR_SS"]:
        draw(f, reg, o, fd)
    print("written to", o)
