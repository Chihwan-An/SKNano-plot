# xsec_x_eff — (m_WR, m_N) 2D mass-grid 요약 (cut-based + BDT)

채널(EE, MM)마다 아래 5종을 (m_WR, m_N) 평면에 그리고, 같은 수치를 CSV로 남긴다.

| 양 | 의미 |
|---|---|
| `acceptance_{total,boost,resolve}` | SR에 남는 신호 비율 [%] |
| `xsec_times_acc_{total,boost,resolve}` | 이론 σ × acceptance [fb] |
| `significance_total` | Asimov Z (total = boost ⊕ resolve) |

여기에 더해 `ratio_plot.py` 가 두 방법의 acceptance 비를 m_N 함수로 그린다
(x = m_N, 선 4개 = m_WR, 채널별 그림 1장).

두 분석 방법을 각각 계산한다: **cut-based** (`Reproduce20_002_copy`) 와
**BDT** (`HNWR_BDT_presel` + XGBoost score > 0.5). 둘 다 **62.31 fb⁻¹**
(2022 + 2022EE + 2023 + 2023BPix) 기준이다.

## 실행

```bash
cd plots/HNWR/singnal_sample_test/xsec_x_eff

python cutbased_grid.py --outdir output/cutbased --check-xsec
python bdt_grid.py      --outdir output/bdt      --check-templates

# BDT / cut-based acceptance 비 (x = m_N, 선 = m_WR)
python ratio_plot.py                 # total
python ratio_plot.py --region all    # total/boost/resolve 3패널

# 두 방법이 겹치는 100 mass point로만 제한 (공정 비교용)
python cutbased_grid.py --outdir output/common/cutbased --grid common
python bdt_grid.py      --outdir output/common/bdt      --grid common
```

주요 옵션: `--style {scatter,mesh}`, `--csv-only`, `--grid {all,common}`,
`--wr` (기본 2000 4000 6000 8000, `--wr 0` 이면 전부),
BDT는 `--score-cut` (기본 0.5), `--eras`.

**m_WR 3000/5000/7000 은 기본에서 빠진다.** N 점이 1~2개뿐인 단발 probe라
(`WR3000N200/N1500`, `WR5000N200/N2500`, `WR7000N200/N3500`) 그리드에 넣으면
빈 열만 생긴다. 필요하면 `--wr 0` 으로 전부 넣을 수 있다.
x축은 실제 질량 축이 아니라 **균등 간격 슬롯**이다 (`draw_grid(categorical_x=True)`).

## 파일

| 파일 | 역할 |
|---|---|
| `grid_common.py` | xsec 로더, Asimov Z, 2D grid 플로터, CSV 저장 |
| `cutbased_grid.py` | cut-based 수치 추출 + 플롯. `PLOTS`/`make_plots` 는 BDT 쪽에서 재사용 |
| `bdt_grid.py` | BDT 수치 추출 + 플롯 |
| `ratio_plot.py` | 두 CSV를 읽어 `A_BDT / A_cut` 를 m_N 함수로 (선 = m_WR) |
| `check.ipynb` | 이 스터디의 원형 프로토타입 (건드리지 않음, 아래 "차이" 참조) |

산출물은 `output/<method>/` 아래 개별 PNG + `summary_{EE,MM}.png` (2×4 패널) + CSV.

## 정의

### 공통
- 이론 σ: `data/Run3_v12_Run2_v9/2022/Sample/CommonSampleInfo.json` 의 `xsec` [pb].
  EE/MM 키가 모두 있고 값은 같다. (로컬 `WRtoNELtoEEJJ_cross_sections.json` 은 EE
  이름 규약만 있고 수치는 동일 — 쓰지 않는다.)
- `A_total = A_boost + A_resolve`. 두 영역은 직교하다 (boosted cutflow bin 3 = "Not resolved").
- `Z_total = sqrt(Z_boost² + Z_resolve²)`.
- Asimov Z = `sqrt(2·((s+b)·ln(1+s/b) − s))`, `s≤0` 또는 `b≤0` 이면 0.

### cut-based
입력: `/gv0/.../Reproduce20_002_copy/combined_22_23/merged/` — 신호 114 mass point × {EE, MM}.

```
denom      = Central/Cutflow_for_reseolved_SR.values()[1]   # 모든 이벤트 = σ × L_eff
S_boost    = ∫ Central/SR_Boosted_<CH>_mlljj                # 최종 SR yield (SF 반영)
S_resolve  = ∫ Central/SR_Resolved_<CH>_mlljj
B_<reg>    = 배경 MC 전체 합 (mass point 무관)
Z_<reg>    = asimov_z(S, B)                                  # SR 전체 yield 하나로
```

cutflow bin이 아니라 `SR_*_mlljj` 적분을 쓴다. cutflow 히스토그램은
flavor-inclusive라 채널을 나눌 수 없고 마지막 SF 적용 전 값이다.
(검증: 배경 boosted cutflow bin 12 = 948 vs `SR_Boosted_{EE,MM}_mlljj` 합 = 927,
resolved bin 9 = 3540 vs 3188 — 차이는 cutflow fill 이후 곱해지는 SF.)

배경 제외 토큰: `Skim`, `EGamma`, `Muon`, `SingleMuon`, `DYJets`.
`DYJets` 는 inclusive aMC@NLO 샘플이라 HT-binned `DYMLL*` 와 이중계산된다
(`syst_plotter/integrated/plotter_file/year_sep/EE.py:44` 와 같은 규약).

### BDT
입력:
- 템플릿 `BDT/SR/all_mass_point_uniform/nb10/<era>/fit_templates/<cat>/<ch>/fit_template_<ch>_WR*N*.root`
  — era별 lumi-weighted BDT score TH1D (uniform 10 bin, [0,1]), 키
  `signal`, `DYJets`, `TT`, `Nonprompt`, `Others`. 100 mass point × 4 era × 2 cat × 2 ch.
- 분모 `/gv0/.../HNWR_BDT_presel/<era>/sig/{EE,MM}/WR*N*{EE,MM}.root` 의
  `Central/Cutflow.values()[0]`.

```
denom     = Σ_era Cutflow[0]
S_<cat>   = Σ_era Σ_{score>0.5} signal            # score>0.5 = bin index 5..9
B_<cat>   = Σ_era Σ_{score>0.5} (DYJets+TT+Nonprompt+Others)
Z_<cat>   = sqrt( Σ_bin asimov_z(s_bin, b_bin)² ) # 10 bin 전부 <- 플롯에 쓰는 값
```

검증: 100 mass point × 2 채널 전부에서 템플릿 `signal` 총적분이 presel
`Central/Cutflow` 의 SR bin (resolved=6, boosted=7) 과 1% 이내로 일치한다
(`--check-templates`). 또 `BDT/combine/scenarios/uniform_nb10/shapes/2023/2023_bdt_shapes.json`
의 `process_yields` 와도 자릿수까지 일치 (WR2000N1100 MM: boosted 121.81, resolved 1002.97).

## CSV 컬럼

공통: `method, channel, mWR, mN, xsec_pb, denom, denom_over_lumi_pb, lumi_frac,
s_*, b_*, acc_*(+_pct), xsec_acc_*_fb, z_boost, z_resolve, z_total`.

- `lumi_frac = (denom/L) / xsec` — 1에 가까워야 정상 (trigger lumi weighting 때문에 ~0.993).
- cut-based 추가: `z_*_shape` — mlljj shape Z (아래 "Z 비교" 참조). **플롯에는 안 쓴다.**
- BDT 추가: `z_*_allbins` (= 플롯 값), `z_*_gt0p5` (score cut 위 bin만),
  `z_*_incl` (score cut 위를 yield 하나로), `presel_sr_*`, `n_eras`, `score_cut`.

## Z 비교 시 주의

`z_total`(cut-based, inclusive)과 `z_total`(BDT, bin 합산)을 그대로 나누면
BDT가 중앙값 **11배** 좋아 보이는데, 이 중 상당 부분은 방법 차이가 아니라
**counting vs shape** 차이다. 같은 축에서 보면:

| 비교 | EE | MM |
|---|---|---|
| `A_bdt / A_cut` | 1.23 | 1.13 |
| inclusive Z: `bdt(z_total_incl) / cut(z_total)` | 6.50 | 6.26 |
| shape Z: `bdt(z_total_allbins) / cut(z_total_shape)` | 0.88 | 0.63 |

(200 공통 점의 중앙값. `output/common/` 의 CSV로 재현된다.)

`z_*_shape` 는 mlljj를 160 bin으로 rebin한 뒤 **배경이 1 이벤트 이상 쌓일 때까지
이웃 bin을 병합**해서 계산한다 (BDT 템플릿의 background Neff 가드와 같은 취지).
가드 없이 균등 40 bin으로 하면 배경이 0인 bin에서 Asimov Z가 발산해
cut-based Z가 5배쯤 부풀려진다.

그래도 **cut-based SR과 BDT presel SR은 서로 다른 영역**이라 (BDT presel이 훨씬 느슨해서
배경이 한 자릿수 배 많다) 이 비율들은 어디까지나 참고값이다. 계통오차와 CR 제약이
빠진 순수 Asimov 근사라는 점도 같다. 진짜 비교는 combine limit
(`BDT/combine/scenarios/plots/ratio_vs_cutbased/`) 쪽을 봐야 한다.

## 알려진 데이터 문제 (코드 문제 아님)

`combined_22_23/merged/` 에서:

| mass point | 상태 |
|---|---|
| `WR4000N2000MM` | 2022EE era 산출물이 비어 있어 lumi 57%만 존재 |
| `WR5000N2500MM` | 2023 + 2023BPix 가 비어 있어 lumi 56%만 존재 |
| `WR7000N3500MM` | 파일이 463 B (완전히 비어 있음) |
| `WR8000N4000MM` | 파일이 463 B (완전히 비어 있음) |

앞의 둘은 acceptance / σ×A 는 비율이라 그대로 유효하지만, S만 lumi가 모자라고
B는 full lumi라 Z가 왜곡되므로 **Z를 비워 둔다** (`lumi_frac < 0.95` 이면 자동).
뒤의 둘은 아예 빠져서 MM 채널은 112점, EE는 114점이다.
해당 era의 `Reproduce20_002_copy` 잡을 다시 돌리면 해결된다.

## `check.ipynb` 프로토타입과의 차이

| | `check.ipynb` | 여기 |
|---|---|---|
| lumi | 2023 단독 (17.96 fb⁻¹) | 22+23 합산 (62.31 fb⁻¹) |
| boosted 분자 | cutflow `values[-2]` = bin 11 (M_ll>200) | `SR_Boosted_<CH>_mlljj` (= bin 12, 최종 SR) |
| 채널 분리 | flavor-inclusive cutflow를 채널값처럼 사용 | 채널별 SR 히스토그램 |
| 저장 | 없음 (`plt.show()` 만) | PNG + CSV |
| significance | 없음 | Asimov Z |
| BDT | 없음 | `bdt_grid.py` |

`check.ipynb` 의 `resolved_hist_candidates` 첫 항목 `Central/Cutflow_for_Resolved_SR`
는 존재하지 않는 이름이다. 분석기가 쓰는 실제 이름은 오타가 들어간
`Cutflow_for_reseolved_SR` 하나뿐이다.

## 참고

- 관련 문서: `../../../../docs/HNWR_Analyzers.md`, `../../../../BDT/SR/README.md`,
  `../../../README.md`
- `BDT/README.md` 가 가리키는 `BDT/SR_R_B` 는 `BDT/Not_using/SR_R_B` 로 동결됐다.
  현역은 `BDT/SR`. `BDT/SR/README.md` 의 `all_mass_point/` 도 실제 프로덕션은
  `all_mass_point_uniform/nb10/` 이다.
