#!/usr/bin/env bash
# Submit SR-sideband data FO skims for every complete data period without a skim.
set -uo pipefail
ST=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased/studies/nonprompt_ssmm
RL=/gv0/Users/achihwan/SKNanoRunlog/2026_09_24_122235_HNWR_FOMode_FOSB_RFlav/2024
OUT=/gv0/Users/achihwan/SKNanoOutput_fodata/HNWR/FOMode_FOSB_RFlav/2024
cd $ST; mkdir -p skim/hnwr_fosb; : > ready_fosb.txt
for s in $(ls $RL); do
  [ -f skim/hnwr_fosb/$s.npz ] && continue
  grep -qx "$s" submitted_fosb.txt 2>/dev/null && continue
  if [ -f $OUT/$s.root ] && [ -f $RL/$s/hadd.out ]; then echo $s >> ready_fosb.txt; continue; fi
  nj=$(ls $RL/$s/job_*.cc 2>/dev/null | wc -l); no=$(ls $RL/$s/output/hists_*.root 2>/dev/null | wc -l)
  [ "$nj" -gt 0 ] && [ "$nj" -eq "$no" ] && echo $s >> ready_fosb.txt
done
n=$(wc -l < ready_fosb.txt); echo "ready: $n"
[ "$n" -eq 0 ] && exit 0
ssh -o BatchMode=yes -p 1240 achihwan@210.117.219.6 "cd $ST && condor_submit skim_fosb.sub" | tail -1 && cat ready_fosb.txt >> submitted_fosb.txt
