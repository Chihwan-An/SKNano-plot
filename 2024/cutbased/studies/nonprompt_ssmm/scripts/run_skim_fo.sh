#!/usr/bin/env bash
# condor wrapper: skim_fo.py for one HNWR FOMode MC sample from its per-job outputs.  args: <sample>
set -uo pipefail
ST=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/studies/nonprompt_ssmm
RL1=/gv0/Users/achihwan/SKNanoRunlog/2026_09_24_001016_HNWR_FOMode_RFlav/2024
RL2=/gv0/Users/achihwan/SKNanoRunlog/2026_09_24_031413_HNWR_FOMode_RFlav/2024   # QCD + signals (after both LHE guards)
RL4=/gv0/Users/achihwan/SKNanoRunlog/2026_09_24_040510_HNWR_FOMode_RFlav/2024   # the 6 signals, run on their own
rl() { if [ -d "$RL4/$1" ]; then echo "$RL4"; elif [ -d "$RL2/$1" ]; then echo "$RL2"; else echo "$RL1"; fi; }
case "$1" in *EGamma*|*Muon0*|*Muon1*) echo "refusing data sample $1"; exit 2;; esac
MERGED=/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/FOMode_RFlav/2024/$1.root
if [ "$(rl $1)" != "$RL1" ] && [ -f "$MERGED" ]; then   # part-2 samples are hadded per sample as they finish
  exec /data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/condor/in_container.sh \
    python3 $ST/scripts/skim_fo.py --file "$MERGED" --out "$ST/skim/hnwr_fo/$1.npz"
fi
exec /data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/condor/in_container.sh \
  python3 $ST/scripts/skim_fo.py --glob "$(rl $1)/$1/output/hists_*.root" --out "$ST/skim/hnwr_fo/$1.npz"
