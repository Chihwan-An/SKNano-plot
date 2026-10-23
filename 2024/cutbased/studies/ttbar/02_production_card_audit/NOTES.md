# 02. 기존 cut-based card 체인 조사와 데이터 stream 버그

## 1. 체인 구조 (조사 결과)

```
HNWR analyzer 출력 (RFlav_DYCRCharge/2024)
   └─ linkfarm  BDT/SR/test/cbv15dc/input2024/   (v13 식 이름의 symlink: TTLL_powheg_pNN, ST_tW_top_Lep, EGamma0_C ...)
        └─ cbv15/post_processor_chsplit.py      샘플→그룹 합산, region 별 rebin, overflow fold, SR blinding(Asimov)
             → cbv15dc/shapes_2024_dc.root (2 GB, SR 1-GeV bin + flavor CR), _dc_mm, _dc_cr, _dc_b_* ...
                  └─ scripts/cbv15_dc_cards.py   2차 rebin, data-driven Flip 삽입, card + shapes 작성
                       → BDT/combine/scenarios/test/<tag>/{shapes_2024_<tag>.root, datacards/2024/{EE,MM}/card_WR*_N*.txt}
                            └─ condor/asym_inner.sh, toyfill_inner.sh, fitdiag_*.sh  (Combine)
```
- 시나리오 빌드 명령은 `condor/build_an2_cards.sh` (ref, ssonly, bsplit, bsplit_bdd ...).
- EE / MM card 는 **따로** 만든다 (결합 card 없음). POI 는 `r` 하나, signal process 하나 (`WR<m>N<n><CH>`).
- SR 의 `data_obs` = 네 배경 그룹의 합 (Asimov), card 에는 `observation -1`. CR 은 실데이터.

## 2. Top 모델은 이미 구현돼 있었다

`cbv15_dc_cards.py` 의 rateParam 블록 (수정 시나리오 EE card `card_WR5000_N2500.txt` 75–91행에서 확인):

| rateParam (범위 [0.5,1.5]) | EE card 에서 걸리는 (bin, process) | MM card |
|---|---|---|
| `R_TT_Resolved_2024` | rEESR_OS, rDYEECR_OS, rDYMuMuCR_OS, rDYMuMuCR_SS, **rFlvCR** — 전부 `TT` | rMuMuSR_OS, **rMuMuSR_SS**, rDYEECR_OS, rDYMuMuCR_OS, rDYMuMuCR_SS, rFlvCR |
| `R_TT_Boosted_EE_2024` | bEESR, bDYEECR, **bFlvEMuCR** | bDYEECR, bFlvEMuCR (SR 없음) |
| `R_TT_Boosted_MuMu_2024` | bDYMuMuCR, **bFlvMuECR** (SR 없음) | bMuMuSR, bDYMuMuCR, bFlvMuECR |
| `R_DY_Resolved_2024`, `R_DY_Boosted_2024` | DYJets, SR + DY CR | 〃 |

명세와 비교한 관찰:
- 같은 이름을 여러 줄에 써서 하나의 parameter 를 공유 — 명세 §6.1 과 동일한 방식. constraint 없음 (flat) — 명세와 일치.
- `rEESR_SS` 의 TT 에는 R_TT 가 없다 (data-driven Flip + MC non-flip, `TTNonFlipNorm_2024 lnN 1.3`). 명세 §4.4 의 권고와 일치.
  반면 **MM card 는 `rMuMuSR_SS` 의 TT 에도 R_TT_Resolved 를 건다** — 명세는 OS 에서 잰 β 를 SS 로 자동 전파하지 말라고 함.
- **boosted 짝 맞춤이 AN 과 반대**: production 은 ee SR ↔ `bFlvEMuCR` (= `FlavCR_Boosted_EMJ`, e tight + μ-jet, EGamma stream).
  AN Fig. 98/99 는 μμ ↔ e+μ-jet, ee ↔ μ+e-jet (jet 안 lepton 의 flavor 유지). → `06_open_issues.md` #1.
- 범위 [0.5,1.5] 는 명세 예시 [0,5] 보다 좁다. 수정 전에는 실제로 경계에 붙었다 (03 참조).
- `autoMCStats`: SR 10, CR 0. lnN: `CMS_lumi_2024 1.0161`, `OthersNorm_2024 1.5`, `NonPromptNorm_* 2.0` 등. TT 전용 lnN 은 없음 (rateParam 이 대신).

## 3. TT 그룹에 뭐가 들어가나 (`audit_tt_composition.py`)

`post_processor_chsplit.py` 의 `SAMPLE_MAP` 은 **부분일치 + 첫 일치 우선**이고 `"ST"` 가 `"ST_tch"`, `"ST_sch"` 보다 앞에 있다
(주석: "intentionally precedes ... kept from EE.py"). 그래서 card 의 TT = ttbar(2L) + tW + single-top s/t-channel.
플로터 (`plot/cutbased/config.py`) 는 s/t-channel 을 Nonprompt 로 둔다 — 두 곳의 규칙이 다르다.

```
FlavCR_Resolved_EM_mlljj     ttbar 2L 2889.0 (89.4%)  tW 340.2 (10.5%)  ST s-ch 0.1 (0.0%)  ST t-ch 2.1 (0.1%)
SR_Resolved_EE_mlljj         ttbar 2L 1305.7 (89.8%)  tW 147.3 (10.1%)  ST s-ch 0.0 (0.0%)  ST t-ch 1.5 (0.1%)
SR_Resolved_MM_mlljj         ttbar 2L 1822.3 (89.6%)  tW 209.5 (10.3%)  ST s-ch 0.1 (0.0%)  ST t-ch 0.9 (0.0%)
FlavCR_Boosted_EMJ_mlljj     ttbar 2L  382.9 (86.0%)  tW  61.8 (13.9%)  ST s-ch 0.2 (0.0%)  ST t-ch 0.5 (0.1%)
FlavCR_Boosted_MEJ_mlljj     ttbar 2L  443.3 (86.5%)  tW  66.7 (13.0%)  ST s-ch 0.2 (0.0%)  ST t-ch 2.2 (0.4%)
SR_Boosted_EE_mlljj          ttbar 2L  393.8 (86.1%)  tW  62.8 (13.7%)  ST s-ch 0.0 (0.0%)  ST t-ch 0.9 (0.2%)
SR_Boosted_MM_mlljj          ttbar 2L  430.3 (86.6%)  tW  64.3 (13.0%)  ST s-ch 0.5 (0.1%)  ST t-ch 1.5 (0.3%)
```
s/t-channel 은 ≤0.4% 라 실질 영향은 없다. tW 는 의도대로 TT 에 들어간다 (linkfarm 이름이 `ST_tW_*` 라서).
참고: boosted 히스토그램 이름은 `_mlljj` 지만 값은 `WRCand.M()` = m(lead lepton + fatjet) 이다.

## 4. 버그 1 — `rFlvCR` 데이터가 2배

발견 경위: eμ CR 의 data 를 stream 별로 세어 봤다.
```
rFlvCR (FlavCR_Resolved_EM_mlljj)   EGamma 3559   Muon 3623
```
resolved eμ 는 muon trigger 만 요구하므로 Muon PD 의 3623 이 전체다. EGamma PD 의 3559 는 그중 electron trigger 도
같이 켠 event, 즉 **같은 event 의 중복**이다 (98%). 그런데 `REGION_CONFIG["rFlvCR"]["data"] = ["EGamma","Muon","SingleMuon"]` 이라
card 의 data_obs = 7182. MC 합은 3469 → data/MC 2.07. Muon 만 쓰면 3623/3469 = 1.044.
플로터 config 와 BDT 쪽 `make_cr_template.py` ("Muon data ONLY") 는 이미 Muon 만 쓰고 있었다.

## 5. 버그 2 — 반대 stream 의 데이터 파일이 MC `Others` 로 들어감

발견 경위: production shapes 에서 `bFlvEMuCR` 의 Others 가 458 로 TT(445) 만큼 컸다. 직접 MC 를 합하면 22 뿐.
차이 436 = Muon stream 의 데이터 event 수와 정확히 일치.

`classify_file()` 로직 (수정 전):
```python
if any(pat in fname_base for pat in data_patterns): return "data", "data_obs"
group = "Others"                       # ← region 의 패턴에 없는 데이터 파일도 여기로 떨어진다
for key, grp in SAMPLE_MAP.items(): ...
return "mc", group
```
`bFlvEMuCR` 의 패턴은 `["EGamma"]` 뿐이라 `Muon0_C.root` 같은 파일이 MC/Others 로 분류되고, 그 raw count 가 Others template 에 더해졌다.

CR 전체의 누수량 (`audit_datastream_leak.py`, CR 만 출력):
```
region            data(sel)  leak->Others
bFlvMuECR             648        567
bFlvEMuCR             472        436
bDYEECR              3326        184
bDYMuMuCR            3815        374
bDYEECR_OS / _SS     3107/219    172/12
bDYMuMuCR_OS / _SS   3688/127    352/22
rDYEECR_OS          35120        997
rDYEECR_SS_2e/_lt2    183/991     10/18
rDYMuMuCR_OS        52218       2663
rDYMuMuCR_SS           84          9
rFlvCR               7182          0   (두 stream 을 다 data 로 쓰므로 누수는 없고 대신 2배)
```
boosted SR 에도 같은 누수가 있다 (analyzer 가 boosted SR 은 데이터에도 채운다 — `HNWR.cc:125` 주석 "boosted SR was never guarded").
SR 의 data_obs 는 Asimov (배경 합) 이므로 부풀려진 Others 가 SR 의 Asimov 에도 들어간다. resolved SR 은 데이터가 안 채워져 누수 0.
**주의 (기록)**: 처음 전 region 을 셀 때 boosted SR 의 반대-stream 데이터 개수 (bEESR 49, bMuMuSR 68) 가 화면에 출력됐다.
이후 스크립트는 blind region 을 건너뛰게 고쳤다.

## 6. 수정 내용

`post_processor_chsplit.diff` (33줄):
1. `ALL_DATA_PATTERNS` = 모든 region 의 data 패턴 합집합. `classify_file` 에서 region 패턴에 안 맞지만 이 목록에 걸리는 파일은 `return None, None` (skip).
2. `rFlvCR` 의 data → `["Muon","SingleMuon"]`.

`cbv15_dc_cards.diff` (81줄, 대부분 context): `--shapes-override <file[,file]>` — `read_region()` 과 `raw_bkg()` 가 이 파일들을 **먼저** 찾는다.
기본값 None 이면 기존과 동일하게 동작. (원래는 `--shapes` 를 먼저 보고 없을 때만 `--shapes-mm/-cr/-b` 를 봐서, flavor CR 은 항상 2 GB 파일 것이 쓰였다.)

## 7. 재생성한 것과 안 한 것

```bash
# CR 10개 region 만 (약 30분, /gv0 I/O 가 병목)
/cvmfs/cms.cern.ch/common/cmssw-el9 -B /data6 -B /data9 -B /gv0 -B /tmp -- bash studies/ttbar/03_combine_validation/work_20260919/run_pp_cr_fix.sh
#   → cbv15dc/shapes_2024_dc_cr_fixstream.root
#   regions: rFlvCR bFlvEMuCR bFlvMuECR bDYEECR bDYMuMuCR rDYEECR_OS rDYEECR_SS_2e rDYEECR_SS_lt2 rDYMuMuCR_OS rDYMuMuCR_SS
# 시나리오 (build_an2_cards.sh 의 'ref' 와 같은 인자 + override)
python3 scripts/cbv15_dc_cards.py --shapes cbv15dc/shapes_2024_dc.root --shapes-mm cbv15dc/shapes_2024_dc_mm.root \
  --shapes-cr cbv15dc/shapes_2024_dc_cr.root --ddss cbv15dc/ddss_ee_2024_an2rf_3132.root --edges-json cbv15dc/edges_an2_3132.json \
  --shapes-override cbv15dc/shapes_2024_dc_cr_fixstream.root --tag cbv15_an2_ref_fixstream
```
수정 전후 eμ CR (`audit_scenario_cr_yields.out`):
```
cbv15_an2_ref            rFlvCR data 7182 Others 163.2 data/MC 2.070 | bFlvEMuCR Others 458.0 data/MC 0.497 | bFlvMuECR Others 600.1 data/MC 0.536
cbv15_an2_ref_fixstream  rFlvCR data 3623 Others 163.2 data/MC 1.044 | bFlvEMuCR Others  22.0 data/MC 0.920 | bFlvMuECR Others  33.1 data/MC 1.011
```

**안 한 것**: `shapes_2024_dc.root`, `_dc_mm`, `_dc_b_*` (SR 포함, 1-GeV bin × signal ~120개 × syst) 는 재생성하지 않았다.
따라서 `cbv15_an2_ref_fixstream` 도 boosted SR 의 Others 에는 누수가 남아 있고, `rDYEECR_SS` 는 ddss 파일에서 오므로 영향 없음.
다른 기존 시나리오 (~85개) 는 전부 수정 전 입력이다. 전체를 바로잡으려면 `cbv15dc/run_pp*.sh` 를 전부 다시 돌리고 `build_an2_cards.sh` 를 재실행해야 한다.
