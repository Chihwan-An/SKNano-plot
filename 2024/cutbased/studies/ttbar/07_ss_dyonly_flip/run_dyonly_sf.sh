#!/usr/bin/env bash
# DY-only flip, with and without the measured flip SF applied to gen-flipped MC.
set -uo pipefail
H=$(cd "$(dirname "$0")" && pwd)
T=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
cd $T
E=800,1000,1200,1400,1600,2000,2400,2800,3132,8000
J=data/chargeflip/chargeflip_ptshift_ee2024_sf3roofit.json
python3 -u $H/chargeflip_ddss_dyonly.py --dumps data/chargeflip/dumps_v4/all --json $J --sf2 --dy-only \
  --sr-edges $E --out $H/ddss_dyonly_sf.root > $H/log_dyonly_sf.txt 2>&1
echo "dyonly+SF rc=$?"
