# JES_2024 pull (+2.9σ, 제약 0.5–0.7) 원인 진단 — 2026-09-25

대상: v2 card (`cbv15_an2_ref_v2`, SS-TT rateParam 제거, WR5000_N2500, CR data + SR Asimov, r = 0 고정).
EE card / MM card 둘 다. 모든 숫자의 출처는 `results/` 아래 파일.

## 결론 (먼저)

1. **JES pull 은 JES 가 틀려서가 아니라, CR 의 m_lljj data/MC 기울기를 JES 가 대신 흡수해서 생긴다.**
   세 resolved CR (rFlvCR = eμ ttbar, rDYEECR_OS, rDYMuMuCR_OS) 모두 data/MC 가 800 → 2400 GeV 에서
   약 +10–15 % 오른다. JES +1σ 가 만드는 기울기는 약 1.5 % 뿐이라 data 는 JES ≈ +5.5σ 를 원한다.
   m_lljj 기울기 nuisance (DY, TT 각각) 를 넣으면 **JES +2.91 → +0.84, DY R Bin4 +2.41 → +0.53,
   MuonTrig +1.37 → +0.80, R_DY 0.89 → 0.96** 로 한꺼번에 풀린다 (§D3).
2. **"과한 제약" 은 한 채널 탓이 아니다.** data 만의 JES likelihood 폭이 ±0.95 로 prior (±1) 와 비슷하고,
   둘을 합치면 1/√(1/0.95² + 1) ≈ 0.69 — 관측된 0.53–0.77 이 그대로 나온다. pull 도 data (+5.55) 와
   prior (0) 의 가중평균 5.55 × 1.11/2.11 ≈ +2.9 로 정확히 재현된다 (§D2).
3. **어느 채널을 빼도 data 는 여전히 JES ≈ +5 를 원한다** (4.9–5.8). 세 CR 이 각자 독립적으로 같은 것을
   요구한다 — 범인 하나는 없다. 앞서 `ttbar/06_open_issues.md` §16 (b) 의 "과한 제약은 rDYMuMuCR_OS 에서
   온다" 는 Hesse 오차(covQual 2/3) 비교에서 나온 것으로, **likelihood scan 으로는 지지되지 않는다** (§D2).
4. 기울기는 **ee DY, μμ DY, eμ ttbar 에 같은 방향**으로 있다 → 렙톤 flavour 와 무관. 원인이 제트 쪽인지
   (JES 템플릿이 고 pT 효과를 과소평가?) 생성기 m_lljj 꼬리 모델링인지는 **이 진단으로는 가를 수 없다**.
   참고: 잘 알려진 top pT 효과 (data 가 MC 보다 부드러움) 는 반대 방향이라 이것으로는 설명되지 않는다.

## 근거

### D1. 템플릿만으로: 채널별로 JES 하나만 풀었을 때 원하는 값 — `results/template_fit_JES_2024.md`, `results/shape_vs_JES_2024.png`

`scripts/jes_template_check.py`. card 템플릿에서 채널마다 JES 한 개 + 그 채널의 자유 rateParam 만 χ² fit (prior 없음,
다른 nuisance 0). combine 없이 몇 초.

| 채널 | 원하는 JES | ±1σ | χ²(0) − χ²min |
|---|---|---|---|
| rDYEECR_OS | +7.7 | −1.6 / +2.0 | 32.7 |
| rDYMuMuCR_OS | +5.7 | −1.4 / +1.7 | 27.9 |
| rFlvCR | +8.3 | −2.6 / +2.9 | 13.6 |
| boosted CR 들 | 0 – +8, 오차 3–10 | | ≤ 2.3 (무관) |

prefit data/MC (resolved μμ OS): 800 0.995, 1000 1.034, 1200 1.035, 1400 1.077, 1600 1.077, 2000 **1.145**, 2400 1.115.
같은 bin 에서 JES Up 은 MC 를 +3.5 % → +5.1 % 만 올린다 (정규화를 빼면 기울기 ~1.5 %/σ).
그림 `shape_vs_JES_2024.png`: 검은 점 (data/MC) 의 기울기를 JES +2.9σ (주황) 도 절반도 못 따라간다.

### D2. combine likelihood scan — `results/scans.md`, `results/jes_scan_{EE,MM}.png`

MultiDimFit grid (JES ∈ [−1, 9], 51 점, 나머지 nuisance 전부 profile). JES 를 POI 로 올리면 combine 이 JES 의
Gaussian 제약을 빼므로 scan = **data 만의 profile**. 여기에 θ² 를 더하면 전체 fit (prior 포함) 의 profile.
검증: prior 포함 최소 +2.82 (EE), +2.82 (MM) ↔ FitDiagnostics +2.91 / +2.75 (격자 0.2 간격 안에서 일치).
또 FitDiagnostics 를 JES = 0 과 5.5 에서 각각 시작해도 같은 +2.91, 같은 NLL → 극소점은 하나.

| scan (EE card) | data 만: 최적 ± 폭 | prior 포함: 최적 (폭) | prior 포함 q(0) |
|---|---|---|---|
| 전체 | **+5.55 ± 0.95** | **+2.82** (0.60/0.77) | 18.4 |
| − rDYMuMuCR_OS | +5.83 ± 1.1 | +2.63 (0.73) | 12.9 |
| − rDYEECR_OS | +5.05 ± 1.05 | +2.43 (0.71) | 11.4 |
| − rFlvCR | +4.93 ± 1.08 | +2.43 (0.72) | 10.6 |
| resolved CR 3 개만 | +6.53 ± 1.1 | +3.02 (0.73) | 16.5 |
| rDYMuMuCR_OS 만 | +5.66 (−1.55/+1.32) | +1.65 | 3.8 |
| rDYEECR_OS 만 | +7.36 (−1.7/+1.5) | +1.84 | 4.9 |
| rFlvCR 만 | +7.24 (−2.1/+1.7) | +1.25 | 1.6 |
| SR 만 (Asimov) | 0 | 0 | 0 |
| 전체, DY R bin 1–6 + MuonTrig 고정 | +6.53 ± 0.84 | **+3.80** | 38.3 |
| 전체, JES 외 constrained nuisance 전부 고정 | +5.87 ± 0.73 | **+3.80** | 42.4 |
| **전체 + MassSlopeDY/TT** | **+2.13 ± 1.26** | **+0.86** (0.80/0.74) | **1.1** |

MM card: 전체 +5.14 ± 0.93 → prior 포함 +2.82; + slope 에서 +1.88 ± 1.2 → +0.86 (q(0) = 0.9).

읽는 법:
- 채널 하나만으로도 data 는 JES +5.7 ~ +7.4 를 원한다 (D1 템플릿 값과 일치). 세 CR 이 **독립적으로** 같은 것을 요구.
- 하나를 빼도 +4.9 ~ +5.8. 따라서 "한 채널 때문" 이 아니다.
- DY R bin 과 MuonTrig 를 고정하면 JES 가 +3.8 까지 더 당겨진다 → 그 nuisance 들이 **같은 기울기를 나눠서** 흡수하고 있었다
  (DY R Bin4 +2.4 등의 pull 이 같은 원인).
- SR (Asimov) 은 JES 를 당기지 않는다.

### D3. m_lljj 기울기 nuisance 추가 — `results/fitdiag_slope.md`, `scripts/make_slope_card.py`

DYJets 와 TT 에 각각 shape-only nuisance (MassSlopeDY / MassSlopeTT): +1σ 가 800 GeV → 3 TeV 에서 약 +10 % 기울임
(log m 에 선형, 정규화 보존, 모든 채널 공통). **임시 진단용** — 크기 10 % 는 임의.

| param | EE base | EE +slope | MM base | MM +slope |
|---|---|---|---|---|
| JES_2024 | +2.91 ± 0.53 | **+0.84 ± 0.90** | +2.75 ± 0.66 | **+0.78 ± 0.39** |
| MassSlopeDY | – | +1.52 ± 0.33 | – | +1.44 ± 0.25 |
| MassSlopeTT | – | +1.61 ± 0.81 | – | +1.39 ± 0.69 |
| ResolvedDYReshapeBin2 | −1.25 | −0.24 | −1.28 | −0.29 |
| ResolvedDYReshapeBin4 | +2.41 | **+0.53** | +2.41 | **+0.58** |
| ResolvedDYReshapeBin5 | +1.13 | −0.19 | +1.06 | −0.22 |
| MuonTrig_2024 | +1.37 | +0.80 | +1.36 | +0.75 |
| R_DY_Resolved | 0.89 | **0.96** | 0.90 | **0.97** |
| R_TT_Resolved | 0.90 | **0.96** | 0.90 | **0.96** |
| covQual | 2 | 3 | 2 | 2 |

- slope 가 +1.4 ~ +1.6σ (≈ +15 % 기울기) 로 당겨지고 DY 쪽은 ±0.3σ (≈ ±3 %) 로 잘 측정된다 — data 가 원하는 것이 바로 이 기울기.
- 기울기를 주면 JES, DY R bin, MuonTrig 가 모두 풀리고, rateParam 도 1 에 가까워진다 (JES 가 MC 를 ~10 % 올리던 것을
  R 이 0.89 로 되돌리던 구조가 사라짐; JES–R_DY 상관 −0.72).
- MM +slope 의 JES Hesse 오차 0.39 는 covQual 2 라 믿기 어렵다. 같은 card 의 scan 폭은 0.9/0.66 (D2).
- slope 를 넣어도 |pull| > 1 로 남는 것: OthersNorm +1.02 (EE). FlipClosure +0.7 은 그대로 (SS 초과, 별개 문제).

## 한계 / 아직 모르는 것

- 기울기의 **물리적 원인**은 미정. 후보: (a) JES 불확도 템플릿이 고 pT 제트에서 너무 작음 (JES 를 +5σ 까지 당겨야 할 정도면
  JES 자체 문제라기보다 모양이 다름), (b) DY LO MLM / TT powheg 의 m_lljj (또는 HT) 꼬리 모델링, (c) R(jet pT) 보정이 m_lljj
  모양까지는 못 맞춤. ee/μμ/eμ 공통이므로 렙톤 SF 는 아님.
- MassSlope nuisance 는 진단용 임의 모양이다. 분석에 넣으려면 근거 있는 모양 (예: HT/m_lljj 재가중 대안 생성기 비교,
  FxFx vs MLM) 과 크기가 필요하고, SR 외삽에서 이 nuisance 가 limit 에 주는 영향을 봐야 한다.
- 모두 v2 card 기준. FlipSF 재생산 (2026-09-24 제출) 으로 card 가 바뀌어도 기울기 자체는 OS CR 이라 그대로일 것으로 예상.

## 파일

- `scripts/jes_template_check.py` — D1 (로컬, 수 초)
- `scripts/make_slope_card.py` — D3 card 생성 (PyROOT, tamsa2)
- `scripts/collect_scans.py` — D2 정리 + 그림 (로컬 uproot)
- `scripts/fd_summary.py` — D3 FitDiagnostics 정리 (PyROOT, tamsa2)
- `combine/prep.sh` (workspace), `combine/job_inner.sh` + `job.sh` (condor job), `combine/*.sub`, `combine/jobs*.txt`
- `combine/{EE,MM}/{base,slope}/` card + workspace, `combine/{EE,MM}/out/` combine 출력과 로그
- `results/` 표와 그림

재현: `ssh tamsa2 "bash combine/prep.sh"` → `condor_submit combine/diag.sub` (+ `redo.sub`, `only.sub`, `fd.sub`)
→ `python3 scripts/collect_scans.py`, `python3 scripts/fd_summary.py` (tamsa2).
