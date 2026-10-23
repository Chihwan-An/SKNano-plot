#!/usr/bin/env bash
# 2026-09-22: redraw every run_specs family of out/ for one (region, channel) job with the new DY
# correction (per-GenJet FxFx/LO C + its R). Inputs = the symlinked sets built by
# studies/DY/09_three_generators/scripts/make_dynew_plotsets.sh. Order matters: --skip-existing keeps
# the first drawing of a file, and out/<..>/sig Inclusive came from the rawcharge specs.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$HERE/.."
JOB="$1"
D=/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/RFlav_DYCRCharge_ZptNJet/2024
C=/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/RFlav_SRChargeSplit_plot_ZptNJet/2024
run() { echo "=== $JOB :: $*"; "$HERE/in_container.sh" python run_specs.py "$JOB" --skip-existing --quiet "$@" || echo "!!! FAILED: $JOB $*"; }
R=${JOB%%_*}                                   # Boost | Resolve
[ -f specs/rawcharge/$JOB.txt ]   && run --spec specs/rawcharge/$JOB.txt --input $D
run --spec specs/$JOB.txt --input $D
for s in specs/tightcharge/$JOB.txt specs/tightcharge/${JOB}_alltc.txt specs/tightcharge/${JOB}_alltc_etawide.txt; do
    [ -f $s ] && run --spec $s --input $D; done
[ "$JOB" = Resolve_FLV_EM ] && run --spec specs/rawcharge/Resolve_FLV_EM_charge.txt --input $D --outdir out/Resolve/FLV
export PLOT_SIGNAL_POINTS=MWR4000_N200,MWR4000_N2000,MWR6000_N200,MWR6000_N3000
for s in specs/chargesign/$JOB.txt specs/chargesign/${JOB}_mll.txt; do
    [ -f $s ] && run --spec $s --input $C --outdir out/$R/sig_chargesign; done
echo "=== done $JOB $(date)"
