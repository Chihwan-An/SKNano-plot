# Study 18 — OS **MC** × 데이터 보정 flip weight 로 SS 예측: resolved EE DY CR closure

2026-09-19. collision data 를 읽는다 (DY CR 은 blind 아님). SR 데이터는 읽지 않는다.

## 왜
- 기존 방법 (OS **데이터** × w) 은 SR 에서 OS SR 데이터를 열어야 SS template 을 만들 수 있다.
- study 17 의 1-jet 대안은 yield 와 lepton 분포는 주지만 **jet 이 하나뿐이라 m_lljj 를 만들 수 없다.**
- OS **MC** event 에 w 를 곱하면 event 가 jet 2개와 m_lljj 를 그대로 들고 오고, 해당 영역의 OS 데이터는 전혀 쓰지 않는다.
  flip 확률의 데이터 보정 (SF, Z peak 에서 유도) 은 그대로 들어간다.

      N_SS^pred(T) = Σ_{OS MC in T} weight · w(P·SF(l1), P·SF(l2))  +  MC non-flip SS in T

T = EE, hasPair, `isDYCR` (nJet ≥ 2, passResolved, 60 < m_ee < 150, m_lljj > 800). w/P/SF 는 `chargeflip_ptshift_ee2024_sf3.json`,
계산은 `chargeflip_ddss.new_weights` 와 동일. 입력은 study 17 의 event cache (`data/jetbin_ss_dycr_events.npz`; `dumps_boost` 에서 선택).

## 결과 (`AN_rawcharge/18_osmc_flip_dycr/summary.json`)

관측 SS 데이터 **1174**, non-flip MC 47.3.

| 방법 | flip | total | obs/pred |
|---|---:|---:|---:|
| 기존: OS 데이터 (35,120) × w | 1048.4 ± 8.2 | 1095.8 | 1.071 ± 0.031 |
| **OS MC (35,542) × w** | **1047.7 ± 2.4** | 1095.1 | **1.072 ± 0.031** |
| OS MC × w, OS yield 를 데이터에 맞춤 (×0.988) | 1035.3 | 1082.6 | 1.084 |
| OS MC × w, SF 없이 (MC 의 flip 확률 그대로) | 711.4 ± 1.6 | 758.7 | 1.547 |
| MC 의 SS 를 그대로 (truth-flipped SS) | 704.7 ± 7.8 | 752.1 | 1.561 |

오차는 통계만 (flip: Σ(weight·w)² 의 제곱근). SF·P 의 불확도와 MC normalization 불확도는 전파하지 않았다.

그룹별: OS MC = DY 33,265.6 + TT 1,284.6 + Others 970.3 + Nonprompt 21.9. flip 예측 = DY 1003.7 + Others 24.3 + TT 19.2 + Nonprompt 0.5.

m_lljj bin 별 (card 의 `rDYEECR_SS` binning):

| m_lljj [GeV] | obs | 기존 | OS MC × w | obs/기존 | obs/(OS MC, norm) |
|---|---:|---:|---:|---:|---:|
| 800–1000 | 517 | 472.7 | 487.9 | 1.094 | 1.072 |
| 1000–1200 | 270 | 259.7 | 259.0 | 1.040 | 1.055 |
| 1200–1400 | 158 | 148.5 | 142.8 | 1.064 | 1.119 |
| 1400–1600 | 78 | 85.6 | 80.8 | 0.911 | 0.977 |
| 1600–2000 | 111 | 78.7 | 76.1 | 1.410 | 1.476 |
| 2000–2400 | 22 | 30.0 | 28.5 | 0.732 | 0.780 |
| 2400–2800 | 10 | 12.7 | 11.2 | 0.785 | 0.907 |
| 2800–3200 | 4 | 3.9 | 4.9 | 1.037 | 0.834 |
| 3200–8000 | 4 | 3.9 | 4.0 | 1.034 | 1.024 |

## 읽는 법

1. **OS MC × w 는 기존 방법을 0.1% 로 재현한다** (1047.7 vs 1048.4), m_lljj bin 별로도 수 % 이내. 1600–2000 의 +41% 는 두 방법에 똑같이 있다
   (기존 AN 표에도 있던 1.410) — flip 방법의 문제가 아니라 그 bin 의 데이터 변동.
2. **w 자체의 MC closure**: SF 를 빼고 MC 의 P 만 쓰면 OS MC × w = 711.4, MC 가 실제로 만든 flipped SS = 704.7 → 1% 로 닫힌다.
   즉 "OS event × lepton 만의 weight → SS" 라는 구조가 jet 을 포함한 event 전체에서 성립한다 (m_lljj, nJet 분포 그림도 `OSMC_x_w/` 참조).
   통계 오차는 OS MC × w 가 2.4, MC SS 직접이 7.8 — 같은 MC 에서 약 3배 (분산 10배) 좋다.
3. 데이터 보정 SF 의 효과가 전부다: 711 → 1048 (×1.47). MC SS 를 그대로 쓰면 obs/pred 1.56 (기존에 알려진 값).
4. **DY CR 에서 잘 맞는 데에는 구조적인 이유가 있다**: DY 의 jet-pT 보정 R 이 바로 이 CR 에서 data/MC 로 유도됐기 때문에 OS data/MC = 0.988 이 보장돼 있다.
   SR 에서는 OS 의 data/MC 를 미리 알 수 없다 (blind). OS MC 의 normalization 은 fit 의 `R_DY_Resolved`, `R_TT_Resolved` 가 CR 데이터로 잡아 주지만,
   SR 의 OS mass shape 모델링 (예: resolved eμ CR 에서 본 tt̄ 의 질량 기울기 0.95→1.3) 은 그대로 SS 예측에 들어온다.
   기존 방법은 이 부분을 데이터가 자동으로 해결해 준다는 점이 다르다.

## SR 에 쓸 때 고려할 것 (아직 안 함)

- SR 의 OS MC 조성은 DY CR 과 다르다 (tt̄+tW 비중이 크다). flip 예측을 그룹별 (`Flip_DY`, `Flip_TT`) 로 나눠 card 에 넣고 각각 `R_DY`, `R_TT` 에 묶으면
  OS normalization 의 불확도가 fit 안에서 일관되게 전파된다. 지금 card 의 `Flip` 은 rateParam 없는 단일 process 다.
- systematic: SF 3개 + P 통계 + closure 5% 는 기존과 같이 w 의 변주로 만들 수 있다. 추가로 OS MC 의 object systematic (JES 등) 이 Flip template 에도 걸려야 한다 (기존 데이터 기반 Flip 에는 없던 것).
- tt̄ 의 flip 은 Z peak 에서 유도한 P·SF 를 그대로 쓴다는 가정 (전자 kinematics 만의 함수) — 기존 방법도 같은 가정.
- 검증 순서 제안: SR 의 MC 에서 "OS MC × w_noSF vs MC truth-flipped SS" closure (데이터 불필요) → flavor CR 이나 low-mass 영역에서 데이터 검증.

## 파일

```
scripts/osmc_flip_dycr_closure.py                  실행 코드 (plotter._draw 형식)
AN_rawcharge/18_osmc_flip_dycr/summary.json        모든 수치, m_lljj bin 별 표
AN_rawcharge/18_osmc_flip_dycr/nominal_OSdata_x_w/ 기존 방법의 SS 그림 (m_lljj, lepton pT/η_SC, m_ee, pT(ll), nJet)
AN_rawcharge/18_osmc_flip_dycr/OSMC_x_w/           OS MC × w 의 SS 그림
AN_rawcharge/18_osmc_flip_dycr/OSMC_x_w_normalised/ OS yield 를 데이터에 맞춘 버전
AN_rawcharge/18_osmc_flip_dycr/OS_data_vs_MC/      OS 영역 자체의 data vs MC (OS MC × w 가 물려받는 모델링)
```
재실행: `cd plot/HNWR_2024/cutbased; ./condor/in_container.sh python3 studies/chargeflip/scripts/osmc_flip_dycr_closure.py` (cache 사용, 약 1분).

## 추가 (2026-09-19) — "OS MC 가 맞는지 어떻게 아나": 열린 영역에서 Σw(data) vs Σw(MC)

flip 예측에 필요한 것은 OS MC 의 event 수가 아니라 **w 로 가중한 합** (yield × 전자 (pT, η_SC) 분포) 이다.
그래서 데이터가 열려 있는 영역에서 `Σ_data w` 와 `Σ_MC weight·w` 를 직접 비교했다 (EE, OS, 같은 `sf3` json; 입력 `data/zpt_zeta_transfer_events.npz`).

| 영역 | N data | N MC | data/MC | Σw data | Σw MC | **Σw 비율** | ⟨w⟩ data / MC |
|---|---:|---:|---:|---:|---:|---:|---|
| 2-jet DY CR (기준) | 35,120 | 35,542 | 0.988 | 1048.5 | 1047.7 | **1.001 ± 0.008** | 0.02985 / 0.02948 |
| 1-jet, 60 ≤ m_ll < 150 | 324,151 | 293,450 | 1.105 | 5974 | 5133 | 1.164 ± 0.003 | 0.01843 / 0.01749 |
| 1-jet, 150 ≤ m_ll < 400 | 59,023 | 57,203 | 1.032 | 1334 | 1203 | 1.109 ± 0.007 | 0.02260 / 0.02103 |
| 1-jet, m_ll ≥ 400 | 4,503 | 4,400 | 1.023 | 182.1 | 165.5 | **1.100 ± 0.021** | 0.04043 / 0.03762 |
| 1-jet, m_ll ≥ 700 | 553 | 502 | 1.103 | 28.2 | 24.3 | 1.159 ± 0.061 | 0.05091 / 0.04845 |

- 2-jet DY CR 에서는 0.1% 로 일치 — 단 이 영역은 R 을 여기서 유도했으므로 맞을 수밖에 없는 면이 있다.
- 1-jet 고질량 (m_ll ≥ 400, 전자 kinematics 가 SR 과 비슷, DY 61% + tt̄ 32%) 에서는 **MC 가 w-가중 yield 를 10% 과소 예측**한다.
  event 수 차이는 2% 뿐이고 나머지 7% 는 **event 당 평균 w 가 데이터에서 더 크다**는 것 (0.0404 vs 0.0376) — 데이터의 전자가 MC 보다 더 forward / 더 고 pT 쪽에 있다는 뜻.
- 이 10% 가 "OS MC × w 를 쓸 때 OS MC 모델링에서 오는 불확도" 의 현재 크기 추정치다. 2-jet SR 자체에서는 (blind 라) 잴 수 없고, 1-jet 은 R 보정이 없는 영역이라 2-jet 보다 나쁠 가능성이 있다.
- 같은 비교를 **eμ flavor CR** (2-jet, m_ll > 400, m_lljj > 800, tt̄ 지배, 열려 있음) 에서 하면 SR 의 tt̄ 성분 (OS SR 의 ~61%) 에 대한 직접 검증이 된다 — dump 에 eμ 가 없어 아직 못 했다.
