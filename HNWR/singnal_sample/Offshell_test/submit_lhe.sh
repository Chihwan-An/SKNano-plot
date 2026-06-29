#!/bin/bash
# Submit LHE precompute jobs + plot generation via HTCondor DAG.
# LHE jobs run in Singularity/Nano env on worker nodes.
# Plot job runs locally on submit node (hep-py-env) after all LHE jobs finish.
# Usage: bash submit_lhe.sh [--rerun]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CACHE_DIR="${SCRIPT_DIR}/lhe_cache"
LOG_DIR="${SCRIPT_DIR}/condor_logs/lhe"
WRAPPER="${SCRIPT_DIR}/wrapper_lhe.sh"
PYTHON_LOCAL="/home/achihwan/miniconda3/envs/hep-py-env/bin/python3"
PLOT_SCRIPT="${SCRIPT_DIR}/generate_plots.py"
PAIRS_FILE="${SCRIPT_DIR}/wr_n_pairs.txt"
LHE_SUB="${SCRIPT_DIR}/condor_lhe.sub"
PLOT_SUB="${SCRIPT_DIR}/condor_plot.sub"
DAG_FILE="${SCRIPT_DIR}/lhe_plot.dag"

RERUN=0
[[ "$1" == "--rerun" ]] && RERUN=1

mkdir -p "${CACHE_DIR}" "${LOG_DIR}"
chmod +x "${WRAPPER}"

# ── (WR, N) pairs ────────────────────────────────────────────────────────────
> "${PAIRS_FILE}"
for WR in 2000 4000 6000 8000; do
    N=100
    while [ $N -lt $WR ]; do
        CACHE_FILE="${CACHE_DIR}/WR${WR}_N${N}.npz"
        if [ "$RERUN" -eq 1 ] || [ ! -f "$CACHE_FILE" ]; then
            echo "${WR} ${N}" >> "${PAIRS_FILE}"
        fi
        N=$((N + 200))
    done
done

N_LHE=$(wc -l < "${PAIRS_FILE}")
if [ "$N_LHE" -eq 0 ]; then
    echo "All LHE cache files exist. Running plot generation only..."
    "${PYTHON_LOCAL}" "${PLOT_SCRIPT}"
    exit $?
fi
echo "Submitting ${N_LHE} LHE jobs + 1 plot job via DAG..."

# ── LHE submit file ──────────────────────────────────────────────────────────
cat > "${LHE_SUB}" << EOF
universe              = vanilla
executable            = ${WRAPPER}
arguments             = \$(WR) \$(N)
initialdir            = ${SCRIPT_DIR}
output                = ${LOG_DIR}/WR\$(WR)_N\$(N).out
error                 = ${LOG_DIR}/WR\$(WR)_N\$(N).err
log                   = ${LOG_DIR}/condor.log
should_transfer_files = NO
request_memory        = 3GB
request_cpus          = 1
notification          = Never
queue WR,N from ${PAIRS_FILE}
EOF

# ── Plot submit file (universe=local → runs on submit node) ──────────────────
cat > "${PLOT_SUB}" << EOF
universe              = local
executable            = ${PYTHON_LOCAL}
arguments             = ${PLOT_SCRIPT}
initialdir            = ${SCRIPT_DIR}
output                = ${LOG_DIR}/plot.out
error                 = ${LOG_DIR}/plot.err
log                   = ${LOG_DIR}/condor.log
notification          = Never
queue
EOF

# ── DAG file ─────────────────────────────────────────────────────────────────
> "${DAG_FILE}"

# One JOB node per (WR, N)
JOB_NAMES=""
while read -r WR N; do
    JOB="lhe_WR${WR}_N${N}"
    echo "JOB    ${JOB} ${LHE_SUB}"   >> "${DAG_FILE}"
    echo "VARS   ${JOB} WR=\"${WR}\" N=\"${N}\"" >> "${DAG_FILE}"
    JOB_NAMES="${JOB_NAMES} ${JOB}"
done < "${PAIRS_FILE}"

# Plot job as FINAL node (runs after all jobs complete, success or fail)
echo ""                                >> "${DAG_FILE}"
echo "FINAL  plot_job ${PLOT_SUB}"     >> "${DAG_FILE}"

condor_submit_dag "${DAG_FILE}"
echo ""
echo "Monitor:  condor_q \$USER"
echo "LHE logs: ${LOG_DIR}/WR*.out"
echo "Plot log: ${LOG_DIR}/plot.out"
echo "PNGs out: ${SCRIPT_DIR}/WR*_MM_lhe_vs_reco_stacked.png"
