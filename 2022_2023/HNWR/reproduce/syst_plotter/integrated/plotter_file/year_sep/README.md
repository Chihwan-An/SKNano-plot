# year_sep/EE.py, MM.py 사용법

era별(2022/2022EE/2023/2023BPix/2024) 또는 Run3 2022+2023 통합 systematic-uncertainty-band
data/MC 비교 플랏을 그리는 스크립트. `EE.py`는 EGamma(전자) 채널, `MM.py`는 Muon 채널용이며 나머지
로직은 동일함.

## 기본 실행

```bash
cd /data6/Users/achihwan/SKNanoAnalyzer-v13/plots/HNWR/reproduce/syst_plotter/integrated/plotter_file/year_sep
python3 EE.py --hist Obj_PU_Corr_DYCR_Resolved_EE_pt
```

`--year`를 안 주면 `DEFAULT_DATA_PATH` (`.../combined_22_23/merged/`, Run3 2022+2023 4개 sub-era를
합친 데이터)를 사용하고, 라벨에는 `62.31 fb^-1 (13.6 TeV)`가 찍힘.

## era 하나만 골라서 그리기 (`--year`)

```bash
python3 EE.py --hist Obj_PU_Corr_DYCR_Resolved_EE_pt --year 2024
python3 MM.py --hist Obj_PU_Corr_DYCR_Resolved_MM_pt --year 2023BPix
```

`--year` choices: `2022`, `2022EE`, `2023`, `2023BPix`, `2024`.

- `2022`/`2022EE`/`2023`/`2023BPix` → `DATA_PATH_BY_YEAR`를 통해
  `/gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy/combined_22_23/{year}/`를 읽음.
- `2024` → 위 combined 트리에 없고 별도 raw merged 경로
  `/gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy/2024/`를 읽음 (2024는 아직 2022+2023
  combine 단계에 합쳐지지 않았고, 샘플 이름도 NanoAODv15 기준: `DYto2E/2Mu_MLL...`,
  `EGamma0/1_C~I.root`, `Muon0/1_C~I.root`, `WtoLNu_1J~4J.root` 등으로 다름).

각 era 선택 시 CMS 라벨에 찍히는 luminosity는 `LUMI_BY_YEAR`에서 자동으로 맞춰짐:

| year | luminosity |
|---|---|
| 2022 | 7.99 fb⁻¹ |
| 2022EE | 26.68 fb⁻¹ |
| 2023 | 17.96 fb⁻¹ |
| 2023BPix | 9.68 fb⁻¹ |
| 2024 | 109.82 fb⁻¹ |
| (미지정, 기본) | 62.31 fb⁻¹ (2022+2022EE+2023+2023BPix 합산) |

luminosity 값이 바뀌면 스크립트 상단의 `LUMI_BY_YEAR` dict만 고치면 됨 (EE.py, MM.py 둘 다 동일하게
있으니 같이 수정).

## 주요 옵션

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `--hist` | `Obj_PU_Corr_DYCR_Resolved_EE_pt` | 불러올 히스토그램 이름 (파일 내 `Central/<hist>` 경로에서 로드) |
| `--year` | None | 위 표 참조. 안 주면 Run3 22+23 통합 |
| `--rebin` | 1 | 리빈 factor |
| `--bins` | None | 커스텀 bin edge, 쉼표로 구분 (예: `--bins 0,100,200,500,1000`) — 지정 시 `--rebin` 무시 |
| `--xmin` / `--xmax` | 40 / 2000 (또는 `--bins`의 양 끝) | x축 범위 |
| `--ymin` / `--ymax` | 5.0 / auto | y축(상단 패널) 범위 |
| `--rmin` / `--rmax` | 0.5 / 1.5 | ratio 패널 y축 범위 |
| `--logy` | on (지정하면 꺼짐) | y축 로그 스케일 |
| `--signal-scale` | 10.0 | WR 시그널 히스토그램에 곱할 스케일 |
| `--show-sb` | off | 빈별 S/√B 표 + TSV 출력 |
| `--label1` | `"ee"` | 좌측 채널 라벨 |
| `--label2` | `IS_BLIND` 여부로 자동 (`"Resolved SR"` / `"Boosted DY CR"`) | 좌측 영역 라벨 |
| `--output` | `--hist` 값과 동일 | 출력 파일 접두사 |

히스토그램 이름에 `SR`이 들어있으면 자동으로 blind 모드(데이터 안 그림, ratio 패널에 "Blinded" 표시)로
전환됨.

## 결과물

`--output`(또는 `--hist`) 기준 아래 파일들이 실행 디렉토리에 생성됨:

- `<output>_plot.png` — data/MC 스택 + systematic band + ratio 패널
- `<output>.tsv` — bin별 yield/systematic 상세
- `<output>_integrated.tsv` — 전체 적분값 기준 한 줄 요약
- `<output>_ssqrtb.tsv` — `--show-sb` 줬을 때만, bin별 S/√B
- `signal/<Region><Category><Channel>_<year_dirname>_<WR샘플>_integrated.tsv` — 시그널 샘플별 개별 요약
  (2024처럼 WR 시그널 파일이 아직 없으면 값 0으로 채워서 생성됨)

## 2024 관련 참고

- 2024는 아직 자체 WR 시그널 샘플이 없음 (`/gv0/.../Reproduce20_002_copy/2024/`에 `WR*.root` 없음).
  대신 `--year 2024`일 때 시그널 히스토그램만 **2023 단독 디렉토리
  (`combined_22_23/2023/`)에서 로드해서 `109.82/17.96` 배(2024/2023 luminosity 비)로 스케일링**해서
  대체 시그널로 사용함 (`SIGNAL_DATA_PATH`, `SIGNAL_LUMI_SCALE` 참고). 배경(DY/TT/Nonprompt/Others)과
  데이터는 그대로 2024 자체 데이터를 사용함 — 시그널만 2023 shape을 빌려온 것.
  - 실제 2024 WR 시그널 샘플이 생기면 `SIGNAL_DATA_PATH = DATA_PATH`, `SIGNAL_LUMI_SCALE = 1.0`으로
    되돌리면 됨 (해당 `if args.year == "2024":` 블록을 지우면 자동으로 일반 로직을 탐).
- 2024 데이터는 아직 `combined_22_23`처럼 다른 era와 hadd로 합쳐지는 단계를 거치지 않은 raw merged
  상태. Run3 2022~2024 전체를 하나로 합쳐서 보고 싶으면 `combined_22_23/merge.sh` /
  `merge_data.sh`에 해당하는 2024 포함 버전을 별도로 만들어야 함 (이번 작업 범위 아님).
