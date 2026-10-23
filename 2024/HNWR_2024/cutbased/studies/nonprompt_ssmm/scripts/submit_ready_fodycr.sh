#!/usr/bin/env bash
# Submit DY CR FO skims for every sample (MC from the main run, data from the data run) that is complete and has no skim yet.
set -uo pipefail
ST=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased/studies/nonprompt_ssmm
source $ST/scripts/fodycr_paths.sh
cd $ST; mkdir -p skim/hnwr_fodycr; : > ready_fodycr.txt
for s in $( (ls $RL_MC | grep -v Muon; ls $RL_DATA) ); do
  [ -f skim/hnwr_fodycr/$s.npz ] && continue
  grep -qx "$s" submitted_fodycr.txt 2>/dev/null && continue
  [ -n "$(fo_src $s)" ] && echo $s >> ready_fodycr.txt
done
n=$(wc -l < ready_fodycr.txt); echo "ready: $n"
[ "$n" -eq 0 ] && exit 0
ssh -o BatchMode=yes -p 1240 achihwan@210.117.219.6 "cd $ST && condor_submit skim_fodycr.sub" | tail -1 && cat ready_fodycr.txt >> submitted_fodycr.txt
