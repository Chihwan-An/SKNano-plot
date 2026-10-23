#!/usr/bin/env bash
# Impacts on r for one channel, run locally in parallel (this host has 48 cores; one fit is
# ~2 min, so ~50 fits finish in well under 10 min -- faster than a condor round trip).
# autoMCStats (prop_bin*) are excluded: 108 extra fits that do not bear on the JES question.
#   bash run_impacts_local.sh <EE|MM> [nparallel]
set -uo pipefail
CH=$1; NP=${2:-16}
H=$(cd "$(dirname "$0")" && pwd)
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
cd $H/$CH
OPTS="-m 125 --robustFit 1 --cminDefaultMinimizerStrategy 0"
[ -f higgsCombine_initialFit_Test.MultiDimFit.mH125.root ] || \
  combineTool.py -M Impacts -d ws.root --doInitialFit $OPTS > initfit.log 2>&1
combineTool.py -M Impacts -d ws.root --doFits --parallel $NP \
  --exclude 'rgx{prop_bin.*}' $OPTS > dofits.log 2>&1
echo "doFits rc=$?"
combineTool.py -M Impacts -d ws.root -o impacts_${CH}.json --exclude 'rgx{prop_bin.*}' $OPTS > collect.log 2>&1
plotImpacts.py -i impacts_${CH}.json -o impacts_${CH} > plot.log 2>&1
echo "IMPACTS_DONE $CH rc=$?"; ls -la impacts_${CH}.json impacts_${CH}.pdf 2>&1
