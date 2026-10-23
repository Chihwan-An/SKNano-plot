#!/usr/bin/env python3
"""NLO pseudo-data validation of the DY jet-pT correction (AN2019_083 Fig. 31-32), 2024.

Fig 31: NLO/LO vs (data - non-DY)/LO in the DY control regions as a function of m(lljj) / m(lJ).
Fig 32: NLO/LO in the DY CR vs NLO/LO in the SR (transfer of a Z-peak correction to mll > 400 GeV).
Inputs:
  NLO  : $SKNANO_OUTPUT/HNWR/DYCRSplit_NoDYCorr_WeightSystOnly/2024/DYto2{E,Mu}_MLL*.root      (POWHEG, 18 samples)
  LO   : same dir, Skim_HNWR_DYto2L-4Jets_Bin-HT-*.root  (14 LO samples, C = EW = R = 1)
  data, non-DY (CR only): $SKNANO_OUTPUT/HNWR/DYCRStudy_RFlav/2024 (any variant, identical for non-DY/data)
Histograms: Central/DYCR_<cat>_<ch>_mlljj, Central/SR_<cat>_<ch>_mlljj (LO/NLO: MC only in the SR).
Output: ../validation/nlo_lo_mlljj_{cr,sr}_<cat>_<ch>.{pdf,png}
"""
import argparse, glob, os, re, sys
import numpy as np, uproot
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
sys.path.insert(0, "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased")
import config  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--prod", default="/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/DYCRSplit_NoDYCorr_WeightSystOnly/2024")
ap.add_argument("--cr", default="/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/DYCRStudy_RFlav/2024", help="data / non-DY for the CR")
ap.add_argument("--cr-variant", default="DYCR_NoCorr")
ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "validation"))
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
MBINS = {"Resolved": [800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 8000], "Boosted": [800, 1000, 1200, 1500, 1800, 8000]}
CH = {"EE": "ee", "MM": r"$\mu\mu$"}


def rebin(h, edges):
    v = h.values(flow=False); e = h.axis().edges(); w = h.variances(flow=False)
    idx = np.searchsorted(e, edges)
    return (np.array([v[idx[i]:idx[i + 1]].sum() for i in range(len(edges) - 1)]),
            np.array([w[idx[i]:idx[i + 1]].sum() for i in range(len(edges) - 1)]))


def collect(prod, prefix, selector, chdir="Central"):
    """sum histograms <chdir>/<prefix>_<cat>_<ch>_mlljj over the files accepted by selector(stem, ch)"""
    out = {}
    for p in sorted(glob.glob(os.path.join(prod, "*.root"))):
        stem = os.path.basename(p)[:-5]
        f = uproot.open(p)
        for cat in ("Resolved", "Boosted"):
            for ch in ("EE", "MM"):
                if not selector(stem, ch):
                    continue
                name = f"{chdir}/{prefix}_{cat}_{ch}_mlljj"
                if name not in f:
                    continue
                v, w = rebin(f[name], np.array(MBINS[cat], float))
                k = (cat, ch)
                out[k] = (out[k][0] + v, out[k][1] + w) if k in out else (v, w)
        f.close()
    return out


is_nlo = lambda s, ch: re.match(r"^DYto2(E|Mu)_MLL", s) is not None
is_lo = lambda s, ch: re.match(r"^Skim_HNWR_DYto2L", s) is not None


def is_data(s, ch):
    st = config.sample_stem(s)
    return st is not None and config.is_data(st, config.CHANNELS[ch]["data"])


def is_nondy(s, ch):
    st = config.sample_stem(s)
    if st is None or config.is_data(st) or config.is_signal(st):
        return False
    g, _ = config.classify_sample(re.sub(r"_p\d\d$", "", st))
    return g in ("TT", "Nonprompt", "Others")


NLO_CR = collect(a.prod, "DYCR", is_nlo); LO_CR = collect(a.prod, "DYCR", is_lo)
NLO_SR = collect(a.prod, "SR", is_nlo); LO_SR = collect(a.prod, "SR", is_lo)
DATA_CR = collect(a.cr, "DYCR", is_data, chdir=f"{a.cr_variant}/Central")
NONDY_CR = collect(a.cr, "DYCR", is_nondy, chdir=f"{a.cr_variant}/Central")
print("collected:", {k: len(v) for k, v in dict(NLO_CR=NLO_CR, LO_CR=LO_CR, NLO_SR=NLO_SR, LO_SR=LO_SR, DATA_CR=DATA_CR, NONDY_CR=NONDY_CR).items()})


def ratio(n, d):
    r = np.where(d[0] > 0, n[0] / np.where(d[0] > 0, d[0], 1), np.nan)
    e = r * np.sqrt(np.where(n[0] > 0, n[1] / np.where(n[0] > 0, n[0], 1) ** 2, 0) + np.where(d[0] > 0, d[1] / np.where(d[0] > 0, d[0], 1) ** 2, 0))
    return r, e


for cat in ("Resolved", "Boosted"):
    mb = np.array(MBINS[cat], float); xc = 0.5 * (mb[1:] + mb[:-1]); xw = 0.5 * np.diff(mb)
    xlab = r"$m_{\ell\ell jj}$ [GeV]" if cat == "Resolved" else r"$m_{\ell J}$ [GeV]"
    for ch in ("EE", "MM"):
        k = (cat, ch)
        if k not in NLO_CR or k not in LO_CR:
            print("missing", k); continue
        # --- Fig 31: NLO/LO vs (data - nonDY)/LO in the CR
        r_nlo, e_nlo = ratio(NLO_CR[k], LO_CR[k])
        if k in DATA_CR and k in NONDY_CR:
            dd = (DATA_CR[k][0] - NONDY_CR[k][0], DATA_CR[k][1] + NONDY_CR[k][1])
            r_dat, e_dat = ratio(dd, LO_CR[k])
            fig = plt.figure(figsize=(6, 5.6), dpi=150); gs = GridSpec(2, 1, height_ratios=[3, 1], hspace=0.05)
            ax = fig.add_subplot(gs[0]); axr = fig.add_subplot(gs[1], sharex=ax)
            ax.errorbar(xc, r_nlo, xerr=xw, yerr=e_nlo, fmt="ks", ms=4, label="NLO / LO")
            ax.errorbar(xc, r_dat, xerr=xw, yerr=e_dat, fmt="bo", ms=4, label="(Data $-$ non-DY) / LO")
            ax.axhline(1, color="gray", ls=":"); ax.set_ylim(0, 2.5); ax.set_ylabel("ratio to LO DY"); ax.legend(fontsize=8)
            ax.set_title(f"{cat} DY CR, {CH[ch]}, 2024", fontsize=10)
            dr, de = ratio((r_nlo, e_nlo ** 2), (r_dat, e_dat ** 2))
            axr.errorbar(xc, dr, xerr=xw, yerr=de, fmt="ko", ms=4); axr.axhline(1, color="gray", ls="--")
            axr.set_ylim(0.5, 1.5); axr.set_ylabel("NLO / (Data$-$non-DY)"); axr.set_xlabel(xlab); axr.set_xlim(mb[0], min(mb[-1], 4000))
            plt.setp(ax.get_xticklabels(), visible=False)
            fig.suptitle("CMS Work in progress   —   109.8 fb$^{-1}$ (13.6 TeV)", fontsize=9)
            for ext in ("pdf", "png"):
                fig.savefig(os.path.join(a.out, f"nlo_lo_mlljj_cr_{cat.lower()}_{ch}.{ext}"), bbox_inches="tight")
            plt.close(fig)
        # --- Fig 32: NLO/LO in CR vs SR
        if k in NLO_SR and k in LO_SR:
            r_sr, e_sr = ratio(NLO_SR[k], LO_SR[k])
            fig = plt.figure(figsize=(6, 5.6), dpi=150); gs = GridSpec(2, 1, height_ratios=[3, 1], hspace=0.05)
            ax = fig.add_subplot(gs[0]); axr = fig.add_subplot(gs[1], sharex=ax)
            ax.errorbar(xc, r_nlo, xerr=xw, yerr=e_nlo, fmt="ks", ms=4, label="NLO / LO, DY CR")
            ax.errorbar(xc + 0.1 * xw, r_sr, xerr=xw, yerr=e_sr, fmt="s", mfc="none", color="k", ms=4, ls="--", label="NLO / LO, SR")
            ax.axhline(1, color="gray", ls=":"); ax.set_ylim(0, 2.5); ax.set_ylabel("NLO / LO"); ax.legend(fontsize=8)
            ax.set_title(f"{cat}, {CH[ch]}, 2024", fontsize=10)
            dr, de = ratio((r_sr, e_sr ** 2), (r_nlo, e_nlo ** 2))
            axr.errorbar(xc, dr, xerr=xw, yerr=de, fmt="ko", ms=4); axr.axhline(1, color="gray", ls="--")
            axr.set_ylim(0.5, 1.5); axr.set_ylabel("SR / CR"); axr.set_xlabel(xlab); axr.set_xlim(mb[0], min(mb[-1], 4000))
            plt.setp(ax.get_xticklabels(), visible=False)
            fig.suptitle("CMS Work in progress   —   109.8 fb$^{-1}$ (13.6 TeV)", fontsize=9)
            for ext in ("pdf", "png"):
                fig.savefig(os.path.join(a.out, f"nlo_lo_mlljj_sr_{cat.lower()}_{ch}.{ext}"), bbox_inches="tight")
            plt.close(fig)
print("done ->", a.out)
