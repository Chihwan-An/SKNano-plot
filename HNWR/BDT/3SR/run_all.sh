#!/bin/bash
# presel_3SR ntuple의 주요 변수들을 4개 SR region에 대해 일괄 플롯 (병렬 실행).
# 사용법: ./run_all.sh [NJOBS]   (기본 12 병렬; 개별 변수는 plot_SR.py 직접 호출)
cd "$(dirname "$0")"
NJOBS=${1:-12}

JOBS=()
add() {  # region var xmin xmax nbin xlabel
    JOBS+=("$1|$2|$3|$4|$5|$6")
}

for ch in EE MM; do
    if [ "$ch" == "EE" ]; then lep=ele; llab="e"; else lep=mu; llab="#mu"; fi

    # ── Resolved SR ──
    R=${ch}_resolved
    add $R mlljj         0 4000 40 "m_{lljj} [GeV]"
    add $R mll           0 2000 40 "m_{ll} [GeV]"
    add $R mjj           0 1500 30 "m_{jj} [GeV]"
    add $R ptll          0 1500 30 "p_{T}^{ll} [GeV]"
    add $R ptjj          0 1500 30 "p_{T}^{jj} [GeV]"
    add $R dRll          0 6    30 "#DeltaR(l,l)"
    add $R dRjj          0 6    30 "#DeltaR(j,j)"
    add $R minDR_lep_jet 0 6    30 "min #DeltaR(l,j)"
    add $R ht            0 3000 30 "H_{T} [GeV]"
    add $R st            0 4000 40 "S_{T} [GeV]"
    add $R met_pt        0 1000 25 "p_{T}^{miss} [GeV]"
    add $R ${lep}1_pt    0 1500 30 "Leading ${llab} p_{T} [GeV]"
    add $R ${lep}2_pt    0 800  32 "Subleading ${llab} p_{T} [GeV]"
    add $R jet1_pt       0 1500 30 "Leading jet p_{T} [GeV]"
    add $R jet2_pt       0 800  32 "Subleading jet p_{T} [GeV]"
    add $R nJet          0 10   10 "N_{jet}"
    add $R nBJetMedium   0 5    5  "N_{b-jet} (medium)"

    # ── Boosted SR ──
    B=${ch}_boosted
    add $B ml1fatjet     0 4000 40 "m(l_{1}, J) [GeV]"
    add $B mll           0 2000 40 "m_{ll} [GeV]"
    add $B fatjet1_pt    0 2000 40 "Leading fatjet p_{T} [GeV]"
    add $B fatjet1_sdMass 0 500 25 "Fatjet m_{SD} [GeV]"
    add $B fatjet1_lsf3  0 1    25 "Fatjet LSF_{3}"
    add $B ${lep}1_pt    0 1500 30 "Leading ${llab} p_{T} [GeV]"
    add $B met_pt        0 1000 25 "p_{T}^{miss} [GeV]"
    add $B st            0 4000 40 "S_{T} [GeV]"
    add $B dR_l1_fatjet1 0 6    30 "#DeltaR(l_{1}, J)"
    add $B nFatJet       0 5    5  "N_{fatjet}"
done

run_one() {
    IFS='|' read -r region var xmin xmax nbin xlabel <<< "$1"
    mkdir -p "$region"
    python plot_SR.py --region "$region" --var "$var" \
        --xmin "$xmin" --xmax "$xmax" --nbin "$nbin" \
        --xlabel "$xlabel" --output "$region/${region}_${var}" \
        > "$region/${region}_${var}.log" 2>&1
    echo "done: $region $var"
}
export -f run_one

printf '%s\n' "${JOBS[@]}" | xargs -P "$NJOBS" -I {} bash -c 'run_one "$@"' _ {}
echo "ALL DONE (${#JOBS[@]} plots)"
