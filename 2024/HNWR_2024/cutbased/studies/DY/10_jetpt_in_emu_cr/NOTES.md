# 10. R(jet pT) 는 m_ll > 400 (SR) 에서도 맞나 — e-mu CR 과 FxFx pseudo-data (2026-09-22)

질문 (사용자): "SR 에서도 맞냐는 질문은 결국 m_ll dependence 인데, resolved 는 ttbar CR 에서 jet pT 에 대해 (data − non-DY MC) 와 DY 를
겹쳐 분포가 비슷한지 보자" + "FxFx 에서도 해봐".

두 스크립트, 출력은 `plots/`:
- `scripts_jetpt_emu.py` → `jetpt_dataMinusNonDY_vs_DY_<var>_2024.png`, `jetpt_emu_cr_2024.json`, `run.log`
- `scripts_fxfx_pseudodata.py` → `fxfx_pseudodata_<var>_2024.png`, `fxfx_pseudodata_2024.json`, `run_fxfx.log`

입력: data·non-DY·LO(새 보정) = `SKNanoOutput/HNWR/backup/RFlav_DYCRCharge_ZptNJet/2024`, LO(옛 보정) = `RFlav_DYCRCharge/2024`,
LO 무보정·FxFx = `SKNanoOutput_dy3gen/HNWR/DYCRSplit_NoDYCorr_WeightSystOnly/2024`. 전부 `Central`.
e-mu CR = `FlavCR_Resolved_EM` (`HNWR.cc:2236`: m_ll > 400, m_lljj > 800 — SR 선택 그대로, e-mu 쌍). 플로터와 같이 Muon stream 만 data 로 쓴다
(처음 EGamma+Muon 을 둘 다 세서 data/MC 가 2.03 으로 나왔던 것은 이중 계수, 수정함).

## A. e-mu CR: (data − non-DY) vs DY — 검증력이 없다

e-mu CR 의 DY 는 DY→ττ→eμ 로 MC 의 0.6% (3534 중 21 events) 다. (data − non-DY) 는 TT 모델링의 잔차가 지배하고 DY 통계 오차가
±20–80 이라 R 의 m_ll 의존을 잴 수 없다. (표는 `run.log`.) 이 영역에서 실제로 읽을 수 있는 것은 TT 의 jet pT data/MC 뿐이다 → §C.

## B. FxFx pseudo-data (MC 만, SR blind 아님)

FxFx (NLO, 보정 없음) 를 data 로 놓고 LO × C × EW × R 이 DY CR 과 SR 에서 같은 비를 주는지 본다. R 이 m_ll 방향으로 외삽되면
보정된 LO 에 대한 FxFx/LO 가 CR 과 SR 에서 같아야 한다.

FxFx / LO, leading jet pT (resolved, ee+μμ):
```
                              합     40-100     100-200    200-400    400-600    600-800    800-2000
DY CR  LO 무보정            1.224   1.49±0.05  1.39±0.02  1.20±0.01  1.10±0.02  0.90±0.03  0.75±0.05
DY CR  LO×C(per-jet)×EW×R  0.993   0.80±0.03  0.93±0.01  1.01±0.01  1.10±0.02  1.00±0.04  1.01±0.07
SR     LO 무보정            1.274   1.25±0.12  1.34±0.09  1.33±0.09  0.92±0.16  0.69±0.29  1.45±0.49
SR     LO×C(per-jet)×EW×R  0.896   0.66±0.06  0.89±0.06  1.14±0.08  1.01±0.17  0.91±0.39  2.59±0.88
```
FxFx / LO, m_lljj (resolved):
```
                              합    800-1000  1000-1200  1200-1400  1400-1600  1600-2000  2000-2400
DY CR  LO×C(per-jet)×EW×R  0.993   0.98±0.01  1.03±0.01  1.02±0.02  0.94±0.02  1.00±0.02  0.95±0.04
SR     LO×C(per-jet)×EW×R  0.896   0.81±0.06  0.94±0.07  0.95±0.09  1.06±0.13  0.88±0.14  0.87±0.23
```
boosted (leading AK8 pT): DY CR 0.87 / 1.00 / 1.02 (합 0.94), SR 0.83 / 1.01 / 0.74 (합 0.91, SR FxFx 301 events).

읽는 법:
- **normalization**: 보정된 LO 에 대한 FxFx/LO 합이 CR 0.99 → SR 0.90. 즉 CR 에서 맞춘 보정을 SR 에 가져가면 FxFx 기준으로 DY 를 **~10% 과대** 예측한다
  (resolved). fit 의 `R_DY` rateParam 은 CR 과 SR 이 공유하므로 이 10% 는 흡수되지 않는다. boosted 는 0.94 → 0.91 (3%).
- **jet pT 모양**: 무보정 NLO/LO 의 soft-jet 기울기가 SR 에서 더 완만하다 (40–100: CR 1.49 vs SR 1.25±0.12; 100–200: 1.39 vs 1.34).
  CR 에서 유도한 R (40–100 에서 1.9) 을 SR 에 곱하면 soft-jet bin 이 0.66±0.06 (CR 0.80±0.03) 으로 2σ 더 낮고, 200–400 은 1.14±0.08 (CR 1.01) 로 높다.
  → **R 은 m_ll 에 약하게 의존한다** (soft jet 일수록 고-m_ll 에서 보정이 작아야 한다). m_lljj < 800 에서 본 것 (`chargeflip/new_DYCR/README.md` §6) 과 같은 방향.
- 한계: FxFx 자체도 DY CR 의 data 와 soft-jet 에서 20% 다르다 (CR 의 0.80). 그래서 절대값이 아니라 **CR 대 SR 의 차이** 만 읽어야 한다.
  SR FxFx 는 1607 weighted events (음수 weight 포함) 라 bin 별 오차가 6–9%.
- 옛 C 와 새 C 의 차이는 여기서도 1–2% 뿐.

## C. e-mu CR 의 TT jet pT (부산물)

data / MC (Muon stream, DY 새 보정, 총 3623 / 3534 = 1.025):
```
jet pT   40-60  60-80  80-100 100-130 130-160 160-200 200-250 250-300 300-400 400-500 500-600 600-800 800-1200
d/MC     1.10   1.03   1.00   1.06    1.01    1.06    0.94    0.99    1.01    1.11    1.40    1.24    0.99
```
TT 의 jet pT 는 40–400 GeV 에서 ±6% 안으로 평평하다. 즉 DY CR 의 1.9 → 0.8 기울기는 jet 재구성·JES 같은 공통 효과가 아니라 **DY MC 고유** 의 것이다.
(data − non-DY) / DY 는 3.6±5.0, 8.0±4.5, −5.7±6.7, … 로 의미 없음 (§A).

## 결론

- e-mu CR 은 R 의 m_ll 의존을 못 잰다 (DY 0.6%). 대신 TT 의 jet pT 가 평평해서 R 이 DY 고유 보정임은 확인된다.
- FxFx pseudo-data 로는 **CR 에서 맞춘 R 을 SR 에 가져가면 resolved DY 가 FxFx 기준 ~10% 과대** 이고, soft-jet bin 에서 R 이 2σ 과대다.
  R 의 m_ll 의존 (또는 m_lljj 의존) 이 있다는 쪽. 크기는 10% 수준이라 systematic 으로 넣거나 R 을 (jet pT, m_lljj) 2D 로 바꾸는 것이 후보.
- 이 10% 는 FxFx 자체의 불확실성 (CR soft-jet 에서 data 와 20% 차이) 안에 있을 수 있어, 단독 근거로는 약하다.
  data 로 직접 재려면 m_lljj > 800, 150 < m_ll < 400 (blind 아님) 이 남은 유일한 영역이다.

## D. jet pT 모양: DY CR 대 SR 대 signal (2026-09-22, `scripts_jetpt_cr_vs_sr_shape.py`)

`plots/jetpt_shape_DYCR_vs_SR_vs_signal_{Resolved_leading_jet_pt,Resolved_subleading_jet_pt,Boosted_leading_fatjet_pt}_2024.png`, 수치 `run_shape.log`.
unit-area, 비율은 DY CR 의 DY MC 기준. DY = C(per-jet)×EW×R, ee+μμ 합.

resolved leading jet pT, bin 별 비율 (%):
```
                      40-60 60-80 80-100 100-130 130-160 160-200 200-250 250-300 300-400 400-500 500-600 600-800 800-1000 >1000
DY CR  DY MC            0.2   1.1   2.7    5.8     8.3    13.7    15.5    14.8    22.9     9.2     3.5     1.8     0.3     0.1
DY CR  data-nonDY       0.2   1.2   2.6    6.3     8.3    13.3    16.8    15.0    21.4     9.3     3.3     1.8     0.3     0.1
SR     DY MC            6.2  11.5  12.2   13.7    12.0    13.5    10.2     7.0     7.5     3.2     1.5     1.1     0.3     0.1
SR     sig 4000/2000    0.0   0.1   0.1    0.3     0.5     0.9     1.6     2.3     6.7     8.8    10.4    22.2    19.2    26.7
SR     sig 4000/200     1.8   3.8   5.0    8.0     7.9     9.2     8.9     7.2    10.2     7.4     5.4     7.8     5.4    11.7
```
- **DY CR 과 SR 의 DY jet pT 는 완전히 다른 분포다.** DY CR 은 m_lljj > 800 을 m_ll ≈ 90 으로 만들어야 하므로 jet 이 단단하다 (40–100 GeV 가 4%, 최빈 300–400).
  SR 은 m_ll > 400 이 m_lljj 를 채우므로 jet 이 부드럽다 (40–100 GeV 가 **30%**, 100–200 이 39%). subleading 은 더 심하다: SR 의 62% 가 40–80 GeV (DY CR 29%).
- 그래서 R 이 SR 에서 가장 많이 작용하는 곳은 DY CR 에서 **통계가 가장 적고 (4%) R 이 가장 큰 (1.9)** 40–100 bin 이다. R 의 m_ll 외삽 문제는 곧 이 soft-jet bin 의 문제다.
  §B 의 FxFx 결과 (SR soft-jet bin 0.66) 와 m_lljj<800 결과가 모두 이 bin 을 가리킨다.
- signal (4 TeV / 2 TeV) 은 jet pT 600 GeV 위에 76% 가 있어 DY 와 거의 안 겹친다 (DY SR 은 >600 이 1.5%). R 의 soft-jet 불확실성은 이 점의 SR 에는 거의 안 들어간다.
  반면 m_N = 200 GeV 점은 jet 이 부드러워 (40–200 에 36%) DY 와 겹친다 — R 문제가 limit 에 영향을 주는 것은 저-m_N 쪽이다.
- boosted 는 CR/SR 의 AK8 pT 모양이 비슷하다 (최빈 400–500 둘 다). signal 은 >1 TeV 가 78%.
