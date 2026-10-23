#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLOTTER="${SCRIPT_DIR}/atlas_plotter.py"
DATA_PATH="${DATA_PATH:-/gv0/Users/achihwan/SKNanoOutput/atlas/2023}"
OUTDIR="${OUTDIR:-${SCRIPT_DIR}/output}"
SIGNALS="${SIGNALS:-WR2000N1100,WR4000N2100}"

python -c "import ROOT" 2>/dev/null || {
  echo "ERROR: ROOT is not available in this shell."
  exit 1
}

run_plot() {
  local hist="$1"
  local output="$2"
  local xlabel="$3"
  local xmin="$4"
  local xmax="$5"
  local bins="${6:-}"
  local extra_bins=()
  if [[ -n "${bins}" ]]; then
    extra_bins=(--bins "${bins}")
  fi
  python "${PLOTTER}" \
    --data-path "${DATA_PATH}" \
    --hist "${hist}" \
    --output-dir "${OUTDIR}" \
    --output "${output}" \
    --xlabel "${xlabel}" \
    --xmin "${xmin}" \
    --xmax "${xmax}" \
    --signals "${SIGNALS}" \
    --signal-scale 1.0 \
    --rmin 0.0 \
    --rmax 2.0 \
    "${extra_bins[@]}"
}

# Resolved SR/CR
run_plot "Resolved/rSROS2e/mlljj"       "resolved_rSROS2e_mlljj"       "m(lljj) [GeV]" 800 8000 "800,1000,1200,1400,1600,2000,2400,2800,3200,8000"
run_plot "Resolved/rSROS2mu/mlljj"      "resolved_rSROS2mu_mlljj"      "m(lljj) [GeV]" 800 8000 "800,1000,1200,1400,1600,2000,2400,2800,3200,8000"
run_plot "Resolved/rCROS2e/mll"         "resolved_rCROS2e_mll"         "m(ll) [GeV]"     0  300
run_plot "Resolved/rCROS2mu/mll"        "resolved_rCROS2mu_mll"        "m(ll) [GeV]"     0  300
run_plot "Resolved/rCROSemu/mlljj"      "resolved_rCROSemu_mlljj"      "m(lljj) [GeV]" 800 8000 "800,1000,1200,1400,1600,2000,2400,2800,3200,8000"

# Boosted SR/CR
run_plot "Boosted/bSR2e/mWR"            "boosted_bSR2e_mWR"            "m(lJ) [GeV]"   800 8000 "800,1000,1200,1400,1600,2000,2400,2800,3200,8000"
run_plot "Boosted/bSR2mu/mWR"           "boosted_bSR2mu_mWR"           "m(lJ) [GeV]"   800 8000 "800,1000,1200,1400,1600,2000,2400,2800,3200,8000"
run_plot "Boosted/bCRZ2e/largeR_sdmass" "boosted_bCRZ2e_largeR_sdmass" "Large-R jet SD mass [GeV]" 0 250
run_plot "Boosted/bCRZ2mu/largeR_sdmass" "boosted_bCRZ2mu_largeR_sdmass" "Large-R jet SD mass [GeV]" 0 250

echo "Plots written to ${OUTDIR}"
