#!/usr/bin/env python3
"""LHE full-shape vs SR-passing (resolved/boosted) shapes, from WRGenRecoMass output.

Unlike the old Offshell_test plots (python LHE cache + unit-normalized reco shapes
scaled by a single efficiency), everything here comes from one analyzer file and
the SR histograms are true per-bin subsets of the full LHE distribution:
  gray    = LHE_mass_lljj_all_noweight / N_total          (sums to 1)
  stacked = SR_{Resolved,Boosted}_{ch}_lhe_mass_noweight / N_total
so the stack is bin-by-bin <= gray, and its integral is the category fraction.
"""

import glob, math, os, re
import numpy as np
import uproot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep

hep.style.use("CMS")

IN_DIR  = "/gv0/Users/achihwan/SKNanoOutput/WRGenRecoMass/2023"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

REBIN = 200          # display binning in GeV (input histograms are 1 GeV)
XMAX_FACTOR = 1.2

COLOR_LHE      = "dimgray"
COLOR_BOOSTED  = "steelblue"
COLOR_RESOLVED = "tomato"

# sumall, not lljj: the lljj definition collapses to ~0 for samples whose LHE
# record keeps N undecayed (N200 and N=WR/2 points). sumall equals lljj for the
# fully-decayed samples and stays correct for the undecayed ones.
H_ALL   = "LHE_mass_sumall_all_noweight"
H_RES   = "Central/SR_Resolved_{ch}_lhe_mass_noweight"
H_BOO   = "Central/SR_Boosted_{ch}_lhe_mass_noweight"
# BDT-preselection SR (WRGenRecoMass::FillBDTPreselSR) — drawn as step outlines
# when present; silently skipped for outputs produced before that fill existed.
H_BDT_RES = "Central/BDTSR_Resolved_{ch}_lhe_mass_noweight"
H_BDT_BOO = "Central/BDTSR_Boosted_{ch}_lhe_mass_noweight"
COLOR_BDT_BOOSTED  = "navy"
COLOR_BDT_RESOLVED = "darkred"


def load_rebinned(f, name):
    if name not in f:
        return None
    vals  = f[name].values(flow=False)
    edges = f[name].axis().edges()
    n = len(vals) // REBIN * REBIN
    vals = vals[:n].reshape(-1, REBIN).sum(axis=1)
    edges = edges[: n + 1 : REBIN]
    return vals, edges


def discover_points():
    points = {}
    for path in glob.glob(f"{IN_DIR}/WR*N*.root"):
        m = re.match(r"WR(\d+)N(\d+)(EE|MM)\.root", os.path.basename(path))
        if not m:
            continue
        wr, n, ch = int(m.group(1)), int(m.group(2)), m.group(3)
        # skip the undecayed-N LHE productions (N200 and N=WR/2): their SR
        # histograms from the pre-fix analyzer sit at m~0 (see README note)
        if n == 200 or 2 * n == wr:
            continue
        points.setdefault((wr, ch), []).append(n)
    return {k: sorted(v) for k, v in points.items()}


def make_grid(wr, ch, n_list):
    ncols = math.ceil(math.sqrt(len(n_list)))
    nrows = math.ceil(len(n_list) / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 5, nrows * 4.5), squeeze=False)
    axes_flat = axes.flatten()
    x_max = wr * XMAX_FACTOR

    for i, n in enumerate(n_list):
        ax = axes_flat[i]
        with uproot.open(f"{IN_DIR}/WR{wr}N{n}{ch}.root") as f:
            all_h = load_rebinned(f, H_ALL)
            res_h = load_rebinned(f, H_RES.format(ch=ch))
            boo_h = load_rebinned(f, H_BOO.format(ch=ch))
            bdt_res_h = load_rebinned(f, H_BDT_RES.format(ch=ch))
            bdt_boo_h = load_rebinned(f, H_BDT_BOO.format(ch=ch))
        if all_h is None:
            ax.axis("off")
            continue
        all_v, edges = all_h
        n_tot = all_v.sum()
        if n_tot <= 0:
            ax.axis("off")
            continue

        gray = all_v / n_tot
        res  = (res_h[0] / n_tot) if res_h is not None else np.zeros_like(gray)
        boo  = (boo_h[0] / n_tot) if boo_h is not None else np.zeros_like(gray)
        eff_r, eff_b = res.sum(), boo.sum()

        hep.histplot(gray, bins=edges, ax=ax, histtype="fill",
                     color=COLOR_LHE, alpha=0.25, linewidth=1, edgecolor=COLOR_LHE,
                     label="LHE all")
        hep.histplot([boo, res], bins=edges, ax=ax, stack=True, histtype="fill",
                     color=[COLOR_BOOSTED, COLOR_RESOLVED], alpha=0.7,
                     label=[f"Boosted SR  ε={eff_b:.2%}",
                            f"Resolved SR  ε={eff_r:.2%}"])

        # BDT-preselection SR — stacked like the cut-based SR (boosted bottom,
        # resolved on top), drawn as dashed step outlines with the same
        # normalization so the stack tops are directly comparable
        if bdt_res_h is not None or bdt_boo_h is not None:
            bdt_res = (bdt_res_h[0] / n_tot) if bdt_res_h is not None else np.zeros_like(gray)
            bdt_boo = (bdt_boo_h[0] / n_tot) if bdt_boo_h is not None else np.zeros_like(gray)
            hep.histplot([bdt_boo, bdt_res], bins=edges, ax=ax, stack=True,
                         histtype="step", linewidth=1.2, linestyle="--",
                         color=[COLOR_BDT_BOOSTED, COLOR_BDT_RESOLVED],
                         label=[f"BDT Boosted  ε={bdt_boo.sum():.2%}",
                                f"BDT Resolved  ε={bdt_res.sum():.2%}"])

        frac800 = all_v[edges[:-1] < 800].sum() / n_tot
        ax.text(0.97, 0.72, f"LHE < 800 GeV: {frac800:.1%}",
                transform=ax.transAxes, ha="right", va="top", fontsize=7,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7,
                          edgecolor="gray"))

        ax.axvline(800, color="black", linestyle="--", linewidth=0.8, alpha=0.6)
        ax.set_xlim(0, x_max)
        ax.set_ylim(bottom=0)
        ax.set_xlabel("LHE m(lljj) [GeV]", fontsize=9)
        ax.set_ylabel("fraction / bin", fontsize=9)
        ax.set_title(f"N{n}", fontsize=10)
        ax.legend(fontsize=7, loc="upper right")

    for ax in axes_flat[len(n_list):]:
        ax.axis("off")

    fig.suptitle(f"WR{wr} {ch}  —  LHE full shape (gray) vs SR-passing subsets (stacked)",
                 fontsize=14, y=1.01)
    plt.tight_layout()
    out = f"{OUT_DIR}/WR{wr}_{ch}_lhe_all_vs_sr_stacked.png"
    fig.savefig(out, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out}", flush=True)


def main():
    for (wr, ch), n_list in sorted(discover_points().items()):
        print(f"WR{wr} {ch}: {len(n_list)} mass points", flush=True)
        make_grid(wr, ch, n_list)


if __name__ == "__main__":
    main()
