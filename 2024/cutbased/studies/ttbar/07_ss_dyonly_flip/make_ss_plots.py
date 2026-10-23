#!/usr/bin/env python3
"""Same-sign templates with charge mis-ID applied to DY only.

Flip = (OS data - non-DY OS MC) x w, and TT/Nonprompt/Others come from the full SS MC with the
measured flip SF applied to gen-flipped events -- so the ttbar part of the SS region is normalised
by R_TT_Resolved_2024 (the e-mu flavour CR) rather than by the flip weight.

  python3 make_ss_plots.py [outdir]
Reads ddss_dyonly_sf.root written by run_dyonly_sf.sh.
"""
import os, sys, array, math
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.TH1.AddDirectory(False)

H = os.path.dirname(os.path.abspath(__file__))
LUMI = "109.8 fb^{-1}"
PROCS = [("Others",    ROOT.TColor.GetColor("#94A4A2"), "Others"),
         ("Nonprompt", ROOT.TColor.GetColor("#E76300"), "Nonprompt"),
         ("DYJets",    ROOT.TColor.GetColor("#5790FC"), "DY+jets (non-flip)"),
         ("TT",        ROOT.TColor.GetColor("#F89C20"), "t#bar{t}+tW"),
         ("Flip",      ROOT.TColor.GetColor("#B9AC70"), "DY charge mis-ID")]
TITLE = {"rEESR_SS": "Resolved ee SR, same-sign", "rDYEECR_SS": "Resolved ee DY CR, same-sign"}
keep = []


def capped(h):
    """Same edges, but the open last bin closed at a display width."""
    e = [h.GetBinLowEdge(i) for i in range(1, h.GetNbinsX() + 2)]
    if len(e) >= 3:
        e[-1] = e[-2] + 2.0 * (e[-2] - e[-3])
    o = ROOT.TH1D(h.GetName() + "_c", "", len(e) - 1, array.array("d", e))
    for i in range(1, o.GetNbinsX() + 1):
        o.SetBinContent(i, h.GetBinContent(i)); o.SetBinError(i, h.GetBinError(i))
    keep.append(o); return o


def draw(reg, outdir):
    f = ROOT.TFile.Open(H + "/ddss_dyonly_sf.root")
    st = ROOT.THStack("st_" + reg, "")
    items, tot = [], None
    for p, col, lab in PROCS:
        h = f.Get("%s/%s" % (reg, p))
        if not h or h.Integral() <= 0:
            continue
        h = capped(h)
        h.SetFillColor(col); h.SetLineColor(ROOT.kBlack); h.SetLineWidth(1)
        st.Add(h); items.append((h, lab))
        if tot is None:
            tot = h.Clone("tot_" + reg)      # 첫 성분은 복제만 (Add 하면 두 번 세진다)
        else:
            tot.Add(h)
    keep.extend([st, tot])

    has_data = reg == "rDYEECR_SS"
    dh = None
    if has_data:
        d = f.Get("%s/data_obs" % reg)
        if d:
            dh = capped(d)
            for i in range(1, dh.GetNbinsX() + 1):
                dh.SetBinError(i, math.sqrt(max(dh.GetBinContent(i), 0)))

    c = ROOT.TCanvas("c_" + reg, "", 800, 800)
    p1 = ROOT.TPad("p1", "", 0, 0.30, 1, 1); p1.SetBottomMargin(0.02)
    p2 = ROOT.TPad("p2", "", 0, 0.00, 1, 0.30); p2.SetTopMargin(0.02); p2.SetBottomMargin(0.36)
    for p in (p1, p2):
        p.SetLeftMargin(0.14); p.SetRightMargin(0.04); p.SetTicks(1, 1); p.Draw()
    keep.extend([c, p1, p2])

    edges = [tot.GetBinLowEdge(i) for i in range(1, tot.GetNbinsX() + 2)]
    ymax = max(tot.GetMaximum(), dh.GetMaximum() if dh else 0)

    p1.cd(); p1.SetLogy()
    fr = p1.DrawFrame(edges[0], 0.03, edges[-1], ymax * 300)
    fr.GetYaxis().SetTitle("Events / bin"); fr.GetYaxis().SetTitleSize(0.055)
    fr.GetYaxis().SetTitleOffset(1.25); fr.GetYaxis().SetLabelSize(0.045)
    fr.GetXaxis().SetLabelSize(0)
    st.Draw("hist same")
    if dh:
        dh.SetMarkerStyle(20); dh.SetMarkerSize(1.0); dh.SetLineColor(ROOT.kBlack); dh.Draw("e0 p same")
    p1.RedrawAxis()

    leg = ROOT.TLegend(0.56, 0.55, 0.95, 0.85)
    leg.SetBorderSize(0); leg.SetFillStyle(0); leg.SetTextSize(0.040)
    if dh:
        leg.AddEntry(dh, "Data (SS)", "pe")
    for h, l in reversed(items):
        leg.AddEntry(h, l, "f")
    leg.Draw(); keep.append(leg)

    l = ROOT.TLatex(); l.SetNDC()
    l.SetTextFont(61); l.SetTextSize(0.075); l.DrawLatex(0.16, 0.90, "CMS")
    l.SetTextFont(52); l.SetTextSize(0.057); l.DrawLatex(0.27, 0.90, "Preliminary")
    l.SetTextFont(42); l.SetTextSize(0.055); l.DrawLatex(0.63, 0.94, "%s (13.6 TeV)" % LUMI)
    l.SetTextSize(0.042); l.DrawLatex(0.17, 0.82, TITLE.get(reg, reg))
    l.SetTextSize(0.034)
    l.DrawLatex(0.17, 0.775, "#scale[0.9]{#it{charge mis-ID applied to DY only}}")
    l.DrawLatex(0.17, 0.735, "#scale[0.9]{total = %.1f%s}" % (
        tot.Integral(), ("   data/MC = %.3f" % (dh.Integral() / tot.Integral())) if dh else ""))
    l.SetTextSize(0.029)
    l.DrawLatex(0.17, 0.697, "#scale[0.9]{#it{last bin: overflow, drawn at reduced width}}")
    keep.append(l)

    p2.cd()
    if dh:
        r = dh.Clone("r_" + reg); r.Divide(tot); ytit = "Data / MC"; lo, hi = 0.4, 1.6
    else:
        # SR 에는 데이터가 없다. 대신 예측 중 데이터 기반(DY flip) 비중을 보여 준다.
        r = capped(f.Get("%s/Flip" % reg)).Clone("fr_" + reg); r.Divide(tot)
        ytit = "DY flip / total"; lo, hi = 0.0, 1.0
    keep.append(r)
    f2 = p2.DrawFrame(edges[0], lo, edges[-1], hi)
    f2.GetYaxis().SetTitle(ytit); f2.GetYaxis().SetNdivisions(505)
    f2.GetYaxis().SetTitleSize(0.125); f2.GetYaxis().SetTitleOffset(0.52); f2.GetYaxis().SetLabelSize(0.10)
    f2.GetXaxis().SetTitle("m_{#font[12]{ll}jj} [GeV]")
    f2.GetXaxis().SetTitleSize(0.14); f2.GetXaxis().SetTitleOffset(1.05); f2.GetXaxis().SetLabelSize(0.11)
    if dh:
        ln = ROOT.TLine(edges[0], 1, edges[-1], 1); ln.SetLineStyle(2); ln.Draw(); keep.append(ln)
    r.SetMarkerStyle(20); r.SetMarkerSize(1.0); r.SetLineColor(ROOT.kBlack); r.SetMarkerColor(ROOT.kBlack)
    r.Draw("e0 p same")
    p2.RedrawAxis()

    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "ss_template_%s.png" % reg)
    c.SaveAs(out); c.SaveAs(out.replace(".png", ".pdf"))
    print("%-13s total %8.1f%s" % (reg, tot.Integral(),
                                   "   data %8.1f  data/pred %.3f" % (dh.Integral(), dh.Integral() / tot.Integral()) if dh else ""))


if __name__ == "__main__":
    o = sys.argv[1] if len(sys.argv) > 1 else H + "/plots"
    for reg in ["rEESR_SS", "rDYEECR_SS"]:
        draw(reg, o)
    print("written to", o)
