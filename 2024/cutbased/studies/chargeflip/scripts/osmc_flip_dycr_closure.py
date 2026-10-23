#!/usr/bin/env python3
"""Study 18: same-sign ee prediction of the resolved DY CR from opposite-sign MC (not data) times the data-corrected flip weight.

      N_SS^pred(T) = sum_{OS MC in T} weight * w(P(l1) SF, P(l2) SF)  +  MC non-flip SS in T
Every OS MC event keeps its two jets, so m_lljj (the fit variable) comes for free and no OS data of the region is used --
in the SR this avoids opening the OS SR data to build the SS template. The price: the OS yield and shape are the MC ones.
Compared with   nominal : OS DATA of T x w + non-flip MC        (AN method)
                rawMC   : MC SS of T as simulated (flipped + non-flip), i.e. no data-driven flip correction at all
T = EE, hasPair, isDYCR (nJet >= 2, passResolved, 60 < m_ee < 150, m_lljj > 800). w, P, SF as in chargeflip_ddss.new_weights with
chargeflip_ptshift_ee2024_sf3.json. Input: the event cache of study 17 (data/jetbin_ss_dycr_events.npz).
    ./condor/in_container.sh python3 studies/chargeflip/scripts/osmc_flip_dycr_closure.py
"""
import argparse, json, sys, types
from pathlib import Path
import numpy as np
BASE = Path(__file__).resolve().parents[1]; PC = Path(__file__).resolve().parents[3]; T_ = PC.parents[1] / "BDT/SR/test"
ap = argparse.ArgumentParser()
ap.add_argument("--cache", default=str(BASE / "data/jetbin_ss_dycr_events.npz"))
ap.add_argument("--json", default=str(T_ / "data/chargeflip/chargeflip_ptshift_ee2024_sf3.json"))
ap.add_argument("--out-dir", default=str(BASE / "AN_rawcharge/18_osmc_flip_dycr"))
ap.add_argument("--region", default="dycr", choices=["dycr", "lowmlljj"], help="lowmlljj (study 25): cache data/lowmlljj_events.npz = nJet>=2, passResolved, m_lljj < 800; T = m_ll in [--mll-min, --mll-max)")
ap.add_argument("--mll-min", type=float, default=400.0); ap.add_argument("--mll-max", type=float, default=1e9)
a = ap.parse_args(); OUT = Path(a.out_dir); OUT.mkdir(parents=True, exist_ok=True)
d = dict(np.load(a.cache)); isdata = d["grp"] == "DATA"; d["weight"] = np.where(isdata, 1.0, d["weight"]).astype("float64")
ss = d["isSS"] > 0; T = (d["isDYCR"] > 0) if a.region == "dycr" else ((d["m_l1l2"] >= a.mll_min) & (d["m_l1l2"] < a.mll_max))
RLAB = "Resolved DY CR" if a.region == "dycr" else ("m_{lljj} < 800, m_{ll} #geq %.0f" % a.mll_min if a.mll_max > 1e8 else "m_{lljj} < 800, %.0f #leq m_{ll} < %.0f" % (a.mll_min, a.mll_max))
STEM = "ResolveDYEE" if a.region == "dycr" else "ResolveLowMlljjEE"
flip = np.zeros(len(ss), bool)
for i in (1, 2):
    g = np.where(d[f"l{i}_genChargeIdx"] == 0, -999.0, d[f"l{i}_genChargeIdx"]); flip |= (g > -900) & (d[f"l{i}_charge"] != g)
J = json.load(open(a.json)); regs = list(J["rate_regions"].items()); P = np.nan_to_num(np.array(J["P"])); pt_edges = np.array(J["pt_edges"])
sfreg = {n: tuple(v) for n, v in J["sf"]["SF3"]["regions"].items()}; SFv = dict(J["sf"]["SF3"]["SF"]); names = list(sfreg)
reg_sf = np.array([next((k for k, n in enumerate(names) if sfreg[n][0] <= 0.5 * (lo + hi) < sfreg[n][1]), -1) for _, (lo, hi) in regs])
sf0 = np.array([SFv[n] for n in names])


def flipw(sfvec):
    pl = []
    for i in (1, 2):
        ae = np.abs(d[f"l{i}_scEta"]); ie = np.full(len(ae), -1)
        for k, (_, (lo, hi)) in enumerate(regs): ie[(ae >= lo) & (ae < hi)] = k
        ip = np.clip(np.searchsorted(pt_edges, d[f"l{i}_pt"], side="right") - 1, 0, len(pt_edges) - 2)
        p = np.zeros(len(ie)); ok = ie >= 0; p[ok] = P[ie[ok], ip[ok]] * sfvec[reg_sf[ie[ok]]]; pl.append(p)
    return (pl[0] * (1 - pl[1]) + pl[1] * (1 - pl[0])) / ((1 - pl[0]) * (1 - pl[1]) + pl[0] * pl[1])


w = flipw(sf0); w_nosf = flipw(np.ones_like(sf0))            # w_nosf: MC flip probability without the data SF
GROUPS = ("DY", "TT", "Nonprompt", "Others")
os_data = T & isdata & ~ss; ss_data = T & isdata & ss; os_mc = T & ~isdata & ~ss; ss_mc = T & ~isdata & ss; nonflip = ss_mc & ~flip; flipmc = ss_mc & flip
obs = int(ss_data.sum()); nf = float(d["weight"][nonflip].sum())
sumw = lambda m, ww=None: float((d["weight"][m] * (1.0 if ww is None else ww[m])).sum())
err = lambda m, ww=None: float(np.sqrt(((d["weight"][m] * (1.0 if ww is None else ww[m])) ** 2).sum()))
R = {"counts": dict(obs_ss_data=obs, os_data=int(os_data.sum()), os_mc=sumw(os_mc), os_mc_by_group={g: sumw(os_mc & (d["grp"] == g)) for g in GROUPS},
                    os_data_over_mc=int(os_data.sum()) / sumw(os_mc), nonflip_mc=nf, mc_ss_flipped=sumw(flipmc), mc_ss_flipped_by_group={g: sumw(flipmc & (d["grp"] == g)) for g in GROUPS})}
k = int(os_data.sum()) / sumw(os_mc)
PR = {"nominal_OSdata_x_w": (sumw(os_data, w), err(os_data, w)), "OSMC_x_w": (sumw(os_mc, w), err(os_mc, w)), "OSMC_x_w_normalised_to_OSdata": (k * sumw(os_mc, w), k * err(os_mc, w)),
      "OSMC_x_w_noSF (closure of w on MC)": (sumw(os_mc, w_nosf), err(os_mc, w_nosf)), "rawMC_SS_flipped": (sumw(flipmc), err(flipmc))}
R["predictions"] = {}
for n, (fl, e) in PR.items():
    tot = fl + nf; R["predictions"][n] = dict(flip=fl, flip_stat=e, nonflip_mc=nf, total=tot, obs=obs, obs_over_pred=obs / tot, obs_over_pred_stat=float(np.sqrt(obs)) / tot)
    print(f"{n:38s} flip {fl:8.1f} +- {e:5.1f}  + nonflip {nf:5.1f} = {tot:8.1f}   obs {obs}   obs/pred {obs / tot:.3f} +- {np.sqrt(obs) / tot:.3f}")
R["OSMC_x_w_by_group"] = {g: sumw(os_mc & (d["grp"] == g), w) for g in GROUPS}
print("OS data / OS MC in T = %.4f   (OS MC by group: %s)" % (k, {g: round(v, 1) for g, v in R["counts"]["os_mc_by_group"].items()}))
print("flip from OS MC x w by group:", {g: round(v, 1) for g, v in R["OSMC_x_w_by_group"].items()}, "| MC truth flipped SS (no SF):", {g: round(v, 1) for g, v in R["counts"]["mc_ss_flipped_by_group"].items()})
# per m_lljj bin (card binning of rDYEECR_SS)
ME = np.array([800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 8000.]) if a.region == "dycr" else np.arange(np.floor(a.mll_min / 100) * 100, 801, 100.)
MLE = np.linspace(60, 150, 10) if a.region == "dycr" else np.array([x for x in (200, 250, 300, 350, 400, 450, 500, 550, 600, 700, 800.) if a.mll_min <= x <= min(a.mll_max, 800)])
h = lambda m, ww: np.histogram(np.clip(d["m_lljj"][m], ME[0], ME[-1] - 1), ME, weights=ww)[0]
hn = h(nonflip, d["weight"][nonflip]); ho = h(ss_data, np.ones(obs)); hd = h(os_data, w[os_data]) + hn; hm = h(os_mc, (d["weight"] * w)[os_mc]) + hn
R["mlljj"] = dict(edges=ME.tolist(), obs=ho.tolist(), nominal=hd.tolist(), osmc=hm.tolist(), osmc_normalised=(k * (hm - hn) + hn).tolist())
print("m_lljj bin      obs   nominal  OSMCxw  OSMCxw(norm)   obs/nominal  obs/OSMC(norm)")
for i in range(len(ME) - 1):
    on = k * (hm[i] - hn[i]) + hn[i]; print(f"{ME[i]:5.0f}-{ME[i+1]:5.0f} {ho[i]:6.0f} {hd[i]:9.1f} {hm[i]:8.1f} {on:9.1f}   {ho[i]/hd[i]:9.3f}  {ho[i]/on:9.3f}")
(OUT / "summary.json").write_text(json.dumps(R, indent=1) + "\n")

# ---- plots, cutbased plotter format ----------------------------------------------------------------------------------
sys.path.insert(0, str(PC)); import ROOT, config, plotter, chargeflip_plots as cfp            # noqa: E402
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0); ROOT.gErrorIgnoreLevel = ROOT.kWarning
VARS = [("m_lljj", ME, "m_{lljj} (GeV)", "mlljj"), ("l1_pt", np.array([53, 70, 100, 150, 250, 400, 1000.]), "Leading Lepton p_{T} (GeV)", "leading_lep_pt"),
        ("l2_pt", np.array([53, 70, 100, 150, 250, 400, 1000.]), "Sub-leading Lepton p_{T} (GeV)", "subleading_lep_pt"),
        ("l1_scEta", np.linspace(-2.5, 2.5, 11), "Leading Lepton #eta_{SC}", "leading_lep_eta"), ("l2_scEta", np.linspace(-2.5, 2.5, 11), "Sub-leading Lepton #eta_{SC}", "subleading_lep_eta"),
        ("m_l1l2", MLE, "Dilepton Mass (GeV)", "dilepton_mass"), ("pt_l1l2", np.array([0, 50, 100, 150, 200, 300, 400, 600, 1000.]), "Dilepton p_{T} (GeV)", "dilepton_pt"),
        ("nJet", np.arange(1.5, 8.5, 1.0), "Number of jets", "njet")]
GMAP = {"DY": "DYJets", "TT": "TT", "Nonprompt": "Nonprompt", "Others": "Others"}


def draw(stem, comps, xdata, edges, xlabel, groups, outdir, label1="ee SS", rmin=0.5, rmax=2.0):
    keeper = []; saved = config.BACKGROUND_GROUPS; config.BACKGROUND_GROUPS = groups
    try:
        gh = {g: None for g in groups}; tot = None
        for g, (x, ww) in comps.items():
            hh = cfp.th1(f"h_{stem}_{g}", edges, np.clip(x, edges[0], edges[-1] - 1e-6), ww); keeper.append(hh); gh[g] = hh if hh.Integral() > 0 else None
            if tot is None: tot = hh.Clone(f"tot_{stem}"); tot.SetDirectory(0)
            else: tot.Add(hh)
        hdat = cfp.th1(f"h_data_{stem}", edges, np.clip(xdata, edges[0], edges[-1] - 1e-6)); gs, grb, grs = cfp.stat_graphs(tot); keeper += [tot, hdat, gs, grb, grs]
        args = types.SimpleNamespace(output=stem, logy=True, ymin=0.5, ymax=None, rmin=rmin, rmax=rmax, xlabel=xlabel, hist=stem, label1=label1, label2=RLAB)
        plotter._draw(args, tot, hdat, gh, gs, grb, grs, float(edges[0]), float(edges[-1]), False, str(outdir / stem), keeper)
    finally:
        config.BACKGROUND_GROUPS = saved


for name, src, scale, lab in (("nominal_OSdata_x_w", os_data, 1.0, "Charge flip (OS data #times w)"), ("OSMC_x_w", os_mc, 1.0, "Charge flip (OS MC #times w)"),
                              ("OSMC_x_w_normalised", os_mc, k, "Charge flip (OS MC #times w, OS norm.)")):
    od = OUT / name; od.mkdir(exist_ok=True)
    GR = {"Flip": ("kOrange", lab), "DYJets": ("kYellow", "Drell-Yan non-flip"), "TT": ("kRed", "T#bar{T}+tW non-flip"), "Nonprompt": ("kGreen+2", "Nonprompt"), "Others": ("kBlue", "Others (WZ/ZZ)")}
    for var, edges, xl, suf in VARS:
        comps = {"Flip": (d[var][src], scale * (d["weight"] * w)[src])}
        for g, gg in GMAP.items():
            mm = nonflip & (d["grp"] == g); comps[gg] = (d[var][mm], d["weight"][mm])
        draw(f"{STEM}_SS_{suf}", comps, d[var][ss_data], edges, "SS " + xl, GR, od)
# OS region itself: data vs MC (what the OS MC x w prediction inherits)
od = OUT / "OS_data_vs_MC"; od.mkdir(exist_ok=True)
for var, edges, xl, suf in VARS:
    comps = {gg: (d[var][os_mc & (d["grp"] == g)], d["weight"][os_mc & (d["grp"] == g)]) for g, gg in GMAP.items()}
    draw(f"{STEM}_OS_{suf}", comps, d[var][os_data], edges, "OS " + xl, config.BACKGROUND_GROUPS, od, label1="ee OS", rmin=0.5, rmax=1.5)
print("wrote", OUT)
