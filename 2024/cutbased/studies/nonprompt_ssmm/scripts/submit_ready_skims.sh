#!/usr/bin/env bash
# Submit skim jobs for every sample whose analyzer jobs have all written output and that has no skim yet.
set -uo pipefail
ST=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/studies/nonprompt_ssmm
RL1=/gv0/Users/achihwan/SKNanoRunlog/2026_09_24_001016_HNWR_FOMode_RFlav/2024
RL2=/gv0/Users/achihwan/SKNanoRunlog/2026_09_24_031413_HNWR_FOMode_RFlav/2024   # QCD + signals (after both LHE guards)
RL4=/gv0/Users/achihwan/SKNanoRunlog/2026_09_24_040510_HNWR_FOMode_RFlav/2024   # the 6 signals, run on their own
rl() { if [ -d "$RL4/$1" ]; then echo "$RL4"; elif [ -d "$RL2/$1" ]; then echo "$RL2"; else echo "$RL1"; fi; }
cd $ST; : > ready_skims.txt
while read -r s; do
  [ -f skim/hnwr_fo/$s.npz ] && continue
  grep -qx "$s" submitted_skims.txt 2>/dev/null && continue
  RL=$(rl $s); nj=$(ls $RL/$s/job_*.cc 2>/dev/null | wc -l); no=$(ls $RL/$s/output/hists_*.root 2>/dev/null | wc -l)
  if [ "$RL" != "$RL1" ] && [ -f /gv0/Users/achihwan/SKNanoOutput/HNWR/backup/FOMode_RFlav/2024/$s.root ] && [ -f $RL/$s/hadd.out ]; then
    echo $s >> ready_skims.txt; continue   # hadded (per-job outputs are removed after the merge)
  fi
  [ "$nj" -gt 0 ] && [ "$nj" -eq "$no" ] && echo $s >> ready_skims.txt
done < hnwr_fo_mc_samples_2024.txt
n=$(wc -l < ready_skims.txt); echo "ready: $n"
[ "$n" -eq 0 ] && exit 0
sed 's/queue sample from hnwr_fo_mc_samples_2024.txt/queue sample from ready_skims.txt/' skim_fo.sub > skim_fo_ready.sub
ssh -o BatchMode=yes -p 1240 achihwan@210.117.219.6 "cd $ST && condor_submit skim_fo_ready.sub" | tail -1 && cat ready_skims.txt >> submitted_skims.txt
