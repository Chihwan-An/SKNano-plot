#!/usr/bin/env bash
# One diagnostic job. args: CH VAR TAG MODE KEEP FREEZE FIRST LAST
#   VAR   base|slope          workspace
#   MODE  scan|fitdiag        MultiDimFit grid on JES_2024 (points FIRST..LAST of 51 on [-1,9]) | FitDiagnostics b-only
#   KEEP  all | comma list of channels to KEEP (every other channel masked) | -comma list of channels to MASK
#   FREEZE none | comma list of nuisances to freeze | @alljes = freeze every constrained nuisance except JES_2024
set -uo pipefail
CH=$1; VAR=$2; TAG=$3; MODE=$4; KEEP=$5; FREEZE=$6; FIRST=${7:-0}; LAST=${8:-50}
P=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/studies/pull_plot
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
W=$P/combine/$CH/$VAR; CARD=$W/card.txt; [ -f $W/card_slope.txt ] && CARD=$W/card_slope.txt
OUT=$P/combine/$CH/out; mkdir -p $OUT; cd $OUT
BINS=$(awk '$1=="bin"{for(i=2;i<=NF;i++) print $i; exit}' $CARD)
SP="r=0"; FR="r"
for b in $BINS; do
  m=0
  if [ "$KEEP" != "all" ]; then
    if [[ "$KEEP" == -* ]]; then [[ ",${KEEP#-}," == *",$b,"* ]] && m=1
    else [[ ",$KEEP," == *",$b,"* ]] || m=1; fi
  fi
  SP="$SP,mask_$b=$m"; FR="$FR,mask_$b"
done
# rateParams acting only on masked channels have no data left: flat directions that make the initial fit fail -> freeze at 1
if [ "$KEEP" != "all" ]; then
  for rp in $(awk '$2=="rateParam"{print $1}' $CARD | sort -u); do
    live=0
    for c in $(awk -v n=$rp '$1==n && $2=="rateParam"{print $3}' $CARD); do
      if [[ "$KEEP" == -* ]]; then [[ ",${KEEP#-}," == *",$c,"* ]] || live=1
      else [[ ",$KEEP," == *",$c,"* ]] && live=1; fi
    done
    [ $live = 0 ] && { SP="$SP,$rp=1"; FR="$FR,$rp"; }
  done
fi
if [ "$FREEZE" = "@alljes" ]; then
  NU=$(awk '$2=="shape"||$2=="lnN"{print $1}' $CARD | grep -vx JES_2024 | paste -sd,)
  FR="$FR,$NU"
elif [ "$FREEZE" != "none" ]; then FR="$FR,$FREEZE"; fi
COMMON="--cminDefaultMinimizerStrategy 1 --cminDefaultMinimizerTolerance 0.1 --cminFallbackAlgo Minuit2,Migrad,0:0.5 --cminFallbackAlgo Minuit2,Migrad,0:1.0 --X-rtd MINIMIZER_analytic"
if [ "$MODE" = "scan" ]; then
  combine -M MultiDimFit $W/ws.root -n ".${VAR}.${TAG}.p${FIRST}" --algo grid --points 51 --firstPoint $FIRST --lastPoint $LAST \
    --redefineSignalPOIs JES_2024 -P JES_2024 --setParameterRanges JES_2024=-1,9 --floatOtherPOIs 0 \
    --setParameters $SP --freezeParameters $FR $COMMON > log_${VAR}_${TAG}_p${FIRST}.txt 2>&1
else
  combine -M FitDiagnostics $W/ws.root -n ".${TAG}" --setParameters $SP --setParameterRanges JES_2024=-4,8 --freezeParameters $FR --skipSBFit $COMMON \
    > log_${TAG}.txt 2>&1
fi
echo "JOB_DONE $CH $VAR $TAG $MODE rc=$?"
