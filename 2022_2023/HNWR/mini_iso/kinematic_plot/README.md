# HNWR_miniiso 플로터 (plots/HNWR/mini_iso)

`reproduce/syst_plotter/integrated/charge_inclusive_year_combined` 클론.
입력만 `HNWR_miniiso` 분석기 출력(LSF3>0.75 → 서브리딩 루즈 렙톤 miniIso<0.1 대체판)으로 교체.

- 입력: `/gv0/Users/achihwan/SKNanoOutput/HNWR_miniiso/merged/`
  (2022 + 2022EE + 2023 + 2023BPix 병합; **2024 없음** — HNWR_miniiso는 Run3 22/23만 돌림)
- 원본 대비 변경점 상세: `/data9/Users/achihwan/AN/For_claude/11_LSF_test/HNWR_miniiso_CHANGES.md`

## 0. era 병합 (최초 1회만, 수동)

```bash
source /data6/Users/achihwan/SKNanoAnalyzer-v13/setup.sh   # hadd 필요
bash /gv0/Users/achihwan/SKNanoOutput/HNWR_miniiso/merge_data.sh
```

`HNWR_miniiso/{2022,2022EE,2023,2023BPix}` → `HNWR_miniiso/merged/`. 분석기를 다시 돌린 경우에만 재실행.

## 1. 플롯 (condor, 권장)

```bash
cd /data6/Users/achihwan/SKNanoAnalyzer-v13/plots/HNWR/mini_iso/condor_files
condor_submit_dag plotter.dag
condor_q -dag        # 진행 확인
```

DAG 구조: 6개 플로터 병렬(boost/resolve × DY/FLV/sr) → `organize`(png/tsv 폴더 정리). merge는 포함되지 않음.

재제출 전 정리: `bash clean.sh` (pdf/png/tsv 삭제), `rm -f condor_files/plotter.dag.*` (dagman 잔여물).

## 로컬 실행 (소규모 확인용)

```bash
source /data6/Users/achihwan/SKNanoAnalyzer-v13/setup.sh   # ROOT 필요
bash all.sh          # 6개 플로터 순차 실행, 또는 각 리전 디렉토리에서 bash plotter.sh
```

## 원본과 다른 점

1. **경로**: 모든 절대 경로 `.../charge_inclusive_year_combined` → `.../mini_iso`,
   `DEFAULT_DATA_PATH` → `HNWR_miniiso/merged/` (EE.py/MM.py 12개 전부).
2. **miniIso 플롯 추가** (각 boost plotter.sh 끝 `### Subleading loose lepton miniIso` 섹션):
   - `boost/DY`: `DYCR_Boosted_{EE,MM}[_SS|_OS]_subleadlep_miniiso` (히스토 6개) — 컷 없음 → 전체 분포
   - `boost/sr`: `SR_Boosted_{EE,MM}_subleadlep_miniiso` (2개) — 컷 후 → <0.1만 채워짐
   - `boost/FLV`: `FlavCR_Boosted_{EMJ,MEJ}[_SS|_OS]_subleadlep_miniiso` (6개) — 컷 후
   - 각 히스토그램당 **두 버전** 플롯: x축 0~0.5(`*_to0p5`)와 0~0.1(`*_to0p1`), 둘 다 rebin 2 = **빈 폭 0.01** (원본 200빈/0~1).
   - miniIso 라인에만 `--no-overflow` 사용: xmax 초과분을 마지막 빈에 합산하지 않고 버림
     (boost EE.py/MM.py 6개에 옵션 추가; 기본값 off라 **다른 플롯들은 기존 오버플로우 합산 규약 그대로**).
3. **FLV EMJ/MEJ 버그 수정**: 원본 `boost/FLV/plotter.sh`는 MM.py(MEJ 리전, Muon 데이터) 호출에도
   `FlavCR_Boosted_EMJ_*` 히스토그램을 쓰고 있었음(복붙 버그로 판단). 여기서는 MM.py 라인의 hist를
   전부 `FlavCR_Boosted_MEJ_*`로 수정. **원본 플롯의 MEJ 결과와 비교할 때 주의.**
4. **organize_files.py**: `subleadlep_miniiso` 변수를 `lepton` 폴더로 분류하는 규칙 추가.
5. **era 병합 스크립트**: `/gv0/Users/achihwan/SKNanoOutput/HNWR_miniiso/merge_data.sh` (수동 1회 실행, 동시 hadd 4개 스로틀).
   DAG는 플롯 전용 — merge 노드 없음.
6. **루미 라벨**: 원본의 172.13 fb⁻¹(22+23+24 하드코딩)을 **62.31 fb⁻¹**(22+23, combined_22_23 백업 플로터와 동일)로 수정 (12개 py 전부).

## 참고: 플롯되지 않는 보조 히스토그램

분석기 출력에는 있지만 스택 플롯 대상이 아닌 것 (필요시 수동 확인):
- `SR_{EE,MM}_miniiso_cutflow`, `Flav{EMJ,MEJ}_miniiso_cutflow` (2빈: 렙톤존재/+miniIso 통과 — bin1/bin0 = miniIso 단독 효율)
- `{SF,OF}LooseLepton_infatjet_miniiso_beforecut` (컷 전 전체 분포; lead-e/lead-mu 이벤트가 섞여 있어 단일 채널 데이터 스택에 부적합)
