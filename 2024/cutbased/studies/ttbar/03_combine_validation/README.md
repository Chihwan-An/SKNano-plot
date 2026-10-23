# ttbar+tW simultaneous-fit 검증 (2026-09-19)

모델: 각 영역의 TT(=ttbar+tW) MC template 유지, e-mu flavor CR 과 SR 에 공통 `rateParam`
(`R_TT_Resolved_2024`, `R_TT_Boosted_EE_2024`, `R_TT_Boosted_MuMu_2024`) — card writer
`scripts/cbv15_dc_cards.py` 에 이미 구현되어 있던 것. 여기 있는 것은 그 검증 도구와 결과.

환경: `/cvmfs/cms.cern.ch/common/cmssw-el9` 안에서 `/data6/Users/achihwan/combine/CMSSW_14_1_0_pre4`,
Combine `v10.5.1-3-gb937f34f`. cms1 (EL8) 에서는 container 필수. 첫 실행은 cvmfs cold cache 로 수 분 걸린다.

    C="/cvmfs/cms.cern.ch/common/cmssw-el9 -B /data6 -B /data9 -B /gv0 -B /tmp --"
    $C bash run_fixture.sh                                              # synthetic beta injection + mask test
    $C bash run_cronly_fit.sh cbv15_an2_ref_fixstream EE WR5000_N2500   # 실데이터 CR-only fit (SR 전부 mask, r=0)
    $C bash run_blind_limit.sh cbv15_an2_ref_fixstream EE WR5000_N2500  # --run blind expected limit

| 파일 | 역할 |
|---|---|
| `make_fixture.py`, `run_fixture.sh`, `check_fixture.py` | 2-channel fixture (CR obs = beta 1.2 Asimov). 통과 기준: beta 복원, masked SR Top = [48,24,12], SR pseudo-data 를 바꿔도 결과 불변, beta 1->1.1 이 연결된 Top 만 10% scale, mask 변수 2개 / beta 변수 1개 |
| `run_cronly_fit.sh` | 시나리오 card 를 복사해 `--channel-masks` workspace 를 만들고 SR 채널을 전부 mask 한 FitDiagnostics. `cronly_result.json` 에 rateParam 값/경계 여부/상관 |
| `run_blind_limit.sh` | `AsymptoticLimits --run blind` |
| `results_20260919/` | 이번 실행 결과 |

## 같이 고친 production 버그 (2026-09-19)
`cbv15/post_processor_chsplit.py` (백업 `.bak_20260919_datastream`):
1. region 의 data 패턴에 없는 stream 의 **데이터 파일**이 MC `Others` 로 분류되던 것 -> skip.
   (bFlvEMuCR Others 22 -> 458, rDYMuMuCR_OS +2663, boosted SR 에도 누수)
2. `rFlvCR` 가 EGamma+Muon 을 합쳐 data_obs 가 2배 (7182; Muon only = 3623, MC 3469) -> Muon stream only.
`scripts/cbv15_dc_cards.py` (백업 `.bak_20260919`): `--shapes-override` 추가 (기본 없음 = 기존 동작).
수정된 CR shapes: `cbv15dc/shapes_2024_dc_cr_fixstream.root`, 시나리오 `cbv15_an2_ref_fixstream`.
**SR / 나머지 shapes (`shapes_2024_dc*.root`) 는 아직 재생성하지 않았다** — boosted SR 의 Others 에는 누수가 남아 있다.
