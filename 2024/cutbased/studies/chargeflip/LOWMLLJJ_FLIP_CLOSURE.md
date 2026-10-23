# Study 25 — 2-jet, m_lljj < 800 시험 영역에서 flip 예측 (OS 데이터 × w, OS MC × w) vs 관측 SS

2026-09-20. 질문: "테스트 리전은 m_ll > 400, m_lljj < 800 에서 방법이 통하는 걸 보여 줘야 하나".
이 영역은 분석의 low-mass validation region (m_ll > 200, m_lljj < 800; `tex/04_events.tex` 의 주석 처리된 정의, ttbar App. J closure 에서 이미 데이터를 본 영역) 이라 **OS, SS 데이터 모두 열려 있다.**
m_lljj ≥ 800 인 event 는 cache 단계에서 읽지 않는다.

## 왜 이 영역인가
- SR 과 같은 object 선택·같은 jet 수 (nJet ≥ 2, passResolved)·같은 m_ll 범위이고 m_lljj 만 반대 → **1-jet 전달 없이** 2-jet event 로 직접 시험할 수 있다.
- 조성도 SR 에 가깝다 (OS MC: tt̄+tW 67%, DY 29% at m_ll ≥ 400; DY CR 은 DY 94%).
- DY CR 이 검증해 주지 못하던 세 가지 (`SUMMARY_jetbin_idea.md` §3: 고 pT 전자의 P·SF, non-flip SS 성분, Z peak 밖) 를 한 번에 본다.

## 선택과 입력
EE, hasPair, nJet ≥ 2, passResolved, m_lljj < 800; (A) m_ll ≥ 400, (B) 200 ≤ m_ll < 400. EGamma 데이터 + 전 MC (`dumps_boost`), cache `data/lowmlljj_events.npz` (1.15M event, `scripts/lowmlljj_build.py`).
w, P, SF 는 study 18 과 동일 (`chargeflip_ptshift_ee2024_sf3.json`). 코드는 study 18 의 `scripts/osmc_flip_dycr_closure.py` 에 `--region lowmlljj --mll-min --mll-max` 를 추가한 것 (기본 동작은 그대로).
non-flip = MC SS 중 두 전자 모두 gen-match 된 charge 가 reco 와 같은 것 + gen-match 가 없는 전자가 있는 것.

## 결과 (`AN_rawcharge/25_lowmlljj_mll400/`, `25_lowmlljj_mll200to400/`; `summary.json`, `run.log`)

| | (A) m_ll ≥ 400 | (B) 200 ≤ m_ll < 400 | (참고) DY CR, study 18 |
|---|---:|---:|---:|
| 관측 SS | **88** | **814** | 1174 |
| non-flip MC | 14.1 | 197.3 | 47.3 |
| 기존: OS 데이터 × w | 34.2 ± 1.3 | 355.6 ± 3.8 | 1048.4 |
| → total, obs/pred | 48.3, **1.82 ± 0.19** | 552.9, **1.47 ± 0.05** | 1095.8, 1.071 |
| OS MC × w | 43.2 ± 0.3 | 417.2 ± 0.8 | 1047.7 |
| → total, obs/pred | 57.3, 1.54 ± 0.16 | 614.5, 1.33 ± 0.05 | 1095.1, 1.072 |
| OS MC × w, OS yield 를 데이터에 맞춤 | 34.2 → 1.82 | 353.2 → 1.48 | 1035.3 → 1.084 |
| OS MC × w (SF 없이) vs MC truth flip SS | 29.4 vs 28.8 | 285.5 vs 284.8 | 711.4 vs 704.7 |
| OS data / OS MC (yield) | 0.792 | 0.847 | 0.988 |
| ⟨w⟩ OS data / ⟨w⟩ OS MC | 0.998 | 1.007 | 1.013 |

OS MC 조성: (A) DY 411 / TT 932 / Others 48 / Nonprompt 9; (B) DY 4774 / TT 16134 / Others 419 / Nonprompt 98.
non-flip 구성 (`25_lowmlljj_mll400/nonflip_breakdown.txt`): (A) Nonprompt 5.7, Others 4.7, TT 1.9, DY 1.8 — 그중 gen-match 없는 전자가 있는 (fake 성) 것 9.1, 진짜 SS (WZ/ZZ/ttV) 5.0.
(B) Nonprompt 85.9, Others 61.1, TT 25.6, DY 24.7 — fake 성 104.6, 진짜 SS 92.8.

m_lljj bin 별 (B): 300–400: 1.26, 400–500: 1.40, 500–600: 1.65, 600–700: 1.40, 700–800: 1.52. (A): 500–600: 1.68, 600–700: 1.77, 700–800: 1.91.

## 읽는 법

1. **OS MC × w 의 구조는 여기서도 성립한다.**
   - w 의 MC closure (SF 없이 OS MC × w vs MC truth flip SS): 29.4 vs 28.8, 285.5 vs 284.8 — 1–2%. tt̄ 가 지배하는 표본에서도 "전자 (pT, η) 만의 weight" 가 닫힌다.
   - OS data 와 OS MC 의 **event 당 평균 w 가 같다** (0.998, 1.007). 즉 2-jet 고질량에서 OS MC 의 전자 kinematics 는 데이터와 맞고, 어긋나는 것은 **normalization 뿐** (0.79, 0.85 — tt̄ 가 MC 에서 과대; CR-only fit 의 R_TT_Resolved 0.88, ttbar study 의 low-mass tt_dd/tt_mc 0.91 과 같은 방향).
     normalization 을 맞추면 OS MC × w = OS 데이터 × w (34.2 vs 34.2, 353.2 vs 355.6). → "OS MC 가 맞는지" 에 대한 **2-jet 에서의 직접 답**: shape 은 맞고 norm 은 R_TT/R_DY 로 잡아야 한다.
     (1-jet 에서 보였던 "데이터가 더 forward, ⟨w⟩ +5–8%" 는 2-jet 에서는 보이지 않는다.)
2. **그러나 예측 자체가 관측 SS 의 55–68% 밖에 안 된다** (obs/pred 1.82 ± 0.19, 1.47 ± 0.05). OS 데이터를 쓰든 OS MC 를 쓰든 같다 → source 의 문제가 아니라 **flip 확률 또는 non-flip 성분**의 문제.
   - 초과는 전자 η 에 대해 평평하다 (1.3–1.65; endcap 에 몰리지 않음) 그리고 subleading pT 가 낮을수록 크다 (53–70 GeV: 1.7, 100–150: 1.3).
     flip 확률이 틀렸다면 endcap 에서 커야 하므로, **MC 로만 넣는 non-flip (특히 fake 전자) 이 부족할 가능성**이 더 크다. 부족분 (B) 814 − 553 = 261 을 fake 성 non-flip (104.6) 으로만 메우려면 ×3.5 가 필요하다.
   - 다른 후보: tt̄ 전자에 Z peak 의 P·SF 를 그대로 쓰는 가정, Z peak 밖 (DY CR 의 60–80: 1.3, 120–150: 1.8 과 같은 경향). 이 시험만으로는 가르지 못한다.
   - DY CR 에서는 non-flip 이 4% 라 이 문제가 보이지 않았다. SR 에서는 non-flip 이 ~30% 다.
3. 따라서 "m_lljj < 800 에서 방법이 통한다" 를 보여 주는 용도로는 **현재 상태로는 쓸 수 없다** — 오히려 SS 예측에 50–80% 의 미해결 부족이 있음을 보여 준다. 이것은 1-jet 전달·OS MC 여부와 무관한, 기존 방법 자체의 문제다.

## (A) m_ll ≥ 400 만 자세히 — 초과가 어디에 있나 (`AN_rawcharge/25_lowmlljj_mll400/ss_excess_mll400.txt`)

관측 88, flip (OS 데이터 × w) 34.2, non-flip MC 14.1. 오차는 √obs 만.

| 구분 | obs | flip | non-flip | obs/pred |
|---|---:|---:|---:|---:|
| subleading pT 53–100 | 56 | 12.6 | 7.7 | **2.77 ± 0.37** |
| subleading pT 100–150 | 16 | 11.3 | 3.9 | 1.05 ± 0.26 |
| subleading pT 150–200 | 12 | 7.5 | 1.8 | 1.30 ± 0.38 |
| subleading pT 200–400 | 4 | 2.9 | 0.8 | 1.10 ± 0.55 |
| **subleading pT ≥ 100 합** | **32** | 21.6 | 6.4 | **1.14 ± 0.20** |
| 둘 다 barrel | 14 | 7.2 | 3.6 | 1.29 ± 0.34 |
| 하나 endcap | 55 | 23.4 | 9.5 | 1.67 ± 0.23 |
| 둘 다 endcap | 19 | 3.5 | 0.9 | 4.26 ± 0.98 |
| m_ll 400–450 / 450–500 / 500–600 / 600–800 | 40 / 29 / 17 / 2 | 18.5 / 9.8 / 4.9 / 1.0 | 7.8 / 3.8 / 2.4 / 0.1 | 1.52 / 2.14 / 2.32 / 1.83 |

- 초과는 **subleading pT < 100 GeV** 에 몰려 있다 (56 vs 20.2). subleading pT ≥ 100 에서는 obs/pred 1.14 ± 0.20 으로 닫힌다.
- 둘 다 endcap 인 경우가 특히 크다 (4.3 ± 1.0). "저 pT + endcap" 은 fake 전자가 많은 곳이기도 하고 flip 확률이 가장 빨리 변하는 곳이기도 해서, 이 표만으로는 둘을 가르지 못한다.
- m_lljj < 800 이라 이 영역의 전자는 SR 보다 부드럽다 (m_ll ≥ 400 인데 m_lljj < 800 이려면 jet 과 lepton 이 모두 soft). SR 의 subleading 전자는 대부분 100 GeV 위일 것이므로
  (미확인 — SR MC 로 확인 가능), **subleading pT ≥ 100 으로 제한한 closure (1.14 ± 0.20) 가 SR 에 더 가까운 시험**이다. 다만 통계가 32 event 뿐이다.

## 다음에 볼 것 (미실시)
- SS 초과를 (leading, subleading) pT × η, tightCharge/convVeto/lostHits 별로 나눠 fake 인지 flip 인지 가르기. 데이터 기반 fake 추정 (loose-not-tight) 이 있으면 non-flip 을 그것으로 교체.
- eμ flavor CR 의 SS (tt̄ 순수, DY flip 없음) 로 tt̄ 전자의 P·SF 가정 점검.
- μμ 의 SS (flip 이 사실상 없음) 로 non-flip MC 의 크기를 직접 점검: μμ SS data/MC 가 1.5–2 라면 fake MC 부족이 확인된다.

## 파일
```
scripts/lowmlljj_build.py                                   cache 생성 (dump 80개, 약 10분)
scripts/osmc_flip_dycr_closure.py --region lowmlljj --cache data/lowmlljj_events.npz --mll-min 400 [--mll-max 1e9] --out-dir AN_rawcharge/25_lowmlljj_mll400
AN_rawcharge/25_lowmlljj_<mll400|mll200to400>/summary.json, run.log
AN_rawcharge/25_lowmlljj_*/nominal_OSdata_x_w/ResolveLowMlljjEE_SS_<var>_plot.png     SS: data vs [OS data × w + non-flip MC]
AN_rawcharge/25_lowmlljj_*/OSMC_x_w{,_normalised}/                                     SS: data vs [OS MC × w + non-flip MC]
AN_rawcharge/25_lowmlljj_*/OS_data_vs_MC/ResolveLowMlljjEE_OS_<var>_plot.png           OS data vs MC (norm 0.79 / 0.85)
```

---

# Study 26 — 같은 시험 영역에서 2-jet → 1-jet 전달을 시험: "2-jet OS MC × f × w" vs "1-jet OS 데이터 × w"

2026-09-20. 지적: study 25 의 "OS MC × w vs OS 데이터 × w" 는 같은 영역에 같은 w 를 곱한 것이라 (OS MC 의 전자 분포가 데이터와 같은지만 보는) 약한 시험이고,
SR 에서는 그 OS 데이터를 쓸 수 없다. SR 에서 실제로 할 수 있는 비교는 **2-jet OS MC 를 1-jet 으로 옮긴 것 vs 1-jet OS 데이터** 이므로, 그 절차가 통하는지를 열린 시험 영역에서 본다.
여기서는 2-jet 데이터도 열려 있어서 **2-jet OS 데이터 × f** 까지 넣어 전달 자체를 데이터로 검사할 수 있다 (SR 에서는 불가능한 검사).

- T (2-jet) = nJet ≥ 2, passResolved, m_lljj < 800; S (1-jet) = nJet == 1, ΔR(ℓℓ) > 0.4; 같은 m_ll 범위; EE, OS.
- f_g(m_ll, Z pT) = N_g^MC(S)/N_g^MC(T), g = DY, TT, 나머지 (그룹별); f_tot = 전체 MC. m_ll 6 bin × Z pT 9 bin, N_eff < 30 cell 은 m_ll-only.
- 입력: 1-jet 은 `data/zpt_zeta_transfer_events.npz`, 2-jet 은 `data/lowmlljj_events.npz`. 코드 `scripts/lowmlljj_to_1jet_transfer.py`.

## 결과 (`AN_rawcharge/26_lowmlljj_to_1jet_mll400to800/`, `..._mll200to400/`; `summary.json`, `run.log`)

### 400 ≤ m_ll < 800
| 표본 (1-jet 영역에서) | N | Σw | ⟨w⟩ | 1-jet data / 이것 (Σw) | leading η χ²/4 | endcap 비율 |
|---|---:|---:|---:|---:|---:|---:|
| **1-jet OS 데이터** | 4184 | 165.0 ± 3.3 | 0.0395 | 1 | — | 0.311 |
| native 1-jet MC | 4124 | 151.5 | 0.0367 | 1.089 ± 0.022 | 41 | 0.268 |
| 2-jet OS MC × f_g | 3876 | 127.8 | 0.0330 | **1.292 ± 0.031** | 118 | 0.238 |
| 2-jet OS MC × f_tot | 4064 | 126.7 | 0.0312 | 1.302 ± 0.040 | 173 | 0.231 |
| 2-jet OS **데이터** × f_tot | 2985 | 94.7 ± 5.1 | 0.0317 | 1.744 ± 0.101 | 72 | 0.258 |
| (참고) 2-jet OS MC, f 없이 | 1400 | 43.2 | 0.0309 | | | 0.241 |
| (참고) 2-jet OS 데이터, f 없이 | 1109 | 34.2 | 0.0308 | | | 0.271 |

### 200 ≤ m_ll < 400
| 표본 | N | Σw | ⟨w⟩ | 1-jet data / 이것 (Σw) | η χ²/4 | endcap |
|---|---:|---:|---:|---:|---:|---:|
| 1-jet OS 데이터 | 30,352 | 767.0 ± 6.4 | 0.0253 | 1 | — | 0.251 |
| native 1-jet MC | 29,974 | 710.0 | 0.0237 | 1.080 ± 0.009 | 97 | 0.228 |
| 2-jet OS MC × f_g | 29,970 | 652.4 | 0.0218 | **1.176 ± 0.011** | 423 | 0.203 |
| 2-jet OS MC × f_tot | 29,974 | 586.3 | 0.0196 | 1.308 ± 0.011 | 858 | 0.183 |
| 2-jet OS 데이터 × f_tot | 25,462 | 501.8 ± 5.5 | 0.0197 | 1.529 ± 0.021 | 804 | 0.189 |

(2-jet × f_g 의 N 이 native 와 정확히 같지 않은 것 (3876 vs 4124) 은 N_eff 부족 cell 의 fallback 때문.)

## 읽는 법
1. **시험 영역에서 (m_ll, Z pT) 전달은 통하지 않는다.** 1-jet 데이터 / (2-jet MC × f) 의 Σw = 1.29 ± 0.03 (400–800), 1.18 ± 0.01 (200–400). native 1-jet MC (1.09, 1.08) 보다 **나쁘다**.
2. 방향이 SR topology 와 **반대**다. m_lljj > 800 (study 24) 에서는 2-jet 전자가 1-jet 보다 forward 였고 (endcap 0.30 vs 0.27), m_lljj < 800 에서는 더 central 이다 (0.24 vs 0.27).
   m_lljj 조건이 계 전체의 boost 를 고르기 때문: 큰 m_lljj → forward, 작은 m_lljj → central. 1-jet 은 그 사이. (m_ll, Z pT) 는 이 η 차이를 담지 못한다.
3. **이것은 MC 의 문제가 아니라 전달 변수의 문제**다. 2-jet **데이터**에 같은 f 를 곱해도 ⟨w⟩ = 0.0317 로 1-jet 데이터 (0.0395) 와 다르고, 2-jet 데이터와 2-jet MC 의 ⟨w⟩ 는 서로 같다 (0.0308 vs 0.0309).
   즉 2-jet MC 는 2-jet 데이터를 잘 기술하지만, 어느 쪽이든 (m_ll, Z pT) 만으로는 1-jet 의 전자 η 분포로 옮겨지지 않는다.
4. 따라서 study 24c 의 "m_ll ≥ 400, m_lljj > 800 에서 2j×f 가 1-jet 데이터와 맞는다 (Σw 1.03)" 는, 2j 의 forward 편향 (+12%) 이 1-jet data/MC 차이 (+10%) 와 크기가 같아서 생긴 일치로 보는 것이 맞다 (24d 의 "교차점" 해석).
   같은 절차가 m_lljj < 800 에서는 편향이 반대 부호라 1.29 로 벌어진다.
5. 전달을 살리려면 factor 에 전자 η 가 들어가야 한다 (study 17: t(Z pT, |η1|, |η2|) 로 78% → 98%). 그러나 w 는 전자 (pT, η) 만의 함수라, η 까지 맞춘 전달은 Σw 를 **정의상** native 1-jet MC 와 같게 만들고
   비교는 "native 1-jet MC vs 1-jet 데이터" (1.09) 로 환원된다. 1-jet 데이터로 2-jet OS MC 를 독립적으로 검증하는 경로는 이 점에서 막힌다.

## 그림
`AN_rawcharge/26_lowmlljj_to_1jet_mll*/<native_1jetMC|transferred_fg|transferred_ftot>/OneJetEE_OSxw_<var>_plot.png` — 1-jet OS 데이터 × w (점) vs MC × w (stack), 변수: 전자 η_SC, pT, m_ll, pT(ll).
재실행: `cd plot/cutbased; ./condor/in_container.sh python3 studies/chargeflip/scripts/lowmlljj_to_1jet_transfer.py --mll-min 400 --mll-max 800` (약 3분).

---

# Study 27 — 같은 시험 영역의 OS / SS data/MC (보정 없는 순수 stack), EE 와 MM

2026-09-21. 요청: "resolved EE SR 과 셀렉션이 같고 m_lljj < 800 인 영역에서, DY CR 에서 그리던 변수들을 OS/SS 각각 data/MC 로" + "이 영역 muon 도".
선택은 SR 에서 m_lljj 부등호만 뒤집은 것 — `channel==11 (EE) / 13 (MM), hasPair, nJet>=2, passResolved, m_ll >= 400, m_lljj < 800`
(SR 은 `passResolved & m_ll > 400 & m_lljj > 800`, `BDT/SR/test/scripts/chargeflip_ddss.py` 의 `rEESR_SS`). 열린 low-mass validation 영역이라 OS·SS 데이터 모두 표시한다.
Study 25 와 달리 **flip weight 를 쓰지 않는다**: SS 의 MC 는 시뮬레이션이 스스로 만든 flip + non-flip 을 그대로 쌓은 것이다 (= study 25 의 rawMC 28.8 + non-flip 14.1 = 42.9).

## Yield (`AN_rawcharge/27_lowmlljj_datamc_mll400{,_MM}/summary.json`)

| | data | MC 합 | data/MC | DY | TT+tW | Nonprompt | Others |
|---|---:|---:|---:|---:|---:|---:|---:|
| EE OS | 1109 | 1399.7 | **0.792 ± 0.024** | 411.4 | 931.9 | 8.8 | 47.7 |
| EE SS | 88 | 42.9 | **2.05 ± 0.22** | 10.8 | 20.4 | 5.7 | 6.0 |
| MM OS | 1568 | 1887.9 | **0.831 ± 0.021** | 529.0 | 1290.8 | 5.6 | 62.5 |
| MM SS | 28 | 19.1 | **1.47 ± 0.28** | 1.2 | 2.6 | 10.3 | 4.9 |
| EE Inclusive | 1197 | 1442.7 | 0.830 ± 0.024 | 422.2 | 952.3 | 14.5 | 53.7 |
| MM Inclusive | 1596 | 1907.0 | 0.837 ± 0.021 | 530.2 | 1293.5 | 15.9 | 67.5 |

(오차는 데이터의 √N 만. MM 의 데이터는 Muon dataset, cache 는 `data/lowmlljj_events_mm.npz`.
Inclusive = OS + SS 합. EE 는 SS 의 초과 때문에 OS 의 0.792 에서 0.830 으로 올라가고, MM 은 SS 가 작아 0.831 → 0.837 로 거의 변하지 않는다.)

subleading lepton pT bin 별 data/MC:

| pT | 53–70 | 70–100 | 100–150 | 150–200 | 200–250 |
|---|---:|---:|---:|---:|---:|
| EE OS | 1.04 | 0.85 | 0.85 | 0.69 | 0.67 |
| MM OS | 0.97 | 1.05 | 0.82 | 0.75 | 0.65 |
| EE SS | **5.35** | 2.06 | 1.30 | 1.34 | 0.77 |
| MM SS | 1.28 | 1.79 | 1.56 | 1.33 | 0.68 |

- **OS 는 두 채널이 같다**: 0.792 (EE), 0.831 (MM). EE 의 0.792 는 study 25 의 OS data/OS MC 와 같은 수다.
  어긋남은 m_lljj·jet η·lepton η 에 평평하고 (m_lljj bin 별 EE 0.62–0.83), subleading lepton pT 가 높아질수록 커지는 것도 두 채널이 같다
  (150 GeV 위에서 0.59–0.75). tt̄ 가 지배하는 표본의 normalisation 문제로, CR-only fit 의 R_TT_Resolved 0.88 과 같은 방향이다.
  전자 특유의 효과가 아니라는 것이 muon 으로 확인된다.
- **SS 는 두 채널이 다르다.** EE 는 raw MC 대비 2.05 이고 초과가 subleading pT 53–70 (5.35) 과 70–100 (2.06) 에 몰려 있다.
  MM 은 1.47 ± 0.28 이고 pT 에 대해 1.3–1.8 으로 평평하다.
- MM SS 의 MC 는 사실상 전부 non-flip 이다 (muon charge flip 은 무시할 수준; Nonprompt 10.3 = 54%, Others 4.9, TT 2.6, DY 1.2).
  따라서 이것이 study 25 의 "다음에 볼 것" 에 적은 **non-flip/fake MC 크기의 직접 점검**이다. 결과는 부족한 쪽 (1.47) 이지만 28 event 라 1 로부터 1.7σ 이고,
  EE 의 2.05 를 fake MC 부족만으로 설명하기에는 크기가 모자란다. 특히 EE 초과가 몰려 있는 저 pT (53–70) 에서 MM 은 1.28 뿐이라,
  **EE 초과의 상당 부분은 전자 특유의 것** (flip 확률 또는 conversion/fake 전자) 으로 보인다. 다만 두 채널의 fake 조성이 같지 않으므로 이 비교만으로 단정할 수는 없다.

## 그림

`AN_rawcharge/27_lowmlljj_datamc_mll400{,_MM}/{OS,SS,Inclusive}/ResolveLowMlljj{EE,MM}_[{OS,SS}_]<var>_plot.png`,
DY CR 과 같은 13 개 변수: `dilepton_{mass,pt}`, `jetnum`, `{leading,subleading}_jet_{pt,eta}`, `mlljj`, `mlljj_fine`, `{leading,subleading}_lep_{pt,eta}`.
`dilepton_pt` 가 reco Z pT (`pt_l1l2`) 다. Inclusive 는 DY CR 산출물과 같은 규칙으로 파일 이름에 charge tag 를 붙이지 않는다.
Binning 은 이 phase space 에 맞췄고 두 채널이 같다 (m_ll < ~650, 480 < m_lljj < 800, jet pT 40–300;
lepton η 만 acceptance 에 따라 EE ±2.5, MM ±2.4). Ratio 축은 OS 0.5–1.5, SS 0–5.5.
마지막 bin 밖으로 나가는 event 는 data·MC 모두 4 개 이하라 clip 의 영향은 없다.

```bash
./condor/in_container.sh python3 studies/chargeflip/scripts/lowmlljj_datamc_plots.py               # EE
./condor/in_container.sh python3 studies/chargeflip/scripts/lowmlljj_datamc_plots.py --channel 13  # MM
# m_ll 200–400 (SR 밖, 통계용):
./condor/in_container.sh python3 studies/chargeflip/scripts/lowmlljj_datamc_plots.py --mll-min 200 --mll-max 400 \
    --out-dir studies/chargeflip/AN_rawcharge/27_lowmlljj_datamc_mll200to400
```

Cache: `scripts/lowmlljj_build.py` 에 `--channel` 을 추가했다 (11 → `data/lowmlljj_events.npz`, 13 → `data/lowmlljj_events_mm.npz`, MM 의 데이터는 Muon dataset).
EE cache 에는 `j1_eta`, `j2_eta` 를 추가로 넣어 다시 만들었다. 나머지 key 와 이벤트 수 (1,148,626) 는 그대로이고
study 25 를 다시 돌려 숫자가 같은 것 (nominal 34.2 + 14.1, obs 88, obs/pred 1.823, OS data/MC 0.7923) 을 확인했다 — study 25·26 은 재실행 없이 유효하다.
MM cache 는 1,487,864 event.
