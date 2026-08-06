#!/usr/bin/env python3
"""First-failing-cut breakdown for low-mass (LHE sumall <= 2000) events that end
up in NEITHER the resolved nor the boosted SR, from WRGenRecoMass output.

Six figure types per (WR, channel) grid — bin meanings differ, see labels:
  cutbased / BDT                   : resolved-chain first-fail cutflow
  cutbased_boosted / BDT_boosted   : boosted-chain first-fail cutflow
  cutbased_ntight / BDT_ntight     : N(tight)!=2 sub-breakdown (0/1 tight,
                                     leading vs subleading candidate passing)

Every bar is normalized to N(LHE mass <= 2000) of the sample, so
  sum(bars) + captured(resolved) + captured(boosted) ~= 1
per panel (captured fractions are printed in the panel corner).

Run after rebuilding the analyzer and re-running WRGenRecoMass — outputs
produced before the fail-cutflow existed are skipped with a message.
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

LHE_CUT = 2000.0  # matches the analyzer-side gate on the 1D cutflows

# Fail-bin labels, index == histogram bin (0-based). Keep in sync with the
# comment blocks in WRGenRecoMass.cc (FillResolvedFailCutflow / BDT twin).
CUTBASED_LABELS = [
    "MET noise filter",
    "Jet veto map",
    r"N(tight lep) $\neq$ 2",
    r"Lead lep $p_T$ (130 e / 60 $\mu$)",
    r"Sublead lep $p_T$ < 53",
    r"e-$\mu$ mixed pair",
    "Trigger",
    "< 2 jet cand. (any $p_T$)",
    r"Jet $p_T$ < 40",
    r"$\Delta R$(j1, lep) < 0.4",
    r"$\Delta R$(j2, lep) < 0.4",
    r"$\Delta R$(l1, l2) < 0.4",
    r"$\Delta R$(j1, j2) < 0.4",
    r"$m_{ll}$ < 400",
    r"$m_{lljj}$ < 800",
    "passed all (sanity)",
]
BDT_LABELS = [
    "No HLT fired",
    "MET noise filter",
    "N(tight lep) = 0",
    "Jet veto map",
    r"N(tight lep) $\neq$ 2",
    r"e-$\mu$ mixed pair",
    r"Lead lep $p_T$ < 60",
    r"Sublead lep $p_T$ < 53",
    r"Lead trig / safe $p_T$ (118 e / 52 $\mu$)",
    r"$m_{ll}$ < 200",
    "< 2 jet cand. (any $p_T$)",
    r"Jet $p_T$ < 40",
    r"$\Delta R$(j1, lep) < 0.4",
    r"$\Delta R$(j2, lep) < 0.4",
    r"$\Delta R$(l1, l2) < 0.4",
    r"$\Delta R$(j1, j2) < 0.4",
    "passed all (sanity)",
]

CUTBASED_BOOSTED_LABELS = [
    "resolved-like (boosted skipped)",
    "No tight lepton",
    r"Lead lep $p_T$ (130 e / 60 $\mu$)",
    "Trigger",
    r"low-$m_{ll}$ SF pair (60-150, DY CR)",
    r"No AK8 ($p_T$/$\eta$/ID/SDM)",
    "No LSF3 > 0.75 fatjet",
    r"No away fatjet ($|\Delta\phi|$ > 2)",
    "Extra tight lepton",
    "No SF loose lep in fatjet",
    "OF loose lep in fatjet",
    r"$m_{ll}$(lead, SF loose) < 200",
    r"$m$(lep + fatjet) < 800",
    "passed all (sanity)",
]
BDT_BOOSTED_LABELS = [
    r"Lead lep $p_T$ < 60",
    "No extra loose lepton",
    r"Lead trig / safe $p_T$",
    r"No SF loose pair $m_{ll}$ > 200",
    "resolved-like topology (veto)",
    "No AK8 fatjet",
    "passed all (sanity)",
]
NTIGHT_LABELS = [
    "0 tight, < 2 candidates",
    r"0 tight, $\geq$ 2 candidates",
    "1 tight, no 2nd candidate",
    "1 tight = leading cand.",
    "1 tight = subleading cand.",
    r"$\geq$ 3 tight",
]

CONFIGS = {
    "cutbased": {
        "subdir":   "resolved",
        "hist":     "Central/ResolvedFail_lowLHE_cutflow_noweight",
        "labels":   CUTBASED_LABELS,
        "sr_res":   "Central/SR_Resolved_{ch}_lhe_mass_noweight",
        "sr_boo":   "Central/SR_Boosted_{ch}_lhe_mass_noweight",
        "color":    "tomato",
        "title":    "cut-based resolved chain",
    },
    "BDT": {
        "subdir":   "resolved",
        "hist":     "Central/BDTResolvedFail_lowLHE_cutflow_noweight",
        "labels":   BDT_LABELS,
        "sr_res":   "Central/BDTSR_Resolved_{ch}_lhe_mass_noweight",
        "sr_boo":   "Central/BDTSR_Boosted_{ch}_lhe_mass_noweight",
        "color":    "darkred",
        "title":    "BDT resolved chain",
    },
    "cutbased_boosted": {
        "subdir":   "boosted",
        "hist":     "Central/BoostedFail_lowLHE_cutflow_noweight",
        "labels":   CUTBASED_BOOSTED_LABELS,
        "sr_res":   "Central/SR_Resolved_{ch}_lhe_mass_noweight",
        "sr_boo":   "Central/SR_Boosted_{ch}_lhe_mass_noweight",
        "color":    "steelblue",
        "title":    "cut-based boosted chain",
    },
    "BDT_boosted": {
        "subdir":   "boosted",
        "hist":     "Central/BDTBoostedFail_lowLHE_cutflow_noweight",
        "labels":   BDT_BOOSTED_LABELS,
        "sr_res":   "Central/BDTSR_Resolved_{ch}_lhe_mass_noweight",
        "sr_boo":   "Central/BDTSR_Boosted_{ch}_lhe_mass_noweight",
        "color":    "navy",
        "title":    "BDT boosted chain",
    },
    "cutbased_ntight": {
        "subdir":   "ntight_breakdown",
        "hist":     "Central/ResolvedFail_lowLHE_ntight_breakdown_noweight",
        "labels":   NTIGHT_LABELS,
        "sr_res":   "Central/SR_Resolved_{ch}_lhe_mass_noweight",
        "sr_boo":   "Central/SR_Boosted_{ch}_lhe_mass_noweight",
        "color":    "dimgray",
        "title":    r"cut-based N(tight)$\neq$2 breakdown",
    },
    "BDT_ntight": {
        "subdir":   "ntight_breakdown",
        "hist":     "Central/BDTResolvedFail_lowLHE_ntight_breakdown_noweight",
        "labels":   NTIGHT_LABELS,
        "sr_res":   "Central/BDTSR_Resolved_{ch}_lhe_mass_noweight",
        "sr_boo":   "Central/BDTSR_Boosted_{ch}_lhe_mass_noweight",
        "color":    "dimgray",
        "title":    r"BDT N(tight)$\neq$2 breakdown",
    },
}


def integral_below(f, name, cut):
    """Integral of a 1 GeV-binned histogram below `cut`; None if absent."""
    if name not in f:
        return None
    vals  = f[name].values(flow=False)
    edges = f[name].axis().edges()
    return float(vals[edges[:-1] < cut].sum())


def discover_points():
    points = {}
    for path in glob.glob(f"{IN_DIR}/WR*N*.root"):
        m = re.match(r"WR(\d+)N(\d+)(EE|MM)\.root", os.path.basename(path))
        if not m:
            continue
        wr, n, ch = int(m.group(1)), int(m.group(2)), m.group(3)
        # same skip as generate_plots.py: undecayed-N LHE productions
        if n == 200 or 2 * n == wr:
            continue
        points.setdefault((wr, ch), []).append(n)
    return {k: sorted(v) for k, v in points.items()}


def draw_panel(ax, fracs, labels, color, header, footer):
    y = np.arange(len(labels))
    ax.barh(y, fracs, height=0.62, color=color)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=11)
    ax.invert_yaxis()  # bin 0 on top, chain order downwards
    ax.tick_params(axis="x", labelsize=11)
    ax.set_xlabel(r"fraction of $m_{LHE} \leq 2000$ events", fontsize=12)
    xmax = max(fracs.max() * 1.25, 1e-3)
    ax.set_xlim(0., xmax)
    # direct labels only where a bar is visible; text in ink, not series color
    for yi, v in zip(y, fracs):
        if v <= 0:
            continue
        ax.text(v + 0.01 * xmax, yi, f"{v:.1%}", va="center", fontsize=10, color="#333333")
    ax.set_title(header, fontsize=13, loc="left")
    ax.text(0.98, 0.02, footer, transform=ax.transAxes, ha="right", va="bottom",
            fontsize=10, color="#555555")
    ax.grid(axis="x", alpha=0.3, linewidth=0.6)
    ax.set_axisbelow(True)


def make_grid(wr, ch, n_list, cfg_key):
    cfg = CONFIGS[cfg_key]
    ncols = math.ceil(math.sqrt(len(n_list)))
    nrows = math.ceil(len(n_list) / ncols)
    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(ncols * 7.5, nrows * 0.42 * len(cfg["labels"]) + 2),
                             squeeze=False)
    axes_flat = axes.flatten()
    drew_any = False

    for i, n in enumerate(n_list):
        ax = axes_flat[i]
        with uproot.open(f"{IN_DIR}/WR{wr}N{n}{ch}.root") as f:
            if cfg["hist"] not in f:
                print(f"  [skip] WR{wr}N{n}{ch}: {cfg['hist']} not in file "
                      "(output predates the fail-cutflow — rerun the analyzer)")
                ax.axis("off")
                continue
            fails = f[cfg["hist"]].values(flow=False)
            n_tot = integral_below(f, "LHE_mass_sumall_all_noweight", LHE_CUT)
            n_res = integral_below(f, cfg["sr_res"].format(ch=ch), LHE_CUT) or 0.
            n_boo = integral_below(f, cfg["sr_boo"].format(ch=ch), LHE_CUT) or 0.
        if not n_tot:
            ax.axis("off")
            continue
        drew_any = True
        fracs = fails / n_tot
        footer = (f"N(LHE$\\leq$2000) = {n_tot:.0f}   "
                  f"resolved {n_res / n_tot:.1%}   boosted {n_boo / n_tot:.1%}   "
                  f"failed {fails.sum() / n_tot:.1%}")
        draw_panel(ax, fracs, cfg["labels"], cfg["color"],
                   f"WR{wr} N{n} {ch}  ({cfg['title']})", footer)

    for j in range(len(n_list), len(axes_flat)):
        axes_flat[j].axis("off")
    if not drew_any:
        plt.close(fig)
        return None

    fig.tight_layout()
    outdir = f"{OUT_DIR}/{cfg['subdir']}"
    os.makedirs(outdir, exist_ok=True)
    out = f"{outdir}/WR{wr}_{ch}_{cfg_key}_failcutflow.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def main():
    points = discover_points()
    if not points:
        print(f"no WR*N*.root files found in {IN_DIR}")
        return
    made = 0
    for (wr, ch), n_list in sorted(points.items()):
        for cfg_key in CONFIGS:
            out = make_grid(wr, ch, n_list, cfg_key)
            if out:
                print(f"wrote {out}")
                made += 1
    if made == 0:
        print("nothing plotted — the fail-cutflow histograms are not in any output yet.")


if __name__ == "__main__":
    main()
