#!/usr/bin/env bash
# condor wrapper: skim_fo.py --allow-data on one sample of the FOMode,FODYCR,RFlav production (DY CR window). args: <sample>
set -uo pipefail
ST=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased/studies/nonprompt_ssmm
source $ST/scripts/fodycr_paths.sh
case "$1" in *EGamma*) echo "refusing EGamma sample $1"; exit 2;; esac
read -r kind src <<< "$(fo_src $1)"
[ -n "${kind:-}" ] || { echo "sample $1 not complete"; exit 3; }
exec /data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased/condor/in_container.sh \
  python3 $ST/scripts/skim_fo.py --allow-data --$kind "$src" --out "$ST/skim/hnwr_fodycr/$1.npz"
