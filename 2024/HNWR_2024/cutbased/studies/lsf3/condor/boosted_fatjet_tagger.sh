#!/usr/bin/env bash
# boosted-candidate fatjet tagger scores (no LSF3 cut), signal points ("sig" <points>) or a background chunk ("bkg" <sample> <list>) (2026-09-15)
export CONDA_PREFIX=/data6/Users/achihwan/micromamba/envs/Nano15; export PATH=$CONDA_PREFIX/bin:$PATH
unset PYTHONPATH LD_LIBRARY_PATH ROOTSYS
S=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased/studies/lsf3
if [ "$1" = sig ]; then
  python $S/scripts/boosted_fatjet_tagger_hists.py --points "$2" --out $S/hists_boosted_sig --mt 4 2>&1 | grep -v "^Info in"
else
  python $S/scripts/boosted_fatjet_tagger_hists.py --sample "$2" --file-list "$3" --out $S/hists_boosted_bkg --mt 4 2>&1 | grep -v "^Info in"
fi
