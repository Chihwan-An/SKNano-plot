# NLO에서 정확히 0 / 1 / 2jet의 Z eta

## 결과

20 sample, 총 7,600,000 raw events의 부분 통계 확인이다. Analyzer event error는 0개였다.
각 jet category를 면적 1로 정규화했을 때 평균 |eta_ll|는 다음과 같다 (MC 통계 오차).

| channel / reco mll | 0jet | 1jet | 2jet |
|---|---:|---:|---:|
| EE, 80–100 GeV | 1.468 ± 0.054 | 1.084 ± 0.016 | 1.028 ± 0.029 |
| MM, 80–100 GeV | 1.469 ± 0.040 | 1.162 ± 0.015 | 1.112 ± 0.022 |
| EE, >=400 GeV | 3.738 ± 0.007 | 2.268 ± 0.009 | 1.889 ± 0.016 |
| MM, >=400 GeV | 3.609 ± 0.006 | 2.277 ± 0.008 | 1.857 ± 0.015 |

이 선택에서는 **0jet의 eta가 가장 넓다**. Z peak에서 1jet/2jet의 평균 차이는
각 채널에서 약 1.7/1.9 sigma에 불과하므로 작은 순서 차이를 단정하지 않는다.
고질량에서는 2jet이 1jet보다 eta 기준으로 확실히 중앙 쪽이다.

그러나 EE 고질량의 평균 |y_ll|는 0/1/2jet에서 0.863 / 0.820 / 0.815로
eta 차이보다 훨씬 작다. 평균 qT는 26.2 / 110.3 / 179.9 GeV로 크게 다르다.
qT를 100–150 GeV로 제한하면 같은 EE 고질량의 평균 |eta|는
1jet 1.982 ± 0.015, 2jet 1.948 ± 0.030으로 서로 약 1 sigma 이내이다.
MM도 1.992 ± 0.014 대 1.963 ± 0.035이다.
이는 eta 차이의 상당 부분이 recoil 크기와 연관됨을 보여 주는 조건부 진단이다.
구간 안의 qT/mll/decay angle을 정확히 맞춘 검사는 아니며 subleading-pT residual의 원인 확정은 아니다.

## 입력과 정의

- 2024 `DYto2E_MLL*`, `DYto2Mu_MLL*`, POWHEG+PYTHIA8. 각 채널에서
  10–50, 50–120, 120–200, 200–400, 400–800, 800–1500, 1500–2500,
  2500–4000, 4000–6000, >=6000 GeV의 10개 generator mass sample을 사용한다.
- 빠른 진단용 부분 통계: 50–120은 채널별 2,000,000 events,
  나머지는 각 sample의 최대 200,000 events. 정렬된 raw file 목록의 앞부분이다.
  전체 생산 통계 결과가 아니다. 실제 입력 파일과 처리량은 결과의 provenance.json에 기록한다.
- **Generator HT cut 없음.** 기존 LO study 14는 HT>=40 입력만 있었으므로
  특히 0jet의 LO/NLO 차이를 순수 perturbative-order 효과로 해석하면 안 된다.
- 기존 `HNWR_ChargeFlip` 분석기를 그대로 실행한다. 기존 trigger/ID/acceptance,
  leading/subleading lepton pT>60/53 GeV 선택을 유지한다.
  따라서 detector/analysis selection 전의 inclusive generator Z 분포가 아니다.
- `hasPair`, OS, reco mll>=60, cleaned jet pT>40 GeV, |eta|<2.5.
  그림은 정확히 nJet=0,1,2이며 >=2나 SR topology 선택이 아니다.
- eta는 두 reconstructed lepton의 **합 운동량 pseudorapidity**이다.
  Lepton eta 또는 supercluster eta가 아니다. 비교용 massive dilepton rapidity y도 표시한다.

## 가중치와 통계

- 기존 MCweight() 정의대로 `sign(genWeight) * xsec / processed_sumSign`에
  luminosity, PU 및 lepton SF를 곱한다. 부분 통계이므로 전체 sample의 sumSign이 아닌
  **실제로 처리한 이벤트의 sumSign**을 사용해 mass sample들을 합친다.
- NLO 음수 가중치를 버리지 않는다. sumw2와 normalization의 영향을 통계 오차에 포함한다.
- 모든 선택된 NLO 이벤트에서 `w_dy==1`을 검사한다. LO용 DY reweight,
  1jet→2jet 전달계수, charge-flip weight는 적용하지 않는다.
- 각 jet category의 히스토그램 면적을 독립적으로 1로 맞춘다.
  아래 ratio는 normalized 0jet/1jet, 2jet/1jet이다. Neff<20인 bin의 ratio는 숨긴다.
- |eta|>=6을 가장자리 표시 bin에 합치되, 평균값은 자르지 않고 계산한다.
  qT=0은 eta에서만 제외하고 개수를 기록한다. Systematic uncertainty는 포함하지 않는다.
- Framework가 읽는 correction 파일 중 `latest` 경로가 있다. 재실행 때 그 외부 파일이
  바뀌면 analyzer 결과가 달라질 수 있다. 저장된 NPZ에서의 재그리기는 원본 ROOT나 correction에 의존하지 않는다.

## 읽을 때 주의

`eta_ll = asinh(sqrt(mll^2+qT^2)/qT * sinh(y_ll))`.
따라서 낮은 qT에서 큰 |eta|가 나오는 것은 큰 longitudinal boost와 같은 뜻이 아니다.
0jet은 acceptance/threshold를 통과한 jet이 없다는 뜻이며 radiation이 없는 것은 아니다.
NLO generator sample에서 나눈 jet multiplicity 결과를 모든 jet bin이 각각 NLO 정밀도라는 뜻으로 사용하지 않는다.

## 결과와 재현

- [전체 숫자 및 통계 오차](AN_rawcharge/15_nlo_jetbin_z_direction/RESULTS.md)
- [EE, Z peak 80–100 GeV](AN_rawcharge/15_nlo_jetbin_z_direction/Zpeak/all_zpt/z_direction_EE.png)
- [MM, Z peak 80–100 GeV](AN_rawcharge/15_nlo_jetbin_z_direction/Zpeak/all_zpt/z_direction_MM.png)
- [EE, mll>=400 GeV](AN_rawcharge/15_nlo_jetbin_z_direction/highmass/all_zpt/z_direction_EE.png)
- [MM, mll>=400 GeV](AN_rawcharge/15_nlo_jetbin_z_direction/highmass/all_zpt/z_direction_MM.png)

ROOT와 NumPy가 있는 환경에서 이 chargeflip directory 안에서 실행:

```bash
python scripts/nlo_jetbin_z_direction.py
python -m unittest discover -s scripts -p 'test_*z_direction.py' -v
```

이벤트 생성은 `scripts/nlo_direction_batch.py` → `scripts/run_nlo_direction.sh`
→ `scripts/nlo_direction_events.py`. raw input 위치는 `--raw-base`로 변경할 수 있다.
플롯의 NPZ 입력과 출력은 `--dumps`, `--out-dir`로 지정할 수 있다.
