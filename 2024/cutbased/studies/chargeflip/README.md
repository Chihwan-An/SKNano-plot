# Charge-flip studies

2026-09-19: `out/Resolve/DY/chargeflip`의 내용은 이 디렉터리로,
`out/Resolve/DY/chargeflip_corr`의 내용은 [chargeflip_corr/](chargeflip_corr/)로 이동했다.
옛 두 경로에는 기존 producer와 문서의 호환성을 위한 상대 심볼릭 링크만 남겼다.
실제 결과와 새 실행 코드는 이 폴더 안에 있으며, 새 study는 옛 경로를 사용하지 않는다.

| 경로 | 내용 |
|---|---|
| [AN_rawcharge/07_mll_jetbins/](AN_rawcharge/07_mll_jetbins/) | 기존 DY 보정이 포함된 그림, 보존 |
| [AN_rawcharge/08_mll_jetbins_noDY/](AN_rawcharge/08_mll_jetbins_noDY/) | 이번 DY 보정 제거 비교, PNG/PDF와 수치 표 |
| `AN_rawcharge/08_mll_jetbins_noDY/nominal_check/` | 동일 이벤트의 기존 보정 적용 비교 |
| `AN_rawcharge/08_mll_jetbins_noDY/OS/` | OS DY MC만 사용한 보정 제거 비교 |
| `AN_rawcharge/08_mll_jetbins_noDY/zpt_slices/` | 재구성 dilepton pT 구간별 보정 제거 비교 |
| `AN_rawcharge/08_mll_jetbins_noDY/mll_ratio_zpt_overview_{EE,MM}.png` | pT 구간별 1 jet/SR ratio를 한 그림에 비교 |
| [RESULTS.md](RESULTS.md) | 이번 비교의 수치와 해석 |
| [MLL_TO_MLLJJ.md](MLL_TO_MLLJJ.md) | 2 jet OS의 mll만 SS에 맞춘 뒤 mlljj closure 검사 |
| [AN_rawcharge/09_mll_to_mlljj_closure/](AN_rawcharge/09_mll_to_mlljj_closure/) | DY 보정 적용/제거, EE/MM, reco SS 및 truth single-flip SS 검증 |
| [AN_rawcharge/10_1jet_2jet_os_leptons/](AN_rawcharge/10_1jet_2jet_os_leptons/) | 1 jet OS와 >=2 jet OS의 leading/subleading pT, abs eta 및 2D 분포 비교 |
| [JETBIN_LEPTONS.md](JETBIN_LEPTONS.md) | 1 jet / 2 jet OS lepton 분포의 수치 요약과 해석 |
| [AN_rawcharge/11_1jet_2jet_mll_reweighted/](AN_rawcharge/11_1jet_2jet_mll_reweighted/) | 1 jet OS를 2 jet OS에 mll-bin별 재가중한 뒤 lepton pT/eta 재비교 |
| [JETBIN_MLL_REWEIGHT.md](JETBIN_MLL_REWEIGHT.md) | mll matching 전후 결과와 해석 |
| [AN_rawcharge/12_1jet_2jet_zpt_reweighted/](AN_rawcharge/12_1jet_2jet_zpt_reweighted/) | reco Z pT 기반 1jet→2jet 전달계수, mll+Z pT 비교 및 독립 MC 절반 검증 |
| [JETBIN_ZPT_REWEIGHT.md](JETBIN_ZPT_REWEIGHT.md) | recoil 전달계수 결과 요약과 적용 범위 |
| [AN_rawcharge/13_conditional_lepton_angles/](AN_rawcharge/13_conditional_lepton_angles/) | 좁은 mll/Z pT 구간에서 A_pT, Δφ, lepton pT 및 bin 세분화 검사 |
| [CONDITIONAL_LEPTON_ANGLES.md](CONDITIONAL_LEPTON_ANGLES.md) | 조건부 운동량 분배/각도 비교의 해석과 한계 |
| [AN_rawcharge/14_jetbin_z_direction/](AN_rawcharge/14_jetbin_z_direction/) | 정확히 0/1/2jet의 unit-area dilepton eta 및 rapidity, nominal/noDY |
| [JETBIN_Z_DIRECTION.md](JETBIN_Z_DIRECTION.md) | Z 방향 분포 비교의 수치와 0jet 입력/선택 한계 |
| [AN_rawcharge/17_1jet_to_2jet_ss_dycr/](AN_rawcharge/17_1jet_to_2jet_ss_dycr/) | **데이터 사용.** 1 jet OS 데이터 × 전달계수 × flip weight 로 resolved EE DY CR 의 2 jet SS 예측, 기존 방법과 비교 |
| [JETBIN_SS_DYCR_CLOSURE.md](JETBIN_SS_DYCR_CLOSURE.md) | 위 closure 의 수치와 해석 (Z pT 만으로는 η 가 안 맞아 78%, η 를 넣으면 98%) |
| [AN_rawcharge/18_osmc_flip_dycr/](AN_rawcharge/18_osmc_flip_dycr/) | **데이터 사용.** OS MC × 데이터 보정 flip weight 로 resolved EE DY CR 의 SS 예측 (m_lljj 포함), 기존 OS 데이터 방법과 비교 |
| [OSMC_FLIP_DYCR_CLOSURE.md](OSMC_FLIP_DYCR_CLOSURE.md) | 위 closure 의 수치와 해석 (flip 1047.7 vs 기존 1048.4) |
| [AN_rawcharge/19_zpt_zeta_2j_to_1j/](AN_rawcharge/19_zpt_zeta_2j_to_1j/) | **데이터 사용 (1 jet).** DY window 에서 구한 f(Z pT, Z eta) 로 2 jet DY MC 를 1 jet 으로 옮겨 MC / data 와 비교, DY window 와 m_ll>=400 |
| [AN_rawcharge/23_zpt_ratio_vs_mll_normalised/](AN_rawcharge/23_zpt_ratio_vs_mll_normalised/) | MC 만. m_ll bin 별로 1 jet / 2 jet 을 정규화한 뒤 Z pT 비율이 m_ll 과 무관한지 (factorisation), m_lljj>800 유무 비교 |
| [AN_rawcharge/24_mll_zpt_2d_factor_drll/](AN_rawcharge/24_mll_zpt_2d_factor_drll/) | **데이터 사용 (1 jet).** 2D factor f(m_ll, Z pT) 로 2 jet DY MC 를 1 jet 으로 옮김: MC closure, 1 jet data 비교, flip-weight 합 (24b) |
| [AN_rawcharge/25_lowmlljj_mll400/](AN_rawcharge/25_lowmlljj_mll400/), [25_lowmlljj_mll200to400/](AN_rawcharge/25_lowmlljj_mll200to400/) | **데이터 사용 (2 jet, m_lljj<800).** 열린 low-m_lljj validation 영역에서 OS data × w, OS MC × w vs 관측 SS |
| [LOWMLLJJ_FLIP_CLOSURE.md](LOWMLLJJ_FLIP_CLOSURE.md) | 위 결과: OS MC 의 ⟨w⟩ 는 데이터와 같지만 SS 예측이 관측의 55–68% (obs/pred 1.5–1.8) |
| [AN_rawcharge/26_lowmlljj_to_1jet_mll400to800/](AN_rawcharge/26_lowmlljj_to_1jet_mll400to800/), [..._mll200to400/](AN_rawcharge/26_lowmlljj_to_1jet_mll200to400/) | **데이터 사용.** 시험 영역의 2 jet OS MC (및 데이터) × f(m_ll, Z pT) × w vs 1 jet OS 데이터 × w; 결과는 `LOWMLLJJ_FLIP_CLOSURE.md` 의 Study 26 |
| [AN_rawcharge/27_lowmlljj_datamc_mll400/](AN_rawcharge/27_lowmlljj_datamc_mll400/), [..._MM/](AN_rawcharge/27_lowmlljj_datamc_mll400_MM/) | **데이터 사용 (2 jet, m_lljj<800).** SR 과 셀렉션이 같고 m_lljj 만 뒤집은 영역의 OS/SS/Inclusive data/MC stack, EE 와 MM, DY CR 과 같은 13 개 변수 (보정·flip weight 없음); 결과는 `LOWMLLJJ_FLIP_CLOSURE.md` 의 Study 27 |
| [ZPT_ZETA_2J_TO_1J.md](ZPT_ZETA_2J_TO_1J.md) | 위 결과: DY window 는 대체로 성립, 같은 f 를 SR 에 쓰면 5배 어긋남 (m_lljj>800 때문에 f 가 m_ll 에 의존) |
| [scripts/mll_shape_study.py](scripts/mll_shape_study.py) | 새 비교의 독립 실행 코드 (NumPy, PyROOT) |
| `data/mll_jetbins_histograms.npz` | 재실행에 필요한 sumw/sumw2/entry count와 binning |
| `data/mll_jetbins_histograms.json` | 입력 파일 목록, 크기/수정 시각, 가중치 및 선택 정보 |
| [reference/](reference/) | 당시 analyzer와 원본 비교 코드/표의 provenance 사본 |
| [README_legacy.md](README_legacy.md) | 이전 결과 설명, 옛 상대 경로는 역사 기록 |

## 재실행

이 `chargeflip` 폴더 전체를 옮겨도 다음처럼 실행할 수 있다. 현재 작업 디렉터리는 무관하다.
캐시가 있으면 원본 NPZ, 저장소, condor, 기존 plotter 모듈에 의존하지 않는다.

```bash
python3 /path/to/chargeflip/scripts/mll_shape_study.py --zpt-slices
```

원본 이벤트로 히스토그램을 다시 만들 때만 dump 위치를 명시한다.

```bash
python3 /path/to/chargeflip/scripts/mll_shape_study.py \
  --dumps /path/to/dumps_boost --zpt-slices
```

`--cache`와 `--out-dir`로 입력 캐시와 출력 위치를 바꿀 수 있다.
`reference/`의 옛 코드는 실행용이 아니며 당시 절대 경로를 provenance로 보존한다.
기존 01–07 및 nonAN 결과의 전체 event-level 재생산은 원래 BDT/SR/test workflow와 입력이 필요하다.

## 비교 정의

- 입력: cfboost 2024 DY HT-binned 14개 샘플, HT >= 40. 데이터는 읽지 않는다.
- `nominal`: 저장된 `weight`; `noDY`: `weight / w_dy`.
  `w_dy` 안의 C(gen Z pT), EW, R(jet pT)를 모두 제거한다.
  MC normalization, luminosity, pileup, lepton SF는 유지한다.
- 기존 그림과 같은 `hasPair` 및 EE/MM 선택, raw charge, tightCharge 추가 조건 없음.
  기본 그림은 OS+SS이고 `OS/`는 `isSS == 0`이다.
- SR reference: nJet >= 2, passResolved > 0, mlljj > 800 GeV.
  mll 자체의 SR cut은 적용하지 않는다. `2j` 곡선은 mlljj < 800 GeV이다.
  따라서 SR과 1 jet의 차이를 jet multiplicity 하나의 효과로 해석할 수 없다.
- 모든 곡선은 80 <= mll < 100 GeV의 yield를 SR에 맞춘다.
  pT 구간 그림에서는 각 구간 안에서 따로 정규화한다.
  단, pT(ll)<50 GeV에는 Z-peak 이벤트가 없으므로 이 구간만
  60–2000 GeV 전체 면적을 1로 맞춘다 (그림/표에 명시).
  `summary.json`의 `zpt_0to50` 수치도 이 전체 면적 정규화에 해당한다.
- pT 구간: [0,50), [50,100), [100,150), [150,200), [200,300), [300,500), [500,infinity) GeV.
  변수는 `pt_l1l2` (reco pT(ll))이며 generator Z pT가 아니다.
- 아래 ratio와 표의 통계 오차는 sumw2와 Z-peak 정규화의 공분산을 포함한다.
  위쪽 yield 오차는 기존 형식대로 고정된 표시 scale을 곱한 sumw2이다.
  mll >= 2000 GeV는 마지막 bin에 합치지 않는다. systematic은 포함하지 않는다.
- 이 비교는 DY mll template 진단이며 SS charge-flip prediction의 closure 검증은 아니다.
  HT < 40 입력이 없어 특히 0 jet의 완전한 inclusive DY 예측으로 해석하면 안 된다.

코드에서 확인한 적용 범위: C와 EW는 1 jet에도 적용된다. R은 passResolved이면
resolved leading-jet R을, 그렇지 않고 passBoosted이면 boosted fatjet R을 사용한다.
따라서 모든 1 jet 이벤트가 R 없이 가중된 것도 아니다.

## mll만 맞추면 mlljj도 맞는지 검사

```bash
python3 /path/to/chargeflip/scripts/mll_to_mlljj_closure.py
```

`data/mll_to_mlljj_histograms.npz`를 이용하므로 원본 event 경로는 필요 없다.
캐시를 다시 만들 때만 `--dumps /path/to/dumps_boost`를 지정한다.
`--validation-fold 0`으로 학습/검증 절반을 바꿀 수 있고, `--min-train-neff`로
mll bin의 최소 학습 유효 통계를 바꿀 수 있다 (기본 30).
`--channels EE --modes nominal --kinds prompt_singleflip`로 결과를 제한할 수 있다.
변형 결과를 보존하려면 별도의 `--out-dir`을 지정한다.

## 1 jet / 2 jet OS lepton 분포

```bash
python3 /path/to/chargeflip/scripts/jetbin_lepton_shapes.py
```

새 cache 생성 시에만 `--dumps /path/to/dumps_boost`를 지정한다.
`data/jetbin_lepton_histograms.npz` 안에 mll × lepton pT × abs eta의 sumw/sumw2,
event counts와 unclipped lepton 변수의 moments가 있어 원본 경로 없이 재실행할 수 있다.
주 결과는 nominal DY 보정 적용, OS only, charge-flip weight 미적용이다.
`ge2j`는 nJet>=2만 요구하고, `SRtopology`는 passResolved와 mlljj>800도 요구한다.
`highmass/`는 모든 category에 mll>=400을 추가하므로 SR과 비교할 때 먼저 볼 결과다.
EE는 abs eta_SC, MM은 abs eta를 사용하며, 별도 mll shape 재가중은 하지 않았다.

## mll-bin별 정규화 이후 lepton 분포 재비교

```bash
python3 /path/to/chargeflip/scripts/jetbin_lepton_mll_reweight.py
python3 /path/to/chargeflip/scripts/test_jetbin_lepton_mll_reweight.py
```

동일한 local lepton histogram/moment cache를 이용한다. 각 mll bin에서
`w_1j_new = w_nominal * sumw_2j / sumw_1j`를 적용한다.
`ge2j`, `SRtopology` target별 및 EE/MM별로 독립적인 factor를 구한다.
20개 mll 구간: 60,70,80,90,100,110,120,130,150,175,200,250,300,400,
500,700,1000,1300,1600,2000,inf GeV.
구간 내부의 mll 모양까지 맞춘 것은 아니다. Charge-flip weight는 적용하지 않았다.
통계 오차에는 factor 추정과 target 재사용의 상관을 포함하며, 별도 독립 closure 검증은 아니다.

## Z pT 기반 전달계수와 독립 표본 검사

```bash
python3 /path/to/chargeflip/scripts/jetbin_lepton_zpt_reweight.py
python3 /path/to/chargeflip/scripts/test_jetbin_lepton_zpt_reweight.py
```

`data/jetbin_lepton_zpt_histograms.npz`가 있으면 원본 경로 없이 실행한다.
캐시 재생성 시에만 `--dumps /path/to/dumps_boost`를 지정한다.
`--min-train-neff` 기본값은 50이며 낮은 통계의 인접 Z pT bin을 합친다.
`--out-dir`로 다른 binning/통계 설정 결과를 별도로 보존할 수 있다.
Z pT는 reco `pt_l1l2`이고 nominal DY 보정은 유지한다. Charge-flip weight는 적용하지 않는다.
계수는 EE/MM, target, mll 영역별로 구하며 `mll`, `zpt`, `mll_zpt`를 비교한다.
`same_sample/`은 전체 MC의 계수를 같은 MC에 적용한 진단,
`validation/`은 random 절반에서 구한 계수를 다른 절반에 적용한 독립 검사다.
최종 SS 전달계수나 mlljj shape 검증으로 해석하면 안 된다.

## 조건부 lepton 비대칭 / 각도 검사

```bash
python3 /path/to/chargeflip/scripts/jetbin_conditional_angles.py
```

`data/jetbin_conditional_angles.npz`로 독립 실행한다. 원본에서 새 cache를 만들 때만
`--dumps /path/to/dumps_boost`를 지정한다. Study 12와 동일한 random split을 유지한다.
mll>=400 GeV에서 coarse/fine mll-Z pT 전달계수를 비교하고, 400<=mll<600 및
50<=Z pT<250 GeV의 미리 고정한 16개 50x50 GeV 구간도 비교한다.
구간 내부 재가중 역시 mll/Z pT만 사용하며 angular weight는 추가하지 않는다.
모든 histogram은 nominal DY OS MC, charge-flip weight 미적용이다.

## 0/1/2jet의 Z eta 및 rapidity

```bash
python3 /path/to/chargeflip/scripts/jetbin_z_direction.py
python3 /path/to/chargeflip/scripts/test_jetbin_z_direction.py
```

`data/jetbin_z_direction.npz`가 있으면 원본 경로 없이 재실행한다.
새 cache를 만들 때만 `--dumps /path/to/dumps_boost`가 필요하다.
각 category를 면적 1로 정규화하며 정확히 0/1/2jet을 비교한다.
추가적인 SR topology/mlljj 조건, transfer/charge-flip weight는 없다.
eta는 momentum eta로 재구성한 dilepton 방향이며, mass를 포함한 rapidity도 함께 표시한다.
`Zpeak`는 80–100, `Zwindow`는 60–150, `highmass`는 >=400 GeV이다.
`all_zpt` 외에 50–100, 100–150 GeV qT slice도 저장한다.
현재 입력은 HT>=40뿐이고 기존 lepton selection이 있으므로 특히 0jet을 inclusive DY로 해석하지 않는다.

## 시험 영역 (m_lljj < 800) 의 OS/SS data/MC

```bash
./condor/in_container.sh python3 studies/chargeflip/scripts/lowmlljj_datamc_plots.py               # EE
./condor/in_container.sh python3 studies/chargeflip/scripts/lowmlljj_datamc_plots.py --channel 13  # MM
```

`data/lowmlljj_events{,_mm}.npz` 만 읽는다 (cache 는 `scripts/lowmlljj_build.py [--channel 13]`). 선택은 해당 채널의 resolved SR 에서 m_lljj 부등호만 뒤집은 것
(`nJet>=2, passResolved, m_ll >= 400, m_lljj < 800`) 이고, 열린 영역이라 OS·SS 데이터를 모두 그린다.
DY CR 에서 그리던 13 개 변수 (reco Z pT 는 `dilepton_pt`) 를 OS / SS / Inclusive 각각
`AN_rawcharge/27_lowmlljj_datamc_mll400{,_MM}/{OS,SS,Inclusive}/` 에 저장한다.
flip weight 를 적용하지 않은 순수 stack 이므로 SS 의 MC 는 시뮬레이션이 스스로 만든 flip 을 포함한다 —
데이터 기반 flip 예측과의 비교는 study 25 (`--region lowmlljj`) 를 본다.
`--mll-min/--mll-max` 로 SR 밖 구간 (예: 200–400) 을 별도 `--out-dir` 에 낼 수 있다.
