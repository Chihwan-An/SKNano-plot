# 13. Leading-jet pT vs m(ll): one jet (m(llj) > 800) vs two jets (m(lljj) > 800) — 2026-09-25

질문 (사용자): R(jet pT) 이 DY CR 과 SR 에서 모양이 달라서 생기는 것 같다. 1 jet 만 요구하고 m(llj) > 800 에서 m(ll) 60–150 과
m(ll) > 400 의 leading jet pT 차이를 보고, 2 jet 에서의 모양 차이와 같은지 확인.

방법: HNWR userflag `JetXcheck` (JX_ 히스토그램; 1j = AK4 정확히 1 개, AK8 없음 → 모든 SR 과 겹치지 않음; 2j = resolved 선택,
AK8 허용/금지 두 가지; OS; R 포함/미포함). 빠른 로컬 실행: 샘플마다 파일 몇 개 (MC 는 파일 수 비로 scale), data = 기간 G
(Muon 전부, EGamma 80 개/stream). 배경은 DY + ttbar + tW 만. 통계 오차만. 스크립트 `scripts/`, 그림/표 `plots/`
(`summary.md`, `dy_shape_ratio_{MM,EE}.png`, `datamc_shape_{MM,EE}.png`).

## DY MC: jet pT 모양의 m(ll) 의존 (m(ll)>400 / 60–150, 정규화, R 없음)
- 1j 와 2j(noAK8) 는 100–400 GeV 에서 같다 (μμ 1.23/0.67/0.49/0.37 vs 1.23/0.79/0.51/0.43). 400 GeV 위는 1j 가 AK8 veto 때문에 다름.
- 실제 분석 선택 (2j, AK8 허용) 은 100–200 GeV 에서 1.9 로 1j (1.2) 와 다름. → 1j 는 100–400 GeV 에서만 2j 대리 영역.
- m(ll) 의존의 대부분은 m(ll(j)j) > 800 컷의 운동학 (m(ll) 이 작으면 jet 이 질량을 채워야 함).

## data/MC 모양 (R 없음, 각 영역 정규화)
μμ: 1j m(ll) 60–150 은 100–600 GeV 에서 평평 (1.01/1.09/0.85/1.01/1.01, ±10–15 %), 1j m(ll)>400 은 1.14 (40–70) → 0.75–0.98 → 0.80 (400–600)
로 완만히 내려감 (±10–25 %). 2j DY CR 은 400 GeV 까지 1.0, 위에서 0.90/0.71/0.64 로 떨어짐 (R 이 고치는 부분). ee 는 통계가 더 작고
두 m(ll) 영역 모두 내려가는 경향.
→ 1-jet data 에서 m(ll) 에 따른 모양 차이는 통계 안 (1–2σ 암시 수준). 이 정도 통계로는 "R 이 m(ll) 에 따라 달라야 한다" 를
data 로 확인하지도 반박하지도 못한다. FxFx pseudo-data (10_jetpt_in_emu_cr) 의 soft-jet 쪽 CR/SR 차이 (0.80 vs 0.66) 와 방향은 같다.

## v2 (같은 날): 1-jet R vs 2-jet R, 그리고 m_ll 이동 closure — `plots_v2/` (`scripts/plot_jx_v2.py`, `summary.md`)
- MC 규격화 수정: 로컬 실행의 "파일 수 비" 는 틀렸다 (파일마다 이벤트 수가 다름). 샘플별 k = 전체 production 의 2-jet OS DY CR (μμ) / 로컬
  같은 선택. data 는 stream 별 같은 방식 (MM 2.875, EE 6.789). VV/ttV 추가 (W+jets 없음). 남은 편차: 로컬 2-jet 60–100→100–150 μμ 합 1.10 vs 전체 production 1.03 (~7 %).
- **R(jet pT), m_ll 60–150**: 1-jet + m(llj)>800 은 2-jet 과 오차 안에서 같다. 1-jet 질량 컷 없음은 100–300 GeV 에서 2-jet 의 0.7 배 (μμ 1.13–1.22 vs 1.5–1.7) →
  보정은 jet pT 만의 함수가 아니다; m(ll(j)j) 컷 (즉 사건 hardness/HT) 에 의존.
- **60–100 → 100–150**: 1-jet 질량 컷 없음은 닫힘 (합 1.00–1.03), 여기서는 (ii) MC 모양 bin 별 보정이 (i) 보다 확실히 낫다 (χ² ee 42.8→23.9, μμ 59.8→20.5; 통계가 커서 굵은 bin 안 기울기가 보임). 1-jet + m(llj)>800 은 통계가 작아 (i)/(ii) 차이 없음 (합 0.98/1.20).
- **60–150 → >400 (SR 방향)**: 1-jet 질량 컷 없음은 닫힘 (μμ 0.96–0.98, χ² 8/12; ee 0.93, χ² 21–26/11). **1-jet + m(llj)>800 은 안 닫힘: μμ 0.77–0.82, ee 0.62** (DY 72–74 %)
  → 저-m_ll 에서 구한 R 을 고-m_ll 로 가져가면 DY 를 20–40 % 과대예측. 2-jet 의 같은 방향 (60–150 → 150–400) 은 μμ 1.02, ee 0.90–0.93.
  FxFx pseudo-data (10 번) 의 SR ~10 % 과대와 같은 방향. 단 로컬 규격화 편차 (~7 %) 와 W+jets 누락이 남은 한계.
