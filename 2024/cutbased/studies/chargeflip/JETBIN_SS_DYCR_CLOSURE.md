# Study 17 — 1-jet OS 데이터로 2-jet SS 를 예측: resolved EE DY CR closure

2026-09-19. 다른 study (08–16) 와 달리 **collision data 를 읽는다** (DY CR 은 blind 가 아님). SR 데이터는 읽지 않는다.

## 왜
기존 추정은 같은 (≥2 jet) 영역의 OS 데이터에 flip weight `w(P1,P2)` 를 곱한다. SR 에서는 그 OS 표본 자체가 signal region 이다.
그래서 OS source 를 `nJet == 1` 로 옮기고, reco Z pT bin 별 전달계수 (study 12 의 아이디어) 로 2-jet 의 lepton kinematics 를 흉내낸 뒤
event 별로 같은 flip weight 를 곱한다. 먼저 데이터가 열려 있는 DY CR 에서 되는지 본다.

    N_SS^pred(T) = Σ_{1-jet OS data} t(cell) · w(P(l1), P(l2))  +  MC non-flip SS in T

| | 정의 |
|---|---|
| T (target) | EE, hasPair, `isDYCR` (nJet ≥ 2, passResolved, 60 < m_ee < 150, m_lljj > 800) |
| S (source) | EE, hasPair, **nJet == 1**, 60 ≤ m_ee < 150, OS, EGamma 데이터 324,151 event |
| t | cell 별 `N_OS(T)/N_OS(S)`. `mc_*` = 전체 MC (모든 그룹, nominal weight) 에서, `data_*` = OS 데이터에서 (target OS 데이터를 쓰므로 개념 검증용) |
| w, P, SF | `BDT/SR/test/scripts/chargeflip_ddss.new_weights` 와 동일, `chargeflip_ptshift_ee2024_sf3.json` (3-region SF) |
| non-flip | T 의 MC SS 중 gen-matched flip 이 없는 것: 47.3 (DY 17.5, Nonprompt 13.5, Others 12.6, TT 3.8) |
| 관측 | T 의 SS 데이터 **1174**, OS 데이터 35,120 |

cell 정의 (`mode`): `zpt` = reco pT(ll) 12–13 bin (양쪽 N_eff ≥ 50 이 되게 위에서부터 병합), `mll_zpt` = m_ee 9 bin × Z pT,
`zpt_eta1` = Z pT × |η_SC(l1)| 3 bin (0–0.8–1.5–2.5), `zpt_eta2d` = Z pT × |η_SC(l1)| × |η_SC(l2)|. source 가 빈 cell 은 Z-pT-only 계수로 대체.
입력: `BDT/SR/test/data/chargeflip/dumps_boost` (jet 수 제한 없는 event dump, 데이터 포함), 선택된 event 는 `data/jetbin_ss_dycr_events.npz` 에 cache.

## 결과 (`AN_rawcharge/17_1jet_to_2jet_ss_dycr/summary.json`)

| 방법 | Σt (OS 예측) | flip | total | obs/pred | OS yield 를 35,120 에 맞추면 |
|---|---:|---:|---:|---:|---|
| **기존: 2-jet OS 데이터 × w** | 35,120 | 1048.4 ± 8.2 | 1095.8 | **1.071 ± 0.031** | — (기존 표 1048.4 / 1096.0 / 1.071 과 일치 → 구현 검증) |
| 1-jet, data t(Z pT) | 35,120 | 812.9 | 860.3 | 1.365 ± 0.040 | |
| 1-jet, data t(m_ee, Z pT) | 35,120 | 815.4 | 862.7 | 1.361 | |
| 1-jet, data t(Z pT, \|η1\|) | 35,120 | 991.9 | 1039.2 | 1.130 | |
| **1-jet, data t(Z pT, \|η1\|, \|η2\|)** | 35,120 | **1028.1** | 1075.5 | **1.092 ± 0.032** | |
| 1-jet, MC t(Z pT) | 42,157 | 974.9 | 1022.2 | 1.148 | ×0.833 → flip 812.2, obs/pred 1.366 |
| 1-jet, MC t(m_ee, Z pT) | 42,136 | 979.4 | 1026.8 | 1.143 | ×0.833 → 1.359 |
| 1-jet, MC t(Z pT, \|η1\|) | 42,553 | 1230.9 | 1278.2 | 0.918 | ×0.825 → flip 1015.9, obs/pred 1.104 |
| 1-jet, MC t(Z pT, \|η1\|, \|η2\|) | 42,613 | 1280.2 | 1327.5 | 0.884 | ×0.824 → flip 1055.1, **obs/pred 1.065** |

오차는 통계만 (flip: Σ(tw)² 의 제곱근, obs/pred: √obs). t 자체의 통계 오차와 systematic 은 전파하지 않았다.

## 읽는 법

1. **Z pT 만으로는 안 된다.** OS event 수를 정확히 맞춰도 (data t) flip 예측이 기존의 78% 다 (813 vs 1048).
   `os_mimic/` 그림 (1-jet OS 데이터 × t vs 2-jet OS 데이터, flip weight 없음) 을 보면 lepton **pT 는 잘 맞는다** (400 GeV 아래 비율 ≈ 1)
   그러나 **η 가 다르다**: 2-jet DY CR 의 전자는 훨씬 forward — leading η_SC 비율이 |η|≈0 에서 0.75, |η|>1.5 에서 1.3–1.4 이상.
   m_lljj > 800 을 m_ee ≈ 90 으로 넘기려면 Z 와 jet 이 크게 벌어져야 해서 전자가 앞으로 쏠린다 (study 10 의 Z window: endcap 비율 22% → 32%).
   flip 확률은 endcap 에서 훨씬 크므로 endcap 비율 부족이 그대로 flip 부족이 된다. m_ee 를 추가해도 효과 없음 (815).
2. **η 를 전달계수에 넣으면 닫힌다.** data t(Z pT, |η1|, |η2|): flip 1028 (기존의 98%), obs/pred 1.092 vs 기존 1.071.
   leading 만 넣으면 992 (95%). SS 분포 (lepton pT, η, m_ee, pT(ll)) 도 기존 방법과 같은 수준으로 맞는다 — 각 폴더의 `ResolveDYEE_SS_*_plot.png`.
3. **MC 로 구한 t 는 shape 은 맞고 normalization 이 21% 크다.** Σt = 42.6k vs 실제 OS 35.1k. 1-jet 과 ≥2-jet DY CR 의 상대 yield 를 MC 가 못 맞춘다
   (jet-pT 보정 R 은 passResolved event 에만 적용되고 1-jet 에는 C×EW 뿐이라는 점이 한 원인 후보 — 미확인).
   normalization 을 OS yield 에 맞추면 MC t(Z pT, |η1|, |η2|) 는 flip 1055, obs/pred 1.065 로 기존 방법을 재현한다.
   MC t 의 "우연히 괜찮아 보이는" Z-pT-only 결과 (1.148) 는 +20% normalization 과 −22% kinematics 가 상쇄된 것이다.

## SR 로 가져갈 때의 함의 (아직 하지 않음)

- SR 에서는 data-derived t 를 쓸 수 없다 (OS SR 데이터를 쓰게 되므로). MC-derived t(Z pT, |η1|, |η2|) 의 **shape** 은 DY CR 에서 검증됐다.
  **normalization** 은 별도로 정해야 한다: (a) DY CR 에서 잰 0.824 를 SR 로 전이 (m_ee 외삽 가정 필요), (b) fit 의 free parameter, (c) 1-jet/2-jet MC 비율을 고치는 것.
- SR 은 m_ee > 400 이라 study 12 에서 본 대로 Z pT 만으로는 부족하고 m_ee 도 필요했다 (SRtopology target). 여기에 η 까지 넣으면 cell 수가 늘어 MC 통계가 문제될 수 있다.
- **1-jet event 에는 m_lljj 가 없다.** 이 방법은 SS yield 와 lepton 분포만 준다. fit 변수 shape 은 `MLL_TO_MLLJJ.md` (study 09) 의 P(m_lljj | m_ee) 같은 별도 단계가 필요하다.
- 1-jet OS 데이터의 조성 (ttbar, nonprompt 비율) 이 2-jet 과 다르다. DY CR 에서는 DY 가 지배해 문제없지만 SR (ttbar 비중 큼) 에서는 t 를 전체 MC 로 구하는 것의 타당성을 다시 봐야 한다.

## 파일

```
scripts/jetbin_ss_dycr_closure.py                      실행 코드 (plot/cutbased 의 plotter/_draw 형식으로 그림)
data/jetbin_ss_dycr_events.npz (+ .json)               선택된 event cache (EE, hasPair, 60≤m_ee<150, nJet==1 | isDYCR)
AN_rawcharge/17_1jet_to_2jet_ss_dycr/summary.json      모든 예측값, 전달계수 (edges, t)
AN_rawcharge/17_1jet_to_2jet_ss_dycr/<방법>/           SS: data vs [flip + non-flip MC], 변수 6개
AN_rawcharge/17_1jet_to_2jet_ss_dycr/<방법>/os_mimic/  OS: 2-jet OS 데이터 vs 1-jet OS 데이터 × t (flip weight 없음)
```
재실행: `cd plot/cutbased; ./condor/in_container.sh python3 studies/chargeflip/scripts/jetbin_ss_dycr_closure.py [--rebuild]`
(`--rebuild` 는 dump 80개를 다시 읽는다, 약 5분. cache 가 있으면 1분.) 이 스크립트는 다른 study 와 달리 `plot/cutbased` 의 `plotter`, `chargeflip_plots` 를 import 한다 (기존 그림 형식을 쓰기 위해).
