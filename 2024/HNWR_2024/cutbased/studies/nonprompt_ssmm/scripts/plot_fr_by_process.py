#!/usr/bin/env python3
"""Muon fake rate f = T/(T+L) of truth-F muons vs pT, per MC process, in three regions:
DY CR mumu SS, SR mumu SS low window, SR sideband (SS+OS). MC noQCD, W+jets HT.
  -> out/nonprompt_ssmm/dycr/fakerate_by_process.{png,pdf}
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import mplhep as hep  # noqa: E402
import numpy as np  # noqa: E402

import dycr_analysis as DA  # noqa: E402
import fo_analysis as FA  # noqa: E402
import folib as L  # noqa: E402

hep.style.use("CMS")
PROCS = [("all MC", None, "black", "o"), ("TTLJ", "TTLJ", "#e42536", "s"), ("W+jets(HT)", "W+jets(HT)", "#5790fc", "^"),
         ("TTLL", "TTLL", "#f89c20", "v"), ("tW", "tW", "#964a8b", "D")]


def main():
    dy, _ = DA.load_dy()
    sr, _ = L.load()
    b = FA.bkg_mask(sr, False)
    sb = sr["base"] & (((sr["mll"] > 400) & (sr["mlljj"] < 800)) | ((sr["mll"] > 200) & (sr["mll"] < 400))) & b
    regions = [("DY CR $\\mu\\mu$ SS", dy, dy["base"] & dy["ss"] & ~dy["data"] & ~dy["qcd"]),
               ("SR $\\mu\\mu$ SS low (800-1600)", sr, L.sel(sr, "SS", "Low") & b),
               ("sideband SS+OS (outside SR)", sr, sb)]
    pt = np.asarray(FA.PT_EDGES, float)
    pt_draw = pt.copy(); pt_draw[-1] = 400.0
    ctr = 0.5 * (pt_draw[:-1] + pt_draw[1:])
    fig, axes = plt.subplots(2, 3, figsize=(27, 16), sharey="row")
    for c, (rname, d, m) in enumerate(regions):
        for i, (lab, proc, col, mk) in enumerate(PROCS):
            mm = m if proc is None else m & (d["proc"] == proc)
            if not mm.any():
                continue
            rm = FA.build_map(d, mm, "F")
            neffT = np.where(rm.T2 > 0, rm.T ** 2 / np.where(rm.T2 > 0, rm.T2, 1), 0)
            for j in range(2):
                ok = (rm.T[:, j] + rm.L[:, j] > 0) & (neffT[:, j] >= 3)   # hide bins with < 3 effective passing muons
                off = (i - 2) * 3.0
                axes[j, c].errorbar(ctr[ok] + off, rm.r[ok, j], yerr=rm.err[ok, j], fmt=mk, color=col, ms=10,
                                    capsize=3, label=lab, mfc=col if proc else "none", mew=2)
        for j in range(2):
            ax = axes[j, c]
            ax.set_xlim(45, 400)
            ax.set_ylim(0, 0.40)
            for e in pt_draw:
                ax.axvline(e, color="grey", lw=0.3, ls=":")
            ax.text(0.04, 0.92, f"{rname}\n$|\\eta|$ {FA.ETA_EDGES[j]}-{FA.ETA_EDGES[j + 1]}", transform=ax.transAxes,
                    fontsize=17, va="top")
            ax.set_xlabel(r"muon $p_T$ (GeV)  [last bin 200+]")
            hep.cms.label(ax=ax, label="Preliminary", data=False, lumi=None, com=13.6, year="2024", fontsize=15)
    for j in range(2):
        axes[j, 0].set_ylabel(r"fake rate $f$ = N(T)/N(FO), truth-F $\mu$")
    axes[0, 2].legend(loc="upper right", fontsize=15, title="bins with $N_{eff}(T)<3$ hidden", title_fontsize=12)
    od = os.path.join(L.PLOTS, "dycr")
    os.makedirs(od, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(od, f"fakerate_by_process.{ext}"), bbox_inches="tight")
    print("wrote", od)


if __name__ == "__main__":
    main()
