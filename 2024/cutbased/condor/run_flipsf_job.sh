#!/usr/bin/env bash
# 2026-09-25: redraw every run_specs family of out/ for one (region, channel) job from the FlipSF(+EM) production
# (flip SF on all MC, resolved EE + EM; DYCRCharge + SRChargeSplit + ZptNJet in one production). Input = combined set
# /gv0/Users/achihwan/SKNanoOutput/HNWR/FlipSFEM_combined_for_plots/2024 (FlipSF+FlipSFEM MC, data and EE signal from
# the FlipSF production, MuMu signal from RFlav_SRChargeSplit_plot_ZptNJet). Same order as run_dynew_job.sh.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$HERE/.."
JOB="$1"
D=/gv0/Users/achihwan/SKNanoOutput/HNWR/FlipSFEM_combined_for_plots/2024
run() { echo "=== $JOB :: $*"; "$HERE/in_container.sh" python run_specs.py "$JOB" --skip-existing --quiet "$@" || echo "!!! FAILED: $JOB $*"; }
R=${JOB%%_*}
[ -f specs/rawcharge/$JOB.txt ]   && run --spec specs/rawcharge/$JOB.txt --input $D
run --spec specs/$JOB.txt --input $D
for s in specs/tightcharge/$JOB.txt specs/tightcharge/${JOB}_alltc.txt specs/tightcharge/${JOB}_alltc_etawide.txt; do
    [ -f $s ] && run --spec $s --input $D; done
[ "$JOB" = Resolve_FLV_EM ] && run --spec specs/rawcharge/Resolve_FLV_EM_charge.txt --input $D --outdir out/Resolve/FLV
export PLOT_SIGNAL_POINTS=MWR4000_N200,MWR4000_N2000,MWR6000_N200,MWR6000_N3000
for s in specs/chargesign/$JOB.txt specs/chargesign/${JOB}_mll.txt; do
    [ -f $s ] && run --spec $s --input $D --outdir out/$R/sig_chargesign; done
echo "=== done $JOB $(date)"
