#!/usr/bin/env python3
"""
cutflow_tb_vs_light.py — signal-efficiency cutflow split into WR*->tb vs
WR*->light-quark decays, overlaid on one plot.

Reproduce20_002_copy.cc fills, per SR cut step, dedicated cutflow histograms
that are split by the LHE decay-mode tag (SetSignalFlags / FillSignalCutflow):

    Central/Cutflow_for_reseolved_SR_tb      resolved, tb events   (|PDG| 5/6 in LHE)
    Central/Cutflow_for_reseolved_SR_light   resolved, light-quark events
    Central/Cutflow_for_reseolved_SR_signal  resolved, all signal (denominator)
    Central/Cutflow_for_Boosted_SR_{tb,light,signal}   boosted counterparts

bin 1 of each histogram = all events entering (right after the MC weight); the
last used bin = events passing the SR. This script normalizes each curve to its
own bin 1 (efficiency = remaining fraction) and overlays tb vs light so you can
see, from the very first step, how the two decay modes survive the selection
differently.

  * "_light"/"_signal" require Reproduce20_002_copy to have been re-run after the
    FillSignalCutflow edit that adds those fills. If they are missing the script
    warns and falls back to "_signal - _tb" for light where possible.

Usage:
  python cutflow_tb_vs_light.py                         # every WR*N* file in SIG_DIR
  python cutflow_tb_vs_light.py --wr 4000 --n 2500      # one mass point
  python cutflow_tb_vs_light.py --flavor EE --outdir ./tb_light_out
  python cutflow_tb_vs_light.py --sig-dir /gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy/2023BPix
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

# Default location of the Reproduce20_002_copy signal outputs (era 2023BPix).
SIG_DIR = "/gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy/2023BPix"

# Cutflow histogram base names (the "_tb"/"_light"/"_signal" suffix is appended).
RESOLVED_BASE = "Cutflow_for_reseolved_SR"
BOOSTED_BASE = "Cutflow_for_Boosted_SR"

# Bin meaning (1-indexed as filled in Reproduce20_002_copy.cc). We keep the cut
# steps and drop the two unconditional pass-through markers (resolved bins 7,8).
RESOLVED_BINS = [1, 2, 3, 4, 5, 6, 9]
RESOLVED_LABELS = [
    "All",
    "Noise filter",
    r"$N_{\ell_{\rm tight}}=2$",
    "Trigger",
    r"$N_{\rm jet}\geq 2$",
    "All obj. resolved",
    r"$M_{ll}>400,\ W_R>800$",
]

BOOSTED_BINS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
BOOSTED_LABELS = [
    "All",
    "Noise filter",
    "Enter boosted",
    r"$\ell+$Fatjet chan.",
    "Sel. stage",
    "Fatjet/Ncand",
    r"$W_R$ cand.",
    "No extra tight lep",
    r"$\ell_{\rm loose,SF}$ in Jet",
    r"No $\ell_{\rm loose,OF}$",
    r"$M_{ll}>200$",
    r"$W_R>800$",
]

COLOR_TB = "#C44E52"      # red
COLOR_LIGHT = "#4C72B0"   # blue


def _read_hist(central, name):
    """Return the histogram values array or None if absent."""
    if name not in central:
        return None
    return np.asarray(central[name].values(), dtype=float)


def load_split_cutflows(fname):
    """Return dict of {(topo, mode): values} for topo in resolved/boosted,
    mode in tb/light/signal. Missing histograms are omitted."""
    out = {}
    with uproot.open(fname) as f:
        if "Central" not in f:
            print(f"[WARN] 'Central' not found in {fname}")
            return out
        central = f["Central"]
        for topo, base in (("resolved", RESOLVED_BASE), ("boosted", BOOSTED_BASE)):
            for mode in ("tb", "light", "signal"):
                vals = _read_hist(central, f"{base}_{mode}")
                if vals is not None:
                    out[(topo, mode)] = vals
    return out


def pick_bins(vals, bins):
    """Select cut steps from a ROOT values array.

    FillHist(..., binN, ...) puts the value binN into ROOT bin index binN (bins
    are [0,1),[1,2),... so index 0 is always empty). So cut step binN == values
    index binN -- no -1 offset.
    """
    arr = np.asarray(vals, dtype=float)
    idx = [b for b in bins if b < len(arr)]
    return arr[idx]


def efficiency(vals, bins):
    """Remaining-fraction curve, normalized to the first selected bin."""
    y = pick_bins(vals, bins)
    if y.size == 0 or y[0] == 0:
        return None, y
    return y / y[0], y


def get_mode(cuts, topo, mode):
    """Return the values array for (topo, mode).

    A masspoint with zero tb events never creates the '_tb' histogram; light is
    then the whole signal. Synthesize light = signal - tb when '_light' is absent.
    """
    if (topo, mode) in cuts:
        return cuts[(topo, mode)]
    sig = cuts.get((topo, "signal"))
    tb = cuts.get((topo, "tb"))
    if mode == "light" and sig is not None:
        return sig - (tb if tb is not None else 0.0)
    # mode == "tb" but no _tb histogram -> genuinely zero tb events -> no curve
    return None


def draw_panel(ax, cuts, topo, bins, labels, title):
    x = np.arange(len(bins))
    plotted = False
    for mode, color, lbl in (("tb", COLOR_TB, r"WR$\to$tb"),
                             ("light", COLOR_LIGHT, r"WR$\to$light q")):
        vals = get_mode(cuts, topo, mode)
        if vals is None:
            continue
        eff, raw = efficiency(vals, bins)
        if eff is None:
            continue
        n0 = raw[0]
        nlast = raw[-1]
        ax.plot(x, eff, "-o", color=color, lw=1.8, ms=5,
                label=f"{lbl}  (N={n0:.0f}, SR={nlast:.1f}, "
                      f"eff={nlast / n0 * 100:.1f}%)")
        plotted = True

    ax.set_xticks(x)
    ax.set_xticklabels(labels[:len(bins)], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Efficiency (fraction remaining)", fontsize=10)
    ax.set_ylim(0, 1.15)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_xlim(-0.5, len(bins) - 0.5)
    if plotted:
        ax.legend(fontsize=8, loc="upper right")
    else:
        ax.text(0.5, 0.5, "no tb/light histograms\n(re-run Reproduce20_002_copy)",
                ha="center", va="center", transform=ax.transAxes, fontsize=9)


def make_figure(fname, outdir):
    cuts = load_split_cutflows(fname)
    if not cuts:
        print(f"[SKIP] {fname}: no split cutflow histograms")
        return
    base = os.path.basename(fname).replace(".root", "")
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    draw_panel(axes[0], cuts, "resolved", RESOLVED_BINS, RESOLVED_LABELS,
               f"Resolved SR — {base}")
    draw_panel(axes[1], cuts, "boosted", BOOSTED_BINS, BOOSTED_LABELS,
               f"Boosted SR — {base}")
    fig.suptitle("Signal-efficiency cutflow: WR$\\to$tb vs WR$\\to$light quark",
                 fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, f"cutflow_tb_vs_light_{base}.png")
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    print(f"[OK] wrote {outpath}")


def list_signal_files(sig_dir, wr, n, flavor):
    pat = re.compile(r"^WR(\d+)N(\d+)(EE|MM)\.root$")
    files = []
    for name in sorted(os.listdir(sig_dir)):
        m = pat.match(name)
        if not m:
            continue
        fwr, fn, fflav = int(m.group(1)), int(m.group(2)), m.group(3)
        if wr is not None and fwr != wr:
            continue
        if n is not None and fn != n:
            continue
        if flavor is not None and fflav != flavor:
            continue
        files.append(os.path.join(sig_dir, name))
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sig-dir", default=SIG_DIR)
    ap.add_argument("--wr", type=int, default=None)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--flavor", choices=["EE", "MM"], default=None)
    ap.add_argument("--outdir",
                    default="/data9/Users/achihwan/AN/For_claude/12_is_there_top/tb_vs_light_out")
    args = ap.parse_args()

    files = list_signal_files(args.sig_dir, args.wr, args.n, args.flavor)
    if not files:
        print(f"[ERROR] no signal files matched under {args.sig_dir}")
        return
    print(f"[INFO] {len(files)} signal file(s) to plot")
    for fname in files:
        make_figure(fname, args.outdir)


if __name__ == "__main__":
    main()
