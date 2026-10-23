#!/usr/bin/env bash
# npz-based families of plot/HNWR_2024/cutbased/out redrawn with the new DY correction (dumps_dynew + new flip jsons):
# out/Resolve/DY/EE/<obj>/SS_flip_an3*, out/Resolve/sig/EE/<obj>/SS_flip_an3, out/Resolve/sig_chargesign/EE/other/{SSpp,SSmm,OSleadP,OSleadM}
set -uo pipefail
A=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers; T=$A/BDT/SR/test; PC=$A/plot/HNWR_2024/cutbased
N=$PC/studies/chargeflip/new_DYCR; D=$T/data/chargeflip/dumps_dynew; J3=$N/json/ptshift_LO_dynew.json; JR=$N/json/ptshift_LO_dynew_sf3roofit.json
cd $PC; C=./condor/in_container.sh
DE=$T/data/chargeflip/dumps_dynew_ee     # dumps_dynew without the muon data / mumu signal (the apply script loads every column of every file)
ap() { echo "=== apply $*"; $C python3 chargeflip_apply_plots.py --dumps $DE "$@" 2>&1 | grep -v "^Info in" | tail -4; }
ap --json $J3 --folder SS_flip_an3
ap --json $J3 --folder SS_flip_an3count
ap --json $JR --folder SS_flip_an3roofit --ymin 0.1
ap --json $JR --folder SS_flip_an3roofit --keep-tt --only '^(mlljj|dilepton_mass)$'
ap --json $JR --folder SS_flip_an3roofit --mlljj-window 1600,2800 --extra-vars --ymin 0.1
ap --region SR --json $J3 --folder SS_flip_an3
echo "=== chargesign_mll"; $C python3 chargesign_mll_plots.py --dumps $D 2>&1 | grep -v "Info in" | tail -12
echo NPZ_FAMILIES_DONE
