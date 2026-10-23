# 09. 세 generator 비교 — 그릴 그림 목록과 경로

> 전체 결과·결론은 `SUMMARY.md` 에 있다. 이 파일은 그림 목록과 경로만 다룬다.

요청 2026-09-21. 세 샘플: **LO** (madgraphMLM HT-binned 14개), **POWHEG** (NLO mass-binned 18개), **FxFx** (aMC@NLO, `DYto2{E,Mu}-2Jets_Bin-MLL-50`).
**전제조건 (전부 공통): `LHE_HT > 40`, gen Z pT > 50.** Z→ee/μμ, gen Z 는 `HNWRDY::FindGenZ`.

그림 위치: `plot/cutbased/studies/DY/09_three_generators/plots/<set>/<변수>/` (2026-09-21 종류별로 정리)

```
plots/
├── ptZ50__LO_POWHEG_FxFx/        세트 1: 세 generator, HT>40, Z pT>50
│   ├── mll/   mll_allJets, mll_GenJ2, mll_overlay_allJets_vs_GenJ2
│   ├── zpt/   zpt_3panel_{allJets,GenJ2}, zpt_overlay_{allJets,GenJ2}
│   └── numbers_2024.json
├── noZptCut__LO_FxFx/            세트 2: POWHEG 없이, Z pT 컷 없이 (HT>40 은 유지)
│   ├── mll/   (같은 이름)
│   ├── zpt/   (같은 이름)
│   └── numbers_2024.json
├── datamc_resolvedDYCR_allvars__test/   그림 2a·2b (1D 히스토그램 전 변수)
│   └── cutbased_format/          같은 내용을 cutbased 플로터 포맷으로
└── datamc_stages/                DY 보정 단계 6개 비교
    ├── stage1_C/                 C 만 (DYCR_COnly), 6 단계를 한 프레임에
    │   └── cutbased_format/      단계별 스택 플랏 (6 단계 × 2 채널 × 5 변수 = 60 장)
    └── stage2_C_x_EW/            C × EW (DYCR_ZptOnly), 같은 구성
        └── cutbased_format/
```
모든 파일은 `_2024.{pdf,png}`. `allJets` = jet 조건 없음, `GenJ2` = GenJet ≥ 2.

| # | 요청한 그림 | 파일 (`<set>/` 아래) | 상태 |
|---|---|---|---|
| 1 | gen m(ll) shape 비교 | `mll/mll_allJets` | ✅ 두 세트 |
| 1′ | 위 + ≥2 GenJet 을 한 플랏에 | `mll/mll_overlay_allJets_vs_GenJ2` | ✅ 두 세트 |
| 3 | gen Z pT shape, m_ll inclusive / 60–150 / >400 (3 패널) | `zpt/zpt_3panel_allJets` | ✅ 두 세트 |
| 3′ | 위 세 구간을 한 플랏에 | `zpt/zpt_overlay_allJets` | ✅ 두 세트 |
| 4a | ≥2 GenJet: gen m(ll) | `mll/mll_GenJ2` | ✅ 두 세트 |
| 4b | ≥2 GenJet: gen Z pT, 세 구간 | `zpt/zpt_3panel_GenJ2`, `zpt/zpt_overlay_GenJ2` | ✅ 두 세트 |
| 2a | reco m(ll) data/MC, resolved DY CR, reco pT(ll) > 50 | `datamc_resolvedDYCR/`, POWHEG 뺀 것 `datamc_resolvedDYCR__LO_FxFx/` | ✅ |
| 2b | reco pT(ll) data/MC, resolved DY CR | 〃 | ✅ |
| 5 | LowJet (AK4<2, AK8==0) data/MC, nJet 0/1, pT(ll)>50 / 컷 없음 | `datamc_lowJet__LO_FxFx/nJet{0,1}_{ptll50,noPtllCut}/` | ✅ |
| 6 | jet별 C, Fig. 10 형식 (theory band) | `C_per_jet/dy_zpt_fxfx_lo_Zpt_genZ_HT40_{Incl,GenJ0,GenJ1,GenJ2}` (+ `_square` = ratio 패널 없는 정사각형 판), `dy_zpt_fxfx_lo_njet` | ✅ |
| 7 | 세 단계 data/MC (C / C×EW / C×EW×R) | `datamc_stages/stage{1_C,2_C_x_EW,3_C_x_EW_x_R}/` + `cutbased_format/` | ✅ |
| 8 | jet pT 축 (data−nonDY) vs 보정된 DY | `datamc_stages/stage2_C_x_EW/jetpt_dataMinusNonDY/` | ✅ |
| — | 절대 normalization 버전 | `ptZ50__LO_POWHEG_FxFx__absNorm/`, `noZptCut__LO_FxFx__absNorm/` | ✅ |

세트 2 실행: `python3 HNWR/scripts/make_dy_gen_compare.py --out <plots> --ptmin 0 --drop POWHEG`
(pT 0 부터 그리려면 5 GeV-from-zero 비닝이 필요 — LO 와 FxFx 는 2026-09-21 15:47/15:49 프로덕션부터 그 비닝. POWHEG 는 옛 비닝이라 세트 2 에 못 들어간다.)

## 정의
- shape = 그 창 안에서 면적 1 로 정규화 (yield 는 스크립트가 따로 출력).
- "2 jet" = hadron-level **GenJet ≥ 2**, pT > 40, |η| < 2.5 (분석의 AK4 컷), hard-process 렙톤과 ΔR > 0.4.
  `LHE_Njets` 는 MLM merging 때문에 generator 간 비교가 안 돼서 쓰지 않는다 (`../06_nlo_lo_mll_njet/NOTES.md`).
  "정확히 2개" 버전도 같이 채운다 (`Zpt_mll_genZ_HT40_GenJ2ex`).
- 4 번은 LO vs FxFx 가 목적. POWHEG 는 2-jet ME 가 없어 참고로만 겹친다.

## cutbased 플로터 포맷 (2026-09-21)

오버레이 그림은 단계마다 total-MC 선 하나씩을 한 프레임에 겹치지만, 분석의 표준 플랏은
DY/TT/Nonprompt/Others 스택 + data + ratio 다. 스택에는 DY 가 하나만 들어가므로 **단계마다 파일이
하나**다: `<Region><CH>_<변수>__DY-<tag>_plot.png`, 첫 라벨 줄에 단계 이름이 들어간다.
data 와 non-DY 는 보정과 무관하므로 `DYCRSplit_NoDYCorr_WeightSystOnly` 에서 한 번만 읽는다.

```
studies/DY/09_three_generators/scripts/run_stages_cutbased_format.sh [stage1_C|stage2_C_x_EW]
```

| tag | 라벨 | 프로덕션 (`$SKNanoOutput_dy3gen/HNWR/`) | 히스토그램 디렉토리 |
|---|---|---|---|
| `LO-nocorr` | LO, no corr. | `DYCRSplit_NoDYCorr_WeightSystOnly` | `Central` |
| `LO-C-powheg` | LO × C shipped (powheg, incl.) | `DYCRStudy_DYCRSplit_ZptOnly_WeightSystOnly` | `DYCR_<단계>/Central` |
| `LO-C-FxFx-incl` | LO × C FxFx incl. | `..._ZptOnly_ZptFxFxIncl_...` | 〃 |
| `LO-C-FxFx-perjet-shape` | LO × C FxFx per-jet (shape) | `..._ZptOnly_ZptNJet_...` | 〃 |
| `LO-C-FxFx-perjet-abs` | LO × C FxFx per-jet (abs) | `..._ZptOnly_ZptNJetAbs_...` | 〃 |
| `FxFx-direct` | FxFx direct | `DYCRSplit_NoDYCorr_WeightSystOnly` (FxFx 파일) | `Central` |

`<단계>` = `stage1_C` → `DYCR_COnly` (C), `stage2_C_x_EW` → `DYCR_ZptOnly` (C × EW). twin 이름은
`HNWR.cc` 의 것이고 (`Full` = C × EW × R), 폴더 이름이 어느 twin 을 읽는지 정한다. 보정이 아예 없는
두 줄 (`LO-nocorr`, `FxFx-direct`) 은 두 폴더에서 같은 그림이다 (`DYCR_NoCorr` 와 `Central` 이 같은 값).
각 그림의 data/MC 는 그 폴더의 `yields_2024.json` 과 일치한다 (같은 프로덕션·히스토그램·비닝).

## 입력과 스크립트
| 그림 | 스크립트 | 입력 히스토그램 (`$SKNANO_OUTPUT/DYGenZpT/2024/<alias>.root`, `Central/`) |
|---|---|---|
| 1, 3 | `HNWR/scripts/make_dy_gen_compare.py` | `Zpt_mll_genZ_HT40` (TH2: gen Z pT × gen m(ll); pT ≥ 50 만 읽음) |
| 4a, 4b | 같은 스크립트 | `Zpt_mll_genZ_HT40_GenJ2` (2026-09-21 아날라이저에 추가, batch `DYGenZpT_GenJ2`) |
| 2a, 2b | 미작성 | reco: `HNWR/DYCRSplit_NoDYCorr_WeightSystOnly/2024` (LO·POWHEG, C=EW=R=1) 의 `DYCR_*_{mass,pt}`; FxFx 는 HNWR 을 돌려야 함 |

실행 (tamsa2, Nano15 env):
```
python3 HNWR/scripts/make_dy_gen_compare.py --out plot/cutbased/studies/DY/09_three_generators/plots [--fxfx <alias,alias>]
```
없는 generator 는 건너뛰므로, FxFx 가 등록되면 같은 명령을 다시 돌리면 세 개가 겹쳐진다.

## 결과 (2026-09-21) — Z pT shape 의 /LO 비

jet 조건 없음, m_ll 60–150:
```
pT        50-60 60-70 70-80 80-90 90-100 100-120 120-150 150-200 200-250 250-350 350-500 500-1000
POWHEG    0.917 0.991 1.032 1.049 1.065  1.112   1.092   1.040   0.979   0.913   0.827   0.716
FxFx      0.934 0.974 0.999 1.018 1.045  1.110   1.127   1.120   1.103   1.073   1.026   0.938   (stat ≤ 1%)
```
≥ 2 GenJet, m_ll 60–150:
```
POWHEG    0.578 0.753 0.907 1.034 1.128  1.207   1.242   1.223   1.168   1.092   0.985   0.846
FxFx      1.002 1.005 1.001 1.004 0.998  1.004   1.008   1.003   0.983   0.955   0.899   0.815   (stat ≤ 1%)
```
m_ll > 400 은 FxFx 통계가 bin 당 3–9% (jet 조건 없음), 5–13% (≥2 GenJet) 라 POWHEG 와 구별이 안 된다 — FxFx 에는 고질량 전용 샘플이 없다.

yield (pT > 50, HT > 40): jet 조건 없음 LO 3.58e7 / POWHEG 3.54e7 / FxFx 3.99e7; ≥2 GenJet LO 4.73e6 / POWHEG 3.55e6 / FxFx 6.11e6.

읽는 법:
- 100 GeV 까지는 두 NLO 가 같다. 그 위에서 POWHEG 는 계속 떨어지고 (>500 에서 0.72) FxFx 는 거의 1 에 머문다 (0.94). 2023 FxFx vs 2024 POWHEG 에서 본 17–23% 차이가 같은 era 에서 그대로 재현됐다.
- 분석이 실제로 쓰는 ≥2 jet 위상공간에서는 **LO 와 FxFx 의 모양이 250 GeV 까지 1% 안으로 같다.** 그 위에서만 FxFx 가 5–18% 낮다. POWHEG 는 여기서 0.58–1.24 로 크게 어긋난다 (2-jet ME 없음).
- ≥2 GenJet yield 는 FxFx 가 LO 보다 29% 많고 POWHEG 는 25% 적다.

### LowJet cutbased_format 을 오버레이와 같은 축으로 (2026-09-22)

`datamc_lowJet__LO_FxFx/nJet1_noPtllCut/cutbased_format/` 의 bin edge 는 원래부터 옆의 오버레이
그림 (`datamc_{mll,ptll}_{EE,MM}_2024`) 과 같았다 (`MLL_WIDE` = `MLL_EDGES_WIDE`, `PTLL` =
`PTLL_EDGES`). 달랐던 건 축뿐이라 `--logx --per-gev` 로 축까지 맞췄다 — 로그 x, `Events / GeV`.
p_T(ll) 은 첫 edge 가 0 이라 ROOT 로그 축에 못 올라가므로 오버레이와 같은 **symlog**
(linthresh 50, linscale 0.4) 로 그리고 눈금은 손으로 찍는다 (`plotter._draw` 의 `args.xticks`).
두 플래그를 안 주면 예전 그림과 바이트 단위로 같다.

```
cd plot/cutbased
B=/gv0/Users/achihwan/SKNanoOutput_dy3gen/HNWR/DYCRSplit_NoDYCorr_WeightSystOnly/2024
./condor/in_container.sh python3 studies/DY/09_three_generators/scripts/draw_datamc_cutbased_format.py \
    --preset lowjet1 --ptll-min 0 --logx --per-gev --nondy-base "$B" \
    --out studies/DY/09_three_generators/plots/datamc_lowJet__LO_FxFx/nJet1_noPtllCut/cutbased_format \
    --dy "LO=$B:LO:Central:LO" --dy "FxFx=$B:FxFx:Central:FxFx"
```

## 남은 단계
전부 완료 (2026-09-21). 미해결 항목은 `SUMMARY.md` §9.

### GenJet = 1 (2026-09-23)
`noZptCut__LO_FxFx/{zpt,mll}/*_GenJ1_*` — `make_dy_gen_compare.py --ptmin 0 --drop POWHEG --jetcats all,GenJ1,GenJ2` (새 `--jetcats` 옵션, 기본값 `all,GenJ2` 는 예전과 같음).
GenJ1 파일만 복사했다 (allJets/GenJ2 수치는 기존 `numbers_2024.json` 과 완전히 같음 확인; json 은 덮어쓰지 않음).
m_ll 60–150 FxFx/LO 모양 비: GenJ1 은 100–200 에서 1.10 의 bump, 500 에서 1.00, 700 위 0.75–0.85. 200–1000 에서 다시 정규화하면
allJets / GenJ1 / GenJ2 가 3–5% 안에서 같다 (500: 0.91 / 0.95 / 0.89, 800–1000: 0.75 / 0.78 / 0.73). 즉 boosted 가 사는 200 GeV 위에서는 jet 수와 무관한 모양.
