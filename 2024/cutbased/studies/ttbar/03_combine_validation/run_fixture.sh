#!/usr/bin/env bash
# spec 10.2 / 10.3: beta injection recovery and mask test on the synthetic fixture.   bash run_fixture.sh [WORKDIR]
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); W=${1:-$HERE/work_fixture}
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
mkdir -p $W; cd $W
echo "combine: $(command -v combine)   version: $(cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit && git describe --tags 2>/dev/null)"
python3 $HERE/make_fixture.py $W
for v in A B; do
  text2workspace.py card_$v.txt -o ws_$v.root --channel-masks > t2w_$v.log 2>&1
  combine -M FitDiagnostics ws_$v.root -n .CRonly_$v \
    --setParameters r=0,mask_CR_EM=0,mask_SR_EE=1 --freezeParameters r,mask_CR_EM,mask_SR_EE \
    --skipSBFit --saveShapes --saveNormalizations --saveWithUncertainties > fit_$v.log 2>&1
  echo "fit $v rc=$?"
done
python3 $HERE/check_fixture.py $W
