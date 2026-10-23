#!/usr/bin/env bash
# Re-run the v2 noSSTT CR+SR b-only fit with --ignoreCovWarning so shapes_fit_b keeps
# postfit uncertainties (fit_b covQual is 2, and combine otherwise drops them).
#   bash run_unc_fit.sh <EE|MM>      (EL9 host, e.g. tamsa2)
set -uo pipefail
CH=$1; HERE=$(cd "$(dirname "$0")" && pwd)
N=cbv15_an2_ref_v2_${CH}_WR5000_N2500_noSSTT
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
mkdir -p $HERE/$N; cd $HERE/$N
cp $HERE/../work_srcr/$N/card.txt $HERE/../work_srcr/$N/ws.root .
combine -M FitDiagnostics ws.root -n .SRCR --setParameters r=0 --freezeParameters r \
  --skipSBFit --saveShapes --saveNormalizations --saveWithUncertainties --ignoreCovWarning \
  --cminDefaultMinimizerStrategy 1 --cminDefaultMinimizerTolerance 0.1 \
  --cminFallbackAlgo Minuit2,Migrad,0:0.5 --cminFallbackAlgo Minuit2,Migrad,0:1.0 > fit.log 2>&1
echo "$CH fit rc=$?"
