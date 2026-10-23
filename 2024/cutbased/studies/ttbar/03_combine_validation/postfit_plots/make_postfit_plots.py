#!/usr/bin/env python3
"""Postfit WR-mass plots for every channel in the CR+SR simultaneous fit.

Reads the shapes combine writes with --saveShapes --saveWithUncertainties
(shapes_fit_b / shapes_prefit, x-axis = bin index) and re-labels the x axis with
the real mass edges taken from the scenario shapes file.

  python3 make_postfit_plots.py <fitDiagnostics.root> <scenario shapes.root> <outdir> [label]
"""
import os, sys, array, math
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.TH1.AddDirectory(False)

LUMI = "109.8 fb^{-1}"
# draw order = stack order (bottom -> top), matching the cutbased plotter colours
PROCS = [("Others",    ROOT.TColor.GetColor("#94A4A2"), "Others"),
         ("Nonprompt", ROOT.TColor.GetColor("#E76300"), "Nonprompt"),
         ("Flip",      ROOT.TColor.GetColor("#B9AC70"), "Charge mis-ID"),
         ("DYJets",    ROOT.TColor.GetColor("#5790FC"), "DY+jets"),
         ("TT",        ROOT.TColor.GetColor("#F89C20"), "t#bar{t}+tW")]

BOOSTED = lambda ch: ch.startswith("b")
XTITLE  = lambda ch: "m_{#font[12]{l}J} [GeV]" if BOOSTED(ch) else "m_{#font[12]{ll}jj} [GeV]"

TITLE = {
    "rEESR_OS": "Resolved ee SR (OS)",   "rEESR_SS": "Resolved ee SR (SS)",
    "rMuMuSR_OS": "Resolved #mu#mu SR (OS)", "rMuMuSR_SS": "Resolved #mu#mu SR (SS)",
    "bEESR": "Boosted ee SR",            "bMuMuSR": "Boosted #mu#mu SR",
    "rDYEECR_OS": "Resolved ee DY CR (OS)",  "rDYEECR_SS": "Resolved ee DY CR (SS)",
    "rDYMuMuCR_OS": "Resolved #mu#mu DY CR (OS)", "rDYMuMuCR_SS": "Resolved #mu#mu DY CR (SS)",
    "bDYEECR": "Boosted ee DY CR",       "bDYMuMuCR": "Boosted #mu#mu DY CR",
    "bFlvEMuCR": "Boosted e+#mu-jet flavour CR", "bFlvMuECR": "Boosted #mu+e-jet flavour CR",
    "rFlvCR": "Resolved e#mu flavour CR",
}
IS_SR = lambda ch: "SR" in ch


def real_edges(shapes, ch):
    """Physical bin edges from the scenario file; the open last bin is closed at a
    display value so one 3200-8000 bin does not swallow the plot."""
    for p in ("TT", "DYJets", "data_obs"):
        h = shapes.Get("%s/%s" % (ch, p))
        if alive(h):
            e = [h.GetBinLowEdge(i) for i in range(1, h.GetNbinsX() + 2)]
            if len(e) >= 3:
                e[-1] = e[-2] + 2.0 * (e[-2] - e[-3])       # display-only cap
            return e
    return None


def alive(o):
    """PyROOT hands back a null-wrapped object for a missing key; touching it raises."""
    try:
        return bool(o) and o.InheritsFrom("TH1") or bool(o) and o.InheritsFrom("TGraph")
    except (ReferenceError, AttributeError):
        return False


def rebuild(h_idx, edges):
    """Copy a bin-index histogram onto the real mass axis."""
    if not alive(h_idx) or edges is None:
        return None
    out = ROOT.TH1D(h_idx.GetName() + "_m", "", len(edges) - 1, array.array("d", edges))
    for i in range(1, out.GetNbinsX() + 1):
        out.SetBinContent(i, h_idx.GetBinContent(i))
        out.SetBinError(i, h_idx.GetBinError(i))
    return out


def graph_to_hist(g, edges, name):
    if not alive(g) or edges is None:
        return None
    h = ROOT.TH1D(name, "", len(edges) - 1, array.array("d", edges))
    for i in range(g.GetN()):
        b = i + 1
        if b > h.GetNbinsX():
            break
        h.SetBinContent(b, g.GetY()[i])
        h.SetBinError(b, math.sqrt(max(g.GetY()[i], 0.0)))
    return h


def band_graph(h, relative):
    """Postfit uncertainty as a TGraphAsymmErrors. A TH1 drawn with "e2" fills from the
    pad floor once it carries a fill style, which hides the stack, so use a graph."""
    g = ROOT.TGraphAsymmErrors()
    n = 0
    for i in range(1, h.GetNbinsX() + 1):
        v, e = h.GetBinContent(i), h.GetBinError(i)
        x, w = h.GetBinCenter(i), 0.5 * h.GetBinWidth(i)
        if relative:
            if v <= 0:
                continue
            g.SetPoint(n, x, 1.0); g.SetPointError(n, w, w, e / v, e / v)
        else:
            g.SetPoint(n, x, v); g.SetPointError(n, w, w, e, e)
        n += 1
    g.SetFillColor(ROOT.kBlack); g.SetFillStyle(3354); g.SetLineWidth(0); g.SetMarkerSize(0)
    return g


def cms_header(pad, extra):
    pad.cd()
    l = ROOT.TLatex(); l.SetNDC(); l.SetTextFont(61); l.SetTextSize(0.075)
    l.DrawLatex(0.16, 0.90, "CMS")
    l.SetTextFont(52); l.SetTextSize(0.057)
    l.DrawLatex(0.27, 0.90, extra)
    l.SetTextFont(42); l.SetTextSize(0.055)
    l.DrawLatex(0.63, 0.94, "%s (13.6 TeV)" % LUMI)


def draw_channel(fd, shapes, ch, outdir, tag):
    edges = real_edges(shapes, ch)
    post = fd.Get("shapes_fit_b/%s" % ch)
    pre = fd.Get("shapes_prefit/%s" % ch)
    try:
        ok_post = bool(post) and post.InheritsFrom("TDirectory")
    except (ReferenceError, AttributeError):
        ok_post = False
    try:
        ok_pre = bool(pre) and pre.InheritsFrom("TDirectory")
    except (ReferenceError, AttributeError):
        ok_pre = False
    if not ok_post or not edges:
        return None
    if not ok_pre:
        pre = None

    stack = ROOT.THStack("st_%s" % ch, "")
    legend_items, hists = [], []
    for proc, col, lab in PROCS:
        h = rebuild(post.Get(proc), edges)
        if not h or h.Integral() <= 0:
            continue
        h.SetFillColor(col); h.SetLineColor(ROOT.kBlack); h.SetLineWidth(1)
        stack.Add(h); hists.append(h); legend_items.append((h, lab))

    tot = rebuild(post.Get("total_background"), edges)
    tot_pre = rebuild(pre.Get("total_background"), edges) if pre else None
    data = graph_to_hist(post.Get("data"), edges, "data_%s" % ch)
    if tot is None or data is None:
        return None

    c = ROOT.TCanvas("c_%s" % ch, "", 800, 800)
    p1 = ROOT.TPad("p1", "", 0, 0.30, 1, 1); p1.SetBottomMargin(0.02)
    p2 = ROOT.TPad("p2", "", 0, 0.00, 1, 0.30); p2.SetTopMargin(0.02); p2.SetBottomMargin(0.36)
    for p in (p1, p2):
        p.SetLeftMargin(0.14); p.SetRightMargin(0.04); p.SetTicks(1, 1); p.Draw()

    p1.cd(); p1.SetLogy()
    ymax = max(data.GetMaximum(), tot.GetMaximum())
    frame = p1.DrawFrame(edges[0], 0.05, edges[-1], ymax * 200)
    frame.GetYaxis().SetTitle("Events / bin")
    frame.GetYaxis().SetTitleSize(0.055); frame.GetYaxis().SetTitleOffset(1.25)
    frame.GetYaxis().SetLabelSize(0.045); frame.GetXaxis().SetLabelSize(0)
    stack.Draw("hist same")

    band = band_graph(tot, relative=False)
    band.Draw("2 same")
    if tot_pre:
        tot_pre.SetLineColor(ROOT.kRed + 1); tot_pre.SetLineStyle(2); tot_pre.SetLineWidth(2)
        tot_pre.SetFillStyle(0); tot_pre.Draw("hist same")
    data.SetMarkerStyle(20); data.SetMarkerSize(1.0); data.SetLineColor(ROOT.kBlack)
    data.Draw("e0 p same")
    p1.RedrawAxis()

    leg = ROOT.TLegend(0.55, 0.56, 0.94, 0.86)
    leg.SetBorderSize(0); leg.SetFillStyle(0); leg.SetTextSize(0.040); leg.SetNColumns(2)
    leg.AddEntry(data, "Asimov (blind)" if IS_SR(ch) else "Data", "pe")
    for h, lab in reversed(legend_items):
        leg.AddEntry(h, lab, "f")
    leg.AddEntry(band, "Postfit unc.", "f")
    if tot_pre:
        leg.AddEntry(tot_pre, "Prefit total", "l")
    leg.Draw()
    cms_header(p1, "Preliminary")
    t = ROOT.TLatex(); t.SetNDC(); t.SetTextFont(42); t.SetTextSize(0.042)
    t.DrawLatex(0.17, 0.80, TITLE.get(ch, ch))
    t.SetTextSize(0.034)
    t.DrawLatex(0.17, 0.755, "#scale[0.9]{%s}" % tag)
    t.SetTextSize(0.030)
    t.DrawLatex(0.17, 0.715, "#scale[0.9]{#it{last bin: overflow, drawn at reduced width}}")

    p2.cd()
    r = data.Clone("r_%s" % ch); r.Divide(tot)
    rb = band_graph(tot, relative=True)
    f2 = p2.DrawFrame(edges[0], 0.0, edges[-1], 2.0)
    f2.GetYaxis().SetTitle("Data / postfit"); f2.GetYaxis().SetNdivisions(505)
    f2.GetYaxis().SetTitleSize(0.13); f2.GetYaxis().SetTitleOffset(0.50); f2.GetYaxis().SetLabelSize(0.10)
    f2.GetXaxis().SetTitle(XTITLE(ch))
    f2.GetXaxis().SetTitleSize(0.14); f2.GetXaxis().SetTitleOffset(1.05); f2.GetXaxis().SetLabelSize(0.11)
    rb.Draw("2 same")
    line = ROOT.TLine(edges[0], 1, edges[-1], 1); line.SetLineStyle(2); line.Draw()
    r.SetMarkerStyle(20); r.SetMarkerSize(1.0); r.Draw("e0 p same")
    p2.RedrawAxis()

    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "postfit_%s.png" % ch)
    c.SaveAs(out); c.SaveAs(out.replace(".png", ".pdf"))
    return (ch, data.Integral(), tot.Integral(),
            tot_pre.Integral() if tot_pre else float("nan"))


def main():
    fdp, shp, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    tag = sys.argv[4] if len(sys.argv) > 4 else ""
    fd = ROOT.TFile.Open(fdp); shapes = ROOT.TFile.Open(shp)
    chans = [k.GetName() for k in fd.Get("shapes_fit_b").GetListOfKeys()]
    order = [c for c in chans if IS_SR(c)] + [c for c in chans if not IS_SR(c)]
    print("%-15s%12s%12s%12s%10s" % ("channel", "data", "postfit", "prefit", "d/post"))
    for ch in order:
        try:
            r = draw_channel(fd, shapes, ch, outdir, tag)
        except Exception as e:
            print("%-15s  SKIPPED: %s" % (ch, e)); continue
        if r:
            print("%-15s%12.1f%12.1f%12.1f%10.4f" %
                  (r[0], r[1], r[2], r[3], r[1] / r[2] if r[2] else 0))
    print("\nwritten to", outdir)


if __name__ == "__main__":
    main()
