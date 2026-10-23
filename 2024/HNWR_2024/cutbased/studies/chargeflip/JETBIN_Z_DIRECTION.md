# 정확히 0/1/2jet의 Z 방향 분포

## 무엇을 그렸나

- 기존 DY OS MC, hasPair, mll>=60. nJet==0, ==1, ==2를 각각 면적 1로 정규화했다.
  nJet>=2도 숫자 파일에는 있으나 그림에는 정확히 2jet만 그린다.
- 분석 jet은 lepton cleaning을 거친 pT>40 GeV, abs eta<2.5 jet이다.
  **0jet은 이 조건의 jet이 없다는 뜻이지 QCD radiation이 없다는 뜻이 아니다.**
- passResolved 또는 mlljj cut은 요구하지 않는다. 기존 trigger/tight-lepton/pT/eta selection은 남아 있다.
- nominal은 기존 DY 보정 포함, noDY는 weight/w_dy. 그 외 normalization과 lepton SF는 유지한다.
  이전에 구한 1jet→2jet 전달계수, angular/charge-flip weight는 사용하지 않는다.
- signed eta_ll / signed y_ll / abs eta_ll / abs y_ll를 한 그림에 표시한다.
  검정=0jet, 파랑=1jet, 빨강=2jet. 아래 ratio는 각각 normalized category / normalized 1jet이다.
- 모든 eta는 lepton momentum eta에서 재구성한 dilepton 값이며 supercluster eta가 아니다.

## 결과: EE, nominal DY

| mll 범위 | jet 수 | 평균 abs eta_ll | 평균 abs y_ll | 평균 Z pT [GeV] | abs eta_ll<1 비율 |
|---|---:|---:|---:|---:|---:|
| 80–100 GeV | 0 | 1.424 | 1.215 | 118.08 | 31.77% |
| 80–100 GeV | 1 | 1.071 | 0.928 | 141.97 | 50.69% |
| 80–100 GeV | 2 | 1.039 | 0.923 | 162.02 | 52.37% |
| >=400 GeV | 0 | 2.802 | 0.859 | 56.77 | 7.57% |
| >=400 GeV | 1 | 2.206 | 0.805 | 106.89 | 15.77% |
| >=400 GeV | 2 | 1.967 | 0.788 | 151.78 | 20.96% |

이번 입력/선택에서는 eta 기준으로 **2jet이 1jet보다 약간 더 중앙**, 0jet이 가장 넓다.
사용자가 예상한 '1jet > 2jet > 0jet 순으로 중앙 집중'은 이 표본에서 성립하지 않는다.
MM 및 DY 보정을 제거한 비교에서도 평균 abs eta의 순서는 동일하다.
반면 rapidity에서는 1jet과 2jet의 차이가 훨씬 작다.

Z pT를 100–150 GeV로 제한하면 EE highmass의 평균 abs eta는
0jet 2.205±0.020, 1jet 1.938±0.007, 2jet 1.919±0.014이다.
1jet/2jet 차이가 줄지만 이 50 GeV 구간 내부 qT와 mll은 정확히 맞추지 않았다.
이는 조건부 진단이며 jet 수만의 인과 효과 측정이 아니다.

## eta와 rapidity를 함께 봐야 하는 이유

`pz = sum(pt_l*sinh(eta_l))`, `qT = |sum(vec pt_l)|`, `mT = sqrt(mll^2+qT^2)`로 계산했다.

`y_ll = asinh(pz/mT)`

`eta_ll = asinh(pz/qT) = asinh((mT/qT)*sinh(y_ll))`

따라서 같은 mll와 y에서도 qT가 작으면 abs eta가 커진다.
고질량의 signed eta 분포가 양쪽으로 갈라져 보여도, 그것이 같은 모양의 rapidity/longitudinal boost를 뜻하지 않는다.
그림의 큰 eta 차이에는 recoil 크기 자체의 효과가 섞여 있다.
eta 자체는 lab 운동량의 방향을 나타내는 올바른 변수이며, mass가 있는 입자의 종방향 boost 비교에는 y가 더 직접적이다.

0jet의 분포도 eta에서 평탄/완전 무작위일 이유는 없다.
입사 beam 축과 parton momentum fractions, radiation 및 선택 조건에 의존한다.
Z rapidity와 transverse momentum을 PDF/QCD 예측과 비교하는 실험 예:
[CMS, arXiv:1110.4973](https://arxiv.org/abs/1110.4973).

또한 순수한 longitudinal boost는 개별 lepton pT를 바꾸지 않는다.
따라서 y 차이를 찾는 것만으로 앞서 본 subleading pT residual의 원인이 확정되지는 않는다.
Lepton acceptance 및 decay-angle/recoil과의 상관을 함께 확인해야 한다.

## 중요한 한계

1. 입력 14개는 **generator HT>=40 샘플뿐**이다. 특히 0jet의 inclusive DY 예측에는 HT<40 기여가 빠져 있다.
   위 순서와 shape를 일반적인 generator-level 0/1/2jet DY 법칙으로 사용하면 안 된다.
2. Leading/subleading lepton pT>60/53 GeV 등의 기존 선택이 있다.
   Z peak에서는 낮은 qT 이벤트가 강하게 걸러진다. 출력은 이 분석에서 선택된 reco 이벤트 분포이다.
3. 2jet sample도 두 jet의 방향/세기/추가 radiation이 다양하므로, jet가 하나 늘면 qT가 반드시 줄어드는 것은 아니다.
   현재 표본에서는 평균 qT가 오히려 2jet에서 더 높다.
4. eta 바깥쪽 bin은 abs eta>=6 overflow를 포함한다. Raw 평균은 clipping하지 않았다.
   EE highmass overflow 비율은 0jet 0.240%, 1jet 0.045%, 2jet 0.073%이다.
   정확한 qT==0 이벤트는 이번 입력에서 없었다. 코드상 존재하면 eta 통계에서만 제외하고 기록한다.
5. 오차는 weighted MC 통계와 정규화 상관을 포함한다. Systematic은 포함하지 않는다.

## 결과 파일

- [EE Z peak, 80–100 GeV](AN_rawcharge/14_jetbin_z_direction/nominal/Zpeak/all_zpt/z_direction_EE.png)
- [EE highmass, >=400 GeV](AN_rawcharge/14_jetbin_z_direction/nominal/highmass/all_zpt/z_direction_EE.png)
- [EE highmass, Z pT 100–150 GeV](AN_rawcharge/14_jetbin_z_direction/nominal/highmass/zpt_100to150/z_direction_EE.png)
- [EE highmass, DY 보정 제거](AN_rawcharge/14_jetbin_z_direction/noDY/highmass/all_zpt/z_direction_EE.png)
- [전체 수치 및 통계 오차](AN_rawcharge/14_jetbin_z_direction/RESULTS.md)

검증: 재구성 qT가 저장된 pt_l1l2와 일치한다. 1jet 및 >=2jet의 mll-bin별 yield/sumw2/counts는
기존 study 10과 일치한다. eta/y 재구성의 longitudinal reflection, azimuthal rotation 및 같은 lepton eta 조건의 단위 검사를 통과했다.
