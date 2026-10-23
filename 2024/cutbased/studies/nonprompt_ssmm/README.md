# resolved SS μμ nonprompt study (MC only) — 폴더 안내

**결과와 결론은 [`MEMO_20260924.md`](MEMO_20260924.md) 를 먼저 읽는다.** 데이터는 읽지 않았다.

## 폴더
| 경로 | 내용 |
|---|---|
| `00_analyzer_patch/` | HNWR.cc/h 원본 백업 (`*.orig`, `HNWR.cc.before_lheguard`), 철회한 presel 패치 (`abandoned_presel/`) |
| `scripts/` | 모든 코드 (아래) |
| `skim/orig/` | 원본 presel ntuple skim (요청 2 재현용) |
| `skim/hnwr_fo/` | HNWR FOMode 출력 skim, 102 MC 샘플 |
| `results/` | 표 (`*.txt`) 와 플랏용 숫자 (`*.json`). `smoke_test/` 는 초기 파이프라인 시험 (쓰지 않음) |
| `fit/<signal>_<config>[_QCD]/` | Asimov card/shapes/info.json/fit_result.json. `_smoke_test` 는 시험 |
| `logs/` | 빌드·condor·분석 로그 |
| `hnwr_fo_mc_samples_2024.txt` | 생산 샘플 목록 (102, 데이터 없음). `_part2` = QCD+signal, `hnwr_fo_signals.txt` |
| 플랏 | `plot/cutbased/out/nonprompt_ssmm/{composition,coverage,fakerate,closure,signal,fit}/` |

## 스크립트
| 파일 | 역할 |
|---|---|
| `skim_trees.py`, `run_skim.sh`, `../skim_orig.sub` | presel ntuple 의 SR_MM / SR_LL_MM → npz (요청 2) |
| `reproduce_orig.py` | 요청 2 재현 + 카드 비교 → `results/02_reproduce.txt` |
| `skim_fo.py`, `run_skim_fo.sh`, `submit_ready_skims.sh`, `../skim_fo.sub` | HNWR FO tree (+SR 히스토그램 적분) → npz. per-job 출력 또는 hadd 파일 |
| `validate_fo.py` | FO iso-TT vs 같은 job SR 히스토그램 vs v3 카드 입력 → `results/01_validate_fo.txt` |
| `folib.py` | 공통: 로더 (W+jets 세트 선택), category/truth/window, `RateMap` (상관 오차, clip 없음), fake-factor / full matrix 가중치 |
| `fo_analysis.py` | `composition`(03) `coverage`(04a) `fakerate`(04b) `closure`(04c) `signal`(05) |
| `make_asimov_cards.py`, `fit_driver.py` | Asimov 동시 fit card (+ fixed-template 비교 card) |
| `run_asimov_fit.sh`, `run_all_fits.sh`, `summarize_fits.py` | tamsa2 에서 combine (MultiDimFit + FitDiagnostics) → `results/06_*` |
| `plot_results.py` | 모든 플랏 (`NP_PLOTS` 로 출력 위치 변경 가능) |

## 재실행
```bash
CB=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased
ST=$CB/studies/nonprompt_ssmm
RUN="env PLOT_EXTRA_BINDS=/tmp:/tmp $CB/condor/in_container.sh"

# 0) 생산 (tamsa2, setup.sh 후). 데이터 없음.
#    python3 python/SKNano.py -a HNWR -i $ST/hnwr_fo_mc_samples_2024.txt -e 2024 -n -2 --nmax 100 \
#            --memory 4096 --userflags FOMode,RFlav --batchname HNWR_FO
#    (run_skim_fo.sh / submit_ready_skims.sh 의 RL1/RL2/RL4 를 새 runlog 로 바꿀 것)
# 1) skim
bash $ST/scripts/submit_ready_skims.sh
# 2) 요청 2 (원본 presel ntuple)
ssh -p 1240 achihwan@210.117.219.6 "cd $ST && condor_submit skim_orig.sub"
$RUN bash -c "cd $ST/scripts && python3 reproduce_orig.py"
# 3) 검증·분석
$RUN bash -c "cd $ST/scripts && python3 validate_fo.py && python3 fo_analysis.py all"
# 4) Asimov fit (card 는 컨테이너, combine 은 tamsa2)
$RUN bash -c "cd $ST/scripts && python3 fit_driver.py && python3 fit_driver.py --qcd --signals MWR4000_N200,MWR4000_N2000"
ssh -p 1240 achihwan@210.117.219.6 "bash $ST/scripts/run_all_fits.sh"
python3 $ST/scripts/summarize_fits.py > $ST/results/06_asimov_fits.txt
python3 $ST/scripts/summarize_fits.py _QCD > $ST/results/06_asimov_fits_QCD.txt
# 5) 플랏
$RUN bash -c "cd $ST/scripts && python3 plot_results.py"
```
