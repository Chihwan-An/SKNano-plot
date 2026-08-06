#!/usr/bin/env python3
"""Where the 3 SRs (resolved / boosted / boosted_nolep) sit per signal mass point.

Input: presel_3SR ntuples (/u/user/snu202527803/SKNanoOutput/presel_3SR/NoSyst/2022).
Unlike the WRGenRecoMass reference plots (LHE m(lljj) axis), presel_3SR trees carry
no LHE information, so each SR is drawn in its own reco W_R-mass estimator:
  resolved      -> mlljj      (l1 + l2 + j1 + j2)
  boosted       -> ml1fatjet  (lead lepton + leading fatjet)
  boosted_nolep -> ml1fatjet
The three categories are mutually exclusive by construction (boosted requires
!isResolvedCandidate; with-lep vs no-lep split on captured-sublead presence), so
stacking them is a true partition of selected events.

Normalization: raw entries / nmc (total generated, from CommonSampleInfo.json),
matching the reference plots' unweighted-fraction convention. Note the analyzer ran
on Skim_20002 skims; SR entries are unaffected (SR events pass the skim), only the
implicit "LHE all" shape is unavailable.

Outputs (per channel):
  {ch}_3SR_mass_distribution.png  -- grid of stacked reco-mass shapes per mass point
  {ch}_3SR_efficiency_summary.png -- epsilon per SR vs mass point
"""

import glob
import json
import os
import re

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep
import ROOT

hep.style.use("CMS")
ROOT.gROOT.SetBatch(True)

IN_DIR = "/u/user/snu202527803/SKNanoOutput/presel_3SR/NoSyst/2022"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_INFO = ("/u/user/snu202527803/SKNanoAnalyzer/data/Run3_v12_Run2_v9/2022/"
               "Sample/CommonSampleInfo.json")

NBINS = 24
XMAX_FACTOR = 1.2

CATEGORIES = [
    # (tree suffix, mass branch, label, color)
    ("resolved",      "mlljj",     "Resolved SR",       "tomato"),
    ("boosted",       "ml1fatjet", "Boosted SR (lep)",  "steelblue"),
    ("boosted_nolep", "ml1fatjet", "Boosted SR (no lep)", "seagreen"),
]


def discover_points():
    points = {}  # ch -> sorted [(wr, n), ...]
    for path in glob.glob(f"{IN_DIR}/Skim_20002_WR*N*.root"):
        m = re.match(r"Skim_20002_WR(\d+)N(\d+)(EE|MM)\.root", os.path.basename(path))
        if not m:
            continue
        wr, n, ch = int(m.group(1)), int(m.group(2)), m.group(3)
        points.setdefault(ch, []).append((wr, n))
    return {ch: sorted(v) for ch, v in points.items()}


def load_sample(wr, n, ch):
    """Return {suffix: masses ndarray}, n_skim (raw events processed)."""
    path = f"{IN_DIR}/Skim_20002_WR{wr}N{n}{ch}.root"
    f = ROOT.TFile.Open(path)
    d = f.Get("Central")
    out, n_skim = {}, None
    raw_cf = d.Get("Cutflow_BDT_Boosted_raw")
    if raw_cf:
        n_skim = raw_cf.GetBinContent(1)
    for key in d.GetListOfKeys():
        name = key.GetName()  # literal name e.g. "Central/SR_EE_BDTTree_boosted_nolep"
        m = re.match(rf"Central/SR_{ch}_BDTTree_(\w+)$", name)
        if not m or m.group(1) not in {c[0] for c in CATEGORIES}:
            continue
        suffix = m.group(1)
        branch = next(c[1] for c in CATEGORIES if c[0] == suffix)
        tree = key.ReadObj()
        if tree.GetEntries() == 0:
            out[suffix] = np.array([])
            continue
        arr = ROOT.RDataFrame(tree).AsNumpy([branch])[branch]
        out[suffix] = np.asarray(arr, dtype=float)
    f.Close()
    return out, n_skim


def main():
    with open(SAMPLE_INFO) as fh:
        sample_info = json.load(fh)

    points = discover_points()
    for ch, mass_points in points.items():
        ncols = 3
        nrows = int(np.ceil(len(mass_points) / ncols))
        fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 5.2, nrows * 4.6),
                                 squeeze=False)
        axes_flat = axes.flatten()

        summary = []  # (label, {suffix: eff})
        for i, (wr, n) in enumerate(mass_points):
            ax = axes_flat[i]
            info = sample_info.get(f"WR{wr}N{n}{ch}")
            masses, n_skim = load_sample(wr, n, ch)
            if info is None or not masses:
                ax.axis("off")
                continue
            n_gen = info["nmc"]

            edges = np.linspace(0., wr * XMAX_FACTOR, NBINS + 1)
            bottom = np.zeros(NBINS)
            effs = {}
            for suffix, branch, label, color in CATEGORIES:
                vals = masses.get(suffix, np.array([]))
                n_sel = len(vals)
                effs[suffix] = n_sel / n_gen
                vals = vals[vals > 0]  # drop fMissing (-999)
                hist, _ = np.histogram(vals, bins=edges)
                frac = hist / n_gen
                ax.stairs(bottom + frac, edges, baseline=bottom, fill=True,
                          color=color, alpha=0.85,
                          label=f"{label}  $\\epsilon$={100*effs[suffix]:.2f}%")
                bottom += frac
            summary.append((f"WR{wr}\nN{n}", effs))

            ax.axvline(wr, color="gray", ls="--", lw=1)
            ax.set_title(f"WR{wr} N{n}", fontsize=14)
            ax.set_xlabel("reco $m_{W_R}$ estimate [GeV]", fontsize=11)
            ax.set_ylabel("fraction / bin", fontsize=11)
            ax.tick_params(labelsize=11)
            ax.legend(fontsize=8.5, loc="upper left")
            skim_note = (f"skim: {100*n_skim/n_gen:.0f}% of gen"
                         if n_skim else "skim total n/a")
            ax.text(0.03, 0.62, f"total SR $\\epsilon$={100*sum(effs.values()):.1f}%\n{skim_note}",
                    transform=ax.transAxes, fontsize=8.5,
                    bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.8))

        for j in range(len(mass_points), len(axes_flat)):
            axes_flat[j].axis("off")

        fig.suptitle(f"{ch} 2022  —  3SR reco-mass distributions per mass point "
                     f"(fractions of generated events)", fontsize=16)
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        out = f"{OUT_DIR}/{ch}_3SR_mass_distribution.png"
        fig.savefig(out, dpi=130)
        plt.close(fig)
        print("wrote", out)

        # --- efficiency summary: epsilon per SR vs mass point ---
        fig, ax = plt.subplots(figsize=(11, 6))
        x = np.arange(len(summary))
        width = 0.27
        for k, (suffix, _, label, color) in enumerate(CATEGORIES):
            ys = [100 * effs[suffix] for _, effs in summary]
            ax.bar(x + (k - 1) * width, ys, width, color=color, label=label)
        ax.set_xticks(x)
        ax.set_xticklabels([lab for lab, _ in summary], fontsize=11)
        ax.set_ylabel("selection efficiency [%]", fontsize=13)
        ax.set_title(f"{ch} 2022 — 3SR efficiencies vs mass point", fontsize=15)
        ax.legend(fontsize=11)
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        out = f"{OUT_DIR}/{ch}_3SR_efficiency_summary.png"
        fig.savefig(out, dpi=130)
        plt.close(fig)
        print("wrote", out)


if __name__ == "__main__":
    main()
