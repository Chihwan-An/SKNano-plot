#!/usr/bin/env python3
"""Postfit m(lljj)/m(lJ) plots drawn in the plot/cutbased/out style and binning.

Same inputs as make_postfit_plots.py (fitDiagnostics with --saveShapes
--saveWithUncertainties, plus the scenario shapes file for the real mass edges),
but the look follows plotter._draw (colours/labels from config.py, 800x900
canvas, Data/MC 0.7-1.3 ratio) and the binning follows the out/ specs:

  resolved 800,1000,1200,1400,1600,2000,2400,2800,3200,8000
  boosted  800,1000,1200,1500,1800,8000
  x range  CR 800-4000, SR 800-8000 (last bin carries the overflow)

The fit bins are finer in the SR tails (e.g. rEESR_OS 3200,3561,4643,5533,8000),
so they are summed into the out bins. The postfit uncertainty of a merged bin is
taken from shapes_fit_b/<ch>/total_covar (sum of the covariance block), not a
quadrature sum -- the bins are strongly correlated after the fit.

Needs a fit run with --ignoreCovWarning (work_srcr_unc/run_unc_fit.sh): fit_b has
covQual 2 and combine otherwise stores zero postfit errors.

SR data_obs is the Asimov pseudo-data, so SRs are drawn blinded as in out/.

  python3 make_postfit_plots_cutstyle.py <fitDiagnostics.root> <shapes.root> <outdir> [label]
"""
import array
import math
import os
import sys

import ROOT

CUTBASED = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, CUTBASED)
import config                                            # noqa: E402
from plotter import root_color, draw_ratio_points        # noqa: E402

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.TH1.AddDirectory(False)

BINS_RESOLVED = [800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 8000]
BINS_BOOSTED = [800, 1000, 1200, 1500, 1800, 8000]

# config.BACKGROUND_GROUPS + the SS-only charge-flip process (colour from chargeflip_apply_plots.py)
GROUPS = dict(config.BACKGROUND_GROUPS)
GROUPS["Flip"] = ("kOrange", "Charge flip")

# channel -> (label1, label2)
LABELS = {
    "rEESR_OS": ("ee", "Resolved SR (OS)"),           "rEESR_SS": ("ee", "Resolved SR (SS)"),
    "rMuMuSR_OS": ("#mu#mu", "Resolved SR (OS)"),     "rMuMuSR_SS": ("#mu#mu", "Resolved SR (SS)"),
    "bEESR": ("ee", "Boosted SR"),                    "bMuMuSR": ("#mu#mu", "Boosted SR"),
    "rDYEECR_OS": ("ee", "Resolved DY CR (OS)"),      "rDYEECR_SS": ("ee", "Resolved DY CR (SS)"),
    "rDYMuMuCR_OS": ("#mu#mu", "Resolved DY CR (OS)"), "rDYMuMuCR_SS": ("#mu#mu", "Resolved DY CR (SS)"),
    "bDYEECR": ("ee", "Boosted DY CR"),               "bDYMuMuCR": ("#mu#mu", "Boosted DY CR"),
    "bFlvEMuCR": ("e#mu", "Boosted Flavour CR"),      "bFlvMuECR": ("#mu e", "Boosted Flavour CR"),
    "rFlvCR": ("e#mu", "Resolved Flavour CR"),
}

is_sr = lambda ch: "SR" in ch
is_boosted = lambda ch: ch.startswith("b")


def y_range(ch):
    """ymin/ymax from the matching out/ spec lines (SS regions are too small for them)."""
    if ch.endswith("_SS"):
        return 0.1, 1e4
    if is_sr(ch):
        return (3, 1e5) if is_boosted(ch) else (1, 1e5)
    if "Flv" in ch:
        return (1, 2e3) if is_boosted(ch) else (1, 1e5)
    return 1, 1e6


def alive(o):
    try:
        return bool(o) and (o.InheritsFrom("TH1") or o.InheritsFrom("TGraph"))
    except (ReferenceError, AttributeError):
        return False


def fit_edges(shapes, ch):
    for p in ("TT", "DYJets", "data_obs"):
        h = shapes.Get("%s/%s" % (ch, p))
        if alive(h):
            return [h.GetBinLowEdge(i) for i in range(1, h.GetNbinsX() + 2)]
    return None


def snap_target(fit, target, ch):
    """An out edge that is not a fit edge (rEESR_SS has 3132 where out has 3200)
    cannot be reproduced; move it to the nearest fit edge and say so."""
    out = list(target)
    for k in range(1, len(out) - 1):
        near = min(fit[1:-1], key=lambda f: abs(f - out[k]))
        if abs(near - out[k]) > 1e-6:
            print("   %s: out edge %g not in the fit binning -> %g" % (ch, out[k], near))
            out[k] = near
    return out


def bin_map(fit, target):
    """fit bin index (0-based) -> target bin index. Every inner target edge is a fit
    edge (snap_target); the fit's last bin (whatever its nominal upper edge) is the
    overflow bin and goes to the target's last bin."""
    out = []
    for lo in fit[:-1]:
        j = max(k for k in range(len(target) - 1) if target[k] <= lo + 1e-6)
        out.append(j)
    return out


def merged(h_idx, mapping, target, name, covar=None):
    """Bin-index histogram -> TH1D on the out binning. With covar the bin errors are
    sqrt(sum of the covariance block), otherwise the quadrature sum."""
    h = ROOT.TH1D(name, "", len(target) - 1, array.array("d", target))
    var = [0.0] * len(target)
    for i, j in enumerate(mapping):
        h.SetBinContent(j + 1, h.GetBinContent(j + 1) + h_idx.GetBinContent(i + 1))
        if covar is None:
            var[j] += h_idx.GetBinError(i + 1) ** 2
    if covar is not None:
        for i, ji in enumerate(mapping):
            for k, jk in enumerate(mapping):
                if ji == jk:
                    var[ji] += covar.GetBinContent(i + 1, k + 1)
    for j in range(len(target) - 1):
        h.SetBinError(j + 1, math.sqrt(max(var[j], 0.0)))
    return h


def data_hist(g, mapping, target, name):
    h = ROOT.TH1D(name, "", len(target) - 1, array.array("d", target))
    for i in range(min(g.GetN(), len(mapping))):
        h.SetBinContent(mapping[i] + 1, h.GetBinContent(mapping[i] + 1) + g.GetY()[i])
    for j in range(1, h.GetNbinsX() + 1):
        h.SetBinError(j, math.sqrt(max(h.GetBinContent(j), 0.0)))
    return h


def get_dir(fd, path):
    d = fd.Get(path)
    try:
        return d if (bool(d) and d.InheritsFrom("TDirectory")) else None
    except (ReferenceError, AttributeError):
        return None


def draw_channel(fd, shapes, ch, outdir, tag):
    post, pre = get_dir(fd, "shapes_fit_b/%s" % ch), get_dir(fd, "shapes_prefit/%s" % ch)
    fe = fit_edges(shapes, ch)
    if post is None or fe is None:
        return None
    target = snap_target(fe, BINS_BOOSTED if is_boosted(ch) else BINS_RESOLVED, ch)
    mapping = bin_map(fe, target)
    x_min, x_max = 800.0, (8000.0 if is_sr(ch) else 4000.0)
    ymin, ymax = y_range(ch)
    blind = is_sr(ch)
    keeper = []

    groups = {}
    for g in GROUPS:
        h = post.Get(g)
        if alive(h):
            hm = merged(h, mapping, target, "h_%s_%s" % (ch, g))
            if hm.Integral() > 0:
                groups[g] = hm
    covar = post.Get("total_covar")
    tot = merged(post.Get("total_background"), mapping, target, "tot_%s" % ch,
                 covar if alive(covar) else None)
    tot_pre = None
    if pre is not None and alive(pre.Get("total_background")):
        tot_pre = merged(pre.Get("total_background"), mapping, target, "pre_%s" % ch)
    data = data_hist(post.Get("data"), mapping, target, "data_%s" % ch)

    ordered = sorted(groups, key=lambda g: groups[g].Integral())
    stack = ROOT.THStack("st_" + ch, "")
    for g in ordered:
        col = root_color(GROUPS[g][0])
        groups[g].SetFillColor(col); groups[g].SetLineColor(col)
        stack.Add(groups[g])

    n = tot.GetNbinsX()
    g_unc, g_rband = ROOT.TGraphAsymmErrors(n), ROOT.TGraphAsymmErrors(n)
    for i in range(1, n + 1):
        x, w, y, e = tot.GetBinCenter(i), 0.5 * tot.GetBinWidth(i), tot.GetBinContent(i), tot.GetBinError(i)
        g_unc.SetPoint(i - 1, x, y); g_unc.SetPointError(i - 1, w, w, e, e)
        if y > 0:
            g_rband.SetPoint(i - 1, x, 1.0); g_rband.SetPointError(i - 1, w, w, e / y, e / y)
    for g in (g_unc, g_rband):
        g.SetFillColorAlpha(ROOT.kGray + 2, 0.8); g.SetFillStyle(3013)

    c = ROOT.TCanvas("c_" + ch, "c", 800, 900)
    p1 = ROOT.TPad("p1", "p1", 0, 0.3, 1, 1)
    p2 = ROOT.TPad("p2", "p2", 0, 0, 1, 0.3)
    p1.SetBottomMargin(0.02); p2.SetTopMargin(0.02); p2.SetBottomMargin(0.35)
    p1.Draw(); p2.Draw()
    keeper += [c, p1, p2, stack, g_unc, g_rband]

    p1.cd(); p1.SetLogy()
    h_dummy = tot.Clone("dummy_" + ch); h_dummy.Reset()
    h_dummy.GetYaxis().SetTitle("Events / bin")
    h_dummy.GetYaxis().SetTitleSize(0.05); h_dummy.GetYaxis().SetTitleOffset(1.1)
    h_dummy.GetXaxis().SetLabelSize(0)
    h_dummy.SetMinimum(ymin); h_dummy.SetMaximum(ymax)
    h_dummy.GetXaxis().SetRangeUser(x_min, x_max)
    h_dummy.Draw("HIST"); keeper.append(h_dummy)
    stack.Draw("HIST SAME")
    g_unc.Draw("SAME E2")
    if tot_pre:
        tot_pre.SetLineColor(ROOT.kBlack); tot_pre.SetLineStyle(2); tot_pre.SetLineWidth(2)
        tot_pre.SetFillStyle(0); tot_pre.Draw("HIST SAME")
    if not blind:
        data.SetMarkerStyle(20); data.SetMarkerSize(1.2); data.SetLineColor(ROOT.kBlack)
        data.Draw("PE SAME")

    leg = ROOT.TLegend(0.55, 0.58, 0.92, 0.88)
    leg.SetBorderSize(0); leg.SetFillStyle(0); leg.SetTextSize(0.035)
    for g in reversed(ordered):
        leg.AddEntry(groups[g], GROUPS[g][1], "f")
    if not blind:
        leg.AddEntry(data, "Data", "pe")
    # fit_b with covQual < 3 comes back with zero postfit errors (combine does not
    # sample a forced-pos-def covariance); an empty hatch in the legend would lie.
    if any(tot.GetBinError(i) > 0 for i in range(1, n + 1)):
        leg.AddEntry(g_unc, "Stat #oplus Syst Unc. (postfit)", "f")
    else:
        print("   %s: postfit uncertainties are all zero -- band omitted" % ch)
    if tot_pre:
        leg.AddEntry(tot_pre, "Prefit total", "l")
    leg.Draw(); keeper.append(leg)

    label1, label2 = LABELS.get(ch, ("", ch))
    lt = ROOT.TLatex(); lt.SetNDC()
    lt.SetTextFont(61); lt.SetTextSize(0.045); lt.DrawLatex(0.12, 0.93, "CMS")
    lt.SetTextFont(52); lt.SetTextSize(0.035); lt.DrawLatex(0.21, 0.93, config.CMS_SUBLABEL)
    lt.SetTextFont(42); lt.SetTextSize(0.030); lt.SetTextAlign(31)
    lt.DrawLatex(0.90, 0.93, config.LUMI_LABEL)
    lt.SetTextAlign(11); lt.SetTextFont(62); lt.SetTextSize(0.06); lt.DrawLatex(0.18, 0.82, label1)
    lt.SetTextFont(42); lt.SetTextSize(0.060); lt.DrawLatex(0.18, 0.75, label2)
    lt.SetTextSize(0.030); lt.DrawLatex(0.18, 0.695, "B-only postfit" + (", " + tag if tag else ""))
    keeper.append(lt)
    p1.RedrawAxis()

    p2.cd()
    h_frame = h_dummy.Clone("frame_" + ch); h_frame.Reset()
    h_frame.GetYaxis().SetTitle("Data / Postfit")
    h_frame.SetMinimum(0.7); h_frame.SetMaximum(1.3)
    h_frame.GetXaxis().SetTitle("m(lJ) (GeV)" if is_boosted(ch) else "m(lljj) (GeV)")
    h_frame.GetXaxis().SetTitleSize(0.1); h_frame.GetXaxis().SetLabelSize(0.11)
    h_frame.GetYaxis().SetTitleSize(0.1); h_frame.GetYaxis().SetLabelSize(0.11)
    h_frame.GetYaxis().SetTitleOffset(0.45); h_frame.GetYaxis().SetNdivisions(505)
    h_frame.GetXaxis().SetRangeUser(x_min, x_max)
    h_frame.Draw("HIST"); keeper.append(h_frame)
    if blind:
        bl = ROOT.TLatex(); bl.SetNDC(); bl.SetTextAlign(22); bl.SetTextSize(0.18); bl.SetTextFont(62)
        bl.DrawLatex(0.5, 0.5, "Blinded"); keeper.append(bl)
    else:
        g_rband.Draw("SAME E2")
        r = data.Clone("ratio_" + ch); r.Divide(tot)
        for i in range(1, r.GetNbinsX() + 1):          # data-only error in the ratio
            t = tot.GetBinContent(i)
            r.SetBinError(i, data.GetBinError(i) / t if t > 0 else 0.0)
        r.SetMarkerStyle(20); r.SetMarkerSize(1.2); r.SetLineColor(ROOT.kBlack)
        draw_ratio_points(r, 0.7, 1.3, x_min, x_max, keeper)
        keeper.append(r)
        ln = ROOT.TLine(x_min, 1, x_max, 1); ln.SetLineStyle(2); ln.Draw(); keeper.append(ln)
    p2.RedrawAxis()

    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "postfit_%s_plot.png" % ch)
    c.SaveAs(out); c.SaveAs(out.replace(".png", ".pdf"))
    c.Close()
    return ch, data.Integral(), tot.Integral(), tot_pre.Integral() if tot_pre else float("nan")


def main():
    fdp, shp, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    tag = sys.argv[4] if len(sys.argv) > 4 else ""
    fd, shapes = ROOT.TFile.Open(fdp), ROOT.TFile.Open(shp)
    chans = [k.GetName() for k in fd.Get("shapes_fit_b").GetListOfKeys()]
    order = [c for c in chans if is_sr(c)] + [c for c in chans if not is_sr(c)]
    print("%-15s%12s%12s%12s%10s" % ("channel", "data", "postfit", "prefit", "d/post"))
    for ch in order:
        try:
            r = draw_channel(fd, shapes, ch, outdir, tag)
        except Exception as e:
            print("%-15s  SKIPPED: %s" % (ch, e)); continue
        if r:
            print("%-15s%12.1f%12.1f%12.1f%10.4f" % (r[0], r[1], r[2], r[3], r[1] / r[2] if r[2] else 0))
    print("\nwritten to", outdir)


if __name__ == "__main__":
    main()
