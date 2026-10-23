#!/usr/bin/env bash
# Fully blind expected limit (spec 8.6): all channels unmasked, r and the rate parameters profiled, no observed data used.
#   bash run_blind_limit.sh <scenario tag> <EE|MM> <mass point> [WORKDIR]
set -uo pipefail
TAG=$1; CH=$2; MP=$3; HERE=$(cd "$(dirname "$0")" && pwd); W=${4:-$HERE/work_blind}/${TAG}_${CH}_${MP}
SCEN=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/combine/scenarios/test/$TAG
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
mkdir -p $W; cd $W
[ -f ws.root ] || { cp $SCEN/datacards/2024/$CH/card_$MP.txt card.txt; text2workspace.py card.txt -o ws.root > t2w.log 2>&1 || { echo T2W_FAILED; exit 1; }; }
combine -M AsymptoticLimits ws.root -n .ExpectedBlind --run blind --rAbsAcc 1e-5 --rRelAcc 0.005 > limit.log 2>&1
echo "rc=$?"; grep "Expected" limit.log
