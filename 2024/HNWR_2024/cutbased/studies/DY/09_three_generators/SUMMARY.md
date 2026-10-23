# DY Z-pT 보정 (C) 재검토 — 전체 정리 (2026-09-20 ~ 09-21)

Claude Code 세션 기록. 06–09 번 study 를 한 줄기로 묶은 것이다. 세부 과정은 각 폴더의 `NOTES.md`,
그림 목록은 이 폴더의 `PLOTS.md` 에 있다. 모든 수치는 2024, 별도 표시가 없으면 resolved DY CR (m_ll 60–150).

DY 추정식 (바뀐 것 없음): `w × C(gen Z pT) × κ_EW(gen Z pT) × R(reco leading jet pT)`,
그 위에 fit 의 `R_DY_{Resolved,Boosted}_2024` rateParam (DY CR 과 SR 공유).

---

## 0. 결론부터

| 질문 | 답 |
|---|---|
| Fig. 10 의 theory band 가 왜 거의 안 보이나 | 버그 아님. C 를 pT ≥ 50 에서 shape-only 로 정규화 (K = ΣNLO/ΣLO 로 나눔) 해서 normalization 성분이 상쇄된다. 남는 shape 변동은 POWHEG 에서 ≤ 1.4% |
| NNLO xsec 을 LO 에 곱하고 C 도 곱하면 normalization 이중 보정 아닌가 | 아니다. 같은 이유 (shape-only). 배포본 K = 0.990 (run log 의 0.7148 은 전 구간 합의 비, 진단용) |
| C 가 jet 수에 의존하나 | **크게 의존한다.** POWHEG 는 LHE parton 이 0/1 개뿐 (0.5%/99.5%), LO MLM 은 1–4 개 (37/43/13/6%). 배포본 C 는 사실상 "ME 1-parton NLO / MLM 1–4 parton LO" 다 |
| m_ll 별로 C 를 나눠야 하나 | FxFx 기준으로 pT > 70 에서는 m_ll 의존이 유의하지 않다 (0–50 bin 만 9σ). 나눌 필요 없음 |
| 어느 generator 가 data 에 맞나 | **FxFx.** 보정 없이 data/MC: LO 1.18/1.24, POWHEG 1.83/1.94, FxFx 0.98/1.03 (ee/μμ) |
| jet-inclusive C 와 ≥2jet C 의 차이 | pT(ll) > 100 에서는 normalization (×1.22) 뿐, 모양 차이는 pT(ll) < 100 에만 있다. R 을 넣으면 m_lljj·jet pT 는 0.4% 안으로 같다 |
| 어느 쪽이 data 에 더 맞나 | pT(ll) < 100 은 jet별이 확실히 낫고 (50–100: 0.985 vs 1.066), > 300 은 jet-incl 이 1–3%p 가깝지만 불확도 안 |
| 어느 쪽의 오차가 작나 | **jet별.** scale 이 지배하고 jet별이 절반 (500–600: 4.3% vs 8.3%). stat 손해는 작다 (1.7% vs 1.4%) |
| **추천** | **FxFx/LO, GenJet 수별 (0/1/≥2), shape-only C** (`dy_zpt_fxfx_lo_njet.root`, userflag `ZptNJet`) + 그 C 로 다시 유도한 R |
| 아직 안 풀린 것 | pT(ll) > 500 에서 data/MC 1.15–1.2 가 C 종류와 무관하게 남는다 (κ_EW 기여가 큼, §6) |

**분석에는 아직 적용하지 않았다.** 아래 전부는 별도 출력 base (`SKNanoOutput_dy3gen`) 의 study 프로덕션이다.
적용하려면 §8 의 절차가 필요하다.

---

## 1. 출발점: 배포본 C 의 성질 (06 번)

- 배포본: `dy_zpt_nlo_lo.root` = POWHEG mass-binned (NLO) / madgraphMLM HT-binned (LO), 양쪽 `LHE_HT > 40`,
  gen Z pT ≥ 50 에서 shape-only. pT < 50 은 C = 1, tail bin 250–350/350–500/500–1000, 1000 위 clamp.
- `LHE_HT > 40` 은 NLO 전체의 90% 를 자르지만 거의 전부 저-pT 다. **pT ≥ 50 에서는 8% 만 자른다.**
  (세션 중 "Born 을 자른다" 고 말했던 것은 틀렸고 정정했다 — POWHEG 의 LHE parton 0 개는 0.5% 뿐.)
- jet 수로 나눌 때 `LHE_Njets` 는 쓰지 않는다 (MLM merging 때문에 generator 간 의미가 다르다).
  대신 **GenJet**: pT > 40, |η| < 2.5, hard-process 렙톤과 ΔR > 0.4 (`HNWRDY::CountGenJets`, `DYGenZ.h`).
- ≥2 GenJet 에서 POWHEG/LO 의 Z pT 모양은 0.58–1.24 로 크게 어긋난다 (2-jet ME 없음, 두 번째 jet 은 shower).
  04 번 study 의 "NLO pseudo-data 붕괴" 와 같은 뿌리다.

## 2. jet pT reweight 의 양쪽 (07 번)

(data − nonDY) 와 DY MC 를 jet pT 축에 겹친 4 영역 그림. resolved 는 40 GeV 의 ~2.0 에서 2 TeV 의 ~0.6 까지
매끄럽게 단조 감소, boosted 는 1.5 → 1. 마지막 bin 에서 ee/μμ 가 갈린다 (0.78 / 0.93).

## 3. C(pT | m_ll) 와 theory error 재구현 (08 번)

- 2D 히스토그램 `Zpt_mll_genZ_HT40` (5 GeV × 22 m_ll edge) 으로 m_ll slice 별 K_m 정규화 후 C 를 구함.
  `make_dy_zpt_mll.py` → `dy_zpt_nlo_lo_mll.{json,root}`.
- theory member 를 히스토그램으로 직접 채움: `Theory/Scale_{0..8}/`, `Theory/PDF_{0..102}/` (envelope / Hessian).
  제대로 구현해도 POWHEG 의 band 는 작다 — 구현 문제가 아니라 shape-only + POWHEG weight 의 성질.
- 현실적인 크기는 generator 차이: FxFx vs POWHEG 가 tail 에서 ~30%.

## 4. FxFx 2024 확보

| 단계 | 내용 |
|---|---|
| 탐색 | rucio (`/gv0/Users/achihwan` 의 `rucio.sh`). `DYto2{E,Mu}-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8`, NanoAODv15 |
| 다운로드 | `/gv0/Users/achihwan/bkg/nano15/DYFxFx/2024/` (`down.sh -j 16`, KNU). 5965 파일 1.8 TB, 실패 0, 28 분 |
| RNTuple 변환 | `DYFxFx/condor/` (`job.sh`, `rntuple.sub`) → `DYFxFx/rntuple/`. `verify.py` 전수 검증 5965/5965 정상 |
| 등록 | `HNWR/scripts/register_dy_fxfx.py` → alias `DYto2E_MLL50_FxFx`, `DYto2Mu_MLL50_FxFx`, `HNWR/data/Sample/2024/<alias>.json` |
| xsec | XSDB 2240 pb (Mu; E 에도 같은 값) |
| 확인 | `LHE_NpNLO` 0/1/2 = 66/21/13%, 음수 weight 16.7%, |genWeight| 상수 → sumsign = genEventSumw/|w0| |

PTLL-binned / 고질량 FxFx 는 받지 않았다 (`datasets.txt` 는 요청 초안, 미사용). 그래서 m_ll > 400 은 FxFx 통계 부족.

## 5. 세 generator 비교 (09 번, gen level)

전제: `LHE_HT > 40`, gen Z pT > 50 (세트 1). POWHEG 빼고 pT 컷 없는 버전이 세트 2. 각각 unit / 절대 normalization.

Z pT shape 의 /LO 비, m_ll 60–150:
```
pT              50-60 60-70 70-80 80-90 90-100 100-120 120-150 150-200 200-250 250-350 350-500 500-1000
jet 무관 POWHEG 0.917 0.991 1.032 1.049 1.065  1.112   1.092   1.040   0.979   0.913   0.827   0.716
jet 무관 FxFx   0.934 0.974 0.999 1.018 1.045  1.110   1.127   1.120   1.103   1.073   1.026   0.938
≥2GenJet POWHEG 0.578 0.753 0.907 1.034 1.128  1.207   1.242   1.223   1.168   1.092   0.985   0.846
≥2GenJet FxFx   1.002 1.005 1.001 1.004 0.998  1.004   1.008   1.003   0.983   0.955   0.899   0.815
```
- ≥2 GenJet 에서 **LO 와 FxFx 의 모양은 250 GeV 까지 1% 안으로 같다.** 그 위에서만 FxFx 가 5–18% 낮다.
- yield (pT>50, HT>40): jet 무관 LO 3.58e7 / POWHEG 3.54e7 / FxFx 3.99e7; ≥2 GenJet 4.73e6 / 3.55e6 / 6.11e6.
- 그림의 비율 패널이 그림마다 달라 보였던 것은 panel 별 unit normalization 때문 → `__absNorm` 세트 추가.

reco data/MC, 보정 없음 (`datamc_resolvedDYCR/`, reco pT(ll) > 50):

| | LO | POWHEG | FxFx |
|---|---|---|---|
| ee | 1.176 | 1.833 | 0.980 |
| μμ | 1.240 | 1.942 | 1.025 |

SR 과 겹치지 않는 LowJet 영역 (tight 렙톤 2 + trigger, AK4 < 2, AK8 == 0; `datamc_lowJet__LO_FxFx/`):

| 영역 | LO ee / μμ | FxFx ee / μμ |
|---|---|---|
| nJet0, pT(ll)>50 | 1.155 / 1.224 | 0.996 / 1.049 |
| nJet0, 컷 없음 | 4.80 / 5.18 (LO 는 HT≥40 샘플이라 0-jet 을 못 채움) | 0.920 / 0.973 |
| nJet1, pT(ll)>50 | 1.023 / 1.081 | 0.891 / 0.939 |
| nJet1, 컷 없음 | 1.036 / 1.091 | 0.889 / 0.936 |

## 6. jet 수별 C 와 세 단계 data/MC

### 6.1 C (FxFx/LO, m_ll 60–150, GenJet 0 / 1 / ≥2 / incl)

`make_dy_zpt_njet.py` → `HNWR/data/corrections/zpt/dy_zpt_fxfx_lo_njet[_abs].root`, `dy_zpt_fxfx_lo_incl.root`, `.json`.
tail 은 상대 오차 15% 가 될 때까지 자동 merge. κ_EW 는 analyzer 가 따로 곱하므로 파일에 곱해 넣지 않는다
(json 에 `C_x_EW` 로 참고값만).

K_j (pT ≥ 50 의 FxFx/LO yield 비): incl 1.02, 0j 0.86, 1j 1.11, ≥2j 1.29.
`shape` = K_j 로 나눈 것, `abs` = shape × K_j. **R 을 적용하면 둘은 동일** (yield 33902.3 / 48997.3 으로 일치) —
2-jet normalization 은 어차피 R 과 rateParam 이 가져가므로 shape 이면 충분하다.

shape C 와 상대 오차 (stat ⊕ scale ⊕ PDF):
```
pT(Z)      | jet-incl:  C    stat  scale  PDF   합  | ≥2jet:  C    stat  scale  PDF   합
 50-60     |          1.018  0.0%  2.6%  0.1%  2.6% |       1.000  0.2%  0.4%  0.1%  0.4%
 100-120   |          1.210  0.1   2.6   0.2   2.6  |       1.002  0.2   0.3   0.1   0.3
 200-250   |          1.201  0.2   3.8   0.6   3.8  |       0.982  0.3   2.1   0.4   2.1
 300-350   |          1.154  0.5   5.7   0.9   5.8  |       0.942  0.6   3.3   0.7   3.4
 400-450   |          1.104  1.0   7.2   1.0   7.3  |       0.895  1.2   4.1   0.9   4.3
 500-600   |          1.057  1.4   8.1   1.3   8.3  |       0.838  1.7   3.8   1.2   4.3
 700-800   |          0.940  3.7   8.3   2.3   9.3  |       0.781  4.0   4.9   1.9   6.6
 800-1000  |          0.889  4.5   8.8   3.7  10.6  |       0.703  5.2   4.7   3.6   7.8
 >1000     |          0.864  7.1  12.7   3.6  14.9  |       0.667  8.1   6.7   3.1  11.0
```
jet-incl 은 μR/μF 를 바꾸면 0/1/2-jet 구성비가 같이 움직여 scale band 가 크다. ≥2jet 안에서는 변화 대부분이
normalization 이라 shape-only 에서 상쇄된다. jet-incl C 를 ≥2jet 이벤트에 쓰는 외삽 오차는 band 에 없다.
(scale band 는 분자 FxFx 만 변동시킨 값.)

κ_EW (arXiv:1705.04664, Run 2 에서 가져온 Z pT 의 함수): 0.975 (100), 0.937 (200), 0.867 (500), 0.802 (1000).
EW 보정은 색과 무관한 Sudakov log 라 jet 수 의존은 작다고 보고 그대로 썼다 (검증은 안 함).

Fig. 10 형식 그림: `plots/C_per_jet/dy_zpt_fxfx_lo_Zpt_genZ_HT40_{Incl,GenJ0,GenJ1,GenJ2}_2024`, 4 열 band 그림 `dy_zpt_fxfx_lo_njet_2024`.

### 6.2 (data − nonDY)/DY, ee+μμ — `scripts/binned_stage_table.py`

pT(ll):
```
단계       C 종류            0-50  50-100 100-150 150-200 200-300 300-400 400-500 500-700 700-1000
1 C        배포본(POWHEG)    2.020  1.352  1.221   1.270   1.300   1.276   1.238   1.365   1.137
1 C        FxFx jet-incl     2.242  1.270  1.096   1.079   1.043   0.988   0.940   0.965   0.887
1 C        FxFx jet별        2.014  1.422  1.326   1.309   1.273   1.215   1.162   1.208   1.084
2 CxEW     배포본(POWHEG)    2.012  1.379  1.264   1.334   1.399   1.412   1.402   1.583   1.365
2 CxEW     FxFx jet-incl     2.233  1.296  1.134   1.134   1.122   1.094   1.065   1.119   1.064
2 CxEW     FxFx jet별        2.006  1.450  1.373   1.376   1.370   1.345   1.316   1.401   1.301
3 CxEWxR   배포본(POWHEG)    1.336  0.962  0.896   0.963   1.041   1.091   1.120   1.332   1.270
3 CxEWxR   FxFx jet-incl     1.729  1.066  0.953   0.975   1.002   1.023   1.036   1.155   1.219
3 CxEWxR   FxFx jet별        1.288  0.985  0.951   0.974   1.005   1.032   1.049   1.182   1.216
data stat                    0.075  0.020  0.009   0.008   0.006   0.008   0.013   0.029   0.130
```
m_lljj (3 단계):
```
                  800-1000 1000-1200 1200-1400 1400-1600 1600-2000 2000-2400 2400-2800 2800-3200 3200-4000 4000-8000
배포본(POWHEG)      0.983    1.023     1.039     1.060     1.094     1.102     1.125     1.001     0.950     1.192
FxFx jet-incl       0.973    1.009     1.023     1.043     1.075     1.081     1.103     0.979     0.928     1.160
FxFx jet별          0.972    1.010     1.025     1.045     1.077     1.085     1.106     0.982     0.931     1.164
data stat           0.005    0.007     0.010     0.014     0.015     0.026     0.041     0.069     0.092     0.162
```
읽는 법:
- **m_lljj 는 R 뒤에는 C 종류에 무관** (R 이 jet pT 의 함수이므로). 남는 기울기 (0.97 → 1.10) 는 세 경우 공통.
- **pT(ll) 모양은 C 가 정한다.** 배포본은 300–700 에서 1.09–1.33, FxFx 기반은 1.02–1.18.
- jet-incl / jet별 의 1 단계 비는 pT > 100 에서 1.21–1.25 로 상수 (normalization 뿐), 0–50 에서 0.90, 50–100 에서 1.12.
- data-stat-only χ²: 전 구간 jet-incl ~190 / jet별 ~129, 50 GeV 이상만 ~95 / ~114. 둘 다 큰 것은 공통 어긋남
  (100–200 의 −5%, > 500 의 +15–20%) 때문이고 jet 분할과 무관하다.
- **pT(ll) > 500 의 잔차**: κ_EW 를 곱하면 DY 가 13–20% 줄어 data/MC 가 올라간다. FxFx direct (EW 없음) 는 0.96–1.0.

### 6.3 R (leading jet pT), C × κ_EW 에 대해 다시 유도

`HNWR/data/corrections/jetpt/{zptnjet, zptnjet_abs, zptfxfxincl, zptshipped_rederived}/dy_jetpt_ratio.{root,json}`
```
resolved_comb   40-100 100-200 200-400 400-600 600-800 800-2000       boosted_comb 200-400 400-600 600-2000
배포본 C        1.833  1.553   1.328   1.182   1.079   0.876                       1.310   1.192   1.019
FxFx jet-incl   1.617  1.316   1.083   0.945   0.863   0.705                       1.033   0.893   0.767
FxFx jet별      1.918  1.589   1.320   1.158   1.059   0.864                       1.202   1.052   0.929
FxFx jet별 abs  1.510  1.239   1.027   0.899   0.820   0.669                       1.015   0.875   0.745
```
jet pT 기울기 (1.9 → 0.8) 는 C 종류와 무관하게 남는다 — Z pT 보정으로는 못 고치고 R 이 맡는다.
겹쳐 그린 그림: `plots/datamc_stages/stage2_C_x_EW/jetpt_dataMinusNonDY/jetpt_dataMinusNonDY_vs_DY__<C>__{fine,rbins}_2024`.

### 6.4 boosted DY CR 의 세 단계 (2026-09-22 추가)

그림: `plots/datamc_stages/stage{1_C,2_C_x_EW,3_C_x_EW_x_R}/boosted/` (overlay 8 장씩) 와 그 안의
`cutbased_format/` (48 장씩, `BoostDY<CH>_<var>__DY-<tag>_plot.png`). 실행 `scripts/run_stages_boosted.sh`,
표 `scripts/binned_stage_table.py Boosted`. boosted 이벤트에도 C 는 AK4 GenJet 수 (0/1/>=2) 로 고른다.

(data − nonDY)/DY, ee+μμ:
```
pT(ll)              0-100 100-200 200-300 300-400 400-500 500-700 700-1000
1 C      배포본     1.628  0.932   1.066   1.069   1.117   1.195   0.944
1 C      jet-incl   1.530  0.799   0.852   0.822   0.847   0.843   0.745
1 C      jet별      1.703  0.938   0.994   0.951   0.993   1.019   0.906
3 CxEWxR 배포본     1.292  0.763   0.899   0.937   1.037   1.178   1.029
3 CxEWxR jet-incl   1.564  0.847   0.933   0.944   1.053   1.124   1.114
3 CxEWxR jet별      1.492  0.851   0.930   0.933   1.049   1.147   1.127
data stat           0.354  0.065   0.034   0.030   0.029   0.029   0.098

m(lJ)             800-1000 1000-1200 1200-1500 1500-1800 1800-2400 2400-8000
1 C      jet별      0.984    0.978     1.005     0.937     1.012     0.938
3 CxEWxR 배포본     0.939    0.993     1.073     1.010     1.092     1.047
3 CxEWxR jet-incl   0.958    1.002     1.080     1.029     1.122     1.074
3 CxEWxR jet별      0.951    1.005     1.087     1.041     1.140     1.096
data stat           0.022    0.029     0.034     0.059     0.075     0.150

leading AK8 pT     200-300 300-400 400-500 500-600 600-800 800-1200 1200-2000
2 CxEW   jet별      1.377   1.084   1.061   1.037   0.955   0.838    0.911
3 CxEWxR jet별      1.146   0.903   1.008   0.986   1.028   0.904    0.991
data stat           0.030   0.028   0.028   0.039   0.053   0.116    0.347
```
- boosted 에서는 **jet별 C 만으로 (R 없이) 이미 data/MC ≈ 1** 이다 (m(lJ) 0.94–1.01). jet-incl 은 0.77–0.85, 배포본은 1.02–1.13.
- R 을 넣은 뒤에는 resolved 와 같이 세 C 가 m(lJ) 에서 5% 안으로 같다. jet-incl 과 jet별은 2% 안.
- R 의 첫 bin (200–400) 이 넓어서 200–300 에 +15%, 300–400 에 −10% 가 남는다 (07 번에서 본 것과 같다) — boosted R 의 bin 을 나눌 이유.
- pT(ll) 100–200 의 0.85 와 500–700 의 1.15 는 C 종류와 무관.

---

## 7. 코드·파일 변경 (커밋 안 함)

| 파일 | 내용 |
|---|---|
| `HNWR/include/HNWR/DYGenZ.h` | `CountGenJets`, `kGenJetPtMin=40`, `kGenJetEtaMax=2.5` |
| `HNWR/src/DYGenZpT.cc`, `.h` | `Mll_genZ*`, `Zpt_genZ*_Njet*`, `Zpt_mll_genZ_HT40[_GenJ0/1/2/2ex]` (TH2), `NGenJet_genZ_HT40`, `Theory/Scale_*`, `Theory/PDF_*` |
| `HNWR/src/HNWR.cc`, `.h` | userflag `ZptNJet` / `ZptNJetAbs` / `ZptFxFxIncl` (jet별 ZptSet, flag 별 R 파일), `DYCR_COnly` twin, `DYCR_*_mll_ptll[_HT40]`, `LowJet_*` 영역 |
| `HNWR/scripts/` | `make_dy_nlo_lo_mll.py`, `make_dy_jetpt_overlay.py`, `make_dy_zpt_mll.py`, `make_dy_gen_compare.py`, `make_dy_datamc_3gen.py`, `make_dy_zpt_njet.py`, `make_dy_cr_datamc.py`, `register_dy_fxfx.py` |
| samplelist | `DYGenZpT_2024_{LO,FxFx}.txt`, `dy3gen_data_nondy_2024.txt` (wht 목록에서 LO DY 를 뺀 38 개) |
| 이 폴더 `scripts/` | `draw_datamc_cutbased_format.py` (`plotter._draw` 사용), `run_stages_cutbased_format.sh`, `binned_stage_table.py` |

프로덕션 (tamsa2 condor, `SKNANO_OUTPUT=/gv0/Users/achihwan/SKNanoOutput_dy3gen` 로 분리):

| 경로 (`SKNanoOutput_dy3gen/HNWR/`) | 내용 |
|---|---|
| `DYCRSplit_NoDYCorr_WeightSystOnly` | data, nonDY, LO, POWHEG, FxFx (C=EW=R=1), LowJet 포함 |
| `DYCRStudy_DYCRSplit_ZptOnly[_ZptNJet\|_ZptNJetAbs\|_ZptFxFxIncl]_WeightSystOnly` | 1 차: R 없이, R 유도용 |
| `DYCRStudy_DYCRSplit_RFlav[...]_WeightSystOnly` | 2 차: 새 R 적용. twin `DYCR_{NoCorr,COnly,ZptOnly,Full}/Central` = 무보정 / C / C×EW / C×EW×R |

gen level: `/gv0/Users/achihwan/SKNanoOutput/DYGenZpT/2024/`.

운영 메모: cms1 에서 수정 직후 tamsa2 에서 빌드하면 NFS 지연으로 반영이 안 될 수 있다 → 빌드 전 grep, 빌드 후
`strings libHNWR.so | grep <flag>` 로 확인. uproot 는 이 RNTuple 을 못 읽는다 (ROOT `RNTupleReader` 사용).

## 8. 분석에 적용하려면

1. C 선택 확정 (추천: jet별 shape, `ZptNJet`). 기본값으로 만들지 flag 로 둘지 결정.
2. theory systematic 을 jet별 C 의 `QCDScale`/`QCDPDFError`/`QCDPDFAlphaS` 로 교체 (파일에 이미 들어 있음).
   FxFx − POWHEG 차이를 추가 shape systematic 으로 넣을지 결정.
3. boosted 의 GenJet 정의 결정 (지금은 AK4 컷 기준 0/1/≥2 를 boosted 에도 그대로 씀).
4. R 을 정식 절차 (`jet_pt_reweight`) 로 재유도 → 전체 재프로덕션 → 카드.
5. 노트: Fig. 10 교체 (`C_per_jet/`), 5.1 절 본문 (generator, GenJet 분할), Table 8 샘플 이름 교정 (미수정 상태).

## 9. 미해결 / 하지 않은 것

- pT(ll) > 500 잔차 1.15–1.2 (κ_EW 기여). κ_EW 없이 / NLL 버전 등으로 확인 필요.
- m_lljj 의 완만한 기울기 0.97 → 1.10 (C 와 무관, 기존 `dycr-mlljj-zpt-slope` 와 같은 현상).
- m_ll > 400 에서 FxFx 통계 부족 (고질량 FxFx 샘플 없음). high-m_ll 검증 영역 미정.
- FxFx 로 04 번 (NLO pseudo-data) 재수행은 안 했다.
- `make_dy_cr_datamc.py` 는 히스토그램마다 파일을 다시 열어 느리다 (10 분+). `binned_stage_table.py` 방식
  (파일당 한 번) 으로 바꾸면 1 분.
- HNWR 요약 로그가 flag 와 무관하게 "C from dy_zpt_nlo_lo.root" 라고 찍는다 (표시만 틀림, 동작은 맞음).
- `00_overview/DY_CORRECTIONS_EXPLAINED.md` §0, `01_.../NOTES.md` 의 "K = 0.7148 = pT>50 정규화" 표현은 stale
  (실제 0.990).
- `plots/datamc_stages/stage{1,2}*/cutbased_format/` 에 두 번의 실행 tag 가 섞여 있다
  (`LO x C(per-jet)` = `LO-C-FxFx-perjet-shape`, 같은 내용; 앞의 것은 파일 이름에 공백·괄호).

---

## 10. 2026-09-22 — 새 보정으로 플랏 최신화 (`plot/HNWR_2024/cutbased/out/`) 와 charge-flip 체인 재실행

채택: **jet별 shape C (`ZptNJet`) + 그 C 로 유도한 R** (`jetpt/zptnjet/`). 분석 카드·BDT 체인에는 아직 넣지 않았다 (§8 그대로).

### 프로덕션 (tamsa2, `SKNANO_OUTPUT=/gv0/Users/achihwan/SKNanoOutput_dynew`, `scripts/submit_dynew.sh`)
DY 보정은 DY 샘플에만 작용하므로 **LO DY 14 개만** 다시 돌렸다. data·non-DY·signal 은 기존 프로덕션을 symlink 한다.

| batch | 내용 | 출력 |
|---|---|---|
| `HNWR_dynew` | HNWR, `RFlav,DYCRCharge,SRChargeSplit,ZptNJet`, full syst (세 plot 프로덕션의 superset) | `HNWR/RFlav_DYCRCharge_SRChargeSplit_ZptNJet/2024` |
| `HNWR_dycheck` | 같은 코드·**옛 보정**, DY 1 샘플 — 코드 drift 확인 | `HNWR/RFlav_DYCRCharge_SRChargeSplit/2024` |
| `cfdynew`, `cffxfx` | HNWR_ChargeFlip (LO 새 보정 / FxFx) | `studies/chargeflip/new_DYCR/README.md` 참조 |

drift 확인 (`scripts/dy_driftcheck.py`): 오늘 코드 = `RFlav_DYCRCharge` (09-08) 와 Central·ZPtRw·DYReshape·JES 전부 일치.
`RFlav` (08-28) 와는 JES 변동 디렉토리의 shape 만 다르다 (81 개, 적분 동일 — 08-28 과 09-08 사이의 변화).
그래서 plot 입력 세트는 전부 09-08 계열로 통일했다 (`scripts/make_dynew_plotsets.sh`):
`/gv0/Users/achihwan/SKNanoOutput/HNWR/{RFlav_ZptNJet, RFlav_DYCRCharge_ZptNJet, RFlav_SRChargeSplit_plot_ZptNJet}/2024`
(= 기존 non-DY symlink + 새 DY symlink). 플로터가 읽는 샘플 구성은 `RFlav` 와 `RFlav_DYCRCharge` 가 같다.
새 DY 파일에는 `config.SYST_LIST` 의 31 개 디렉토리가 전부 있다.

### `out/` 재생성
- 기존 `out/` → `plot/HNWR_2024/cutbased/out_shippedDY_2026-09-21/` (898 png 그대로 백업), `out/` 은 비우고 새로 그림.
- `condor/run_dynew_job.sh` + `condor/dynew_all.sub` (batch `plot_dynew`, 11 job): job 마다 rawcharge → main → tightcharge(+alltc, etawide)
  → FLV charge → chargesign 순서 (`--skip-existing` 이라 순서가 기존 상태를 재현). 사용자 `specs/`, 기존 `.sub` 는 수정하지 않았다.
- 결과: run_specs 계열 전부 재생성, 실패 0. 백업에만 있는 것은 `*_cardbins` 12 장 (현재 spec 에 없는 9/12 출력) 과
  npz 기반 옛 방식 폴더 (`SS_flip`, `_tc2`, `_pp`, `_mm`, `_an`, `OS_2d`).
- npz 기반 (`SS_flip_an3*`, SR `SS_flip_an3`, chargesign m_ll 4 종): `studies/chargeflip/new_DYCR/scripts/run_out_npz_families.sh`.

resolved DY CR pT(ll) data/MC (out/ 의 TSV, 옛 → 새):
```
pT(ll)     50-100  100-150 150-200 250-300 350-400 400-450 500-550 600-650
ee   옛    0.967   0.903   0.943   1.058   1.088   1.118   1.214   1.347
ee   새    1.000   0.968   0.967   1.021   1.020   1.061   1.090   1.252
μμ   옛    0.969   0.905   0.983   1.079   1.139   1.118   1.392   1.418
μμ   새    0.982   0.948   0.983   1.018   1.045   1.036   1.235   1.280
```
SR 의 DY 예측 (새/옛, MC 만): resolved ee +1.0%, μμ +3.6%; boosted ee −6.1%, μμ −2.7%; m_lljj bin 별로 ±1% 안에서 평평.

**주의 (기존부터 있던 문제):** SR 그림은 "Blinded" 지만 옆에 쓰이는 TSV 의 `Data` 열에는 0 이 아닌 값이 들어 있다
(백업된 옛 `out/` 도 동일). 위 비교는 MC 열만 썼다. `plotter.py` 에서 blind 영역의 TSV Data 를 비울지는 미결정.
