#!/usr/bin/env python
"""Preflight check for the HNWR syst_plotter inputs.

Catches the failure mode that produced the fake one-sided systematic band on the
2024 plots (2026-07-10): a sample that has a `Central` histogram but is missing
its `{syst}_Up` / `{syst}_Down` counterpart.

The year_sep plotters drop such a sample from the up/down sum while still
counting it in Central, so both variations land *below* nominal and the whole
deviation is booked as a downward uncertainty. The year_combined plotters
substitute Central instead, which hides the problem but silently understates the
uncertainty. Either way the sample must not be there.

Run before submitting the plotter DAGs:

    python check_inputs.py                # all input dirs the plotters read
    python check_inputs.py --dir /some/dir

Exit status is 1 if any sample is incomplete, so it can gate a submit script.
"""
import argparse
import os
import sys

import ROOT

ROOT.gErrorIgnoreLevel = ROOT.kFatal
ROOT.gROOT.SetBatch(True)

BASE = "/gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy"

DEFAULT_DIRS = [
    f"{BASE}/combined_22_23/2022",
    f"{BASE}/combined_22_23/2022EE",
    f"{BASE}/combined_22_23/2023",
    f"{BASE}/combined_22_23/2023BPix",
    f"{BASE}/2024",
    f"{BASE}/combined_22_23_24/merged",
]

SYST_LIST = ["Pileup", "ElectronID", "ElectronReco", "ElectronTrig",
             "MuonID", "MuonReco", "MuonTrig", "MuonIso", "JER", "JES"]

# One probe histogram per (category, channel). A sample is checked in a channel
# only if it actually populates that channel's Central histogram.
PROBES = [
    "DYCR_Boosted_EE_phi",
    "DYCR_Resolved_EE_phi",
    "DYCR_Boosted_MM_phi",
    "DYCR_Resolved_MM_phi",
]

# Data and skims carry no systematic variations. "Muon"/"EGamma" cover both the
# 22/23 naming (Muon_C) and the 2024 v15 naming (2024Muon0_C), matching the
# plotters' own EXCLUDE_SAMPLES / DATA_FILES.
SKIP_SUBSTR = ["Skim", "EGamma", "Muon", "SingleMuon"]


def is_mc(fname):
    return (fname.endswith(".root")
            and not fname.startswith("WR")
            and not any(s in fname for s in SKIP_SUBSTR))


def check_dir(path, threshold):
    """Return (n_mc, blocking problems, negligible problems).

    A missing variation only matters in proportion to the yield the sample
    contributes: the plotter writes no histogram at all when a variation has
    zero entries, so a sample holding a fraction of an event legitimately shows
    up as "missing". Anything at or above `threshold` percent of the channel is
    treated as blocking.
    """
    if not os.path.isdir(path):
        print(f"  !! directory not found: {path}")
        return 0, [], []

    found = []
    totals = {p: 0.0 for p in PROBES}
    mc = sorted(f for f in os.listdir(path) if is_mc(f))

    for fname in mc:
        f = ROOT.TFile.Open(os.path.join(path, fname))
        if not f or f.IsZombie():
            print(f"  !! unreadable: {fname}")
            continue
        for probe in PROBES:
            hc = f.Get(f"Central/{probe}")
            if not hc:
                continue
            central = hc.Integral()
            if central <= 0:
                continue
            totals[probe] += central
            missing = [f"{s}_{v}" for s in SYST_LIST for v in ("Up", "Down")
                       if not f.Get(f"{s}_{v}/{probe}")]
            if missing:
                found.append((fname, probe, central, missing))
        f.Close()

    blocking, negligible = [], []
    for fname, probe, central, missing in found:
        frac = central / totals[probe] * 100 if totals[probe] else 0.0
        tag = ", ".join(missing) if len(missing) <= 4 else f"{len(missing)} variations"
        line = (f"{fname:38s} {probe:24s} Central={central:10.1f} "
                f"({frac:5.2f}% of channel)  missing: {tag}")
        if frac >= threshold:
            blocking.append(line)
        else:
            negligible.append(line)

    for line in blocking:
        print(f"  BAD  {line}")
    for line in negligible:
        print(f"  warn {line}")

    return len(mc), blocking, negligible


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", action="append", dest="dirs",
                    help="input directory to check (repeatable); default: all plotter inputs")
    ap.add_argument("--threshold", type=float, default=0.5,
                    help="percent of a channel's yield above which a missing "
                         "variation is blocking rather than a warning (default: 0.5)")
    args = ap.parse_args()

    dirs = args.dirs or DEFAULT_DIRS
    bad_dirs, n_warn = 0, 0

    for path in dirs:
        print(f"\n>> {path}")
        n_mc, blocking, negligible = check_dir(path, args.threshold)
        n_warn += len(negligible)
        if blocking:
            bad_dirs += 1
            print(f"  -> {len(blocking)} blocking, {len(negligible)} negligible "
                  f"(of {n_mc} MC samples)")
        elif negligible:
            print(f"  OK  {n_mc} MC samples ({len(negligible)} sub-threshold, "
                  f"empty-histogram cases)")
        else:
            print(f"  OK  {n_mc} MC samples, all {len(SYST_LIST)} systematics present")

    print()
    if bad_dirs:
        print(f"FAIL: {bad_dirs} directory(ies) contain samples with a Central "
              f"histogram but no up/down variation.")
        print("Move those files out of the input directory before plotting.")
        return 1
    print(f"PASS: every MC sample carries all systematic variations "
          f"(+{n_warn} sub-threshold warnings).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
