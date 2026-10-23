#!/usr/bin/env bash
# GlobalParT3 XWWqqev / XWWqqmv of the boosted-candidate fatjet in the W_R signal skims, one chunk of mass points (2026-09-15)
export CONDA_PREFIX=/data6/Users/achihwan/micromamba/envs/Nano15; export PATH=$CONDA_PREFIX/bin:$PATH
unset PYTHONPATH LD_LIBRARY_PATH ROOTSYS
S=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased/studies/lsf3
python $S/scripts/fatjet_tagger_hists.py --points "$1" --out $S/hists_fatjet_taggers --mt 4 2>&1 | grep -v "^Info in"
