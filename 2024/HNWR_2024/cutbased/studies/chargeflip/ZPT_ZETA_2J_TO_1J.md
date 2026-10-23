# Study 19 — (Z pT, |Z η|) 2D factor 로 2-jet DY MC 를 1-jet 영역으로 옮기기

2026-09-19. 아이디어: 2-jet MC 를 1-jet 영역으로 옮겨 놓고, **열려 있는 1-jet 데이터**로 2-jet MC 의 lepton kinematics 를 검증한다
(OS SR 데이터를 열지 않고 "OS MC × w" 의 OS MC 를 점검하려는 목적).

    f(Z pT, |Z η|) = N_DY^MC(1 jet) / N_DY^MC(2 jet)      ← DY window (60 ≤ m_ll < 150) 에서 **한 번만** 유도, EE/MM 별
    step A (DY window) : 2-jet DY MC × f  vs 1-jet DY MC,  1-jet data vs MC
    step B (m_ll ≥ 400): **같은 f** 를 2-jet SR DY MC 에 곱해 1-jet (m_ll ≥ 400) DY MC / data 와 비교

- 2-jet = nJet ≥ 2, passResolved, m_lljj > 800 (SR topology). 1-jet = nJet == 1. OS 만. Z 방향은 두 lepton 운동량에서 계산한 dilepton η.
- Z pT 14 bin × |Z η| 8 bin (0–0.5–…–3–4–∞). 양쪽 N_eff ≥ 30 인 cell 만 2D 값 (EE 76/112, MM 73/112), 나머지는 Z-pT-only → 전체 비율로 대체.
- 데이터: 1-jet 은 전 m_ll, 2-jet 은 DY CR (m_ll < 150) 만 cache 에 넣었다. **2-jet, m_ll ≥ 150 데이터는 읽지 않는다.**
- 입력 `dumps_boost` → `data/zpt_zeta_transfer_events.npz` (OS 28.3M event, float32). b-tag 정보는 dump 에 없다.

## 결과 (`AN_rawcharge/19_zpt_zeta_2j_to_1j/summary.json`)

### Step A — DY window: 대체로 성립
| | EE | MM |
|---|---|---|
| DY MC: 1-jet / 2-jet×f | 280,211 / 280,232 (정의상 일치) | 390,225 / 390,228 |
| MC closure, 분포의 몸통 | m_ll: 80–150 에서 ±5%, 60–80 에서 +15–20%. lepton pT: 200 GeV 아래 ±5%. lepton η: ≤ 10% | 같은 경향 (m_ll 최대 30%) |
| MC closure, 꼬리 | subleading pT > 200 GeV 에서 2j×f 가 1/2–1/8 로 부족 (전체의 0.1% 미만) | 〃 |
| 1-jet data / MC | **1.105** | **1.172** |

χ²/ndf 는 크다 (예: EE leading pT 610/8) — MC 통계가 수십만이라 3–5% 차이도 크게 잡히기 때문. 실질적인 어긋남은 위 표 수준.
1-jet 의 data/MC 가 1.10–1.17 인 것은 DY MC 의 1-jet normalization 부족이다 (1-jet 에는 C×EW 만 걸리고 jet-pT 보정 R 이 없다). study 17 에서 MC 전달계수가 21% 어긋났던 것과 같은 현상.

### Step B — 같은 f 를 SR (m_ll ≥ 400) 에: **성립하지 않는다**
| | EE | MM |
|---|---|---|
| 1-jet DY MC | 2,675 | 3,399 |
| 2-jet SR DY MC → × f | 752 → 14,300 | 966 → 17,283 |
| 2j×f / 1-jet MC | **5.35** | **5.09** |
| 분포 (yield 를 맞춘 뒤에도) | Z pT χ² 3779/7, m_ll 706/7, lepton pT 최대 +110–180% | 같은 경향 |
| 1-jet data / (2j×f + non-DY) | 0.28 | 0.32 |
| 1-jet data / native 1-jet MC | **1.023** | **1.076** |

원인: f 는 m_ll 에 강하게 의존한다. DY 의 N(1j)/N(2j) 는 m_ll 60–150 에서 8.4, 150–400 에서 15.4, ≥400 에서 3.6 이다.
2-jet 정의에 **m_lljj > 800** 이 들어 있어서, m_ll 이 클수록 같은 Z pT 에서도 이 조건을 쉽게 통과한다. DY window 에서는 2-jet event 의 4% 만 Z pT < 100 인데
m_ll ≥ 400 에서는 23–24% 다. 그래서 low Z pT 에서 큰 값을 갖는 f (DY window 에서 2-jet 이 희귀해서) 가 고질량 2-jet event 에 과하게 곱해진다.
즉 **(Z pT, Z η) 만으로는 DY window → SR 로 옮길 수 없다.** m_ll 을 factor 에 넣어야 하는데, 그러면 고질량의 f 는 고질량 MC 에서 구할 수밖에 없고 (데이터로 유도 불가),
그 경우 "2j×f" 는 정의상 1-jet MC 와 같아져 데이터와의 비교는 결국 **1-jet MC vs 1-jet data** 를 보는 것과 같다.

### 그래도 얻은 것 — 1-jet 고질량에서 MC 는 데이터를 잘 기술한다
native 1-jet MC 기준 data/MC = 1.02 (EE), 1.08 (MM). m_ll 분포는 400–1000 GeV 에서 ±10% 이내, 1.3 TeV 위에서 +40% (EE, 통계 작음).
조성: DY 61% / tt̄+tW 32% / Others 7% (EE). 같은 m_ll 의 2-jet SR topology 는 DY 33% / tt̄+tW 61% 로 **조성이 뒤집힌다**.
1-jet 고질량 데이터는 "고 m_ll 에서의 DY + tt̄ lepton kinematics" 검증으로는 쓸 만하지만, 2-jet SR 의 jet 관련 모델링 (m_lljj, jet pT) 은 검증하지 못한다.

## b-jet veto 에 대해 (질문: "b jet veto 하면 high mll 에서 더 깨끗한 Z 를 볼 수 있나")
- 1-jet, m_ll ≥ 400 에서 tt̄+tW 가 32–34% 다. 1-jet tt̄ event 의 그 jet 은 대부분 b jet 이므로 medium b-veto 로 tt̄ 를 1/4–1/5 로 줄일 수 있고, DY purity 는 60% → 85% 안팎으로 오를 것이다 (추정; 미측정).
- 다만 m_ll ≥ 400 은 Z peak 이 아니라 γ*/Z continuum 이라 "peak" 이 보이는 것은 아니고, DY 의 순도가 오르는 것이다.
- 이 dump (`HNWR_ChargeFlip`) 에는 b-tag 변수가 없다. BDT presel ntuple 에는 `nBJetMedium` 이 있지만 1-jet 영역이 없다. 하려면 dump analyzer 에 b-tag 를 추가해 재처리해야 한다.
- b-veto 를 1-jet 에만 걸면 2-jet SR (b-veto 없음) 과 선택이 달라진다. DY 만 비교하는 목적에는 문제없지만 b-tag SF 와 mistag 이 새 systematic 으로 들어온다.

## 파일
```
scripts/zpt_zeta_transfer_build.py      cache 생성 (dump 80개, 약 5분)
scripts/zpt_zeta_transfer_study.py      factor 유도 + 그림 (plot/HNWR_2024/cutbased 의 plotter 형식; MC-vs-MC 는 같은 헤더의 2-line ratio 그림)
data/zpt_zeta_transfer_events.npz       OS, hasPair, m_ll ≥ 60, (nJet==1 | SR topology)
AN_rawcharge/19_zpt_zeta_2j_to_1j/<EE|MM>/<DYwindow|highmass>/mc_closure/<var>.png        2-jet DY MC × f vs 1-jet DY MC
AN_rawcharge/19_zpt_zeta_2j_to_1j/<EE|MM>/<DYwindow|highmass>/data_vs_transferred_<var>_plot.png   1-jet data vs [2j DY MC × f + 1-jet non-DY MC]
AN_rawcharge/19_zpt_zeta_2j_to_1j/<EE|MM>/<DYwindow|highmass>/data_vs_native_<var>_plot.png        1-jet data vs native 1-jet MC
```
변수: m_ll, leading/subleading lepton pT, lepton η (EE 는 η_SC), dilepton pT, dilepton η.

## 추가 (2026-09-19 저녁): "DY CR 에서도 pT 가 올라가면 안 맞는 이유" — bin 폭이 아니라 ΔR(ℓℓ) cut

질문: Z pT bin 이 너무 넓어서 그런 것 아닌가? 기본 경계는 0,60,80,100,125,150,175,200,250,300,400,500,700,1000,∞ GeV.

1. **bin 은 실제로 넓었다.** MC entries 는 bin 당 수만–백만으로 충분한데, 한 bin 안에서 f 가 30–50% 변한다
   (200–250: 3.76→2.71, 300–400: 1.02→0.66, 0–60: 37→90).
2. **그런데 잘게 나눠도 꼬리는 그대로다** (`--binning fine`: Z pT 5 GeV 간격 (300 까지) / 10 / 25 / 50, |Z η| 0.25 간격; 출력 `19_zpt_zeta_2j_to_1j_fine/`).
   subleading pT 최대 편차 87% → 86%. 오히려 cell 이 1425 개로 늘어 2-jet event 가 없는 cell 이 생기고 (2D 값을 쓴 cell 776 개)
   Z pT 자체의 일치가 깨진다 (χ² 1.3/7 → 423/7, yield 0.98).
3. **진짜 원인**: 좁은 Z pT 구간 안에서 직접 비교하면 (EE, DY window, DY MC; `<l1 pT> / <l2 pT> / <A_pT>`, A_pT = (pT1−pT2)/(pT1+pT2))

   | Z pT [GeV] | 1-jet | 2-jet |
   |---|---|---|
   | 300–320 | 214 / 103 / 0.350 | 214 / 103 / 0.348 |
   | 400–420 | 290 / 125 / 0.397 | 290 / 125 / 0.400 |
   | 500–550 | 378 / 149 / 0.434, frac(l2 pT>150) = 0.47 | 426 / 99 / 0.621, frac = 0.07 |
   | 600–700 | 518 / 123 / 0.615 | 559 / 84 / 0.739 |

   450 GeV 아래는 완전히 같고 500 GeV 위에서만 갈라진다. m_ll ≈ 90 에서 Z pT ≈ 500 이면 대칭 붕괴의 ΔR(ℓℓ) ≈ 2m/pT ≈ 0.36 < 0.4.
   2-jet 의 `passResolved` 는 lepton–lepton ΔR > 0.4 를 요구하므로 대칭 붕괴 (subleading pT 가 큰 event) 가 2-jet 에서만 잘린다. 1-jet 에는 그 cut 이 없다.
4. **1-jet 에도 ΔR(ℓℓ) > 0.4 를 걸면 닫힌다** (`--drll`, 출력 `19_zpt_zeta_2j_to_1j_drll/`; 1-jet DY MC 의 0.14% 만 제거됨):
   EE DY window: leading pT 최대 편차 39.7% → **8.2%**, subleading 86.8% → **11.6%** (χ² 610→253, 1525→263). m_ll, η 는 그대로 (≤ 20%, ≤ 10%).
   남은 m_ll 60–80 GeV 의 +15–20% 와 η 의 5–10% 는 이 cut 과 무관한 별개의 잔차.
5. step B (같은 f 를 m_ll ≥ 400 에) 는 ΔR cut 과 무관하게 여전히 5.3배 어긋난다 — 그쪽 원인은 f 의 m_ll 의존 (아래 study 20).

옵션: `zpt_zeta_transfer_study.py [--binning fine] [--drll]` → 출력 폴더에 `_fine`, `_drll` 접미사.

## Study 20 — DY window 의 f 와 m_ll ≥ 400 의 f 를 MC 로 직접 비교 (`AN_rawcharge/20_factor_dywindow_vs_highmass/`)

DY MC 만, OS, 1-jet 에 ΔR(ℓℓ) > 0.4 적용. f = N(1 jet)/N(2 jet, SR topology). EE (MM 도 3% 이내로 같은 값):

| Z pT [GeV] | f, m_ll 60–150 | f, 150–400 | f, ≥ 400 | (≥400)/(60–150) |
|---|---:|---:|---:|---:|
| 0–60 | 70.8 ± 1.5 | 45.0 ± 0.6 | 8.96 ± 0.25 | 0.13 |
| 60–80 | 76.5 ± 1.5 | 49.0 ± 0.8 | 10.7 ± 0.4 | 0.14 |
| 80–100 | 51.1 ± 0.5 | 30.2 ± 0.5 | 7.56 ± 0.24 | 0.15 |
| 100–125 | 26.8 ± 0.2 | 16.8 ± 0.3 | 4.50 ± 0.13 | 0.17 |
| 125–150 | 14.8 ± 0.1 | 10.0 ± 0.2 | 2.85 ± 0.08 | 0.19 |
| 150–175 | 8.82 ± 0.05 | 6.36 ± 0.10 | 1.94 ± 0.06 | 0.22 |
| 175–200 | 5.62 ± 0.03 | 4.26 ± 0.07 | 1.53 ± 0.05 | 0.27 |
| 200–250 | 3.27 ± 0.01 | 2.62 ± 0.04 | 1.14 ± 0.03 | 0.35 |
| 250–300 | 1.73 ± 0.01 | 1.46 ± 0.02 | 0.83 ± 0.03 | 0.48 |
| 300–400 | 0.869 ± 0.004 | 0.805 ± 0.012 | 0.656 ± 0.024 | 0.76 |
| 400–500 | 0.496 ± 0.004 | 0.541 ± 0.011 | 0.641 ± 0.023 | 1.29 |
| 500–700 | 0.442 ± 0.008 | 0.463 ± 0.012 | 0.536 ± 0.023 | 1.21 |
| 700–1000 | 0.386 ± 0.028 | 0.418 ± 0.018 | 0.398 ± 0.022 | 1.03 |

전체 비율: 8.41 / 15.36 / 3.56. 2D 로 보면 (≥400)/(60–150) 은 |Z η| 가 작을수록 더 작다: Z pT 0–60 에서 |η|<1: 0.05, 1–2: 0.07, 2–3: 0.17, >3: 0.32;
Z pT 200–250 에서 0.27 / 0.43 / 0.58; Z pT ≥ 400 에서는 |η| 와 무관하게 1.2–1.5.

**읽는 법**: factor 는 비슷하지 않다. Z pT ≲ 300 GeV 에서 고질량의 f 는 DY window 의 1/8–1/2 이고, Z pT 가 커질수록 1 에 가까워져 400 GeV 위에서는 같아진다 (1.0–1.3).
2-jet 정의의 m_lljj > 800 이 원인이다: m_ll ≈ 90 이면 jet 들이 (따라서 recoil 하는 Z 가) 매우 세야 이 조건을 넘지만, m_ll ≥ 400 이면 Z pT 가 작아도 넘는다.
Z pT 가 충분히 크면 두 경우 모두 m_lljj > 800 이 자동으로 만족되어 f 가 jet multiplicity 만의 비율로 수렴한다. 150–400 은 그 중간.
그림: `factor_vs_zpt_<EE|MM>_allEta.png`, `..._eta0..3.png` (세 m_ll 구간의 f 와 DY window 대비 비율), 수치 `summary.json`. 코드 `scripts/zpt_zeta_factor_compare.py`.

## Study 21 — m_ll 구간별 dilepton pT shape (`AN_rawcharge/21_zpt_shape_vs_mll/`)

DY MC, OS, 면적 1 (1/N dN/dpT, GeV 당). m_ll 구간 8개 (60–80, 80–100, 100–150, 150–250, 250–400, 400–700, 700–1000, ≥1000) 를 한 그림에 겹침,
아래 패널은 Z peak (80–100) 대비 비율. 1-jet (ΔR(ℓℓ)>0.4 포함) 과 2-jet SR topology 를 각각, EE / MM. 코드 `scripts/zpt_shape_vs_mll.py`.

| m_ll [GeV] | 1-jet <pT> / median / pT<100 비율 | 2-jet <pT> / median / pT<100 비율 |
|---|---|---|
| 60–80 | 153 / 139 / 7% | 221 / 207 / 1% |
| 80–100 | 141 / 127 / 23% | 239 / 219 / 3% |
| 100–150 | 100 / 86 / 61% | 225 / 203 / 13% |
| 150–250 | 80 / 67 / 78% | 192 / 160 / 29% |
| 250–400 | 93 / 77 / 69% | 201 / 173 / 24% |
| 400–700 | 104 / 84 / 62% | 196 / 168 / 23% |
| 700–1000 | 120 / 95 / 54% | 183 / 150 / 27% |
| ≥1000 | 147 / 117 / 38% | 202 / 161 / 24% |

(EE 값; MM 은 ±3 GeV 이내로 같다.)

보이는 것:
1. **낮은 pT 의 문턱이 m_ll 에 따라 움직인다.** lepton pT > 60/53 cut 때문에 m_ll < 100 이면 pT(ll) ≳ 53 GeV 가 되어야 하고 (60–80 에서는 ≳ 80), m_ll 이 커지면 pT(ll) ≈ 0 까지 채워진다.
   그래서 1-jet 의 pT<100 비율이 Z peak 에서 23% 인데 150–250 에서 78% 로 뛴다. 이것이 DY window 와 고질량의 Z pT 분포 (따라서 f) 가 다른 가장 큰 이유 중 하나다.
2. **2-jet 은 Z peak 에서 훨씬 단단하다** (평균 239 vs 고질량 ~195). m_lljj > 800 을 m_ll ≈ 90 으로 넘기려면 센 recoil 이 필요하기 때문. 고질량 (≥150) 의 2-jet shape 은 m_ll 에 거의 무관하다 (평균 183–202).
3. **m_ll < 150 곡선은 pT > 500 GeV 에서 급락한다** (1-jet, 2-jet 모두). ΔR(ℓℓ) > 0.4 가 boost 된 Z (ΔR ≈ 2m/pT) 를 자르기 때문. 고질량 곡선은 계속 이어진다.
4. 1-jet 의 고 pT 꼬리는 m_ll 이 클수록 단단해진다 (pT 300–500 에서 ≥1000 곡선이 Z peak 의 2–2.5배).

### Study 21b — 반대로: pT(ll) 구간별 m_ll shape (`mll_shape_vs_zpt_<EE|MM>_<1jet|2jet>.png`, 수치 `summary_mll_vs_zpt.json`)

질문: "Z pT 가 낮으면 m_ll 이 높은 쪽에 몰리고, Z pT 가 높으면 상대적으로 낮은 m_ll 이 많아지나?" — 그렇다. EE, DY MC, OS:

| pT(ll) [GeV] | 1-jet: Z peak (80–100) 비율 / m_ll ≥ 150 / ≥ 400 / 최소 m_ll | 2-jet (SR topology) |
|---|---|---|
| 0–50 | **0%** / 59.3% / 2.8% / 102 GeV | 0% / 72.9% / 14.9% / 105 |
| 50–100 | 62% / 19.9% / 1.4% / 60 | 57% / 28.9% / 7.4% |
| 100–150 | 86% / 4.5% / 0.47% | 82% / 8.1% / 2.4% |
| 150–200 | 87% / 3.5% / 0.44% | 85% / 5.8% / 1.8% |
| 200–300 | 87% / 3.8% / 0.57% | 85% / 5.4% / 1.5% |
| 300–500 | 87% / 4.9% / 0.98% | 86% / 5.2% / 1.2% |
| ≥ 500 | 69% / 17.9% / 5.5% | 70% / 17.0% / 4.9% |

원인은 lepton pT cut (60 / 53 GeV) 의 acceptance 다: 질량을 무시하면 m_ll² + pT(ll)² ≥ (pT1 + pT2)² > 113² 이므로
pT(ll) < 50 이면 m_ll > 100 GeV 여야 한다 → Z peak 이 통째로 사라지고 남는 것은 전부 continuum. pT(ll) 가 100 GeV 를 넘으면 Z peak 이 cut 을 통과하기 시작해
(단면적이 압도적으로 커서) 86–87% 를 차지하고 고질량 비율은 수 % 로 떨어진다. pT(ll) ≥ 500 에서 Z peak 비율이 다시 69% 로 내려가는 것은 ΔR(ℓℓ) > 0.4 가 boost 된 Z 를 자르기 때문 (study 19 추가분).

## Study 22 — m_lljj > 800 을 빼면 m_ll (≥150) shape 이 jet 수와 무관한가 (`AN_rawcharge/22_mll_shape_jetdef/`)

DY MC, OS, m_ll ≥ 150 안에서 면적 1. 모든 category 에 ΔR(ℓℓ) > 0.4. 2-jet 정의 3단계를 1-jet 과 비교 (EE; MM 도 같은 경향).
cache `data/dy_jetdef_events.npz` (DY dump 14개, nJet ≥ 1 전부), 코드 `scripts/mll_shape_jetdef_compare.py`.

ratio = (2-jet 정의) / (1-jet), m_ll bin = 150–200, 200–250, 250–300, 300–400, 400–500, 500–700, 700–1000, 1000–2000:

| 2-jet 정의 | Z pT 전체 | 0–50 | 50–100 | 100–200 | 200–300 | 300–500 | ≥500 |
|---|---|---|---|---|---|---|---|
| **nJet ≥ 2** | 0.98 0.98 1.01 1.02 1.06 1.11 1.33 1.77 | 1.05 … 0.84 0.87 0.97 1.66 | 1.03 … 0.89 0.90 1.03 1.79 | 최대 편차 11% | 14% | 11% | 20% (통계) |
| nJet ≥ 2 + resolved | 위와 동일 (resolved 가 제거하는 event 는 13427 중 1개) | | | | | | |
| + m_lljj > 800 (SR topology) | 0.60 0.78 1.04 1.46 2.26 3.91 6.27 8.37 | 0.64 … 18.1 | 0.62 … 14.2 | 최대 4.8배 | 2.5배 | 11% | 20% |

**읽는 법**
- m_lljj cut 을 빼면 m_ll shape 은 jet 수와 거의 무관하다: 150–700 GeV 에서 ±11% 이내, Z pT 구간별로도 ±10–16%.
  `passResolved` (ΔR 조건들) 는 이 영역에서 사실상 아무 것도 자르지 않는다.
- 남는 차이는 **m_ll ≥ 700 의 꼬리**: Z pT 전체에서 700–1000 이 ×1.33, ≥1000 이 ×1.77. Z pT < 100 에서 온다 (×1.66–1.79); Z pT ≥ 100 에서는 없다.
  즉 아주 높은 질량에서는 jet 이 2개 이상인 event 가 상대적으로 더 많다 (hard process 의 scale 이 클수록 radiation 이 많아지는 효과로 해석 — 미검증).
- SR topology 에서 보이던 큰 기울기 (0.6 → 8.4) 는 **전부 m_lljj > 800 한 줄**에서 온다.
- 함의: "1-jet 의 m_ll shape 을 2-jet 에 쓴다" 는 것은 **m_lljj cut 이전 단계**에서는 (700 GeV 아래) 성립한다. SR 은 m_lljj > 800 이 필수이므로,
  1-jet 에서 가져온 것에 "m_ll 별 m_lljj>800 통과 확률" 을 따로 곱해야 하는데, 그 확률은 jet kinematics 에 달려 있어 1-jet 에서는 얻을 수 없다 (MC 나 2-jet 데이터 필요).

그림: `mll_shape_jetdef_<EE|MM>_{allZpt,Zpt0to100,Zpt100to300,Zpt300toInf}.png` (네 category 겹침 + 1-jet 대비 비율). 파란선 (nJet≥2) 은 초록선 (resolved) 에 완전히 가려진다.

## Study 22 추가 — (a) 왜 m_ll ≳ 700 에서 1-jet 과 2-jet 이 갈라지나, (b) m_lljj > 800 을 1-jet 에도 정의되는 변수로 대체할 수 있나

**(a)** N(nJet≥2)/N(nJet==1), EE (MM 도 같은 값): Z pT 전체 0.380 (150–200) → 0.428 (500–700) → 0.513 (700–1000) → 0.648 (1000–1500) → 0.97 (1500–2000).
700 에서 갑자기 갈라지는 게 아니라 **m_ll 에 따라 서서히 커지다가 1 TeV 위에서 가팔라지는** 경향이다. 구간별로는
Z pT < 100: 0.275 → 0.22 (400–700) → 0.25 → **0.41 → 0.69**; Z pT ≥ 100: 0.73–0.80 으로 평평하다가 1.5 TeV 위에서 ~1.0.
- EE = MM → 전자가 jet 으로 잡히는 식의 검출기 효과가 아니다.
- DY 보정을 전부 뺀 weight (`weight/w_dy`) 로도 같은 모양 (0.134 → 0.150 → 0.242 → 0.376) → 보정 (2-jet 에만 걸리는 R ≈ ×1.7, m_ll 무관) 때문도 아니다.
- 1-jet 의 jet pT 평균 63–69 GeV, 2-jet 의 (j1, j2) = (90, 62) GeV 로 m_ll 에 거의 무관 — jet 자체가 세지는 게 아니라 **jet 이 2개 이상일 확률**이 m_ll 과 함께 커진다.
- 해석 (미검증): hard scale 이 클수록 ISR 이 많아지는 일반적 경향 (LO MadGraph + MLM). 데이터에서도 그런지는 1-jet/2-jet 고질량 데이터 비교가 필요한데 2-jet 고질량은 SR.

**(b)** 2-jet resolved DY MC (EE) 에서 "m_lljj > 800 과 같은 효율이 되도록 threshold 를 잡은 X > X0" 가 m_lljj > 800 과 얼마나 같은 event 를 고르는지
(효율을 맞췄으므로 '통과 비율' = '순도'):

| X | DY window (m_lljj>800 비율 15.6%) threshold / 겹침 / 상관계수 | m_ll ≥ 400 (비율 64.6%) threshold / 겹침 / 상관계수 |
|---|---|---|
| Z pT | 226 GeV / 47% / 0.54 | 107 GeV / 73% / 0.52 |
| HT2 = j1 + j2 | 331 / 63% / 0.76 | 145 / 78% / 0.66 |
| S_T = l1 + l2 + j1 + j2 | 560 / 64% / 0.79 | 591 / 82% / 0.78 |
| m_ll + HT2 | 423 / 63% / 0.76 | 658 / 87% / 0.81 |
| sqrt(m_ll² + Z pT²) + HT2 | 568 / 64% / 0.79 | 679 / 87% / 0.83 |

- 어떤 변수도 m_lljj > 800 을 잘 흉내내지 못한다: DY window 에서 겹침이 최대 64% (Z pT 는 47%), m_ll ≥ 400 에서 최대 87%.
  m_lljj 는 네 물체의 **각도** (jet–jet, lepton–jet 의 벌어짐) 에 크게 의존하는데 pT 합에는 그 정보가 없다.
- 또 **같은 threshold 가 두 m_ll 영역에서 통하지 않는다**: Z pT 226 vs 107, HT2 331 vs 145. S_T 만 560 vs 591 로 비슷하다 (S_T ≈ 질량 scale 을 가장 잘 따라감).
- 1-jet 에 그대로 쓰려면 HT2 → j1, S_T → l1+l2+j1 인데, 1-jet 의 S_T 분포는 jet 하나가 빠진 만큼 구조적으로 낮아 "같은 cut" 의 의미가 달라진다.
- 더 근본적으로: fit 변수가 m_lljj 이고 800 GeV 부터 시작하므로, 영역 정의에서 m_lljj cut 을 빼더라도 histogram 에 들어가는 event 는 결국 m_lljj > 800 이다.
  대체 cut 은 "SR 의 정의" 가 아니라 "SR 에 가까운 보조 영역" 을 만드는 용도로만 의미가 있다.

## Study 23 — m_ll bin 별로 1-jet/2-jet normalization 을 맞춘 뒤, Z pT 비율이 m_ll 과 무관한가 (`AN_rawcharge/23_zpt_ratio_vs_mll_normalised/`)

질문: 2-jet/1-jet 의 m_ll 의존을 normalization 으로 흡수하면 (m_ll bin 마다 따로 정규화) 남는 Z pT 비율 r(Z pT | m_ll) = shape_2j / shape_1j 이
모든 m_ll bin 에서 같은가 — 즉 factor 가 g(m_ll) × h(Z pT) 로 **factorise** 하는가. study 20 은 m_ll 3구간의 절대 factor 만 봤고 이 형태로는 보지 않았다.

DY MC 만, OS, 모든 category 에 ΔR(ℓℓ) > 0.4. m_ll 8 bin (60–150, 150–200, 200–300, 300–400, 400–500, 500–700, 700–1000, ≥1000), Z pT 10 bin (0–50–…–1000).
2-jet 정의 두 가지: `ge2j` (nJet ≥ 2; `ge2j_res` = +passResolved 는 수치가 같다), `SRtopo` (+ m_lljj > 800). 입력 `data/dy_jetdef_events.npz`.
"평탄도": r_k / r_ref 를 Z pT 10 bin 에 걸쳐 상수 c 로 fit → chi2/ndf 와 (r_k/r_ref)/c 의 min..max (`flatness.txt`).

### (1) m_lljj > 800 이 **없으면** (`ge2j`): m_ll 150–700 안에서는 factorise 한다 (EE; MM 도 같은 결과)

| m_ll bin | g = N2j/N1j | 기준 150–200: c | chi2/ndf | (r/r_ref)/c 범위 |
|---|---:|---:|---:|---|
| 60–150 | 0.761 | 0.609 | 174 | 0.82 – 1.25 |
| 150–200 | 0.380 | (기준) | | |
| 200–300 | 0.383 | 0.932 | 2.8 | 0.92 – 1.09 |
| 300–400 | 0.396 | 0.844 | 1.7 | 0.92 – 1.13 |
| 400–500 | 0.409 | 0.797 | 1.9 | 0.93 – 1.16 |
| 500–700 | 0.429 | 0.748 | 1.0 | 0.92 – 1.10 |
| 700–1000 | 0.513 | 0.667 | 3.2 | 0.77 – 1.21 |
| ≥ 1000 | 0.684 | 0.511 | 4.7 | 0.80 – 1.88 |

- 150 ≤ m_ll < 700: Z pT 비율의 모양이 ±10% 안에서 같다 (chi2/ndf 1–3). 상수 c 가 1 이 아닌 것은 1-jet 의 Z pT shape 자체가 m_ll 에 따라 달라 정규화 분모가 바뀌기 때문이며, 모양이 같다는 결론과 모순이 아니다.
- **DY window (60–150) 는 같은 모양이 아니다** (chi2/ndf 174): Z pT 50–100 에서 상대적으로 30% 낮고 그 외에서는 평평. lepton pT cut 이 Z peak 의 저 pT(ll) 영역을 깎는 것 (study 21: m_ll² + pT(ll)² > 113²) 이 1-jet 과 2-jet 에 다르게 작용한다.
  Z pT ≥ 100 만 보면 DY window 도 ±10% 로 평평하다 (r/r(60–150) = 1.71–2.01 @150–200).
- m_ll ≥ 700 부터 어긋난다: 저 Z pT (< 100) 에서 2-jet 비율이 상대적으로 커진다 (≥1000 에서 최대 1.9배). study 22 (a) 에서 본 고질량의 jet multiplicity 증가와 같은 현상.

### (2) m_lljj > 800 이 **있으면** (`SRtopo`): factorise 하지 않는다

| m_ll bin | g | 기준 60–150: c | chi2/ndf | (r/r_ref)/c 범위 |
|---|---:|---:|---:|---|
| 150–200 | 0.049 | 2.64 | 8.8 | 0.89 – 1.11 |
| 200–300 | 0.071 | 2.11 | 53 | 0.69 – 1.44 |
| 300–400 | 0.120 | 1.40 | 114 | 0.60 – 2.19 |
| 400–500 | 0.185 | 0.97 | 131 | 0.53 – 2.98 |
| 500–700 | 0.320 | 0.52 | 242 | 0.55 – 7.0 |
| 700–1000 | 0.513 | 0.26 | 150 | 0.58 – 17 |
| ≥ 1000 | 0.684 | 0.21 | 47 | 0.62 – 28 |

r / r(60–150) 가 Z pT 0–50 에서 2.9–5.8, Z pT ≥ 400 에서 0.13–0.5: m_ll bin 별 정규화로는 흡수되지 않는 **기울기** 차이다 (m_ll 400–500 에서 저/고 Z pT 사이에 ×5.6, 700–1000 에서 ×26).
DY window 와 150–200 만 서로 비슷하다 (±11%). m_lljj > 800 이 m_ll 과 Z pT 를 직접 묶기 때문 (m_ll 이 크면 Z pT 가 작아도 통과) — study 20/21 의 결론과 같다.
m_ll ≥ 700 에서는 `SRtopo` 와 `ge2j` 의 수치가 같다 (m_lljj > 800 이 자동 만족).

### 결론
- "m_ll 은 normalization 으로, Z pT 는 공통 shape 으로" 라는 분리는 **m_lljj cut 이 없는 2-jet 정의에서만, m_ll 150–700 에서** 성립한다 (±10%).
- SR 정의 (m_lljj > 800) 에서는 성립하지 않으므로, DY window 에서 구한 h(Z pT) 를 m_ll ≥ 400 에 쓰려면 m_ll bin 별 normalization 만으로는 부족하고 2D (m_ll, Z pT) factor 가 필요하다 — MC 로만 구할 수 있다.

그림: `zpt_ratio_vs_mll_<EE|MM>_<ge2j|ge2j_res|SRtopo>.png` (위: m_ll bin 별 r(Z pT), 아래: DY window 대비). 수치 `summary.json`, `flatness.txt`, 전체 표 `run.log`.
코드 `scripts/zpt_ratio_vs_mll_normalised.py` (재실행: `cd plot/HNWR_2024/cutbased; ./condor/in_container.sh python3 studies/chargeflip/scripts/zpt_ratio_vs_mll_normalised.py`, 약 2분).

## Study 24 — 2D factor f(m_ll, Z pT) 로 2-jet DY MC 를 1-jet 으로 옮기기 (`AN_rawcharge/24_mll_zpt_2d_factor_drll/`)

study 23 의 결론 (SR 정의에서는 m_ll normalization + 공통 Z pT shape 으로 분리되지 않는다) 을 받아, factor 자체를 **(m_ll, Z pT) 2D** 로 만들었다.

    f(m_ll, Z pT) = N_DY^MC(1 jet) / N_DY^MC(2 jet, SR topology)     ← DY MC, OS, m_ll ≥ 60 **전 구간**에서 유도 (EE/MM 별), 1-jet 에 ΔR(ℓℓ) > 0.4
    m_ll 21 bin (60,70,80,85,90,95,100,110,130,150,200,250,300,400,450,500,600,700,800,1000,1300,∞) × Z pT 16 bin (0,25,…,200,250,300,400,500,600,800,1000,∞)
    양쪽 N_eff ≥ 30 인 cell 만 2D 값 (EE 279/336, MM 287/336), 나머지는 m_ll-only factor

코드는 study 19 의 `scripts/zpt_zeta_transfer_study.py` 에 `--factor mll_zpt` 옵션을 추가한 것 (기본값 `zpt_zeta` 는 study 19 그대로).
주의: 이 f 는 고질량 cell 을 고질량 MC 에서 구하므로 **yield, m_ll, Z pT 는 정의상 닫힌다.** 의미 있는 시험은 f 에 들어가지 않은 변수 (lepton pT, lepton η, Z η) 와 flip-weight 합이다.

### MC closure (2-jet DY MC × f vs 1-jet DY MC; yield 를 맞춘 뒤의 shape)

| 변수 | EE DY window | EE m_ll ≥ 400 | MM DY window | MM m_ll ≥ 400 |
|---|---|---|---|---|
| yield (2j×f / 1j) | 1.000 | 1.000 (751.9 → 2674.8 vs 2675.0) | 1.000 | 1.000 |
| m_ll | χ² 17/17 | 2.0/7 | 18/17 | 0.1/7 |
| dilepton pT | 131/7 (꼬리의 fallback cell) | 39/7 (> 600 GeV 에서 +30%) | 195/7 | 14/7 |
| leading lepton pT | 525/8, 최대 21% | 31/9; 100–1000 GeV 에서 ±10%, > 1 TeV +86% (event ~2) | 707/8 | 54/9 |
| subleading lepton pT | 391/8, 최대 12% | 16/9, 최대 13% | 628/8 | 42/9 |
| **leading lepton η** | **30,000/9, 최대 145%** | **75/9: \|η\|<0.5 에서 −12%, \|η\|>2 에서 +34%** | 38,000/9 | 69/9, 최대 20% |
| subleading lepton η | 26,500/9 | 24/9, 최대 16% | 31,800/9 | 32/9, 최대 15% |
| dilepton η | 34,000/19 | 86/19 | 43,000/19 | 116/19 |

- study 19 의 step B (DY window 의 f 를 고질량에 → yield 5.3배, lepton pT 최대 +180%) 와 비교하면 **lepton pT 는 2D factor 로 닫힌다** (±10%).
- **η 는 닫히지 않는다.** 같은 (m_ll, Z pT) 에서도 2-jet SR topology 의 전자가 더 forward 다. DY window 에서는 극단적 (m_lljj > 800 을 m_ll≈90 으로 넘기려면 계 전체가 boost — study 17 과 같은 현상),
  m_ll ≥ 400 에서는 완만 (−12% … +34%).

### 1-jet 데이터와 비교 (`data_vs_transferred_*_plot.png`, `data_vs_native_*_plot.png`)
data / (2j DY×f + 1-jet non-DY MC) = 1.024 (EE), 1.076 (MM) at m_ll ≥ 400 — native 1-jet MC 기준 (1.023, 1.076) 과 같다 (yield 가 정의상 같으므로).
lepton η 분포는 데이터와 ±10% 안에서 맞는다 (2-jet 의 forward 초과가 그대로 보이지는 않는 수준; DY 는 전체의 61%).

### Study 24b — flip-weight 합으로 본 결과 (`sigma_w.txt`, `sigma_w.json`; 코드 `scripts/mll_zpt_2d_sigma_w.py`)

EE, OS, w = `sf3` json 의 flip weight. "transferred" = 2-jet DY MC × f + 1-jet non-DY MC.

| m_ll | Σw 1-jet data | Σw native 1-jet MC (data/MC) | Σw transferred (data/MC) | ⟨w⟩ DY: native 1j | 2j × f | 2j (f 없이) |
|---|---:|---:|---:|---:|---:|---:|
| 60–150 | 5959 ± 17 | 5121 (1.164) | 8804 (0.677) | 0.01763 | 0.03080 | 0.03017 |
| 150–400 | 1334 ± 8 | 1203 (1.109) | 1765 (0.756) | 0.02323 | 0.04078 | 0.03662 |
| ≥ 400 | 182.1 ± 3.5 | 165.5 (1.100) | 177.3 (1.027) | 0.03827 | 0.04268 | 0.04124 |
| ≥ 700 | 28.2 ± 1.5 | 24.3 (1.159) | 24.2 (1.162) | 0.04608 | 0.04602 | 0.04595 |

- yield·m_ll·Z pT 를 다 맞췄는데도 **event 당 평균 flip weight 가 다르다**: DY window 에서 2j×f 가 native 1-jet 의 1.75배, 150–400 에서 1.76배, ≥ 400 에서 1.12배, ≥ 700 에서 같다.
  전적으로 전자 η 차이에서 온다 (flip 확률은 endcap 에서 크다).
- m_ll ≥ 400 의 data/transferred = 1.027 은 "잘 맞는다" 가 아니라 **우연한 상쇄**: native MC 가 데이터보다 10% 작은 것 (study 18 추가분) 을 2-jet 의 forward 초과 (+12%) 가 메운 것이다.
- m_ll ≥ 700 에서는 m_lljj > 800 이 자동 만족이라 2-jet 과 1-jet 의 lepton kinematics 가 같아지고 (⟨w⟩ 동일), 데이터와의 16% 차이가 그대로 남는다.

### 결론
1. (m_ll, Z pT) 2D factor 는 lepton **pT** 까지는 옮겨 준다. **η 는 못 옮긴다.** flip 예측에 중요한 것은 η 이므로, 이 전달을 flip 용 검증에 쓰려면 factor 에 lepton η (또는 Z η) 가 더 들어가야 한다 → 3D 이상.
2. 그러나 factor 의 차원을 늘릴수록 "2j×f" 는 정의상 native 1-jet MC 에 수렴하고, 데이터와의 비교는 **1-jet MC vs 1-jet data** 와 같아진다 (study 19 에서 이미 지적한 점).
   즉 이 경로로 알 수 있는 것은 "1-jet 고질량에서 MC 가 데이터의 w-가중 yield 를 10–16% 과소 예측한다" 는 사실까지이고, 2-jet SR 의 OS MC 자체에 대한 독립 검증은 되지 않는다.
3. 2-jet 고유의 정보 (forward 쏠림, m_lljj) 를 데이터로 검증하려면 2-jet 데이터가 필요하다: DY CR (열려 있음, 이미 1.001), eμ flavor CR (열려 있음, 미실시), 2-jet 150 < m_ll < 400 sideband (열지 여부 미정).

### 파일
```
scripts/zpt_zeta_transfer_study.py --factor mll_zpt --drll --out-dir .../24_mll_zpt_2d_factor     (약 5분)
scripts/mll_zpt_2d_sigma_w.py                                                                     (numpy 만, 1분)
AN_rawcharge/24_mll_zpt_2d_factor_drll/summary.json          f (2D 배열, edges: 이 모드에서는 "zpt_edges" = m_ll, "zeta_edges" = Z pT), yield, closure χ²
AN_rawcharge/24_mll_zpt_2d_factor_drll/run.log, sigma_w.txt  위 표의 원본 출력
AN_rawcharge/24_mll_zpt_2d_factor_drll/<EE|MM>/<DYwindow|highmass>/mc_closure/<var>.png
AN_rawcharge/24_mll_zpt_2d_factor_drll/<EE|MM>/<DYwindow|highmass>/data_vs_{transferred,native}_<var>_plot.png
```

## Study 24c — (질문: "m_ll, Z pT 로 잘 맞는 것 아닌가") 1-jet 데이터는 두 MC 중 어느 쪽 η 를 선호하나 (`eta_datacheck.txt`, `.json`; 코드 `scripts/mll_zpt_2d_eta_datacheck.py`)

EE, OS, 1-jet, m_ll ≥ 400. 전자 |η_SC| 6 bin (0, 0.5, 1.0, 1.4442, 1.566, 2.0, 2.5). shape χ² 는 yield 를 맞춘 뒤, 데이터 통계 오차만.

| | leading: data/MC per bin (gap 제외) | χ²/ndf | endcap 비율 | subleading: χ²/ndf | endcap 비율 |
|---|---|---:|---:|---:|---:|
| data | 1104 / 1146 / 873 / 737 / 643 | | 0.306 ± 0.006 | | 0.315 |
| native 1-jet MC | 0.95 / 0.99 / 0.96 / 1.10 / **1.27** | **38.5/4** | 0.267 | 17.8/4 | 0.287 |
| 2j DY×f + 1j non-DY | 1.03 / 1.02 / 0.97 / 1.03 / 1.08 | **4.3/4** | 0.297 | 8.9/4 | 0.299 |
| (DY 만) 2j×f / native 1j | 0.88 / 0.96 / 0.98 / 1.12 / 1.32 | | | 0.97 / 0.95 / 1.01 / 1.02 / 1.16 | |

**study 24b 의 해석을 고친다.** 거기서 m_ll ≥ 400 의 data/transferred Σw = 1.027 을 "우연한 상쇄" 라고 썼는데, η 분포를 직접 보면
**1-jet 데이터가 native 1-jet MC 보다 forward 이고 (|η|>2 에서 data/MC 1.27), 2j×f 가 그 데이터와 더 잘 맞는다** (χ² 4.3/4 vs 38.5/4). 즉 m_ll ≥ 400 에서는 (m_ll, Z pT) 전달이 데이터 기준으로 잘 맞는 것이 사실이다.

다만 "왜 맞는가" 는 이 시험으로 갈리지 않는다:
- 2j×f 가 native 1-jet MC 보다 forward 인 이유는 MC 안에서 분명하다 (m_lljj > 800 선택). 1-jet **데이터**가 1-jet MC 보다 forward 인 이유는 모른다 (DY MC 의 1-jet η 모델링, PDF, 또는 1-jet 에 R 보정이 없는 것 등 — 미확인).
  두 효과의 크기가 m_ll ≥ 400 에서 비슷해서 (+12% vs +10% in Σw) 맞아떨어진다.
- 같은 방법이 통계가 훨씬 많은 낮은 질량에서는 **크게 틀린다**: data/transferred Σw = 0.677 (60–150), 0.756 (150–400) — 거기서는 2j×f 가 데이터보다 훨씬 forward 다.
  방법이 원리적으로 옳다면 모든 m_ll 에서 맞아야 하므로, m_ll ≥ 400 의 일치를 "검증됨" 으로 읽기는 어렵다. m_ll ≥ 700 에서는 2j×f = native (⟨w⟩ 동일) 인데 데이터와 16% 차이가 남는다.
- 실용적으로는: m_ll ≥ 400 의 1-jet 데이터는 **2-jet SR DY MC 의 전자 (pT, η) 분포와 모순되지 않는다** (pT ±10%, η χ² 4.3/4, Σw 1.03). 이것은 OS MC × w 의 DY 성분에 대한 (약한) 긍정적 점검으로 쓸 수 있다.

## Study 24d — (질문: "700 이상은 binning 때문 아닌가, 200–400 은?") m_ll slice 별 결과와 f binning 의존 (`slices.txt`, `slices.json`; 코드 `scripts/mll_zpt_2d_slices.py`)

EE, OS, 1-jet, ΔR(ℓℓ) > 0.4. f(m_ll, Z pT) 를 세 가지 binning 으로 다시 유도: nominal (21×16, study 24 와 동일), fine (45×44; m_ll 5/25/50 GeV 폭, Z pT 10/25 GeV 폭), coarse (8×8).
오차: data 는 √Σw², MC 는 √Σ(weight·w·f)². η χ² 는 leading 전자 |η_SC| 5 bin shape (데이터 통계만, ndf 4).

| m_ll | N data / native MC | Σw data/native | Σw data/transferred | DY ⟨w⟩ native / 2j×f | η χ²: native / transf. | endcap 비율 data / native / transf. |
|---|---|---:|---:|---|---|---|
| 150–200 | 28,671 / 27,228 | 1.150 ± 0.011 | 0.712 ± 0.011 | 0.0202 / 0.0388 | 126 / 3753 | 0.238 / 0.212 / 0.375 |
| 200–300 | 23,529 / 23,068 | 1.089 ± 0.011 | 0.768 ± 0.011 | 0.0249 / 0.0427 | 80 / 1396 | 0.246 / 0.222 / 0.339 |
| 300–400 | 6,823 / 6,906 | 1.058 ± 0.018 | 0.866 ± 0.019 | 0.0312 / 0.0434 | 20 / 90 | 0.269 / 0.247 / 0.312 |
| **200–400** | 30,352 / 29,974 | **1.080 ± 0.009** | **0.792 ± 0.009** | 0.0264 / 0.0428 | **97 / 1361** | 0.251 / 0.228 / 0.333 |
| 400–500 | 2,393 / 2,444 | 1.077 ± 0.029 | 0.953 ± 0.031 | 0.0350 / 0.0427 | 33 / 5.8 | 0.311 / 0.262 / 0.307 |
| 500–700 | 1,557 / 1,454 | 1.108 ± 0.036 | 1.088 ± 0.039 | 0.0402 / 0.0413 | 8.4 / 3.6 | 0.310 / 0.277 / 0.289 |
| 700–1000 | 434 / 404 | 1.120 ± 0.067 | 1.122 ± 0.070 | 0.0452 / 0.0448 | 2.4 / 3.8 | 0.281 / 0.274 / 0.280 |
| ≥ 1000 | 119 / 97.6 | 1.30 ± 0.15 | 1.31 ± 0.16 | 0.0494 / 0.0506 | 4.7 / 6.8 | 0.269 / 0.227 / 0.242 |
| **≥ 700** | 553 / 501.5 | **1.159 ± 0.062** | **1.162 ± 0.064** | 0.0461 / 0.0460 | 4.7 / 4.9 | 0.278 / 0.265 / 0.273 |

### (1) m_ll ≥ 700 의 16% 는 f 의 binning 때문이 아니다
- data/transferred: nominal 1.162, fine 1.176, coarse 1.158 — binning 을 5배 잘게/3배 거칠게 해도 1–2% 안에서 같다.
- 애초에 이 구간에서는 m_lljj > 800 이 자동 만족이라 2j×f 와 native 1-jet MC 가 같다 (Σw 24.23 vs 24.30, ⟨w⟩ 0.0460 vs 0.0461). 즉 16% 는 전달과 무관한 **1-jet data vs MC 차이** 다.
- 구성: event 수 553 / 501.5 = 1.10 ± 0.05 가 대부분이고, ⟨w⟩ 가 5% 더 (0.0509 vs 0.0485). 통계적으로 2.5σ; ≥ 1000 (119 vs 97.6) 의 기여가 크다. study 19 에서 본 "m_ll > 1.3 TeV 에서 data/MC +40%" 와 같은 초과.

### (2) 200–400 에서는 전달이 **안 맞는다**
- data/transferred Σw = 0.79 ± 0.01, η shape χ² 1361/4 (native 는 97/4). 2j×f 의 endcap 비율 0.333 vs 데이터 0.251.
- 원인은 study 17/24 와 같다: m_ll 이 작을수록 m_lljj > 800 을 넘기 위해 계 전체가 boost 되어 2-jet SR topology 의 전자가 forward 로 쏠리는데, (m_ll, Z pT) 는 이 η 차이를 옮기지 못한다.

### (3) 전체 그림 — m_ll ≥ 400 의 일치는 "교차점" 이다
endcap 비율을 m_ll 순서로 보면
- 2j×f : 0.375 → 0.339 → 0.312 → 0.307 → 0.289 → 0.280 (m_ll 이 커질수록 **감소**, native 로 수렴)
- native: 0.212 → 0.222 → 0.247 → 0.262 → 0.277 → 0.274 (증가)
- data  : 0.238 → 0.246 → 0.269 → 0.311 → 0.310 → 0.281 (**모든 구간에서 native 보다 0.02–0.05 높다**)

데이터는 m_ll 전 구간에서 native MC 보다 일관되게 forward 이고 (Σw 로 +6–15%), 2j×f 는 위에서 내려오다가 400–500 근처에서 데이터와 만난다.
따라서 m_ll ≥ 400 에서 2j×f 가 native 보다 데이터에 잘 맞는 것은 사실이지만 (24c), 전달이 옳아서라기보다 두 곡선이 그 질량에서 교차하기 때문으로 보는 것이 자연스럽다.
**더 중요한 관측은 "1-jet 데이터의 전자가 MC 보다 forward 이고 그 결과 Σw 가 6–15% 크다" 는 것** — 이것은 전달과 무관하게 모든 m_ll 에서 보이며, OS MC × w 에 붙여야 할 불확도의 크기를 준다.
(데이터의 endcap 비율이 300–400 → 400–500 에서 0.269 → 0.311 로 뛰는 것은 native MC (0.247 → 0.262) 보다 크다. 원인 미확인.)

## Study 24e — 한눈에 보는 그림, 그리고 "m_ll > 700 에서 왜 안 통하나" 에 대한 정리

그림 (`AN_rawcharge/24_mll_zpt_2d_factor_drll/`, 코드 `scripts/mll_zpt_2d_summary_plot.py`, 입력 `slices.json`):
- `sumw_ratio_vs_mll.png` — m_ll 구간별 Σw data/MC: 검정 = native 1-jet MC, 빨강 = 2j DY×f + non-DY. 녹색 음영 = SR 의 m_ll 범위.
- `endcap_frac_vs_mll.png` — leading 전자의 endcap 비율: data / native / transferred. 빨강이 위에서 내려와 400–500 에서 데이터와 만나고 700 위에서 파랑 (native) 과 합쳐지는 것이 보인다.

**m_ll > 700 에 대해**: "전달이 안 통한다" 가 아니다. 구분하면
1. 전달 (2j → 1j) 자체는 m_ll > 700 에서 **자명하게 성립**한다. m_lljj > 800 이 자동 만족이라 2-jet 과 1-jet 의 전자 분포가 같고, 2j×f = native 1-jet MC 다 (Σw 24.23 vs 24.30).
2. f 는 DY MC 의 1-jet yield 에 맞춰 정의되므로 **전달은 normalization 을 절대 바꾸지 못한다**: 모든 m_ll 에서 N(transferred) ≡ N(native). 전달이 바꿀 수 있는 것은 전자 (pT, η) 의 모양 (⟨w⟩) 뿐.
3. m_ll > 700 에서 남는 1.16 ± 0.06 은 **1-jet MC 가 데이터보다 10% 적고 (553 vs 501.5) ⟨w⟩ 가 5% 작은 것** — 전달과 무관한 data/MC 차이이고 2.5σ 수준.
   400–700 에서는 2j×f 의 ⟨w⟩ 가 native 보다 커서 (+14%) 이 data/MC 차이 (+9%) 를 우연히 덮었고, 700 위에서는 덮을 것이 없어 차이가 그대로 드러난 것이다.

2-jet 에서 직접 본 결과는 `LOWMLLJJ_FLIP_CLOSURE.md` (study 25): m_lljj < 800 영역에서 OS data 와 OS MC 의 ⟨w⟩ 는 같다 (1.000) — 1-jet 에서 보인 forward 초과는 2-jet 에서는 없다.
