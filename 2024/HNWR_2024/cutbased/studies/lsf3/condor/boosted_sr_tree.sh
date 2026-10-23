#!/usr/bin/env bash
# boosted SR tagger tree, one background chunk: <sample> <file list> <output stem>   (2026-09-17)
export CONDA_PREFIX=/data6/Users/achihwan/micromamba/envs/Nano15; export PATH=$CONDA_PREFIX/bin:$PATH
unset PYTHONPATH LD_LIBRARY_PATH ROOTSYS
S=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased/studies/lsf3
python $S/scripts/boosted_sr_tagger_tree.py --sample "$1" --file-list "$2" --name "$3" \
       --skim-tag HNWR --out $S/trees_boosted_bkg_full --mt 4 2>&1 | grep -v "^Info in"
