#!/usr/bin/env bash
# Asymptotic blind limits over the whole mass grid of a scenario, in parallel on this host.
# AsymptoticLimits is ~1 min per point, so 24 points finish in a couple of minutes on 48 cores;
# only the HybridNew toy limits are worth a condor round trip (see condor/).
#   bash run_blind_grid_local.sh <scenario tag> [nparallel]
set -uo pipefail
TAG=$1; NP=${2:-12}
H=$(cd "$(dirname "$0")" && pwd)
SCEN=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/combine/scenarios/test/$TAG
JOBS=$H/work_blind/${TAG}_jobs.txt; mkdir -p $H/work_blind; : > $JOBS
for ch in EE MM; do
  for c in $SCEN/datacards/2024/$ch/card_WR*_N*.txt; do
    [ -e "$c" ] || continue
    mp=$(basename "$c" .txt); echo "$ch ${mp#card_}" >> $JOBS
  done
done
echo "points: $(wc -l < $JOBS)"
xargs -a $JOBS -P $NP -L1 bash -c 'bash '"$H"'/run_blind_limit.sh '"$TAG"' $0 $1 >/dev/null 2>&1; echo "done $0 $1"'
echo "GRID_DONE"
