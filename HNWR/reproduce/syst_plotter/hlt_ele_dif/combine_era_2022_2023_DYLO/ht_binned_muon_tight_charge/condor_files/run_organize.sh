#!/usr/bin/env bash
# Wrapper script for running organize_files.py after all plotters complete
# Usage: run_organize.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$(dirname "${SCRIPT_DIR}")"  # Parent of condor_files (ht_binned_tight_charge)
SKNANO_DIR="/data6/Users/achihwan/SKNanoAnalyzer-v13"
SINGULARITY_IMAGE="/data6/Users/achihwan/private-el9.sif"

# Micromamba settings
MAMBA_EXE="/data6/Users/achihwan/.local/bin/micromamba"
MAMBA_ROOT="/data6/Users/achihwan/micromamba"
MAMBA_ENV="Nano"

echo "=== Running organize_files.py ==="
echo "=== Start time: $(date) ==="

# Run inside singularity container with micromamba
singularity exec --bind /data6:/data6,/home/achihwan:/home/achihwan,/gv0:/gv0 "${SINGULARITY_IMAGE}" bash -c "
    # Setup micromamba (setup.sh 없이)
    export MAMBA_EXE=\"${MAMBA_EXE}\"
    export MAMBA_ROOT_PREFIX=\"${MAMBA_ROOT}\"
    eval \"\$(${MAMBA_EXE} shell hook -s bash)\"
    micromamba activate ${MAMBA_ENV}

    echo \"Python: \$(which python)\"

    cd ${WORK_DIR}
    python organize_files.py
"
EXIT_CODE=$?

echo "=== End time: $(date) ==="
echo "=== Exit code: ${EXIT_CODE} ==="

exit ${EXIT_CODE}
