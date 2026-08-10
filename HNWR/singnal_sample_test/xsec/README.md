# xsec — (m_WR, m_N) 이론 cross section 맵 + "최소 N event" 경계선

`xsec_mass_grid.py` 는 `data/Run3_v12_Run2_v9/2022/Sample/CommonSampleInfo.json` 의
`WR{m_WR}N{m_N}{EE,MM}` 샘플 xsec 만 써서 (acceptance 는 안 쓴다) 다음을 그린다.

* x = `m_WR`, y = `m_N`, color = σ [fb] (log scale). 7개 m_WR column(2–8 TeV, 1 TeV 간격) ×
  m_N = 100 GeV ~ m_WR−100 GeV(100 GeV 간격), 총 343 point.
  보간은 `(m_WR, m_N/m_WR)` 좌표에서 log σ 선형보간 — kinematic edge 왜곡을 줄이기 위해서다.
  **EE 와 MM 의 xsec 은 완전히 동일**하므로 그림은 한 장이면 된다.
* 빨간 실선 = 500 fb⁻¹, 빨간 파선 = 137 fb⁻¹ 에서 μ = σ·L = **3** 이 되는 경계.
  선의 **아래/왼쪽이 μ ≥ 3** 영역이다.
* 옅은 빨간 점선 = μ = 1 (최소 1 event) 경계. 참고용.
* 검은 실선 + 빗금 = **Run 2 observed 95% CL exclusion** (CMS, 138 fb⁻¹ @ 13 TeV).
  HEPData 114866 Figure 7 (`e.json` = e channel = EE, `mu.json` = μ channel = MM) 의
  `values[i].y[0]` (observed UL on σB / theory) 이 1 이 되는 등고선. 빗금 안쪽이 배제 영역.
  이 표는 채널별로 값이 다르므로 **exclusion 때문에 EE/MM 그림이 갈린다** (xsec 자체는 동일).
  표의 격자는 m_WR 800–6000 (200 GeV), m_N 200 ~ m_WR−200 (200 GeV) 라 m_N < 200 GeV 와
  kinematic edge 바로 아래는 데이터가 없어 선이 거기서 끊긴다 (외삽하지 않는다).
* Poisson 통계오차 띠는 **기본으로 안 그린다** (`--bands` 로 켠다). 관측 n = 3 의
  Garwood central interval 기준: 1σ → μ ∈ [1.367, 5.918], 2σ → μ ∈ [0.596, 8.902].
  띠를 끄더라도 `_boundary.csv` 에는 ±1,2σ 경계가 그대로 들어간다.

## 실행

```bash
cd plots/HNWR/singnal_sample_test/xsec
python xsec_mass_grid.py                    # n=3, EE, μ=1 점선 포함
python xsec_mass_grid.py --n-target 1       # 기준을 1 event 로
python xsec_mass_grid.py --n-thin 0         # 옅은 점선 끄기
python xsec_mass_grid.py --bands            # Poisson stat 1/2 sigma 띠 켜기
python xsec_mass_grid.py --channel MM       # MM (exclusion 이 채널별로 다르다)
python xsec_mass_grid.py --no-limit         # Run 2 observed exclusion 빼기
python xsec_mass_grid.py --points           # sample mass point 흰 점 표시
```

출력: `xsec_mass_grid_n{N}_{CH}.png/.pdf`, `xsec_mass_grid_n{N}_{CH}_boundary.csv`
(CSV = m_WR column 별로 μ = 3 / ±1σ / ±2σ 가 되는 m_N, 빈 칸이면 그 column 은 전 m_N 구간이
그 level 을 통과).

## μ = 3 경계 (m_N, GeV)

| m_WR | 500 fb⁻¹ (1σ 범위) | 137 fb⁻¹ (1σ 범위) |
|---|---|---|
| 2000 | 전 구간 통과 | 전 구간 통과 |
| 3000 | 전 구간 통과 | 전 구간 통과 |
| 4000 | 전 구간 통과 | 3811 (3710 – kin. edge) |
| 5000 | 4676 (4518 – 4810) | 4313 (3975 – 4562) |
| 6000 | 5105 (4664 – 5429) | 4015 (2655 – 4795) |
| 7000 | 4537 (2907 – 5512) | 1325 (514 – 3401) |
| 8000 | 1625 (900 – 3378)  | 438 (– – 1055) |

즉 500 fb⁻¹ 이면 m_WR ≤ 4 TeV 는 m_N 전 영역에서 3 event 이상이 나오고, 8 TeV 에서는
m_N ≲ 1.6 TeV 로 제한된다. 137 fb⁻¹ 에서는 8 TeV 에서 m_N ≲ 0.44 TeV 뿐이다.
(acceptance × efficiency 를 곱하면 이보다 훨씬 줄어든다 — `../xsec_x_eff/` 참고.)
