#!/usr/bin/env bash
# Leave-one-channel-out scan: which channel drags JES_2024 to +2.9 sigma and over-constrains it?
# One fit with nothing masked, then one fit per channel with that channel masked (r = 0 frozen).
# The card is the v2 card with the SS-channel TT rateParam already removed (DROP_SS_TT=1).
#   bash run_mask_scan.sh <EE|MM> [nparallel]
set -uo pipefail
CH=$1; NP=${2:-13}
H=$(cd "$(dirname "$0")" && pwd)
SRC=$H/../work_srcr/cbv15_an2_ref_v2_${CH}_WR5000_N2500_noSSTT/card.txt
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
W=$H/$CH; mkdir -p $W; cd $W
cp $SRC card.txt
[ -f ws_masks.root ] || text2workspace.py card.txt -o ws_masks.root --channel-masks > t2w.log 2>&1 || { echo T2W_FAILED; exit 1; }
BINS=$(awk '$1=="bin"{for(i=2;i<=NF;i++) print $i; exit}' card.txt)
ALLM=""; for b in $BINS; do ALLM="$ALLM,mask_$b"; done; ALLM=${ALLM#,}
fit() {   # $1 = tag, $2 = masked channel or "none"
  local tag=$1 m=$2 sp="r=0"
  for b in $BINS; do [ "$b" = "$m" ] && sp="$sp,mask_$b=1" || sp="$sp,mask_$b=0"; done
  combine -M FitDiagnostics ws_masks.root -n ".$tag" --setParameters $sp --freezeParameters r,$ALLM \
    --skipSBFit --cminDefaultMinimizerStrategy 1 --cminDefaultMinimizerTolerance 0.1 \
    --cminFallbackAlgo Minuit2,Migrad,0:0.5 --cminFallbackAlgo Minuit2,Migrad,0:1.0 > fit_$tag.log 2>&1
}
export -f fit; export BINS ALLM
( echo "none none"; for b in $BINS; do echo "no_$b $b"; done ) | xargs -P $NP -L1 bash -c 'fit $0 $1'
echo "MASKSCAN_DONE $CH"
