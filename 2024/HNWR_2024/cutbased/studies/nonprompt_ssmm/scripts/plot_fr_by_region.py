#!/usr/bin/env python3
"""Muon fake rate f = T/(T+L) of truth-F muons vs pT (all MC background, noQCD, W+jets HT), regions overlaid.
  plot_fr_by_region.py [--proc TTLJ]   -> out/nonprompt_ssmm/dycr/fakerate_by_region[_<proc>].{png,pdf}
"""
import argparse
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--proc", default="", help="restrict to one MC process (folib.process_of name, e.g. TTLJ)")
    ap.add_argument("--eta", default="", help="comma-separated |eta| edges, e.g. 0,0.8,1.5,2.0,2.4 (default folib/fo_analysis 0,1.2,2.4)")
    ap.add_argument("--lmax", type=float, default=0.0, help="upper TkRelIso cut on L muons (FO = T or 0.1<=iso<lmax); 0 = none")
    a = ap.parse_args()
    dy, _ = DA.load_dy()
    sr, _ = L.load()
    b = FA.bkg_mask(sr, False)
    sbA = (sr["mll"] > 400) & (sr["mlljj"] < 800)
    sbB = (sr["mll"] > 200) & (sr["mll"] < 400)
    regions = [
        ("DY CR SS (60<mll<150, mlljj>800)", dy, dy["base"] & dy["ss"] & ~dy["data"] & ~dy["qcd"], "#5790fc", "o"),
        ("SR SS (mll>400, mlljj>800)", sr, L.sel(sr, "SS", "Full") & b, "black", "s"),
        ("SR SS low (800<mlljj<1600)", sr, L.sel(sr, "SS", "Low") & b, "#9c9ca1", "D"),
        ("sideband SS+OS (mll>200, not SR)", sr, sr["base"] & (sbA | sbB) & b, "#e42536", "^"),
        ("SB-A SS+OS (mll>400, mlljj<800)", sr, sr["base"] & sbA & b, "#f89c20", "v"),
    ]
    if a.proc:
        regions = [(lab, d, m & (d["proc"] == a.proc), col, mk) for lab, d, m, col, mk in regions]
    eta = [float(x) for x in a.eta.split(",")] if a.eta else list(FA.ETA_EDGES)
    neta = len(eta) - 1
    pt = np.asarray(FA.PT_EDGES, float)
    pt_draw = pt.copy(); pt_draw[-1] = 400.0
    ctr = 0.5 * (pt_draw[:-1] + pt_draw[1:])
    fig, axes = plt.subplots(1, neta, figsize=(10 * neta, 9), sharey=True)
    for i, (lab, d, m, col, mk) in enumerate(regions):
        rm = L.RateMap(FA.PT_EDGES, eta)
        for k in (1, 2):
            iso = d[f"mu{k}_tkRelIso"]
            sel = m & (d[f"t{k}"] == "F")
            if a.lmax > 0:
                sel &= iso < a.lmax          # muons above the L upper cut are not FO
            rm.fill(d[f"mu{k}_pt"][sel], d[f"mu{k}_eta"][sel], iso[sel] < L.TIGHT_ISO, d["weight"][sel])
        neffT = np.where(rm.T2 > 0, rm.T ** 2 / np.where(rm.T2 > 0, rm.T2, 1), 0)
        for j, ax in enumerate(axes):
            ok = (rm.T[:, j] + rm.L[:, j] > 0) & (neffT[:, j] >= 3)
            ax.errorbar(ctr[ok] + (i - 2) * 3.5, rm.r[ok, j], yerr=rm.err[ok, j], fmt=mk, color=col, ms=10,
                        capsize=3, mew=2, label=lab)
    for j, ax in enumerate(axes):
        ax.set_xlim(45, 400)
        ax.set_ylim(0, 0.6 if a.lmax > 0 else 0.45)
        for e in pt_draw:
            ax.axvline(e, color="grey", lw=0.3, ls=":")
        ax.text(0.04, 0.93, rf"$|\eta|$ {eta[j]:g}-{eta[j + 1]:g}", transform=ax.transAxes, fontsize=20)
        ax.set_xlabel(r"muon $p_T$ (GeV)  [last bin 200+]")
        hep.cms.label(ax=ax, label="Preliminary", data=False, lumi=None, com=13.6, year="2024", fontsize=16)
    axes[0].set_ylabel(r"fake rate $f$ = N(T)/N(FO), truth-F $\mu$, " + (a.proc or "all MC"))
    axes[-1].legend(loc="upper right", fontsize=13, title=(a.proc or "MC noQCD") + (f"; L: 0.1<=TkRelIso<{a.lmax:g}" if a.lmax > 0 else "; L: TkRelIso>=0.1") + r"; $N_{eff}(T)<3$ hidden", title_fontsize=12)
    od = os.path.join(L.PLOTS, "dycr")
    os.makedirs(od, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(od, f"fakerate_by_region{'_' + a.proc if a.proc else ''}{f'_lmax{a.lmax:g}' if a.lmax > 0 else ''}{f'_eta{neta}' if a.eta else ''}.{ext}"), bbox_inches="tight")
    print("wrote", od)


if __name__ == "__main__":
    main()
