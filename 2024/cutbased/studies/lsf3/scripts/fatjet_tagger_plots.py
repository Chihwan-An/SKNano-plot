#!/usr/bin/env python3
"""Plots of the per-event max GlobalParT3 XWWqqev / XWWqqmv score in the W_R signal samples (from fatjet_tagger_hists.py).
For each tagger (folder <out>/<tagger>/):
  MWR<m>_N<n>/<tagger>_<CH>_MWR<m>_N<n>.png : left = distribution of the per-event max score (fraction of all events per bin),
      right = pass rate (fraction of all events with max score > cut) vs the cut; all fatjets and fatjets with LSF3 > 0.75
  N200_all_masspoints/<tagger>_<CH>_N200_<all|LSF075>.png : every W_R mass with N = 200 in one plot (distribution + pass rate)
  passrate_<tagger>.md : pass rates at cuts 0.5 / 0.8 / 0.9 for every point
  fatjet_tagger_plots.py [--hists studies/lsf3/hists_fatjet_taggers] [--out studies/lsf3/fatjet_taggers]"""
import argparse, glob, os, re
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import mplhep as hep

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--hists", default=f"{S}/hists_fatjet_taggers")
ap.add_argument("--out", default=f"{S}/fatjet_taggers")
ap.add_argument("--n200-only", action="store_true", help="only the N = 200 plots (skip the per-point plots and the table)")
a = ap.parse_args()
hep.style.use("CMS")

TAGGERS = {"XWWqqev": "GlobalParT3 XWW(qq e#nu)".replace("#nu", "$\\nu$"), "XWWqqmv": "GlobalParT3 XWW(qq $\\mu\\nu$)"}
TAGCH = {"XWWqqev": "EE", "XWWqqmv": "MM"}   # each tagger only on the signal of its own lepton flavour
CHLAB = {"EE":"$W_R \\to eN \\to eejj$", "MM": "$W_R \\to \\mu N \\to \\mu\\mu jj$"}
SEL = {"all": "all fatjets", "lsf": "fatjets with LSF$_3$ > 0.75"}
CUTS = [0.3, 0.5, 0.7]   # the per-event max score stays below ~0.75 in the signal
REB = 4   # 200 -> 50 bins for the distribution

pts = {}
for p in sorted(glob.glob(f"{a.hists}/*.npz")):
    m = re.match(r"(EE|MM)_MWR(\d+)_N(\d+)\.npz", os.path.basename(p))
    if m: pts[(m.group(1), int(m.group(2)), int(m.group(3)))] = dict(np.load(p))
print(f"{len(pts)} points")

def passrate(h, T):   # fraction of events with score >= bin low edge, per bin edge
    return np.cumsum(h[::-1])[::-1] / T
def dist(h, T):
    return h.reshape(-1, REB).sum(axis=1) / T
def label(ax, ch):
    hep.cms.label("Work in progress", data=False, com=13.6, ax=ax, fontsize=16, rlabel="(13.6 TeV)")
    ax.text(0.04, 0.96, CHLAB[ch], transform=ax.transAxes, va="top", fontsize=17)

n = 0
for tag, tlab in TAGGERS.items():
    tdir = f"{a.out}/{tag}"; os.makedirs(tdir, exist_ok=True)
    md = [f"# {tag}: pass rate of the per-event max score (W_R signal, 2024 skims)", "",
          "Pass rate = fraction of all events of the HNWR3SR skim with max score over the fatjets > cut; 'LSF' = only fatjets with LSF3 > 0.75.", "",
          "| channel | m_WR | m_N | events | with fatjet | " + " | ".join(f"all > {c}" for c in CUTS) + " | " + " | ".join(f"LSF > {c}" for c in CUTS) + " |",
          "|---|---|---|---|---|" + "---|" * (2 * len(CUTS))]
    for (ch, mwr, mn), r in ([] if a.n200_only else sorted(pts.items())):
        if ch != TAGCH[tag]: continue
        T = r["total"]; e = r["edges"]; c = 0.5 * (e[1:] + e[:-1])
        fig, axs = plt.subplots(1, 2, figsize=(22, 9))
        for sel, col in (("all", "tab:blue"), ("lsf", "tab:red")):
            h = r[f"h_{sel}_{tag}"]; pr = passrate(h, T)
            eb = e[::REB]
            axs[0].stairs(dist(h, T), eb, color=col, lw=2, label=f"{SEL[sel]} (any: {h.sum() / T * 100:.1f}%)")
            axs[1].plot(e[:-1], pr, color=col, lw=2, label=SEL[sel] + ": " + ", ".join(f">{cc}: {pr[int(round(cc * 200))] * 100:.1f}%" for cc in CUTS))
        axs[0].set_yscale("log"); axs[0].set_ylim(1e-4, 2); axs[0].set_xlabel(f"max {tlab} score"); axs[0].set_ylabel("fraction of events / 0.02")
        axs[1].set_ylim(0, 1.05); axs[1].set_xlabel(f"cut on max {tlab} score"); axs[1].set_ylabel("pass rate (score > cut)")
        for j, ax in enumerate(axs):   # axs[0] = distribution, axs[1] = pass rate (legend bottom left)
            ax.set_xlim(0, 1); label(ax, ch)
            ax.legend(fontsize=14, loc="lower left" if j else "upper right", title=f"$m_{{W_R}}$ = {mwr} GeV, $m_N$ = {mn} GeV", title_fontsize=15)
        fig.tight_layout(); d = f"{tdir}/MWR{mwr}_N{mn}"; os.makedirs(d, exist_ok=True)
        fig.savefig(f"{d}/{tag}_{ch}_MWR{mwr}_N{mn}.png", dpi=90); plt.close(fig); n += 1
        pa, pl = passrate(r[f"h_all_{tag}"], T), passrate(r[f"h_lsf_{tag}"], T)
        md.append(f"| {ch} | {mwr} | {mn} | {T:.0f} | {r['n_anyfj'] / T * 100:.1f}% | " + " | ".join(f"{pa[int(round(cc * 200))] * 100:.1f}%" for cc in CUTS) + " | "
                  + " | ".join(f"{pl[int(round(cc * 200))] * 100:.1f}%" for cc in CUTS) + " |")
    # N = 200: every W_R mass in one plot
    nd = f"{tdir}/N200_all_masspoints"; os.makedirs(nd, exist_ok=True)
    for ch in (TAGCH[tag],):
        masses = sorted(m for (c, m, nn) in pts if c == ch and nn == 200)
        cmap = plt.get_cmap("viridis")(np.linspace(0, 0.95, max(len(masses), 1)))
        for sel, stag in (("all", "all"), ("lsf", "LSF075")):
            fig, axs = plt.subplots(1, 2, figsize=(22, 9))
            for k, m in enumerate(masses):
                r = pts[(ch, m, 200)]; T = r["total"]; e = r["edges"]; h = r[f"h_{sel}_{tag}"]; pr = passrate(h, T)
                axs[0].stairs(dist(h, T), e[::REB], color=cmap[k], lw=2, label=f"$m_{{W_R}}$ = {m / 1000:g} TeV")
                axs[1].plot(e[:-1], pr, color=cmap[k], lw=2, label=f"$m_{{W_R}}$ = {m / 1000:g} TeV (>0.5: {pr[100] * 100:.1f}%, >0.7: {pr[140] * 100:.2f}%)")
            axs[0].set_yscale("log"); axs[0].set_ylim(1e-4, 2); axs[0].set_xlabel(f"max {tlab} score"); axs[0].set_ylabel("fraction of events / 0.02")
            axs[1].set_ylim(0, 1.05); axs[1].set_xlabel(f"cut on max {tlab} score"); axs[1].set_ylabel("pass rate (score > cut)")
            for j, ax in enumerate(axs):   # axs[0] = distribution, axs[1] = pass rate (legend bottom left)
                ax.set_xlim(0, 1); label(ax, ch)
                ax.legend(fontsize=13, loc="lower left" if j else "upper right", title=f"$m_N$ = 200 GeV, {SEL[sel]}", title_fontsize=14)
            fig.tight_layout(); fig.savefig(f"{nd}/{tag}_{ch}_N200_{stag}.png", dpi=90); plt.close(fig); n += 1
            # pass rate only
            fig, ax = plt.subplots(figsize=(12, 9))
            for k, m in enumerate(masses):
                r = pts[(ch, m, 200)]; pr = passrate(r[f"h_{sel}_{tag}"], r["total"])
                ax.plot(r["edges"][:-1], pr, color=cmap[k], lw=2.5, label=f"$m_{{W_R}}$ = {m / 1000:g} TeV")
            ax.set_xlim(0, 0.8); ax.set_ylim(0, 1.05); ax.set_xlabel(f"cut on max {tlab} score"); ax.set_ylabel("pass rate (score > cut)")
            ax.grid(alpha=0.3); label(ax, ch); ax.legend(fontsize=16, loc="lower left", title=f"$m_N$ = 200 GeV, {SEL[sel]}", title_fontsize=15)
            fig.tight_layout(); fig.savefig(f"{nd}/{tag}_{ch}_N200_{stag}_passrate.png", dpi=110); plt.close(fig); n += 1
        # pass rate vs m_WR at fixed cuts, all fatjets (solid) vs LSF3 > 0.75 (dashed)
        fig, ax = plt.subplots(figsize=(12, 9))
        for cc, col in zip(CUTS, ("tab:blue", "tab:orange", "tab:green")):
            for sel, ls in (("all", "-"), ("lsf", "--")):
                y = [passrate(pts[(ch, m, 200)][f"h_{sel}_{tag}"], pts[(ch, m, 200)]["total"])[int(round(cc * 200))] * 100 for m in masses]
                ax.plot([m / 1000 for m in masses], y, ls, marker="o", color=col, lw=2.5, ms=8, label=f"score > {cc}, {SEL[sel]}")
        ax.set_yscale("log"); ax.set_ylim(0.005, 3000); ax.set_xlabel("$m_{W_R}$ [TeV]"); ax.set_ylabel("pass rate [%]")
        ax.grid(alpha=0.3, which="both"); label(ax, ch)
        ax.legend(fontsize=12, loc="lower left", title=f"{tlab}, $m_N$ = 200 GeV (solid: all fatjets, dashed: LSF$_3$ > 0.75)", title_fontsize=12, ncol=2)
        fig.tight_layout(); fig.savefig(f"{nd}/{tag}_{ch}_N200_passrate_vs_mWR.png", dpi=110); plt.close(fig); n += 1
    if not a.n200_only: open(f"{tdir}/passrate_{tag}.md", "w").write("\n".join(md) + "\n")
print(f"{n} plots under {a.out}"); print("FATJET_TAGGER_PLOTS_DONE")
