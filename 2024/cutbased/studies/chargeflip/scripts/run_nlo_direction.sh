#!/bin/bash
set -euo pipefail
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
repo=$(cd "$script_dir/../../../../../.." && pwd)
export SKNANO_HOME="$repo"
export SKNANO_DATA="$repo/data/Run3_v15_Run2_v15"
export SKNANO_INSTALLDIR="$repo/install/redhat"
export SKNANO_LIB="$SKNANO_INSTALLDIR/lib"
export SKNANO_ANALYSIS_MODULE_DIRS="$repo/Nano15_Analyzers"
export ROOT_INCLUDE_PATH="$SKNANO_INSTALLDIR/include:${CONDA_PREFIX}/include"
correction_lib=$(correction config --libdir)
export LD_LIBRARY_PATH="$SKNANO_LIB:${CONDA_PREFIX}/lib:$repo/external/lhapdf/redhat/lib:$correction_lib:${LD_LIBRARY_PATH:-}"
export LHAPDF_DATA_PATH="$repo/external/lhapdf/data"
export JSONPOG_REPO_PATH="$repo/CMS_corrections"
export ROCCOR_PATH="$repo/external/RoccoR"
export ROOT_HIST=0
exec python "$script_dir/nlo_direction_events.py" "$@"
