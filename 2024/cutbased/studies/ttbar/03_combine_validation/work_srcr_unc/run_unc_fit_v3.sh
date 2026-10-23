#!/usr/bin/env bash
# v3 (DY-only EE same-sign flip) CR+SR b-only fit with --ignoreCovWarning so shapes_fit_b keeps
# postfit uncertainties. v3 cards already carry the right SS rateParams -- do NOT strip them
# (no DROP_SS_TT here).   bash run_unc_fit_v3.sh <EE|MM>
set -uo pipefail
CH=$1; HERE=$(cd "$(dirname "$0")" && pwd)
N=cbv15_an2_ref_v3_${CH}_WR5000_N2500
SCEN=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/combine/scenarios/test/cbv15_an2_ref_v3
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
mkdir -p $HERE/$N; cd $HERE/$N
cp $SCEN/datacards/2024/$CH/card_WR5000_N2500.txt card.txt
[ -f ws.root ] || text2workspace.py card.txt -o ws.root > t2w.log 2>&1 || { echo T2W_FAILED; tail -3 t2w.log; exit 1; }
combine -M FitDiagnostics ws.root -n .SRCR --setParameters r=0 --freezeParameters r \
  --skipSBFit --saveShapes --saveNormalizations --saveWithUncertainties --ignoreCovWarning \
  --cminDefaultMinimizerStrategy 1 --cminDefaultMinimizerTolerance 0.1 \
  --cminFallbackAlgo Minuit2,Migrad,0:0.5 --cminFallbackAlgo Minuit2,Migrad,0:1.0 > fit.log 2>&1
echo "$CH fit rc=$?"
