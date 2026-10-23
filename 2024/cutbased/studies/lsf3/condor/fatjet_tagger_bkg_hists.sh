#!/usr/bin/env bash
# max GlobalParT3 XWWqqev / XWWqqmv over LSF3 > 0.75 fatjets in DY / TT 2L / tW 2L skims, one file chunk (2026-09-15)
export CONDA_PREFIX=/data6/Users/achihwan/micromamba/envs/Nano15; export PATH=$CONDA_PREFIX/bin:$PATH
unset PYTHONPATH LD_LIBRARY_PATH ROOTSYS
S=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/studies/lsf3
python $S/scripts/fatjet_tagger_bkg_hists.py --sample "$1" --file-list "$2" --out $S/hists_fatjet_taggers_bkg --mt 4 2>&1 | grep -v "^Info in"
