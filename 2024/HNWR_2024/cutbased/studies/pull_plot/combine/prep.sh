#!/usr/bin/env bash
# Build the workspaces for the pull_plot diagnostics (runs on tamsa2, EL9, native CMSSW).
#   base  : the v2 card of the mask scan (SS-TT rateParam removed), --channel-masks
#   slope : the same card + MassSlopeDY / MassSlopeTT (make_slope_card.py), --channel-masks
set -uo pipefail
P=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased/studies/pull_plot
M=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased/studies/ttbar/03_combine_validation/mask_scan
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
for CH in EE MM; do
  W=$P/combine/$CH; mkdir -p $W/base $W/slope
  cp $M/$CH/card.txt $W/base/card.txt; cp $M/$CH/ws_masks.root $W/base/ws.root
  python3 $P/scripts/make_slope_card.py $W/base/card.txt $W/slope --k 0.10 > $W/slope/make.log 2>&1 || { echo SLOPE_FAILED $CH; tail $W/slope/make.log; }
  ( cd $W/slope && text2workspace.py card_slope.txt -o ws.root --channel-masks > t2w.log 2>&1 && echo T2W_OK $CH || { echo T2W_FAILED $CH; tail -5 t2w.log; } )
done
