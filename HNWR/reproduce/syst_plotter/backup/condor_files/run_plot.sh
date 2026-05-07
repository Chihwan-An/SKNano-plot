#!/usr/bin/env bash
# Wrapper script for running a year's all.sh in condor job
# Working directory is set via condor initialdir

SINGULARITY_IMAGE="/data6/Users/achihwan/private-el9.sif"
WORK_DIR="$(pwd)"

MAMBA_EXE="/data6/Users/achihwan/.local/bin/micromamba"
MAMBA_ROOT="/data6/Users/achihwan/micromamba"
MAMBA_ENV="Nano"

echo "=== Running plot in: ${WORK_DIR} ==="
echo "=== Start time: $(date) ==="

singularity exec --bind /data6:/data6,/home/achihwan:/home/achihwan,/gv0:/gv0 "${SINGULARITY_IMAGE}" bash -c "
    export MAMBA_EXE=\"${MAMBA_EXE}\"
    export MAMBA_ROOT_PREFIX=\"${MAMBA_ROOT}\"
    eval \"\$(${MAMBA_EXE} shell hook -s bash)\"
    micromamba activate ${MAMBA_ENV}

    echo \"Python: \$(which python)\"
    echo \"ROOT: \$(which root)\"

    cd ${WORK_DIR}
    bash all.sh
"
EXIT_CODE=$?

echo "=== End time: $(date) ==="
echo "=== Exit code: ${EXIT_CODE} ==="

exit ${EXIT_CODE}
