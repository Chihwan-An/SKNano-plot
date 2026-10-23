#!/bin/bash
# boosted_nolep 의 nonprompt CR (40 < met_mt_l1 < 400 GeV) — Data/MC 포함 플롯.
# Nonprompt 는 초록 채도로 서브그룹 분리. 출력: CR/nonprompt_CR/<region>/
# 사용법: ./run_nonprompt_cr.sh [NJOBS]   (기본 6 병렬; 12 이상은 numpy import 크래시 위험)
cd "$(dirname "$0")/.."   # plot_SR.py 가 있는 3SR/ 에서 실행
NJOBS=${1:-6}

CUT="met_mt_l1>40 && met_mt_l1<400"
LABEL="Nonprompt CR (40<m_{T}<400)"

JOBS=()
add() {  # region var xmin xmax nbin xlabel [custom-bins]
    JOBS+=("$1|$2|$3|$4|$5|$6|$7")
}

CHG_BINS="-1.5,-0.5,0.5,1.5"

for ch in EE MM; do
    if [ "$ch" == "EE" ]; then lep=ele; llab="e"; else lep=mu; llab="#mu"; fi
    N=${ch}_boosted_nolep
    add $N ${lep}1_pt        0 1500 30 "Leading ${llab} p_{T} [GeV]"
    add $N ${lep}1_eta      -3 3    30 "Leading ${llab} #eta"
    add $N ${lep}1_phi      -3.2 3.2 32 "Leading ${llab} #phi"
    add $N ${lep}1_charge   -1.5 1.5 3 "Leading ${llab} charge" "$CHG_BINS"
    add $N fatjet1_pt        0 2000 40 "Leading fatjet p_{T} [GeV]"
    add $N fatjet1_eta      -3 3    30 "Leading fatjet #eta"
    add $N fatjet1_phi      -3.2 3.2 32 "Leading fatjet #phi"
    add $N fatjet1_sdMass    0 500  25 "Fatjet m_{SD} [GeV]"
    add $N dPhi_l1_fatjet1   0 3.2  32 "#Delta#phi(l_{1}, J)"
    add $N lt                0 2500 25 "L_{T} [GeV]"
    add $N ml1fatjet         0 4000 40 "m(l_{1}, J) [GeV]"
    add $N met_pt            0 500  25 "p_{T}^{miss} [GeV]"
    add $N met_phi          -3.2 3.2 32 "#phi^{miss}"
    add $N met_mt_l1         0 400  40 "m_{T}(l_{1}, p_{T}^{miss}) [GeV]"
done

run_one() {
    IFS='|' read -r region var xmin xmax nbin xlabel custombins <<< "$1"
    mkdir -p "CR/nonprompt_CR/$region"
    if [ -s "CR/nonprompt_CR/$region/${region}_${var}_plot.png" ]; then
        echo "skip (exists): $region $var"; return
    fi
    EXTRA=()
    if [ -n "$custombins" ]; then
        EXTRA=(--bins="$custombins")
    else
        EXTRA=(--xmin "$xmin" --xmax "$xmax" --nbin "$nbin")
    fi
    python plot_SR.py --region "$region" --var "$var" \
        "${EXTRA[@]}" --xlabel "$xlabel" \
        --cut "met_mt_l1>40 && met_mt_l1<400" --data --split-nonprompt \
        --region-label "Nonprompt CR (40<m_{T}<400)" --ratio-ymax 2.0 \
        --output "CR/nonprompt_CR/$region/${region}_${var}" \
        > "CR/nonprompt_CR/$region/${region}_${var}.log" 2>&1
    echo "done: $region $var"
}
export -f run_one

printf '%s\n' "${JOBS[@]}" | xargs -P "$NJOBS" -I {} bash -c 'run_one "$@"' _ {}
echo "ALL DONE (${#JOBS[@]} plots)"
