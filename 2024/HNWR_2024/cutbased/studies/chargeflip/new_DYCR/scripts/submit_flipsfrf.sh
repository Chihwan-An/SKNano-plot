#!/usr/bin/env bash
# 2026-09-30: HNWR MC rerun with the RooFit flip SF (FlipSF + FlipSFEM). Run on tamsa2.
export CONDA_PREFIX=/data6/Users/achihwan/micromamba/envs/Nano15; export PATH=$CONDA_PREFIX/bin:$PATH
micromamba() { :; }; export __MAMBA_SETUP_DONE=1
cd /data9/Users/achihwan/nano15/SKNanoAnalyzer && source setup.sh
export SKNANO_OUTPUT=/gv0/Users/achihwan/SKNanoOutput_flipsfroofit
python/SKNano.py -a HNWR -i Nano15_Analyzers/HNWR/samplelists/hnwr_flipsfrf_mc_2024.txt -e 2024 -n -1 --nmax 100 --memory 8192 \
  --userflags RFlav,DYCRCharge,SRChargeSplit,ZptNJet,FlipSF,FlipSFEM --batchname HNWR_flipsfrf
