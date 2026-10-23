# plots/ — HNWR (W_R→lN→lljj) 분석 플로팅 영역

> 이 디렉토리는 SKNanoAnalyzer-v13 분석기(`Reproduce20_002_copy` 등)가
> `/gv0/Users/achihwan/SKNanoOutput/`에 만들어 놓은 ROOT 파일을 읽어
> data/MC 비교 플롯, systematic band, yield 테이블(tsv)을 만드는 곳이다.
> 자체 git repo이며(analyzer repo와 별개), 실제 입력 ROOT 파일은 repo 밖에 있다.
>
> 자주 쓰는 명령어: [`../COMMANDS.md`](../COMMANDS.md) ·
> 개선 권고: [`../RECOMMENDATIONS.md`](../RECOMMENDATIONS.md)

## 한눈에 보는 구조 (활성도 순)

| 경로 | 상태 | 용도 |
|---|---|---|
| `HNWR/reproduce/syst_plotter/integrated/` | **현역 (메인)** | data/MC + systematic band 플로터. 3개 캠페인 유지 |
| `HNWR/singnal_sample/` (오타: signal_sample) | 현역 | 신호 전용 스터디: cutflow, tb fraction, xsec×eff 등 |
| `atlas/` | 준현역 (레퍼런스) | ATLAS 방식 재현 플로터. 코드가 가장 깔끔한 모범 사례 |
| `HNWR/combine/` | 유지 | `make_combineroot.py` — combine 입력 root + datacard 생성 |
| `HNWR/reproduce/regions/` | 부속 | 영역/카테고리 정의 모식도(2D schematic)만 그림 |
| `DY/` | **구식** | Z-peak data/MC 검증. syst_plotter의 DY CR로 대체됨 |
| `TTBar/` | **구식** | ttbar CR 플롯. syst_plotter의 FLV CR로 대체됨 |
| `HNWR/topchannel/` | **구식** | tb-channel CR 스터디 (2025-12에 동결) |
| `plotting_code_test/` | 폐기 | 초기 프로토타입 sandbox |
| `HNWR/reproduce/plotall.sh` | **깨짐** | 삭제된 `hlt_ele_dif/` 경로를 참조 — 실행 불가 |

## 입력 데이터 규약

- 분석기 출력: `/gv0/Users/achihwan/SKNanoOutput/<Analyzer>/<era>/` 아래
  **샘플당 ROOT 파일 1개** (이미 lumi-weighted; 플로터는 재규격화하지 않음).
- 파일 내부 구조: `Central/<hist>` 및 `{SYST}_Up/<hist>`, `{SYST}_Down/<hist>` TDirectory.
- 메인 플로터 입력 경로 (플로터 스크립트 상단 dict):
  - era별: `/gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy/combined_22_23/<era>/`
    (예외: 2024는 `.../Reproduce20_002_copy/2024/`)
  - era 합산: `.../combined_22_23_24/merged/` (172.13 fb⁻¹ = 2022+2023+2024)
- 신호 샘플 파일명: `WR{M_WR}N{M_N}{EE,MM}` (예: `WR2000N1000EE`).

## 메인 플로터 메커니즘 — `syst_plotter/integrated/`

캠페인 3종 (각 폴더 안에 Boost/Resolve × DY/FLV/sig(=SR) × EE/MM 리프 폴더):

1. `charge_inclusive_year_sep/{2022,2022EE,2023,2023BPix,2024}/…` — era별 플롯
2. `charge_inclusive_year_combined/{boost,resolve}/{DY,FLV,sr}/…` — 전체 era 합산
3. `charge_tight_year_sep/` — tight charge 요구 변형 (구버전, 대부분 대체됨)

**canonical 템플릿은 `plotter_file/year_sep/{EE.py,MM.py}`** 이고, 각 리프 폴더의
`EE.py`/`MM.py`는 이 템플릿의 **바이트 동일 복사본**(총 ~124개)이다.
리프 폴더 위치는 출력 파일명 prefix를 만드는 데만 쓰인다 (`EE.py:704-709`).
→ syst 리스트·색상 등을 바꾸려면 템플릿 수정 후 전체 재복사가 필요함 (RECOMMENDATIONS 참조).

`EE.py`(≈`MM.py`, 채널은 파일명에서 자동 감지 `:16-19`) 동작 순서:

1. **샘플 그룹핑** (`:22-41`): 파일명 substring 매칭 →
   `DYJets`(kYellow, "Drell-Yan") / `TT`=TTLL+ST(kRed) / `Nonprompt`=TTLJ,WJets,ST_tch/sch(kGreen+2) / `Others`(kBlue).
   Data는 EE→`EGamma`, MM→`Muon`. `EXCLUDE_SAMPLES`로 반대 채널 데이터 제외.
2. **히스토그램 로드**: `f.Get("Central/<hist>")`, overflow는 마지막 bin에 fold (`:133-146`).
3. **Systematic band** (`SYST_LIST :42-43`): Pileup, Electron{ID,Reco,Trig},
   Muon{ID,Reco,Trig,Iso}, JER, JES. 각 syst의 `_Up/_Down`을 읽어
   bin별 max(|up|,|down|) envelope → `sqrt(stat² + Σsyst²)` 총 band.
   메인 pad에는 회색 hatch(3013) `TGraphAsymmErrors`, ratio pad에는 총 band + 주황 stat-only band.
4. **Blinding**: 히스토그램 이름에 `SR` 포함 시 data 숨김, ratio pad에 "Blinded" 표시 (`:186,:839-844`).
5. **2024 신호 hack** (`:176-183`): 2024엔 WR 신호 샘플이 없어 2023 신호를
   `109.82/17.96 = 6.1147`배 스케일해 대용 (syst 변형에도 적용). 임시방편임에 유의.
6. **신호 표시 스케일**: `--signal-scale` (기본 ×10, 표시 전용, 라벨에 `(×10)` 자동 표기).
7. **출력**: `<name>_plot.png`, `<name>.tsv` (bin별 yield + syst% + 그룹/신호별),
   `<name>_integrated.tsv`, `--show-sb` 시 `<name>_ssqrtb.tsv`,
   신호별 `signal/<Region><Sub><Chan>_<year>_<WR…>_integrated.tsv`.

**실행 체인**: 리프 `plotter.sh`(관측량 ~35개 × `python EE.py --hist … --rebin … --year …`)
→ era별 `all.sh` → HTCondor `condor_files/plotter_all.dag`
(sep_22_23 + sep_2024 + combined 서브 DAG; tamsa2에서 제출).

**제출 전 필수 게이트**: `check_inputs.py` — 어떤 MC 샘플이 `Central`만 있고
`{syst}_Up/Down`이 없으면 exit 1로 차단. 이 가드를 건너뛰면
year_sep 플로터는 편차 전체를 한쪽(down)으로 계상하고, year_combined는 Central로
대체해 band를 과소평가한다 (두 변형의 처리 방식이 서로 다름 — 알려진 함정).

## 기타 활성 영역

- **`HNWR/combine/make_combineroot.py`**: 동일한 merged 입력에서 combine용
  shape root 파일 + datacard 뼈대를 생성. `get_hist_from_file`과 syst envelope
  로직이 플로터와 **동일 코드 복제본**이므로 한쪽을 고치면 반드시 같이 고칠 것.
- **`HNWR/singnal_sample/cutflow/`** (2026-07-11 활동): `cutflow.py`,
  `tb_fraction_grid.py`, `cutflow_tb_vs_light.py` — 신호 샘플 cutflow/조성 스터디.
- **`atlas/`**: 자세한 사용법은 `atlas/README.md`. HNWR 플로터와 달리
  **stat-only band**이며 히스토그램 경로가 ATLAS식(`Resolved/rSROS2e/mlljj` 등).
- 작업 로그: `HNWR/reproduce/syst_plotter/integrated/2026-07-08_HNWR_2024_작업정리.md` (한글).

## 새 플롯을 추가할 때 (Claude Code용 체크리스트)

1. 템플릿은 `syst_plotter/integrated/plotter_file/year_sep/EE.py` 기준으로 수정.
2. 수정 후 리프 폴더들의 복사본도 동기화해야 함 (현재 공유 모듈 없음).
3. 실행 전 `check_inputs.py`로 syst 변형 누락 샘플 확인.
4. SR 플롯은 자동 blind — 이름에 `SR`이 들어가는지 확인.
5. 2024 관련 플롯은 신호가 2023×6.1147 대용임을 캡션/해석에 반영.
