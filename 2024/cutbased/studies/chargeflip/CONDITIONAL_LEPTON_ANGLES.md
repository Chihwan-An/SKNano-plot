# Subleading pT residual: binning 및 조건부 각도 검사

## 검사 내용

DY OS MC, nominal DY 보정, mll>=400 GeV. Charge-flip/각도 보정은 적용하지 않았다.
Study 12와 동일한 random MC split으로 fold 0에서 mll-Z pT 전달계수를 구하고 fold 1에서 검사한다.
1jet은 정확히 nJet==1, ge2j는 nJet>=2,
SRtopology는 nJet>=2, passResolved, mlljj>800 GeV이다.

- A_pT=(pT1-pT2)/(pT1+pT2), abs(delta phi_ll), leading/subleading pT를 비교했다.
- Coarse는 study 12의 mll+Z pT 결과를 그대로 재현한다.
- Fine은 mll 400–700에서 25 GeV, 700–1000에서 50 GeV, >=1000 통합 bin이다.
  Z pT는 기존 경계를 유지하면서 200 아래 10 GeV, 200–500에서 25 GeV 경계를 추가했다.
  양쪽 학습 MC 유효 통계가 50 이상이 되도록 인접 Z pT bin을 합치므로 모든 최종 구간이 좁은 것은 아니다.
- 별도로 mll 400–600, Z pT 50–250에서 사전 고정한 16개 50x50 GeV 구간을 확인했다.
  각 구간 내부에서도 위 fine grid를 사용하되 최소 학습 Neff=20으로 합쳐 mll/Z pT를 재가중했다.
  angular/개별 lepton pT 변수를 weight 결정에 사용하지 않았다.
- 그림의 ratio는 raw source/target bin Neff>=20일 때만 표시한다. 전체 bin은 평균/shape/TV 계산에 포함한다.

## 결과: EE, SRtopology, 독립 검증 표본

| 평균 | Coarse matching | Fine matching | 2jet target |
|---|---:|---:|---:|
| Leading pT [GeV] | 335.50 ± 1.61 | 337.88 ± 1.63 | 337.95 ± 1.48 |
| Subleading pT [GeV] | 219.48 ± 1.37 | 221.73 ± 1.40 | 220.60 ± 1.35 |
| A_pT | 0.2170 ± 0.0019 | 0.2164 ± 0.0019 | 0.2182 ± 0.0023 |
| abs(delta phi) [rad] | 2.5775 ± 0.0062 | 2.5805 ± 0.0063 | 2.5538 ± 0.0060 |

pT shape TV (0이면 동일): leading 0.0204 -> 0.0104, subleading 0.0244 -> 0.0202.
Subleading은 평균부터 이미 큰 불일치가 아니며, 세분화 후에도 약간의 bin별 residual은 남는다.
두 matching 결과는 같은 학습/검증 이벤트를 사용하므로 서로 독립적인 오차로 차이의 유의도를 계산하면 안 된다.

A_pT 평균은 target과 가까워 **EE에서 subleading만 특별히 잘못 분배된다는 뚜렷한 근거는 찾지 못했다.**
반면 delta phi 평균 차이는 fine matching 후에도 0.0267±0.0087 rad (통계 오차)가 남는다.
이것만으로 polarization 등의 원인을 특정할 수는 없다. 같은 fine 검증에서 평균 Z pT는
191.37±1.72 vs target 195.59±1.29 GeV로 완전히 일치하지 않으며,
통계상 합쳐진 bin과 >=1000 GeV mll 통합 bin도 남아 있다.

MM SR에서는 fine matching 평균 subleading 217.61±1.14 vs target 218.69±0.96 GeV이다.
A_pT는 0.2235±0.0017 vs 0.2173±0.0014로 EE보다 차이가 남는다.
따라서 EE 한 channel의 평균 일치만으로 모든 lepton angular structure가 일치한다고 일반화하지 않는다.

## 좁은 구간에서의 확인

EE SR, 400<=mll<450 및 50<=Z pT<100 GeV 구간의 예:

| 내부 fine matching 후, 1jet - target | 차이 ± 통계 오차 |
|---|---:|
| A_pT 평균 | +0.0014 ± 0.0056 |
| delta phi 평균 [rad] | -0.0012 ± 0.0124 |
| subleading pT 평균 [GeV] | -1.53 ± 2.40 |
| mll 평균 [GeV] | +1.21 ± 1.25 |
| Z pT 평균 [GeV] | +0.42 ± 1.35 |

이 구간은 같은 50 GeV Z pT bin으로 자르기만 했을 때 Z pT 평균이 3.23 GeV 달랐지만,
내부 matching 후에는 그 차이가 줄고 각도/분배 차이도 작다.
다른 구간 모두가 완벽히 일치하는 것은 아니다. 예를 들어 mll 450–500, Z pT 150–200에서는
delta phi 차이 +0.0772±0.0399 rad가 남는다. 16개 구간의 결과를 모두 저장했으며,
이 여러 비교 중 한두 개의 편차를 전체 유의도로 해석하지 않는다.

결론: 넓은 mll/Z pT bin 내부 차이가 residual의 일부임은 확인했지만,
모든 residual을 binning으로 설명했다고 주장할 수는 없다. 현재 결과는
subleading 전용 보정보다 남은 recoil/각도/acceptance 상관을 점검할 근거이며,
charge-flip나 mlljj closure 검증을 대신하지 않는다.

## 파일

- [EE SR: coarse/fine 및 각도 전체 비교](AN_rawcharge/13_conditional_lepton_angles/SRtopology/binning_comparison_EE.png)
- [EE SR: mll 400–450, Z pT 50–100 조건부 비교](AN_rawcharge/13_conditional_lepton_angles/SRtopology/EE_mll400_450_zpt50_100.png)
- [EE SR: mll 450–500, Z pT 150–200 조건부 비교](AN_rawcharge/13_conditional_lepton_angles/SRtopology/EE_mll450_500_zpt150_200.png)
- [전체 평균과 TV](AN_rawcharge/13_conditional_lepton_angles/RESULTS.md)
- [모든 고정 구간의 내부 matching 후 차이](AN_rawcharge/13_conditional_lepton_angles/CONDITIONAL_RESULTS.md)

검증: 원래 lepton pT/phi로 계산한 vector-sum pT가 저장된 pt_l1l2와 일치한다.
새 cache의 pT histogram 및 sumw2는 두 fold 모두 study 12와 일치하고,
coarse 전달계수 결과의 평균/오차/TV도 EE/MM 두 target 모두 재현했다.
