# 01. 입력과 region 정의

## 1. 두 종류의 입력

| | A. cut-based 히스토그램 | B. BDT preselection ntuple |
|---|---|---|
| 경로 | `/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/RFlav/2024/` (플로터), `.../HNWR/RFlav_DYCRCharge/2024/` (card 체인의 linkfarm `BDT/SR/test/cbv15dc/input2024` 가 가리키는 곳) | `/gv0/Users/achihwan/SKNanoOutput/HNWR_BDT_presel_3SR/2024/` |
| 형식 | `<syst>/<hist>` TH1, 파일 = 샘플(part) | 파일 = 샘플, `ROOT::RNTuple` `<syst>_<region>_BDTTree_<resolved\|boosted>` (event 단위, 833 column) |
| 생산 시기 | 2026-09 (RFlav, DY 보정 C×EW×R, per-flavour R) | 2026-08-23 ~ 09-03 |
| mass cut | **있음**: SR / flavor CR 모두 `m > 800` 만 채움 | **없음** (BDT 입력이라 mll>400, mlljj>800, mlJ>800 을 안 건다) |
| 어디에 썼나 | 02 (card 조사), 03 (Combine fit) — production card 가 이걸로 만들어짐 | 04 (App. J 재현) — low-mass 영역이 여기에만 있음 |

### 왜 B 가 필요했나
App. J 의 절반은 low-mass (m_WR < 800 GeV) 영역이다 (Fig. 97–102 왼쪽, Fig. 103–128, Table 55 아래 줄).
그런데 2024 analyzer 의 low-mass CR 블록은 빈 stub 이다:

```cpp
// HNWR/src/HNWR.cc:2235
// low mass CR
if (DiLepMassGT200 && WRCand.M() < 800.0 ){
}
```

TTto2L2Nu 파일의 `Central/` 에 있는 region prefix 를 전부 세어 봐도
(`SR_Resolved_EE/MM`, `SR_Boosted_EE/MM`, `FlavCR_Resolved_EM`, `FlavCR_Boosted_EMJ/MEJ`, `DYCR_*`) low-mass 는 없다.
analyzer 를 고쳐 재처리하려면 condor (tamsa2) 가 필요해서, mass cut 이 없는 B 에서 영역을 다시 만들었다.

## 2. region 정의 (B 에서 만든 것; `04_.../scripts/make_emu_method_hists_2024.py` 의 `REG`)

| 이름 | ntuple | fit 변수 | high-mass | low-mass | 데이터 stream |
|---|---|---|---|---|---|
| `Res_EE` | `Central_SR_EE_BDTTree_resolved` | `mlljj` | mll>400 && m≥800 | mll>200 && 200≤m<800 | EGamma (low 만) |
| `Res_MM` | `Central_SR_MM_BDTTree_resolved` | `mlljj` | 〃 | 〃 | Muon (low 만) |
| `Res_EM` | `Central_CR_FLV_EM_BDTTree_resolved` | `mlljj` | 〃 | 〃 | Muon |
| `Boost_EE` | `Central_SR_EE_BDTTree_boosted` | `ml1fatjet` | mll>200 && m≥800 | mll>200 && 200≤m<800 | EGamma (low 만) |
| `Boost_MM` | `Central_SR_MM_BDTTree_boosted` | `ml1fatjet` | 〃 | 〃 | Muon (low 만) |
| `Boost_EMJ` | `Central_CR_FLV_EM_BDTTree_boosted` | `ml1fatjet` | 〃 | 〃 | EGamma — e(tight) + μ-jet |
| `Boost_MEJ` | `Central_CR_FLV_ME_BDTTree_boosted` | `ml1fatjet` | 〃 | 〃 | Muon — μ(tight) + e-jet |

- 컷 값의 근거: AN2019_083 §4 와 현재 analyzer (`HNWR.cc:2158-2162` flavor CR: mll>400, mlljj>800; boosted: mll>200, mlJ>800).
  ntuple 의 `mll` 최소값이 정확히 200.0 임을 확인 (presel 에 mll>200 이 이미 걸려 있음).
- 데이터 stream 규칙은 `plot/cutbased/config.py` 와 같다: `Resolve_FLV` = `[("MM","EM")]` (Muon),
  `Boost_FLV` = `[("EE","EMJ"), ("MM","MEJ")]`. resolved eμ 는 analyzer 가 muon trigger 만 요구한다
  (`HNWR.cc:1875-1881`, `this_trigger_pass = pass_trig_muon`).
- **blinding**: same-flavor (`*_EE`, `*_MM`) 의 high-mass 데이터는 스크립트가 아예 읽지 않는다
  (`if isdata and sf and rng == "high": continue`). low-mass same-flavor 는 AN 에서 control region 이므로 읽었다.
  주의: BDT 분석에서는 mass cut 이 없어서 이 low-mass event 들이 BDT SR 의 일부다. cut-based 관점에서만 CR 이다.
- binning: low = [200,300,…,800]; high resolved = [800,1000,1200,1400,1600,2000,2400,2800,3200,8000];
  high boosted = [800,1000,1200,1500,1800,8000] (card 의 ORIG_R / ORIG_B 와 동일). 마지막 bin 에 overflow 를 접었다.
- 그룹 분류는 `config.classify_sample()` 을 그대로 호출 (ntuple 파일 이름이 v13 식 `TTLL_powheg`, `ST_tW_*` 라 config 의 v13 규칙에 걸린다).
  TT = TTLL_powheg + ST_tW_{top,antitop}_{Lep,Semilep}. QCD MC 는 cut-based 배경 모델에 없으므로 제외.

## 3. A 와 B 가 같은 선택인지 확인 (ttbar, resolved eμ, high-mass)

```
B: Central_CR_FLV_EM_BDTTree_resolved, TTLL_powheg, mll>400 && mlljj>800 : entries 144,434
A: RFlav Central/FlavCR_Resolved_EM_mlljj, TTto2L2Nu 전 part 합          : entries 144,556
```
entries 차이 0.08% → 선택은 사실상 같다. (boosted 는 이 비교를 따로 하지 않았다 — 미검증.)

## 4. weight 함정 (시행착오 기록)

처음에 ntuple 의 `weight` 열을 nominal 로 썼더니
- 위 비교에서 sum(weight) = 3102 vs A 의 integral 2889 (**+7%**),
- syst band 가 플랏 전체를 덮을 만큼 컸다.

원인을 syst 별 TT yield 변화로 찍어 보니 (`Res_EM/high`, 첫 버전 히스토그램 `hists/emu_method_hists_2024_wrongnominal.root`):

```
ElectronID_Up -6.15%  ElectronID_Down -7.30%  MuonTrig_Up -6.72%  MuonTrig_Down -6.72%  Pileup_Up -6.73% ...
JES_Up -100%  JER_Up -100%  ElectronScale_Up -100%  MuonRes_Up -100% ...
```
- 모든 weight variation 이 `weight` 대비 약 -6.7% → **올바른 nominal 은 `weight_Central`** 이고 `weight` 는 그보다 7% 크다.
  0.933 × 3102 ≈ 2894 ≈ A 의 2889 로 맞아떨어진다. (`weight` 와 `weight_Central` 의 차이가 어떤 SF 인지는 확인하지 않았다.)
- JES/JER/lepton Scale·Res 의 `weight_*` 열은 Central tree 에서 0 이다. 이 variation 은 별도 tree
  (`JES_Up_SR_EE_BDTTree_*` 등) 에만 있고 **SR 에만** 존재한다 (flavor CR 에는 object-variation tree 가 없다).
  → App. J 재현의 syst band 는 weight 형 (ElectronID/Reco/Trig, MuonID/Iso/Reco/Trig, Pileup, LSF) 만 포함한다.

수정 후 (`weight_Central`) 가 최종본이다. 04 의 모든 숫자·그림은 수정 후 것이다.

## 5. 재현 명령

```bash
cd /data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased
S=studies/ttbar/04_emu_method_appendixJ
PLOT_EXTRA_BINDS="/tmp:/tmp" ./condor/in_container.sh python3 $S/scripts/make_emu_method_hists_2024.py --out <DIR>   # 152 파일, 첫 실행 ~25분 (I/O), 캐시되면 ~5분
PLOT_EXTRA_BINDS="/tmp:/tmp" ./condor/in_container.sh python3 $S/scripts/make_emu_method_plots_2024.py --inp <DIR> --out <DIR>/plots
```
