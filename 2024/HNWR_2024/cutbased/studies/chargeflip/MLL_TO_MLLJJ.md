# mll-only reweighting으로 DY 2 jet mlljj가 닫히는가?

2026-09-19. **EE의 mll >=400 GeV SR에서는 현재 MC 통계로 유의한 불일치가 없지만,
Z 구간에서는 mll이 맞아도 mlljj가 명확히 다르다.** 따라서 모든 mll 영역에서
mll 하나가 충분하다는 가정은 성립하지 않는다. SR만 사용하는 방법은 더 검토할 여지가 있다.

## 이번에 실제로 검사한 것

1 jet 이벤트 자체에는 두 번째 jet과 mlljj가 없으므로, 우선 2 jet OS MC의
`P(mlljj | mll)`을 SS에 재사용할 수 있는지 검사했다. 이것은 1j -> 2j transfer의
완성된 검증이 아니고, OS의 2 jet kinematics를 이용하는 방식을 위한 선행 검사다.

- cfboost DY 14개 샘플 중 `hasPair`, `nJet>=2`, `passResolved`, `mlljj>800`, `mll>=60`.
  총 2,504,603개 이벤트. TightCharge 추가 조건 없음. collision data는 전혀 읽지 않았다.
- 주 결과는 기존 DY 보정이 켜진 `weight`. `weight/w_dy`는 보조 검사다.
- 각 샘플 안에서 고정 seed 20260919와 파일 이름에 따른 seed로 이벤트를 50/50 랜덤 분할.
  한쪽에서 `T(mll)=SS_train(mll)/OS_train(mll)`을 구하고 다른 쪽 OS에 곱한다.
  `mll` 이외의 변수로는 재가중하지 않는다. jet/lepton 4-vector를 수정하지 않는다.
- 학습 SS/OS 유효 통계가 각각 30 이상이 되도록 mll bin을 병합한다.
  100, 150, 400 GeV 경계는 넘지 않는다. 학습과 검증은 분리돼 있다.
- 검증 표본에서 mll closure와 mlljj closure를 별도로 검사한다.
  Shape 비교는 해당 mll 영역 안에서 각각 unit area로 정규화한다.
  별도로 absolute predicted/SS yield도 보고한다.
- mlljj bin은 기존 resolved SR plotting spec과 같은
  800,1000,1200,1400,1600,2000,2400,2800,3200,8000 GeV.
  >=8000 GeV overflow는 마지막 bin에 포함한다 (전체 입력 168 events).
- mll>=400 경계에 정확히 걸리는 입력 이벤트는 0개라, 실제 analyzer의 mll>400과 동일하다.

## DY 보정 적용, EE 결과

아래 주 표는 genPartIdx로 양쪽 lepton이 prompt 또는 tau-origin gen lepton에 매칭되고
gen charge가 OS인 이벤트에서, **zero-flip OS -> single-flip SS**를 검사한 결과다.
일반 reco DY OS/SS 비교도 별도로 수행했으며 같은 정성적 결론이다.

| mll 영역 | mll 검증 chi2/ndf, p | mlljj 검증 chi2/ndf, p | 해석 |
|---|---|---|---|
| 60–150 GeV | 20.69/16, 0.191 | 157.30/8, 5.9e-30 | mll은 맞지만 mlljj는 불일치 |
| 150–400 GeV | 14.59/11, 0.202 | 12.41/8, 0.134 | 현재 통계로 유의한 불일치 없음 |
| >=400 GeV (SR) | 7.44/6, 0.282 | 4.50/8, 0.810 | 현재 통계로 유의한 불일치 없음 |

일반 reco SS 전체를 target으로 삼아도 SR mlljj는 3.50/7, p=0.835이고,
Z 구간에서는 151.16/8로 크게 어긋난다.
SS purity는 weighted yield 기준 Z 구간 97.35%, SR 71.46%가 위 truth single-flip 정의에 해당한다.
나머지를 전부 non-flip이라고 단정할 수는 없다 (매칭 실패 등도 포함).

| 주요 그림 | mll 검증 | mlljj 검증 |
|---|---|---|
| EE SR, single flip | [PNG](AN_rawcharge/09_mll_to_mlljj_closure/nominal/prompt_singleflip/EE/SR/mll_validation.png) | [PNG](AN_rawcharge/09_mll_to_mlljj_closure/nominal/prompt_singleflip/EE/SR/mlljj_closure.png) |
| EE Z 구간, single flip | [PNG](AN_rawcharge/09_mll_to_mlljj_closure/nominal/prompt_singleflip/EE/Zwindow/mll_validation.png) | [PNG](AN_rawcharge/09_mll_to_mlljj_closure/nominal/prompt_singleflip/EE/Zwindow/mlljj_closure.png) |
| EE SR, reco SS 전체 | [PNG](AN_rawcharge/09_mll_to_mlljj_closure/nominal/reco_all/EE/SR/mll_validation.png) | [PNG](AN_rawcharge/09_mll_to_mlljj_closure/nominal/reco_all/EE/SR/mlljj_closure.png) |

각 PNG에 같은 이름의 PDF가 있다. 검정은 SS validation, 파랑은 총 면적만 맞춘 OS,
빨강은 학습한 T(mll)을 적용한 OS이다. Ratio pad의 빨간 band는 예측 통계와
T(mll)의 통계 오차, 검정 점의 오차는 SS validation 통계다.

## SR에서 어디까지 말할 수 있는가

SR의 absolute yield ratio는 single-flip target에서 **1.085 +/- 0.096**,
일반 reco SS target에서 **1.144 +/- 0.103**이다.

그러나 SR mlljj는 재가중 전에도 single-flip target에서 6.74/8, p=0.565였다.
따라서 mll 재가중이 반드시 필요하거나 그것만으로 충분하다는 결론은 아니다.
또한 SR single-flip 검증 표본은 780 MC events이고 weight에 따른 유효 통계는 더 적다.
고질량 tail의 shape 오차는 크다. 예를 들어 마지막 mlljj >=3200 GeV bin의
prediction/SS는 **0.59 +/- 0.31**, SS 유효 통계는 3.68이다.
이 bin은 Gaussian chi2에서 제외된다. Tail에서 10% 정밀도의 closure를 확인한 것은 아니다.

Z 구간에서는 이에 비해 mlljj 1600–2000 GeV ratio가 **0.687 +/- 0.037**,
2000–2400 GeV는 **0.581 +/- 0.047**로 명확히 다르다.
같은 mll marginal distribution만 맞춰도 conditional jet/lepton kinematics 차이는 남을 수 있음을 보여준다.

## 안정성 및 통계 처리

- 학습/검증 절반을 바꾸면 nominal EE single-flip SR의 mll 검증 p=0.140,
  mlljj는 10.91/7, p=0.142. Z 구간의 불일치는 유지된다 (133.33/8).
  [반대 분할 결과](AN_rawcharge/09_mll_to_mlljj_closure/reverse_split/RESULTS.md).
  두 분할 결과는 서로 독립적인 두 실험이 아니므로 p-value를 합치지 않는다.
- 최소 학습 유효 통계를 15/30/60으로 바꾸고 분할도 뒤집어 점검했다.
  EE single-flip SR mlljj p는 0.063–0.870 범위여서 이 변형들에서 5% 수준으로 기각되지는 않았다.
  Z 구간은 모든 변형에서 크게 어긋났다. 낮은 SR 통계와 binning 의존성은 계속 고려해야 한다.
- DY 보정을 제거해도 nominal과 같은 정성적 결론이다.
  기본 분할 single-flip EE SR mlljj는 3.46/8, p=0.903이고 Z 구간은 161.74/8.
- mlljj 예측의 공분산에는 validation OS의 sumw2와 동일 T(mll)을 공유하는
  mlljj bin 간 학습-factor 통계 상관관계를 포함했다. Unit-area normalization도 공분산에 전파했다.
- Gaussian chi2는 SS validation 유효 통계 >=10인 bin만 사용하고 covariance rank를 ndf로 쓴다.
  p-value는 통계오차 기준 근사 검정이며 detector/theory systematics는 포함하지 않는다.
- MM truth single-flip SS는 전체 선택에서 총 18개, SR에서 총 3개뿐이다.
  MM에서는 이 입력으로 closure 여부를 판정할 수 없다.

## 실행 및 결과 파일

```bash
python3 /path/to/chargeflip/scripts/mll_to_mlljj_closure.py

python3 /path/to/chargeflip/scripts/mll_to_mlljj_closure.py \
  --validation-fold 0 --channels EE --modes nominal --kinds prompt_singleflip \
  --out-dir /path/to/reverse_split
```

원본 NPZ가 필요 없는 portable cache는 `data/mll_to_mlljj_histograms.npz`이다.
원본으로 다시 만들 때만 `--dumps /path/to/dumps_boost`를 지정한다.
bin별 yield/covariance는 각 결과 폴더의 `histograms.npz`, ratio/error와 학습 factor는
`summary.json`, 전체 표는 [RESULTS.md](AN_rawcharge/09_mll_to_mlljj_closure/RESULTS.md)에 있다.

이번 검사는 DY 2 jet OS MC의 conditional mlljj shape를 재사용하는 테스트이다.
1 jet OS 데이터로부터 얻은 mll template의 2 jet SS extrapolation, charge-flip SF,
lepton energy-shift, 실제 데이터의 non-DY subtraction은 아직 검증한 것이 아니다.
