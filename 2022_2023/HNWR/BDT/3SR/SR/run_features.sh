#!/bin/bash
# BDT 입력 feature 변수들을 3개 SR (resolved / boosted / boosted_nolep) x EE/MM 에 대해 일괄 플롯.
# feature 목록: LRSM_BDT/SR/Tools/features/3SR/keep_features_*.txt
# (boosted_nolep 은 l2 관련 브랜치가 -999 sentinel 이므로 l1/fatjet/event 변수만 그림)
# 사용법: ./run_features.sh [NJOBS]   (기본 12 병렬)
cd "$(dirname "$0")/.."   # plot_SR.py 가 있는 3SR/ 에서 실행
NJOBS=${1:-12}

JOBS=()
add() {  # region var xmin xmax nbin xlabel [custom-bins]
    JOBS+=("$1|$2|$3|$4|$5|$6|$7")
}

CHG_BINS="-1.5,-0.5,0.5,1.5"   # charge(±1) 전용 빈 경계

for ch in EE MM; do
    if [ "$ch" == "EE" ]; then lep=ele; llab="e"; else lep=mu; llab="#mu"; fi

    # ── Resolved SR ──────────────────────────────────────────────
    R=${ch}_resolved
    add $R ${lep}1_pt        0 1500 30 "Leading ${llab} p_{T} [GeV]"
    add $R ${lep}1_eta      -3 3    30 "Leading ${llab} #eta"
    add $R ${lep}1_phi      -3.2 3.2 32 "Leading ${llab} #phi"
    add $R ${lep}1_charge   -1.5 1.5 3 "Leading ${llab} charge" "$CHG_BINS"
    add $R ${lep}2_pt        0 800  32 "Subleading ${llab} p_{T} [GeV]"
    add $R ${lep}2_eta      -3 3    30 "Subleading ${llab} #eta"
    add $R ${lep}2_phi      -3.2 3.2 32 "Subleading ${llab} #phi"
    add $R ${lep}2_charge   -1.5 1.5 3 "Subleading ${llab} charge" "$CHG_BINS"
    add $R jet1_pt           0 1500 30 "Leading jet p_{T} [GeV]"
    add $R jet1_eta         -3 3    30 "Leading jet #eta"
    add $R jet1_phi         -3.2 3.2 32 "Leading jet #phi"
    add $R jet1_partB        0 1    25 "Leading jet ParticleNet B"
    add $R jet1_mass         0 200  25 "Leading jet mass [GeV]"
    add $R jet2_pt           0 800  32 "Subleading jet p_{T} [GeV]"
    add $R jet2_eta         -3 3    30 "Subleading jet #eta"
    add $R jet2_phi         -3.2 3.2 32 "Subleading jet #phi"
    add $R jet2_partB        0 1    25 "Subleading jet ParticleNet B"
    add $R jet2_mass         0 150  30 "Subleading jet mass [GeV]"
    add $R m_l1l2            0 2000 40 "m_{l1l2} [GeV]"
    add $R pt_l1l2           0 1500 30 "p_{T}^{l1l2} [GeV]"
    add $R dR_l1l2           0 6    30 "#DeltaR(l_{1},l_{2})"
    add $R chargeProduct_l1l2 -1.5 1.5 3 "q_{l1} #times q_{l2}" "$CHG_BINS"
    add $R mjj               0 1500 30 "m_{jj} [GeV]"
    add $R ptjj              0 1500 30 "p_{T}^{jj} [GeV]"
    add $R dRjj              0 6    30 "#DeltaR(j,j)"
    add $R ptlljj            0 1500 30 "p_{T}^{lljj} [GeV]"
    add $R minDR_lep_jet     0 6    30 "min #DeltaR(l,j)"
    add $R ht                0 3000 30 "H_{T} [GeV]"
    add $R lt                0 2500 25 "L_{T} [GeV]"
    add $R mlljj             0 4000 40 "m_{lljj} [GeV]"
    add $R met_pt            0 1000 25 "p_{T}^{miss} [GeV]"
    add $R met_phi          -3.2 3.2 32 "#phi^{miss}"

    # ── Boosted SR (l2 있음) ─────────────────────────────────────
    B=${ch}_boosted
    add $B ${lep}1_pt        0 1500 30 "Leading ${llab} p_{T} [GeV]"
    add $B ${lep}1_eta      -3 3    30 "Leading ${llab} #eta"
    add $B ${lep}1_phi      -3.2 3.2 32 "Leading ${llab} #phi"
    add $B ${lep}1_charge   -1.5 1.5 3 "Leading ${llab} charge" "$CHG_BINS"
    add $B ${lep}2_charge   -1.5 1.5 3 "Subleading ${llab} charge" "$CHG_BINS"
    if [ "$ch" == "EE" ]; then
        add $B ele2_mvaNoIso -1 1   25 "Subleading e mvaNoIso"
    fi
    add $B fatjet1_pt        0 2000 40 "Leading fatjet p_{T} [GeV]"
    add $B fatjet1_eta      -3 3    30 "Leading fatjet #eta"
    add $B fatjet1_phi      -3.2 3.2 32 "Leading fatjet #phi"
    add $B fatjet1_sdMass    0 500  25 "Fatjet m_{SD} [GeV]"
    add $B m_l1l2            0 2000 40 "m_{l1l2} [GeV]"
    add $B pt_l1l2           0 1500 30 "p_{T}^{l1l2} [GeV]"
    add $B dR_l1l2           0 6    30 "#DeltaR(l_{1},l_{2})"
    add $B chargeProduct_l1l2 -1.5 1.5 3 "q_{l1} #times q_{l2}" "$CHG_BINS"
    add $B dPhi_l1_fatjet1   0 3.2  32 "#Delta#phi(l_{1}, J)"
    add $B dR_l2_fatjet1     0 6    30 "#DeltaR(l_{2}, J)"
    add $B lt                0 2500 25 "L_{T} [GeV]"
    add $B ml1fatjet         0 4000 40 "m(l_{1}, J) [GeV]"
    add $B met_pt            0 1000 25 "p_{T}^{miss} [GeV]"
    add $B met_phi          -3.2 3.2 32 "#phi^{miss}"

    # ── Boosted nolep SR (l2 없음 → l1/fatjet/event 변수만) ──────
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
    add $N met_pt            0 1000 25 "p_{T}^{miss} [GeV]"
    add $N met_phi          -3.2 3.2 32 "#phi^{miss}"
done

run_one() {
    IFS='|' read -r region var xmin xmax nbin xlabel custombins <<< "$1"
    mkdir -p "SR/$region"
    if [ -s "SR/$region/${region}_${var}_plot.png" ]; then
        echo "skip (exists): $region $var"; return
    fi
    EXTRA=()
    if [ -n "$custombins" ]; then
        EXTRA=(--bins="$custombins")   # 음수 시작 값이 옵션으로 오인되지 않게 = 로 붙임
    else
        EXTRA=(--xmin "$xmin" --xmax "$xmax" --nbin "$nbin")
    fi
    case "$region" in
        *_boosted_nolep) EXTRA+=(--split-nonprompt);;
    esac
    python plot_SR.py --region "$region" --var "$var" \
        "${EXTRA[@]}" --xlabel "$xlabel" \
        --output "SR/$region/${region}_${var}" \
        > "SR/$region/${region}_${var}.log" 2>&1
    echo "done: $region $var"
}
export -f run_one

printf '%s\n' "${JOBS[@]}" | xargs -P "$NJOBS" -I {} bash -c 'run_one "$@"' _ {}
echo "ALL DONE (${#JOBS[@]} plots)"
