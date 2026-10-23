#!/usr/bin/env bash
# Charge-flip chain with the new DY correction (per-GenJet FxFx/LO C + its R, userflag ZptNJet). 2026-09-22.
# Everything is written under new_DYCR/ (nothing of AN_rawcharge/ or BDT/SR/test/data is overwritten).
#   run_chain.sh linkdumps | rate | closure | lowmlljj
set -euo pipefail
A=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers
T=$A/BDT/SR/test; S=$A/plot/HNWR_2024/cutbased/studies/chargeflip; N=$S/new_DYCR; PC=$A/plot/HNWR_2024/cutbased
DUMPS=$T/data/chargeflip/dumps_dynew        # non-DY + data = links to dumps_boost, DY = dumps_dynew_dy (cfdynew production)
FXFX=$T/data/chargeflip/dumps_fxfx          # DYto2{E,Mu}_MLL50_FxFx (cffxfx production, w_dy = 1)
C="$PC/condor/in_container.sh"; cd $PC
mkdir -p $N/json $N/data $N/logs
case "$1" in
linkdumps)
    mkdir -p $DUMPS; find $DUMPS -maxdepth 1 -type l -delete
    for f in $T/data/chargeflip/dumps_boost/tree_*.npz; do
        case "$(basename $f)" in tree_Skim_HNWR_DYto2L*) continue ;; esac
        ln -s $f $DUMPS/$(basename $f); done
    for f in $T/data/chargeflip/dumps_dynew_dy/tree_*.npz; do ln -s $f $DUMPS/$(basename $f); done
    echo "$(ls $DUMPS | wc -l) dumps in $DUMPS ($(ls $DUMPS | grep -c DYto2L) DY)" ;;
rate)
    O=$N/01_rate_chi2_LO_vs_NLO; mkdir -p $O
    $C python3 $T/scripts/chargeflip_ptshift.py --dump $DUMPS --gencharge dr --out-json $N/json/ptshift_LO_dynew.json --out-md $O/ptshift_LO_dynew.md --plots $O/LO_dynew > $N/logs/rate_LO.log 2>&1
    $C python3 $T/scripts/chargeflip_ptshift.py --dump $FXFX  --gencharge dr --out-json $N/json/ptshift_NLO_fxfx.json --out-md $O/ptshift_NLO_fxfx.md --plots $O/NLO_fxfx > $N/logs/rate_NLO.log 2>&1
    $C python3 $N/scripts/compare_rate_chi2.py --lo $N/json/ptshift_LO_dynew.json --nlo $N/json/ptshift_NLO_fxfx.json \
        --old $T/data/chargeflip/chargeflip_ptshift_ee2024_sf3.json --out $O | tee $N/logs/rate_compare.log ;;
closure)
    J=$N/json/ptshift_LO_dynew.json
    $C python3 $S/scripts/jetbin_ss_dycr_closure.py --dumps $DUMPS --json $J --cache $N/data/jetbin_ss_dycr_events.npz --rebuild --out-dir $N/17_1jet_to_2jet_ss_dycr > $N/logs/closure17.log 2>&1
    $C python3 $S/scripts/osmc_flip_dycr_closure.py --cache $N/data/jetbin_ss_dycr_events.npz --json $J --region dycr --out-dir $N/18_osmc_flip_dycr > $N/logs/closure18.log 2>&1
    tail -25 $N/logs/closure18.log ;;
lowmlljj)
    J=$N/json/ptshift_LO_dynew.json
    $C python3 $S/scripts/lowmlljj_build.py --dumps $DUMPS --cache $N/data/lowmlljj_events.npz > $N/logs/lowmlljj_build_EE.log 2>&1
    $C python3 $S/scripts/lowmlljj_build.py --dumps $DUMPS --channel 13 --cache $N/data/lowmlljj_events_mm.npz > $N/logs/lowmlljj_build_MM.log 2>&1
    $C python3 $S/scripts/lowmlljj_datamc_plots.py --cache $N/data/lowmlljj_events.npz --out-dir $N/27_lowmlljj_datamc_mll400 > $N/logs/lowmlljj27_EE.log 2>&1
    $C python3 $S/scripts/lowmlljj_datamc_plots.py --channel 13 --cache $N/data/lowmlljj_events_mm.npz --out-dir $N/27_lowmlljj_datamc_mll400_MM > $N/logs/lowmlljj27_MM.log 2>&1
    $C python3 $S/scripts/osmc_flip_dycr_closure.py --region lowmlljj --cache $N/data/lowmlljj_events.npz --json $J --mll-min 400 --out-dir $N/25_lowmlljj_mll400 > $N/logs/lowmlljj25.log 2>&1
    tail -5 $N/logs/lowmlljj27_EE.log $N/logs/lowmlljj27_MM.log; tail -25 $N/logs/lowmlljj25.log ;;
lowmlljj60)
    # m_lljj < 800 over the whole 60 <= m_ll < 400 (Z window included): cache from 60, then the full range with fine
    # m_ll bins plus three slices, EE and MM, to see where data/MC departs from 1
    for ch in 11 13; do
        sfx=$([ $ch = 13 ] && echo _mm || echo); CH=$([ $ch = 13 ] && echo _MM || echo)
        $C python3 $S/scripts/lowmlljj_build.py --dumps $DUMPS --channel $ch --mll-min 60 --cache $N/data/lowmlljj_mll60_events$sfx.npz > $N/logs/lowmlljj60_build$CH.log 2>&1
        for r in "60 400" "60 150" "150 200" "200 400"; do set -- $r
            $C python3 $S/scripts/lowmlljj_datamc_plots.py --channel $ch --cache $N/data/lowmlljj_mll60_events$sfx.npz --mll-min $1 --mll-max $2 \
                --out-dir $N/28_lowmlljj_datamc_mll${1}to${2}$CH > $N/logs/lowmlljj28_${1}to${2}$CH.log 2>&1
            echo "== $CH $1-$2"; grep -E "^(OS|SS|Inclusive):" $N/logs/lowmlljj28_${1}to${2}$CH.log
        done
    done ;;
*) echo "usage: $0 linkdumps|rate|closure|lowmlljj|lowmlljj60"; exit 1 ;;
esac
