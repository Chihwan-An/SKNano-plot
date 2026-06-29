#!/usr/bin/env bash
# Condor wrapper: run cutflow.py inside singularity+micromamba
# Args: $1=WR  $2=N  $3=OUTDIR

WR="$1"
N="$2"
OUTDIR="$3"

SCRIPT_DIR="/data6/Users/achihwan/SKNanoAnalyzer-v13/plots/HNWR/singnal_sample/cutflow"
SINGULARITY_IMAGE="/data6/Users/achihwan/private-el9.sif"
MAMBA_EXE="/data6/Users/achihwan/.local/bin/micromamba"
MAMBA_ROOT="/data6/Users/achihwan/micromamba"
MAMBA_ENV="Nano"

echo "=== cutflow job: WR=${WR} N=${N} ==="
echo "=== Start: $(date) ==="

singularity exec \
  --bind /data6:/data6,/home/achihwan:/home/achihwan,/gv0:/gv0 \
  "${SINGULARITY_IMAGE}" bash -c "
    export MAMBA_EXE='${MAMBA_EXE}'
    export MAMBA_ROOT_PREFIX='${MAMBA_ROOT}'
    eval \"\$(${MAMBA_EXE} shell hook -s bash)\"
    micromamba activate ${MAMBA_ENV}

    echo \"Python: \$(which python)\"
    python ${SCRIPT_DIR}/cutflow.py --wr ${WR} --n ${N} --outdir ${OUTDIR}
"

EXIT_CODE=$?
echo "=== End: $(date) ==="
echo "=== Exit code: ${EXIT_CODE} ==="
exit ${EXIT_CODE}
