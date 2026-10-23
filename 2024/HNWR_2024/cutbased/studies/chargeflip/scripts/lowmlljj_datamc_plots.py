#!/usr/bin/env python3
"""Study 27: plain data/MC of the low-m_lljj test region, EE or MM, OS and SS separately.

Selection = the resolved SR of that channel with the m_lljj cut reversed:
    channel == 11 (EE) or 13 (MM), hasPair, nJet >= 2, passResolved, m_ll >= 400, m_lljj < 800
(the SR is `passResolved & m_l1l2 > 400 & m_lljj > 800`, cf. BDT/SR/test/scripts/chargeflip_ddss.py rEESR_SS).
This is the analysis' open low-mass validation region, so both OS and SS data are drawn -- no blinding.
Variables are the ones drawn for the resolved DY CR (plot/HNWR_2024/cutbased/out/Resolve/DY/{EE,MM}/{dilepton,jet,jet_lepton,lepton}),
with the binning adapted to this phase space (m_ll < ~650, m_lljj < 800, soft jets).

    ./condor/in_container.sh python3 studies/chargeflip/scripts/lowmlljj_datamc_plots.py
    ./condor/in_container.sh python3 studies/chargeflip/scripts/lowmlljj_datamc_plots.py --channel 13
    ./condor/in_container.sh python3 studies/chargeflip/scripts/lowmlljj_datamc_plots.py --mll-min 200 --mll-max 400 \
        --out-dir studies/chargeflip/AN_rawcharge/27_lowmlljj_datamc_mll200to400
"""
import argparse, json, sys, types
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parents[1]; PC = Path(__file__).resolve().parents[3]
ap = argparse.ArgumentParser()
ap.add_argument("--channel", type=int, default=11, choices=[11, 13], help="11 = EE, 13 = MM; picks the default cache and out-dir")
ap.add_argument("--cache", default=None)
ap.add_argument("--out-dir", default=None)
ap.add_argument("--mll-min", type=float, default=400.0, help="SR value; the default cache holds m_ll >= 200 (lowmlljj_build.py --mll-min 60 for the Z window)")
ap.add_argument("--mll-max", type=float, default=1e9)
a = ap.parse_args()
EE = a.channel == 11
CACHE = a.cache or str(BASE / ("data/lowmlljj_events.npz" if EE else "data/lowmlljj_events_mm.npz"))
OUT = Path(a.out_dir or str(BASE / ("AN_rawcharge/27_lowmlljj_datamc_mll400" if EE else "AN_rawcharge/27_lowmlljj_datamc_mll400_MM")))
OUT.mkdir(parents=True, exist_ok=True)

d = dict(np.load(CACHE))
isdata = d["grp"] == "DATA"; d["weight"] = np.where(isdata, 1.0, d["weight"]).astype("float64")
ss = d["isSS"] > 0
T = (d["m_l1l2"] >= a.mll_min) & (d["m_l1l2"] < a.mll_max)
RLAB = ("m_{lljj} < 800, m_{ll} #geq %.0f" % a.mll_min if a.mll_max > 1e8
        else "m_{lljj} < 800, %.0f #leq m_{ll} < %.0f" % (a.mll_min, a.mll_max))
STEM = "ResolveLowMlljjEE" if EE else "ResolveLowMlljjMM"
LEP = "ee" if EE else "#mu#mu"
LETA = np.linspace(-2.5, 2.5, 11) if EE else np.linspace(-2.4, 2.4, 12)   # electron / muon acceptance
GMAP = {"DY": "DYJets", "TT": "TT", "Nonprompt": "Nonprompt", "Others": "Others"}

# (cache key, bin edges, x label, output suffix) -- the resolved DY CR variable set.
def _e(*v): return np.array(v, dtype="float64")
VARS = [
    ("m_l1l2",   _e(400, 425, 450, 475, 500, 550, 650)          if a.mll_min >= 400 else
                 _e(200, 240, 280, 320, 360, 400)                if a.mll_min >= 200 else
                 _e(60, 70, 80, 90, 100, 110, 120, 140, 160, 200, 250, 300, 400), "m(ll) (GeV)",       "dilepton_mass"),
    ("pt_l1l2",  _e(0, 50, 100, 150, 200, 250, 350),                      "Dilepton p_{T} (GeV)",     "dilepton_pt"),
    ("nJet",     _e(1.5, 2.5, 3.5, 4.5, 6.5),                             "Number of Jets",           "jetnum"),
    ("j1_pt",    _e(40, 60, 80, 100, 125, 150, 200, 300),                 "Leading Jet p_{T} (GeV)",  "leading_jet_pt"),
    ("j1_eta",   np.linspace(-2.5, 2.5, 11),                              "Leading Jet #eta",         "leading_jet_eta"),
    ("j2_pt",    _e(40, 50, 60, 75, 100, 130, 200),                       "Subleading Jet p_{T} (GeV)", "subleading_jet_pt"),
    ("j2_eta",   np.linspace(-2.5, 2.5, 11),                              "Subleading Jet #eta",      "subleading_jet_eta"),
    ("m_lljj",   _e(480, 520, 560, 600, 650, 700, 750, 800)      if a.mll_min >= 400 else
                 _e(200, 300, 400, 500, 600, 700, 800)           if a.mll_min >= 200 else
                 _e(100, 200, 300, 400, 500, 600, 700, 800),              "m(lljj) (GeV)",            "mlljj"),
    ("m_lljj",   np.arange(480, 801, 20.0)                       if a.mll_min >= 400 else
                 np.arange(200, 801, 50.0)                       if a.mll_min >= 200 else
                 np.arange(100, 801, 25.0),                               "m(lljj) (GeV)",            "mlljj_fine"),
    ("l1_pt",    _e(53, 100, 150, 200, 250, 300, 400, 500),               "Leading Lepton p_{T} (GeV)",    "leading_lep_pt"),
    ("l1_eta",   LETA,                                                    "Leading Lepton #eta",           "leading_lep_eta"),
    ("l2_pt",    _e(53, 70, 100, 150, 200, 250, 400),                     "Subleading Lepton p_{T} (GeV)", "subleading_lep_pt"),
    ("l2_eta",   LETA,                                                    "Subleading Lepton #eta",        "subleading_lep_eta"),
]

sys.path.insert(0, str(PC)); import ROOT, config, plotter, chargeflip_plots as cfp            # noqa: E402
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0); ROOT.gErrorIgnoreLevel = ROOT.kWarning


def draw(stem, comps, xdata, edges, xlabel, outdir, label1, ymin, rmin, rmax):
    keeper = []; gh = {g: None for g in config.BACKGROUND_GROUPS}; tot = None
    for g, (x, ww) in comps.items():
        hh = cfp.th1(f"h_{stem}_{g}", edges, np.clip(x, edges[0], edges[-1] - 1e-6), ww); keeper.append(hh)
        gh[g] = hh if hh.Integral() > 0 else None
        if tot is None: tot = hh.Clone(f"tot_{stem}"); tot.SetDirectory(0)
        else: tot.Add(hh)
    hdat = cfp.th1(f"h_data_{stem}", edges, np.clip(xdata, edges[0], edges[-1] - 1e-6))
    gs, grb, grs = cfp.stat_graphs(tot); keeper += [tot, hdat, gs, grb, grs]
    args = types.SimpleNamespace(output=stem, logy=True, ymin=ymin, ymax=None, rmin=rmin, rmax=rmax,
                                 xlabel=xlabel, hist=stem, label1=label1, label2=RLAB)
    plotter._draw(args, tot, hdat, gh, gs, grb, grs, float(edges[0]), float(edges[-1]), False, str(outdir / stem), keeper)


R = {"selection": ("EE" if EE else "MM") + ", hasPair, nJet>=2, passResolved, m_lljj<800, %.0f <= m_ll < %.0f" % (a.mll_min, a.mll_max), "yields": {}}
# (sub-directory, stem/label tag, event mask, label1, y minimum, ratio range) -- Inclusive carries no charge tag,
# the same convention as the DY CR output (out/Resolve/DY/<ch>/<obj>/Inclusive/ResolveDY<ch>_<var>).
for sign, tag, sel, label1, ymin, rr in (("OS", "OS_", T & ~ss, LEP + " OS", 0.5, (0.5, 1.5)),
                                         ("SS", "SS_", T & ss, LEP + " SS", 0.05, (0.0, 5.5)),
                                         ("Inclusive", "", T, LEP, 0.5, (0.5, 1.5))):
    od = OUT / sign; od.mkdir(exist_ok=True)
    mc = {gg: sel & ~isdata & (d["grp"] == g) for g, gg in GMAP.items()}
    dat = sel & isdata
    y = {gg: float(d["weight"][m].sum()) for gg, m in mc.items()}
    tot = sum(y.values()); obs = int(dat.sum())
    R["yields"][sign] = dict(data=obs, total_mc=tot, data_over_mc=(obs / tot if tot else None), by_group=y)
    print(f"{sign}: data {obs:7d}   MC {tot:9.1f}   data/MC {obs / tot:6.3f}   " +
          "  ".join(f"{g} {v:8.1f}" for g, v in y.items()), flush=True)
    for var, edges, xl, suf in VARS:
        comps = {gg: (d[var][m], d["weight"][m]) for gg, m in mc.items()}
        draw(f"{STEM}_{tag}{suf}", comps, d[var][dat], edges, (f"{sign} {xl}" if tag else xl), od, label1, ymin, *rr)
(OUT / "summary.json").write_text(json.dumps(R, indent=1) + "\n")
print("wrote", OUT)
