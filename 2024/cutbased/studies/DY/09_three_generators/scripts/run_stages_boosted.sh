#!/usr/bin/env bash
# Boosted DY CR version of plots/datamc_stages: the three correction stages (C, C x EW, C x EW x R) as
# overlay figures (make_dy_cr_datamc.py) and in the cutbased plotter format, into
# plots/datamc_stages/<stage>/boosted/[cutbased_format/].
#
# All three twins (DYCR_COnly, DYCR_ZptOnly, DYCR_Full) are read from the RFlav productions: C and
# C x EW do not depend on R, so they equal the ZptOnly productions' twins used for the resolved stages.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STUDY="$(dirname "$HERE")"
PC="$(cd "$STUDY/../../.." && pwd)"                       # plot/cutbased
REPO="$(cd "$PC/../.." && pwd)"
B=/gv0/Users/achihwan/SKNanoOutput_dy3gen/HNWR
NODY="$B/DYCRSplit_NoDYCorr_WeightSystOnly/2024"
P=DYCRStudy_DYCRSplit_RFlav

# tag | production | DY kind | '@' uncorrected (Central) or '#' stage twin | overlay label | plotter label
ROWS=(
  "LO-nocorr|DYCRSplit_NoDYCorr_WeightSystOnly|LO|@|LO no corr.|LO, no corr."
  "LO-C-powheg|${P}_WeightSystOnly|LO|#|LO x C shipped|LO #times C shipped (powheg)"
  "LO-C-FxFx-incl|${P}_ZptFxFxIncl_WeightSystOnly|LO|#|LO x C FxFx incl|LO #times C FxFx incl."
  "LO-C-FxFx-perjet-shape|${P}_ZptNJet_WeightSystOnly|LO|#|LO x C FxFx per-jet shape|LO #times C FxFx per-jet (shape)"
  "LO-C-FxFx-perjet-abs|${P}_ZptNJetAbs_WeightSystOnly|LO|#|LO x C FxFx per-jet abs|LO #times C FxFx per-jet (abs)"
  "FxFx-direct|DYCRSplit_NoDYCorr_WeightSystOnly|FxFx|@|FxFx direct|FxFx direct"
)
for entry in "stage1_C|COnly" "stage2_C_x_EW|ZptOnly" "stage3_C_x_EW_x_R|Full"; do
    IFS='|' read -r folder twin <<< "$entry"
    out="$STUDY/plots/datamc_stages/${folder}/boosted"
    ov=(); cb=()
    for row in "${ROWS[@]}"; do
        IFS='|' read -r tag prod kind marker olab plab <<< "$row"
        [ "$marker" = "@" ] && hdir="Central" || hdir="DYCR_${twin}/Central"
        ov+=(--dy "${olab}=${B}/${prod}/2024:${kind}:${hdir}")
        cb+=(--dy "${tag}=${B}/${prod}/2024:${kind}:${hdir}:${plab}")
    done
    echo "=== ${folder} (DYCR_${twin}) overlay -> ${out}"
    (cd "$REPO" && python3 HNWR/scripts/make_dy_cr_datamc.py --nondy-base "$NODY" --regions Boosted --out "$out" "${ov[@]}")
    echo "=== ${folder} cutbased format"
    (cd "$PC" && ./condor/in_container.sh python3 studies/DY/09_three_generators/scripts/draw_datamc_cutbased_format.py \
        --preset boosted1D --nondy-base "$NODY" --out "$out/cutbased_format" "${cb[@]}")
done
