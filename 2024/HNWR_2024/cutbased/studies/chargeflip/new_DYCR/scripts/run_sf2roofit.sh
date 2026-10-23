#!/usr/bin/env bash
# 2026-09-30: rerun the DY-CR / low-mlljj flip checks with the nominal two-region RooFit SF (AN: sideband count removed).
# Outputs only under new_DYCR/29_sf2roofit/ (and ttbar/07_ss_dyonly_flip/*_merge1000*); json P above 1 TeV = 400-1000 bin.
set -euo pipefail
A=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers
T=$A/BDT/SR/test; S=$A/plot/HNWR_2024/cutbased/studies/chargeflip; N=$S/new_DYCR; PC=$A/plot/HNWR_2024/cutbased
C="$PC/condor/in_container.sh"; cd $PC
J=$N/json/ptshift_LO_dynew_sf2roofit.json; O=$N/29_sf2roofit; mkdir -p $O
case "$1" in
dycrcheck) $C python3 $T/scripts/chargeflip_dycr_check.py --json $J --dumps $T/data/chargeflip/dumps_dynew_ee --out-md $O/dycr_check.md ;;
osmc)      $C python3 $S/scripts/osmc_flip_dycr_closure.py --cache $N/data/jetbin_ss_dycr_events.npz --json $J --region dycr --out-dir $O/18_osmc_flip_dycr ;;
low400)    $C python3 $S/scripts/osmc_flip_dycr_closure.py --region lowmlljj --cache $N/data/lowmlljj_events.npz --json $J --mll-min 400 --out-dir $O/25_lowmlljj_mll400 ;;
low200)    $C python3 $S/scripts/osmc_flip_dycr_closure.py --region lowmlljj --cache $N/data/lowmlljj_events.npz --json $J --mll-min 200 --mll-max 400 --out-dir $O/25_lowmlljj_mll200to400 ;;
ddss)      H=$A/plot/HNWR_2024/cutbased/studies/ttbar/07_ss_dyonly_flip  # card template (v3_ss3200 edges), flip rate above 1 TeV = 400-1000 bin
           cd $T; $C python3 $H/chargeflip_ddss_dyonly.py --dumps $T/data/chargeflip/dumps_v4/all --json $T/data/chargeflip/chargeflip_ptshift_ee2024_sf3roofit_merge1000.json \
             --sf2 --dy-only --sr-edges 800,1000,1200,1400,1600,2000,2400,2800,3200,8000 --out $H/ddss_dyonly_sf_ss3200_merge1000.root > $H/log_dyonly_sf_ss3200_merge1000.txt 2>&1 ;;
ddssosmc)  H=$A/plot/HNWR_2024/cutbased/studies/ttbar/07_ss_dyonly_flip  # same as ddss but the OS MC replaces the OS data (--os-mc)
           $C python3 $H/chargeflip_ddss_dyonly.py --dumps $T/data/chargeflip/dumps_v4/all --json $T/data/chargeflip/chargeflip_ptshift_ee2024_sf3roofit_merge1000.json \
             --sf2 --dy-only --os-mc --sr-edges 800,1000,1200,1400,1600,2000,2400,2800,3200,8000 --out $H/ddss_dyonly_sf_ss3200_merge1000_osmc.root > $H/log_dyonly_sf_ss3200_merge1000_osmc.txt 2>&1 ;;
srclos)    H=$A/plot/HNWR_2024/cutbased/studies/ttbar/07_ss_dyonly_flip  # flip-weight closure on MC in SR / SS DY CR (SF = 1)
           $C python3 $H/osmc_sr_closure.py --dumps $T/data/chargeflip/dumps_v4/all --json $T/data/chargeflip/chargeflip_ptshift_ee2024_sf3roofit_merge1000.json \
             --out $H/osmc_sr_closure.json > $H/log_osmc_sr_closure.txt 2>&1 ;;
ddssps)    H=$A/plot/HNWR_2024/cutbased/studies/ttbar/07_ss_dyonly_flip  # OS data, two entries per OS event with the energy shift (--pt-shift)
           $C python3 $H/chargeflip_ddss_dyonly.py --dumps $T/data/chargeflip/dumps_v4/all --json $T/data/chargeflip/chargeflip_ptshift_ee2024_sf3roofit_merge1000.json \
             --sf2 --dy-only --pt-shift --sr-edges 800,1000,1200,1400,1600,2000,2400,2800,3200,8000 --out $H/ddss_dyonly_sf_ss3200_merge1000_ptshift.root > $H/log_dyonly_sf_ss3200_merge1000_ptshift.txt 2>&1 ;;
ddssosmcps) H=$A/plot/HNWR_2024/cutbased/studies/ttbar/07_ss_dyonly_flip  # OS MC as data + energy shift
           $C python3 $H/chargeflip_ddss_dyonly.py --dumps $T/data/chargeflip/dumps_v4/all --json $T/data/chargeflip/chargeflip_ptshift_ee2024_sf3roofit_merge1000.json \
             --sf2 --dy-only --os-mc --pt-shift --sr-edges 800,1000,1200,1400,1600,2000,2400,2800,3200,8000 --out $H/ddss_dyonly_sf_ss3200_merge1000_osmc_ptshift.root > $H/log_dyonly_sf_ss3200_merge1000_osmc_ptshift.txt 2>&1 ;;
ddsstt)    H=$A/plot/HNWR_2024/cutbased/studies/ttbar/07_ss_dyonly_flip  # flip term for DY + TT, OS data, energy shift
           $C python3 $H/chargeflip_ddss_dyonly.py --dumps $T/data/chargeflip/dumps_v4/all --json $T/data/chargeflip/chargeflip_ptshift_ee2024_sf3roofit_merge1000.json \
             --sf2 --dy-only --flip-groups DY,TT --pt-shift --sr-edges 800,1000,1200,1400,1600,2000,2400,2800,3200,8000 --out $H/ddss_dytt_sf_ss3200_merge1000_ptshift.root > $H/log_dytt_sf_ss3200_merge1000_ptshift.txt 2>&1 ;;
ddssttosmc) H=$A/plot/HNWR_2024/cutbased/studies/ttbar/07_ss_dyonly_flip  # flip term for DY + TT, OS MC as data, energy shift
           $C python3 $H/chargeflip_ddss_dyonly.py --dumps $T/data/chargeflip/dumps_v4/all --json $T/data/chargeflip/chargeflip_ptshift_ee2024_sf3roofit_merge1000.json \
             --sf2 --dy-only --flip-groups DY,TT --os-mc --pt-shift --sr-edges 800,1000,1200,1400,1600,2000,2400,2800,3200,8000 --out $H/ddss_dytt_sf_ss3200_merge1000_osmc_ptshift.root > $H/log_dytt_sf_ss3200_merge1000_osmc_ptshift.txt 2>&1 ;;
esac
