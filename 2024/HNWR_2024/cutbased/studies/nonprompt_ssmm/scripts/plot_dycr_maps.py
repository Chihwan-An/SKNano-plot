#!/usr/bin/env python3
"""MC fake-rate maps (truth-F muons, r = T/FO) of the DY CR mumu FO production vs the SR map.
Writes out/nonprompt_ssmm/dycr/fakerate_maps.{png,pdf} and results/10_dycr_maps.txt.

  plot_dycr_maps.py
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


def main():
    d, _ = DA.load_dy()
    noQ = ~d["data"] & ~d["qcd"]
    sr, _ = L.load()
    maps = {
        "DY CR MC, SS": FA.build_map(d, d["base"] & d["ss"] & noQ, "F"),
        "DY CR MC, SS+OS": FA.build_map(d, d["base"] & noQ, "F"),
        "SR MC, SS low window": FA.maps(sr)["F_lowSS"],
    }
    del sr
    style = {"DY CR MC, SS": ("#e42536", "o"), "DY CR MC, SS+OS": ("#f89c20", "s"),
             "SR MC, SS low window": ("#5790fc", "^")}
    lines = []
    for k, m in maps.items():
        lines.append(m.table(k))
    out_t = os.path.join(L.RESULTS, "10_dycr_maps.txt")
    open(out_t, "w").write("\n\n".join(lines) + "\n")

    pt = np.asarray(FA.PT_EDGES, float)
    pt_draw = pt.copy(); pt_draw[-1] = 400.0          # last bin 200-4000 drawn to 400
    ctr = 0.5 * (pt_draw[:-1] + pt_draw[1:])
    fig, axes = plt.subplots(1, 2, figsize=(18, 8), sharey=True)
    for j, ax in enumerate(axes):
        for i, (k, m) in enumerate(maps.items()):
            col, mk = style[k]
            off = (i - 1) * 4.0
            ax.errorbar(ctr + off, m.r[:, j], yerr=m.err[:, j], xerr=None, fmt=mk, color=col, ms=9,
                        capsize=3, label=k)
        for e in pt_draw:
            ax.axvline(e, color="grey", lw=0.3, ls=":")
        ax.set_xlim(45, pt_draw[-1])
        ax.set_xlabel(r"muon $p_T$ (GeV)  [last bin 200+]")
        ax.text(0.05, 0.93, rf"$|\eta|$ {FA.ETA_EDGES[j]}-{FA.ETA_EDGES[j + 1]}", transform=ax.transAxes, fontsize=18)
        hep.cms.label(ax=ax, label="Preliminary", data=False, lumi=None, com=13.6, year="2024", fontsize=16)
    axes[0].set_ylabel(r"fake rate $f$ = N(T)/N(FO), truth-nonprompt $\mu$")
    axes[0].set_ylim(0, 0.35)
    axes[1].legend(loc="upper right", fontsize=14,
                   title="no W+jets / VVV / QCD yet" if not (d["proc"] == "W+jets(HT)").any() else None,
                   title_fontsize=12)
    od = os.path.join(L.PLOTS, "dycr")
    os.makedirs(od, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(od, f"fakerate_maps.{ext}"), bbox_inches="tight")
    print("wrote", od, out_t)


if __name__ == "__main__":
    main()
