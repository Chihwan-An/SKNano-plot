#!/usr/bin/env bash
# Condor wrapper: runs lhe_precompute.py inside Singularity + micromamba Nano env
# Usage: wrapper_lhe.sh <WR> <N>

WR="$1"
N="$2"

SINGULARITY_IMAGE="/data6/Users/achihwan/private-el9.sif"
MAMBA_EXE="/data6/Users/achihwan/.local/bin/micromamba"
MAMBA_ROOT="/data6/Users/achihwan/micromamba"
MAMBA_ENV="Nano"
WORKER="/data6/Users/achihwan/SKNanoAnalyzer-v13/plots/HNWR/singnal_sample/Offshell_test/lhe_precompute.py"

echo "=== WR${WR} N${N} | $(date) ==="

singularity exec \
    --bind /data6:/data6,/home/achihwan:/home/achihwan,/gv0:/gv0 \
    "${SINGULARITY_IMAGE}" bash -c "
    export MAMBA_EXE=\"${MAMBA_EXE}\"
    export MAMBA_ROOT_PREFIX=\"${MAMBA_ROOT}\"
    eval \"\$(${MAMBA_EXE} shell hook -s bash)\"
    micromamba activate ${MAMBA_ENV}

    echo \"Python: \$(which python3)\"
    python3 ${WORKER} --wr ${WR} --n ${N}
"
EXIT_CODE=$?

echo "=== Exit code: ${EXIT_CODE} | $(date) ==="
exit ${EXIT_CODE}
