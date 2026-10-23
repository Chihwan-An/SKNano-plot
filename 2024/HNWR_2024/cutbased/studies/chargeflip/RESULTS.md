# DY 보정 제거와 jet-category mll shape (2026-09-19)

DY 보정을 모두 제거해도 1 jet과 resolved SR의 mll shape 차이가 남는다.
reco pT(ll) 구간을 맞추면 150–200 GeV의 차이는 크게 줄지만,
넓은 mll 영역에서 template가 일치하지는 않는다.

## 그림

| 비교 | EE | MM |
|---|---|---|
| DY 보정 모두 제거 | [PNG](AN_rawcharge/08_mll_jetbins_noDY/mll_shape_EE.png) | [PNG](AN_rawcharge/08_mll_jetbins_noDY/mll_shape_MM.png) |
| reco Z pT 구간별 1 jet/SR ratio | [PNG](AN_rawcharge/08_mll_jetbins_noDY/mll_ratio_zpt_overview_EE.png) | [PNG](AN_rawcharge/08_mll_jetbins_noDY/mll_ratio_zpt_overview_MM.png) |
| OS-only, DY 보정 제거 | [PNG](AN_rawcharge/08_mll_jetbins_noDY/OS/mll_shape_EE.png) | [PNG](AN_rawcharge/08_mll_jetbins_noDY/OS/mll_shape_MM.png) |
| OS-only, reco Z pT 구간별 ratio | [PNG](AN_rawcharge/08_mll_jetbins_noDY/OS/mll_ratio_zpt_overview_EE.png) | [PNG](AN_rawcharge/08_mll_jetbins_noDY/OS/mll_ratio_zpt_overview_MM.png) |

모든 그림에 동일 이름의 PDF가 있다. 각 pT 구간의 4개 category mll 그림과 수치표는
[zpt_slices/](AN_rawcharge/08_mll_jetbins_noDY/zpt_slices/)에 있다.

## 보정을 제거한 효과

아래 숫자는 각 category의 Z peak (80–100 GeV)를 SR에 맞춘 뒤,
해당 mll 구간에서 적분한 **1 jet / SR**이다. 오차는 가중 MC 통계와
Z-peak 정규화 통계를 포함하며 systematic은 포함하지 않는다.

| mll [GeV] | EE nominal | EE noDY | MM nominal | MM noDY |
|---|---|---|---|---|
| 100–150 | 1.704 ± 0.010 | 1.755 ± 0.010 | 1.644 ± 0.008 | 1.684 ± 0.008 |
| 150–200 | 2.542 ± 0.017 | 2.756 ± 0.017 | 2.524 ± 0.015 | 2.719 ± 0.015 |
| 200–400 | 1.510 ± 0.009 | 1.643 ± 0.009 | 1.494 ± 0.007 | 1.615 ± 0.008 |
| 400–1000 | 0.462 ± 0.004 | 0.522 ± 0.005 | 0.466 ± 0.004 | 0.526 ± 0.004 |
| 1000–2000 | 0.183 ± 0.007 | 0.219 ± 0.007 | 0.192 ± 0.006 | 0.226 ± 0.007 |

OS-only에서도 noDY 150–200 GeV ratio는 EE 2.765 ± 0.017, MM 2.720 ± 0.015,
400–1000 GeV에서는 EE 0.523 ± 0.005, MM 0.527 ± 0.004로 거의 같다.

따라서 현재 그림의 불일치를 DY correction의 적용 차이만으로 설명할 수 없다.
코드상 C(gen Z pT)와 EW는 1 jet에도 적용된다. resolved jet-pT R은 passResolved일 때만
적용되며, passResolved가 아니어도 passBoosted인 이벤트에는 boosted R이 적용된다.
이번에는 저장된 `weight / w_dy`로 이 세 보정을 한꺼번에 제거했다.
개별 보정의 효과를 분리한 결과는 아니다.

## 보정 없이 reco pT(ll) 구간을 나눈 결과

각 pT 구간 안에서 Z-peak 정규화를 독립적으로 수행했다.

| reco pT(ll) [GeV] | EE, mll 150–200 | MM, mll 150–200 | EE, mll 400–1000 | MM, mll 400–1000 |
|---|---|---|---|---|
| 50–100 | 1.061 ± 0.020 | 1.077 ± 0.017 | 0.207 ± 0.005 | 0.212 ± 0.004 |
| 100–150 | 0.841 ± 0.015 | 0.851 ± 0.013 | 0.208 ± 0.004 | 0.223 ± 0.004 |
| 150–200 | 0.888 ± 0.016 | 0.881 ± 0.014 | 0.263 ± 0.006 | 0.284 ± 0.006 |
| 200–300 | 0.915 ± 0.014 | 0.919 ± 0.013 | 0.405 ± 0.008 | 0.447 ± 0.008 |
| 300–500 | 0.950 ± 0.018 | 0.975 ± 0.016 | 0.837 ± 0.024 | 0.925 ± 0.020 |
| >=500 | 0.401 ± 0.016 | 0.389 ± 0.013 | 0.434 ± 0.017 | 0.403 ± 0.014 |

pT 50–500 GeV에서 mll 150–200 GeV의 ratio가 약 0.84–1.08로 줄어든 점은
서로 다른 pT(ll) 구성 비율이 inclusive shape 차이에 크게 관여함을 시사한다.
하지만 높은 mll에서 남는 차이와 pT >=500 GeV의 차이 때문에,
이 결과만으로 pT 보정 후 1 jet template를 SR에 그대로 사용할 수 있다고 결론낼 수는 없다.

0–50 GeV 구간에는 모든 category의 Z-peak yield가 0이다.
이 구간의 그림은 60–2000 GeV 전체 면적을 1로 정규화했으므로 위 표와 직접 비교하지 않는다.
lepton pT >60/53 GeV 조건에서, 질량을 무시하면
`mll² + pT(ll)² >= (pT1+pT2)² > 113²`이므로
`mll <100 GeV`인 이벤트는 `pT(ll)>52.6 GeV`여야 한다.
따라서 낮은 pT 구간의 빈 Z peak는 이 선택과 일관된다.

## 해석 범위와 확인

- SR reference는 >=2 jets뿐 아니라 passResolved의 ΔR 조건과 mlljj >800 GeV를 요구한다.
  mll 자체의 SR threshold는 제거한 reference이다. 1 jet에는 같은 mlljj 조건을 줄 수 없고,
  기존 비교는 1 jet에 별도의 lepton-lepton ΔR 조건도 추가하지 않는다.
  남은 차이의 원인을 jet multiplicity 하나로 단정할 수 없다.
- 여기서 Z pT는 **reco dilepton pT**이다. 보정 C의 인자인 generator Z pT와 구분한다.
- cfboost DY 14개 HT >=40 샘플, hasPair 28,318,767 events를 사용했다.
  HT <40 샘플은 포함되지 않으며 특히 0 jet 전체 DY 예측에는 이 제한이 중요하다.
- collision data, OS data SR, SS data SR는 읽지 않았다. 이 비교는 DY mll 진단이고,
  charge-flip rate/energy-shift를 적용한 SS closure 검증은 아니다.
- 가중치를 float64로 누적했다. nominal SR 총 yield는 EE 36,888.759, MM 51,741.500으로
  이전 표의 36,889 / 51,742와 일치하며, bin별 차이는 최대 0.100 event이다
  (기존 표는 반올림 및 float32 histogram 누적을 사용).
- w_dy가 양수/유한한지 검사하고 `(weight/w_dy)*w_dy == weight`를 검증했다.
- 작고 독립적인 histogram cache로 PNG 40개와 PDF 40개를 만들었다.
  script와 cache만 별도 임시 경로로 복사한 후 `/tmp`에서 재실행해 경로 독립성도 확인했다.

세부 선택 및 재실행 방법은 [README.md](README.md), bin별 값은
[ratios.md](AN_rawcharge/08_mll_jetbins_noDY/ratios.md),
기계 판독용 결과는 [summary.json](AN_rawcharge/08_mll_jetbins_noDY/summary.json)을 참고한다.
