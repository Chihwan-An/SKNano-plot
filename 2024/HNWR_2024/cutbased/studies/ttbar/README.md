# ttbar+tW background estimation study (2024, cut-based) — 작업 기록

작성: 2026-09-19 (Claude Code 세션). 요청: "AN2019_083 §5.2 의 eμ CR simultaneous fit 으로 ttbar 추정을
구현/검증하고, Appendix J 의 플랏을 2024 로 그대로 따라 그릴 것". 처음에는 AN-25-020 노트에 넣었다가
사용자 요청으로 **노트에서는 전부 빼고** 이 폴더로 옮겼다 (AN 은 76쪽, ttbar 관련 흔적 없음 확인).

이 문서들은 나중에 질문을 받았을 때 답할 수 있도록 "무엇을, 어떤 입력으로, 어떤 명령으로, 왜" 했는지를
중간 과정과 시행착오까지 포함해 적은 것이다. 숫자는 전부 실제 실행 결과에서 옮겼고, 출처 파일을 같이 적었다.

## 이 스터디를 처음 보면

**[`SESSION_20260922.md`](SESSION_20260922.md) 를 먼저 읽는다** — 2026-09-22/23 세션에서 한 일 전부가
한 장에 있다 (환경 문제, 입력 결함 3개, 합친 fit, postfit 플랏 24장, impacts, blind limit,
DY-only SS 템플릿, 남은 것).

실행이 멈추면 **[`RUNBOOK_env.md`](RUNBOOK_env.md)** — `cmssw-el9` 래퍼는 이 호스트에서 무한 정지한다.
네이티브로 돌릴 것.

미결 항목 전체는 **[`06_open_issues.md`](06_open_issues.md)** (§1~15).

## 폴더 구성 (읽는 순서)

| 폴더 | 내용 | 핵심 문서 |
|---|---|---|
| `01_inputs_and_selection/` | 어떤 산출물을 입력으로 썼는지, region 정의, 두 입력(히스토그램 / ntuple)의 일치 검증, weight 함정 | `NOTES.md` |
| `02_production_card_audit/` | 기존 cut-based card 체인 조사. 모델이 이미 구현돼 있었다는 것, **데이터 stream 버그 2개** 발견·수정, rateParam 연결표 | `NOTES.md`, `*.diff`, `audit_*.py` |
| `03_combine_validation/` | Combine 검증: synthetic β injection / mask test, 실데이터 CR-only fit, blind expected limit | `NOTES.md`, `README.md`(실행법), `results_20260919/`, `work_20260919/` |
| `04_emu_method_appendixJ/` | AN2019_083 App. J (옛 eμ data-driven 방법) 의 2024 재현: 비율, sideband, closure, syst scan, 표 | `NOTES.md`, `scripts/`, `plots/`, `tables/`, `hists/` |
| `05_an_text_removed_from_note/` | 노트에 썼다가 뺀 LaTeX 원문 (§5.2 재작성본, Appendix) | `*.tex` |
| `07_ss_dyonly_flip/` | SS 를 DY 만 charge-misID 로 추정하는 변형 (2026-09-22). baseline 과 1% 일치, ttbar 는 β 가 통제 | `NOTES.md` |
| `06_open_issues.md` | 남은 물리/구현 이슈와 결정이 필요한 것 (§1~15) | |
| `SESSION_20260922.md` | **2026-09-22/23 세션 한 장 요약** — 여기부터 읽으면 된다 | |
| `RUNBOOK_env.md` | `cmssw-el9` 래퍼가 멈출 때의 진단·해결·재개 | |

## 한 장 요약

1. **모델은 이미 있었다.** `BDT/SR/test/scripts/cbv15_dc_cards.py` 가 `R_TT_Resolved_2024`,
   `R_TT_Boosted_EE_2024`, `R_TT_Boosted_MuMu_2024` 세 `rateParam` 으로 TT(=ttbar+tW) template 을
   SR + DY CR + eμ flavor CR 에 묶어 동시에 fit 한다. AN §5.2 의 최종 방식과 같은 구조.
2. **그런데 CR 입력이 틀려 있었다** (`cbv15/post_processor_chsplit.py`):
   - `rFlvCR` 데이터가 EGamma+Muon 합 = 7182 (Muon 만 = 3623, MC 3469) → 2배.
   - region 의 data 패턴에 없는 stream 의 데이터 파일이 MC `Others` 로 더해짐 (bFlvEMuCR Others 22→458 등).
   두 곳을 고치고 CR 만 재생성해 새 시나리오 `cbv15_an2_ref_fixstream` 을 만들었다.
   **(2026-09-22 갱신)** 그 뒤 결함 2개를 더 찾아 고치고(SS 채널의 TT rateParam, charge-inclusive rFlvCR),
   boosted SR 도 재생성했다. 전부 반영한 시나리오가 `cbv15_an2_ref_v2` 다 — `SESSION_20260922.md` 참조.
3. **검증 결과** (Combine v10.5.1-3-gb937f34f, CMSSW_14_1_0_pre4, cmssw-el9 container):
   - synthetic: β=1.2 주입 → 1.2000 ± 0.0360 복원, masked SR Top = [48,24,12], mask 기능 통과.
   - 실데이터 CR-only fit (수정 시나리오): R_TT_Resolved 0.879±0.042, R_TT_Boosted_EE 0.804±0.113,
     R_TT_Boosted_MuMu 0.765±0.211 (EE card). status 0, covQual 3, 경계 안.
     수정 전 시나리오: R_TT_Boosted_* = 0.500 (하한에 붙음), R_TT_Resolved = 1.415.
   - blind expected limit: 정상 동작, 수정 전후 차이 < 0.5%.
4. **App. J 재현** (BDT presel ntuple 에서 low-mass 영역을 만들어서): ee/eμ 0.45, μμ/eμ 0.60–0.63,
   boosted ee/μe 0.94, μμ/eμ 1.18–1.21. low-mass closure: resolved 1.02 / 1.08, boosted 1.52 / 1.45.
5. **결정이 필요한 것**: boosted CR↔SR 짝 맞춤이 AN 과 반대, resolved eμ CR 의 질량 기울기, JES +3.3σ,
   SR shapes 전체 재생성. → `06_open_issues.md`.

## 이 세션에서 건드린 것 전체 목록

**새로 만든 것 (이 폴더 밖)**
- `BDT/SR/test/cbv15dc/shapes_2024_dc_cr_fixstream.root` — 수정된 pp 로 재생성한 CR 10개 region.
- `BDT/combine/scenarios/test/cbv15_an2_ref_fixstream/` — 위 CR 을 쓴 card 24장 + shapes.
  (card 가 shapes 절대경로를 참조하므로 옮기지 않았다.)

**수정한 기존 파일 (둘 다 git 미추적이라 같은 폴더에 백업을 남김)**
- `BDT/SR/test/cbv15/post_processor_chsplit.py` ← 백업 `.bak_20260919_datastream`, diff: `02_.../post_processor_chsplit.diff`
- `BDT/SR/test/scripts/cbv15_dc_cards.py` ← 백업 `.bak_20260919`, diff: `02_.../cbv15_dc_cards.diff` (`--shapes-override` 추가만)

**읽기만 한 것**: `HNWR/src/HNWR.cc`, `plot/HNWR_2024/cutbased/config.py`, `plotter.py`, `chargeflip_plots.py`,
`/gv0/.../HNWR/RFlav*/2024`, `/gv0/.../HNWR_BDT_presel_3SR/2024`, 기존 시나리오들.

## 실행 환경 메모

- 호스트 cms1 = AlmaLinux 8. Combine CMSSW 는 el9 → `/cvmfs/cms.cern.ch/common/cmssw-el9 -B /data6 -B /data9 -B /gv0 -B /tmp -- bash <script>` 필수.
  첫 실행은 cvmfs cold cache 때문에 환경 준비만 수 분 걸린다 (hang 아님).
- 플랏/ntuple 읽기: `plot/HNWR_2024/cutbased/condor/in_container.sh python3 ...` (ROOT 6.40, micromamba env Nano15).
  scratch 를 쓰려면 `PLOT_EXTRA_BINDS="/tmp:/tmp"`.
- RNTuple 은 이 env 의 uproot 로 못 읽는다 (checksum assert). `ROOT.RDataFrame` 으로 읽는다.
- condor 제출은 이 호스트에서 불가 (tamsa2 에서만).
