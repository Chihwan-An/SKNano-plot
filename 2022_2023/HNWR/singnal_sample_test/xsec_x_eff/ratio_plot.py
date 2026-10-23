#!/usr/bin/env python3
"""
ratio_plot.py — BDT / cut-based acceptance 비율을 m_N 함수로 그린다.

x축 = m_N, y축 = A(BDT, score>cut) / A(cut-based), 선 4개 = m_WR (2000/4000/6000/8000).
채널(EE, MM)마다 그림 하나씩.

입력은 cutbased_grid.py / bdt_grid.py 가 만든 CSV다. 두 CSV에 모두 있는
mass point만 쓴다 (BDT는 홀수-백 m_N 100점만 학습돼 있다).

Usage:
  python ratio_plot.py                                  # output/*/ 기본 CSV 사용
  python ratio_plot.py --region all                     # total/boost/resolve 3패널
  python ratio_plot.py --cutbased-csv … --bdt-csv … --outdir …
"""

import argparse
import csv
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import grid_common as gc

DEFAULT_CUTBASED_CSV = "output/cutbased/cutbased_grid.csv"
DEFAULT_BDT_CSV = "output/bdt/bdt_grid.csv"

REGIONS = {
    "total":   ("acc_total",   "Total"),
    "boost":   ("acc_boost",   "Boosted"),
    "resolve": ("acc_resolve", "Resolved"),
}

# m_WR 별 선 색/마커
STYLE = {
    2000: ("#4C72B0", "o"),
    4000: ("#DD8452", "s"),
    6000: ("#55A868", "^"),
    8000: ("#C44E52", "D"),
}


def load(path):
    """{(channel, mWR, mN): row}"""
    with open(path) as f:
        return {(r["channel"], int(r["mWR"]), int(r["mN"])): r
                for r in csv.DictReader(f)}


def draw_panel(ax, cut, bdt, channel, column, title):
    keys = sorted(set(cut) & set(bdt))
    wr_values = sorted({k[1] for k in keys if k[0] == channel})

    n_used = 0
    for mWR in wr_values:
        pts = []
        for k in keys:
            if k[0] != channel or k[1] != mWR:
                continue
            a_cut = float(cut[k][column])
            a_bdt = float(bdt[k][column])
            if not np.isfinite(a_cut) or a_cut <= 0 or not np.isfinite(a_bdt):
                continue
            pts.append((k[2], a_bdt / a_cut))
        if not pts:
            continue
        pts.sort()
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        n_used += len(pts)
        color, marker = STYLE.get(mWR, ("black", "o"))
        ax.plot(xs, ys, marker=marker, markersize=5, linewidth=1.6,
                color=color, label=rf"$m_{{W_R}}$ = {mWR} GeV")

    ax.axhline(1.0, color="grey", linestyle="--", linewidth=1.0, zorder=0)
    ax.set_xlabel(r"$m_{N}$ [GeV]", fontsize=12)
    ax.set_ylabel(r"$A_{\mathrm{BDT}}\,/\,A_{\mathrm{cut\text{-}based}}$", fontsize=12)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend(fontsize=10, framealpha=0.9)
    return n_used


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cutbased-csv", default=DEFAULT_CUTBASED_CSV)
    ap.add_argument("--bdt-csv", default=DEFAULT_BDT_CSV)
    ap.add_argument("--outdir", default="output/ratio")
    ap.add_argument("--region", default="total",
                    choices=["total", "boost", "resolve", "all"])
    ap.add_argument("--logy", action="store_true")
    args = ap.parse_args()

    cut = load(args.cutbased_csv)
    bdt = load(args.bdt_csv)
    os.makedirs(args.outdir, exist_ok=True)

    regions = list(REGIONS) if args.region == "all" else [args.region]

    for channel in gc.CHANNELS:
        fig, axes = plt.subplots(1, len(regions), figsize=(7.5 * len(regions), 6),
                                 squeeze=False)
        total = 0
        for ax, region in zip(axes[0], regions):
            column, label = REGIONS[region]
            total += draw_panel(ax, cut, bdt, channel, column,
                                f"{label} acceptance ratio — {channel}")
            if args.logy:
                ax.set_yscale("log")
        gc.stamp_lumi(fig)
        fig.tight_layout()
        suffix = "all" if args.region == "all" else args.region
        path = os.path.join(args.outdir, f"ratio_acceptance_{suffix}_{channel}.png")
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"[OK] {path}  ({total} points)")


if __name__ == "__main__":
    main()
