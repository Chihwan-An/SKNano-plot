#!/home/achihwan/miniconda3/envs/hep-py-env/bin/python3
"""Generate LHE-vs-reco stacked plots for all WR mass points."""

import math, os
import numpy as np
import uproot, hist
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep

hep.style.use("CMS")

SIG_DIR   = "/gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy/2023/sig"
CACHE_DIR = "/data6/Users/achihwan/SKNanoAnalyzer-v13/plots/HNWR/singnal_sample/Offshell_test/lhe_cache"
OUT_DIR   = "/data6/Users/achihwan/SKNanoAnalyzer-v13/plots/HNWR/singnal_sample/Offshell_test"

WR_N_MAP = {
    2000: list(range(100, 2000, 200)),
    4000: list(range(100, 4000, 200)),
    6000: list(range(100, 6000, 200)),
    8000: list(range(100, 8000, 200)),
}

REBIN = 200
BINS  = np.arange(0, 8200, REBIN)

BOOSTED_CF  = "Central/Cutflow_for_Boosted_SR"
RESOLVED_CF = ["Central/Cutflow_for_Resolved_SR", "Central/Cutflow_for_reseolved_SR"]

COLOR_LHE      = "dimgray"
COLOR_BOOSTED  = "steelblue"
COLOR_RESOLVED = "tomato"

# Mass windows for diff annotation.
# Each entry: list of (max_n_or_None, mass_lo, mass_hi, shade_color, text_y)
#   max_n_or_None : only draw for N <= max_n; None = all N
DIFF_WINDOWS = {
    2000: [
        (None, 1000, 2400, "green",  0.82),
    ],
    4000: [
        (500,  800,  2000, "purple", 0.82),   # N <= 500
        (None, 2000, 4400, "green",  0.62),   # all N
    ],
    6000: [
        (1100, 800,  4000, "purple", 0.82),   # N <= 1100
        (None, 4000, 6400, "green",  0.62),   # all N
    ],
    8000: [
        (2300, 800,  5000, "purple", 0.82),   # N <= 2300
        (None, 5000, 8000, "green",  0.62),   # all N
    ],
}


def get_eff(wr, n, region):
    fpath = f"{SIG_DIR}/WR{wr}N{n}MM.root"
    try:
        with uproot.open(fpath) as f:
            if region == "boosted":
                if BOOSTED_CF not in f:
                    return np.nan
                vals  = f[BOOSTED_CF].values(flow=False)
                denom = float(vals[1])
                numer = float(vals[-2])
            else:
                cf_key = next((k for k in RESOLVED_CF if k in f), None)
                if cf_key is None:
                    return np.nan
                vals  = f[cf_key].values(flow=False)
                denom = float(vals[1])
                numer = float(vals[-1])
            return np.nan if denom <= 0 else numer / denom
    except (FileNotFoundError, OSError):
        return np.nan


def get_reco_vals(wr, n, branch):
    fpath = f"{SIG_DIR}/WR{wr}N{n}MM.root"
    try:
        with uproot.open(fpath) as f:
            if branch not in f:
                return np.zeros(len(BINS) - 1), BINS
            h = f[branch].to_hist()[:: hist.rebin(REBIN)]
            return h.values(), h.axes[0].edges
    except (FileNotFoundError, OSError):
        return np.zeros(len(BINS) - 1), BINS


def bin_mask(lo, hi):
    centers = (BINS[:-1] + BINS[1:]) / 2
    return (centers >= lo) & (centers <= hi)


# Load LHE cache
lhe_cache = {}
missing = []
for wr, n_list in WR_N_MAP.items():
    for n in n_list:
        npz_path = f"{CACHE_DIR}/WR{wr}_N{n}.npz"
        if os.path.exists(npz_path):
            lhe_cache[(wr, n)] = np.load(npz_path)["mass"]
        else:
            lhe_cache[(wr, n)] = np.array([])
            missing.append((wr, n))

if missing:
    print(f"[WARN] Missing {len(missing)} cache files: {missing[:5]}...")

for wr, n_list in WR_N_MAP.items():
    print(f"Plotting WR{wr}...", flush=True)
    n_plots = len(n_list)
    ncols   = math.ceil(math.sqrt(n_plots))
    nrows   = math.ceil(n_plots / ncols)
    x_max   = wr * 1.2

    diff_windows = DIFF_WINDOWS.get(wr, [])   # list of window configs

    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 5, nrows * 4.5), squeeze=False)
    axes_flat = axes.flatten()

    for i, n in enumerate(n_list):
        ax = axes_flat[i]

        lhe = lhe_cache[(wr, n)]
        lhe_norm = np.zeros(len(BINS) - 1)
        if len(lhe) > 0:
            lhe_vals, _ = np.histogram(lhe, bins=BINS)
            s = lhe_vals.sum()
            lhe_norm = lhe_vals / s if s > 0 else lhe_vals
            hep.histplot(lhe_norm, bins=BINS, ax=ax, histtype="fill",
                         color=COLOR_LHE, alpha=0.25, linewidth=1, edgecolor=COLOR_LHE,
                         label="LHE")
            frac_below_800 = np.count_nonzero(lhe < 800) / len(lhe)
            ax.text(0.97, 0.97, f"LHE < 800 GeV: {frac_below_800:.1%}",
                    transform=ax.transAxes, ha="right", va="top", fontsize=7,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7, edgecolor="gray"))

        b_vals, b_edges = get_reco_vals(wr, n, "Central/SR_Boosted_MM_mlljj")
        eff_b = get_eff(wr, n, "boosted")
        b_s   = b_vals.sum()
        b_scaled = (b_vals / b_s * eff_b if (b_s > 0 and not np.isnan(eff_b))
                    else np.zeros_like(b_vals, dtype=float))

        r_vals, r_edges = get_reco_vals(wr, n, "Central/SR_Resolved_MM_mlljj")
        eff_r = get_eff(wr, n, "resolved")
        r_s   = r_vals.sum()
        r_scaled = (r_vals / r_s * eff_r if (r_s > 0 and not np.isnan(eff_r))
                    else np.zeros_like(r_vals, dtype=float))

        b_lbl = f"m(lJ) Boost  ε={eff_b:.2%}"  if not np.isnan(eff_b) else "m(lJ) Boost  ε=N/A"
        r_lbl = f"m(lljj) Res  ε={eff_r:.2%}"  if not np.isnan(eff_r) else "m(lljj) Res  ε=N/A"

        hep.histplot([b_scaled, r_scaled], bins=b_edges, ax=ax, stack=True, histtype="fill",
                     color=[COLOR_BOOSTED, COLOR_RESOLVED], alpha=0.7, label=[b_lbl, r_lbl])

        ax.axvline(800, color="black", linestyle="--", linewidth=0.8, alpha=0.6)

        # ── Diff annotations (one per configured window) ──────────────────
        for max_n, mass_lo, mass_hi, color, text_y in diff_windows:
            if (max_n is None or n <= max_n) and len(lhe) > 0:
                mask          = bin_mask(mass_lo, mass_hi)
                lhe_in_range  = lhe_norm[mask].sum()
                reco_in_range = (b_scaled + r_scaled)[mask].sum()
                diff          = lhe_in_range - reco_in_range

                ax.axvspan(mass_lo, mass_hi, alpha=0.07, color=color, zorder=0)
                ax.axvline(mass_lo, color=color, linestyle=":", linewidth=0.9, alpha=0.7)
                ax.axvline(mass_hi, color=color, linestyle=":", linewidth=0.9, alpha=0.7)
                ax.text(0.97, text_y,
                        f"Δ(LHE−Reco)\n[{mass_lo}–{mass_hi}]: {diff:+.2%}",
                        transform=ax.transAxes, ha="right", va="top", fontsize=7,
                        color=color,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                                  alpha=0.7, edgecolor=color))

        ax.set_xlim(0, x_max)
        ax.set_ylim(bottom=0)
        ax.set_xlabel("Mass [GeV]", fontsize=9)
        ax.set_ylabel("a.u.", fontsize=9)
        ax.set_title(f"N{n}", fontsize=10)
        ax.legend(fontsize=7, loc="upper right")

    for ax in axes_flat[len(n_list):]:
        ax.axis("off")

    fig.suptitle(f"WR{wr} MM  —  LHE (gray, a.u.=1) vs Reco stacked (×ε)", fontsize=14, y=1.01)
    plt.tight_layout()
    out = f"{OUT_DIR}/WR{wr}_MM_lhe_vs_reco_stacked.png"
    fig.savefig(out, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {out}", flush=True)

print("Done.")
