#!/usr/bin/env python3
"""Leading-jet pT shape vs m(ll) window, one jet (m(llj) > 800, no AK8) vs two jets (resolved, m(lljj) > 800). OS, stat errors only.
Input: quick local JetXcheck run (a few files per sample), /gv0/Users/achihwan/SKNanoOutput_jetxcheck/<sample>/hists_*.root;
MC scaled by total/used files, data (period G) used for shapes only. Weights WITHOUT the DY jet-pT R (`_noR`) unless stated.

Fig. 1  DY MC: j1pt shape ratio  m(ll)>400 / m(ll) 60-150  for 1j, 2j, 2j-noAK8  -> is the m(ll) dependence the same?
Fig. 2  1j data/MC (DY+ttbar+tW, noR) shape in m(ll) 60-150 and > 400, plus 2j 60-150 (DY CR) -> would R derived at low m(ll) fit high m(ll)?
"""
import glob, os
import numpy as np
import uproot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

IN = "/gv0/Users/achihwan/SKNanoOutput_jetxcheck"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plots")
EDGES = np.array([40, 70, 100, 150, 200, 300, 400, 600, 800, 1200, 2000.])
os.makedirs(OUT, exist_ok=True)


def group_files(g):
    if g == "DY": return sorted(glob.glob(f"{IN}/Skim_HNWR_DYto2L-4Jets_*"))
    if g == "TT": return [f"{IN}/{s}" for s in ["Skim_HNWR_TTto2L2Nu_TuneCP5", "Skim_HNWR_TWminusto2L2Nu", "Skim_HNWR_TbarWplusto2L2Nu"]]
    if g == "dataMM": return [f"{IN}/Skim_HNWR_Muon0_G", f"{IN}/Skim_HNWR_Muon1_G"]
    if g == "dataEE": return [f"{IN}/Skim_HNWR_EGamma0_G", f"{IN}/Skim_HNWR_EGamma1_G"]


CACHE = {}


def hist(g, name):
    """sum over the group's samples, rebinned to EDGES; returns (values, variances)"""
    key = (g, name)
    if key in CACHE: return CACHE[key]
    v = np.zeros(len(EDGES) - 1); e2 = np.zeros(len(EDGES) - 1)
    for d in group_files(g):
        tot, used = map(int, open(f"{d}/scale.txt").read().split()) if os.path.exists(f"{d}/scale.txt") else (1, 1)
        sc = tot / used if not g.startswith("data") else 1.0
        for f in glob.glob(f"{d}/hists_*.root"):
            try: h = uproot.open(f)[f"Central/{name}"]
            except Exception: continue
            x = h.axis().edges(); c = h.values(); w2 = h.variances()
            idx = np.digitize(0.5 * (x[:-1] + x[1:]), EDGES) - 1
            ok = (idx >= 0) & (idx < len(v))
            np.add.at(v, idx[ok], c[ok] * sc); np.add.at(e2, idx[ok], w2[ok] * sc * sc)
    CACHE[key] = (v, e2); return v, e2


def norm(v, e2):
    s = v.sum()
    return (v / s, np.sqrt(e2) / s) if s > 0 else (v * np.nan, v * np.nan)


def ratio(a, b):
    (va, ea), (vb, eb) = a, b
    with np.errstate(divide="ignore", invalid="ignore"):
        r = va / vb; er = r * np.sqrt((ea / va) ** 2 + (eb / vb) ** 2)
    return r, er


x = 0.5 * (EDGES[:-1] + EDGES[1:]); xe = 0.5 * np.diff(EDGES)
L = ["# leading-jet pT vs m(ll): one jet (m(llj)>800, no AK8) vs two jets (m(lljj)>800), OS, stat only", "",
     "quick local run (few files/sample, data = period G only). weights without R unless noted.", ""]
for ch in ["MM", "EE"]:
    # ---------- Fig. 1: DY MC ratio of shapes
    fig, axs = plt.subplots(2, 1, figsize=(7.5, 7.5), sharex=True, gridspec_kw={"height_ratios": [1.4, 1]})
    L += [f"## {ch}: DY MC, shape ratio m(ll)>400 / m(ll) 60-150 (normalised), noR", "",
          "| j1 pT | " + " | ".join(f"{EDGES[i]:.0f}-{EDGES[i+1]:.0f}" for i in range(len(x))) + " |", "|---" * (len(x) + 1) + "|"]
    for sel, col, mk in [("1j", "#c2410c", "o"), ("2j", "#1d4ed8", "s"), ("2jnoAK8", "#0f766e", "^")]:
        lo = hist("DY", f"JX_{ch}_{sel}_mll60to150_j1pt_noR"); hi = hist("DY", f"JX_{ch}_{sel}_mll400_j1pt_noR")
        nl, nh = norm(*lo), norm(*hi)
        axs[0].errorbar(x, nl[0], nl[1], xerr=xe, fmt=mk, mfc="none", color=col, ms=5, label=f"{sel}  m(ll) 60-150")
        axs[0].errorbar(x, nh[0], nh[1], xerr=xe, fmt=mk, color=col, ms=5, label=f"{sel}  m(ll) > 400")
        r, er = ratio(nh, nl)
        axs[1].errorbar(x * (1 + {"1j": -0.02, "2j": 0, "2jnoAK8": 0.02}[sel]), r, er, fmt=mk, color=col, ms=5, label=sel)
        L.append(f"| {sel} | " + " | ".join(f"{a:.2f}±{b:.2f}" if np.isfinite(a) else "-" for a, b in zip(r, er)) + " |")
        L.append(f"| {sel} raw DY (60-150 / >400) | {lo[0].sum():.0f} / {hi[0].sum():.0f} |" + " |" * (len(x) - 1))
    axs[0].set_yscale("log"); axs[0].set_ylabel("fraction / bin"); axs[0].legend(fontsize=7, ncol=2)
    axs[0].set_title(f"{ch} OS, DY MC (no R): leading-jet pT shape by m(ll)", fontsize=10, loc="left")
    axs[1].axhline(1, color="gray", lw=0.8); axs[1].set_xscale("log"); axs[1].set_ylim(0, 3)
    axs[1].set_ylabel("m(ll)>400 / 60-150"); axs[1].set_xlabel("leading jet pT (GeV)"); axs[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(f"{OUT}/dy_shape_ratio_{ch}.png", dpi=130); plt.close(fig)
    L.append("")

    # ---------- Fig. 2: data / MC shape (normalised) in each region, noR
    dat = f"data{ch}"
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    L += [f"## {ch}: data/MC (DY+ttbar+tW, noR, each normalised), shape", "",
          "| region | data | MC | " + " | ".join(f"{EDGES[i]:.0f}-{EDGES[i+1]:.0f}" for i in range(len(x))) + " |", "|---" * (len(x) + 3) + "|"]
    regs = [("1j", "mll60to150", "#c2410c", "o", "none"), ("1j", "mll400", "#c2410c", "o", None),
            ("2j", "mll60to150", "#1d4ed8", "s", "none"), ("1j", "mll150to400", "#7c3aed", "D", "none"),
            ("2j", "mll150to400", "#1d4ed8", "D", None)]
    for i, (sel, win, col, mk, mfc) in enumerate(regs):
        n = f"JX_{ch}_{sel}_{win}_j1pt_noR"
        d = hist(dat, n); dy = hist("DY", n); tt = hist("TT", n)
        mc = (dy[0] + tt[0], dy[1] + tt[1])
        r, er = ratio(norm(*d), norm(*mc))
        ax.errorbar(x * (1 + 0.015 * (i - 2)), r, er, fmt=mk, color=col, mfc=mfc or col, ms=5, label=f"{sel} {win} (data {d[0].sum():.0f})")
        L.append(f"| {sel} {win} | {d[0].sum():.0f} | {mc[0].sum():.0f} (DY {dy[0].sum() / max(mc[0].sum(), 1e-9):.0%}) | "
                 + " | ".join(f"{a:.2f}±{b:.2f}" if np.isfinite(a) else "-" for a, b in zip(r, er)) + " |")
    ax.axhline(1, color="gray", lw=0.8); ax.set_xscale("log"); ax.set_ylim(0, 2.5)
    ax.set_xlabel("leading jet pT (GeV)"); ax.set_ylabel("data / MC (shape, no R)")
    ax.set_title(f"{ch} OS: data/MC shape by m(ll), one vs two jets (2j m(ll)>400 = SR, blind)", fontsize=10, loc="left")
    ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(f"{OUT}/datamc_shape_{ch}.png", dpi=130); plt.close(fig)
    L.append("")
open(f"{OUT}/summary.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
