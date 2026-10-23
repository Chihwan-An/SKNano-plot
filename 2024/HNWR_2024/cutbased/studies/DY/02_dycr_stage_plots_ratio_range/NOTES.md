# 02. DY CR 단계별 플랏 (노트 Fig. 12–18) — ratio pad 0.5–1.5 로 재생성

## 요청 (2026-09-18)
"figure 12 부터 이 계열은 모두 ratio 최대치를 1.5까지 해야 할 것 같은데" — 기존 플랏은 plotter 기본값 `--rmin 0.7 --rmax 1.3` 이라
ZptOnly / NoCorr 단계의 data/MC (1.3–1.8) 가 패널 밖으로 나가 화살표로만 표시됐다.

## 대상 28장 (`plots/`, 노트의 `fig/05_backgrounds/2024/dycr_stages/` 와 동일)

| 시나리오 | ROOT 디렉토리 | DY weight | 재생성한 변수 | 장수 |
|---|---|---|---|---|
| `NoCorr` | `DYCR_NoCorr/` | 1 | dilepton_pt (Resolve/Boost × EE/MM) | 4 |
| `ZptOnly` | `DYCR_ZptOnly/` | C×κ_EW | dilepton_pt, leading/subleading_jet_pt, leading_fatjet_pt, mlljj | 14 |
| `Full` | `DYCR_Full/` | C×κ_EW×R | leading/subleading_jet_pt, leading_fatjet_pt, mlljj | 10 |

세 시나리오는 한 프로덕션의 세 디렉토리이고 히스토그램 이름이 같아서, 부모의 spec 을 그대로 쓰고 `plotter --histdir` 로만 고른다 (`DY/README.md`).
비-DY 배경과 데이터는 세 시나리오에서 동일.

## 방법

사용자의 `specs/` 와 `DY/out/` 을 건드리지 않기 위해 spec 사본을 scratch 에 만들어 ratio 범위만 바꿨다 (`specs/` 에 보관):
```bash
for j in Resolve_DY_EE Resolve_DY_MM Boost_DY_EE Boost_DY_MM; do
  sed -E 's/ --rmin [0-9.]+//; s/ --rmax [0-9.]+//; s/$/ --rmin 0.5 --rmax 1.5/' specs/$j.txt > $S/specs/$j.txt
done
```
(주석 줄에도 옵션이 붙었지만 `read_spec` 이 주석을 무시하므로 무해.)

실행은 9/17 의 로컬 실행 (`DY/logs/local_20260917/`) 과 같은 입력이 되도록 `run_dycr.py --raw-input`:
```bash
export PLOT_EXTRA_BINDS="/tmp:/tmp"
./DY/condor/in_container.sh python DY/run_dycr.py ${job}_${Variant} --raw-input \
    --spec $S/specs/$job.txt --outdir $S/out/$Variant/$region/DY --match "<정규식>"
#   NoCorr : '_dilepton_pt$'
#   ZptOnly: '_(dilepton_pt|leading_jet_pt|subleading_jet_pt|leading_fatjet_pt|mlljj)$'
#   Full   : '_(leading_jet_pt|subleading_jet_pt|leading_fatjet_pt|mlljj)$'
```
12 job (4 region-channel × 3 시나리오) 을 동시에 백그라운드로. 로그 (`logs/`):
- 입력 `/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/DYCRStudy/2024`, 채널당 MC 259 + Data 16 파일 (part 분할 포함; DYJets 157, TT 55, Nonprompt 37, Others 10; signal 228 제외).
  참고: chihwan 의 `SOURCES.md` 는 이 그림들의 프로덕션을 `DYCRStudy_RFlav` 라고 적었지만, 9/17 로그와 이번 로그 모두 실제로 읽은 것은 `DYCRStudy/2024` 다 (`dyconfig.RAW_DIR`). **어느 쪽이 맞는지는 미확인.**
- 소요: job 당 3.8–10.8 분, 플랏당 147–253 s (`/gv0` cold read 가 99%; 12개 동시 실행이라 9/17 의 65–160 s 보다 느림). 파일 여는 데만 처음 ~4분.
- 28/28 생성, 실패 없음. `_plot.png` 를 노트 폴더의 같은 이름 (`<Variant>/<Region>DY<CH>_<var>.png`) 으로 덮어씀.

syst band 는 9/17 과 같은 전체 syst (`config.SYST_LIST`; Full 에는 DYReshape nuisance 포함). 바뀐 것은 ratio 축 범위뿐이다.

## 같은 세션의 다른 재플랏 (DY 는 아니지만 같은 방식)
- 노트 Fig. 6 (SR m(ll)): `--bins` 가변 bin 으로 재생성 (resolved 400…1000/1200/1500/2000, boosted 200 부터). spec 은 `AN-25-020/fig/04_events/cutbased_2024/specs_mll/`.
  x 최대는 못 늘림 — `HNWR.cc:3518,3569` 에서 `FillHist(..., 2000, 0., 2000.)` 로 booking 돼 있어 2 TeV 위는 overflow 뿐. 늘리려면 analyzer 수정 + 재처리.
