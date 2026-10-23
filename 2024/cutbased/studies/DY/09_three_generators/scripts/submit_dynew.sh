#!/usr/bin/env bash
# 2026-09-22: DY-only re-productions with the per-GenJet FxFx/LO C (userflag ZptNJet) and its R.
# Run on tamsa2. Everything that does not depend on the DY correction (data, non-DY MC, signal) is
# NOT re-run: the plot input sets symlink those from the existing productions (make_dynew_plotsets.sh).
#   ./submit_dynew.sh hnwr|check|cf|cffxfx
export CONDA_PREFIX=/data6/Users/achihwan/micromamba/envs/Nano15; export PATH=$CONDA_PREFIX/bin:$PATH
micromamba() { :; }; export __MAMBA_SETUP_DONE=1
cd /data9/Users/achihwan/nano15/SKNanoAnalyzer && source setup.sh >/dev/null 2>&1
export SKNANO_OUTPUT=/gv0/Users/achihwan/SKNanoOutput_dynew
L=Nano15_Analyzers/HNWR/samplelists
case "$1" in
  hnwr)   python/SKNano.py -a HNWR -i $L/dycrsplit_lo_2024.txt -e 2024 -n -1 --nmax 400 --memory 8192 \
            --userflags RFlav,DYCRCharge,SRChargeSplit,ZptNJet --batchname HNWR_dynew ;;
  check)  python/SKNano.py -a HNWR -i $L/dy_driftcheck_2024.txt -e 2024 -n -1 --nmax 100 --memory 8192 \
            --userflags RFlav,DYCRCharge,SRChargeSplit --batchname HNWR_dycheck ;;
  cf)     python/SKNano.py -a HNWR_ChargeFlip -i $L/chargeflip_dy_2024.txt -e 2024 -n 20 --nmax 100 --memory 4096 \
            --userflags RFlav,ZptNJet --batchname cfdynew ;;
  cffxfx) python/SKNano.py -a HNWR_ChargeFlip -i Nano15_Analyzers/HNWR/scripts/DYGenZpT_2024_FxFx.txt -e 2024 -n 400 --nmax 400 --memory 4096 \
            --userflags RFlav --batchname cffxfx ;;
  *) echo "usage: $0 hnwr|check|cf|cffxfx"; exit 1 ;;
esac
