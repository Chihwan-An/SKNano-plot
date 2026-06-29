#!/usr/bin/env python3
"""
cutflow.py — cutflow efficiency and cut-by-cut significance plots for one
(WR, N) signal mass point.

Panels:
  [0,0] Boost SR — MM
  [0,1] Boost SR — EE
  [1,0] Resolve SR — MM
  [1,1] Resolve SR — EE

Usage:
  python cutflow.py --wr 4000 --n 300 --outdir ./cutflow_output
"""

import argparse
import csv
import os
import numpy as np
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import uproot

SIG_DIR = "/gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy/2023/sig/"
BKG_DIR = "/gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy/2023/skim/"
DATA_SAMPLE_TOKENS = ("EGamma", "Muon")

BOOSTED_HIST = "Cutflow_for_Boosted_SR"
RESOLVED_HIST = "Cutflow_for_reseolved_SR"

# CMS-style integrated-luminosity stamp (top-right of each figure).
LUMI_LABEL = r"18 fb$^{-1}$ (13.6 TeV)"


def stamp_lumi(fig):
    """Add the integrated-luminosity / CME label at the top-right of a figure."""
    fig.text(0.995, 1.01, LUMI_LABEL, ha="right", va="bottom",
             fontsize=13)

BOOSTED_LABELS = [
    "All",
    "Noise filter",
    "Not resolved",
    r"Tight lep $\geq 1$, $p_T$/$\eta$/id",
    "Trigger",
    r"$\Delta\phi(\ell,\mathrm{Fatjet})<2.0$",
    "No extra tight lep",
    r"$\ell_{\mathrm{loose,SF}}$ in Jet",
    r"No $\ell_{\mathrm{loose,OF}}$ in Jet",
    r"$M_{ll}>200$ GeV",
    r"$W_R>800$ GeV",
]

RESOLVED_LABELS = [
    "All",
    "Noise filter",
    r"$N_{\ell_{\rm tight}}=2$, $p_T$/$\eta$/id",
    "Trigger",
    r"$N_{\rm jet}\geq 2$, $p_T$/$\eta$/id",
    "All object resolved",
    r"$W_R>800$ GeV, $M_{ll}>200$ GeV",
]

# From the 9-element slice lhe_pt[1:], pick these indices (skips duplicate cut bins)
RESOLVED_IDX = [0, 1, 2, 3, 4, 5, 8]

COLORS = {
    "boost_mm":   "#4C72B0",
    "boost_ee":   "#DD8452",
    "resolve_mm": "#55A868",
    "resolve_ee": "#C44E52",
}


def to_ratio(values):
    base = float(values[0])
    if base == 0:
        return np.zeros(len(values))
    return np.array(values, dtype=float) / base


def load_cutflows(wr, n, flavor):
    """Return (boost_vals, resolved_vals) or (None, None) if file missing or empty."""
    fname = os.path.join(SIG_DIR, f"WR{wr}N{n}{flavor}.root")
    if not os.path.exists(fname):
        return None, None
    return load_cutflows_from_file(fname)


def load_cutflows_from_file(fname):
    """Return raw boosted/resolved cutflow arrays from one ROOT file."""
    try:
        with uproot.open(fname) as f:
            if "Central" not in f:
                print(f"[WARN] 'Central' key not found in {fname}")
                return None, None
            central = f["Central"]
            boost_vals = central[BOOSTED_HIST].values()
            resolve_vals = central[RESOLVED_HIST].values()
            return boost_vals, resolve_vals
    except Exception as e:
        print(f"[WARN] Failed to read {fname}: {e}")
        return None, None


def is_data_sample(filename):
    return any(token in filename for token in DATA_SAMPLE_TOKENS)


def list_background_files(bkg_dir):
    if not os.path.isdir(bkg_dir):
        print(f"[WARN] Background directory not found: {bkg_dir}")
        return []
    return [
        os.path.join(bkg_dir, name)
        for name in sorted(os.listdir(bkg_dir))
        if name.endswith(".root") and not is_data_sample(name)
    ]


def load_background_cutflows(bkg_dir):
    """Sum boosted/resolved cutflows over all MC background files."""
    total_boost = None
    total_resolve = None
    used = []

    for fname in list_background_files(bkg_dir):
        boost_vals, resolve_vals = load_cutflows_from_file(fname)
        if boost_vals is None or resolve_vals is None:
            continue

        if total_boost is None:
            total_boost = np.zeros_like(boost_vals, dtype=float)
            total_resolve = np.zeros_like(resolve_vals, dtype=float)

        if len(boost_vals) != len(total_boost) or len(resolve_vals) != len(total_resolve):
            print(f"[WARN] Skip background with mismatched cutflow bins: {fname}")
            continue

        total_boost += np.asarray(boost_vals, dtype=float)
        total_resolve += np.asarray(resolve_vals, dtype=float)
        used.append(fname)

    if not used:
        print(f"[WARN] No MC background cutflows loaded from {bkg_dir}")
        return None, None, []

    print(f"[INFO] Loaded background cutflows from {len(used)} MC files")
    return total_boost, total_resolve, used


def boosted_yields(vals):
    if vals is None:
        return None
    # index 0 is 0 (empty bin), indices 1-11 are the 11 cut stages
    arr = np.asarray(vals[1:12], dtype=float)
    if len(arr) < len(BOOSTED_LABELS):
        return None
    return arr


def resolved_yields(vals):
    if vals is None:
        return None
    arr = vals[1:]  # drop leading 0-bin → 9 elements
    if len(arr) < max(RESOLVED_IDX) + 1:
        return None
    return np.asarray(arr[RESOLVED_IDX], dtype=float)


def boosted_ratio(vals):
    arr = boosted_yields(vals)
    return None if arr is None else to_ratio(arr)


def resolved_ratio(vals):
    arr = resolved_yields(vals)
    return None if arr is None else to_ratio(arr)


def asimov_z(signal, background):
    """Asimov median discovery significance for expected S and B."""
    s = np.asarray(signal, dtype=float)
    b = np.asarray(background, dtype=float)
    z = np.zeros_like(s, dtype=float)
    mask = (s > 0.0) & (b > 0.0)
    z[mask] = np.sqrt(2.0 * ((s[mask] + b[mask]) * np.log1p(s[mask] / b[mask]) - s[mask]))
    return z


def z_reduction(z_values):
    z = np.asarray(z_values, dtype=float)
    reduction = np.zeros_like(z, dtype=float)
    prev = z[:-1]
    curr = z[1:]
    mask = prev > 0.0
    reduction[1:][mask] = (prev[mask] - curr[mask]) / prev[mask]
    return reduction


def build_significance(signal_vals, background_vals, yield_func):
    signal = yield_func(signal_vals)
    background = yield_func(background_vals)
    if signal is None or background is None:
        return None
    if len(signal) != len(background):
        return None

    z_vals = asimov_z(signal, background)
    return {
        "signal": signal,
        "background": background,
        "z": z_vals,
        "z_ratio": to_ratio(z_vals),
        "z_reduction": z_reduction(z_vals),
    }


def draw_panel(ax, ratios, labels, title, color):
    if ratios is None:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        ax.set_title(title, fontsize=11, fontweight="bold")
        return

    x = np.arange(len(labels))
    bars = ax.bar(x, ratios, color=color, edgecolor="black", linewidth=0.6, alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Remaining events (A.U.)", fontsize=10)
    ax.set_ylim(0, 1.15)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_xlim(-0.6, len(labels) - 0.4)

    for bar, val in zip(bars, ratios):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{val:.1%}",
            ha="center", va="bottom", fontsize=7.5,
        )


def format_z(value):
    if value == 0:
        return "0"
    if value < 0.01:
        return f"{value:.2e}"
    if value < 10:
        return f"{value:.3f}"
    if value < 100:
        return f"{value:.1f}"
    return f"{value:.0f}"


def draw_z_panel(ax, info, labels, title, color):
    if info is None:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        ax.set_title(title, fontsize=11, fontweight="bold")
        return

    x = np.arange(len(labels))
    z_vals = info["z"]
    z_ratio = info["z_ratio"]
    bars = ax.bar(x, z_vals, color=color, edgecolor="black", linewidth=0.6, alpha=0.82)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Asimov Z", fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.set_xlim(-0.6, len(labels) - 0.4)

    positive = z_vals[z_vals > 0.0]
    if len(positive) > 0:
        ymin = float(np.min(positive))
        ymax = float(np.max(positive))
        if ymax / ymin > 30.0:
            ax.set_yscale("log")
            ax.set_ylim(max(ymin * 0.45, 1.0e-8), ymax * 3.0)
            text_factor = 1.12
        else:
            ax.set_ylim(0.0, ymax * 1.35)
            text_factor = 1.02
    else:
        ax.set_ylim(0.0, 1.0)
        text_factor = 1.02

    for bar, val in zip(bars, z_vals):
        if val <= 0.0:
            continue
        y = val * text_factor if ax.get_yscale() == "log" else val + ax.get_ylim()[1] * 0.015
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            y,
            format_z(float(val)),
            ha="center", va="bottom", fontsize=7.0,
        )

    ax_ratio = ax.twinx()
    ax_ratio.plot(
        x,
        z_ratio,
        color="black",
        marker="o",
        linewidth=1.5,
        markersize=4.0,
        label=r"$Z/Z_{\mathrm{first}}$",
    )
    ax_ratio.set_ylabel(r"$Z/Z_{\mathrm{first}}$", fontsize=10)
    ratio_max = float(np.max(z_ratio)) if len(z_ratio) else 1.0
    ax_ratio.set_ylim(0.0, max(1.15, ratio_max * 1.20))
    ax_ratio.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))


def write_z_csv(wr, n, outdir, panel_rows):
    outpath = os.path.join(outdir, f"cutflow_Z_WR{wr}N{n}.csv")
    with open(outpath, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([
            "region",
            "flavor",
            "cut_index",
            "cut",
            "signal",
            "background",
            "asimov_z",
            "z_over_first",
            "z_reduction_percent",
        ])
        for region, flavor, labels, info in panel_rows:
            if info is None:
                continue
            for idx, (label, sig, bkg, z_val, z_ratio, z_red) in enumerate(
                zip(
                    labels,
                    info["signal"],
                    info["background"],
                    info["z"],
                    info["z_ratio"],
                    info["z_reduction"],
                ),
                start=1,
            ):
                writer.writerow([
                    region,
                    flavor,
                    idx,
                    label,
                    f"{sig:.8g}",
                    f"{bkg:.8g}",
                    f"{z_val:.8g}",
                    f"{z_ratio:.8g}",
                    f"{100.0 * z_red:.8g}",
                ])
    print(f"Saved: {outpath}")


def make_significance_plot(wr, n, outdir, signal_cutflows, background_cutflows, bkg_files):
    boost_mm, resolve_mm, boost_ee, resolve_ee = signal_cutflows
    bkg_boost, bkg_resolve = background_cutflows

    panels = [
        ("Boost", "MM", BOOSTED_LABELS, build_significance(boost_mm, bkg_boost, boosted_yields), COLORS["boost_mm"]),
        ("Boost", "EE", BOOSTED_LABELS, build_significance(boost_ee, bkg_boost, boosted_yields), COLORS["boost_ee"]),
        ("Resolve", "MM", RESOLVED_LABELS, build_significance(resolve_mm, bkg_resolve, resolved_yields), COLORS["resolve_mm"]),
        ("Resolve", "EE", RESOLVED_LABELS, build_significance(resolve_ee, bkg_resolve, resolved_yields), COLORS["resolve_ee"]),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    fig.suptitle(
        f"Cutflow Asimov Z: WR{wr} N{n}",
        fontsize=16,
        fontweight="bold",
        y=1.01,
    )
    stamp_lumi(fig)

    for ax, (region, flavor, labels, info, color) in zip(axes.flat, panels):
        draw_z_panel(ax, info, labels, f"{region} SR — {flavor}  (WR{wr}, N{n})", color)

    fig.text(
        0.5,
        0.005,
        f"Background: sum of {len(bkg_files)} MC skim files, data samples excluded. "
        "SR cutflow histograms are not flavor-split, so the same B is used for EE/MM.",
        ha="center",
        va="bottom",
        fontsize=8,
    )
    plt.tight_layout(rect=[0.0, 0.025, 1.0, 1.0])
    outpath = os.path.join(outdir, f"cutflow_Z_WR{wr}N{n}.png")
    plt.savefig(outpath, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Saved: {outpath}")

    write_z_csv(
        wr,
        n,
        outdir,
        [(region, flavor, labels, info) for region, flavor, labels, info, _ in panels],
    )


def make_plot(wr, n, outdir, bkg_dir):
    boost_mm,   resolve_mm   = load_cutflows(wr, n, "MM")
    boost_ee,   resolve_ee   = load_cutflows(wr, n, "EE")

    if boost_mm is None and boost_ee is None:
        print(f"[WARN] No files found for WR{wr}N{n}. Skipping.")
        return

    os.makedirs(outdir, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    fig.suptitle(f"Cutflow Efficiency: WR{wr} N{n}", fontsize=16, fontweight="bold", y=1.01)
    stamp_lumi(fig)

    draw_panel(axes[0, 0], boosted_ratio(boost_mm),   BOOSTED_LABELS,   f"Boost SR — MM  (WR{wr}, N{n})", COLORS["boost_mm"])
    draw_panel(axes[0, 1], boosted_ratio(boost_ee),   BOOSTED_LABELS,   f"Boost SR — EE  (WR{wr}, N{n})", COLORS["boost_ee"])
    draw_panel(axes[1, 0], resolved_ratio(resolve_mm), RESOLVED_LABELS, f"Resolve SR — MM (WR{wr}, N{n})", COLORS["resolve_mm"])
    draw_panel(axes[1, 1], resolved_ratio(resolve_ee), RESOLVED_LABELS, f"Resolve SR — EE (WR{wr}, N{n})", COLORS["resolve_ee"])

    plt.tight_layout()
    outpath = os.path.join(outdir, f"cutflow_WR{wr}N{n}.png")
    plt.savefig(outpath, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Saved: {outpath}")

    bkg_boost, bkg_resolve, bkg_files = load_background_cutflows(bkg_dir)
    if bkg_boost is None or bkg_resolve is None:
        print("[WARN] Skip Z plot because no background cutflows were loaded.")
        return

    make_significance_plot(
        wr,
        n,
        outdir,
        (boost_mm, resolve_mm, boost_ee, resolve_ee),
        (bkg_boost, bkg_resolve),
        bkg_files,
    )


def main():
    parser = argparse.ArgumentParser(description="Cutflow efficiency and Z plots for one signal mass point")
    parser.add_argument("--wr",     type=int, required=True,  help="WR mass (e.g. 4000)")
    parser.add_argument("--n",      type=int, required=True,  help="N mass (e.g. 300)")
    parser.add_argument("--outdir", default="./cutflow_output", help="Output directory for PNG files")
    parser.add_argument("--bkg-dir", default=BKG_DIR, help="Directory with background skim ROOT files")
    args = parser.parse_args()

    make_plot(args.wr, args.n, args.outdir, args.bkg_dir)


if __name__ == "__main__":
    main()
