#!/usr/bin/env python3
"""Study 26: the 2-jet -> 1-jet transfer in the OPEN test region.  EE, OS.
  2-jet test region T : nJet >= 2, passResolved, m_lljj < 800, mll_min <= m_ll < mll_max   (data/lowmlljj_events.npz; OS and SS data are open here)
  1-jet region S      : nJet == 1, dR(l1,l2) > 0.4, same m_ll range                         (data/zpt_zeta_transfer_events.npz)
  f_g(m_ll, Z pT) = N_g^MC(S) / N_g^MC(T) per group g = DY, TT (Others/Nonprompt: the group-summed factor); f_tot = all MC.
Compared in S, all flip-weighted with w (chargeflip_ptshift_ee2024_sf3.json):
  1-jet OS DATA x w   vs   native 1-jet MC x w   vs   [2-jet OS MC x f_g] x w   vs   [2-jet OS MC x f_tot] x w   vs   [2-jet OS DATA x f_tot] x w  (possible only because T is open)
    ./condor/in_container.sh python3 studies/chargeflip/scripts/lowmlljj_to_1jet_transfer.py [--mll-min 400 --mll-max 800]"""
import argparse, json, sys, types
from pathlib import Path
import numpy as np
BASE = Path(__file__).resolve().parents[1]; PC = Path(__file__).resolve().parents[3]; T_ = PC.parents[1] / "BDT/SR/test"
ap = argparse.ArgumentParser(); ap.add_argument("--mll-min", type=float, default=400.0); ap.add_argument("--mll-max", type=float, default=800.0); ap.add_argument("--neff-min", type=float, default=30.0); a = ap.parse_args()
OUT = BASE / f"AN_rawcharge/26_lowmlljj_to_1jet_mll{a.mll_min:.0f}to{a.mll_max:.0f}"; OUT.mkdir(parents=True, exist_ok=True)
KEYS = ["m_l1l2", "pt_l1l2", "weight", "l1_pt", "l2_pt", "l1_scEta", "l2_scEta", "l1_eta", "l2_eta", "l1_phi", "l2_phi"]
z1 = np.load(BASE / "data/zpt_zeta_transfer_events.npz"); m1 = (z1["channel"] == 11) & (~z1["topo2j"].astype(bool)) & (z1["m_l1l2"] >= a.mll_min) & (z1["m_l1l2"] < a.mll_max)
z2 = np.load(BASE / "data/lowmlljj_events.npz"); m2 = (z2["isSS"] == 0) & (z2["m_l1l2"] >= a.mll_min) & (z2["m_l1l2"] < a.mll_max)
d = {k: np.concatenate([z1[k][m1].astype("float64"), z2[k][m2].astype("float64")]) for k in KEYS}; d["grp"] = np.concatenate([z1["grp"][m1], z2["grp"][m2]]); two = np.concatenate([np.zeros(int(m1.sum()), bool), np.ones(int(m2.sum()), bool)])
dphi = np.abs(d["l1_phi"] - d["l2_phi"]); dphi = np.where(dphi > np.pi, 2 * np.pi - dphi, dphi); keep = two | (np.hypot(d["l1_eta"] - d["l2_eta"], dphi) > 0.4); d = {k: v[keep] for k, v in d.items()}; two = two[keep]; one = ~two
isdata = d["grp"] == "DATA"; W = np.where(isdata, 1.0, d["weight"]); G = ("DY", "TT", "Nonprompt", "Others")
J = json.load(open(T_ / "data/chargeflip/chargeflip_ptshift_ee2024_sf3.json")); regs = list(J["rate_regions"].items()); P = np.nan_to_num(np.array(J["P"])); pe = np.array(J["pt_edges"])
sfreg = {n: tuple(v) for n, v in J["sf"]["SF3"]["regions"].items()}; SFv = dict(J["sf"]["SF3"]["SF"]); names = list(sfreg)
rs = np.array([next((k for k, n in enumerate(names) if sfreg[n][0] <= 0.5 * (lo + hi) < sfreg[n][1]), -1) for _, (lo, hi) in regs]); sf0 = np.array([SFv[n] for n in names]); pl = []
for i in (1, 2):
    ae = np.abs(d[f"l{i}_scEta"]); ie = np.full(len(ae), -1)
    for k, (_, (lo, hi)) in enumerate(regs): ie[(ae >= lo) & (ae < hi)] = k
    ip = np.clip(np.searchsorted(pe, d[f"l{i}_pt"], side="right") - 1, 0, len(pe) - 2); p = np.zeros(len(ie)); ok = ie >= 0; p[ok] = P[ie[ok], ip[ok]] * sf0[rs[ie[ok]]]; pl.append(p)
w = (pl[0] * (1 - pl[1]) + pl[1] * (1 - pl[0])) / ((1 - pl[0]) * (1 - pl[1]) + pl[0] * pl[1])
XE = np.array([x for x in (200, 225, 250, 275, 300, 350, 400, 450, 500, 550, 600, 700, 800.) if a.mll_min <= x <= a.mll_max]); YE = np.array([0, 25, 50, 75, 100, 125, 150, 200, 300, np.inf])


def factor(sel):
    h = lambda m: (np.histogram2d(d["m_l1l2"][m], d["pt_l1l2"][m], [XE, YE], weights=W[m])[0], np.histogram2d(d["m_l1l2"][m], d["pt_l1l2"][m], [XE, YE], weights=W[m] ** 2)[0])
    (n1, v1), (n2, v2) = h(sel & one), h(sel & two); neff = lambda n, v: np.where(v > 0, n * n / np.where(v > 0, v, 1), 0.0); ok = (neff(n1, v1) >= a.neff_min) & (neff(n2, v2) >= a.neff_min)
    fx = n1.sum(1) / np.where(n2.sum(1) > 0, n2.sum(1), 1); f = np.where(ok, n1 / np.where(n2 > 0, n2, 1), fx[:, None])
    return f[np.clip(np.searchsorted(XE, d["m_l1l2"], side="right") - 1, 0, len(XE) - 2), np.clip(np.searchsorted(YE, d["pt_l1l2"], side="right") - 1, 0, len(YE) - 2)], int(ok.sum()), ok.size


mc = ~isdata; f_tot, nok, ntot = factor(mc); f_grp = np.zeros(len(W)); info = {"f_tot_cells": [nok, ntot]}
for g, sel in (("DY", d["grp"] == "DY"), ("TT", d["grp"] == "TT"), ("rest", mc & (d["grp"] != "DY") & (d["grp"] != "TT"))):
    fg, k1, k2 = factor(sel); f_grp[sel] = fg[sel]; info[f"f_{g}_cells"] = [k1, k2]
D1 = one & isdata; M1 = one & mc; M2 = two & mc; D2 = two & isdata; ETA = np.array([0, 0.5, 1.0, 1.4442, 1.566, 2.0, 2.5]); R = {"factor_cells": info, "mll_edges": XE.tolist(), "zpt_edges": [None if not np.isfinite(x) else float(x) for x in YE]}
print(f"EE OS, {a.mll_min:.0f} <= m_ll < {a.mll_max:.0f}.  2-jet test region = nJet>=2, passResolved, m_lljj<800.  2D cells: {info}")
print("composition  1-jet MC:", {g: round(float(W[M1 & (d['grp'] == g)].sum()), 1) for g in G}, "| 2-jet MC:", {g: round(float(W[M2 & (d['grp'] == g)].sum()), 1) for g in G}, f"| data 1j {int(D1.sum())}, 2j {int(D2.sum())}")
SAMPLES = [("1-jet OS data", D1, np.ones(len(W))), ("native 1-jet MC", M1, W), ("2-jet OS MC x f_g (per group)", M2, W * f_grp), ("2-jet OS MC x f_tot", M2, W * f_tot), ("2-jet OS DATA x f_tot", D2, f_tot), ("(2-jet OS MC, no f)", M2, W), ("(2-jet OS data, no f)", D2, np.ones(len(W)))]
hd = np.histogram(np.abs(d["l1_scEta"][D1]), ETA)[0].astype(float); okb = hd > 0; swd = w[D1].sum(); ed = np.sqrt((w[D1] ** 2).sum())
print(f"\n  {'sample':32s} {'N':>10s} {'Sum w':>9s} {'+-':>6s} {'<w>':>8s} | 1j data/this: N      Sum w          | l1 |eta| shape chi2/4 vs 1j data | endcap frac")
for name, m, ww in SAMPLES:
    n = ww[m].sum(); sw = (ww * w)[m].sum(); e = np.sqrt(((ww * w)[m] ** 2).sum()); h = np.histogram(np.abs(d["l1_scEta"][m]), ETA, weights=ww[m])[0]; chi = float((((hd - hd[okb].sum() / h[okb].sum() * h)[okb]) ** 2 / hd[okb]).sum())
    rr = swd / sw; er = rr * np.hypot(ed / swd, e / sw); R[name] = dict(n=float(n), sumw=float(sw), sumw_err=float(e), meanw=float(sw / n), data_over_n=float(D1.sum() / n), data_over_sumw=float(rr), data_over_sumw_err=float(er), chi2_eta=chi, endcap=float(h[4:].sum() / h.sum()))
    print(f"  {name:32s} {n:10.1f} {sw:9.2f} {e:6.2f} {sw / n:8.5f} | {D1.sum() / n:12.3f}   {rr:6.3f} +- {er:5.3f} | {chi:10.1f} | {h[4:].sum() / h.sum():.3f}")
(OUT / "summary.json").write_text(json.dumps(R, indent=1) + "\n")

sys.path.insert(0, str(PC)); import ROOT, config, plotter, chargeflip_plots as cfp            # noqa: E402
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0); ROOT.gErrorIgnoreLevel = ROOT.kWarning
PT = np.array([53, 75, 100, 125, 150, 200, 250, 300, 400, 600.]); VARS = [("l1_scEta", np.linspace(-2.5, 2.5, 11), "Leading Lepton #eta_{SC}", "leading_lep_eta"), ("l2_scEta", np.linspace(-2.5, 2.5, 11), "Sub-leading Lepton #eta_{SC}", "subleading_lep_eta"),
        ("l1_pt", PT, "Leading Lepton p_{T} (GeV)", "leading_lep_pt"), ("l2_pt", PT, "Sub-leading Lepton p_{T} (GeV)", "subleading_lep_pt"), ("m_l1l2", XE, "Dilepton Mass (GeV)", "dilepton_mass"), ("pt_l1l2", np.array([0, 25, 50, 75, 100, 150, 200, 300, 500.]), "Dilepton p_{T} (GeV)", "dilepton_pt")]
GMAP = {"DY": "DYJets", "TT": "TT", "Nonprompt": "Nonprompt", "Others": "Others"}; LAB2 = "1 jet, %.0f #leq m_{ll} < %.0f" % (a.mll_min, a.mll_max)


def draw(stem, comps, xdata, wdata, edges, xl, groups, outdir, l2):
    keeper = []; saved = config.BACKGROUND_GROUPS; config.BACKGROUND_GROUPS = groups
    try:
        gh = {g: None for g in groups}; tot = None
        for g, (x, ww) in comps.items():
            hh = cfp.th1(f"h_{stem}_{g}", edges, np.clip(x, edges[0], edges[-1] - 1e-6), ww); keeper.append(hh); gh[g] = hh if hh.Integral() > 0 else None
            if tot is None: tot = hh.Clone(f"tot_{stem}"); tot.SetDirectory(0)
            else: tot.Add(hh)
        hdat = cfp.th1(f"hd_{stem}", edges, np.clip(xdata, edges[0], edges[-1] - 1e-6), wdata); gs, grb, grs = cfp.stat_graphs(tot); keeper += [tot, hdat, gs, grb, grs]
        args = types.SimpleNamespace(output=stem, logy=True, ymin=0.05, ymax=None, rmin=0.5, rmax=1.5, xlabel=xl, hist=stem, label1="ee OS #times w", label2=l2)
        plotter._draw(args, tot, hdat, gh, gs, grb, grs, float(edges[0]), float(edges[-1]), False, str(outdir / stem), keeper)
    finally:
        config.BACKGROUND_GROUPS = saved


for tag, src, ww, names_ in (("native_1jetMC", M1, W * w, {"DYJets": "DY: native 1-jet MC"}), ("transferred_fg", M2, W * f_grp * w, {"DYJets": "DY: 2-jet MC #times f", "TT": "T#bar{T}+tW: 2-jet MC #times f"}), ("transferred_ftot", M2, W * f_tot * w, {"DYJets": "DY: 2-jet MC #times f_{tot}", "TT": "T#bar{T}+tW: 2-jet MC #times f_{tot}"})):
    od = OUT / tag; od.mkdir(exist_ok=True); GR = {k: (v[0], names_.get(k, v[1])) for k, v in config.BACKGROUND_GROUPS.items()}
    for var, edges, xl, suf in VARS:
        comps = {gg: (d[var][src & (d["grp"] == g)], ww[src & (d["grp"] == g)]) for g, gg in GMAP.items()}; draw(f"OneJetEE_OSxw_{suf}", comps, d[var][D1], w[D1], edges, xl, GR, od, LAB2)
print("wrote", OUT)
