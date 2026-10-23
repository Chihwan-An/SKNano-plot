#!/usr/bin/env bash
# 2026-10-01 EE SS at ...,3200,4000,8000 (raw_ne10 SS edge): DY-only flip bkg + signal (same inputs as v3_ss3200)
set -uo pipefail
H=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased/studies/ttbar/07_ss_dyonly_flip
W=$H/decomp_20261001
T=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
cd $T
python3 -u $H/chargeflip_ddss_dyonly.py --dumps data/chargeflip/dumps_v4/all --json data/chargeflip/chargeflip_ptshift_ee2024_sf3roofit.json \
  --sf2 --dy-only --sr-edges 800,1000,1200,1400,1600,2000,2400,2800,3200,4000,8000 --out $W/ddss_dyonly_sf_ss4000.root > $W/log_ss4000.txt 2>&1
echo DDSS rc=$?
python3 scripts/cbv15_dc_cards.py --shapes cbv15dc/shapes_2024_dc.root --shapes-mm cbv15dc/shapes_2024_dc_mm.root \
  --shapes-cr cbv15dc/shapes_2024_dc_cr.root --ddss $W/ddss_dyonly_sf_ss4000.root --edges-json $W/ss4000.json --all-masses --tag cbv15_tmp_ss4000sig 2>&1 | grep -v "^$" | tail -3
echo SIG rc=$?
