# Reco Z pT 기반 1jet OS → 2jet OS 전달계수

## 정의

- DY OS MC, 기존 nominal DY 보정 및 lepton SF 유지. 데이터와 charge-flip weight는 사용하지 않았다.
- Z pT는 generator 변수가 아니라 저장된 reco dilepton `pt_l1l2`이다.
- Source는 nJet==1. Target은 `ge2j`(nJet>=2) 또는 `SRtopology`(nJet>=2, passResolved, mlljj>800 GeV).
- EE/MM, target, mll 영역마다 별도로 `r = sumw(target)/sumw(1j)`를 구해 기존 1jet weight에 곱한다.
  inclusive 계수를 highmass에 재사용한 것은 아니다. 두 jet target은 서로 겹치므로 독립 비교군은 아니다.
- 세 방법: `mll`만 matching, 영역 내 `zpt`만 matching, `mll_zpt` 공동 분포 matching.
  `mll_zpt`는 두 개의 1D 비율을 단순히 곱한 것이 아니라 2D cell의 target/source이다.
  이는 mll을 먼저 맞춘 뒤 각 mll bin 안에서 조건부 Z pT shape ratio를 곱하는 것과 같다.
- mll edges [GeV]: 60,80,90,100,120,150,200,300,400,500,700,1000,inf.
  Study 11보다 일부 구간이 넓으므로 mll-only 수치도 이 공통 binning에서 다시 계산했다.
- 기본 Z pT edges [GeV]: 0,20,40,60,80,100,125,150,175,200,250,300,400,500,700,1000,1500,inf.
  학습 표본에서 source/target 모두 Neff>=50이 되도록 인접 Z pT 구간을 합친다.
  마지막 부족한 구간은 앞 구간에 합치며 이벤트를 버리지 않는다.
- 파일별 고정 seed로 MC를 두 절반에 무작위 배정했다. Fold 0에서 계수를 만들고 fold 1에서 검사한다.
  통계 오차는 검증 MC의 sumw2 및 학습 계수의 오차를 포함한다. Systematic은 포함하지 않는다.
- `same_sample`은 별도로 전체 MC의 비율을 전체 MC에 적용한다. 이때 matching 변수 일치는 정의상 성립한다.
  bin 선택에 학습 절반 통계를 썼으므로 독립 검증도 완전히 사전 고정한 binning의 hypothesis test는 아니다.
- 두 검사는 모두 shape를 면적 1로 그린다. absolute yield와 factor는 NPZ/JSON에 따로 저장한다.

## EE, mll >= 400 GeV: 독립 검증 표본의 평균 pT [GeV]

| Target | Lepton | 1jet 전 | Z pT만 | mll+Z pT | 2jet target |
|---|---|---:|---:|---:|---:|
| nJet>=2 | leading | 266.43 ± 0.46 | 299.25 ± 0.96 | 301.30 ± 1.24 | 299.61 ± 1.11 |
| nJet>=2 | subleading | 200.50 ± 0.41 | 200.09 ± 0.58 | 202.26 ± 0.98 | 200.99 ± 0.94 |
| SRtopology | leading | 266.43 ± 0.46 | 316.05 ± 1.24 | 335.50 ± 1.61 | 337.95 ± 1.48 |
| SRtopology | subleading | 200.50 ± 0.41 | 199.89 ± 0.69 | 219.48 ± 1.37 | 220.60 ± 1.35 |

평균뿐 아니라 pT-bin shape 차이도 크게 줄었다. TV는 normalized histogram 차이 절댓값 합의 절반이며,
0이면 동일하고 1이면 겹침이 없다. 이는 residual의 통계적 유의도를 뜻하는 p-value는 아니다.

| Target / lepton | 전 | mll만 | Z pT만 | mll+Z pT |
|---|---:|---:|---:|---:|
| nJet>=2 / leading | 0.1295 | 0.1019 | 0.0155 | 0.0116 |
| nJet>=2 / subleading | 0.0552 | 0.0580 | 0.0189 | 0.0167 |
| SRtopology / leading | 0.2920 | 0.1776 | 0.1016 | 0.0204 |
| SRtopology / subleading | 0.1285 | 0.0571 | 0.1068 | 0.0244 |

해석: jet multiplicity만 다른 경우 Z pT matching으로 lepton pT 차이의 상당 부분이 사라진다.
하지만 mlljj/resolved 선택이 포함된 SR target에서는 Z pT만으로 부족하며 mll과 함께 맞추면 크게 개선된다.
MM에서도 같은 경향이다. 이것이 '차이가 무조건 recoil 하나에서만 온다'는 증명은 아니다.
bin 내부 차이, angular/acceptance 차이, MC 모델링 불확도를 이 검사에서 모두 분리한 것은 아니다.

특히 eta와 pT-eta 공동 분포는 pT marginal만큼 잘 맞는다고 일반화하면 안 된다.
EE SR highmass leading eta TV는 전 0.0121 -> mll+Z pT 후 0.0270으로 오히려 커지고,
pT-eta 공동 TV는 leading 0.0502, subleading 0.0474가 남는다.
낮은 pT/고 pT 꼬리에서도 일부 residual이 보인다. 따라서 charge-flip weight 및 mlljj closure는 여전히 별도 검증이 필요하다.

Z window (60–150 GeV)의 SR target에서도 Z pT만으로 평균 leading은
95.77 -> 161.30 GeV (target 163.74), subleading은 66.68 -> 86.57 GeV (target 86.18)로 크게 개선된다.

## 파일과 계수 사용 시 주의

- [독립 검사: nJet>=2, Z pT만](AN_rawcharge/12_1jet_2jet_zpt_reweighted/ge2j/highmass/zpt/validation/lepton_shapes_EE.png)
- [독립 검사: SR target, Z pT만](AN_rawcharge/12_1jet_2jet_zpt_reweighted/SRtopology/highmass/zpt/validation/lepton_shapes_EE.png)
- [독립 검사: SR target, mll+Z pT](AN_rawcharge/12_1jet_2jet_zpt_reweighted/SRtopology/highmass/mll_zpt/validation/lepton_shapes_EE.png)
- [SR highmass Z pT 전달계수 그림](AN_rawcharge/12_1jet_2jet_zpt_reweighted/SRtopology/highmass/zpt_factors_EE.png)
- [전체 계수, 구간 경계 및 유효 통계](AN_rawcharge/12_1jet_2jet_zpt_reweighted/training_factors.json)
- [전체 비교 수치](AN_rawcharge/12_1jet_2jet_zpt_reweighted/RESULTS.md)

계수 JSON은 학습 절반의 비율이며 구간은 [low, high), high=null은 +inf이다.
예를 들어 `EE/SRtopology/highmass`의 `zpt` 계수는 Z pT 100–125: 0.2231±0.0086,
200–250: 0.8742±0.0329, 400–500: 1.6232±0.0824이다. 절대 yield 비율이므로 1보다 클 수 있다.
이를 다른 mll 영역/target의 1jet에 그대로 쓰는 것은 여기서 검증하지 않았다.
같은 영역에서의 추가 MC 전달 가중치이며 이미 적용된 nominal DY 보정을 대체하는 계수가 아니다.

검증: 원본 14개 파일에서 새 cache를 생성했고, Z pT 및 fold 축을 합친 histogram/sumw2/counts와
raw moments가 기존 study 10 cache와 일치함을 확인했다. 동일 표본 matching yield,
joint→marginal covariance 투영 및 독립 표본 오차 전파의 수치 미분 검사도 통과했다.
