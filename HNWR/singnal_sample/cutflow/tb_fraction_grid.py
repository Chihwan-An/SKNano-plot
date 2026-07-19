#!/usr/bin/env python3
"""
tb_fraction_grid.py — tb (WR*->tb) fraction across the (mWR, mN) mass grid, at
two selection stages, from the Reproduce20_002_copy split cutflows.

For every signal file it reads the decay-mode-split SR cutflow histograms filled
by Reproduce20_002_copy.cc (SetSignalFlags / FillSignalCutflow):

    Central/Cutflow_for_reseolved_SR_tb      Central/Cutflow_for_reseolved_SR_signal
    Central/Cutflow_for_Boosted_SR_tb        Central/Cutflow_for_Boosted_SR_signal

and computes the tb fraction  f_tb = N(tb) / N(signal)  at:

  * PLOT 1 "initial" : cutflow bin 1 (all events, before any selection) -> the
    generator-level fraction of WR*->qq signal that decays via tb.
  * PLOT 2 "SR"      : the last SR bin (resolved bin 9 / boosted bin 12) -> the
    tb fraction among events that survive the full SR selection.

Both are drawn as a scatter over the mass grid (x = mWR, y = mN), colored by the
tb fraction, with the value annotated at each point.

Requires Reproduce20_002_copy to have been re-run after the "_signal"/"_light"
FillSignalCutflow additions (older outputs only have "_tb").

Usage:
  python tb_fraction_grid.py                              # every WR*N*EE + MM file
  python tb_fraction_grid.py --category resolved --channel EE
  python tb_fraction_grid.py --sig-dir /gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy/2023BPix
"""

import argparse
import os
import re

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import numpy as np
import uproot
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SIG_DIR = "/gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy/2023BPix"

# (base histogram name, 1-indexed SR bin) per category.
CATEGORY = {
    "resolved": ("Cutflow_for_reseolved_SR", 9),
    "boosted":  ("Cutflow_for_Boosted_SR", 12),
}
MP_RE = re.compile(r"^WR(\d+)N(\d+)(EE|MM)\.root$")


def read_fractions(fname, base, sr_bin):
    """Return (f_tb_initial, f_tb_SR, n_sig_initial, n_sig_SR) or None.

    FillHist(this_syst+base+suf, binN, ...) puts the value binN into ROOT bin
    index binN (bins are [0,1),[1,2),... so index 0 is always empty). Hence the
    "all events" step (binN=1) lives at values index 1, and the SR step
    (resolved binN=9 / boosted binN=12) at values index sr_bin.

    A signal masspoint with zero tb events never creates the "_tb" histogram; we
    treat that as tb=0 (fraction 0), NOT as missing data.
    """
    with uproot.open(fname) as f:
        if "Central" not in f:
            return None
        central = f["Central"]
        sig_name = f"{base}_signal"
        if sig_name not in central:
            return None
        sig = np.asarray(central[sig_name].values(), dtype=float)
        tb_name = f"{base}_tb"
        if tb_name in central:
            tb = np.asarray(central[tb_name].values(), dtype=float)
        else:
            tb = np.zeros_like(sig)  # masspoint with no tb decays
    i0, iSR = 1, sr_bin  # binN=1 -> index 1 (initial); binN=sr_bin -> index sr_bin
    if len(sig) <= iSR or len(tb) <= iSR:
        return None
    f_init = tb[i0] / sig[i0] if sig[i0] > 0 else np.nan
    f_sr = tb[iSR] / sig[iSR] if sig[iSR] > 0 else np.nan
    return f_init, f_sr, sig[i0], sig[iSR]


def collect(sig_dir, category, channel):
    """Return list of dicts with mWR, mN and the two fractions."""
    base, sr_bin = CATEGORY[category]
    rows = []
    for name in sorted(os.listdir(sig_dir)):
        m = MP_RE.match(name)
        if not m:
            continue
        mWR, mN, flav = int(m.group(1)), int(m.group(2)), m.group(3)
        if flav != channel:
            continue
        res = read_fractions(os.path.join(sig_dir, name), base, sr_bin)
        if res is None:
            print(f"  ! {name}: missing _signal histogram (re-run Reproduce20_002_copy)")
            continue
        f_init, f_sr, n_init, n_sr = res
        rows.append(dict(mWR=mWR, mN=mN, f_init=f_init, f_sr=f_sr,
                         n_init=n_init, n_sr=n_sr))
    return rows


def draw_grid(ax, rows, key, title, annotate_n=None):
    if not rows:
        ax.text(0.5, 0.5, "no data", ha="center", va="center",
                transform=ax.transAxes)
        ax.set_title(title, fontsize=11, fontweight="bold")
        return
    x = np.array([r["mWR"] for r in rows], dtype=float)
    y = np.array([r["mN"] for r in rows], dtype=float)
    c = np.array([r[key] for r in rows], dtype=float)
    good = np.isfinite(c)
    sc = ax.scatter(x[good], y[good], c=c[good], s=260, cmap="viridis",
                    vmin=0.0, vmax=1.0, edgecolors="black", linewidths=0.5)
    for r in rows:
        if not np.isfinite(r[key]):
            continue
        label = f"{r[key]*100:.0f}%"
        if annotate_n is not None:
            label += f"\n({r[annotate_n]:.0f})"
        ax.annotate(label, (r["mWR"], r["mN"]), fontsize=6.5,
                    ha="center", va="center", color="white")
    ax.set_xlabel(r"$m_{W_R}$ [GeV]", fontsize=11)
    ax.set_ylabel(r"$m_{N}$ [GeV]", fontsize=11)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.3)
    cb = plt.colorbar(sc, ax=ax)
    cb.set_label(r"$f_{tb}=N_{tb}/N_{\rm signal}$", fontsize=10)


def make_figure(rows, category, channel, outdir):
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    draw_grid(axes[0], rows, "f_init",
              f"Initial tb fraction (bin 1, before selection)\n{category}/{channel}",
              annotate_n="n_init")
    draw_grid(axes[1], rows, "f_sr",
              f"SR tb fraction (after full selection)\n{category}/{channel}",
              annotate_n="n_sr")
    fig.suptitle(r"WR$\to$tb fraction over the mass grid — "
                 f"{category}/{channel}", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, f"tb_fraction_grid_{category}_{channel}.png")
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    print(f"[OK] wrote {outpath}  ({len(rows)} mass points)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sig-dir", default=SIG_DIR)
    ap.add_argument("--category", nargs="+", default=["resolved", "boosted"],
                    choices=["resolved", "boosted"])
    ap.add_argument("--channel", nargs="+", default=["EE", "MM"],
                    choices=["EE", "MM"])
    ap.add_argument("--outdir",
                    default="/data9/Users/achihwan/AN/For_claude/12_is_there_top/tb_fraction_grid_out")
    args = ap.parse_args()

    for category in args.category:
        for channel in args.channel:
            rows = collect(args.sig_dir, category, channel)
            if not rows:
                print(f"[SKIP] {category}/{channel}: no usable signal files")
                continue
            make_figure(rows, category, channel, args.outdir)


if __name__ == "__main__":
    main()
