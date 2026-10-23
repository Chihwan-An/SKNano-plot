#!/usr/bin/env python3
"""Resolved SR mumu SS (mll>400, mlljj>800, FO baseline, iso-TT), BLIND (no data): background BEFORE vs AFTER
replacing the MC nonprompt by the fake-factor estimate, with the statistical uncertainty each would carry.
  before: MC stack by sample group; stat = MC sum w^2.
  after : MC truth-PP only + Fake = (expected data fail events) x F x k - MC PP fail x F x k.
          The fail-event yields are taken from MC (expected data); its stat is the Poisson stat real data would
          have: var = sum_i w_i (F_i k)^2 (+ w_i^2 terms of the prompt subtraction and of the prompt MC).
  map: FOLOW MC (60<mll<300, SS+OS) truth-F, |eta| 0/0.8/1.5/2.0/2.4, one pT bin, L: 0.1<=TkRelIso<LMAX; k.
  ratio panel: relative stat error bands only (before / after), no data.
  -> out/nonprompt_ssmm/dycr/sr_mm_ss_ffapply.{png,pdf}, results/20_sr_ffapply.txt
"""
import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import mplhep as hep  # noqa: E402
import numpy as np  # noqa: E402

import fo_analysis as FA  # noqa: E402
import folib as L  # noqa: E402
import fr_mll60300 as FR  # noqa: E402
from plot_dycr_ffapply import GROUP, GCOL, ff_weights  # noqa: E402

hep.style.use("CMS")
VARS = [("mlljj", r"$m_{\mu\mu jj}$ (GeV)", np.array([800, 1000, 1200, 1400, 1600, 2000, 2400, 3200, 5000], float), lambda d: d["mlljj"]),
        ("lead_pt", r"leading $\mu$ $p_T$ (GeV)", np.array([53, 100, 200, 300, 500, 800, 1500], float), lambda d: d["mu1_pt"]),
        ("sub_pt", r"subleading $\mu$ $p_T$ (GeV)", np.array([53, 80, 120, 200, 300, 500, 1000], float), lambda d: d["mu2_pt"])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=float, default=1.27)
    ap.add_argument("--lmax", type=float, default=0.4)
    a = ap.parse_args()
    FR.PT = [53.0, 4000.0]
    lo, _ = FR.load()
    rm = FR.fmap(lo, lo["base"] & ~lo["data"] & (lo["mll"] > 60) & (lo["mll"] < 300), a.lmax)
    del lo
    d, _ = L.load()
    b = FA.bkg_mask(d, False)
    M = L.sel(d, "SS", "Full") & b          # FO baseline, SS, mll>400, mlljj>800, MC bkg noQCD
    TT = d["cat"] == "TT"
    w_exp = ff_weights(d, M, rm, a.k, a.lmax)                        # expected data fail x F k (all MC fail events)
    fac2 = np.where(d["weight"] != 0, (w_exp / np.where(d["weight"] != 0, d["weight"], 1)) ** 2, 0)
    var_poisson = d["weight"] * fac2                                  # Poisson stat of real data: sum w (Fk)^2
    w_pp = ff_weights(d, M & (d["pair"] == "PP"), rm, a.k, a.lmax)    # prompt subtraction (MC)
    txt = [f"# SR mumu SS (FO baseline, mll>400, mlljj>800), blind. map mll 60-300 MC, |eta| {FR.ETA}, L<{a.lmax}, k={a.k}",
           "# map f: " + " ".join(f"{x:.3f}" for x in rm.r[0])]
    fig, axes = plt.subplots(4, 3, figsize=(27, 22), gridspec_kw={"height_ratios": [3, 1.2, 3, 1.2]}, sharex="col")
    for c, (vn, xl, edges, fx) in enumerate(VARS):
        x = fx(d)
        before, after = {}, {}
        e2b = e2a = 0.0
        for p, g in GROUP.items():
            mp = M & TT & (d["proc"] == p)
            before[g] = before.get(g, 0) + np.histogram(x[mp], edges, weights=d["weight"][mp])[0]
            e2b = e2b + np.histogram(x[mp], edges, weights=d["weight"][mp] ** 2)[0]
            mpp = mp & (d["pair"] == "PP")
            after[g] = after.get(g, 0) + np.histogram(x[mpp], edges, weights=d["weight"][mpp])[0]
            e2a = e2a + np.histogram(x[mpp], edges, weights=d["weight"][mpp] ** 2)[0]
        fake = np.histogram(x, edges, weights=w_exp)[0] - np.histogram(x, edges, weights=w_pp)[0]
        fake_var = np.histogram(x, edges, weights=var_poisson)[0] + np.histogram(x, edges, weights=w_pp ** 2)[0]
        after["Fake (data-driven, exp.)"] = fake
        e2a = e2a + fake_var
        GCOL["Fake (data-driven, exp.)"] = "#9c9ca1"
        rels = []
        for row, (lab, stk, e2) in enumerate((("before: MC nonprompt", before, e2b),
                                               ("after: data-driven fake (expected)", after, e2a))):
            ax, rx = axes[2 * row, c], axes[2 * row + 1, c]
            order = [g for g in ("Others", "Fake (data-driven, exp.)", "Nonprompt", "TT+tW", "DY") if g in stk]
            hep.histplot([stk[g] for g in order], edges, stack=True, histtype="fill", color=[GCOL[g] for g in order],
                         label=order, ax=ax, edgecolor="k", lw=0.5)
            tot = sum(stk[g] for g in order)
            err = np.sqrt(np.clip(e2, 0, None))
            ax.stairs(tot + err, edges, baseline=np.clip(tot - err, 1e-3, None), fill=True, color="none",
                      hatch="////", edgecolor="grey", lw=0, label="bkg stat unc.")
            ax.set_yscale("log"); ax.set_ylim(0.05, tot.max() * 3000)
            ax.text(0.04, 0.92, lab, transform=ax.transAxes, fontsize=18)
            ax.legend(loc="upper right", fontsize=12, ncol=2, bbox_to_anchor=(1.0, 0.88))
            ax.set_ylabel("events / bin")
            hep.cms.label(ax=ax, label="Preliminary", data=False, lumi=109.8, com=13.6, fontsize=15)
            with np.errstate(divide="ignore", invalid="ignore"):
                rel = np.where(tot > 0, err / tot, 0)
            rels.append(rel)
            rx.stairs(1 + rel, edges, baseline=1 - rel, fill=True, color="none", hatch="////", edgecolor="grey", lw=0,
                      label="stat unc.")
            rx.axhline(1, color="grey", ls="--"); rx.set_ylim(0.3, 1.7); rx.set_ylabel("rel. stat", fontsize=16)
            for i in range(len(edges) - 1):
                rx.text(0.5 * (edges[i] + edges[i + 1]), 1.52, f"±{100 * rel[i]:.0f}%", ha="center", fontsize=11)
            txt.append(f"{vn} {lab:36s} total {tot.sum():.2f} ± {np.sqrt(np.clip(e2, 0, None).sum()):.2f}(stat)  "
                       + "  ".join(f"{g} {stk[g].sum():.2f}" for g in order))
            txt.append(f"   per-bin rel stat: " + " ".join(f"{100 * r:.0f}%" for r in rel))
        axes[3, c].set_xlabel(xl)
        if vn != "mlljj":
            continue
    od = os.path.join(L.PLOTS, "dycr"); os.makedirs(od, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(od, f"sr_mm_ss_ffapply.{ext}"), bbox_inches="tight")
    out = os.path.join(L.RESULTS, "20_sr_ffapply.txt")
    open(out, "w").write("\n".join(txt) + "\n")
    print("\n".join(txt)); print("wrote", out)


if __name__ == "__main__":
    sys.exit(main())
