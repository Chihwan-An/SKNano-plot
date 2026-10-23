# HNWR 2024 배경 kinematic 플롯

2024 단독, 배경 MC + Data. SR 에는 시그널 질량점 2개를 선으로 겹쳐 그린다.
v13 의 `plots/HNWR/reproduce/syst_plotter/integrated/charge_inclusive_year_sep/2024`
설정을 nano15 (NanoAODv15) 로 옮긴 것.

입력: `/gv0/Users/achihwan/SKNanoOutput/HNWR/2024/<sample>.root` (`config.INPUT_DIR`)
출력: `out/<Boost|Resolve>/<리전>/<flavour>/<오브젝트>/<OS|SS|Inclusive>/` —
plotter 가 `layout.py` 규칙으로 처음부터 이 위치에 쓴다. DAG 끝의 `organize` job 은
예전에 평평하게 남은 산출물만 마저 옮기는 보험이다.

## 빠른 사용법

```bash
# 0) 입력 점검 — 파일 목록, 샘플 그룹, syst 커버리지, 히스토그램 존재 여부
./condor/in_container.sh python check_inputs.py

# 1) 한 job 만 손으로 (스모크 테스트)
./condor/run_specs.sh Resolve_sig_EE --stat-only --limit 3

# 1') 특정 플롯만 다시 (--match 는 --output 에 거는 정규식)
./condor/run_specs.sh Resolve_sig_EE --match '_(mlljj|WRMass)(_fine)?$'

# 2) 전부 condor 로  (condor 서브밋 노드에서. ai-tamsa1 에는 condor 가 없다)
./submit.sh
```

`submit.sh` 는 점검 -> DAG 생성 -> `condor_submit_dag` 순으로 돈다.
DAG 만 만들려면 `./condor/in_container.sh python make_dag.py`.

## 구조

| 파일 | 역할 |
|---|---|
| `config.py` | 입력 경로, luminosity, 배경 그룹 규칙, `SYST_LIST`, 리전 10개 정의 |
| `plotter.py` | 플롯 하나를 그리는 본체. TFile 캐시가 여기 있다 |
| `run_specs.py` | 스펙 파일 하나를 한 프로세스에서 전부 처리 (condor job 본체) |
| `specs/*.txt` | 리전×채널별 플롯 목록. 한 줄이 플롯 하나 |
| | mass 는 두 벌이다: `_mlljj`/`_WRMass` = WR mass 비닝(datacard 와 같은 경계), `_..._fine` = 100 GeV (Resolve DY 는 200 GeV) 등간격. 모양 확인은 fine, 분석은 coarse |
| `specs/chargesplit/` | OS/SS 분리 플롯 1012개. v13 에서도 기본 비활성이라 DAG 에 없다 |
| `check_inputs.py` | 제출 전 점검 |
| `layout.py` | 출력 이름 -> `<flavour>/<오브젝트>/<OS\|SS\|Inclusive>` 폴더 규칙 (plotter/organize 공용) |
| `organize_files.py` | 평평하게 남은 예전 결과를 계층 구조로 이동 (`--dry-run` 지원) |
| `make_dag.py` | `condor/condor_plotter.sub` + `condor/plotter.dag` 생성 |
| `condor/in_container.sh` | singularity + micromamba 안에서 명령 실행. `PLOT_EXTRA_BINDS` 로 bind 추가 |
| `tools/convert_v13.py` | v13 `plotter.sh` -> `specs/*.txt` 1회성 변환기 |

## 왜 이렇게 나눴나

v13 은 플롯 하나당 파이썬 프로세스 하나였다. 그 프로세스는 입력 ROOT 파일
85 개를 `Central + syst 31종 x Up/Down` 만큼, 즉 파일당 60 번 넘게 다시 열었다.
플롯이 540 개니 `TFile::Open` 이 300 만 번. `/gv0` 는 네트워크 파일시스템이라
여기가 병목이었다 (실측: wall 93 s 중 CPU 15 s).

지금은 job 하나가 (리전, 채널) 하나를 통째로 맡고, `plotter.py` 가 TFile
핸들을 캐시한다. 파일은 job 당 한 번만 열린다. 추가로
* Central 히스토그램을 샘플별로 들고 있다가 syst 디렉토리가 없는 샘플의
  fallback 으로 재사용한다 (DY 전용 syst 의 non-DY 샘플이 여기 해당).
* 어떤 MC 샘플도 안 가진 syst 는 variation 이 정확히 0 이므로 루프를 건너뛴다.

세 번째로, 파일을 열어둔 채 `f.Get()` 을 하면 읽어온 히스토그램이 그 TFile 의
메모리 디렉토리에 쌓인다. `TH1.AddDirectory(False)` 로 막지 않으면 job 하나가
수 GB 로 부푼다.

### 실측 (2026-08-18, 7월 stale 산출물 기준)

| | |
|---|---|
| Central 캐시 + 빈 syst 건너뛰기 적용 전 -> 후 | 18.3 s/plot -> 1.2 s/plot |
| `AddDirectory(False)` 적용 전 -> 후 (peak RSS) | 34 플롯 중 13 플롯에서 2.1 GB (증가 중) -> 34 플롯 완주 1577 MB |
| 메모리 증가 여부 (플롯 5 / 15 / 34개) | 1570 / 1572 / 1577 MB — 평평 |
| `Resolve_sig_EE` (34 플롯) 전체 | exit 0, 34/34 |

TSV 는 최적화 전후 **바이트 단위로 동일**함을 확인했다.

주의: 위 시간은 stale 입력 기준이라 낙관적이다. 7월 산출물에는 syst 디렉토리가
10 종밖에 없는데 (`config.SYST_LIST` 는 당시 31 종, 지금은 22 종) 새 산출물에는
전부 들어오므로 읽는 양이 두 배 넘게 늘어난다. `request_memory` 는 4GB 로 잡아뒀다 (실측의 2.5 배).

### 실측 (2026-08-21, 8월 skim 산출물 / condor 실제 run)

| | |
|---|---|
| job 하나 (34 플롯, syst 포함) | **23~25 분** — `Resolve_DYCR2_EE` 23분 / `_MM` 24분, 둘 다 exit 0 |
| 플롯 하나의 시간 구성 (cProfile) | 47.4 s 중 **46.9 s (99%) 가 `TDirectoryFile::Get`** |
| read 당 — /gv0 cold / 로컬 사본 | **35.6 ms / 3.6 ms** (10배) |
| read 당 — 이미 읽은 것 (캐시) | 1.9 ms  <- **이 숫자로 판단하지 말 것** |
| /gv0 순차 복사 | 18~19 MB/s (DAG 19개가 돌던 중) |

**`--limit 2` 로 잰 s/plot 은 믿지 말 것.** 처음에 `Resolve_DY_EE --limit 2` 로
298 s/plot 이 나왔지만, 이건 job 시작 때 한 번 내는 파일 열기 비용이 두 플롯에
통째로 얹힌 값이다. 34 플롯 완주 기준으로는 41 s/plot 이다 — 7배 차이다.

**시간의 99% 는 cold read 다.** 그래서 `condor/run_specs.sh` 가 입력을 워커
로컬 디스크(`$_CONDOR_SCRATCH_DIR`)로 복사한 뒤 거기서 읽는다:

```
복사 없음:  34 플롯 x 47 s       = 26 분
복사 있음:  6.9 분 + 34 x 7.2 s  = 11 분
```

**캐시된 히스토그램을 재면 1.9 ms 가 나와서 "I/O 는 병목이 아니다" 라는 반대
결론이 나온다.** 실제로 그렇게 잘못 판단한 적이 있다. 다시 잴 일이 있으면
반드시 그 세션에서 한 번도 안 읽은 히스토그램으로 잴 것.

**condor 의 CPU 집계는 믿지 말 것.** `Run Remote Usage` 가 wall 1996 s 에
CPU 16 s (0.8%) 로 찍히는데, 같은 방식으로 찍힌 job 이 68 개 플롯을 정상으로
그려냈다. singularity 안의 CPU 를 못 잡는 것으로 보인다. I/O 대기의 증거가
아니다.

MC 파일 수는 오히려 줄었다 (85 -> 44). 메모리는 실측 2.4 GB 로 `request_memory`
4GB 안에 들어온다.

### eviction — 실제로 job 을 못 끝내던 원인

첫 제출 (19 job) 에서 관측:

```
19 제출 -> 39 실행 (20회 재시작) -> 22 eviction -> 2 완주
```

evict 는 시작 후 **33~41 분**에 온다 (`TimeExecute` 1996 / 2242 / 2480 s).
job 은 23~25 분이라 아슬아슬하다 — 빠른 노드에 걸리면 살아남고, 느린 노드에
걸리면 문턱을 넘겨 evict 된다. 재개가 없으면 **처음부터 다시 그리므로** 그런
job 은 영원히 안 끝난다.

`condor/run_specs.sh` 가 `--skip-existing` 을 붙여서 이걸 막는다. png 는 두 tsv
다음에 쓰이므로 png 가 있으면 그 플롯은 끝난 것이고, 재시작은 남은 것부터
이어서 한다.

그래서 `submit.sh` 는 `out/` 에 png 가 남아 있으면 물어본다 — 이어서 돌리는
거면 그대로 진행하고, 코드를 바꿔 전부 다시 그려야 하면 `./clean.sh` 를 먼저
돌려야 한다. 안 그러면 낡은 플롯이 조용히 살아남는다.

## job 목록 (19 + organize)

```
Boost_DY_EE      Boost_DY_MM       Boost_DYCR1_EE   Boost_DYCR1_MM
Boost_DYCR2_EE   Boost_DYCR2_MM    Boost_FLV_EMJ    Boost_FLV_MEJ
Boost_sig_EE     Boost_sig_MM      Resolve_DY_EE    Resolve_DY_MM
Resolve_DYCR1_EE Resolve_DYCR1_MM  Resolve_DYCR2_EE Resolve_DYCR2_MM
Resolve_FLV_EM   Resolve_sig_EE    Resolve_sig_MM
```

## v13 에서 고친 것

* **라벨.** `plotter.sh` 가 `--label2` 를 한 번도 안 넘겨서 스크립트의 기본값
  (`"Resolved SR" if IS_BLIND else "Boosted DY CR"`) 이 그대로 찍혔다. 리전 10 개 중
  6 개가 틀린 라벨이었다 (Resolve DY/DYCR1/DYCR2, Boost FLV, Resolve FLV 는 전부
  "Boosted DY CR", Boost sig 는 "Resolved SR"). 이제 `config.REGIONS` 에서 넣는다.
  Boost 의 DYCR1/DYCR2 만 `EE.py` 사본을 따로 뒀던 이유도 이 라벨 때문이었다.
* **`organize_files.py` 가 SR/DYCR1/DYCR2 를 정리하지 않았다.** `SUBDIRS` 에
  `'Boost/sr'` 이라 적혀 있었는데 실제 디렉토리는 `'sig'` 였고, DYCR1/DYCR2 는
  아예 목록에 없었다. 이제 `config.REGIONS` 를 직접 읽는다.
* **중복 플롯.** Boost 의 DY/DYCR1/DYCR2 에서 `_mll` 을 ratio 범위만 바꿔 두 번
  그리고 있었다 (뒤엣것이 앞엣것을 덮어씀). 546 -> 540.
* **`_integrated.tsv` 오분류.** `organize_files.py` 가 `_plot` 접미사만 떼고
  `_integrated` 는 안 떼서, `jetnum`/`punum` 처럼 완전일치 규칙을 쓰는 변수의
  `_integrated.tsv` 가 전부 `other/` 로 갔다.
* **blind 플롯의 빈 범례.** blind 면 stat-only 밴드를 아예 안 그리는데 범례에는
  남아 있어 빈 스와치가 찍혔다.
* **죽은 systematic.** `SYST_LIST` 의 `MiniIso` 는 `MCLRSM.yaml` 어디에도 없다.
  플롯마다 파일을 한 번 더 열고 Central 로 되돌아오기만 했다.
* **`*DYReshapeBin*` 9개 제거 (2026-08-21).** 8월 산출물에 디렉토리가 하나도 없다
  (DY 파일의 top-level 키 51개를 직접 확인 — 이름이 바뀐 게 아니라 안 만들어졌다).
  아날라이저에서 R 을 끄는 건 `ZptOnly` userflag 인데 provenance 의 `Userflags` 는
  비어 있으므로 원래는 나왔어야 한다. **산출물이 고쳐지면 다시 넣을 것.** 지금
  band 는 그만큼 과소평가된 상태다. 31 종 -> 22 종.

`specs/*.txt` 는 v13 `plotter.sh` 와 인자 단위로 대조해 540 개 전부 일치함을
확인했다 (중복 6 개 제거 후).

## 손볼 만한 곳

* **luminosity** — `config.LUMI_LABEL`. 지금은 v13 값 `109.82 fb^{-1}` 그대로다.
* **입력 경로** — `config.INPUT_DIR`, 또는 `--input` 으로 그때그때 덮어쓰기.
* **어떤 파일을 쓸지** — `config.INPUT_PREFIX` (기본 `"Skim_HNWR_"`). 아날라이저를
  skim 위에서 돌리면 산출물 이름 앞에 skim 이름이 붙는데, `INPUT_DIR` 에는 접두사
  없는 7월 산출물이 아직 섞여 있다. 같은 샘플이 옛 이름으로도 들어와 있어서 둘 다
  읽으면 배경이 이중으로 쌓이므로, 접두사가 맞는 파일만 쓰고 그룹 매칭은 접두사를
  뗀 이름으로 한다. 옛 평평한 산출물로 스모크 테스트할 땐 `""` 로 둘 것.
* **시그널을 배경에서 빼기** — `config.SIGNAL_GLOBS` (기본 `["WRtoN*"]`). 2024
  산출물에는 시그널이 228개 같이 들어와 있어서, 안 빼면 전부 배경 스택에 쌓인다.
* **시그널 오버레이** — `config.SIGNAL_POINTS` / `SIGNAL_CHANNEL_TAG` /
  `SIGNAL_REGIONS`. 위의 제외와는 별개 경로다: 스택에서 뺀 시그널 중 질량점 몇 개만
  골라 스택 위에 선으로 겹쳐 그린다. 명목 단면적 그대로이고 배율은 없다. 스택,
  `h_total_mc`, syst band, ratio 패널, TSV 어디에도 안 들어가고 `Central` 만 읽는다.

  `run_specs.py` 가 `region["key"] in SIGNAL_REGIONS` 일 때만 `--signal` 을 붙이므로
  지금은 SR 4개 job 에만 그려진다. 손으로 켜려면 `--signal` 을 직접 주면 된다.

  질량점마다 채워진 히스토그램이 다르다 (파일당 Central 히스토그램이 1689 ~ 2161개).
  어느 한 점에 그 플롯의 히스토그램이 없으면 그 점만 건너뛰고 나머지는 그대로
  그린다. `check_inputs.py` 가 SR job 마다 커버리지를 찍는다.
* **샘플 그룹** — `config.SAMPLE_RULES`. 위에서부터 첫 일치가 이긴다. v15 skim
  이름(`DYto2L-4Jets_*`, `TTto2L2Nu*`, `WtoLNu-4Jets_*`)과 v13 이름(`DYMLL*`,
  `WJet*`)을 둘 다 받는다. 규칙에 안 걸리는 파일은 `Others` 로 가되
  `check_inputs.py` 와 job 로그가 경고한다.

  함정 하나: `TTLL_Bin-MLL-*` 는 이름이 v13 의 `TTLL_powheg` 와 비슷하지만
  ttbar 다이렙톤이 아니라 **tt+Z(->ll)** 이다 (skim JSON 의 `PD` 가
  `ttZtoLL_MLL*`). `Others` 로 가야 하고, 그래서 규칙 목록에서 `TT` 보다 위에
  있다. 마찬가지로 `TTLNu-EWK` 는 `ttWtoLNu_EWK` 다. 새 샘플을 넣을 땐
  `Nano15_Analyzers/HNWR/data/Skim/2024/*.json` 의 `PD` 필드로 옛 이름을 확인하면
  그룹이 바로 나온다.
* **플롯 추가/삭제** — `specs/*.txt` 를 직접 고친다. 인자 문법은 v13 `plotter.sh`
  와 같고, `--channel/--outdir/--label1/--label2` 는 `run_specs.py` 가 채운다.
* **OS/SS 분리 플롯** — `specs/chargesplit/` 를 `specs/` 로 옮기고 `make_dag.py`
  를 다시 돌리면 된다 (job 이름이 겹치므로 `--name` 을 따로 줄 것).
