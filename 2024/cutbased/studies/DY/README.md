# DY background study (2024, cut-based) — 작업 기록

작성: 2026-09-19 (Claude Code 세션, 2026-09-18~19 작업분). AN-25-020 노트의 5.1절 (Drell–Yan background) 을
chihwan draft 에서 옮겨 오면서 한 확인·재플랏·검증을, 나중에 질문에 답할 수 있도록 중간 과정까지 적은 것이다.
ttbar 와 달리 **DY 내용은 노트에 그대로 들어가 있다** — 여기는 사본과 과정 기록이다 (원본을 옮기지 않았다).

## 폴더 구성 (단계별)

| 폴더 | 질문 | 핵심 문서 |
|---|---|---|
| `00_overview/` | DY 추정이 전체적으로 어떻게 돼 있나 (C × κ_EW × R), 입력 프로덕션, 노트의 어느 그림이 무엇인가 | `NOTES.md` |
| `01_zpt_correction_systematics/` | "Figure 10 에서 systematics 가 제대로 적용된 거 맞나? 차이가 너무 없는데" | `NOTES.md`, `check_zpt_syst_size.py/.out`, `run_log_zpt.txt` |
| `02_dycr_stage_plots_ratio_range/` | DY CR 단계별 플랏 (Fig. 12–18) 의 ratio pad 를 0.5–1.5 로 다시 그림 | `NOTES.md`, `specs/`, `logs/`, `plots/` |
| `03_cr1_to_cr2_closure/` | R 을 DY CR1 (60–100) 에서 구해 CR2 (100–150) 에 적용하는 closure. 2024 (이번) + 2022–2023 (7/29, 이전 작업) | `NOTES.md`, `scripts/`, `2024_*/`, `prior_2022_2023_CR1_2_validation/` |
| `04_nlo_pseudodata/` | NLO/LO vs Data/LO, NLO/LO 의 CR vs SR (AN2019_083 Fig. 31–32). 2024 POWHEG 의 문제, FxFx 부재 | `NOTES.md`, `scripts/`, 그림 3벌 |
| `05_related_changes_in_AN/` | DY 와 연결된 노트 수정 (Table 8 샘플, 본문 문장 등) 과 미해결 사항 | `NOTES.md` |
| `06_nlo_lo_mll_njet/` | C 가 jet 수에 의존하나 — gen m(ll)/Z pT 를 NLO·LO, jet 수별로 | `NOTES.md` |
| `07_jetpt_overlay/` | R 의 양쪽: (data − nonDY) 와 DY MC 를 jet pT 축에 겹침, 4 영역 | `NOTES.md` |
| `08_zpt_mll_differential/` | C(pT \| m_ll), theory error 재구현 | `NOTES.md` |
| `09_three_generators/` | LO / POWHEG / FxFx 비교, FxFx 2024 확보, jet별 C, 세 단계 data/MC. **06–09 전체 정리는 여기 `SUMMARY.md`** | `SUMMARY.md`, `PLOTS.md` |

## 한 장 요약

1. **Fig. 10 (C 의 theory variation)**: weight 는 제대로 걸려 있다 (NLO 총 yield 가 μF −5.0/+3.1%, PDF ±4.2% 등으로 움직임).
   C 를 pT>50 에서 shape-only 로 정규화하기 때문에 normalization 성분이 사라지고 남는 shape 차이는 최대 1.4% → y축 0–1.8 에서 안 보인다.
2. **Fig. 12–18**: 28장을 `--rmin 0.5 --rmax 1.5` 로 재생성해 같은 파일 이름으로 교체. 내용·입력은 9/17 실행과 동일.
3. **CR1→CR2 closure (2024)**: resolved data/MC 1.27→1.02 (ee), 1.31→1.05 (μμ); boosted 1.47→1.28, 1.24→1.11.
   처음 matplotlib 으로 넣었다가 "기존 형식으로" 지적을 받고 `plotter._draw` 형식으로 다시 그림 (수치 동일).
4. **NLO pseudo-data (2024)**: DY CR 에서 NLO/LO 가 0.70→0.05 로 떨어져 Data/LO (1.26→0.84) 와 안 맞는다.
   2022–2023 은 aMC@NLO FxFx 였고 2024 는 POWHEG (ME jet ≤1) 뿐. 2024 FxFx DY NanoAODv15 는 저장소에 없음 → 재현 불가, 참고용 그림만.
5. 부수 발견: 2024 DY 샘플 실제 이름은 `DYto2L-4Jets_Bin-HT-100to400-MLL-120` 형태 (노트 Table 8 에 넣은 2023 식 이름과 다름, 미수정).

## 공통 실행 환경

- 플랏: `cd plot/cutbased; ./condor/in_container.sh python ...` (singularity `private-el9.sif` + micromamba env `Nano15`, ROOT 6.40).
  scratch 에 쓰려면 `PLOT_EXTRA_BINDS="/tmp:/tmp"`.
- 입력은 전부 `/gv0/Users/achihwan/SKNanoOutput/HNWR/<production>/2024/`. `/gv0` cold read 가 병목 (플랏 한 장 1–4 분).
- 사용자의 `specs/`, `out/`, `DY/out/`, 원본 스크립트는 수정하지 않았다. 출력은 scratch → 노트 폴더 → 여기 사본.
- condor 는 이 호스트 (cms1) 에서 제출 불가 (tamsa2).
