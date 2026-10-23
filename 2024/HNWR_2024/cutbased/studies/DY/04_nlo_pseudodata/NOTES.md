# 04. NLO pseudo-data 검증 (AN2019_083 Fig. 31–32 대응) — 2024 에서는 성립하지 않음

## 질문과 요청
SR 은 blinded 라 "Z peak 에서 구한 보정을 m_ll > 400 에 옮겨도 되는가" 를 데이터로 볼 수 없다. 그래서 NLO 시뮬레이션을 가짜 데이터로 쓴다:
1. (Fig. 31) DY CR 에서 NLO/LO 가 (Data − nonDY)/LO 와 비슷한가 → NLO 가 데이터 대역으로 쓸 만한가.
2. (Fig. 32) NLO/LO 가 DY CR 과 SR 에서 같은가 → CR 의 보정을 SR 로 옮겨도 되는가.

요청 (2026-09-18): "전에 WR 에 대해 NLO/LO, DATA/LO 플랏 같이 그린 거랑, y 가 NLO/LO ratio 이고 Ratio DYCR ee+mumu, SR ee+mumu 인 플랏도 있었던 것 같은데, 없으면
`/data9/Users/achihwan/AN/AN-26-120`, `/data9/Users/achihwan/25-020/AN-25-020` 뒤져봐".

## 찾은 것

| 위치 | 내용 |
|---|---|
| `AN-26-120` | tex 에 "NLO/LO k-factor" TODO 한 줄뿐. 그림 없음 |
| `AN-25-020/chihwan/fig/05_backgrounds/backup/corrections/fig31_nlo_lo_data_lo_{resolved,boosted}.*`, `fig32_nlo_lo_cr_sr_{resolved,boosted}.*` | **사용자가 기억한 그림.** 2022–2023, era 4개 + combined 패널. 스크립트 `backup/scripts/make_ch5_appJ_corrections.py` → 사본: `2022_2023_fxfx_reference/`, `scripts/` |
| `chihwan/fig/05_backgrounds/2024/validation/nlo_lo_mlljj_{cr,sr}_{resolved,boosted}_{EE,MM}.*` | 2024, 채널별, 9/17 11:44 생성. 스크립트 `2024/scripts/make_nlo_lo_mlljj_2024.py` → 사본: `2024_powheg_per_channel_old/` |
| 그 외 | `backup/nlo_lo_{EE,MM}_{mlljj,pt,leading_jet_pt}.*`, `corrections/checks/nlo_lo_mlljj/*_2022.*` (이전 시도들) |

## 2024 의 문제

2022–2023 combined (resolved): NLO/LO ≈ 1.21 → 0.9, (Data−nonDY)/LO 와 bin 마다 겹친다. CR 과 SR 의 NLO/LO 도 통계 안에서 같다.

2024 (ee+μμ 합산, `2024_powheg_combined/nlo_lo_mwr_2024_combined.json`):
```
Resolved   edges [800,1000,1200,1400,1600,2000,2400,2800,3200,4000,8000]
  NLO/LO  CR  [0.699 0.616 0.540 0.472 0.386 0.291 0.202 0.140 0.111 0.054]
  Data/LO CR  [1.262 1.239 1.205 1.188 1.175 1.119 1.090 0.928 0.840 0.970]
  NLO/LO  SR  [1.143 1.159 1.160 1.106 1.135 1.078 0.875 0.855 0.809 0.522]
Boosted    edges [800,1000,1200,1600,2000,2800,4000,8000]
  NLO/LO  CR  [0.620 0.500 0.444 0.421 0.244 0.257 0.000]
  Data/LO CR  [0.994 0.944 0.924 0.881 0.762 1.308 1.491]
  NLO/LO  SR  [1.192 1.259 1.223 1.202 1.534 0.870 11.445]     (마지막 bin 은 통계 없음)
```
DY CR 에서 NLO 는 데이터의 절반에서 1/20 → 1번 확인부터 실패, 2번 비교는 의미 없음.

### 원인 추적
1. **입력 누락인가?** — 아니다.
   - `DYCRSplit_NoDYCorr_WeightSystOnly/2024` 에 NLO 18 + LO 14 = 32 root 전부 존재.
   - NLO `MLL50to120` (각 4.8×10⁸ event) 이 30분 만에 끝난 게 의심스러워 runlog 를 확인: `2026_09_17_004651`, `NJobs 300`, `Reduction 1`, 샘플당 300 job → 전량 처리.
   - 히스토그램 직접 확인: `DYto2E_MLL50to120` 의 `Central/DYCR_Resolved_EE_mlljj` integral 1.69×10⁴, **entries 36,680**; `MLL120to200` 508 / 11,591; LO `HT-400to800-MLL-50to120` 1.52×10⁴ / 284,350.
2. **NLO 샘플 종류가 다르다.**
   - 2022–2023: `NLO_FILES = ["bin/DYJets.root", "bin/DYJets10to50.root"]` = aMC@NLO **FxFx** (jet 2개까지 NLO ME).
   - 2024: `is_nlo = ^DYto2(E|Mu)_MLL` = **POWHEG** mass-binned. POWHEG DY 는 ME 에 parton 이 최대 1개, 두 번째 jet 은 parton shower.
   - DY CR 은 m_ll ≈ 90 이라 mlljj > 800 을 넘기려면 아주 센 jet 2개가 필요 → shower 가 못 채움 → NLO/LO 가 질량에 따라 급락.
   - SR 은 m_ll > 400 이 질량의 대부분을 채워 jet 이 덜 세도 됨 → NLO/LO ≈ 1.15 로 멀쩡. **이 CR/SR 차이가 위 해석과 일관된다.**
   - 단, 이것은 generator 특성에서 나온 해석이고 generator 수준에서 따로 검증하지는 않았다.
3. **2024 FxFx 가 있나?** — 없다.
   - `/gv0/DATA/SKNano/{NanoAODv15_RNTuple,VanillaNanoAODv15,CustomNanoAODv15}/2024/` 의 DY: POWHEG `DYto2{E,Mu}_Bin-MLL-*` 와 MadGraph `DYto2L-4Jets_Bin-HT-*-MLL-*` 뿐. `DYto2L-2Jets…amcatnloFXFX` 없음 (W 는 FxFx 가 있음).
   - SKNano `data/Run3_v15_Run2_v15/2024/Sample/CommonSampleInfo.json` (166 샘플) 에도 FxFx DY 항목 없음.
   - 원래 노트 Table 8 에는 `DYto2E/2Mu-2Jets_Bin-MLL-50_…_amcatnloFXFX` 가 적혀 있었다 (CMS 에는 존재하는 샘플) — 사이트에 ntuple 이 없을 뿐.

## 사용자와의 결정 과정
세 선택지를 제시: (a) 2022–2023 그림을 참고용으로, (b) 2024 POWHEG 를 한계 명시하고, (c) 2024 FxFx 프로덕션 후.
→ "c 로 해볼래" → FxFx 입력이 없어 불가 (위 3) + 이 호스트는 condor 없음 → "없으면 냅둬". → "b 도 참고용으로 해봐" → 아래.

나중에 FxFx ntuple 이 생기면: 샘플 목록만 바꿔 같은 프로덕션을 돌리면 된다.
`python/SKNano.py -a HNWR -i <fxfx list> -e 2024 -n <N> --memory 8192 --userflags DYCRSplit,NoDYCorr,WeightSystOnly` (tamsa2), 그다음 스크립트의 `is_nlo` 정규식만 교체.

## (b) 2024 POWHEG 참고용 그림 — 노트 Fig. 21

`scripts/make_nlo_lo_mwr_2024_combined.py` (이번에 작성). 입력은 9/17 스크립트와 같다:
- NLO, LO: `DYCRSplit_NoDYCorr_WeightSystOnly/2024` 의 `Central/{DYCR,SR}_<cat>_<ch>_mlljj` (LO 는 C=EW=R=1).
- CR 의 data / non-DY: `DYCRStudy_RFlav/2024` 의 `DYCR_NoCorr/Central/…` (non-DY 와 data 는 variant 와 무관하게 동일).
- ee+μμ 합산, SR 데이터는 읽지 않음 (SR 은 MC 비율만).
- 형식: **2022–2023 fig31/fig32 의 combined 패널과 같은 모양** (matplotlib; 검정 ○ NLO/LO, 파랑 □ (Data−nonDY)/LO, 빨강 □ SR; y 0–2; log x; 범례 좌하).
  stack 그림이 아니라서 cutbased plotter 형식이 아니다 — 사용자가 기억한 그림과 같은 형식을 택했다.
출력 4장 (`2024_powheg_combined/`): `fig31_nlo_lo_data_lo_{resolved,boosted}_2024`, `fig32_nlo_lo_cr_sr_{resolved,boosted}_2024`.
노트 캡션은 "For reference only" 로 시작하고, 본문 (5.1.3 두 번째 항목) 에 "2024 POWHEG 비교는 validation 으로 쓰지 않으며 FxFx 가 생기면 다시 한다" 고 적었다.

```bash
cd plot/HNWR_2024/cutbased
PLOT_EXTRA_BINDS="/tmp:/tmp" ./condor/in_container.sh python3 studies/DY/04_nlo_pseudodata/scripts/make_nlo_lo_mwr_2024_combined.py --out <DIR>
```
