#!/usr/bin/env bash
# post_processor (2026-09-19 data-stream fix) on the CR regions only -> shapes_2024_dc_cr_fixstream.root
set -uo pipefail
S=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
cd $S/cbv15dc; export HNWR_XSECSYST_DIR=$S/cbv15dc/xsecsyst
python3 -u $S/cbv15/post_processor_chsplit.py $S/cbv15dc/input2024 --era 2024 --output $S/cbv15dc/shapes_2024_dc_cr_fixstream.root \
  --regions rFlvCR bFlvEMuCR bFlvMuECR bDYEECR bDYMuMuCR rDYEECR_OS rDYEECR_SS_2e rDYEECR_SS_lt2 rDYMuMuCR_OS rDYMuMuCR_SS
echo PP_DONE rc=$?
