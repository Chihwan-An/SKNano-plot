#!/usr/bin/env bash
# Run all plotter.sh scripts in ht_binned_tight_charge subdirectories
# NOTE: Run with "bash all.sh" or "source setup.sh" first for ROOT

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check ROOT is available
python -c "import ROOT" 2>/dev/null || { echo "ERROR: ROOT not found. Run 'source setup.sh' first."; return 1 2>/dev/null || exit 1; }

PLOTTERS=(
    "boost/DY"
    "boost/FLV"
    "boost/sr"
    "resolve/DY"
    "resolve/FLV"
    "resolve/sr"
)

for dir in "${PLOTTERS[@]}"; do
    full_path="${SCRIPT_DIR}/${dir}"
    if [ -f "${full_path}/plotter.sh" ]; then
        echo "=========================================="
        echo ">> Running: ${dir}/plotter.sh"
        echo "=========================================="
        (cd "${full_path}" && bash plotter.sh)
        echo ""
    else
        echo "!! WARNING: ${dir}/plotter.sh not found, skipping"
    fi
done

echo "=========================================="
echo ">> All plotters finished."
echo "=========================================="
