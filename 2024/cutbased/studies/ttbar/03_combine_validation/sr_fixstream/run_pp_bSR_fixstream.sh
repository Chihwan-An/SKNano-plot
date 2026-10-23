#!/usr/bin/env bash
# Regenerate ONLY the boosted SRs with the stream-leak fix in place (studies/ttbar 06 §1).
# Resolved SRs need nothing: the analyzer fills no resolved-SR data at all, so there is no leak there
# (measured 2026-09-22: rEESR_OS / rMuMuSR_OS / rMuMuSR_SS wrong-stream counts are exactly 0).
# Boosted does leak: bEESR 49 Muon-stream events, bMuMuSR 68 EGamma-stream events -> MC "Others".
# Native (no cmssw-el9 wrapper -- see RUNBOOK_env.md).
set -uo pipefail
H=$(cd "$(dirname "$0")" && pwd)
S=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
cd $S/cbv15dc; export HNWR_XSECSYST_DIR=$S/cbv15dc/xsecsyst
python3 -u $S/cbv15/post_processor_chsplit.py $S/cbv15dc/input2024 --era 2024 \
  --output $H/shapes_2024_bSR_fixstream.root --regions bEESR bMuMuSR
echo "PP_DONE rc=$?"
