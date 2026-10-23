#!/usr/bin/env bash
# condor wrapper: skim_fo.py --allow-data on one data period of the FOMode,FOSB,RFlav production (SR sideband). args: <sample>
set -uo pipefail
ST=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased/studies/nonprompt_ssmm
RL=/gv0/Users/achihwan/SKNanoRunlog/2026_09_24_122235_HNWR_FOMode_FOSB_RFlav/2024
OUT=/gv0/Users/achihwan/SKNanoOutput_fodata/HNWR/FOMode_FOSB_RFlav/2024
case "$1" in *Muon*) ;; *) echo "FOSB skim is for Muon data only: $1"; exit 2;; esac
if [ -f $OUT/$1.root ] && [ -f $RL/$1/hadd.out ]; then set -- "$1" --file "$OUT/$1.root"; else set -- "$1" --glob "$RL/$1/output/hists_*.root"; fi
exec /data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased/condor/in_container.sh \
  python3 $ST/scripts/skim_fo.py --allow-data "$2" "$3" --out "$ST/skim/hnwr_fosb/$1.npz"
