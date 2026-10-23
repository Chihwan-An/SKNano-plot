#!/usr/bin/env bash
# Regenerate ONLY the rFlvCR block from the opposite-sign histogram (studies/ttbar 06 §12).
# Native (no cmssw-el9 wrapper -- see RUNBOOK_env.md).
set -uo pipefail
H=$(cd "$(dirname "$0")" && pwd)
S=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
export HNWR_XSECSYST_DIR=$S/cbv15dc/xsecsyst
cd $H
python3 -u $H/post_processor_flvos.py $S/cbv15dc/input2024 --era 2024 \
  --output $H/shapes_flvcr_os.root --regions rFlvCR --no-signal
echo "PP_DONE rc=$?"
