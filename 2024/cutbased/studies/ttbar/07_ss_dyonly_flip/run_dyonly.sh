#!/usr/bin/env bash
# EE same-sign templates two ways, same inputs as BDT/SR/test/condor/an2_chain.sh:
#   baseline : Flip = ALL OS data x w   (current cards)
#   dy-only  : Flip = (OS data - non-DY OS MC) x w, and TT/Nonprompt/Others taken from the FULL SS MC
# Native (no cmssw-el9 wrapper -- see ../RUNBOOK_env.md).
set -uo pipefail
H=$(cd "$(dirname "$0")" && pwd)
T=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
cd $T
EDGES=800,1000,1200,1400,1600,2000,2400,2800,3132,8000     # an2_chain 이 쓴 rEESR_SS edge (3132)
python3 -u $H/chargeflip_ddss_dyonly.py --dumps data/chargeflip/dumps_v4/all \
  --json data/chargeflip/chargeflip_ptshift_ee2024_sf3roofit.json --sf2 \
  --sr-edges $EDGES --out $H/ddss_baseline.root > $H/log_baseline.txt 2>&1
echo "baseline rc=$?"
python3 -u $H/chargeflip_ddss_dyonly.py --dumps data/chargeflip/dumps_v4/all \
  --json data/chargeflip/chargeflip_ptshift_ee2024_sf3roofit.json --sf2 --dy-only \
  --sr-edges $EDGES --out $H/ddss_dyonly.root > $H/log_dyonly.txt 2>&1
echo "dyonly rc=$?"
