#!/usr/bin/env bash
# Two impact scans, run locally in parallel.
#   MODE=r     : POI = r, range opened to negative. With the SR as background-only Asimov the
#                best fit sits exactly at r=0; if r is bounded at 0 every impact comes out 0
#                ("Closed range without finding crossing"), which is what the first attempt hit.
#   MODE=beta  : POI = R_TT_Resolved_2024. Directly answers "what moves beta", i.e. the JES question.
#   bash run_impacts_v2.sh <EE|MM> <r|beta> [nparallel]
set -uo pipefail
CH=$1; MODE=$2; NP=${3:-12}
H=$(cd "$(dirname "$0")" && pwd)
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
D=$H/${CH}_${MODE}; mkdir -p $D; cd $D
cp $H/$CH/ws.root . 2>/dev/null
OPTS="-m 125 --robustFit 1 --cminDefaultMinimizerStrategy 0 --exclude rgx{prop_bin.*}"
if [ "$MODE" = "r" ]; then
  EXTRA="--setParameterRanges r=-5,5"
else
  EXTRA="--redefineSignalPOIs R_TT_Resolved_2024"
fi
combineTool.py -M Impacts -d ws.root --doInitialFit $OPTS $EXTRA > initfit.log 2>&1
combineTool.py -M Impacts -d ws.root --doFits --parallel $NP $OPTS $EXTRA > dofits.log 2>&1
combineTool.py -M Impacts -d ws.root -o impacts.json $OPTS $EXTRA > collect.log 2>&1
plotImpacts.py -i impacts.json -o impacts > plot.log 2>&1
echo "IMPACTS_DONE $CH $MODE"; ls -la impacts.json impacts.pdf 2>&1 | tail -2
