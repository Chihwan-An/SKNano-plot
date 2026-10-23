#!/usr/bin/env bash
# condor job body without the scratch copy: for productions too big for the worker scratch (RFlav_DYCRCharge = 17 GB
# -> "cgroup memory limit" hold when copied). Reads /gv0 directly, --skip-existing so a restart continues.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JOB="${1:?usage: run_specs_nocopy.sh <job name> [extra args...]}"; shift || true
echo "=== job ${JOB} (no copy) ==="; echo "=== start $(date) ==="
"${HERE}/in_container.sh" python run_specs.py "${JOB}" --skip-existing "$@"
EXIT=$?; echo "=== end $(date) ==="; echo "=== exit ${EXIT} ==="; exit ${EXIT}
