#!/usr/bin/env bash
# The six DY-correction stages of plots/datamc_stages/{stage1_C,stage2_C_x_EW} redrawn one stage per
# figure in the cutbased plotter format (stacked DY/TT/Nonprompt/Others + data + ratio), into
# plots/datamc_stages/<stage folder>/cutbased_format/.
#
# The overlay figures put every stage in one frame as a total-MC line; here the stack needs a single
# DY, so each stage gets its own file. The stage is the __DY-<tag> part of the name and the second
# half of the first label line; the yields of the overlay's yields_2024.json are reproduced exactly
# (same productions, same histograms, same binning).
#
#   ./run_stages_cutbased_format.sh                  # both folders
#   ./run_stages_cutbased_format.sh stage2_C_x_EW    # one of them
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STUDY="$(dirname "$HERE")"
PC="$(cd "$STUDY/../../.." && pwd)"                       # plot/cutbased
DYBASE=/gv0/Users/achihwan/SKNanoOutput_dy3gen/HNWR
NODY="$DYBASE/DYCRSplit_NoDYCorr_WeightSystOnly/2024"     # data, non-DY MC, and the uncorrected DY

# stage tag : production under $DYBASE : DY kind : twin marker : label on the plot
# The C-variant productions all carry DYCR_{NoCorr,COnly,ZptOnly,Full} twins (HNWR.cc: COnly = C,
# ZptOnly = C x EW, Full = C x EW x R); the stage folder picks which twin is read, so the same six
# rows serve both folders.
STAGES=(
  "LO-nocorr|DYCRSplit_NoDYCorr_WeightSystOnly|LO|@|LO, no corr."
  "LO-C-powheg|DYCRStudy_DYCRSplit_ZptOnly_WeightSystOnly|LO|#|LO #times C shipped (powheg, incl.)"
  "LO-C-FxFx-incl|DYCRStudy_DYCRSplit_ZptOnly_ZptFxFxIncl_WeightSystOnly|LO|#|LO #times C FxFx incl."
  "LO-C-FxFx-perjet-shape|DYCRStudy_DYCRSplit_ZptOnly_ZptNJet_WeightSystOnly|LO|#|LO #times C FxFx per-jet (shape)"
  "LO-C-FxFx-perjet-abs|DYCRStudy_DYCRSplit_ZptOnly_ZptNJetAbs_WeightSystOnly|LO|#|LO #times C FxFx per-jet (abs)"
  "FxFx-direct|DYCRSplit_NoDYCorr_WeightSystOnly|FxFx|@|FxFx direct"
)

# output folder : DYCR_<twin> the folder's stage reads
FOLDERS=("stage1_C|COnly" "stage2_C_x_EW|ZptOnly")

WANT=("$@")
for entry in "${FOLDERS[@]}"; do
    IFS='|' read -r folder twin <<< "$entry"
    if [ ${#WANT[@]} -gt 0 ] && [[ " ${WANT[*]} " != *" $folder "* ]]; then continue; fi
    out="$STUDY/plots/datamc_stages/${folder}/cutbased_format"
    args=()
    for row in "${STAGES[@]}"; do
        IFS='|' read -r tag prod kind marker label <<< "$row"
        # '@' = no correction anywhere in the file, so the plain Central; '#' = the stage's twin.
        [ "$marker" = "@" ] && hdir="Central" || hdir="DYCR_${twin}/Central"
        args+=(--dy "${tag}=${DYBASE}/${prod}/2024:${kind}:${hdir}:${label}")
    done
    echo "=== ${folder} (DYCR_${twin}) -> ${out}"
    (cd "$PC" && ./condor/in_container.sh python3 \
        studies/DY/09_three_generators/scripts/draw_datamc_cutbased_format.py \
        --preset resolved1D --nondy-base "$NODY" --out "$out" "${args[@]}")
done
