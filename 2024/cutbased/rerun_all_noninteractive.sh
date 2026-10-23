#!/usr/bin/env bash
# Non-interactive full re-plot: wipe out/ + condor logs/dag, then check inputs, build DAG and submit
# (run on a condor submit node, e.g. tamsa2). Used for the 2026-08-28 RFlav refresh.
set -uo pipefail
BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$BASE"
rm -rf out/* condor/logs/*; rm -f condor/*.dag.*
./submit.sh "$@" < /dev/null
