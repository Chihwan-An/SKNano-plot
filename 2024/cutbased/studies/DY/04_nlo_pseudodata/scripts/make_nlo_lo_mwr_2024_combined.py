#!/usr/bin/env python3
"""NLO pseudo-data check of the DY correction, 2024, ee+mumu combined, in the format of the 2022-2023
figures chihwan/fig/05_backgrounds/backup/corrections/fig31_*/fig32_* (make_ch5_appJ_corrections.py):
  fig31: NLO/LO and (Data - non-DY)/LO versus m(WR)^RECO in the DY CR
  fig32: NLO/LO in the DY CR versus NLO/LO in the SR
Inputs are those of chihwan/fig/05_backgrounds/2024/scripts/make_nlo_lo_mlljj_2024.py:
  NLO (POWHEG mass-binned, 18 samples) and LO (MadGraph HT-binned, C = EW = R = 1):
      $SKNANO_OUTPUT/HNWR/DYCRSplit_NoDYCorr_WeightSystOnly/2024
  data / non-DY of the DY CR: $SKNANO_OUTPUT/HNWR/DYCRStudy_RFlav/2024, DYCR_NoCorr/Central
NOTE: the 2022-2023 version used aMC@NLO FxFx as NLO; no FxFx DY sample exists in the 2024 NanoAODv15 production.
    ./condor/in_container.sh python3 make_nlo_lo_mwr_2024_combined.py --out DIR      (from plot/cutbased)
"""
import argparse, glob, json, os, re, sys
import numpy as np, uproot
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased")
import config  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--prod", default="/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/DYCRSplit_NoDYCorr_WeightSystOnly/2024")
ap.add_argument("--cr", default="/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/DYCRStudy_RFlav/2024")
ap.add_argument("--cr-variant", default="DYCR_NoCorr")
ap.add_argument("--out", required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
EDGES = {"Resolved": np.array([800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 4000, 8000], float),
         "Boosted": np.array([800, 1000, 1200, 1600, 2000, 2800, 4000, 8000], float)}


def rebin(h, edges):
    v = h.values(flow=False); e = h.axis().edges(); w = h.variances(flow=False); i = np.searchsorted(e, edges)
    return (np.array([v[i[k]:i[k + 1]].sum() for k in range(len(edges) - 1)]), np.array([w[i[k]:i[k + 1]].sum() for k in range(len(edges) - 1)]))


def collect(prod, prefix, selector, chdir="Central"):
    """ee+mumu sum of <chdir>/<prefix>_<cat>_<ch>_mlljj over the files accepted by selector(stem, ch)"""
    out = {}
    for p in sorted(glob.glob(os.path.join(prod, "*.root"))):
        stem = os.path.basename(p)[:-5]; f = uproot.open(p)
        for cat in EDGES:
            for ch in ("EE", "MM"):
                name = f"{chdir}/{prefix}_{cat}_{ch}_mlljj"
                if not selector(stem, ch) or name not in f:
                    continue
                v, w = rebin(f[name], EDGES[cat])
                out[cat] = (out[cat][0] + v, out[cat][1] + w) if cat in out else (v, w)
        f.close()
    return out


is_nlo = lambda s, ch: re.match(r"^DYto2(E|Mu)_MLL", s) is not None
is_lo = lambda s, ch: re.match(r"^Skim_HNWR_DYto2L", s) is not None


def is_data(s, ch):
    st = config.sample_stem(s); return st is not None and config.is_data(st, config.CHANNELS[ch]["data"])


def is_nondy(s, ch):
    st = config.sample_stem(s)
    if st is None or config.is_data(st) or config.is_signal(st):
        return False
    return config.classify_sample(re.sub(r"_p\d\d$", "", st))[0] in ("TT", "Nonprompt", "Others")


def ratio(n, d):
    ok = d[0] > 0; r = np.where(ok, n[0] / np.where(ok, d[0], 1), np.nan)
    e = np.abs(r) * np.sqrt(np.where(n[0] != 0, n[1] / np.where(n[0] != 0, n[0], 1) ** 2, 0) + np.where(ok, d[1] / np.where(ok, d[0], 1) ** 2, 0))
    return r, e


NLO_CR = collect(a.prod, "DYCR", is_nlo); LO_CR = collect(a.prod, "DYCR", is_lo)
NLO_SR = collect(a.prod, "SR", is_nlo); LO_SR = collect(a.prod, "SR", is_lo)
DATA = collect(a.cr, "DYCR", is_data, chdir=f"{a.cr_variant}/Central"); NONDY = collect(a.cr, "DYCR", is_nondy, chdir=f"{a.cr_variant}/Central")


def steps(ax, edges, v, e, color, label, fmt="o", ms=3.5):
    ax.errorbar(0.5 * (edges[:-1] + edges[1:]), v, yerr=e, xerr=0.5 * (edges[1:] - edges[:-1]), fmt=fmt, ms=ms, lw=1.1, color=color, label=label)


def panel(E, curves, ylabel, text, stem):
    fig, ax = plt.subplots(figsize=(5.2, 4.4), dpi=150)
    for v, e, col, lab, fmt in curves:
        steps(ax, E, v, e, col, lab, fmt)
    ax.axhline(1, color="#999999", lw=0.8, ls=":"); ax.set_ylim(0, 2); ax.set_xscale("log"); ax.set_xlim(E[0], E[-1])
    ax.set_xlabel(r"$m(W_R)^{RECO}$ [GeV]"); ax.set_ylabel(ylabel)
    ax.text(0.04, 0.93, text, transform=ax.transAxes, fontsize=10)
    ax.legend(fontsize=8, loc="lower left", frameon=False); ax.tick_params(direction="in", top=True, right=True, which="both")
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(a.out, f"{stem}.{ext}"))
    plt.close(fig)


OUT = {}
for cat in EDGES:
    E = EDGES[cat]; c = cat.lower()
    r_nlo, e_nlo = ratio(NLO_CR[cat], LO_CR[cat])
    r_dat, e_dat = ratio((DATA[cat][0] - NONDY[cat][0], DATA[cat][1] + NONDY[cat][1]), LO_CR[cat])
    r_sr, e_sr = ratio(NLO_SR[cat], LO_SR[cat])
    panel(E, [(r_nlo, e_nlo, "#222222", "NLO/LO", "o"), (r_dat, e_dat, "#4477aa", r"(Data$-$non-DY)/LO", "s")],
          "ratio to LO DY", f"2024, {c} DY CR, ee+$\\mu\\mu$", f"fig31_nlo_lo_data_lo_{c}_2024")
    panel(E, [(r_nlo, e_nlo, "#222222", "NLO/LO in DY CR", "o"), (r_sr, e_sr, "#cc3311", "NLO/LO in SR", "s")],
          "NLO/LO ratio", f"2024, {c}, ee+$\\mu\\mu$", f"fig32_nlo_lo_cr_sr_{c}_2024")
    OUT[c] = {"edges": E.tolist(), "nlo_over_lo_cr": r_nlo.tolist(), "data_over_lo_cr": r_dat.tolist(), "nlo_over_lo_sr": r_sr.tolist()}
    print(cat, "\n  NLO/LO CR ", np.round(r_nlo, 3), "\n  Data/LO CR", np.round(r_dat, 3), "\n  NLO/LO SR ", np.round(r_sr, 3))
json.dump(OUT, open(os.path.join(a.out, "nlo_lo_mwr_2024_combined.json"), "w"), indent=1)
