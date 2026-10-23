# 1 jet OS의 mll을 2 jet OS에 맞춘 뒤 pT/eta 비교

## 무엇을 했나

- 입력은 기존 nominal DY 보정과 lepton SF가 적용된 DY OS MC이다. 데이터와 charge-flip weight는 사용하지 않았다.
- 1 jet은 `nJet==1`. 목표는 `nJet>=2`만 요구하는 `ge2j`와,
  여기에 `passResolved` 및 `mlljj>800 GeV`를 요구하는 `SRtopology`를 따로 사용했다.
- 각 mll bin에서 `r = sumw(target)/sumw(1j)`를 구하고 1 jet의 기존 event weight에 r을 곱했다.
  EE/MM 및 두 target에 각각 다른 r을 사용한다.
- mll 경계 [GeV]: 60,70,80,90,100,110,120,130,150,175,200,250,300,400,
  500,700,1000,1300,1600,2000,inf. 모든 channel/category/mll bin의 유효 MC 통계는 최소 38.7이다.
- mll 구간별 **yield**는 정확히 일치한다. 구간 내부의 연속 mll 분포까지 일치시키지는 않는다.
  동일 sample로 factor를 구하고 비교하므로 mll 일치는 정의상 성립하며 독립 closure가 아니다.
- 이후 각 mll 영역 안에서 lepton 분포를 면적 1로 표시했다.
  검정: 2jet target, 파랑: 1jet 전, 빨강: 1jet mll matching 후. 아래 ratio는 1jet/target.
- 오차는 weighted MC 통계, 추정한 factor의 불확도, 같은 target 재사용에 따른 상관을 포함한다.
  Systematic은 포함하지 않는다. pT 평균은 overflow clipping 전 원래 값을 사용한다.

## 핵심: EE, mll >= 400 GeV, SRtopology target

| 변수 | 1 jet 전 | 1 jet mll matching 후 | 2 jet target |
|---|---:|---:|---:|
| 평균 leading pT [GeV] | 266.90 ± 0.32 | 296.73 ± 0.81 | 337.88 ± 1.00 |
| 평균 subleading pT [GeV] | 200.62 ± 0.29 | 227.96 ± 0.74 | 221.88 ± 0.91 |
| leading abs etaSC >= 1.566 비율 [%] | 24.12 ± 0.15 | 23.64 ± 0.16 | 24.09 ± 0.34 |
| subleading abs etaSC >= 1.566 비율 [%] | 25.37 ± 0.15 | 24.98 ± 0.16 | 24.39 ± 0.33 |

2D pT/eta 분포 차이(TV: 0이면 동일)는 leading 0.287 -> 0.174,
subleading 0.129 -> 0.054로 줄었다. 하지만 leading pT는 여전히 부족하고,
subleading 평균은 오히려 target보다 약 6 GeV 높아졌다. eta는 대체로 비슷하다.
따라서 **이번 mll-bin별 matching만으로 lepton pT/eta joint 분포가 일치하지는 않는다.**
고질량 mll bin 내부의 남은 shape 차이와, 같은 mll에서도 다른 lepton kinematics는
이 검사만으로 분리할 수 없다. mll을 더 세밀히 나누는 검사는 별도이다.

`ge2j`만 target으로 해도 leading 평균은 266.90 -> 275.41 GeV에 그쳐,
target 299.82 GeV와 차이가 남는다. subleading은 200.62 -> 208.43 GeV,
target 201.86 GeV이다.

Z window (60–150 GeV)의 SRtopology 비교는 개선이 거의 없다:
leading 평균 95.76 -> 96.12 GeV vs target 163.84 GeV,
subleading 66.68 -> 66.80 GeV vs 86.14 GeV.
여기서 eta endcap 비율도 1jet 약 22–23% vs target 약 32%로 다르다.
SRtopology에는 jet 수 외에 resolved/mlljj 선택도 있으므로 차이를 jet 수 하나의 효과라고 해석하지 않는다.

## 결과 파일

- [SR target mll matching 및 factor](AN_rawcharge/11_1jet_2jet_mll_reweighted/SRtopology/mll_matching_EE.png)
- [SR target, 고질량 pT/eta](AN_rawcharge/11_1jet_2jet_mll_reweighted/SRtopology/highmass/lepton_shapes_EE.png)
- [SR target, Z window pT/eta](AN_rawcharge/11_1jet_2jet_mll_reweighted/SRtopology/Zwindow/lepton_shapes_EE.png)
- [nJet>=2만 target, 고질량 pT/eta](AN_rawcharge/11_1jet_2jet_mll_reweighted/ge2j/highmass/lepton_shapes_EE.png)
- [EE/MM 전체 수치와 오차](AN_rawcharge/11_1jet_2jet_mll_reweighted/RESULTS.md)
- [구간별 factor와 유효 통계](AN_rawcharge/11_1jet_2jet_mll_reweighted/mll_factors.json)

이 결과는 OS lepton kinematics 진단이며 SS yield, charge-flip transfer 또는 mlljj closure의 검증이 아니다.
