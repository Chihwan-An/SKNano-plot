#!/usr/bin/env bash
# RUN ON tamsa2 (210.117.219.6) -- ai-tamsa1 has no condor.
# One job per (channel, masspoint, quantile) HybridNew toy limit.
#   bash submit_hybrid_limits.sh [scenario tag]   (default: cbv15_an2_ref_v2)
set -euo pipefail
TAG=${1:-cbv15_an2_ref_v2}
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers
SCEN=$REPO/BDT/combine/scenarios/test/$TAG
LOG=$HERE/logs; mkdir -p "$LOG"

JOBS=$HERE/jobs_hybrid_${TAG}.txt; : > "$JOBS"
for ch in EE MM; do
  for c in "$SCEN"/datacards/2024/$ch/card_WR*_N*.txt; do
    [ -e "$c" ] || continue
    mp=$(basename "$c" .txt); mp=${mp#card_}
    for q in 0.025 0.16 0.5 0.84 0.975; do echo "$TAG $ch $mp $q" >> "$JOBS"; done
  done
done
N=$(wc -l < "$JOBS"); echo "hybrid jobs: $N  ($JOBS)"
[ "$N" -gt 0 ] || { echo "no cards under $SCEN"; exit 1; }

SUB=$HERE/hybrid_${TAG}.sub
cat > "$SUB" <<SUBEOF
universe        = vanilla
executable      = $HERE/run_one_hybrid_limit.sh
arguments       = "\$(ARGS)"
request_cpus    = 1
request_memory  = 4096
request_disk    = 2048MB
getenv          = True
should_transfer_files = NO
log             = $LOG/hybrid_${TAG}.\$(Cluster).log
output          = $LOG/\$(Cluster).\$(Process).out
error           = $LOG/\$(Cluster).\$(Process).err
queue ARGS from $JOBS
SUBEOF
echo "submit file: $SUB"
condor_submit "$SUB"
