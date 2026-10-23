#!/usr/bin/env bash
# 2026-10-02: expected limits (same method as the AN, run_blind_limit.sh = AsymptoticLimits --run blind) for v3_ss3200 (D)
# and the decomposition scenarios, at the mN = 200 GeV and mN = mWR/2 points used in the crossing table.
set -uo pipefail
W=$(cd "$(dirname "$0")" && pwd)
R=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased/studies/ttbar/03_combine_validation/run_blind_limit.sh
TAGS="cbv15_an2_ref_v3_ss3200 cbv15_decomp_split_run2bin cbv15_decomp_incl_run2bin cbv15_decomp_split_newbin cbv15_decomp_incl_newbin cbv15_decomp_split_ssne10"
J=$W/work_blind/jobs.txt; mkdir -p $W/work_blind; : > $J
for t in $TAGS; do for ch in EE MM; do for m in 1000 2000 3000 4000 5000 6000 7000; do
  for n in 200 $((m/2)); do echo "$t $ch WR${m}_N${n}" >> $J; done; done; done; done
echo "jobs: $(wc -l < $J)"
xargs -a $J -P ${1:-12} -L1 bash -c 'bash '"$R"' $0 $1 $2 '"$W"'/work_blind > /dev/null 2>&1; echo "done $0 $1 $2"'
echo ALL_DONE
