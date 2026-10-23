# 00. DY 배경 추정의 전체 구조 (2024) 와 노트 5.1절 지도

이 절의 물리 내용·본문은 chihwan draft (`AN-25-020/chihwan/tex/05_backgrounds.tex`, 2026-09-17 재작성본) 에서 왔다.
이번 세션에서는 그것을 노트 `tex/05_backgrounds.tex` 로 옮기고 (draft 의 6.3.0.1 / 6.3.0.2 두 paragraph 제외), 아래 01–04 의 확인·재플랏·검증을 했다.

## 1. 방법 요약

DY+jets 는 LO MadGraph MLM HT-binned 샘플 (14개: MLL 50–120 / 120–∞ × HT 7 bin) 로 추정하고 event weight 세 개를 곱한다:

    w → w × C(pT^{gen Z}) × κ_EW(pT^{gen Z}) × R(pT^{jet})

| 인자 | 무엇 | 어떻게 구했나 | fit 의 nuisance |
|---|---|---|---|
| C | gen-level Z pT 의 NLO/LO QCD 보정 | NLO = POWHEG mass-binned DY→ee, μμ 18개 (mll>50), LO = HT-binned 14개. 둘 다 HT^LHE>40. pT>50 에서 **shape-only 정규화**, pT<50 은 C=1. 꼬리는 250–350, 350–500, 500–1000 고정 bin. | `ZPtRw_MC_stat`, `ZPtRwQCDScale`, `ZPtRwQCDPDFError`, `ZPtRwQCDPDFAlphaS` |
| κ_EW | NLO EW 보정 (Lindert et al., arXiv:1705.04664), Run 2 에서 그대로 | `HNWR/data/corrections/zpt_ew/ZPtEWCorr.root` | `ZPtRwEW1/2/3` |
| R | reco leading jet pT 의 data-driven 보정 = (data − nonDY)/DY, DY CR 에서 | resolved: leading AK4, bin 40/100/200/400/600/800/2000; boosted: leading AK8, 200/400/600/2000. **per-flavour curve 적용** (userflag `RFlav`) | `ResolvedDYReshapeBin1–6`, `BoostedDYReshapeBin1–3` |

스크립트: `HNWR/scripts/make_dy_zpt_nlo_lo.py` (C), `HNWR/scripts/make_dy_jetpt_ratio.py` (R), 설명 `HNWR/docs/DY_CORRECTIONS_EXPLAINED.md`.
산출물: `HNWR/data/corrections/zpt/dy_zpt_nlo_lo.{json,root}`, `.../jetpt/dy_jetpt_ratio.json`.
fit 에서는 추가로 `R_DY_Resolved_2024`, `R_DY_Boosted_2024` rateParam 이 DY normalization 을 띄운다 (DY CR + SR 공유).

## 2. 단계별 DY CR yield (노트 Table 13, `dycr_stage_yields_2024.tex`)

| Region | 보정 | Data | DY MC | non-DY | Data/MC | (Data−nonDY)/DY |
|---|---|---|---|---|---|---|
| Resolved ee | none | 36294 | 28425.7 | 2337.4 | 1.180 | 1.195 ± 0.007 |
| | C×κ_EW | | 25560.3 | | 1.301 | 1.328 ± 0.007 |
| | C×κ_EW×R | | 33957.0 | | 1.000 | 1.000 ± 0.006 |
| Resolved μμ | none | 52302 | 38867.2 | 3289.7 | 1.241 | 1.261 ± 0.006 |
| | C×κ_EW | | 35061.4 | | 1.364 | 1.398 ± 0.007 |
| | C×κ_EW×R | | 47892.6 | | 1.022 | 1.023 ± 0.005 |
| Boosted ee | none | 3326 | 2995.9 | 351.7 | 0.994 | 0.993 ± 0.019 |
| | C×κ_EW | | 2294.2 | | 1.257 | 1.296 ± 0.025 |
| | C×κ_EW×R | | 2969.6 | | 1.001 | 1.002 ± 0.019 |
| Boosted μμ | none | 3815 | 3205.1 | 867.9 | 0.937 | 0.919 ± 0.019 |
| | C×κ_EW | | 2438.2 | | 1.154 | 1.209 ± 0.025 |
| | C×κ_EW×R | | 2892.1 | | 1.015 | 1.019 ± 0.021 |

C×κ_EW 는 DY 를 10–25% 낮추고 (κ_EW 와 C 의 high-pT 부분이 둘 다 아래로), R 이 그걸 되돌리며 jet pT 기울기를 없앤다.
R 값 (Table 15): resolved 1.81→0.87 (40–100 → 800–2000), boosted 1.32→1.06. ee/μμ 는 resolved 마지막 bin (0.78 vs 0.93) 과 boosted 전 bin (~0.1) 에서 다르다.

**주의할 점**: 이 표의 "non-DY" 는 플로터 (`config.py`) 의 그룹 정의 기준이라 올바르다. card 체인 (`post_processor_chsplit.py`) 에는 같은 CR 에서
반대 stream 데이터가 Others 로 새는 버그가 있었다 (resolved μμ DY CR 에 +2663). → `../../ttbar/02_production_card_audit/NOTES.md`.
R 의 유도 자체는 플로터 쪽 정의를 쓰므로 영향받지 않는다.

## 3. 입력 프로덕션 (전부 `/gv0/Users/achihwan/SKNanoOutput/HNWR/`)

| 프로덕션 | userflags | 용도 |
|---|---|---|
| `DYGenZpT/2024` | — | C 유도 (gen Z pT 히스토그램, theory weight 디렉토리) |
| `jet_pt_reweight/ZptOnly_EWSF/2024` + `HNWR/2024` | | R 유도 |
| `DYCRStudy/2024` (로그 기준 실제 입력; SOURCES.md 는 `DYCRStudy_RFlav` 라고 적음) | DYCRStudy | 세 시나리오 `DYCR_NoCorr/ DYCR_ZptOnly/ DYCR_Full/` 를 한 번에. Fig. 12–18, Table 13 |
| `RFlav/2024` | RFlav | 플로터의 nominal (SR, flavor CR 등) |
| `RFlav_DYCRCharge/2024` | RFlav, DYCRCharge | card 체인 입력 (linkfarm) |
| `DYCRStudy_RFlav_DYCRSplit_WeightSystOnly/2024` | DYCRStudy, RFlav, DYCRSplit, WeightSystOnly | CR1/CR2 closure (03). 2D `jetpt_mlljj` 히스토그램 |
| `DYCRSplit_NoDYCorr_WeightSystOnly/2024` | DYCRSplit, NoDYCorr, WeightSystOnly | NLO pseudo-data (04). POWHEG 18 + LO 14, C=EW=R=1 |

뒤의 두 개는 2026-09-17 00:37–00:47 에 tamsa2 에서 제출 (runlog `2026_09_17_003726`, `_004150`, `_004437`, `_004651`).
제출 명령 예 (`run_manifest.json` 에서): `python/SKNano.py -a HNWR -i HNWR/samplelists/dycrsplit_lo_2024.txt -e 2024 -n -1 --memory 8192 --userflags DYCRSplit,NoDYCorr,WeightSystOnly`.

## 4. 노트 5.1절 그림·표 ↔ 파일 (2026-09-19 빌드 기준 번호)

| 번호 | label | 내용 | 파일 / 출처 |
|---|---|---|---|
| Table 13 | `tab:dycr_stage_yields` | 위 표 | `tables/05_backgrounds/2024/dycr_stage_yields_2024.tex` |
| Fig. 10 | `fig:dy_zpt_draft` | C 와 theory variation | `corrections/dy_zpt_nlo_lo_2024.pdf` ← `make_dy_zpt_nlo_lo.py` → **01** |
| Fig. 11 | `fig:dy_ew_draft` | κ_EW | `corrections/dy_zpt_ew_correction.pdf` |
| Table 14 | `tab:dy_zpt_values` | C 값 | |
| Fig. 12, 13 | `fig:dycr_zpt_{resolved,boosted}_draft` | dilepton pT, NoCorr vs ZptOnly | `dycr_stages/{NoCorr,ZptOnly}/*_dilepton_pt.png` → **02** |
| Fig. 14 | `fig:dycr_jetpt_before_draft` | jet pT, ZptOnly | `dycr_stages/ZptOnly/*_jet_pt.png` → **02** |
| Fig. 15 | `fig:dycr_mass_zpt_draft` | mlljj/mlJ, ZptOnly | → **02** |
| Fig. 16, Table 15 | `fig:dy_jetpt_draft` | R | `corrections/dy_jetpt_ratio_*_2024.pdf` |
| Fig. 17, 18 | `fig:dycr_mass_full_draft`, `fig:dycr_jetpt_after_draft` | Full | → **02** |
| Fig. 19, 20 | `fig:dycr12_closure_{resolved,boosted}` | CR1→CR2 closure | `validation/DYCR2_*` → **03** (이번 세션에 추가) |
| Fig. 21 | `fig:nlo_lo_2024_ref` | NLO pseudo-data (참고용) | `validation/fig3{1,2}_*_2024.pdf` → **04** (이번 세션에 추가) |

노트 쪽 경로는 모두 `AN-25-020/fig/05_backgrounds/2024/` 아래.
