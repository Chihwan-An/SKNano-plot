# 1 jet OS와 2 jet OS의 lepton pT / eta 비교

2026-09-19. **EE에서는 leading electron pT의 차이가 크다. 높은 mll 영역의 eta 분포는
비슷하지만, Z 구간에서 SR topology를 요구하면 endcap 비율도 커진다.**

DY MC, nominal DY 보정 및 lepton SF 적용, OS only이다. Charge-flip weight나
lepton momentum shift는 적용하지 않았다. 실제 OS data나 SS data도 읽지 않았다.
그림은 category마다 면적을 1로 맞춘 shape 비교이다.

## 비교한 세 표본

- 검정 `1 jet`: nJet==1.
- 파랑 `>=2 jets (nJet only)`: nJet>=2. 별도 passResolved / mlljj cut 없음.
- 빨강 `>=2 jets, resolved, mlljj>800`: nJet>=2, passResolved, mlljj>800.
  기존에 SR reference로 썼던 topology이다.

모두 hasPair, OS, mll>=60이며, mll 영역을 다시 나눠 비교했다.
`highmass`의 빨간 표본은 mll>=400도 요구하므로 resolved SR에 해당한다.
"2 jet"은 정확히 2개가 아닌 **2개 이상**이다.
EE는 실제 flip probability 입력인 abs(eta_SC), MM은 abs(eta)를 사용했다.

## EE: mll >=400 GeV

| 변수 | 1 jet OS | >=2 jet OS, jet 수만 | >=2 jet OS, SR |
|---|---|---|---|
| Leading 평균 pT [GeV] | 266.90 ± 0.32 | 299.82 ± 0.76 | 337.88 ± 1.00 |
| Subleading 평균 pT [GeV] | 200.62 ± 0.29 | 201.86 ± 0.65 | 221.88 ± 0.91 |
| Leading pT >=400 비율 | 8.07 ± 0.09% | 15.53 ± 0.23% | 24.00 ± 0.34% |
| Subleading pT >=400 비율 | 2.88 ± 0.06% | 3.96 ± 0.12% | 6.13 ± 0.19% |
| Leading endcap 비율 | 24.12 ± 0.15% | 23.51 ± 0.28% | 24.09 ± 0.34% |
| Subleading endcap 비율 | 25.37 ± 0.15% | 24.53 ± 0.28% | 24.39 ± 0.33% |

Endcap은 abs(eta_SC)>=1.566이다. 오차는 weighted MC 통계만 포함한다.
SR과 비교하면 leading 평균 pT는 약 26.6%, subleading은 약 10.6% 더 높다.
Leading의 pT>=400 fraction은 약 3배이다.
Eta 주변분포는 이보다 훨씬 비슷하지만, 완전히 같은 분포라고 가정한 것은 아니다.

[EE SR 영역 pT/eta 그림](AN_rawcharge/10_1jet_2jet_os_leptons/highmass/lepton_shapes_EE.png)
· [2D pT×eta 비율](AN_rawcharge/10_1jet_2jet_os_leptons/highmass/pt_eta_ratios_EE.png)

## EE: 60 <= mll <150 GeV

| 변수 | 1 jet OS | >=2 jet OS, jet 수만 | >=2 jet OS, SR topology |
|---|---|---|---|
| Leading 평균 pT [GeV] | 95.76 ± 0.02 | 113.04 ± 0.03 | 163.84 ± 0.12 |
| Subleading 평균 pT [GeV] | 66.68 ± 0.01 | 72.13 ± 0.01 | 86.14 ± 0.05 |
| Leading endcap 비율 | 22.48 ± 0.02% | 22.49 ± 0.03% | 32.48 ± 0.08% |
| Subleading endcap 비율 | 22.77 ± 0.02% | 22.79 ± 0.03% | 31.82 ± 0.08% |

Jet 수만 바꾼 표본에서는 eta 분포가 매우 비슷하다. SR topology 선택을 포함한
표본에서는 pT와 eta가 모두 달라진다. 이 비교만으로 passResolved의 ΔR와
mlljj cut의 효과를 각각 분리한 것은 아니다.

[EE Z 구간 pT/eta 그림](AN_rawcharge/10_1jet_2jet_os_leptons/Zwindow/lepton_shapes_EE.png)
· [2D pT×eta 비율](AN_rawcharge/10_1jet_2jet_os_leptons/Zwindow/pt_eta_ratios_EE.png)

## 2D 분포와 해석

2D map은 각 표본의 pT×eta 확률분포를 정규화한 뒤 target/1j를 계산한 것이다.
왼쪽 열은 >=2 jets (nJet only), 오른쪽 열은 SR topology, 위/아래는 leading/subleading이다.
같은 색 범위 0.25–4를 사용하며 이 범위 밖 숫자도 실제 값으로 표시한다.
source와 target의 effective entries가 모두 20 이상인 cell만 표시한다.
빈 cell에는 acceptance gap 또는 낮은 통계의 cell이 포함된다.

고정 binning에서 total variation distance(TV)=0.5*sum(abs(target probability - 1j probability)):

| mll 영역 | target | Leading pT×eta TV | Subleading pT×eta TV |
|---|---|---|---|
| >=400 | >=2 jets, nJet only | 0.129 | 0.057 |
| >=400 | SR topology | 0.287 | 0.129 |
| 60–150 | >=2 jets, nJet only | 0.167 | 0.125 |
| 60–150 | SR topology | 0.487 | 0.358 |

TV=0은 같은 분포, 1은 완전히 겹치지 않는 분포이다. 이는 binning에 의존하는
분포 차이의 요약값이며, charge-flip yield의 차이나 보정 계수 자체가 아니다.

**현재의 1 jet OS와 2 jet OS는 charge-flip 입력인 lepton pT×eta 분포가 같지 않다.**
특히 SR에서는 leading pT 분포를 확인해야 한다.
다만 이번에는 같은 넓은 mll 영역을 선택했을 뿐, mll shape 자체를 재가중해서
맞춘 것은 아니다. 따라서 차이 중 얼마나 mll shape 차이에서 오는지는 아직 분리하지 않았다.
두 전자의 joint event distribution이나 실제 평균 charge-flip weight도 이번 작업에서
맞추거나 비교한 것은 아니다.

MM도 함께 만들었고, highmass에서 평균 pT1은 266.6→336.2 GeV,
pT2는 198.6→218.7 GeV (1j→SR)로 같은 경향이다.
[MM highmass 그림](AN_rawcharge/10_1jet_2jet_os_leptons/highmass/lepton_shapes_MM.png).

## 출력 및 검증

- 전체 mll>=60, Zwindow, sideband 150–400, highmass >=400의 EE/MM 그림과 PDF를 생성했다.
- [전체 수치 표](AN_rawcharge/10_1jet_2jet_os_leptons/RESULTS.md)와
  [summary.json](AN_rawcharge/10_1jet_2jet_os_leptons/summary.json)에 exact weighted moments,
  통계오차, 고-pT/endcap fractions, TV를 저장했다.
- pT>=2000은 그림의 마지막 bin에 포함하지만 평균 pT는 원래 unclipped 값으로 계산했다.
- 두 lepton의 event count 및 histogram/moment yield 일치를 확인했고,
  기존 독립 mll study cache와 1j/SR의 mll-bin yield도 비교했다.
- 코드: [scripts/jetbin_lepton_shapes.py](scripts/jetbin_lepton_shapes.py).
  `data/jetbin_lepton_histograms.npz`와 함께 있으면 원본 dump 없이 재실행 가능하다.
- 입력은 기존과 같은 DY HT>=40 14개 샘플이다.
