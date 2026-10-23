# 06. 남은 이슈 / 결정이 필요한 것

우선순위 순. 각 항목에 근거가 있는 문서를 적었다.

## 1. SR shapes 전체 재생성 (필수, 구현)
`post_processor_chsplit.py` 의 stream 버그는 고쳤지만 재생성한 것은 CR 10개뿐이다 (02 §7).
`cbv15dc/shapes_2024_dc.root`, `_dc_mm`, `_dc_b_*` 는 옛 버전 → boosted SR 의 `Others` 에 반대 stream 데이터가 수십 event 섞여 있고,
SR 의 Asimov data_obs 에도 들어간다. `cbv15dc/run_pp*.sh` 전부 + `condor/build_an2_cards.sh` 재실행 필요.
기존 ~85개 시나리오는 모두 수정 전 입력이다. BDT 쪽 (`BDT/combine/scripts/sample_groups.py`, `make_cr_template.py`) 에 같은 패턴의
누수가 있는지는 확인하지 않았다 (make_cr_template 의 rFlvCR 은 Muon only 라고 주석에 명시돼 있음).

## 2. boosted CR ↔ SR 짝 맞춤 (물리 결정)
- production: ee SR ↔ e(tight)+μ-jet (`bFlvEMuCR`), μμ SR ↔ μ(tight)+e-jet (`bFlvMuECR`). tight lepton 과 trigger/stream 을 유지.
- AN2019_083 (Fig. 98–99): μμ ↔ e+μ-jet, ee ↔ μ+e-jet. jet 안 lepton 의 flavor 를 유지 → LSF / in-jet loose lepton 효율이 CR↔SR 에서 상쇄.
- production 방식의 CR 은 같은 flavor signal 로 오염된다 (ee signal 이 e+μ-jet 에 3.5% @ (2000,200), 0.6% @ (3000,200)); AN 방식은 ~0.01% (04 §2).
- 어느 쪽이든 free β + MC transfer 라 통계적으로는 성립한다. 차이는 어떤 효율이 상쇄되고 어떤 systematic 이 남느냐.
- AN Table 20 은 ee-only / μμ-only fit 모두에 두 boosted parameter 를 보여 준다 — 원본 card 의 전체 연결은 AN 요약만으로 복원 불가.

## 3. resolved eμ CR 의 질량 기울기 (물리)
data/MC 가 0.95 (800–1000) → ~1.3 (2 TeV 이상) 으로 오른다 (04 §3). 전체 normalization (1.04) 은 β 가 잡지만 shape 은 못 잡는다.
후보: top pT 모델링 (POWHEG ttbar 는 top pT 가 hard), JES. 확인 순서 제안: top-pT reweight 유무 비교 → JES Up/Down 의 CR shape → 필요하면 TT mass-shape nuisance.
SR 데이터를 보고 보정하면 안 된다.

## 4. JES +3.3σ, 제약 0.46 (모델)
CR-only fit 에서 JES 가 크게 당겨지고 R_DY/R_TT 가 0.85/0.88 로 내려가 보상 (03 §2). `PBDT_PULLS.md` 에도 알려진 over-constraint.
DY jet-pT 보정 R 을 DY CR 에서 유도하고 같은 CR 을 다시 fit 에 넣는 구조와 관련. AK4/AK8 JES 분리, source 별 분해, DY CR 에서의 JES decorrelation 등이 기존 문서의 제안.
β 의 "값" 을 인용할 때는 이 상관을 같이 말해야 한다. 예측 (β × nuisance) 은 CR 에서 data 와 맞는다 (3616 ± 55 vs 3623).

## 5. rateParam 범위 [0.5, 1.5]
명세는 [0,5] 같은 넓은 numerical range 를 권한다. 수정 후에는 경계에서 멀지만 (최소 0.77 ± 0.21 → 1.3σ), boosted 는 오차가 커서 다시 닿을 수 있다.
경계에 닿으면 Hesse 오차가 무의미해진다. 범위를 넓히는 것을 권장.

## 6. MM card 의 `rMuMuSR_SS`
TT 에 R_TT_Resolved 가 걸려 있다 (EE 의 SS 는 아님). μμ SS 의 TT 성분은 prompt OS ttbar 가 아니라 nonprompt/charge 성분일 가능성이 높아,
OS 에서 잰 β 를 전파하는 것이 맞는지 확인 필요. yield 가 작아 영향은 작을 것 (정량화 안 함).

## 7. card 의 TT 에 single-top s/t-channel 포함
`SAMPLE_MAP` 의 "ST" 우선 매칭 때문 (의도적이라고 주석). ≤0.4% 라 영향 없음. 다만 플로터 (Nonprompt) 와 정의가 다르다는 점은 문서화 필요.

## 8. 검증에서 빠진 것
- boosted 에서 ntuple ↔ cut-based 히스토그램의 선택 일치 (resolved eμ 만 확인: 0.08%).
- ntuple `weight` vs `weight_Central` 의 7% 가 어떤 SF 인지.
- ntuple signal 의 정규화, ntuple DY 의 보정 상태.
- low-mass same-flavor 영역을 VR 로 쓸지 CR 로 likelihood 에 넣을지 (둘을 동시에 주장하면 안 됨).
- analyzer 의 low-mass CR 블록 (`HNWR.cc:2235`, 빈 stub) 을 채워 cut-based 출력으로 App. J 를 다시 만드는 것 — JES 등 object syst 까지 포함하려면 필요.

## 9. 명세 대비 완료 조건 체크

| 항목 | 상태 |
|---|---|
| TT/tW sample mapping, 중복 확인 | 완료 (02 §3) |
| nominal/variation template | 기존 체인이 생성 (변경 없음) |
| sumw2/binning/overflow/negative bin | 기존 체인 확인만: overflow fold 있음, negative-bin 보호 없음 (조치 안 함) |
| shared rateParam 연결 | 확인 + 표 (02 §2) |
| era/topology/charge/boosted mapping | 표로 정리, boosted 짝은 미결 (#2) |
| 동일 CR 데이터 중복 없음 | **버그 발견·수정** (02 §4) |
| DY / signal model 보존 | 변경 없음 |
| detector / MC-stat uncertainty | 기존 그대로 (autoMCStats SR 10 / CR 0) |
| CR signal contamination 근거 | 04 §2 |
| synthetic β injection / mask | 통과 (03 §1) |
| 실데이터 CR-only fit | 수렴, 진단 기록 (03 §2) |
| blinded expected-limit smoke test | 통과 (03 §3) |
| SR 데이터 비노출 | resolved 는 analyzer 가 안 채움. boosted 는 조사 중 반대-stream 개수 2개가 출력됨 (02 §5 에 기록) |
| 독립 validation | App. J low-mass closure (04 §4): resolved 통과, boosted 미통과 |
| 재현 가능한 명령/코드 | 각 NOTES + 스크립트 |

---

## 10. 실행 환경 (2026-09-22 추가)

`cmssw-el9` 래퍼가 이 호스트에서 무한 정지한다 (`/cvmfs/cms-ib.cern.ch` fuse 좀비,
`cmssw-env:103` 의 `ls` 가 D state). **`ai-tamsa1` 은 이미 EL9 이므로 래퍼를 빼고 네이티브로 돌린다.**
진단·해결·재개 명령은 [`RUNBOOK_env.md`](RUNBOOK_env.md).

여기서 드러난 사실 하나: §1 의 SR shapes 재생성용 `BDT/SR/test/cbv15/run_pp.sh` 는
2026-09-03 22:20 에 띄운 뒤 **같은 이유로 18일 넘게 한 번도 실행되지 않았다** (pid 3818081, D state).
SR shapes 가 패치 이전 날짜 그대로인 이유가 이것이다. 재실행은 210.117.219.6 의 condor 로 보낸다.

§7 (CR+SR 동시 fit) 은 `03_combine_validation/run_srcr_fit.sh` 로 2026-09-22 착수.
SR 3채널은 `observation -1` (Asimov) 이라 blind 유지. 단 SR shapes 가 아직 패치 이전이므로
**SR 쪽 결과는 §1 완료 전까지 잠정치**.

## 11. SS 채널의 TT rateParam (2026-09-22, 신규)

`R_TT_Resolved_2024` 가 `rDYMuMuCR_SS` 의 TT 에도 걸려 있다. EE SS 영역
(`rEESR_SS`, `rDYEECR_SS`) 은 `--ddss` 의 `DD_REG` 에 들어 있어 의도적으로 제외돼 있는데
MM SS 만 남았다. post-processor 주석대로 **MM SS = nonprompt/WZ** 이므로
(muon charge flip 은 무시 가능) flavour-symmetry 로 교정하는 prompt ttbar 가 아니다.

수치 영향은 그 채널 TT 2 event 뿐이지만, **빼면 fit 의 covQual 이 2 → 3 이 되고
`--saveWithUncertainties` 경고가 사라지며 채널별 사후오차가 복구된다** (03 §4a).
rateParam 중심값은 ≤ 0.002 만 움직인다.

- 조치: `BDT/SR/test/scripts/cbv15_dc_cards.py:289` 의 `R_TT_Resolved_2024` scope 에서
  `rDYMuMuCR_SS` 제외. 재현: `DROP_SS_TT=1 bash 03_combine_validation/run_srcr_fit.sh ...`
- 미결: 같은 논리가 `R_DY_Resolved_2024` 의 `rDYMuMuCR_SS DYJets` 에도 적용되는가 (안 해 봤다).
- 미결: MM 카드 (`rMuMuSR_SS` 포함) 에서도 같은지 — 아직 안 돌렸다.

## 12. rFlvCR 이 charge-inclusive 다 — β 의 4.8% 가 same-sign fake 에서 온다 (2026-09-22, 신규)

`rFlvCR` 은 `FlavCR_Resolved_EM_mlljj` (charge-inclusive) 를 쓴다. 그런데 이 CR 이 정규화하는
SR 은 `rEESR_OS` (opposite-sign) 다. SS 쪽은 `rEESR_SS` 가 데이터 기반 flip 으로 따로 다룬다.
**CR 과 SR 의 charge 선택이 안 맞는다.**

analyzer 는 이미 `FlavCR_Resolved_EM_OS_mlljj` / `_SS_mlljj` 를 둘 다 만든다 (HNWR.cc:3757,3764).

측정 (m>800, `03_combine_validation/results_20260922/flavcr_charge_split.txt`;
charge-incl MC total 3468.9 가 카드 prefit 과 정확히 일치하므로 분류는 검증됨):

| | charge-incl (현재) | OS only | SS only |
|---|---|---|---|
| data | 3623.0 | 3354.0 | 269.0 |
| TT MC | 3231.4 | 3178.1 | 53.3 |
| non-TT MC | 237.5 | 175.6 | 61.9 |
| **data/MC** | **1.044** | **1.000** | **2.335** |
| naive β | **1.048** | **1.000** | 3.883 |

**OS 만 쓰면 data/MC = 1.000 으로 완벽히 맞는다.** 현재의 4.4% 초과분은 전부 same-sign 에서
온다 — 데이터 269 vs MC 115, MC 가 same-sign fake 를 2.3배 과소평가한다.

즉 prompt ttbar 정규화여야 할 β 가 **"MC 가 same-sign fake 를 못 맞춘다"는 사실을 4.8% 만큼
흡수하고 있다.** §11 (`rDYMuMuCR_SS`, TT 16.3 event, β 0.2% 이동) 보다 20배 큰 효과다.

같은 원리 확인: 샘플별 SS 비율 — TTLL_powheg 1.5%, ST_tW 1.2% (prompt dilepton 은 OS),
TTLJ (semileptonic = fake 1개) 51.8%. SS 영역의 "TT" 는 TTLL 샘플 안의 **b-hadron 유래 lepton**,
즉 물리적으로 nonprompt 다 (muon charge flip 은 무시 가능).

### fit 으로 확인함 (같은 날). **naive 계산만큼 β 가 움직이지는 않는다.**

`03_combine_validation/flvcr_os/` 에서 rFlvCR 만 OS 히스토그램으로 재생성 (90초, condor 불필요),
fixstream shapes 에 접합하여 시나리오 `cbv15_an2_ref_flvos` 생성, 카드의 `observation`
3623 → 3354 수정, 같은 조건(`DROP_SS_TT=1`)으로 CR+SR fit:

| | charge-incl rFlvCR | OS-only rFlvCR |
|---|---|---|
| R_TT_Resolved_2024 | 0.9041 ± 0.0314 | **0.8991 ± 0.0242** (−0.6%, 오차 **−23%**) |
| R_DY_Resolved_2024 | 0.8713 ± 0.0172 | 0.8843 ± 0.0162 (+1.5%) |
| R_TT_Boosted_EE_2024 | 0.8333 ± 0.1036 | 0.8365 ± 0.1051 (+0.4%) |
| JES_2024 pull | +3.15 (제약 0.62) | **+2.91 (제약 0.38)** |
| OthersNorm_2024 pull | +1.06 (0.60) | +0.82 (0.55) |
| NonPromptNorm_Resolved_2024 | +0.92 (1.18) | top-15 밖으로 빠짐 |
| covQual | 3 | 3 |

**입력 수준의 naive β 는 1.048 → 1.000 (−4.6%) 인데 fit 의 β 는 −0.6% 밖에 안 움직였다.**
이유: 전체 fit 에서는 JES(+3.15σ) 와 OthersNorm(+1.06σ) 가 이미 same-sign 초과분을 흡수하고
있었다. SS 를 빼자 β 가 아니라 **그 nuisance 들이 풀렸다** (JES 3.15→2.91, Others 1.06→0.82).
2절의 "β 단독이 아니라 β × nuisance 의 곱이 데이터를 맞춘다" 와 같은 구조다.

얻은 것:
- `R_TT_Resolved_2024` 오차 **−23%** (0.0314 → 0.0242). 통계는 7.4% 줄었는데 오차가 줄었다
  = 통계가 아니라 **모델 긴장이 줄어서** 개선된 것.
- CR 의 charge 선택이 SR(`rEESR_OS`) 과 일치하게 됨. 개념적 정합성.
- nonprompt 가 지배하는 영역을 β 측정에서 제거 (`NonPromptNorm_Resolved_2024` pull 소멸).

**해결 안 된 것: JES over-constraint 는 오히려 나빠졌다** — pull 은 3.15→2.91 로 줄었지만
제약이 0.62 → **0.38** 로 더 조여졌다. §4 는 그대로 열려 있다.
rateParam 상관도 조금 올랐다 (R_DY_Res|R_TT_Res 0.308 → 0.418).

- 조치: `post_processor_chsplit.py` 의 `rFlvCR` hist 를 `FlavCR_Resolved_EM_OS_mlljj` 로 교체하고
  카드의 `observation` 을 따라 갱신. (production 파일은 아직 안 건드렸다 —
  사본 `03_combine_validation/flvcr_os/post_processor_flvos.py` 에만 적용.)
### §3 (질량 기울기) 과의 관계 — 확인함. **설명되지 않는다.**

같은 두 shapes 에서 bin 별 data/MC 를 직접 비교했다
(`03_combine_validation/results_20260922/flavcr_mass_slope.txt`):

| | charge-incl | OS-only |
|---|---|---|
| total data/MC | 1.044 | **1.000** |
| 800-1000 GeV | 0.962 | 0.934 |
| 2000-2400 GeV | 1.470 | 1.335 |
| 3200+ GeV | 1.454 | 1.284 |
| 기울기 (pol1) | +0.299 ± 0.055 /TeV | **+0.223 ± 0.054 /TeV** |
| pol0 vs pol1 | ΔChi2 29.5 (**5.4σ**) | ΔChi2 17.0 (**4.1σ**) |

OS-only 는 **normalization 은 완전히 고치지만**(1.044 → 1.000) **기울기는 25% 줄일 뿐이고
남은 4.1σ 는 그대로다.** 즉 §3 은 charge 선택 문제가 아니라 진짜 ttbar 질량-모양 문제다
(top-pT 모델링). TWiki 의 Sam Kaveh / Reyer Band 질문이 정확히 이 지점이고,
Run 2 의 답변("CR 에서 data/MC 가 잘 맞는다")은 2024 에 통하지 않는다.
→ §3 은 그대로 열려 있고, TT mass-shape nuisance 또는 top-pT reweight 가 필요하다.

- 미결: MM 카드.

## 13. MM 카드는 covQual 2 가 남는다 / DY 는 SS 에서 빼면 안 된다 (2026-09-22, 신규)

§11·§12 를 EE·MM 양쪽에 적용해 4가지 조합을 돌린 결과
(`03_combine_validation/results_20260922/srcr_*.json`):

| card | 변형 | covQual | R_TT_Resolved | R_DY_Resolved |
|---|---|---|---|---|
| EE | charge-incl, SS-TT 제거 | 3 | 0.9041 ± 0.0314 | 0.8713 ± 0.0172 |
| EE | **OS-only, SS-TT 제거** | **3** | **0.8991 ± 0.0242** | **0.8843 ± 0.0162** |
| EE | OS-only, SS-TT+DY 제거 | 2 | 0.8995 ± 0.0260 | 0.8847 ± 0.0249 |
| MM | charge-incl, SS-TT 제거 | **2** | 0.8816 ± 0.0351 | 0.8909 ± 0.0230 |
| MM | **OS-only, SS-TT 제거** | **2** | **0.9024 ± 0.0233** | **0.8958 ± 0.0174** |
| MM | OS-only, SS-TT+DY 제거 | 2 | 0.9029 ± 0.0282 | 0.8964 ± 0.0267 |

**(a) DY 도 SS 에서 빼자는 §11 의 제안은 틀렸다.** TT 와 달리 `R_DY_Resolved_2024` 를
`rDYMuMuCR_SS` 에서 빼면 EE 의 covQual 이 3 → 2 로 나빠지고 오차도 커진다
(0.0162 → 0.0249). 기전은 규명 안 했다 — 그 채널(data 84, MC DY 5.1 / TT 16.3 /
Nonprompt 39.9 / Others 14.2)에서 자유 normalization 이 하나도 없어지면서 강직한
제약이 되는 것으로 보이나 확인 안 했다. **권고: TT 만 빼고 DY 는 둔다.**

**(b) OS-only 가 EE/MM 일치를 개선한다.** `R_TT_Resolved_2024` 는 두 카드가 같은 rFlvCR 을
공유하므로 같아야 한다. charge-incl: 0.9041(EE) vs 0.8816(MM) — 0.6σ 어긋남.
OS-only: **0.8991 vs 0.9024** — 일치. MM 오차도 −34% (0.0351 → 0.0233).
§12 를 지지하는 독립 증거다.

**(c) MM 카드는 여전히 covQual 2 다.** EE 는 SS-TT 제거로 3 이 됐는데 MM 은 안 된다.
MM 카드는 SS TT rateParam 이 `rMuMuSR_SS` + `rDYMuMuCR_SS` 두 줄이었고 둘 다 뺐는데도
그렇다. **다른 원인이 남아 있다 — 미조사.**
(MM 카드의 SS SR `rMuMuSR_SS` 는 EE 와 달리 데이터 기반 flip 템플릿이 없고 순수 MC 다.)

## 14. §1 (SR shapes 재생성) — 범위가 boosted 2개로 줄었고, 실행 완료 (2026-09-22)

§1 은 "run_pp*.sh 전부 + build_an2_cards.sh 재실행 (condor 규모)" 로 적혀 있었다. 측정해 보니
**resolved SR 은 재생성이 필요 없다.**

region 별 반대-stream 데이터 개수 (m>800, input2024 직접 적분):

| SR | 올바른 stream | 반대 stream (Others 로 누수) |
|---|---|---|
| bEESR | 898 | **49** |
| bMuMuSR | 674 | **68** |
| rEESR_OS | 0 | **0** |
| rMuMuSR_OS | 0 | **0** |
| rMuMuSR_SS | 0 | **0** |

resolved SR 은 analyzer 가 데이터를 아예 안 채운다 (analyzer 단계 blinding) → 누수 자체가 없다.
**boosted SR 2개만** 재생성하면 된다. `03_combine_validation/sr_fixstream/run_pp_bSR_fixstream.sh`,
네이티브로 **약 5분** (condor 불필요), 출력 414 MB.

결과 — 예측한 49 / 68 과 정확히 일치:

| region | proc | 패치 이전 | 재생성 | 차이 |
|---|---|---|---|---|
| bEESR | Others | 92.1 | **43.1** | −49.0 |
| bEESR | TT / DYJets / Nonprompt | — | 변화 없음 | 0 |
| bEESR | **총배경 = Asimov data_obs** | 807.8 | **758.8** | **−6.1%** |
| bMuMuSR | Others | 101.8 | **33.8** | −68.0 |
| bMuMuSR | **총배경 = Asimov data_obs** | 805.0 | **737.0** | **−8.4%** |

즉 boosted SR 의 Others 는 **절반 이상이 반대 stream 데이터였다** (92.1 중 49). SR data_obs 가
Asimov(배경 합)이므로 가짜 데이터까지 같이 부풀어 있었다. 한계값에 직접 영향한다.

- 남은 일: 이 boosted SR 블록을 시나리오 shapes 에 접합하고 CR+SR fit / blind limit 재실행.
  (§12 의 OS-only rFlvCR 과 함께 넣어야 한다.)
- `build_an2_cards.sh` 84개 시나리오 재생성은 여전히 필요하다면 별개 작업이다.

## 15. 모든 수정을 합친 fit (`cbv15_an2_ref_v2`) + 전 region postfit 플랏 (2026-09-22)

시나리오 `cbv15_an2_ref_v2` = fixstream(§2 CR 수정) + OS-only rFlvCR(§12) + 재생성 boosted SR(§14).
카드는 `DROP_SS_TT=1`(§11) 적용. EE·MM 양쪽 `status 0`.

**함정 하나**: post_processor 의 SR 출력은 **1 GeV 원시 binning(7200 bins)** 이고 카드가 기대하는
것은 `cbv15_dc_cards.py` 가 rebin 한 6 bins 다. 그대로 접합하면 combine 이 7200 bin 을 붙잡고
20분 넘게 수렴하지 않는다. `sr_fixstream/splice_bSR.py` 가 카드 edge 로 `TH1::Rebin` 한 뒤 접합한다
(카드 edge 가 1 GeV edge 의 부분집합이라 정확히 일치; 변경되지 않아야 할 TT/DYJets/Nonprompt 가
bin 단위로 기존 파일과 일치함을 검증 — 불일치 0).

| rateParam | v1 (OS-only rFlvCR) | **v2 EE** | **v2 MM** |
|---|---|---|---|
| R_TT_Resolved_2024 | 0.8991 ± 0.0242 | 0.9017 ± 0.0302 | 0.9037 ± 0.0234 |
| R_TT_Boosted_EE_2024 | 0.8365 ± 0.1051 | 0.8230 ± 0.0924 | 0.8483 ± 0.0792 |
| R_TT_Boosted_MuMu_2024 | 0.7604 ± 0.2363 | 0.7388 ± 0.1728 | 0.8756 ± 0.0926 |
| R_DY_Resolved_2024 | 0.8843 ± 0.0162 | 0.8857 ± 0.0252 | 0.8966 ± 0.0221 |
| R_DY_Boosted_2024 | 0.9231 ± 0.0405 | 0.9269 ± 0.0392 | 0.9394 ± 0.0315 |
| covQual | 3 | **2** | **2** |
| JES_2024 pull | +2.91 (0.38) | +2.91 (0.53) | +2.75 (0.66) |

**주의: v2 EE 의 covQual 이 3 → 2 로 되돌아갔다.** boosted SR 의 Others 가 절반으로 줄면서
(92.1 → 43.1, 6 bin 에 43 event) MC 통계가 얇아진 것이 원인일 가능성이 있으나 확인 안 했다.
§13(c) 의 MM covQual 2 와 같은 미해결 항목이다. **따라서 v2 의 오차도 그대로 인용 불가.**

사후 예측 대 데이터는 전 region 에서 좋다 (CR 최대 1.8% 차이, SR Asimov 는 구성상 일치).

### postfit 플랏 — `03_combine_validation/postfit_plots/{EE,MM}/postfit_<region>.png`

EE 카드 12장 + MM 카드 12장 = 24장 (png + pdf). 각 그림: 사후 stack + 데이터(SR 은 Asimov 로 명시)
+ 사후 불확도 band + prefit total(빨강 점선) + data/postfit ratio pad.
스크립트 `postfit_plots/make_postfit_plots.py` — combine 의 `shapes_fit_b` 는 x축이 bin index 라
시나리오 shapes 파일에서 실제 질량 edge 를 읽어 다시 붙인다. 마지막 bin(overflow)은 폭을 줄여 그린다.

| region | data | postfit | data/postfit |
|---|---|---|---|
| rFlvCR | 3354.0 | 3363.8 | 0.997 |
| bFlvEMuCR | 472.0 | 481.0 | 0.981 |
| bFlvMuECR | 648.0 | 646.1 | 1.003 |
| rDYEECR_OS | 35120.0 | 35277.0 | 0.996 |
| rDYMuMuCR_OS | 52218.0 | 52066.1 | 1.003 |
| bEESR (Asimov) | 758.8 | 745.5 | 1.018 |
| rEESR_OS (Asimov) | 2304.5 | 2288.4 | 1.007 |

## 16. JES 당김의 원인 — 채널 하나씩 빼기 스캔 (2026-09-23)

`03_combine_validation/mask_scan/` — v2 카드(SS-TT 제거)를 `--channel-masks` workspace 로 만들고,
아무것도 안 뺀 fit 1번 + 채널 하나씩 뺀 fit 12번 (EE, MM 각각). 전체 표: `mask_scan/summary.txt`.
(impacts 는 "nuisance 가 POI 를 얼마나 움직이나"를 볼 뿐 "어느 채널이 nuisance 를 당기나"는 모른다.
그 질문에는 이 스캔이 맞는 도구다.)

JES_2024 pull (제약) — 변화가 큰 것만:

| 뺀 채널 | EE | MM |
|---|---|---|
| (없음) | **+2.91 (0.53)** | **+2.75 (0.66)** |
| rFlvCR | **+2.34** (0.63) | **+2.23** (0.62) |
| rDYEECR_OS | +2.41 (0.57) | +2.29 (0.77) |
| rDYMuMuCR_OS | +2.63 (**0.81**) | +2.48 (**0.83**) |
| 나머지 9개 | +2.84 ~ +3.04 | +2.70 ~ +2.97 |

**(a) 범인 하나는 없다.** 어느 채널을 빼도 JES 는 +2.2σ 아래로 안 내려간다. 당김은 **세 채널이
같은 방향으로 미는 집단 효과**다 — eμ flavour CR(`rFlvCR`)과 resolved DY OS CR 두 개.

> **정정 (2026-09-25, `studies/pull_plot/README.md`)**: 아래 (b) 는 Hesse 오차 (covQual 2/3) 비교에서 나온 것으로 likelihood scan 으로는 지지되지 않는다. data 만의 JES 폭은 ±0.95 로 prior 와 비슷하고 둘을 합친 0.69 가 관측된 "제약" 이다. 어느 채널을 빼도 data 는 JES ≈ +5 를 원한다. JES pull 의 원인은 세 resolved CR 공통의 m_lljj data/MC 기울기이며, 기울기 nuisance 를 넣으면 JES +2.91 → +0.84 로 풀린다.

**(b) 과한 제약은 `rDYMuMuCR_OS`(52k event) 에서 온다.** 그 채널을 빼면 JES 제약이
0.53 → 0.81 (EE), 0.66 → 0.83 (MM) 로 풀린다. 다른 채널은 제약을 거의 안 바꾼다.
같은 채널을 빼면 `MuonTrig_2024` pull (+1.37 → +0.31) 과 `ResolvedDYReshapeBin4` (+2.41 → +1.44) 도
같이 풀린다 → 이 셋은 모두 rDYMuMuCR_OS 의 모양을 맞추려고 움직이는 것.

**(c) eμ CR 을 빼면 JES 가 가장 많이 풀린다** (EE 2.91 → 2.34). §3 의 질량 기울기
(data/MC 가 질량에 따라 오름, 4.1σ)와 연결되는 가설: **JES 를 올리면 m_lljj 가 위로 밀려 MC 고질량 꼬리가
커지므로, JES 가 ttbar(와 DY)의 질량-모양 미스모델링을 대신 흡수하는 손잡이 노릇을 하고 있다.**
확인 방법: TT mass-shape nuisance(또는 top-pT reweight)를 넣었을 때 JES 가 풀리는지 본다. 아직 안 했다.

부수: rFlvCR 을 빼면 β 가 0.902 → 0.963 (EE) 로 뛰고 오차가 0.030 → 0.050 — eμ CR 이 β 를 정하는
주 제약임을 재확인. 13개 fit 전부 status 0.

## 17. 시나리오 v3 — EE SS 를 DY-only flip 으로 교체 (2026-09-23)

`postfit_plots_cutstyle/EE/postfit_rEESR_SS_plot.pdf` (v2) 에서 ttbar 가 너무 적게 보였던 이유:
v2 카드의 SS 템플릿이 **현행 ddss (OS 데이터 전체 × flip weight)** 그대로였다
(Flip 95.23 / TT 5.70 — ddss_baseline.root 와 소수점까지 일치). ttbar 의 flip 성분이 전부
"Charge flip" 안에 들어가 있었다.

`BDT/combine/scenarios/test/cbv15_an2_ref_v3` = v2 에서 `rEESR_SS`, `rDYEECR_SS` 의 배경 템플릿을
`07_ss_dyonly_flip/ddss_dyonly_sf.root` 로 교체 (`07_ss_dyonly_flip/build_v3.py`).
- 히스토그램 이름·binning 이 v2 와 정확히 같아 그대로 교체 (edge assert 포함). 신호 템플릿과 DY CR
  실데이터(1174)는 v2 그대로, SR data_obs(Asimov)는 새 배경 합 135.42 로.
- 카드: **EE SS 의 TT 에 `R_TT_Resolved_2024` 를 건다** (`rEESR_SS`, `rDYEECR_SS`) — DY-only 전환 뒤
  이 TT 는 대부분 전자 charge 가 뒤집힌 prompt ttbar 이므로 eμ CR 이 정규화해야 한다.
  **μμ SS 의 TT(`rMuMuSR_SS`, `rDYMuMuCR_SS`)에는 걸지 않는다** (nonprompt, §11).
  그래서 v3 는 `DROP_SS_TT` 없이 카드 그대로 돌린다 (`work_srcr_unc/run_unc_fit_v3.sh`).
- 남겨 둔 것: `TTNonFlipNorm_2024 lnN 1.3` 이 이제 SS TT 전체(flip 포함)에 걸린다 — 보수적.
  flip SF 불확도는 여전히 `Flip` 에만 걸리고 MC 의 flip 성분에는 안 걸린다. 둘 다 추후 정리할 것.

postfit (EE 카드):

| rEESR_SS | v2 (전체 flip) | **v3 (DY-only)** |
|---|---|---|
| Charge flip | 99.3 | **39.8** |
| t̄t+tW | 5.6 | **48.7** |
| DY / Nonprompt / Others | 8.8 / 12.5 / 16.9 | 9.1 / 14.3 / 26.0 |
| 합계 | 143.2 | 137.9 |

rateParam 은 거의 그대로: R_TT_Resolved 0.9017 → 0.8966 (EE), R_DY_Resolved 0.8857 → 0.8829.
JES +2.91 그대로, covQual 2 그대로.

플랏: `03_combine_validation/postfit_plots_cutstyle_v3/{EE,MM}/` (24장). log y 라 맨 위 층(t̄t)이
얇아 보이지만 SR SS 에서 ttbar 는 48.7/137.9 = 35% 로 **가장 큰 단일 성분**이다.
v2 판(`postfit_plots_cutstyle/`)은 전체-flip 이다.
