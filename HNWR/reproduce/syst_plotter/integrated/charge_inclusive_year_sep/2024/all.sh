#!/usr/bin/env bash
# Run all 2024 plotters locally (condor 대신 수동 실행용)
BASE="/data6/Users/achihwan/SKNanoAnalyzer-v13/plots/HNWR/reproduce/syst_plotter/integrated/charge_inclusive_year_sep/2024"
for d in Boost/DY Boost/FLV Boost/sig Resolve/DY Resolve/FLV Resolve/sig; do
    cd "${BASE}/${d}"
    rm -rf ./signal/*.tsv
    bash plotter.sh
done
