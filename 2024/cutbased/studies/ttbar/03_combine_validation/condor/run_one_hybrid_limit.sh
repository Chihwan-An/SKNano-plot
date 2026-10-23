#!/usr/bin/env bash
# Condor executable: one HybridNew (toy) expected-limit quantile for one (channel, masspoint).
# Toys are the only part of this study that is genuinely condor scale -- AsymptoticLimits and the
# impact scans finish in minutes on a 48-core login node (see run_blind_grid_local.sh,
# impacts/run_impacts_v2.sh).
#
#   args: SCENARIO_TAG CHANNEL MASSPOINT QUANTILE
#     e.g. cbv15_an2_ref_v2 EE WR5000_N2500 0.5
set -uo pipefail
TAG=$1; CH=$2; MP=$3; Q=$4

REPO=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers
SCEN=$REPO/BDT/combine/scenarios/test/$TAG
OUT=$REPO/plot/cutbased/studies/ttbar/03_combine_validation/work_hybrid/${TAG}_${CH}_${MP}_q${Q}

run_it() {
  source /cvmfs/cms.cern.ch/cmsset_default.sh
  cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src && eval $(scramv1 runtime -sh)
  mkdir -p "$OUT" && cd "$OUT"
  cp "$SCEN/datacards/2024/$CH/card_$MP.txt" card.txt
  [ -f ws.root ] || text2workspace.py card.txt -o ws.root > t2w.log 2>&1 || { echo T2W_FAILED; exit 1; }
  combine -M HybridNew ws.root -n ".Hybrid_${CH}_${MP}_q${Q}" \
      --LHCmode LHC-limits --expectedFromGrid "$Q" \
      --rAbsAcc 1e-5 --rRelAcc 0.005 --saveHybridResult \
      -T 2000 --clsAcc 0 > hybrid.log 2>&1
  rc=$?
  echo "HYBRID rc=$rc"; grep -iE "limit:|Limit:" hybrid.log | tail -3
  exit $rc
}

# The cmssw-el9 wrapper hangs forever when a worker has a dead /cvmfs/cms-ib.cern.ch mount
# (it probes that repo with a bare `ls`, which blocks in D state). Run native where the OS
# already matches the build (el9_amd64), and only fall back to the container otherwise.
if grep -qE 'release 9' /etc/redhat-release 2>/dev/null; then
  run_it
else
  export -f run_it; export TAG CH MP Q SCEN OUT
  exec /cvmfs/cms.cern.ch/common/cmssw-el9 -B /data6 -B /data9 -B /gv0 -B /tmp -- bash -c run_it
fi
