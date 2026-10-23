# 한 장 정리 — "OS SR 데이터를 쓰지 않고 SS flip 배경을 구할 수 있나" (2026-09-19)

## 0. 출발점
- 기존 방법: **같은 영역의 OS 데이터 × w(P·SF)** → SS flip 예측. w 는 전자의 (pT, η_SC) 만의 함수. event 전체 (jet 2개, m_lljj) 가 그대로 따라온다.
- 걱정: SR 에서는 그 OS 표본이 OS SR 데이터다 → SS SR template 을 만들려면 OS SR 을 열어야 한다.
- 아이디어: jet 2개가 SR 이니 **1-jet OS** 를 source 로 쓰자. 단 1-jet 과 2-jet 은 lepton kinematics 가 다르므로 Z pT (와 Z η) 로 보정.

## 1. 확인한 것 (study 번호 = `AN_rawcharge/<번호>_*`)

| # | 질문 | 답 |
|---|---|---|
| 08 | 1-jet 과 SR 의 m_ll shape 차이는 DY 보정 (C, EW, R) 을 1-jet 에 안 해서인가? | 아니다. 보정을 다 빼도 차이가 남는다. Z pT 구간을 맞추면 많이 줄어든다 |
| 10–12 | Z pT 로 1-jet → 2-jet 을 흉내낼 수 있나 (MC) | **jet 수만 다르면** Z pT 만으로 pT, η 모두 맞는다. **SR topology (m_lljj>800) 가 목표면** m_ll+Z pT 가 필요하고, Z 구간에서는 η 가 안 맞는다 |
| 17 | 실제로 DY CR 에서 1-jet OS **데이터** × t(Z pT) × w 로 2-jet SS 를 예측하면? | Z pT 만: 기존의 **78%** (813 vs 1048). 원인 = 전자 η_SC (2-jet DY CR 이 더 forward, endcap 에서 flip 이 큼). t 에 (\|η1\|,\|η2\|) 를 넣으면 **98%** (1028). MC 로 구한 t 는 shape 은 맞고 normalization 이 21% 큼 |
| — | 근본 한계 | **1-jet event 에는 두 번째 jet 이 없다 → m_lljj 를 만들 수 없다.** 이 방법은 yield 와 lepton 분포만 준다 |
| 18 | 대안: **OS MC × w** (OS 데이터 대신 MC) | DY CR 에서 기존 방법을 0.1% 로 재현 (1047.7 vs 1048.4), m_lljj bin 별로도 수 %. jet 이 따라오므로 m_lljj 가 나온다. SF 없이 MC truth flip 과의 closure 1% |
| 19 | 2-jet MC 를 f(Z pT, Z η) 로 1-jet 에 옮겨 1-jet 데이터로 검증 (OS MC 의 점검용) | DY window 에서는 성립 (±5–10%). **같은 f 를 m_ll ≥ 400 에 쓰면 5배 어긋남** |
| 19+ | DY window 에서도 고 pT 꼬리가 안 맞던 이유 | bin 폭이 아니라 **ΔR(ℓℓ) > 0.4** (passResolved). Z pT ≳ 500 이면 Z peak 의 대칭 붕괴가 ΔR≈2m/pT<0.4 로 2-jet 에서만 잘린다. 1-jet 에도 걸면 닫힘 (87% → 12%) |
| 20 | DY window 의 f 와 m_ll ≥ 400 의 f 가 같은가 (MC) | 아니다. Z pT < 300 에서 1/8–1/2, Z pT > 400 에서만 같다 (1.0–1.3) |
| 21, 21b | 왜 다른가 | (a) **m_lljj > 800**: m_ll≈90 이면 센 recoil 이 있어야 통과, m_ll≥400 이면 Z pT 가 작아도 통과. (b) **lepton pT cut (60/53)**: m_ll² + pT(ll)² > 113² 이라 pT(ll)<50 에는 Z peak 이 아예 없다 (m_ll>100 만). 같은 "low Z pT bin" 이 DY window 와 고질량에서 전혀 다른 위상공간이다 |
| 23 | m_ll bin 별로 1j/2j 를 정규화하면 Z pT 비율이 m_ll 과 무관한가 (MC) | m_lljj>800 **없이** 는 m_ll 150–700 에서 ±10% 로 같다 (DY window 는 Z pT<100 에서 다름). m_lljj>800 **있으면** 아니다: 저/고 Z pT 사이 기울기가 m_ll 에 따라 ×5–26 변한다 |
| 24 | 그러면 f 를 (m_ll, Z pT) 2D 로 만들면? (MC, 1-jet 데이터) | yield·m_ll·Z pT 는 정의상 닫히고 lepton pT 도 ±10% 로 닫힌다. **η 는 안 닫힌다** (m_ll≥400 에서 \|η\|>2 +34%). 그래서 event 당 평균 flip weight 가 2j×f 쪽이 DY window 에서 1.75배, m_ll≥400 에서 1.12배 크다. m_ll≥400 의 data/transferred Σw = 1.03. **24c: 1-jet 데이터의 η 는 native 1-jet MC (χ² 38.5/4) 보다 2j×f (4.3/4) 와 잘 맞는다** — 단 같은 방법이 m_ll<400 에서는 크게 틀려 (0.68, 0.76) 원리적 검증으로 보기는 어렵다 |
| 25 | 2-jet, m_lljj<800 (열린 validation 영역) 에서 직접 시험하면? | OS MC 의 전자 kinematics 는 데이터와 같다 (⟨w⟩ 비 1.000; norm 만 0.79–0.85, tt̄ 과대) → norm 을 맞추면 OS MC×w = OS data×w. **그러나 두 방법 모두 관측 SS 의 55–68% 만 예측** (obs/pred 1.82±0.19 @m_ll≥400, 1.47±0.05 @200–400). 초과는 η 에 평평, 저 pT 에 큼 → non-flip (fake) MC 부족 의심. `LOWMLLJJ_FLIP_CLOSURE.md` |
| 26 | 같은 시험 영역 (m_lljj<800) 에서 2-jet OS MC × f(m_ll, Z pT) × w vs 1-jet OS 데이터 × w | **안 통한다**: data/transferred Σw = 1.29±0.03 (400–800), 1.18 (200–400) — native 1-jet MC (1.09) 보다 나쁨. m_lljj<800 의 2-jet 전자는 1-jet 보다 central (SR topology 와 반대 부호). 2-jet **데이터**×f 도 똑같이 어긋나므로 MC 가 아니라 전달 변수 (η 없음) 의 문제. 24c 의 일치는 크기가 우연히 맞은 것 |

## 2. 그래서 지금 결론

1. **1-jet source 방법**: DY CR 에서 데이터로 닫히는 것까지는 확인 (η 포함 시 98%). 그러나
   - m_lljj shape 을 못 준다,
   - SR 로 가면 전달계수를 MC 로 구해야 하고 normalization (21%) 을 따로 정해야 하며,
   - DY window 에서 검증한 계수는 m_ll ≥ 400 으로 옮겨지지 않는다 (m_lljj>800 과 lepton pT cut 때문).
   → SR 의 주 방법으로 쓰기는 어렵다. cross-check 용도.
2. **OS MC × w**: jet 과 m_lljj 가 따라오고 OS SR 데이터가 필요 없다. DY CR 에서 기존 방법과 동일. 현재로서는 가장 단순한 대안.
   약점은 OS MC 의 SR 모델링을 그대로 물려받는다는 것 (normalization 은 fit 의 R_DY/R_TT 가 잡지만 shape 은 아님).
3. **기존 방법 (OS 데이터 × w) 의 실제 위험은 크지 않다**: OS 와 SS 는 다른 event, signal 오염은 평균 w≈4%, fit 내 상관도 그 정도. 문제는 "OS SR 을 먼저 열어야 한다" 는 절차.

## 3. DY CR 이 검증해 주지 못하는 것 (어느 방법이든 공통)
- 고 pT 전자에서의 P·SF (SF 는 Z peak, pT 무관 가정; SR leading 평균 340 GeV). DY CR 의 400–1000 GeV bin 은 event ~20개.
- non-flip SS 성분: DY CR 에서 4%, SR 에서 30%. 순수 MC.
- DY CR 의 obs/pred 1.07 은 peak 밖 (60–80: 1.3, 120–150: 1.8) 에서 온다. SR 은 전부 peak 밖.

## 4. 다음에 할 만한 것
- **eμ flavor CR 의 SS closure** (`FlavCR_Resolved_EM_{OS,SS}`, m_ll>400, m_lljj>800): SR 과 같은 kinematics, tt̄ 지배, signal 없음 (blind 아님).
  eμ OS × P·SF(e) → eμ SS 예측. 위 3 의 세 항목을 한 번에 데이터로 시험한다.
- SR 의 MC 에서 "OS MC × w(SF 없이) vs MC truth flip SS" closure (데이터 불필요).
- OS MC × w 를 card 에 넣는다면 Flip 을 DY/TT 로 나눠 R_DY/R_TT 에 묶기, OS MC 의 object systematic 을 Flip template 에도 걸기.

## 5. 문서·그림 위치 (모두 `studies/chargeflip/`)
| 내용 | 문서 | 그림 폴더 (`AN_rawcharge/`) |
|---|---|---|
| 1-jet OS 데이터 → 2-jet SS, DY CR | `JETBIN_SS_DYCR_CLOSURE.md` | `17_1jet_to_2jet_ss_dycr/` |
| OS MC × w, DY CR | `OSMC_FLIP_DYCR_CLOSURE.md` | `18_osmc_flip_dycr/` |
| f(Z pT, Z η) 2j→1j, ΔR(ℓℓ), f 의 m_ll 의존, shape 그림 | `ZPT_ZETA_2J_TO_1J.md` | `19_zpt_zeta_2j_to_1j{,_fine,_drll}/`, `20_factor_dywindow_vs_highmass/`, `21_zpt_shape_vs_mll/` |
| 08–16 (다른 세션의 MC 진단) | `RESULTS.md`, `JETBIN_*.md`, `MLL_TO_MLLJJ.md` 등 | `08_*` – `16_*` |
