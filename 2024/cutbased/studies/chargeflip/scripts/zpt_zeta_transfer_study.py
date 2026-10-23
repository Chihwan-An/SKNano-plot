#!/usr/bin/env python3
"""Study 19: carry the 2-jet DY MC into the 1-jet region with a 2D factor f(Z pT, |Z eta|) and test it against 1-jet MC and DATA.

  f(cell) = N_DY^MC(1 jet) / N_DY^MC(2 jet, SR topology)   derived ONCE in the DY window 60 <= m_ll < 150  (OS, per channel)
  step A (DY window) : 2-jet DY MC x f  vs  1-jet DY MC  (m_ll, lepton pT, lepton eta -- Z pT and Z eta match by construction)
                       1-jet DATA vs [2-jet DY MC x f + 1-jet non-DY MC], and vs the native 1-jet MC
  step B (m_ll >= 400): the SAME f on the 2-jet SR DY MC  vs  1-jet DY MC,  and 1-jet DATA vs [2-jet SR DY MC x f + 1-jet non-DY MC]
2-jet = nJet >= 2, passResolved, m_lljj > 800. No 2-jet data above 150 GeV is in the cache. Z direction from the lepton momenta.
    ./condor/in_container.sh python3 studies/chargeflip/scripts/zpt_zeta_transfer_study.py
"""
import argparse, json, sys, types
from pathlib import Path
import numpy as np
BASE = Path(__file__).resolve().parents[1]; PC = Path(__file__).resolve().parents[3]
ap = argparse.ArgumentParser(); ap.add_argument("--cache", default=str(BASE / "data/zpt_zeta_transfer_events.npz")); ap.add_argument("--out-dir", default=str(BASE / "AN_rawcharge/19_zpt_zeta_2j_to_1j"))
ap.add_argument("--neff-min", type=float, default=30.0)
ap.add_argument("--factor", default="zpt_zeta", choices=["zpt_zeta", "mll_zpt"], help="zpt_zeta: f(Z pT, |Z eta|) from the DY window only (study 19). mll_zpt: f(m_ll, Z pT) from the DY MC over the whole m_ll range (study 24)")
ap.add_argument("--drll", action="store_true", help="require Delta R(l1, l2) > 0.4 in the 1-jet sample too (passResolved applies it to the 2-jet sample); output dir gets _drll")
ap.add_argument("--binning", default="coarse", choices=["coarse", "fine"], help="fine: Z pT 5 GeV to 300, 10 to 500, 25 to 700, 50 to 1000; |Z eta| 0.25 to 3 (output dir gets _fine)")
a = ap.parse_args(); OUT = Path(a.out_dir + ("_fine" if a.binning == "fine" else "") + ("_drll" if a.drll else "")); OUT.mkdir(parents=True, exist_ok=True)
d = {k: v for k, v in np.load(a.cache).items()}
for k in d:
    if d[k].dtype == np.float32: d[k] = d[k].astype("float64")
isdata = d["grp"] == "DATA"; d["weight"] = np.where(isdata, 1.0, d["weight"])
px = d["l1_pt"] * np.cos(d["l1_phi"]) + d["l2_pt"] * np.cos(d["l2_phi"]); py = d["l1_pt"] * np.sin(d["l1_phi"]) + d["l2_pt"] * np.sin(d["l2_phi"])
pz = d["l1_pt"] * np.sinh(d["l1_eta"]) + d["l2_pt"] * np.sinh(d["l2_eta"]); d["eta_ll"] = np.arcsinh(pz / np.maximum(np.hypot(px, py), 1e-9)); d["abs_eta_ll"] = np.abs(d["eta_ll"])
two = d["topo2j"].astype(bool); one = ~two
_dphi = np.abs(d["l1_phi"] - d["l2_phi"]); _dphi = np.where(_dphi > np.pi, 2 * np.pi - _dphi, _dphi); d["dR_ll"] = np.hypot(d["l1_eta"] - d["l2_eta"], _dphi)
if a.drll:
    keep = two | (d["dR_ll"] > 0.4); print("dR(ll) > 0.4 on the 1-jet sample: removes %.2f%% of the 1-jet DY MC weight" % (100 * d["weight"][one & ~keep & (d["grp"] == "DY")].sum() / d["weight"][one & (d["grp"] == "DY")].sum()))
    d = {k: v[keep] for k, v in d.items()}; two = d["topo2j"].astype(bool); one = ~two; isdata = d["grp"] == "DATA"
ZPT = np.array([0, 60, 80, 100, 125, 150, 175, 200, 250, 300, 400, 500, 700, 1000, np.inf]); ZETA = np.array([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, np.inf])
if a.binning == "fine":
    ZPT = np.concatenate([np.arange(0, 300, 5), np.arange(300, 500, 10), np.arange(500, 700, 25), np.arange(700, 1000, 50), [1000, np.inf]]).astype(float)
    ZETA = np.concatenate([np.arange(0, 3.0, 0.25), [3.0, 3.5, 4.0, np.inf]])
FX, FY, FLAB, FLO, FHI = "pt_l1l2", "abs_eta_ll", "f(Z p_{T}, |Z #eta|)", 60.0, 150.0
if a.factor == "mll_zpt":            # x axis = m_ll (fine enough that the m_ll closure inside each window is not trivial only at the window level), y axis = Z pT
    FX, FY, FLAB, FLO, FHI = "m_l1l2", "pt_l1l2", "f(m_{ll}, Z p_{T})", 60.0, np.inf
    ZETA = np.array([0, 25, 50, 75, 100, 125, 150, 175, 200, 250, 300, 400, 500, 600, 800, 1000, np.inf]); ZPT = np.array([60, 70, 80, 85, 90, 95, 100, 110, 130, 150, 200, 250, 300, 400, 450, 500, 600, 700, 800, 1000, 1300, np.inf])
WIN = {"DYwindow": (60.0, 150.0), "highmass": (400.0, np.inf)}
CH = {"EE": (11, "ee", "scEta"), "MM": (13, "#mu#mu", "eta")}


def hist2(m):
    w = d["weight"][m]; x = np.stack([d[FX][m], d[FY][m]], 1)
    n, _ = np.histogramdd(x, [ZPT, ZETA], weights=w); v, _ = np.histogramdd(x, [ZPT, ZETA], weights=w * w); return n, v


def derive(ch_code):
    """f = N1/N2 per (Z pT, |Z eta|) cell; cells with N_eff < neff-min on either side use the Z-pT-only factor, then the global one"""
    base = (d["channel"] == ch_code) & (d["grp"] == "DY") & (d["m_l1l2"] >= FLO) & (d["m_l1l2"] < FHI)
    n1, v1 = hist2(base & one); n2, v2 = hist2(base & two)
    neff = lambda n, v: np.where(v > 0, n * n / np.where(v > 0, v, 1), 0.0)
    ok = (neff(n1, v1) >= a.neff_min) & (neff(n2, v2) >= a.neff_min) & (n2 > 0)
    z1, z2 = n1.sum(1), n2.sum(1); zv1, zv2 = v1.sum(1), v2.sum(1); okz = (neff(z1, zv1) >= a.neff_min) & (neff(z2, zv2) >= a.neff_min) & (z2 > 0)
    glob = n1.sum() / n2.sum(); fz = np.where(okz, z1 / np.where(z2 > 0, z2, 1), glob)
    f = np.where(ok, n1 / np.where(n2 > 0, n2, 1), fz[:, None])
    return f, dict(f=f.tolist(), f_zpt_only=fz.tolist(), cells_2d=int(ok.sum()), cells_total=int(ok.size), global_ratio=float(glob), n1=float(n1.sum()), n2=float(n2.sum()))


def apply_f(f, m):
    iz = np.clip(np.searchsorted(ZPT, d[FX][m], side="right") - 1, 0, len(ZPT) - 2); ie = np.clip(np.searchsorted(ZETA, d[FY][m], side="right") - 1, 0, len(ZETA) - 2)
    return f[iz, ie]


sys.path.insert(0, str(PC)); import ROOT, config, plotter, chargeflip_plots as cfp            # noqa: E402
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0); ROOT.gErrorIgnoreLevel = ROOT.kWarning


def variables(chn, win):
    etav = CH[chn][2]; lo, hi = WIN[win]
    mll = np.linspace(60, 150, 19) if win == "DYwindow" else np.array([400, 450, 500, 600, 700, 800, 1000, 1300, 2000.])
    pt = np.array([53, 60, 70, 85, 100, 125, 150, 200, 250, 400, 1000.]) if win == "DYwindow" else np.array([53, 100, 150, 200, 250, 300, 400, 500, 700, 1000, 2000.])
    return [("m_l1l2", mll, "m(ll) (GeV)", "mll"), ("l1_pt", pt, "Leading Lepton p_{T} (GeV)", "leading_lep_pt"), ("l2_pt", pt, "Sub-leading Lepton p_{T} (GeV)", "subleading_lep_pt"),
            (f"l1_{etav}", np.linspace(-2.5, 2.5, 11), "Leading Lepton #eta" + ("_{SC}" if etav == "scEta" else ""), "leading_lep_eta"),
            (f"l2_{etav}", np.linspace(-2.5, 2.5, 11), "Sub-leading Lepton #eta" + ("_{SC}" if etav == "scEta" else ""), "subleading_lep_eta"),
            ("pt_l1l2", np.array([0, 50, 100, 150, 200, 300, 400, 600, 1000.]), "Dilepton p_{T} (GeV)", "dilepton_pt"), ("eta_ll", np.linspace(-5, 5, 21), "Dilepton #eta", "dilepton_eta")]


def fill(x, w, edges):
    xc = np.clip(x, edges[0], edges[-1] - 1e-6); n, _ = np.histogram(xc, edges, weights=w); v, _ = np.histogram(xc, edges, weights=w * w); return n, v


def mc_closure_plot(path, edges, xl, n_t, v_t, n_s, v_s, l1, l2, lab_t, lab_s):
    """target (1-jet DY MC, black) vs transferred source (2-jet DY MC x f, red), absolute yields, ratio = source / target"""
    c = ROOT.TCanvas("c", "", 800, 900); p1 = ROOT.TPad("p1", "", 0, 0.3, 1, 1); p2 = ROOT.TPad("p2", "", 0, 0, 1, 0.3); p1.SetBottomMargin(0.02); p2.SetTopMargin(0.02); p2.SetBottomMargin(0.35)
    p1.Draw(); p2.Draw(); p1.cd(); p1.SetLogy(); e = np.asarray(edges, float); keep = []
    def th(name, n, v, col):
        h = ROOT.TH1D(name, "", len(e) - 1, e)
        for i in range(len(n)): h.SetBinContent(i + 1, n[i]); h.SetBinError(i + 1, np.sqrt(max(v[i], 0)))
        h.SetLineColor(col); h.SetMarkerColor(col); h.SetLineWidth(2); h.SetMarkerSize(0); return h
    ht = th("ht", n_t, v_t, ROOT.kBlack); hs = th("hs", n_s, v_s, ROOT.kRed + 1); mx = max(ht.GetMaximum(), hs.GetMaximum())
    pos = [x for x in list(n_t) + list(n_s) if x > 0]; ht.SetMaximum(mx * 50); ht.SetMinimum(max(min(pos) * 0.3, 1e-3) if pos else 1e-3)
    ht.GetYaxis().SetTitle("Events / bin"); ht.GetYaxis().SetTitleSize(0.05); ht.GetYaxis().SetTitleOffset(1.1); ht.GetXaxis().SetLabelSize(0); ht.Draw("E HIST"); hs.Draw("E HIST SAME")
    lg = ROOT.TLegend(0.50, 0.72, 0.92, 0.88); lg.SetBorderSize(0); lg.SetFillStyle(0); lg.SetTextSize(0.035); lg.AddEntry(ht, lab_t, "l"); lg.AddEntry(hs, lab_s, "l"); lg.Draw()
    t = ROOT.TLatex(); t.SetNDC(); t.SetTextFont(61); t.SetTextSize(0.045); t.DrawLatex(0.12, 0.93, "CMS"); t.SetTextFont(52); t.SetTextSize(0.035); t.DrawLatex(0.21, 0.93, "Simulation " + config.CMS_SUBLABEL)
    t.SetTextFont(42); t.SetTextSize(0.030); t.SetTextAlign(31); t.DrawLatex(0.90, 0.93, "2024 (13.6 TeV)"); t.SetTextAlign(11); t.SetTextFont(62); t.SetTextSize(0.06); t.DrawLatex(0.18, 0.82, l1)
    t.SetTextFont(42); t.SetTextSize(0.045); t.DrawLatex(0.18, 0.76, l2)
    p2.cd(); r = hs.Clone("r"); r.Divide(ht); r.SetMinimum(0.5); r.SetMaximum(1.5); r.GetYaxis().SetTitle("2j#timesf / 1j"); r.GetXaxis().SetTitle(xl)
    r.GetXaxis().SetTitleSize(0.1); r.GetXaxis().SetLabelSize(0.11); r.GetYaxis().SetTitleSize(0.1); r.GetYaxis().SetLabelSize(0.11); r.GetYaxis().SetTitleOffset(0.45); r.GetYaxis().SetNdivisions(505)
    r.GetXaxis().SetLabelSize(0.11); r.Draw("E"); ln = ROOT.TLine(e[0], 1, e[-1], 1); ln.SetLineStyle(2); ln.Draw(); keep += [ht, hs, lg, t, r, ln]
    c.SaveAs(str(path)); c.Close()


def stack_plot(stem, comps, xdata, edges, xl, l1, l2, groups, outdir, rmin=0.5, rmax=1.5):
    keeper = []; saved = config.BACKGROUND_GROUPS; config.BACKGROUND_GROUPS = groups
    try:
        gh = {g: None for g in groups}; tot = None
        for g, (x, ww) in comps.items():
            hh = cfp.th1(f"h_{stem}_{g}", edges, np.clip(x, edges[0], edges[-1] - 1e-6), ww); keeper.append(hh); gh[g] = hh if hh.Integral() > 0 else None
            if tot is None: tot = hh.Clone(f"tot_{stem}"); tot.SetDirectory(0)
            else: tot.Add(hh)
        hd = cfp.th1(f"hd_{stem}", edges, np.clip(xdata, edges[0], edges[-1] - 1e-6)); gs, grb, grs = cfp.stat_graphs(tot); keeper += [tot, hd, gs, grb, grs]
        args = types.SimpleNamespace(output=stem, logy=True, ymin=0.5, ymax=None, rmin=rmin, rmax=rmax, xlabel=xl, hist=stem, label1=l1, label2=l2)
        plotter._draw(args, tot, hd, gh, gs, grb, grs, float(edges[0]), float(edges[-1]), False, str(outdir / stem), keeper)
    finally:
        config.BACKGROUND_GROUPS = saved


RES = {}
for chn, (code, lab, _) in CH.items():
    f, info = derive(code); RES[chn] = {"factor": dict(zpt_edges=[None if not np.isfinite(x) else float(x) for x in ZPT], zeta_edges=[None if not np.isfinite(x) else float(x) for x in ZETA], **info)}
    print(f"[{chn}] f ({a.factor}) derived in m_ll [{FLO:.0f}, {FHI:.0f}): 2D cells used {info['cells_2d']}/{info['cells_total']}, global N1/N2 = {info['global_ratio']:.3f}")
    for win, (lo, hi) in WIN.items():
        sel = (d["channel"] == code) & (d["m_l1l2"] >= lo) & (d["m_l1l2"] < hi); od = OUT / chn / win; (od / "mc_closure").mkdir(parents=True, exist_ok=True)
        dy1 = sel & one & (d["grp"] == "DY"); dy2 = sel & two & (d["grp"] == "DY"); dat1 = sel & one & isdata; w2f = d["weight"][dy2] * apply_f(f, dy2)
        nondy1 = {g: sel & one & (d["grp"] == g) for g in ("TT", "Nonprompt", "Others")}
        y = dict(dy_1j=float(d["weight"][dy1].sum()), dy_2j=float(d["weight"][dy2].sum()), dy_2j_x_f=float(w2f.sum()), data_1j=int(dat1.sum()), nonDY_1j=float(sum(d["weight"][m].sum() for m in nondy1.values())))
        y["transferred_over_1jMC"] = y["dy_2j_x_f"] / y["dy_1j"]; y["data_over_native_MC"] = y["data_1j"] / (y["dy_1j"] + y["nonDY_1j"]); y["data_over_transferred_MC"] = y["data_1j"] / (y["dy_2j_x_f"] + y["nonDY_1j"])
        chi = {}
        for var, edges, xl, suf in variables(chn, win):
            nt, vt = fill(d[var][dy1], d["weight"][dy1], edges); ns, vs = fill(d[var][dy2], w2f, edges)
            ok = (nt > 0) & (ns > 0); sc = nt[ok].sum() / ns[ok].sum()                                   # shape chi2 after matching the yield
            chi[suf] = dict(chi2_shape=float((((sc * ns - nt)[ok]) ** 2 / (vt + sc * sc * vs)[ok]).sum()), ndf=int(ok.sum() - 1), max_dev_shape=float(np.max(np.abs(sc * ns[ok] / nt[ok] - 1))))
            mc_closure_plot(od / "mc_closure" / f"{suf}.png", edges, xl, nt, vt, ns, vs, lab, f"{'DY window' if win == 'DYwindow' else 'm(ll) #geq 400 GeV'}, OS", "1-jet DY MC", "2-jet DY MC #times " + FLAB)
            GR = {"DYJets": ("kYellow", "DY: 2-jet MC #times f"), "TT": ("kRed", "T#bar{T}+tW"), "Nonprompt": ("kGreen+2", "Nonprompt"), "Others": ("kBlue", "Others")}
            comps = {"DYJets": (d[var][dy2], w2f)}; comps.update({g: (d[var][m], d["weight"][m]) for g, m in nondy1.items()})
            stack_plot(f"data_vs_transferred_{suf}", comps, d[var][dat1], edges, xl, lab, "1 jet, " + ("DY window" if win == "DYwindow" else "m(ll) #geq 400"), GR, od)
            GN = dict(config.BACKGROUND_GROUPS); GN["DYJets"] = ("kYellow", "DY: native 1-jet MC"); comps = {"DYJets": (d[var][dy1], d["weight"][dy1])}; comps.update({g: (d[var][m], d["weight"][m]) for g, m in nondy1.items()})
            stack_plot(f"data_vs_native_{suf}", comps, d[var][dat1], edges, xl, lab, "1 jet, " + ("DY window" if win == "DYwindow" else "m(ll) #geq 400"), GN, od)
        RES[chn][win] = dict(yields=y, mc_closure=chi)
        print(f"  {win:9s} DY 1j MC {y['dy_1j']:11.1f} | 2j MC {y['dy_2j']:9.1f} -> x f {y['dy_2j_x_f']:11.1f}  (transferred/1j MC = {y['transferred_over_1jMC']:.3f}) | 1j data {y['data_1j']} , data/native MC {y['data_over_native_MC']:.3f}, data/transferred MC {y['data_over_transferred_MC']:.3f}")
        for suf, c in chi.items(): print(f"      MC closure {suf:20s} shape chi2/ndf = {c['chi2_shape']:8.1f}/{c['ndf']:<3d} max |dev| = {100 * c['max_dev_shape']:5.1f}%")
(OUT / "summary.json").write_text(json.dumps(RES, indent=1) + "\n"); print("wrote", OUT)
