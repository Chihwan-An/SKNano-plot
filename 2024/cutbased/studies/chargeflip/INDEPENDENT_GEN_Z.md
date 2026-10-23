# HT 및 분석 선택과 독립적인 NLO gen Z 방향

## 무엇을 새로 확인했나

Study 15 역시 HT cut은 없었지만 기존 HNWR_ChargeFlip의 reconstructed lepton
pT>60/53 GeV, ID, trigger, acceptance와 SF가 남아 있었다.
이번 study 16은 **raw NanoAOD의 GenPart와 GenJet을 직접 읽어** 그 선택들까지 제거했다.
Study 15의 manifest는 동일한 raw 파일 목록과 처리 event 수를 찾는 데만 사용했다.
선택된 CF event tree, weight, histogram은 사용하지 않았다.

- 2024 POWHEG+PYTHIA8 DYto2E / DYto2Mu, generator mass bins 10 GeV부터 infinity까지.
- 20개 샘플, 총 7,600,000 raw events의 부분 표본. Z peak sample은 채널별 2M,
  나머지 mass samples는 각각 200k events이다. 전체 생산 통계가 아니다.
- **HT cut 없음**, HLT 요구 없음, lepton pT/eta/ID 요구 없음, reco/SR 선택 없음.
  `LHE_HT`는 cut에 쓰지 않고 저-HT 이벤트가 남았는지 audit할 때만 읽는다.
- Z는 hard-process last-copy GenPart Z. 실제 표본 7.6M개 모두 pdgId=23, status=62
  Z가 유일하게 존재했다. 누락/모호한 Z는 0개였다. 이는 reco dilepton이 아닌 pre-FSR gen boson이다.
  코드상 Z가 없는 경우만 unique isHardProcess OSSF e/mu pair fallback을 허용한다.
- Jet은 GenJet pT>40 GeV, |eta|<2.5. Prompt status-1 gen e/mu에서 dR<0.4인 jet은 제거한다.
  Cleaning lepton에는 pT/eta cut을 주지 않는다. 정확히 0/1/2 jets를 각각 비교한다.
  |eta_jet|<5 버전도 별도 작성했다. 0jet은 정해진 jet 기준을 통과한 jet이 없다는 뜻이다.
- Full signed `genWeight*xsec/processed_sumw`만 적용한다. PU, lepton SF, DY 보정,
  charge-flip, transfer weight는 전혀 없다. Jet category별 면적을 1로 정규화한다.
- Mass window는 gen Z mass이다. 기존 reco mll 선택과 직접 동일하지 않다.

## 주요 결과

평균 |eta_Z|, MC statistical uncertainty:

| channel / gen mass | 0jet | 1jet | 2jet |
|---|---:|---:|---:|
| EE, 80–100 GeV | 3.8946 ± 0.0014 | 1.9774 ± 0.0034 | 1.8320 ± 0.0105 |
| MM, 80–100 GeV | 3.8957 ± 0.0014 | 1.9767 ± 0.0034 | 1.8214 ± 0.0104 |
| EE, >=400 GeV | 4.2946 ± 0.0039 | 2.6534 ± 0.0055 | 2.1723 ± 0.0100 |
| MM, >=400 GeV | 4.2950 ± 0.0039 | 2.6513 ± 0.0056 | 2.1672 ± 0.0103 |

이 jet 정의에서는 0jet의 eta가 가장 넓고, 2jet이 1jet보다 중앙에 가깝다.
EE/MM가 비슷해진 점도 detector/lepton selection 없는 비교와 부합한다.
|eta_jet|<5로 넓혀도 unrestricted-Z-pT 분포의 평균 |eta_Z| 순서는 같다.

EE Z peak에서 평균 |y_Z|는 0/1/2jet 순서로 1.8437 / 1.4355 / 1.4157,
평균 Z pT는 14.68 / 66.65 / 98.53 GeV이다.
큰 eta 차이가 곧 같은 크기의 longitudinal-boost 차이라는 뜻은 아니다.
`eta = asinh(sqrt(m^2+qT^2)/qT * sinh(y))`이므로 낮은 qT 자체가 |eta|를 키운다.
0jet의 eta 분포는 평탄하지 않다.

Z pT를 100–150 GeV로 제한한 EE Z peak의 평균 |eta_Z|는
1jet 1.5306 ± 0.0087, 2jet 1.5107 ± 0.0163으로 차이가 약 1.1 sigma다.
고질량에서도 2.2569 ± 0.0099 대 2.2489 ± 0.0176으로 가까워진다.
이는 조건부 진단이며 qT 구간 내부 분포나 mass/angles를 정확히 맞춘 인과 검사는 아니다.

## HT가 제거되지 않았다는 검증

- Raw 7,600,000 events 중 5,824,305 events가 LHE_HT<40이었다. 모두 캐시에 유지했다.
- EE Z peak 0jet의 weighted HT<40 fraction은 **96.5724 ± 0.0145%**이다.
- 같은 1jet/2jet에도 HT<40 contribution이 각각 12.3946% / 6.2271% 있다.
  LHE_HT는 shower 후 GenJet scalar sum과 같은 변수가 아니다.
- 모든 표본의 Z reconstruction 성공. 모든 주요 category에서 undefined eta event=0.
- Synthetic tests 5개 통과: lepton 없는 Z, jet threshold/acceptance, soft prompt-lepton
  cleaning, hard-pair fallback, ambiguous boson, qT=0 처리를 포함한다.
- Histogram sumw/sumw2 보존을 검사했다. |eta|>10, |y|>6은 표시상 edge bin으로
  fold하며 평균값은 자르지 않는다. Systematic uncertainty는 포함하지 않는다.

## 파일

- [EE Z peak](AN_rawcharge/16_independent_gen_z/njet25/Zpeak/all_pt/z_direction_EE.png)
- [MM Z peak](AN_rawcharge/16_independent_gen_z/njet25/Zpeak/all_pt/z_direction_MM.png)
- [EE highmass](AN_rawcharge/16_independent_gen_z/njet25/highmass/all_pt/z_direction_EE.png)
- [EE Z peak, jet eta<5](AN_rawcharge/16_independent_gen_z/njet50/Zpeak/all_pt/z_direction_EE.png)
- [전체 수치](AN_rawcharge/16_independent_gen_z/RESULTS.md)
- [입력 및 정의 provenance](AN_rawcharge/16_independent_gen_z/provenance.json)

`scripts/independent_gen_z_events.py`와 `scripts/independent_gen_z.hxx`가 raw 입력을 추출한다.
ROOT가 있는 환경에서 `python scripts/independent_gen_z_plot.py`로 재그릴 수 있다.
NPZ cache만 있으면 raw 입력이나 기존 analyzer, correction 파일은 필요하지 않다.
`--dumps`, `--out-dir`, `--manifests`, `--manifest`로 경로를 바꿀 수 있다.

NLO generator sample의 jet-bin 비교이지, 각각의 jet bin이 모두 NLO accuracy라는 주장은 아니다.
Study 15와는 Z/jet의 gen-vs-reco 정의도 바뀌었으므로 두 결과 차이 전체를
하나의 cut 효과로 해석하면 안 된다.
