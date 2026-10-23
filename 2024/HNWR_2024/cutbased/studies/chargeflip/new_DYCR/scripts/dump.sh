#!/usr/bin/env bash
# dump one HNWR_ChargeFlip production to npz:  dump.sh <production dir> <output dir>
export CONDA_PREFIX=/data6/Users/achihwan/micromamba/envs/Nano15; export PATH=$CONDA_PREFIX/bin:$PATH
micromamba() { :; }; export __MAMBA_SETUP_DONE=1
cd /data9/Users/achihwan/nano15/SKNanoAnalyzer && source setup.sh >/dev/null 2>&1
T=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test
mkdir -p "$2"
python3 $T/scripts/chargeflip_tree_dump.py --in "$1" --out "$2" --jobs 8
echo DUMP_DONE "$2"
