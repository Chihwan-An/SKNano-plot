# 12. boosted DY CR 의 AK4 jet 수, 그리고 1-jet 영역 Z pT 를 boosted 에 쓸 수 있나 (2026-09-23)

입력: CF_Tree dump (`BDT/SR/test/data/chargeflip/dumps_dynew_dy` = LO DY 14, 새 jet별 C 보정; `dumps_fxfx` = FxFx 2, w_dy=1, gen 정보 없음).
영역: **B** = `isBoostedDYCR && !passResolved` (본 분석과 같이 resolved topology 실패, `HNWR.cc:2499`), **J1** = hasPair, 60≤m_ll<150, reco nJet==1,
**R2** = resolved DY CR. reco nJet = AK4 pT>40, loose 렙톤과 ΔR>0.4 cleaning (fat jet 안의 AK4 도 셈).
실행: `python3 boosted_njet_zpt.py` (표 `plots/tables.md`, 그림 `plots/genzpt_shapes_*.png`, `plots/fxfx_over_lo_recozpt_*.png`, `summary.json`),
`python3 boosted_split_njet.py` (`plots/tables_split.md`). 각 40 초, 로컬.

## 결과
- **B 의 절반이 1 jet**: reco nJet=1 이 EE 50%, μμ 58% (2: 22/19%, ≥3: 28/23%). GenJet 기준 (C 선택) 1 jet 45/52%, 0 jet 0%.
- FxFx/LO (보정 없음, reco Z pT): J1 1.18 (200–500 에서 1.13–1.16), R2 1.22, **B 0.85 (EE) / 0.90 (μμ)**.
- B 를 nJet 로 나누면: **B nJet=1 0.95 / 1.00**, **B nJet≥2 0.76 / 0.77**. generator 차이 (LO 가 FxFx 보다 많음) 는 주로 fat jet 밖에 AK4 가 더 있는 이벤트에 있다.
- B nJet=1 도 J1 보다 15–20% 낮다 (200–500 GeV: 1.03/0.98/0.87 vs 1.15/1.13/1.16, EE). 즉 1-jet C 를 가져와도 boosted 의 generator 차이는 남는다
  — 11 번에서 본 "reco boosted 선택 단계의 ~25%" 와 같은 현상.
- 모양 (200–700 에서 200–300 bin 으로 나눈 값) 은 J1, R2, B 모두 5–10% 안에서 비슷 — shape-only C 의 선택 (1 jet vs ≥2 jet) 이 B 에서 주는 차이는 작고,
  normalization 차이는 R / `R_DY_Boosted` 가 흡수.

## FxFx/LO Z pT 모양: inclusive vs resolved vs boosted topology — `plot_shape_topology.py` → `plots/zpt_shape_ratio_topology.{png,pdf,json}`
윗줄 reco (정확한 분석 topology, LO 는 보정 없음), 아랫줄 gen (11 번 json, 개수 기준 근사, ee+μμ 합이라 두 칸 같음). boosted 가 200 GeV 위에만 있으므로
모든 곡선을 200–1000 에서 단위 면적으로 맞춘 모양 비.
- reco: 200–600 에서 inclusive / resolved / boosted 가 통계 안에서 같다 (boosted bin 오차 6–11%). 셋 다 ~1.0 → 600–1000 에서 0.8–0.9 로 같은 기울기.
  boosted 에 특이한 모양은 보이지 않는다 (EE 350–400 1.09±0.09, μμ 250–300 1.14±0.09 는 1–1.5σ).
- gen: 200–1000 안에서는 Incl, ≥2 AK4, AK8&<2 AK4 모두 1.0 → 0.75 로 같은 기울기 (±3–5%).
- 즉 2 jet 과 inclusive 의 모양 차이는 pT(Z) < 200 (Incl 0–50 에서 0.90, 100–150 에서 1.22 vs ≥2 jet 1.00) 에만 있고, boosted 가 사는 200 GeV 위에서는
  어떤 topology 든 같은 모양. 차이는 절대 비 (reco: incl 1.19, resolved 1.21, boosted 0.86/0.91) 에만 있고 이것은 shape-only C 가 아니라 R/rateParam 몫.

## boosted 안의 nJet ≥ 2 — `boosted_2jet_reason.py` → `plots/boosted_2jet_reason.{md,json}`, `plots/zpt_shape_ratio_boosted_njet.png`
- boosted DY CR 의 EE 50% / μμ 42% 가 reco AK4 ≥ 2. 이 중 **97% 가 GenJet ≥ 2** → `ZptNJet` 에서 이미 resolved 와 같은 ≥2jet C 를 받는다 (C 는 영역이 아니라 이벤트의 GenJet 수로 고름).
- resolved 실패 이유는 전부 렙톤 쪽: 둘째 렙톤이 tight 쌍이 아님 64% / 44%, tight 쌍이지만 ΔR(ll) < 0.4 (고-pT Z 의 collimated 렙톤) 36% / 56%.
  jet–렙톤·jet–jet 겹침은 0.1%. 즉 hadronic recoil 은 resolved ≥2jet 과 같은 topology 이고, Z 가 boosted 라서 렙톤 조건만 실패.
- FxFx/LO 모양 (200–1000 정규화): boosted nJet≥2 는 resolved 와 bin 오차 (10–17%) 안에서 같다. EE 400–800 에서 1.02–1.09 vs 0.90–0.97 (~1.5σ) 는 통계로 배제 못함.
- 절대 비는 boosted nJet≥2 0.79, nJet=1 0.93–1.01, resolved 1.20 → reco boosted 선택의 generator 차이 (normalization), boosted R / `R_DY_Boosted` 몫.
