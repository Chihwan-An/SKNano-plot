#!/usr/bin/env bash
# signal templates of rEESR_SS at the tail edges (cbv15_dc_cards default TAIL_EE for rEESR_SS), same inputs as cbv15_an2_ref
set -uo pipefail
T=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test
W=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/studies/ttbar/07_ss_dyonly_flip/decomp_20261001
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
cd $T
python3 scripts/cbv15_dc_cards.py --shapes cbv15dc/shapes_2024_dc.root --shapes-mm cbv15dc/shapes_2024_dc_mm.root \
  --shapes-cr cbv15dc/shapes_2024_dc_cr.root --ddss $W/ddss_dyonly_sf_tail.root --all-masses --tag cbv15_tmp_tailsig 2>&1 | grep -v "^$" | tail -8
echo TAILSIG rc=$?
