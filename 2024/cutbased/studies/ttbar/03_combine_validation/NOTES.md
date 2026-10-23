# 03. Combine 검증

실행법은 같은 폴더의 `README.md`. 여기는 무엇을 왜 했고 결과가 뭐였는지.
환경: CMSSW_14_1_0_pre4 (`/data6/Users/achihwan/combine/`), Combine `v10.5.1-3-gb937f34f`, `cmssw-el9` container.

## 1. synthetic fixture — β injection 과 mask 기능 (`make_fixture.py`, `run_fixture.sh`, `check_fixture.py`)

production 입력과 완전히 독립된 2-channel 예제. systematic 없음, MC-stat 없음 (bin error 0), 다른 배경 고정.

| bin | CR Top | CR Other | CR obs (β=1.2 Asimov) | SR Signal | SR Top | SR Other |
|---|---|---|---|---|---|---|
| 1 | 600 | 60 | 780 | 1 | 40 | 5 |
| 2 | 300 | 30 | 390 | 2 | 20 | 3 |
| 3 | 100 | 10 | 130 | 3 | 10 | 2 |

card: `beta_top rateParam CR_EM Top 1 [0,5]` 와 `... SR_EE Top 1 [0,5]` (같은 이름 → 공유). SR pseudo-obs 는 두 벌:
A = [50,25,14], B = [500,1,300] (일부러 터무니없게).

```
text2workspace.py card_X.txt -o ws_X.root --channel-masks
combine -M FitDiagnostics ws_X.root -n .CRonly_X --setParameters r=0,mask_CR_EM=0,mask_SR_EE=1 \
        --freezeParameters r,mask_CR_EM,mask_SR_EE --skipSBFit --saveShapes --saveNormalizations --saveWithUncertainties
```
결과 (`results_20260919/fixture_result.json`):
- β̂ = **1.2000000000 ± 0.03598** (A, B 동일). 단순 기대 √1300/1000 = 0.03606 과 일치. status 0, covQual 3.
- masked SR 의 postfit Top = **[48.0, 24.0, 12.0]** (= 1.2 × nominal) — β 가 SR 로 전달되고, 추가 transfer factor 가 곱해지지 않았음을 확인.
- A 와 B 의 β, 오차가 1e-6 이내로 같음 → mask=1 인 SR 의 관측값은 fit 에 기여하지 않는다 (명세 10.3).
- workspace 에서 β 를 1 → 1.1 로 바꾸면 `n_exp_binCR_EM_proc_Top`, `n_exp_binSR_EE_proc_Top` 만 ×1.1, Signal 은 ×1.0 (명세 10.1-7).
  mask 변수 2개 (`mask_CR_EM`, `mask_SR_EE`), β 변수 1개.
- **PASS**.

시행착오: 처음엔 yield 함수 이름을 `n_exp_final_bin..._proc_Top` 으로 가정해서 scaling 검사만 false 가 나왔다.
이 workspace 에서는 `n_exp_bin*_proc_*` 이 rateParam 을 포함한 product 였다. 이름을 패턴으로 찾도록 `check_fixture.py` 를 고쳤다.
`Other` 는 상수라 RooFit function 목록에 안 나온다 (검사 대상에서 자연히 빠짐).

## 2. 실데이터 CR-only fit (`run_cronly_fit.sh`)

시나리오 card 를 복사 → `--channel-masks` workspace → **이름에 "SR" 이 들어간 채널을 전부 mask=1**, 나머지 mask=0, `r=0` 고정.
R_TT_*, R_DY_* 와 모든 nuisance 는 floating. 옵션은 기존 `condor/fitdiag_data_inner.sh` 와 맞춤:
`--cminDefaultMinimizerStrategy 1 --cminDefaultMinimizerTolerance 0.1` (+ fallback Migrad 0:0.5, 0:1.0).
(처음 strategy 0 으로 돌렸을 때는 "Fit failed." 였다.)

mass point 는 `WR5000_N2500` (r=0, SR mask 이므로 signal 은 결과에 무관. EE/MM card 는 CR 을 전부 공유하고 SR nuisance 구성만 다르다).

EE card: masked = bEESR rEESR_OS rEESR_SS / fitted = bDYEECR bDYMuMuCR bFlvEMuCR bFlvMuECR rDYEECR_OS rDYEECR_SS rDYMuMuCR_OS rDYMuMuCR_SS rFlvCR.

| | 수정 시나리오 EE card | 수정 시나리오 MM card | **수정 전** `cbv15_an2_ref` EE card |
|---|---|---|---|
| status / covQual | 0 / 3 | 0 / 2 | 0 / 2 |
| R_TT_Resolved_2024 | **0.879 ± 0.042** | 0.879 ± 0.033 | 1.415 ± 0.090 |
| R_TT_Boosted_EE_2024 | **0.804 ± 0.113** | 0.804 ± 0.096 | **0.500 (하한)** |
| R_TT_Boosted_MuMu_2024 | **0.765 ± 0.211** | 0.765 ± 0.153 | **0.500 (하한)** |
| R_DY_Resolved_2024 | 0.850 ± 0.023 | 0.850 ± 0.025 | 0.924 ± 0.028 |
| R_DY_Boosted_2024 | 0.875 ± 0.050 | 0.875 ± 0.039 | 0.978 ± 0.034 |

(JSON: `results_20260919/cronly_*.json`; fitDiagnostics, workspace, 로그: `work_20260919/cronly/<tag>_<CH>_WR5000_N2500/`.)

수정 전 결과가 02 의 버그를 그대로 보여 준다: boosted eμ CR 은 Others 가 부풀어 data/MC 0.5 → R_TT 가 하한으로,
resolved 는 데이터가 2배 → R_TT 가 1.42 로 (나머지는 nuisance 가 흡수).

### 왜 R_TT_Resolved 가 1.05 가 아니라 0.88 인가
단순 비율 (data − nonTT)/TT = (3623 − 237.4)/3231.4 = 1.048. 그런데 fit 은 0.879.
postfit nuisance 를 크기순으로 보면 (EE/MM card 동일):
```
JES_2024                +3.34 ± 0.46     ← 크게 당겨지고 prior 의 절반 이하로 제약
ResolvedDYReshapeBin4   +2.34 ± 0.92
OthersNorm_2024         +1.68 ± 0.69
MuonTrig_2024           +1.55 ± 0.91
ResolvedDYReshapeBin2   -1.24 ± 0.95
ResolvedDYReshapeBin5   +1.09 ± 0.93
```
JES 를 올리면 jet pT threshold 를 넘는 event 가 늘어 모든 MC yield 가 커진다. 통계가 큰 resolved DY CR (3.5만 / 5.2만 event) 이
JES 를 +3.3σ 로 끌고, R_DY (0.85) 와 R_TT (0.88) 가 그만큼 내려가 보상한다. 상관계수 R_DY_Resolved–R_TT_Resolved = 0.66,
R_DY_Boosted–R_TT_Resolved = 0.58 (EE card). 즉 의미 있는 것은 β 단독값이 아니라 β × nuisance 효과의 곱이다:

```
                 prefit                    postfit (fit_b)            data
rFlvCR      TT 3231.4  total 3468.9±85.0   TT 3144.8  total 3615.5±54.9   3623
bFlvEMuCR   TT  445.3  total  513.1±45.7   TT  381.0  total  472.2±18.3    472
bFlvMuECR   TT  512.4  total  641.3±74.0   TT  423.1  total  646.5±73.9    648
norm_fit_b: rFlvCR/TT 3144.8±140.9   rEESR_OS/TT 1351.0±59.9 (blinded SR 로 전파된 예측)   bEESR/TT 391.7±36.7
```
JES 의 과도한 제약은 기존 문서 `BDT/SR/test/docs/PBDT_PULLS.md` 에도 알려진 문제로 적혀 있다 (b-only 0.41–0.60).
DY jet-pT 보정 R 을 DY CR 에서 유도한 뒤 같은 DY CR 을 fit 에 넣고 JES 도 띄우므로, jet pT 축의 잔차를 JES 가 가져가는 구조다.

pull 추출 메모: `nuisances_prefit` 의 오차로 나누는 방식은 이 파일에서 작동하지 않아 (목록이 비어 나옴), Gaussian 제약 nuisance 의
postfit 값 자체 (σ 단위) 를 읽었다.

## 3. blind expected limit (`run_blind_limit.sh`)

`text2workspace.py card.txt` (mask 없이) → `combine -M AsymptoticLimits --run blind --rAbsAcc 1e-5 --rRelAcc 0.005`.
r 과 rateParam 은 profile (freeze 안 함). 관측 데이터를 쓰지 않는 완전 blind 계산.

| median expected r | fixstream | ref (수정 전) |
|---|---|---|
| EE WR5000_N2500 | 0.4668 | 0.4688 |
| EE WR5000_N200 | 0.5684 | 0.5703 |
| MM WR5000_N2500 | 0.2910 | 0.2910 |
| MM WR5000_N200 | 0.1323 | 0.1328 |

(전체 ±1σ band: `results_20260919/blind_limits.txt`.) 차이 < 0.5%. blind limit 은 CR 의 data_obs 를 쓰지 않고 prefit Asimov 를 쓰므로
CR 데이터 버그의 영향이 거의 안 보인다. 영향은 **실데이터를 넣는 fit** 에서 나타난다 (위 2절). 또 두 시나리오 모두 boosted SR 의
Others 누수는 그대로라 그 부분의 차이는 이 비교에 안 잡힌다.

## 4. CR + SR 동시 fit (`run_srcr_fit.sh`, 2026-09-22)

2절의 CR-only 와 같은 설정에서 **SR 3채널의 mask 를 풀었다.** SR 은 card 에 `observation -1`,
즉 data_obs 가 prefit 배경 합(Asimov)이므로 **blind 는 유지된다.** `r=0` freeze, `--skipSBFit`.
scenario `cbv15_an2_ref_fixstream`, EE, WR5000_N2500. 12채널 전부 likelihood 에 들어갔다.

```
bEESR rEESR_OS rEESR_SS  bDYEECR rDYEECR_OS rDYEECR_SS  bDYMuMuCR rDYMuMuCR_OS rDYMuMuCR_SS
bFlvEMuCR bFlvMuECR rFlvCR
```

### 4a. 먼저 발견한 것 — SS 채널의 TT rateParam 이 fit 을 망가뜨리고 있었다

카드의 `R_TT_Resolved_2024` 적용 범위:

```
rEESR_OS  rDYEECR_OS  rDYMuMuCR_OS  rDYMuMuCR_SS  rFlvCR
                                    ^^^^^^^^^^^^
```

`rEESR_SS` / `rDYEECR_SS` (EE same-sign) 는 **의도적으로 빠져 있다.** `cbv15_dc_cards.py` 의
`--ddss` 모드에서 이 두 영역은 데이터 기반 charge-flip 템플릿(`Flip` = OS data x w)을 쓰고,
남은 MC non-flip 성분은 rateParam 대신 `TTNonFlipNorm_2024 lnN 1.3` / `DYNonFlipNorm_2024 lnN 1.5`
로 다룬다 (`DD_REG = ["rEESR_SS","rDYEECR_SS"]`). 일관된 설계다.

**그런데 `rDYMuMuCR_SS` 만 빠지지 않았다.** `DD_REG` 에 없기 때문이다. 그러나 post-processor 가
직접 적어 놓았듯

```python
# post_processor_chsplit.py:204
# charge-split resolved MM SR (all tightCharge; muon flips are negligible, MM SS = nonprompt/WZ)
```

muon charge flip 은 무시할 수 있으므로 **MM SS 의 TT 는 prompt flavour-symmetric ttbar 가 아니라
nonprompt/WZ** 다. 여기에 β 를 곱하는 것은 범주 오류다. TT 16.3 event / 총배경 86 짜리 채널이라
수치 영향은 없을 것으로 봤는데, 실제로는 그렇지 않았다.

`DROP_SS_TT=1 bash run_srcr_fit.sh ...` (SS 채널의 TT rateParam 줄만 제거, EE 카드에서는
`R_TT_Resolved_2024 rateParam rDYMuMuCR_SS TT` 한 줄) 로 다시 돌린 결과:

| | 그대로 | SS TT rateParam 제거 |
|---|---|---|
| covQual | **2** (강제 양정의화) | **3** (완전·정확) |
| `--saveWithUncertainties` | **무시됨** (경고) | 정상 |
| 채널별 TT 사후오차 | 전부 **0** (사용 불가) | 정상 (0.7 ~ 108.1) |
| R_DY_Res ↔ R_TT_Res 상관 | +0.569 | +0.308 |

**중심값은 실질적으로 안 변한다** (모든 rateParam 이 ≤ 0.002, ≤ 0.05σ). 바뀌는 채널은
`rDYMuMuCR_SS` 하나뿐이고 TT 16.9 → 18.7 (2 event). 즉 **물리적으로는 무시할 수 있는 한 줄인데
공분산 행렬의 조건수를 망가뜨리고 있었다.** (기전까지 규명하지는 않았다 — 인과는 "그 줄을 빼면
covQual 3 이 된다"는 상관관계로만 확인했다.)

→ **이후 숫자는 전부 `_noSSTT` (covQual 3) 쪽을 인용한다.** 그대로 돌린 covQual 2 fit 의
오차는 신뢰할 수 없다.

→ 조치하려면 `cbv15_dc_cards.py:289` 의 `rcr` 목록에서 `rDYMuMuCR_SS` 를 TT 용 scope 에서 빼면 된다
(DY 용 `R_DY_Resolved_2024` 는 별개 판단 — 같은 논리라면 그것도 빼야 한다. 06 §11).

### 4b. 결과 (`results_20260922/srcr_*_noSSTT.json`)

| rateParam | CR-only (2절, covQual 3) | CR+SR noSSTT (covQual 3) | 이동 | 오차 변화 |
|---|---|---|---|---|
| R_TT_Resolved_2024 | 0.879 ± 0.042 | **0.904 ± 0.031** | +0.025 | −25% |
| R_TT_Boosted_EE_2024 | 0.804 ± 0.113 | **0.833 ± 0.104** | +0.029 | −8% |
| R_TT_Boosted_MuMu_2024 | 0.765 ± 0.211 | **0.755 ± 0.231** | −0.010 | +10% |
| R_DY_Resolved_2024 | 0.850 ± 0.023 | 0.871 ± 0.017 | +0.021 | −25% |
| R_DY_Boosted_2024 | 0.875 ± 0.050 | 0.911 ± 0.040 | +0.036 | −20% |

`status 0`, 전부 경계 안. **중심값은 거의 안 움직인다** (모두 CR-only 오차의 0.6σ 이내).
SR data_obs 가 prefit 배경 합(Asimov)이라 β 를 당길 정보가 없기 때문이다 — 기대한 동작이다.

오차는 **이 카드의 SR 이 조이는 rateParam 에서만** 줄어든다. EE 카드의 SR 은 `bEESR`,
`rEESR_OS`, `rEESR_SS` 이므로 resolved 와 boosted EE 는 개선되고, `R_TT_Boosted_MuMu_2024`
(오직 `bDYMuMuCR` + `bFlvMuECR` 로만 제약됨) 는 **개선되지 않는다** (0.211 → 0.231).
일관된다. MM 카드로 돌리면 반대가 나와야 한다 — 아직 안 했다.

### 4c. pull — JES over-constraint 는 그대로다

| pull (σ) | nuisance | 사후오차/사전오차 |
|---|---|---|
| **+3.15** | **JES_2024** | **0.62** |
| +2.39 | ResolvedDYReshapeBin4 | 0.89 |
| +1.36 | MuonTrig_2024 | 0.90 |
| −1.23 | ResolvedDYReshapeBin2 | 0.98 |
| +1.11 | ResolvedDYReshapeBin5 | 0.93 |
| +1.06 | OthersNorm_2024 | 0.60 |

SR 을 넣어도 JES 는 여전히 +3.2σ 로 당겨지고 제약이 prior 의 0.62 다 (06 §4). **SR 추가로 풀리지 않는다.**

**주의**: 2절 CR-only 의 `largest_pulls` 가 비어 있는 것은 pull 이 없어서가 아니라
`run_cronly_fit.sh` 가 `nuisances_prefit` 에서만 prior 를 읽는데 그 객체가 비어 있기 때문이다.
`run_srcr_fit.sh` 는 "Gaussian 제약 nuisance 는 이미 σ 단위(0±1)" 라는 표준 규약으로 fallback 한다.
→ 두 fit 의 pull 을 직접 비교하려면 CR-only 도 같은 fallback 으로 다시 읽어야 한다.

### 4d. 사후 yield (`_noSSTT`, 채널별)

| channel | TT prefit | TT postfit | ± | 비 | total bkg postfit | data |
|---|---|---|---|---|---|---|
| rFlvCR | 3231.4 | 3201.2 | 108.1 | 0.991 | 3611.5 | 3623 |
| bFlvEMuCR | 445.3 | 395.4 | 32.4 | 0.888 | 474.3 | 472 |
| bFlvMuECR | 512.4 | 420.9 | 103.5 | 0.821 | 646.0 | 648 |
| rEESR_OS | 1413.0 | 1373.2 | 45.4 | 0.972 | 2317.3 | 2304.5 (Asimov) |
| rEESR_SS | 5.7 | 5.6 | 1.3 | 0.982 | 144.2 | 136.8 (Asimov) |
| bEESR | 457.6 | 407.2 | 34.0 | 0.890 | 804.4 | 807.8 (Asimov) |
| rDYEECR_OS | 1286.7 | 1300.8 | 46.4 | 1.011 | 35254.7 | 35120 |
| rDYEECR_SS | 3.8 | 3.8 | 0.9 | 1.000 | 1153.3 | 1174 |
| rDYMuMuCR_OS | 1826.5 | 1892.8 | 67.3 | 1.036 | 52078.6 | 52218 |
| rDYMuMuCR_SS | 16.3 | 18.7 | 0.7 | 1.147 | 86.2 | 84 |
| bDYEECR | 78.3 | 69.3 | 7.9 | 0.885 | 3324.2 | 3326 |
| bDYMuMuCR | 197.1 | 158.6 | 43.8 | 0.805 | 3818.1 | 3815 |

모든 CR 에서 사후 총배경이 데이터와 0.4% 이내로 맞는다. 2절과 같은 구조다 —
β 단독이 아니라 β × nuisance 의 곱이 데이터를 맞춘다.

### ⚠ 이 결과의 유효 범위

`cbv15_an2_ref_fixstream` 의 shapes 는 **CR 10개만 재생성한 것이고 SR 블록은 stream 누수 패치 이전
입력**(9/9~9/17)이다. 따라서 위 표의 **SR 관련 숫자(bEESR, rEESR_*, 그리고 그것이 조인 오차)는 잠정치**다.
06 §1 의 SR shapes 재생성 후 다시 돌려야 한다.

실행은 컨테이너 없이 네이티브로 했다 (`cmssw-el9` 래퍼가 멈춘다 — `RUNBOOK_env.md`).

## 5. 하지 않은 것

- unblinded (SR 실데이터) fit — 하지 않음. 정책 그대로 blinded.
- 전체 mass grid, HybridNew toy limit (production 은 EE asymptotic under-coverage 때문에 toy 를 쓴다) — 하지 않음.
- 실데이터 CR + expected SR 의 hybrid expected limit — 하지 않음.
- boosted 의 A/B 입력 일치 검증, low-mass VR 을 likelihood 에 넣는 검증 — 하지 않음.
