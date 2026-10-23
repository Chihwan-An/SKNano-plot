#!/usr/bin/env python3
"""Study 17: predict the 2-jet same-sign ee yield of the resolved DY CR from 1-jet opposite-sign DATA.

Motivation: the nominal estimate weights the OS data of the SAME (>=2 jet) region with the flip weight w(P1, P2).
In the signal region that OS sample is itself a signal region. Here the OS source is moved to nJet == 1 and brought
to the 2-jet lepton kinematics with a transfer factor in bins of the reconstructed Z pT (study 12), then the usual
flip weight is applied event by event:
      N_SS^pred(T) = sum_{1-jet OS data} t(pT_ll [, m_ll]) * w(P(l1), P(l2))  +  MC non-flip SS in T
  T (target) : EE, hasPair, isDYCR (nJet >= 2, passResolved, 60 < m_ee < 150, m_lljj > 800)       -- NOT blinded (DY CR)
  S (source) : EE, hasPair, nJet == 1, 60 <= m_ee < 150, opposite sign
  t          : N_OS(T) / N_OS(S) per bin. "mc" = from the summed MC (all groups, nominal weights); "data" = from OS data
               (reference only: it uses the target-region OS data, which is what the method wants to avoid in the SR).
  w, P, SF   : identical to BDT/SR/test/scripts/chargeflip_ddss.new_weights with chargeflip_ptshift_ee2024_sf3.json.
The nominal same-region prediction (OS data of T x w) is evaluated alongside as the reference.
1-jet events have no m_lljj, so the closure is tested on the yield and on lepton / dilepton variables only.
    ./condor/in_container.sh python3 studies/chargeflip/scripts/jetbin_ss_dycr_closure.py [--dumps DIR] [--json FILE]
"""
import argparse, glob, json, os, sys, types
from pathlib import Path
import numpy as np
BASE = Path(__file__).resolve().parents[1]                    # studies/chargeflip
PC = Path(__file__).resolve().parents[3]                      # plot/HNWR_2024/cutbased
T_ = PC.parents[1] / "BDT/SR/test"
ap = argparse.ArgumentParser()
ap.add_argument("--dumps", default=str(T_ / "data/chargeflip/dumps_boost"))
ap.add_argument("--json", default=str(T_ / "data/chargeflip/chargeflip_ptshift_ee2024_sf3.json"))
ap.add_argument("--cache", default=str(BASE / "data/jetbin_ss_dycr_events.npz"))
ap.add_argument("--out-dir", default=str(BASE / "AN_rawcharge/17_1jet_to_2jet_ss_dycr"))
ap.add_argument("--rebuild", action="store_true")
a = ap.parse_args()
OUT = Path(a.out_dir); OUT.mkdir(parents=True, exist_ok=True)
KEYS = ["channel", "hasPair", "isDYCR", "isSS", "nJet", "m_l1l2", "pt_l1l2", "m_lljj", "weight",
        "l1_pt", "l2_pt", "l1_scEta", "l2_scEta", "l1_eta", "l2_eta", "l1_phi", "l2_phi", "l1_charge", "l2_charge", "l1_genChargeIdx", "l2_genChargeIdx"]
ZPT = np.array([0, 60, 80, 100, 125, 150, 175, 200, 250, 300, 400, 500, 700, 1000, np.inf])
MLL = np.array([60, 80, 86, 89, 91, 93, 96, 100, 110, 150.])


def group_of(b):
    b = b.replace("tree_Skim_HNWR_", "").replace("tree_", "")
    if b.startswith("DYto2L"): return "DY"
    if b.startswith(("EGamma", "Muon")): return "DATA"
    if b.startswith("WRtoN"): return None
    if b.startswith(("TTto2L2Nu", "TWminusto2L2Nu", "TbarWplusto2L2Nu")): return "TT"
    if b.startswith(("WWto", "WZto", "ZZto", "TTLL", "TTLNu")): return "Others"
    return "Nonprompt"


def build():
    acc = {k: [] for k in KEYS + ["grp"]}
    for p in sorted(glob.glob(os.path.join(a.dumps, "tree_*.npz"))):
        g = group_of(os.path.basename(p))
        if g is None or (g == "DATA" and "Muon" in os.path.basename(p)): continue      # EE: EGamma stream only
        z = np.load(p)
        m = (z["channel"] == 11) & (z["hasPair"] > 0) & (z["m_l1l2"] >= 60) & (z["m_l1l2"] < 150) & ((z["nJet"] == 1) | (z["isDYCR"] > 0))
        if not m.any(): continue
        for k in KEYS: acc[k].append(np.asarray(z[k][m], dtype="float64"))
        acc["grp"].append(np.full(int(m.sum()), g))
        print(f"  {os.path.basename(p):70s} {g:9s} {int(m.sum()):9d}", flush=True)
    d = {k: np.concatenate(v) for k, v in acc.items()}
    np.savez_compressed(a.cache, **d)
    Path(a.cache).with_suffix(".json").write_text(json.dumps(dict(source_directory=str(Path(a.dumps).resolve()), keys=KEYS,
        selection="channel==11 & hasPair & 60<=m_l1l2<150 & (nJet==1 | isDYCR); EGamma data only; signal skipped", n=int(len(d["channel"]))), indent=1) + "\n")
    return d


d = build() if (a.rebuild or not os.path.exists(a.cache)) else dict(np.load(a.cache))
isdata = d["grp"] == "DATA"; d["weight"] = np.where(isdata, 1.0, d["weight"])
ss = d["isSS"] > 0; T = d["isDYCR"] > 0; S = (d["nJet"] == 1) & ~T
flip = np.zeros(len(ss), bool)
for i in (1, 2):
    g = np.where(d[f"l{i}_genChargeIdx"] == 0, -999.0, d[f"l{i}_genChargeIdx"]); flip |= (g > -900) & (d[f"l{i}_charge"] != g)

# ---- flip weight (same as chargeflip_ddss.new_weights) ---------------------------------------------------------------
J = json.load(open(a.json)); regs = list(J["rate_regions"].items()); P = np.nan_to_num(np.array(J["P"])); pt_edges = np.array(J["pt_edges"])
sfreg = {n: tuple(v) for n, v in J["sf"]["SF3"]["regions"].items()}; SFv = dict(J["sf"]["SF3"]["SF"]); names = list(sfreg)
reg_sf = np.array([next((k for k, n in enumerate(names) if sfreg[n][0] <= 0.5 * (lo + hi) < sfreg[n][1]), -1) for _, (lo, hi) in regs])
sf0 = np.array([SFv[n] for n in names]); pl = []
for i in (1, 2):
    ae = np.abs(d[f"l{i}_scEta"]); ie = np.full(len(ae), -1)
    for k, (_, (lo, hi)) in enumerate(regs): ie[(ae >= lo) & (ae < hi)] = k
    ip = np.clip(np.searchsorted(pt_edges, d[f"l{i}_pt"], side="right") - 1, 0, len(pt_edges) - 2)
    p = np.zeros(len(ie)); ok = ie >= 0; p[ok] = P[ie[ok], ip[ok]] * sf0[reg_sf[ie[ok]]]; pl.append(p)
w = (pl[0] * (1 - pl[1]) + pl[1] * (1 - pl[0])) / ((1 - pl[0]) * (1 - pl[1]) + pl[0] * pl[1])

# ---- transfer factors ------------------------------------------------------------------------------------------------
def merged_edges(x_s, w_s, x_t, w_t, edges, nmin=50.0):
    """merge adjacent bins (from the top) until source and target both have N_eff >= nmin"""
    e = list(edges)
    def neff(x, ww, lo, hi):
        m = (x >= lo) & (x < hi); s1 = ww[m].sum(); s2 = (ww[m] ** 2).sum(); return s1 * s1 / s2 if s2 > 0 else 0.0
    k = len(e) - 2
    while k >= 0 and len(e) > 2:
        if min(neff(x_s, w_s, e[k], e[k + 1]), neff(x_t, w_t, e[k], e[k + 1])) < nmin:
            e.pop(k if k > 0 else 1)
            k = min(k, len(e) - 2)
            if k == 0 and min(neff(x_s, w_s, e[0], e[1]), neff(x_t, w_t, e[0], e[1])) >= nmin: break
            continue
        k -= 1
    return np.array(e)


ETA3 = np.array([0.0, 0.8, 1.5, 2.5])                       # |eta_SC|: inner barrel / outer barrel (+crack) / endcap


def axes_of(mode, ez):
    """list of (values, edges) defining the cells of the transfer factor"""
    ax = {"zpt": [("pt_l1l2", ez)], "mll_zpt": [("m_l1l2", MLL), ("pt_l1l2", ez)],
          "zpt_eta1": [("pt_l1l2", ez), ("abs_l1_scEta", ETA3)],
          "zpt_eta2d": [("pt_l1l2", ez), ("abs_l1_scEta", ETA3), ("abs_l2_scEta", ETA3)],
          "zpt_zeta": [("pt_l1l2", ez), ("abs_eta_ll", ZETA)], "zpt_zy": [("pt_l1l2", ez), ("abs_y_ll", ZY)]}
    return ax[mode]


d["abs_l1_scEta"] = np.abs(d["l1_scEta"]); d["abs_l2_scEta"] = np.abs(d["l2_scEta"])
# dilepton (Z) direction from the two lepton momenta (massless leptons, momentum eta -- not supercluster eta)
_px = d["l1_pt"] * np.cos(d["l1_phi"]) + d["l2_pt"] * np.cos(d["l2_phi"]); _py = d["l1_pt"] * np.sin(d["l1_phi"]) + d["l2_pt"] * np.sin(d["l2_phi"])
_pz = d["l1_pt"] * np.sinh(d["l1_eta"]) + d["l2_pt"] * np.sinh(d["l2_eta"]); _e = d["l1_pt"] * np.cosh(d["l1_eta"]) + d["l2_pt"] * np.cosh(d["l2_eta"])
_pt = np.hypot(_px, _py); d["eta_ll"] = np.arcsinh(_pz / np.maximum(_pt, 1e-9)); d["y_ll"] = 0.5 * np.log((_e + _pz) / np.maximum(_e - _pz, 1e-9))
d["abs_eta_ll"] = np.abs(d["eta_ll"]); d["abs_y_ll"] = np.abs(d["y_ll"])
ZETA = np.array([0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.5, 3.0, np.inf]); ZY = np.array([0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.5])


def transfer(sel_src, sel_tgt, mode):
    """t = N(target)/N(source) per cell; a cell with an empty source falls back to the Z-pT-only factor"""
    ws, wt = d["weight"][sel_src], d["weight"][sel_tgt]
    ez = merged_edges(d["pt_l1l2"][sel_src], ws, d["pt_l1l2"][sel_tgt], wt, ZPT)
    axes = axes_of(mode, ez); edges = [e for _, e in axes]
    ns, _ = np.histogramdd(np.stack([d[v][sel_src] for v, _ in axes], 1), edges, weights=ws)
    nt, _ = np.histogramdd(np.stack([d[v][sel_tgt] for v, _ in axes], 1), edges, weights=wt)
    zs, _ = np.histogram(d["pt_l1l2"][sel_src], ez, weights=ws); zt, _ = np.histogram(d["pt_l1l2"][sel_tgt], ez, weights=wt)
    r1 = np.where(zs > 0, zt / np.where(zs > 0, zs, 1), 0.0); iz_axis = [v for v, _ in axes].index("pt_l1l2")
    shape = [1] * len(axes); shape[iz_axis] = len(r1)
    r = np.where(ns > 0, nt / np.where(ns > 0, ns, 1), np.broadcast_to(r1.reshape(shape), ns.shape))
    def f(m):
        idx = tuple(np.clip(np.searchsorted(e, d[v][m], side="right") - 1, 0, len(e) - 2) for v, e in axes); return r[idx]
    fin = lambda e: [None if not np.isfinite(x) else float(x) for x in e]
    return f, dict(axes=[v for v, _ in axes], edges=[fin(e) for e in edges], t=r.tolist())


src_os_data = S & isdata & ~ss; tgt_os_data = T & isdata & ~ss; tgt_ss_data = T & isdata & ss
nonflip = T & ~isdata & ss & ~flip
RES = {"inputs": dict(dumps=a.dumps, json=a.json), "counts": dict(src_os_data=int(src_os_data.sum()), tgt_os_data=int(tgt_os_data.sum()), tgt_ss_data=int(tgt_ss_data.sum()),
       nonflip_mc=float(d["weight"][nonflip].sum()), nonflip_by_group={g: float(d["weight"][nonflip & (d["grp"] == g)].sum()) for g in ("DY", "TT", "Nonprompt", "Others")})}
PRED = {"nominal_2jetOS": (tgt_os_data, np.ones(int(tgt_os_data.sum())))}
FACT = {}
for src_name, (ss_, st_) in {"mc": (S & ~isdata & ~ss, T & ~isdata & ~ss), "data": (src_os_data, tgt_os_data)}.items():
    for mode in ("zpt", "mll_zpt", "zpt_eta1", "zpt_eta2d", "zpt_zeta", "zpt_zy"):
        f, info = transfer(ss_, st_, mode); FACT[f"{src_name}_{mode}"] = info; PRED[f"1jetOS_{src_name}_{mode}"] = (src_os_data, f(src_os_data))
obs = int(tgt_ss_data.sum()); nf = RES["counts"]["nonflip_mc"]
RES["predictions"] = {}
for name, (m, t) in PRED.items():
    fl = float((t * w[m]).sum()); efl = float(np.sqrt(((t * w[m]) ** 2).sum()))
    RES["predictions"][name] = dict(flip=fl, flip_stat=efl, nonflip_mc=nf, total=fl + nf, obs=obs, obs_over_pred=obs / (fl + nf), obs_over_pred_stat=float(np.sqrt(obs)) / (fl + nf),
                                    sum_transfer=float(t.sum()), n_source=int(m.sum()))
    print(f"{name:26s} flip {fl:8.1f} +- {efl:5.1f}  + nonflip {nf:5.1f} = {fl + nf:8.1f}   obs {obs}   obs/pred {obs / (fl + nf):.3f} +- {np.sqrt(obs) / (fl + nf):.3f}   (source events {int(m.sum())}, sum t = {t.sum():.1f} vs OS target {int(tgt_os_data.sum())})")
RES["transfer"] = FACT
(OUT / "summary.json").write_text(json.dumps(RES, indent=1) + "\n")

# ---- plots in the cutbased plotter format (same style as chargeflip_apply_plots.py) ----------------------------------
sys.path.insert(0, str(PC)); import ROOT, config, plotter, chargeflip_plots as cfp            # noqa: E402
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0); ROOT.gErrorIgnoreLevel = ROOT.kWarning
VARS = [("l1_pt", np.array([53, 70, 100, 150, 250, 400, 1000.]), "Leading Lepton p_{T} (GeV)", "leading_lep_pt"),
        ("l2_pt", np.array([53, 70, 100, 150, 250, 400, 1000.]), "Sub-leading Lepton p_{T} (GeV)", "subleading_lep_pt"),
        ("l1_scEta", np.linspace(-2.5, 2.5, 11), "Leading Lepton #eta_{SC}", "leading_lep_eta"),
        ("l2_scEta", np.linspace(-2.5, 2.5, 11), "Sub-leading Lepton #eta_{SC}", "subleading_lep_eta"),
        ("m_l1l2", np.linspace(60, 150, 10), "Dilepton Mass (GeV)", "dilepton_mass"),
        ("pt_l1l2", np.array([0, 50, 100, 150, 200, 300, 400, 600, 1000.]), "Dilepton p_{T} (GeV)", "dilepton_pt"),
        ("eta_ll", np.linspace(-4, 4, 17), "Dilepton #eta", "dilepton_eta"), ("y_ll", np.linspace(-2.5, 2.5, 11), "Dilepton rapidity", "dilepton_y")]
GR_SS = {"Flip": ("kOrange", "Charge flip (source OS #times w)"), "DYJets": ("kYellow", "Drell-Yan non-flip"), "TT": ("kRed", "T#bar{T}+tW non-flip"),
         "Nonprompt": ("kGreen+2", "Nonprompt"), "Others": ("kBlue", "Others (WZ/ZZ)")}
GMAP = {"DY": "DYJets", "TT": "TT", "Nonprompt": "Nonprompt", "Others": "Others"}


def draw(stem, comps, hdata_vals, edges, xlabel, label1, label2, groups, outdir, rmin=0.5, rmax=1.5):
    """comps: {group: (x, weights)}; hdata_vals: x of the data events"""
    keeper = []; saved = config.BACKGROUND_GROUPS; config.BACKGROUND_GROUPS = groups
    try:
        gh = {g: None for g in groups}; tot = None
        for g, (x, ww) in comps.items():
            h = cfp.th1(f"h_{stem}_{g}", edges, np.clip(x, edges[0], edges[-1] - 1e-6), ww); gh[g] = h if h.Integral() > 0 else None; keeper.append(h)
            tot = h.Clone(f"tot_{stem}") if tot is None else tot; tot.Add(h) if tot is not h and tot.GetName() != h.GetName() and g != list(comps)[0] else None
        hd = cfp.th1(f"h_data_{stem}", edges, np.clip(hdata_vals, edges[0], edges[-1] - 1e-6)); gs, grb, grs = cfp.stat_graphs(tot); keeper += [tot, hd, gs, grb, grs]
        args = types.SimpleNamespace(output=stem, logy=True, ymin=0.5, ymax=None, rmin=rmin, rmax=rmax, xlabel=xlabel, hist=stem, label1=label1, label2=label2)
        plotter._draw(args, tot, hd, gh, gs, grb, grs, float(edges[0]), float(edges[-1]), False, str(outdir / stem), keeper)
    finally:
        config.BACKGROUND_GROUPS = saved


for name, (m, t) in PRED.items():
    od = OUT / name; od.mkdir(exist_ok=True)
    for var, edges, xl, suf in VARS:
        comps = {"Flip": (d[var][m], t * w[m])}
        for g, gg in GMAP.items():
            mm = nonflip & (d["grp"] == g); comps[gg] = (d[var][mm], d["weight"][mm])
        draw(f"ResolveDYEE_SS_{suf}", comps, d[var][tgt_ss_data], edges, "SS " + xl, "ee SS", "Resolved DY CR", GR_SS, od, rmin=0.5, rmax=2.0)
# does the re-weighted 1-jet OS DATA look like the 2-jet OS DATA? (no flip weight)
GR_OS = {"Flip": ("kAzure+1", "1-jet OS data #times t")}
for name, (m, t) in PRED.items():
    if name.startswith("nominal"): continue
    od = OUT / name / "os_mimic"; od.mkdir(exist_ok=True)
    for var, edges, xl, suf in VARS:
        draw(f"ResolveDYEE_OS_{suf}", {"Flip": (d[var][m], t)}, d[var][tgt_os_data], edges, "OS " + xl, "ee OS", "Resolved DY CR (2-jet data)", GR_OS, od)
print("wrote", OUT)
