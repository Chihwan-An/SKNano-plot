"""Charge-flip folder plots in the cutbased plotter style (plotter._draw).

Input: per-lepton npz dumps of the HNWR_ChargeFlip CF_Tree (tree_<sample>.npz, made by
BDT/SR/test/scripts/chargeflip_tree_dump.py). Output tree:

  out/Resolve/DY/chargeflip/<DYCR|Zwin>/<prompt|nonprompt>/<electron|muon>/<same|diff>/tc<0|1|2>/
      pt_plot.png, eta_plot.png            stacked MC + data + Data/MC (plotter._draw)
      pt_eta_2d_ratio_plot.png             Data/MC map, pT x signed eta, values printed
      pt_eta_2d_data_plot.png, pt_eta_2d_mc_plot.png
  .../<electron|muon>/fliprate/tc<k>/   MC only: P(flip) = N(reco!=gen)/N(gen-matched) vs pT, |eta|, 2D

Categories: same/diff folders use the PAIR tightCharge category min(tc1,tc2) = 0/1/2 (tc2 = both leptons
tight-charge), and both leptons of the pair are entered; fliprate/ uses the lepton's OWN tightCharge.
  MC   same = reco charge == gen charge, diff = reco != gen (gen-matched leptons)
  data has no gen charge: diff <- both leptons of SS pairs, same <- leptons of OS pairs.
  So the MC stack in each folder is the full prediction for that data selection:
  diff : leptons of OBSERVED SS pairs: flip lepton | partner of a flipped lepton | non-flip SS (WZ/ZZ, nonprompt, tt) | unmatched
  same : leptons of OBSERVED OS pairs: reco==gen by process | double flip (both flipped -> seen as OS) | unmatched
  prompt/nonprompt (genPartFlav 1,15 vs the rest): the highlighted origin is stacked in colour,
  the other origin as one grey component, so Data/MC stays the ratio to the full MC.

Weights: MC x trigger lumi x PU (no lepton SFs). Bands are MC stat only.
"""
import argparse
import glob
import os
import types

import numpy as np
import ROOT

import config
import plotter

PT = np.array([53, 60, 80, 100, 130, 170, 220, 300, 400, 600, 1000.])
# signed eta (scEta for electrons): the flip probability is not assumed +/- symmetric
ETA1 = np.linspace(-2.5, 2.5, 21)
ETA2 = {"electron": np.array([-2.5, -2.0, -1.479, -0.8, 0, 0.8, 1.479, 2.0, 2.5]),
        "muon": np.array([-2.4, -2.1, -1.2, -0.9, 0, 0.9, 1.2, 2.1, 2.4])}

DIFF_GROUPS = {
    "flip":      ("kRed",       "flip (reco #neq gen)"),
    "dflip":     ("kMagenta+2", "double flip"),
    "partner":   ("kOrange",    "partner of flipped"),
    "nonflipSS": ("kBlue",      "non-flip SS"),
    "unmatched": ("kGray+1",    "unmatched"),
    "other":     ("kGray",      "other origin"),
}
SAME_GROUPS = {
    "DYJets":    ("kYellow",   "Drell-Yan reco = gen"),
    "TT":        ("kRed",      "T#bar{T}+tW reco = gen"),
    "Nonprompt": ("kGreen+2",  "Nonprompt reco = gen"),
    "Others":    ("kBlue",     "Others reco = gen"),
    "dflip":     ("kMagenta+2", "double flip"),
    "unmatched": ("kGray+1",   "unmatched"),
    "other":     ("kGray",     "other origin"),
}


def group_of(base):
    b = base.replace("tree_Skim_HNWR_", "")
    if b.startswith("DYto2L"):
        return "DYJets"
    if b.startswith(("EGamma", "Muon")):
        return "DATA"
    if b.startswith("WRtoN"):     # 시그널은 배경이 아니다. 아래 return 이 catch-all 이라 없으면 Nonprompt 로 샌다.
        return "SIG"
    if b.startswith(("TTto2L2Nu", "TWminusto2L2Nu", "TbarWplusto2L2Nu")):
        return "TT"
    if b.startswith(("WWto", "WZto", "ZZto", "TTLL", "TTLNu")):
        return "Others"
    return "Nonprompt"


def load(dump_dir, ch):
    acc = {}
    for p in sorted(glob.glob(os.path.join(dump_dir, "tree_*.npz"))):
        g = group_of(os.path.basename(p))
        z = np.load(p)
        m = z["channel"] == ch
        if m.sum() == 0:
            continue
        for k in z.files:
            acc.setdefault(k, []).append(z[k][m])
        acc.setdefault("grp", []).append(np.full(m.sum(), g))
    d = {k: np.concatenate(v) for k, v in acc.items()}
    d["weight"] = np.where(d["grp"] == "DATA", 1.0, d["weight"])
    return d


def leptons(d, sel):
    m = sel(d)
    out = {}
    for i, j in ((1, 2), (2, 1)):
        # gen charge: NanoAOD genPartIdx match when the dump carries it (photon match -> unmatched), else the dR match
        def gen_charge(k):
            if f"l{k}_genChargeIdx" in d:
                g = d[f"l{k}_genChargeIdx"][m]; return np.where(g == 0, -999.0, g)
            return d[f"l{k}_genCharge"][m]
        gc = gen_charge(i)
        gcp = gen_charge(j)
        fl = d[f"l{i}_genPartFlav"][m].astype(int)
        out.setdefault("pt", []).append(d[f"l{i}_pt"][m])
        out.setdefault("eta", []).append(d[f"l{i}_scEta"][m])   # signed; scEta (== eta for muons)
        out.setdefault("tc", []).append(d[f"l{i}_tightCharge"][m].astype(int))
        # pair-level tightCharge category: the worse of the two leptons (tc2 = both tight)
        out.setdefault("tcmin", []).append(np.minimum(d[f"l{i}_tightCharge"][m], d[f"l{j}_tightCharge"][m]).astype(int))
        out.setdefault("matched", []).append(gc > -900)
        out.setdefault("same", []).append((gc > -900) & (d[f"l{i}_charge"][m] == gc))
        out.setdefault("pflip", []).append((gcp > -900) & (d[f"l{j}_charge"][m] != gcp))
        out.setdefault("prompt", []).append(np.isin(fl, [1, 15]))
        out.setdefault("ss", []).append(d["isSS"][m] > 0)
        out.setdefault("grp", []).append(d["grp"][m])
        out.setdefault("w", []).append(d["weight"][m])
    return {k: np.concatenate(v) for k, v in out.items()}


def th1(name, edges, x, w=None):
    h = ROOT.TH1D(name, "", len(edges) - 1, np.asarray(edges, dtype="float64"))
    h.Sumw2()
    cnt, _ = np.histogram(x, edges, weights=w)
    err2, _ = np.histogram(x, edges, weights=(w * w) if w is not None else None)
    for i in range(len(cnt)):
        h.SetBinContent(i + 1, cnt[i])
        h.SetBinError(i + 1, np.sqrt(err2[i]))
    return h


def stat_graphs(h_total, syst2=None):
    """(band on the stack, ratio band, ratio stat band). Without syst2 all three are MC stat only; with syst2
    (per-bin systematic variance, same binning) the first two are stat (+) syst and the third stays stat."""
    g_syst = ROOT.TGraphAsymmErrors()
    g_rb = ROOT.TGraphAsymmErrors()
    g_rs = ROOT.TGraphAsymmErrors()
    n = 0
    for i in range(1, h_total.GetNbinsX() + 1):
        y = h_total.GetBinContent(i)
        e = h_total.GetBinError(i)
        et = np.sqrt(e * e + (syst2[i - 1] if syst2 is not None else 0.0))
        x = h_total.GetBinCenter(i)
        w = 0.5 * h_total.GetBinWidth(i)
        g_syst.SetPoint(n, x, y)
        g_syst.SetPointError(n, w, w, et, et)
        r = e / y if y > 0 else 0.0
        rt = et / y if y > 0 else 0.0
        g_rb.SetPoint(n, x, 1.0)
        g_rb.SetPointError(n, w, w, rt, rt)
        g_rs.SetPoint(n, x, 1.0)
        g_rs.SetPointError(n, w, w, r, r)
        n += 1
    return g_syst, g_rb, g_rs


def draw_1d(outdir, stem, groups, comps, data_mask, L, var, edges, xlabel, label1, label2, logx, syst2=None, rmin=0.7, rmax=1.3, blind=False, ymin=None):
    """comps: [(key, mask)]; groups: {key: (colour, label)} in plotter's BACKGROUND_GROUPS format.
    syst2: optional per-bin systematic variance of the total prediction (drawn as the stat (+) syst band)."""
    keeper = []
    ROOT.TH1.AddDirectory(False)
    saved = config.BACKGROUND_GROUPS
    config.BACKGROUND_GROUPS = groups
    try:
        group_hists = {g: None for g in groups}
        h_total = None
        for key, m in comps:
            h = th1(f"h_{stem}_{key}", edges, L[var][m], L["w"][m])
            group_hists[key] = h if h.Integral() > 0 else None
            keeper.append(h)
            if h_total is None:
                h_total = h.Clone(f"h_total_{stem}")
            else:
                h_total.Add(h)
        h_data = th1(f"h_data_{stem}", edges, L[var][data_mask])
        keeper += [h_total, h_data]
        g_syst, g_rb, g_rs = stat_graphs(h_total, syst2)
        keeper += [g_syst, g_rb, g_rs]
        ymin = ymin if ymin is not None else (0.05 if var == "pt" else 0.5)
        args = types.SimpleNamespace(output=stem, logy=True, ymin=ymin, ymax=None, rmin=rmin, rmax=rmax,
                                     xlabel=xlabel, hist=var, label1=label1, label2=label2)
        # ROOT log-x is set on the pads by _draw only for log-y; set it on the canvas by hand afterwards
        plotter._draw(args, h_total, h_data, group_hists, g_syst, g_rb, g_rs,
                      float(edges[0]), float(edges[-1]), blind, os.path.join(outdir, stem), keeper)
    finally:
        config.BACKGROUND_GROUPS = saved
    return h_total, h_data


def cms_header(label1, label2):
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(61); latex.SetTextSize(0.045); latex.DrawLatex(0.10, 0.93, "CMS")
    latex.SetTextFont(52); latex.SetTextSize(0.035); latex.DrawLatex(0.19, 0.93, config.CMS_SUBLABEL)
    latex.SetTextFont(42); latex.SetTextSize(0.030); latex.SetTextAlign(31)
    latex.DrawLatex(0.88, 0.93, config.LUMI_LABEL)
    latex.SetTextAlign(11); latex.SetTextFont(62); latex.SetTextSize(0.035)
    latex.DrawLatex(0.10, 0.965, label1 + "   " + label2)
    return latex


def draw_2d(outdir, stem, comps, data_mask, L, ptb, etab, label1, label2):
    keeper = []
    ROOT.gStyle.SetPaintTextFormat(".2f")
    h_mc = ROOT.TH2D(f"h2mc_{stem}", "", len(ptb) - 1, ptb, len(etab) - 1, etab)
    h_da = ROOT.TH2D(f"h2da_{stem}", "", len(ptb) - 1, ptb, len(etab) - 1, etab)
    h_mc.Sumw2(); h_da.Sumw2()
    for key, m in comps:
        for x, y, w in zip(L["pt"][m], L["eta"][m], L["w"][m]):
            h_mc.Fill(min(x, ptb[-1] - 1e-3), y, w)
    for x, y in zip(L["pt"][data_mask], L["eta"][data_mask]):
        h_da.Fill(min(x, ptb[-1] - 1e-3), y)
    h_r = h_da.Clone(f"h2r_{stem}")
    h_r.Divide(h_mc)
    for h, tag, ztitle, fmt in [(h_da, "data", "Data leptons", ".0f"), (h_mc, "mc", "MC leptons", ".1f"), (h_r, "ratio", "Data / MC", ".2f")]:
        c = ROOT.TCanvas(f"c2_{stem}_{tag}", "c", 900, 700)
        c.SetRightMargin(0.15); c.SetLeftMargin(0.10); c.SetTopMargin(0.10)
        c.SetLogx()
        if tag != "ratio":
            c.SetLogz()
        ROOT.gStyle.SetPaintTextFormat(fmt)
        h.GetXaxis().SetTitle("p_{T} (GeV)"); h.GetXaxis().SetMoreLogLabels(); h.GetXaxis().SetNoExponent()
        h.GetYaxis().SetTitle("#eta_{SC}" if label1 == "electron" else "#eta")
        h.GetZaxis().SetTitle(ztitle)
        if tag == "ratio":
            h.SetMinimum(0.7); h.SetMaximum(1.3)
        h.SetMarkerSize(1.1)
        if tag == "ratio":
            # COLZ skips bins below the z minimum (text included). Paint a clipped copy for the
            # colours and the real histogram for the numbers, so out-of-range bins stay readable.
            h_col = h.Clone(h.GetName() + "_col")
            for bx in range(1, h_col.GetNbinsX() + 1):
                for by in range(1, h_col.GetNbinsY() + 1):
                    v = h_col.GetBinContent(bx, by)
                    if v > 0:
                        h_col.SetBinContent(bx, by, min(max(v, 0.7 + 1e-6), 1.3))
            h_col.SetMinimum(0.7); h_col.SetMaximum(1.3)
            h_col.Draw("COLZ")
            h.SetMinimum(-1111); h.SetMaximum(-1111)   # TEXT also skips bins outside [min,max]
            h.Draw("TEXTE SAME")
            keeper.append(h_col)
        else:
            h.Draw("COLZ TEXT")
        keeper.append(cms_header(label1, label2))
        c.SaveAs(os.path.join(outdir, f"{stem}_{tag}_plot.png"))
        c.Close()
        keeper.append(c)


def draw_fliprate(outdir, L, mask_all, ptb, etab, label1, label2, chname):
    """MC only: per-lepton flip probability = w(reco != gen) / w(all gen-matched) vs pT, |eta| and 2D."""
    keeper = []
    flip = mask_all & ~L["same"]
    for var, edges, xlabel, logx in [("pt", ptb, "p_{T} (GeV)", True), ("eta", ETA1, "#eta_{SC}" if chname == "electron" else "#eta", False)]:
        h_all = th1(f"hfr_all_{var}", edges, L[var][mask_all], L["w"][mask_all])
        h_fl = th1(f"hfr_fl_{var}", edges, L[var][flip], L["w"][flip])
        g = ROOT.TGraphAsymmErrors()
        n = 0
        for i in range(1, h_all.GetNbinsX() + 1):
            N = h_all.GetBinContent(i)
            if N <= 0:
                continue
            p = h_fl.GetBinContent(i) / N
            # binomial error with the effective (unweighted-equivalent) count
            neff = N * N / (h_all.GetBinError(i) ** 2) if h_all.GetBinError(i) > 0 else 0.0
            e = (max(p * (1 - p), 1e-12) / neff) ** 0.5 if neff > 0 else 0.0
            g.SetPoint(n, h_all.GetBinCenter(i), p)
            g.SetPointError(n, 0.5 * h_all.GetBinWidth(i), 0.5 * h_all.GetBinWidth(i), e, e)
            n += 1
        c = ROOT.TCanvas(f"cfr_{var}", "c", 800, 700)
        c.SetLeftMargin(0.13); c.SetTopMargin(0.10); c.SetLogy()
        if logx:
            c.SetLogx()
        fr = ROOT.TH1D(f"frame_{var}", "", 1, edges[0], edges[-1])
        fr.SetMinimum(1e-5 if chname == "electron" else 1e-7)
        fr.SetMaximum(1.0)
        fr.GetXaxis().SetTitle(xlabel); fr.GetYaxis().SetTitle("P(flip) = N(reco #neq gen) / N(matched)")
        fr.GetYaxis().SetTitleOffset(1.3)
        if logx:
            fr.GetXaxis().SetMoreLogLabels(); fr.GetXaxis().SetNoExponent()
        fr.Draw()
        g.SetMarkerStyle(20); g.SetMarkerSize(1.1); g.SetLineWidth(2)
        g.Draw("P SAME")
        keeper += [c, fr, g, h_all, h_fl, cms_header(label1, label2)]
        c.SaveAs(os.path.join(outdir, f"{var}_fliprate_plot.png"))
        c.Close()
    # 2D
    h2a = ROOT.TH2D("h2fr_all", "", len(ptb) - 1, ptb, len(etab) - 1, etab); h2a.Sumw2()
    h2f = ROOT.TH2D("h2fr_fl", "", len(ptb) - 1, ptb, len(etab) - 1, etab); h2f.Sumw2()
    for x, y, w in zip(L["pt"][mask_all], L["eta"][mask_all], L["w"][mask_all]):
        h2a.Fill(min(x, ptb[-1] - 1e-3), y, w)
    for x, y, w in zip(L["pt"][flip], L["eta"][flip], L["w"][flip]):
        h2f.Fill(min(x, ptb[-1] - 1e-3), y, w)
    h2r = h2f.Clone("h2fr_r"); h2r.Divide(h2f, h2a, 1, 1, "B")
    c = ROOT.TCanvas("cfr_2d", "c", 900, 700)
    c.SetRightMargin(0.15); c.SetLeftMargin(0.10); c.SetTopMargin(0.10); c.SetLogx(); c.SetLogz()
    ROOT.gStyle.SetPaintTextFormat(".1e")
    h2r.GetXaxis().SetTitle("p_{T} (GeV)"); h2r.GetXaxis().SetMoreLogLabels(); h2r.GetXaxis().SetNoExponent()
    h2r.GetYaxis().SetTitle("#eta_{SC}" if chname == "electron" else "#eta"); h2r.GetZaxis().SetTitle("P(flip)")
    h2r.SetMinimum(1e-5 if chname == "electron" else 1e-7); h2r.SetMaximum(1.0); h2r.SetMarkerSize(0.7)
    h2r.Draw("COLZ TEXTE")
    keeper += [c, h2a, h2f, h2r, cms_header(label1, label2)]
    c.SaveAs(os.path.join(outdir, "pt_eta_2d_fliprate_plot.png"))
    c.Close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dumps", required=True, help="directory with tree_<sample>.npz")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out/Resolve/DY/chargeflip"))
    ap.add_argument("--regions", default="DYCR,Zwin")
    args = ap.parse_args()
    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gErrorIgnoreLevel = ROOT.kWarning

    REG = {"DYCR": (lambda d: d["isDYCR"] > 0, "Resolved DY CR"),
           "Zwin": (lambda d: (d["m_l1l2"] >= 60) & (d["m_l1l2"] < 150), "Z window, no jet cut")}
    for ch, chname, lep in [(11, "electron", "e"), (13, "muon", "#mu")]:
        D = load(args.dumps, ch)
        for region in args.regions.split(","):
            sel, rlab = REG[region]
            L = leptons(D, sel)
            isD = L["grp"] == "DATA"
            mc = ~isD
            for origin in ["prompt", "nonprompt"]:
                orig = L["prompt"] if origin == "prompt" else ~L["prompt"]
                for tc in [0, 1, 2]:
                    l2 = f"{rlab}, {origin}"
                    # ---- MC-only flip rate, per lepton: the lepton's OWN tightCharge
                    tl = L["tc"] == tc
                    outdir = os.path.join(args.out, region, origin, chname, "fliprate", f"tc{tc}")
                    os.makedirs(outdir, exist_ok=True)
                    draw_fliprate(outdir, L, mc & tl & L["matched"] & orig, PT, ETA2[chname], chname, f"flip rate, lepton tc={tc}, {l2}", chname)
                    # ---- same / diff folders: PAIR-level category min(tc1, tc2) == tc, both leptons entered
                    t = L["tcmin"] == tc
                    # ---- diff: data = leptons of SS pairs
                    # every MC component is restricted to OBSERVED SS pairs, like the data: a double
                    # flip of a gen-OS pair is observed as OS and belongs to the same/OS folder.
                    ssm = mc & t & L["ss"]
                    flip = ssm & L["matched"] & ~L["same"]
                    partner = ssm & L["same"] & L["pflip"]
                    nonflip = ssm & L["same"] & ~L["pflip"]
                    unm = ssm & ~L["matched"]
                    comps = [("flip", flip & orig), ("partner", partner & orig),
                             ("nonflipSS", nonflip & orig), ("unmatched", unm & orig), ("other", ssm & ~orig)]
                    outdir = os.path.join(args.out, region, origin, chname, "diff", f"tc{tc}")
                    os.makedirs(outdir, exist_ok=True)
                    dmask = isD & t & L["ss"]
                    draw_1d(outdir, "pt", DIFF_GROUPS, comps, dmask, L, "pt", PT, f"{lep} p_{{T}} (GeV), SS pairs", f"{lep}{lep} diff, min tc={tc}", l2, True)
                    draw_1d(outdir, "eta", DIFF_GROUPS, comps, dmask, L, "eta", ETA1, f"{lep} #eta, SS pairs", f"{lep}{lep} diff, min tc={tc}", l2, False)
                    draw_2d(outdir, "pt_eta_2d", comps, dmask, L, PT, ETA2[chname], chname, f"diff, min tc={tc}, {l2}")
                    # ---- same: data = leptons of OS pairs
                    comps = [(g, mc & t & L["same"] & ~L["ss"] & (L["grp"] == g) & orig) for g in ["DYJets", "TT", "Nonprompt", "Others"]]
                    comps += [("dflip", mc & t & ~L["ss"] & L["matched"] & ~L["same"] & orig),
                              ("unmatched", mc & t & ~L["ss"] & ~L["matched"] & orig), ("other", mc & t & ~L["ss"] & ~orig)]
                    outdir = os.path.join(args.out, region, origin, chname, "same", f"tc{tc}")
                    os.makedirs(outdir, exist_ok=True)
                    dmask = isD & t & ~L["ss"]
                    draw_1d(outdir, "pt", SAME_GROUPS, comps, dmask, L, "pt", PT, f"{lep} p_{{T}} (GeV), OS pairs", f"{lep}{lep} same, min tc={tc}", l2, True)
                    draw_1d(outdir, "eta", SAME_GROUPS, comps, dmask, L, "eta", ETA1, f"{lep} #eta, OS pairs", f"{lep}{lep} same, min tc={tc}", l2, False)
                    draw_2d(outdir, "pt_eta_2d", comps, dmask, L, PT, ETA2[chname], chname, f"same, min tc={tc}, {l2}")
            print("done", chname, region, flush=True)


if __name__ == "__main__":
    main()
