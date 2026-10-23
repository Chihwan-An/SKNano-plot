#!/usr/bin/env bash
# condor wrapper: skim_trees.py for one sample.  args: <indir> <sample> <trees> <outdir>
set -uo pipefail
ST=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/studies/nonprompt_ssmm
case "$2" in EGamma*|Muon*) echo "refusing data sample $2"; exit 2;; esac
exec /data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/condor/in_container.sh \
  python3 $ST/scripts/skim_trees.py --file "$1/$2.root" --trees "$3" --out "$4/$2.npz"
