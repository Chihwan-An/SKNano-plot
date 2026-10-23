#!/usr/bin/env python3
"""AN2019_083 App. J analogue for 2024: data-driven ttbar+tW from the e-mu sideband.

Input : emu_method_hists_2024.root (make_emu_method_hists_2024.py)
Output: <out>/ratio_<cat>.png                 SR / e-mu sideband ratio of the tt+tW MC, constant fit        (Figs. 97-99)
        <out>/<region>_<low|high>_plot.png    e-mu sideband data vs simulation                              (Figs. 100-102)
        <out>/lowmass_dd_<region>_plot.png    low-mass same-flavour regions with the data-driven tt+tW      (Figs. 103-104)
        <out>/obs_pred_<region>.png           obs/pred vs mass for e-mu systematics of 5-60%                (Figs. 105-128)
        <out>/emu_ratio_fit_2024.tex, signal_contamination_2024.tex, emu_method_2024.json                   (Tables 55, 54)
    ./condor/in_container.sh python3 make_emu_method_plots_2024.py --in DIR --out DIR      (from plot/cutbased)
"""
import argparse, json, os, re, sys, types
import numpy as np, ROOT
PC = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased"
sys.path.insert(0, PC)
import config, plotter                    # noqa: E402
import chargeflip_plots as cfp            # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--inp", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0); ROOT.TH1.AddDirectory(False); ROOT.gErrorIgnoreLevel = ROOT.kWarning
F = ROOT.TFile.Open(os.path.join(a.inp, "emu_method_hists_2024.root"))
GROUPS = ["DYJets", "TT", "Nonprompt", "Others"]
LUMI = config.LUMI_LABEL


def get(reg, rng, name):
    h = F.Get(f"{reg}/{rng}/{name}")
    if not h:
        return None
    h = h.Clone(f"{reg}_{rng}_{name}_{np.random.randint(1e9)}"); h.SetDirectory(0); return h


def acc(tot, h, name="acc"):
    """tot += h (tot may be None)"""
    if h is None:
        return tot
    if tot is None:
        tot = h.Clone(f"{name}_{np.random.randint(1e9)}"); tot.SetDirectory(0); return tot
    tot.Add(h); return tot


def names(reg, rng):
    d = F.Get(f"{reg}/{rng}"); return [k.GetName() for k in d.GetListOfKeys()] if d else []


def systs(reg, rng):
    return sorted({re.sub(r"_(Up|Down)$", "", n.split("_", 1)[1]) for n in names(reg, rng) if re.match(r"^(%s)_.*_(Up|Down)$" % "|".join(GROUPS), n)})


def syst2(reg, rng, groups):
    """per-bin systematic variance of the summed `groups` from the weight variations (max(|up-nom|, |down-nom|) each, in quadrature)"""
    nom = None
    for g in groups:
        h = get(reg, rng, g)
        nom = acc(nom, h)
    nb = nom.GetNbinsX(); v = np.zeros(nb)
    for s in systs(reg, rng):
        d = np.zeros(nb)
        for ud in ("Up", "Down"):
            tot = None
            for g in groups:
                h = get(reg, rng, f"{g}_{s}_{ud}") or get(reg, rng, g)
                tot = acc(tot, h)
            d = np.maximum(d, np.abs([tot.GetBinContent(i + 1) - nom.GetBinContent(i + 1) for i in range(nb)]))
        v += d ** 2
    return v


def header(sim=True, x1=0.12, x2=0.90, y=0.93):
    t = ROOT.TLatex(); t.SetNDC(); t.SetTextFont(61); t.SetTextSize(0.045); t.DrawLatex(x1, y, "CMS")
    t.SetTextFont(52); t.SetTextSize(0.035); t.DrawLatex(x1 + 0.09, y, ("Simulation " if sim else "") + config.CMS_SUBLABEL)
    t.SetTextFont(42); t.SetTextSize(0.030); t.SetTextAlign(31); t.DrawLatex(x2, y, LUMI if not sim else "2024 (13.6 TeV)")
    return t


OUT = {"ratio_fit": {}, "signal_contamination": {}, "lowmass_closure": {}}

# ---------------------------------------------------------------- (1) SR / e-mu ratio of the tt+tW MC, Figs. 97-99
RATIOS = {"resolved": [("Res_EE", "Res_EM", ROOT.kRed, "ee/e#mu", "ee"), ("Res_MM", "Res_EM", ROOT.kBlue, "#mu#mu/e#mu", "mm")],
          "boosted_mujet": [("Boost_MM", "Boost_EMJ", ROOT.kBlue, "#mu#mu/e#mu", "mm")],
          "boosted_ejet": [("Boost_EE", "Boost_MEJ", ROOT.kRed, "ee/#mue", "ee")]}
for cat, pairs in RATIOS.items():
    for rng in ("low", "high"):
        keep = []; c = ROOT.TCanvas(f"c_{cat}_{rng}", "", 700, 650); c.SetLeftMargin(0.13); c.SetBottomMargin(0.12); c.SetTopMargin(0.09); c.SetRightMargin(0.05)
        leg = ROOT.TLegend(0.42, 0.70, 0.93, 0.89); leg.SetTextSize(0.030); leg.SetFillStyle(0)
        first = True
        for num, den, col, lab, tag in pairs:
            r = get(num, rng, "TT"); r.Divide(get(den, rng, "TT")); r.SetLineColor(col); r.SetMarkerColor(col); r.SetLineWidth(2); r.SetMarkerSize(0)
            fit = ROOT.TF1(f"f_{cat}_{rng}_{tag}", "pol0", r.GetXaxis().GetXmin(), r.GetXaxis().GetXmax()); fit.SetLineColor(col); fit.SetLineStyle(2); fit.SetLineWidth(2)
            r.Fit(fit, "QN0"); p0, e0, chi2, ndf = fit.GetParameter(0), fit.GetParError(0), fit.GetChisquare(), fit.GetNDF()
            ymax = 1.5 if cat == "resolved" else 2.0
            if first:
                r.SetMinimum(0); r.SetMaximum(ymax); r.GetYaxis().SetTitle("Ratio"); r.GetYaxis().SetTitleSize(0.05); r.GetYaxis().SetTitleOffset(1.1)
                r.GetXaxis().SetTitle("m_{lljj} (GeV)" if cat == "resolved" else "m_{lJ} (GeV)"); r.GetXaxis().SetTitleSize(0.045); r.Draw("E HIST")
                r.Draw("E SAME"); first = False
            else:
                r.Draw("E HIST SAME"); r.Draw("E SAME")
            fit.Draw("SAME")
            leg.AddEntry(r, lab, "l"); leg.AddEntry(fit, f"p0 = {p0:.3f} #pm {e0:.3f} (#chi^{{2}}/ndf = {chi2:.1f}/{ndf})", "l")
            OUT["ratio_fit"].setdefault(cat, {}).setdefault(rng, {})[tag] = {"p0": p0, "err": e0, "chi2": chi2, "ndf": ndf}
            keep += [r, fit]
        leg.Draw(); t = header(sim=True, x1=0.13, x2=0.95)
        c.SaveAs(os.path.join(a.out, f"ratio_{cat}_{rng}.png")); c.Close()

# ---------------------------------------------------------------- helper: stack plot in the cutbased plotter format
def draw_stack(stem, hists, hdata, s2, label1, label2, xlabel, groups=None, rmin=0.5, rmax=1.5, logy=True):
    keeper = []; saved = config.BACKGROUND_GROUPS
    config.BACKGROUND_GROUPS = groups or saved
    try:
        gh = {g: hists.get(g) for g in config.BACKGROUND_GROUPS}
        tot = None
        for g, h in gh.items():
            tot = acc(tot, h, f"tot_{stem}")
        gs, grb, grs = cfp.stat_graphs(tot, s2); keeper += list(gh.values()) + [tot, hdata, gs, grb, grs]
        args = types.SimpleNamespace(output=stem, logy=logy, ymin=0.5, ymax=None, rmin=rmin, rmax=rmax, xlabel=xlabel, hist=stem, label1=label1, label2=label2)
        ed = tot.GetXaxis()
        plotter._draw(args, tot, hdata, gh, gs, grb, grs, ed.GetXmin(), ed.GetXmax(), False, os.path.join(a.out, stem), keeper)
    finally:
        config.BACKGROUND_GROUPS = saved
    return tot


# ---------------------------------------------------------------- (2) e-mu sideband data vs simulation, Figs. 100-102
SB = {"Res_EM": ("e#mu", "Resolved", "m(lljj) (GeV)"), "Boost_EMJ": ("e+#mu-jet", "Boosted", "m(lJ) (GeV)"), "Boost_MEJ": ("#mu+e-jet", "Boosted", "m(lJ) (GeV)")}
for reg, (l1, topo, xl) in SB.items():
    for rng, l2 in (("low", f"{topo} low-mass CR"), ("high", f"{topo} flavor CR")):
        hs = {g: get(reg, rng, g) for g in GROUPS}
        draw_stack(f"{reg}_{rng}", hs, get(reg, rng, "data_obs"), syst2(reg, rng, GROUPS), l1, l2, xl)

# ---------------------------------------------------------------- (3) data-driven tt+tW in the low-mass same-flavour regions, Figs. 103-128
DD = {"Res_EE": ("Res_EM", "resolved", "ee", "ee", "Resolved low-mass CR", "m(lljj) (GeV)"),
      "Res_MM": ("Res_EM", "resolved", "mm", "#mu#mu", "Resolved low-mass CR", "m(lljj) (GeV)"),
      "Boost_EE": ("Boost_MEJ", "boosted_ejet", "ee", "ee", "Boosted low-mass CR", "m(lJ) (GeV)"),
      "Boost_MM": ("Boost_EMJ", "boosted_mujet", "mm", "#mu#mu", "Boosted low-mass CR", "m(lJ) (GeV)")}
DDGROUPS = dict(config.BACKGROUND_GROUPS); DDGROUPS["TT"] = ("kRed", "t#bar{t}+tW (e#mu data)")
for reg, (sb, cat, tag, l1, l2, xl) in DD.items():
    R = OUT["ratio_fit"][cat]["low"][tag]["p0"]; eR = OUT["ratio_fit"][cat]["low"][tag]["err"]
    dd = get(sb, "low", "data_obs")
    for g in ("DYJets", "Nonprompt", "Others"):
        dd.Add(get(sb, "low", g), -1.0)                      # pure tt+tW in the sideband: data - other backgrounds (MC)
    dd.Scale(R)
    hs = {g: get(reg, "low", g) for g in ("DYJets", "Nonprompt", "Others")}; hs["TT"] = dd
    data = get(reg, "low", "data_obs")
    s2 = syst2(reg, "low", ["DYJets", "Nonprompt", "Others"])
    tot = draw_stack(f"lowmass_dd_{reg}", hs, data, s2, l1, l2, xl, groups=DDGROUPS)
    nb = tot.GetNbinsX(); edges = [tot.GetXaxis().GetBinLowEdge(i + 1) for i in range(nb)] + [tot.GetXaxis().GetXmax()]
    obs = np.array([data.GetBinContent(i + 1) for i in range(nb)]); pred = np.array([tot.GetBinContent(i + 1) for i in range(nb)])
    estat = np.array([tot.GetBinError(i + 1) for i in range(nb)]); ddv = np.array([dd.GetBinContent(i + 1) for i in range(nb)])
    mctt = get(reg, "low", "TT")
    OUT["lowmass_closure"][reg] = {"edges": edges, "obs": obs.tolist(), "pred": pred.tolist(), "pred_stat": estat.tolist(), "tt_dd": ddv.tolist(),
                                   "tt_mc": [mctt.GetBinContent(i + 1) for i in range(nb)], "R": R, "R_err": eR,
                                   "obs_over_pred_total": float(obs.sum() / pred.sum())}
    # obs/pred for an e-mu systematic of X% on the data-driven tt+tW, X = 5..60 (Figs. 105-128)
    c = ROOT.TCanvas(f"c_op_{reg}", "", 1600, 1200); c.Divide(4, 3, 0.002, 0.002); keep = []
    for ip, X in enumerate(range(5, 65, 5)):
        pad = c.cd(ip + 1); pad.SetLeftMargin(0.14); pad.SetBottomMargin(0.14); pad.SetTopMargin(0.09); pad.SetRightMargin(0.04)
        fr = ROOT.TH1D(f"fr_{reg}_{X}", "", nb, np.array(edges, float)); fr.SetMinimum(0); fr.SetMaximum(2)
        fr.GetYaxis().SetTitle("Obs. / Pred."); fr.GetXaxis().SetTitle(xl); fr.GetYaxis().SetTitleSize(0.055); fr.GetXaxis().SetTitleSize(0.055)
        fr.GetYaxis().SetLabelSize(0.05); fr.GetXaxis().SetLabelSize(0.05); fr.Draw("AXIS")
        gst = ROOT.TGraphAsymmErrors(); gto = ROOT.TGraphAsymmErrors(); gr = ROOT.TGraphAsymmErrors()
        for i in range(nb):
            x = 0.5 * (edges[i] + edges[i + 1]); w = 0.5 * (edges[i + 1] - edges[i])
            rs = estat[i] / pred[i] if pred[i] > 0 else 0; rt = np.hypot(estat[i], 0.01 * X * ddv[i]) / pred[i] if pred[i] > 0 else 0
            gst.SetPoint(i, x, 1); gst.SetPointError(i, w, w, rs, rs); gto.SetPoint(i, x, 1); gto.SetPointError(i, w, w, rt, rt)
            if pred[i] > 0:
                gr.SetPoint(gr.GetN(), x, obs[i] / pred[i]); gr.SetPointError(gr.GetN() - 1, 0, 0, np.sqrt(obs[i]) / pred[i], np.sqrt(obs[i]) / pred[i])
        gto.SetFillColor(ROOT.kGray); gst.SetFillColor(ROOT.kOrange + 7); gto.Draw("E2 SAME"); gst.Draw("E2 SAME")
        ln = ROOT.TLine(edges[0], 1, edges[-1], 1); ln.Draw(); gr.SetMarkerStyle(20); gr.SetMarkerSize(0.8); gr.Draw("PZ SAME")
        t = ROOT.TLatex(); t.SetNDC(); t.SetTextFont(62); t.SetTextSize(0.06); t.DrawLatex(0.18, 0.83, l1)
        t.SetTextFont(42); t.SetTextSize(0.05); t.DrawLatex(0.18, 0.76, l2); t.DrawLatex(0.18, 0.69, f"e#mu syst. = {X}%")
        t.SetTextFont(61); t.SetTextSize(0.05); t.DrawLatex(0.14, 0.925, "CMS"); t.SetTextFont(52); t.SetTextSize(0.04); t.DrawLatex(0.25, 0.925, config.CMS_SUBLABEL)
        t.SetTextFont(42); t.SetTextSize(0.04); t.SetTextAlign(31); t.DrawLatex(0.96, 0.925, LUMI)
        if ip == 0:
            lg = ROOT.TLegend(0.62, 0.17, 0.95, 0.34); lg.SetTextSize(0.045); lg.SetFillStyle(0); lg.SetBorderSize(0)
            lg.AddEntry(gst, "Stat.", "f"); lg.AddEntry(gto, "Stat.+syst.", "f"); lg.Draw(); keep.append(lg)
        pad.RedrawAxis(); keep += [fr, gst, gto, gr, ln, t]
    c.SaveAs(os.path.join(a.out, f"obs_pred_{reg}.png")); c.Close()

# ---------------------------------------------------------------- (4) tables
def tot_bkg(reg, rng):
    return sum(get(reg, rng, g).Integral() for g in GROUPS if get(reg, rng, g))


sigs = sorted({n for reg in SB for n in names(reg, "high") if n.startswith("sig_")}, key=lambda s: [int(x) for x in re.findall(r"\d+", s)])
for s in sigs:
    OUT["signal_contamination"][s[4:]] = {reg: 100.0 * (get(reg, "high", s).Integral() if get(reg, "high", s) else 0.0) / tot_bkg(reg, "high") for reg in SB}
with open(os.path.join(a.out, "signal_contamination_2024.tex"), "w") as fo:
    fo.write("\\begin{tabular}{llccc}\n\\hline\nChannel & $(\\mWR, \\mN)$ (\\GeVns{}) & Resolved & Boosted ($\\mu$-jet) & Boosted (e-jet) \\\\\n\\hline\n")
    for s, v in OUT["signal_contamination"].items():
        m = re.match(r"WRtoN(El|Mu)to\w+_WR(\d+)_N(\d+)", s)
        fo.write(f"{'ee' if m.group(1) == 'El' else '$\\mu\\mu$'} & ({m.group(2)}, {m.group(3)}) & {v['Res_EM']:.3f} & {v['Boost_EMJ']:.3f} & {v['Boost_MEJ']:.3f} \\\\\n")
    fo.write("\\hline\n\\end{tabular}\n")
with open(os.path.join(a.out, "emu_ratio_fit_2024.tex"), "w") as fo:
    rf = OUT["ratio_fit"]; f3 = lambda d: f"${d['p0']:.3f} \\pm {d['err']:.3f}$"
    fo.write("\\begin{tabular}{llcccc}\n\\hline\n & & \\multicolumn{2}{c}{Resolved} & \\multicolumn{2}{c}{Boosted} \\\\\nYear & Event type & ee & $\\mu\\mu$ & ee & $\\mu\\mu$ \\\\\n\\hline\n")
    for rng, lab in (("high", "$m(\\PWR) > 800\\GeV$"), ("low", "$m(\\PWR) \\leq 800\\GeV$")):
        fo.write(f"{'2024' if rng == 'high' else ''} & {lab} & {f3(rf['resolved'][rng]['ee'])} & {f3(rf['resolved'][rng]['mm'])} & {f3(rf['boosted_ejet'][rng]['ee'])} & {f3(rf['boosted_mujet'][rng]['mm'])} \\\\\n")
    fo.write("\\hline\n\\end{tabular}\n")
json.dump(OUT, open(os.path.join(a.out, "emu_method_2024.json"), "w"), indent=1)
print(json.dumps({k: OUT[k] for k in ("ratio_fit",)}, indent=1)); print({r: v["obs_over_pred_total"] for r, v in OUT["lowmass_closure"].items()})
