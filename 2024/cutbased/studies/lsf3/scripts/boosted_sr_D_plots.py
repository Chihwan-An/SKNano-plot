#!/usr/bin/env python3
"""Shape of the JMAR target-specific discriminant in the boosted SR, from the trees of boosted_sr_tagger_tree.py.

    P_top = TopbWqq + TopbWq + TopbWev + TopbWmv + TopbWtauhv
    D     = P_S / (P_S + a_top * P_top)          P_S = XWWqqev (SR EE) / XWWqqmv (SR MM)
The QCD term of the JMAR formula is dropped: in this region every background sits at P(QCD) < 0.05, so it has
nothing to reject, and including it only dilutes the discriminant (measured AUC against ttbar: 0.9705 with the
term at a_QCD = 1, 0.9753 without).  With a single background term a_top is a pure reparametrisation -- it moves
the scale of D but not the ordering of events -- so it is fixed to 1.

Shapes only: the backgrounds are one skim file each, so the normalisation is meaningless and every histogram is
drawn to unit area.  The raw class scores that go into D are plotted next to it, which is what has to be checked
before any efficiency or significance statement.
  <out>/D_<region>.png          the discriminant
  <out>/score_<region>.png      the raw P_S and P_top scores it is built from
  boosted_sr_D_plots.py [--sig trees_boosted_sig] [--bkg trees_boosted_bkg] [--alpha 1.0]"""
import argparse, glob, os
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import mplhep as hep
import ROOT

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--sig", default=f"{S}/trees_boosted_sig")
ap.add_argument("--bkg", default=f"{S}/trees_boosted_bkg")
ap.add_argument("--out", default=f"{S}/fatjet_taggers/globalpart3_D/01_raw_scores")
ap.add_argument("--alpha", type=float, default=1.0)
ap.add_argument("--suffix", default="", help="appended to the output file names, e.g. _a2")
ap.add_argument("--masses", default="1000,2000,3000,4000,5000,6000,7000")
a = ap.parse_args()
ROOT.gROOT.SetBatch(True)
hep.style.use("CMS")
os.makedirs(a.out, exist_ok=True)

TOP = ["TopbWev", "TopbWmv", "TopbWq", "TopbWqq", "TopbWtauhv"]
MASSES = [int(m) for m in a.masses.split(",")]
REG = {"SR_EE": ("isEE==1", "XWWqqev", "$W_R \\to eN \\to eejj$, boosted SR"),
       "SR_MM": ("isEE==0", "XWWqqmv", "$W_R \\to \\mu N \\to \\mu\\mu jj$, boosted SR")}
BKG = [("TTto2L2Nu_TuneCP5", "$t\\bar{t}$ (2L2Nu)", "tab:red"),
       ("DYto2L-4Jets_Bin-HT-400to800-MLL-120", "Drell-Yan (HT 400-800)", "gold"),
       ("WWto2L2Nu", "WW (2L2Nu)", "tab:blue")]
COL = plt.cm.viridis(np.linspace(0, 0.92, len(MASSES)))


def load(path, sel, sig_name):
    """P_S, P_top and the event weight of one tree, for the events of one region."""
    if not os.path.exists(path):
        return None
    d = ROOT.RDataFrame("tagger", path).Filter(f"region==1 && {sel}")
    cols = [f"p_{sig_name}", "w"] + [f"p_{t}" for t in TOP]
    A = d.AsNumpy(cols)
    if len(A["w"]) == 0:
        return None
    return A[f"p_{sig_name}"], sum(A[f"p_{t}"] for t in TOP), A["w"]


def unit(h):
    s = h.sum()
    return h / s if s > 0 else h


for region, (sel, sig_name, chlab) in REG.items():
    curves, bcurves = [], []
    for m, col in zip(MASSES, COL):
        r = load(f"{a.sig}/{region.split('_')[1]}_MWR{m}_N200.root", sel, sig_name)
        if r is None:
            continue
        curves.append((f"$m_{{W_R}}$ = {m / 1000:g} TeV", col, *r))
    for name, lab, col in BKG:
        r = load(f"{a.bkg}/{name}.root", sel, sig_name)
        if r is None:
            print(f"{region}: no events for {name}"); continue
        bcurves.append((lab, col, *r))
    if not curves:
        continue

    # ---- the discriminant ---------------------------------------------------------------------------------------
    eb = np.linspace(0, 1, 51)
    fig, ax = plt.subplots(figsize=(12, 9))
    print(f"\n== {region}   D = P_S / (P_S + {a.alpha:g} * P_top)")
    for lab, col, Ps, Pt, w in curves + bcurves:
        D = np.where(Ps + Pt > 0, Ps / np.maximum(Ps + a.alpha * Pt, 1e-30), 0.0)
        h = unit(np.histogram(D, bins=eb, weights=w)[0])
        ax.stairs(h, eb, color=col, lw=3 if lab.startswith("$m_") else 4,
                  ls="-" if lab.startswith("$m_") else "--", label=lab)
        print(f"   {lab:26s} n={len(D):6d}  중앙값={np.median(D):.4f}  D>0.5: {np.average(D > 0.5, weights=w) * 100:5.1f}%")
    ax.set_yscale("log"); ax.set_xlim(0, 1)
    ax.set_xlabel(f"$D = P_S\\,/\\,(P_S + {a.alpha:g}\\,P_{{top}})$"); ax.set_ylabel("fraction of events / 0.02")
    ax.grid(alpha=0.3, which="both")
    hep.cms.label("Work in progress", data=False, com=13.6, ax=ax, fontsize=16, rlabel="(13.6 TeV)")
    ax.legend(fontsize=12, loc="upper center", ncol=2, framealpha=0.93,
              title=f"{chlab}\n$m_N$ = 200 GeV, shapes only", title_fontsize=12)
    fig.tight_layout(); fig.savefig(f"{a.out}/D_{region}{a.suffix}.png", dpi=110); plt.close(fig)
    print(f"   wrote {a.out}/D_{region}.png")

    # ---- the raw scores D is built from -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    lo = np.logspace(-8, 0, 81)
    for ax, (vals, xl) in zip(axes, [(0, f"$P_S$ = {sig_name}"), (1, "$P_{top}$ = $\\sum$ TopbW*")]):
        for lab, col, Ps, Pt, w in curves + bcurves:
            v = (Ps, Pt)[vals]
            h = unit(np.histogram(np.clip(v, 1e-8, 1), bins=lo, weights=w)[0])
            ax.stairs(h, lo, color=col, lw=3 if lab.startswith("$m_") else 4,
                      ls="-" if lab.startswith("$m_") else "--", label=lab)
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(1e-6, 1)
        ax.set_xlabel(xl); ax.set_ylabel("fraction of events")
        ax.grid(alpha=0.3, which="both")
    axes[0].legend(fontsize=11, loc="upper left", ncol=2, framealpha=0.93, title=chlab, title_fontsize=11)
    hep.cms.label("Work in progress", data=False, com=13.6, ax=axes[0], fontsize=15, rlabel="")
    fig.tight_layout(); fig.savefig(f"{a.out}/score_{region}{a.suffix}.png", dpi=110); plt.close(fig)
    print(f"   wrote {a.out}/score_{region}.png")
print("BOOSTED_SR_D_PLOTS_DONE")
