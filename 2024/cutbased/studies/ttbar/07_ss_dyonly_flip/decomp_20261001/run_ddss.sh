#!/usr/bin/env bash
# 2026-10-01 binning / charge-split decomposition: DY-only flip EE SS templates
#   chk  : ss3200 edges again (must reproduce ../ddss_dyonly_sf_ss3200.root used by cbv15_an2_ref_v3_ss3200)
#   tail : chsplit3 tail edges (...,3200,3561,4643,5533,8000) for the charge-inclusive new-binning variant
set -uo pipefail
H=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/studies/ttbar/07_ss_dyonly_flip
W=$H/decomp_20261001
T=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
cd $T
J=data/chargeflip/chargeflip_ptshift_ee2024_sf3roofit.json
run() { python3 -u $H/chargeflip_ddss_dyonly.py --dumps data/chargeflip/dumps_v4/all --json $J --sf2 --dy-only --sr-edges $2 --out $W/ddss_dyonly_sf_$1.root > $W/log_$1.txt 2>&1; echo "$1 rc=$?"; }
run chk 800,1000,1200,1400,1600,2000,2400,2800,3200,8000 &
run tail 800,1000,1200,1400,1600,2000,2400,2800,3200,3561,4643,5533,8000 &
wait
