# mT(l1, MET) 시그널/백그라운드 분리 스터디 — boosted_nolep SR

- 날짜: 2026-08-06
- 입력: `/u/user/snu202527803/SKNanoOutput/presel_3SR/NoSyst/2022` (presel_3SR ntuple, 2022, 7.99 fb^-1)
- 트리: `Central/SR_{EE,MM}_BDTTree_boosted_nolep`, 브랜치 `met_mt_l1`, 가중치 `weight_Central`
- 플로터: `../plot_SR.py` (`--split-nonprompt` 로 Nonprompt 를 TTLJ / W+jets(M<120) / W+jets(M>120) 으로 분리)

## 동기

boosted_nolep SR 은 subleading lepton 을 요구하지 않아 nonprompt(W+jets, TTLJ semileptonic)
가 지배적인 영역. W→lν 에서 나오는 lepton+MET 의 transverse mass 는 W 질량의 Jacobian
엣지 때문에 ~80 GeV 위로 급감할 것으로 기대되고, 시그널(W_R→lN, N→(l)qq̄, MET 은 주로
mismeasurement + fatjet 안의 lepton)은 leading lepton pT 가 커서 mT 가 훨씬 단단할
것으로 기대 → 분리 변수 후보인지 확인.

## 결과 요약

- **배경**: 예상대로 W Jacobian 구조가 보이며, 다만 boosted 셀렉션의 높은 lepton pT 와
  MET resolution 때문에 칼같은 80 GeV 컷오프가 아니라 **80–100 GeV 부터 가파른 감소**
  형태 (zoom 플롯 참고). Nonprompt 안에서는 W+jets(M<120) 가 압도적
  (EE: 76k/95k, MM: 160k/215k).
- **시그널**: 모든 마스포인트에서 mT 스펙트럼이 수백 GeV 까지 거의 평탄.
  N 질량이 큰 포인트일수록 더 단단함.
- **채널**: MM 이 EE 보다 분리력이 전반적으로 좋음.

### mT 컷 효율 (컷 이상 잔존 비율, weight_Central 합 기준)

| 컷 | BKG (EE / MM) | WR2000N100 | WR2000N1100 | WR4000N100 | WR4000N2100 | WR6000N100 |
|---|---|---|---|---|---|---|
| mT > 100 GeV | 22.5% / 18.2% | 41.3 / 68.2% | 68.4 / 82.1% | 49.2 / 79.0% | 80.7 / 91.6% | 52.0 / 74.3% |
| mT > 200 GeV | 3.1% / 1.9% | 21.6 / 51.7% | 39.7 / 64.1% | 29.7 / 69.8% | 62.7 / 83.3% | 32.0 / 62.6% |

mT > 200 GeV 에서 배경은 2–3% 만 남고 시그널은 22–83% 잔존 → **분리 변수로 유효**.

## 결론 / 후속 제안

- `met_mt_l1` 은 현재 3SR 학습 feature 목록
  (`LRSM_BDT/SR/Tools/features/3SR/keep_features_boosted_nolep_*.txt`) 에 **없음**.
  nolep 트랙의 BDT 입력으로 추가할 가치가 있어 보임.
- 추가 시 fit observable(ml1fatjet)과의 상관 자동드롭(run_one_bdt.sh 의 correlation
  autodrop) 을 통과하는지 확인 필요.

## 파일

- `EE_boosted_nolep_met_mt_l1_plot.png` / `MM_...` : 0–1000 GeV 전체 범위
- `EE_boosted_nolep_met_mt_l1_zoom_plot.png` / `MM_...` : 0–300 GeV (Jacobian 엣지 확인용)
- `*_met_mt_l1.tsv` : 빈별 수율 (배경 그룹 + Nonprompt 서브그룹 + 시그널 5종)

재현:

```bash
cd plots/HNWR/BDT/3SR
python plot_SR.py --region EE_boosted_nolep --var met_mt_l1 --xmin 0 --xmax 1000 --nbin 40 \
    --split-nonprompt --xlabel "m_{T}(l_{1}, p_{T}^{miss}) [GeV]" --output <out>
# zoom: --xmin 0 --xmax 300 --nbin 30
```
