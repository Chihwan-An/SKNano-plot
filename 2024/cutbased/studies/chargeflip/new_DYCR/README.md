# new_DYCR — charge-flip 체인을 새 DY 보정으로 다시 돌린 결과 (2026-09-22)

새 DY 보정 = **FxFx/LO, GenJet 수별 (0/1/≥2) shape-only C(gen Z pT) × κ_EW × 그 C 로 다시 유도한 R(jet pT)**
(HNWR userflag `ZptNJet`; 유도 과정은 `../../DY/09_three_generators/SUMMARY.md`).
AN raw-charge 방식 (`../AN_rawcharge/`, `BDT/SR/test/scripts/chargeflip_ptshift.py`) 의 전 과정을 rate 부터 같은 순서로
다시 돌렸다. 기존 결과 (`../AN_rawcharge/`, `BDT/SR/test/data/chargeflip/*.json`, `dumps_boost`) 는 하나도 덮어쓰지 않았다.

## 한 줄 결론

**아무것도 바뀌지 않는다.** flip rate 는 같은 샘플 안의 비라 DY weight 가 상쇄되고 (≤ 0.5%), data SF 는 data 기반이고,
DY CR 의 DY yield 는 R 이 data 에 맞추므로 0.2% 만 움직인다. NLO (FxFx) 로 구한 rate·energy shift 도 LO 와 통계 안에서 같다.

## 입력

| | 경로 |
|---|---|
| 프로덕션 (LO DY 14, 새 보정) | `/gv0/Users/achihwan/SKNanoOutput_dynew/HNWR_ChargeFlip/RFlav_ZptNJet/2024` (batch `cfdynew`) |
| 프로덕션 (FxFx 2, `w_dy = 1`) | `/gv0/Users/achihwan/SKNanoOutput_dynew/HNWR_ChargeFlip/RFlav/2024` (batch `cffxfx`) — `IsDYSample()` 에 안 걸려 C·EW·R 없음 |
| dump | `BDT/SR/test/data/chargeflip/dumps_dynew_dy` (새 DY), `dumps_fxfx` (NLO), `dumps_dynew` = data·non-DY 는 `dumps_boost` symlink + 새 DY symlink (80 개) |
| flip json | `json/ptshift_LO_dynew.json` (count SF, 옛 `_sf3.json` 에 해당), `json/ptshift_LO_dynew_sf3roofit.json` (RooFit SF, 옛 `_sf3roofit.json` 에 해당; `06_.../sf_roofit.json` 의 `roofit_full` 을 옮겨 조립), `json/ptshift_NLO_fxfx.json` |

analyzer 수정 (2026-09-22, 빌드 확인): `HNWR_ChargeFlip` 가 jet별 C 에 필요한 `dy_n_genjet` 을 세팅하지 않고 있었다
(부모의 event loop 를 돌지 않으므로) — 그대로면 모든 DY 이벤트에 0-jet C 가 걸린다. `CountGenJets` 호출을 넣었고,
오프라인 재적용이 가능하도록 `CF_Tree` 에 `gen_zpt`, `n_genjet` 을 추가했다 (dump `COLS` 에도 추가; 옛 프로덕션은 −999).
새 dump 검증: 이벤트 수 동일, `w_dy(new)/w_dy(old)` 평균 1.035 (≥2 jet 1.014).

## 1. flip rate 와 energy-shift χ²: LO vs NLO — `01_rate_chi2_LO_vs_NLO/`

`rate_chi2_LO_vs_NLO.md` (전 bin 표), `rate_LO_vs_NLO.png`, 단계별 그림 `LO_dynew/`, `NLO_fxfx/`.

- **rate P(|η_SC| 6 × pT 7): NLO/LO χ² = 21.7 / 35 bin, pull 평균 +0.06, rms 0.79.** 저-pT bin 의 NLO/LO = 1.02–1.06 (±0.04–0.11).
  FxFx 는 ee 213 만 이벤트 (LO 807 만) + 음수 weight 라 pT > 250 GeV 는 오차 30–100%.
  (음수 weight 샘플의 rate 오차는 `sqrt(Σw²_num)/Σw_den` 으로 계산하도록 `chargeflip_ptshift.py` 를 고쳤다. LO 결과는 영향 없음.)
- 새 DY vs 옛 baseline (둘 다 LO): 모든 bin ≤ 0.5%.
- energy shift f: LO 0.991–1.005, NLO 0.978–1.006 (차이 ≤ 1–2%, 고-pT 는 NLO 통계 부족). χ²_min/ndf 는 LO 1598/100 → NLO 242/100
  이지만 이것은 NLO 의 유효 통계가 1/4 이하라서다. "중심은 같고 폭이 다르다" 는 결론은 그대로.
- MC closure (OS MC × W vs SS MC, 60–120): BB / EE / BE = 0.962 / 1.002 / 0.987 (옛 0.961 / 1.003 / 0.987).

## 2. data SF

| | 새 DY | 옛 |
|---|---|---|
| count: SF2 barrel / endcap | 1.425 ± 0.042 / 1.450 ± 0.027 | 1.426 / 1.451 |
| count: SF3 inner B / outer B / endcap | 1.221 / 1.724 / 1.444 | 1.222 / 1.725 / 1.445 |
| RooFit (`06_roofit_nz_check_cmsflat/`): SF2 | 1.457 ± 0.038 / 1.468 ± 0.024 | 1.458 / 1.468 |
| RooFit: SF3 | 1.245 / 1.722 / 1.469 | 1.253 / 1.721 / 1.469 |
| BE 검증 (SF 적용 obs/pred) | 1.005 (count), 1.023 (RooFit) | 같음 |

## 3. DY CR 검증 (resolved ee, SS 관측 1174) — `17_1jet_to_2jet_ss_dycr/`, `18_osmc_flip_dycr/`

| 예측 | flip (새 / 옛) | obs/pred (새 / 옛) |
|---|---|---|
| OS data × w (분석 기본) | 1048.6 / 1048.4 | 1.071 ± 0.031 / 1.071 |
| OS MC × w | 1049.1 / 1047.7 | 1.071 / 1.072 |
| OS MC × w, OS data 로 정규화 | 1038.3 / 1035.3 | 1.082 / 1.084 |
| MC 자체 flip (SF 없음) | 706.3 / 704.7 | 1.558 / 1.561 |
| 1 jet OS data × t(Z pT, Z η) × w (study 17) | 1038.2 | 1.082 ± 0.032 |

OS DY MC: 33209 (옛 33266, −0.2%); OS data/MC 0.99.

## 4. m_lljj < 800, m_ll ≥ 400 — `25_lowmlljj_mll400/`, `27_lowmlljj_datamc_mll400{,_MM}/`

| | data | MC 합 (새 / 옛) | data/MC (새 / 옛) | DY (새 / 옛) | TT |
|---|---|---|---|---|---|
| ee OS | 1109 | 1402.7 / 1399.7 | 0.791 / 0.792 | 414.4 / 411.4 | 931.9 |
| ee SS | 88 | 43.0 / 42.9 | 2.04 / 2.05 | 10.9 / 10.8 | 20.4 |
| μμ OS | 1568 | 1905.7 / 1887.9 | 0.823 / 0.831 | 546.7 / 529.0 | 1290.8 |
| μμ SS | 28 | 19.2 / 19.1 | 1.46 / 1.47 | 1.3 / 1.2 | 2.6 |

- DY 는 ee +0.7%, μμ +3.4% 늘었을 뿐이고 data/MC 0.79–0.82 는 그대로다. 이 영역은 TT 가 2/3 라서 OS 의 20% 부족은
  DY 보정으로 설명되지 않는다.
- SS flip 예측 (study 25): OS data × w obs/pred 1.821 ± 0.194 (옛 1.823), OS MC × w 1.531 (옛 1.536).

## 5. `plot/cutbased/out/` 의 flip 적용 그림

`scripts/run_out_npz_families.sh` 가 새 dump·새 json 으로 `out/Resolve/DY/EE/<obj>/SS_flip_an3{,count,roofit,roofit_keepTT,roofit_mlljj1600to2800}/`,
`out/Resolve/sig/EE/<obj>/SS_flip_an3/`, `out/Resolve/sig_chargesign/EE/other/{SSpp,SSmm,OSleadP,OSleadM}/` 를 다시 그린다.
옛 tightCharge / sign 방식 폴더 (`SS_flip`, `_tc2`, `_pp`, `_mm`, `_an`) 와 `Resolve/DY/MM/lepton/OS_2d` 는 다시 그리지 않았다
(9/11 에 버린 방식, 생성 명령 기록 없음) — `plot/cutbased/out_shippedDY_2026-09-21/` 에 그대로 있다.

결과 (DY CR SS, 관측 1174):

| 폴더 | 예측 (flip) | obs/pred |
|---|---|---|
| `SS_flip_an3`, `SS_flip_an3count` (count SF) | 1095.8 (1048.6) | 1.071 |
| `SS_flip_an3roofit` (RooFit SF) | 1112.3 (1065.1) | 1.055 |
| `SS_flip_an3roofit_keepTT` | 1106.7 (1045.7) | 1.061 |
| `SS_flip_an3roofit_mlljj1600to2800` (관측 143) | 123.4 (119.9) | 1.159 |
| SR `SS_flip_an3` | 172.3 (94.5) | data blind |

apply 스크립트는 dump 의 모든 열을 읽으므로 뮤온 data 를 뺀 `dumps_dynew_ee` 를 쓴다 (전체 세트로는 16 GB 초과로 hold).
`out/` 장수: 새 828 / 백업 898 — 차이 70 = 옛 방식 `SS_flip*` 52 + `OS_2d` 6 + `*_cardbins` 12 (현재 spec 에 없는 9/12 출력).

## 재실행

```bash
# 프로덕션 (tamsa2)            studies/DY/09_three_generators/scripts/submit_dynew.sh cf | cffxfx
# dump (condor)                condor_submit scripts/dump.sub ; scripts/dump_fxfx.sub
scripts/run_chain.sh linkdumps            # dumps_dynew symlink 세트
scripts/run_chain.sh rate                 # 1 (LO, NLO, 비교)
scripts/run_chain.sh closure              # 3  (condor: scripts/chain.sub)
scripts/run_chain.sh lowmlljj             # 4
scripts/run_out_npz_families.sh           # 5  (condor: scripts/npzfam.sub)
```
스크립트 변경: `chargeflip_ptshift.py` (FxFx alias 를 DY 로 인식, 음수 weight 오차), `chargeflip_tree_dump.py` (COLS +2),
`../scripts/lowmlljj_build.py` (`--dumps` 옵션 추가; 기본값은 그대로).

## 6. m_lljj < 800 을 m_ll 60–400 전체로 — `28_lowmlljj_datamc_mll{60to400,60to150,150to200,200to400}{,_MM}/` (2026-09-22)

캐시 `data/lowmlljj_mll60_events{,_mm}.npz` (`lowmlljj_build.py --mll-min 60`), 그림은 `lowmlljj_datamc_plots.py --mll-min/--mll-max`
(m_ll < 200 용 비닝 추가). 선택 = resolved SR 에서 m_lljj 만 뒤집은 것, DY 는 새 보정. OS data/MC:

| m_ll | ee data | ee MC | ee d/MC | DY 비중 | μμ data | μμ MC | μμ d/MC |
|---|---|---|---|---|---|---|---|
| 60–150 | 151089 | 195019 | **0.775** | 91% | 220547 | 276881 | **0.797** |
| 150–200 | 16490 | 19183 | 0.860 | 29% | 23556 | 26030 | 0.905 |
| 200–400 | 18136 | 21459 | 0.845 | 22% | 26213 | 28963 | 0.905 |
| 60–400 | 185715 | 235661 | 0.788 | 79% | 270316 | 331874 | 0.815 |

- **부족은 m_ll 에 거의 무관하고 (60–400 에서 0.78–0.9 로 평평, Z peak 정중앙이 0.72 로 최저) m_lljj 에 강하게 의존한다:**
  m_lljj 200 GeV 에서 0.6 → 800 GeV 에서 0.95 로 단조 증가 (`*/OS/*_mlljj_fine_plot.png`). leading jet pT 40–100 에서 0.72, 200–300 에서 0.9.
- 세 m_ll 구간을 DY·TT 두 scale 로 풀면 (Others 고정): ee s_DY = 0.76, s_TT = 0.88; μμ s_DY = 0.78, s_TT = 0.95 (구간별 잔차 ≤ 1.5%).
  즉 **DY 가 ~23% 과대, TT 도 5–12% 과대**.
- 해석: resolved DY CR (`HNWR.cc:2075`) 은 m_lljj > 800 을 요구하고 R(jet pT) 은 거기서 유도됐다. R 은 jet pT 40–100 에서 1.9 인데,
  m_lljj < 800 의 soft-jet 이벤트에 그대로 곱하면 DY 가 과대해진다 — R 은 jet pT 만의 함수가 아니라 m_lljj (위상공간) 에 의존하고
  m_lljj > 800 밖으로 외삽되지 않는다 (`dycr-mlljj-zpt-slope` 와 같은 뿌리). SS 의 obs/pred 1.5–1.8 (study 25) 도 OS 예측이
  같은 비율로 과대인 것과 함께 봐야 한다.
- 다음 확인 후보: (a) `weight/w_dy` 로 DY 보정을 뺀 버전, (b) eμ (TT) 로 m_lljj<800 의 TT 정규화, (c) m_lljj bin 별 R.

## 7. charge-flip systematic: BE closure — `07_be_closure_syst/` (2026-09-23)

정의: 순수 BB / EE Z-peak (60–120) 에서 SF_B, SF_E 를 구하고, fit 에 안 쓴 BE 를
pred(BE) = OS data × [SF_B·P_B/(1−P_B) + SF_E·P_E/(1−P_E)] 로 예측한다. BE 의 관측 SS N_Z (Z-peak fit) 와의 차이
|obs/pred − 1| 을 Flip process 의 lnN (`FlipBEClosure_2024`) 으로 쓴다. 입력은 §2 의 `06_roofit_nz_check_cmsflat/sf_roofit.json`,
스크립트는 옛 것 그대로 (`BDT/SR/test/scripts/chargeflip_be_syst.py --json ... --out-json/--out-md 07_.../be_syst_dynew.*`).

| N_Z 방법 | SF_B | SF_E | BE obs | BE obs/pred_SF (새) | 옛 | lnN |
|---|---|---|---|---|---|---|
| count | 1.425 ± 0.042 | 1.450 ± 0.027 | 2623 ± 57 | 1.005 ± 0.022 | 1.005 | 1.005 |
| **roofit_full (채택)** | 1.457 ± 0.038 | 1.468 ± 0.024 | 3071 ± 61 | **1.023 ± 0.021** | 1.023 | **1.023** |
| roofit_win | 1.454 ± 0.038 | 1.465 ± 0.024 | 2910 ± 58 | 1.023 ± 0.021 | 1.023 | 1.023 |

새 DY 보정으로도 **lnN 1.023** (통계 오차를 quadrature 로 더하면 1.031) — 옛 값과 소수 셋째 자리까지 같다.
카드: `cbv15_dc_cards.py --flip-lnn FlipBEClosure_2024=1.023` (rEESR_SS, rDYEECR_SS 의 Flip).
