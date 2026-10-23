#!/usr/bin/env bash
# Plot input sets for the new DY correction (per-GenJet FxFx/LO C + its R, userflag ZptNJet):
# everything except DY is a symlink into the existing production, DY is a symlink to the 2026-09-22
# DY-only re-production (flags RFlav,DYCRCharge,SRChargeSplit,ZptNJet = superset of the three).
# 2026-09-24: W+jets = HT-binned set only and VVV added (no skim -> no Skim_HNWR_ prefix;
# plot/cutbased/config.py UNPREFIXED_GLOBS takes them, DROP_GLOBS drops the mass-binned set).
#   W+jets HT: the 2026-09-24 superset re-production (flags RFlav,DYCRCharge,SRChargeSplit,ZptNJet, in NEWDY),
#              so the sig_chargesign plots stack W+jets too. (The card chain cbv15dc_ht still uses the
#              2026-09-11 RFlav,DYCRCharge files, which carry the same card histograms.)
#   VVV      : the superset production in NEWDY.
set -euo pipefail
NEWDY=/gv0/Users/achihwan/SKNanoOutput_dynew/HNWR/RFlav_DYCRCharge_SRChargeSplit_ZptNJet/2024
B=/gv0/Users/achihwan/SKNanoOutput/HNWR
HTW=$NEWDY
for old in RFlav RFlav_DYCRCharge RFlav_SRChargeSplit_plot; do
    dst=$B/${old}_ZptNJet/2024; mkdir -p "$dst"; find "$dst" -maxdepth 1 -type l -delete
    n=0
    for f in "$B/$old/2024"/*.root; do
        case "$(basename "$f")" in Skim_HNWR_DYto2L*|WtoLNu_MLNu*_HT*|WWW.root|WWZ.root|WZZ.root|ZZZ.root) continue ;; esac
        ln -s "$(readlink -f "$f")" "$dst/$(basename "$f")"; n=$((n+1))
    done
    m=0; for f in "$NEWDY"/Skim_HNWR_DYto2L*.root; do ln -s "$f" "$dst/$(basename "$f")"; m=$((m+1)); done
    k=0; for f in "$HTW"/WtoLNu_MLNu*_HT*.root "$NEWDY"/{WWW,WWZ,WZZ,ZZZ}.root; do
        [ -f "$f" ] || { echo "missing $f" >&2; exit 1; }
        ln -s "$f" "$dst/$(basename "$f")"; k=$((k+1)); done
    echo "$dst: $n non-DY links + $m new DY links + $k W+jets(HT)/VVV links"
done
