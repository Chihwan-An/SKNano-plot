# HNWR BDT CR data/sim plotter

`/gv0/Users/achihwan/SKNanoOutput/HNWR_BDT_presel`의 nominal CR trees를 사용해
data/simulation 비교 플롯을 그립니다.

기본 실행:

```bash
bash run_all.sh
```

기본값:

- eras: `2022 2022EE 2023 2023BPix`
- channels: `EE`, `MM`
- CRs: `DY`, `FLV`
- resolved variables: `mll`, `mlljj`
- boosted variables: `mll`, `mlfatjet`

예시:

```bash
bash run_all.sh --channel EE --cr DY
bash run_all.sh --eras 2022EE --category boosted
bash run_all.sh --linear --formats png
```

출력:

```text
plots/CR_{DY,FLV}_{resolved,boosted}_{EE,MM}_{mll,mlljj,mlfatjet}.png
plots/*.pdf
plots/*.tsv
```
