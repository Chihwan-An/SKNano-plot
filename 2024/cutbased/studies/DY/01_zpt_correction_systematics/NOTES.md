# 01. Figure 10 — Z-pT 보정 C 의 systematics 가 제대로 걸렸는가

## 질문 (2026-09-18)
"figure 10 에서 systematics 제대로 적용한 거 맞아? 너무 차이가 없는데?"
Fig. 10 = `dy_zpt_nlo_lo_2024.pdf` (이 폴더에 사본). Central 과 μR/μF/PDF/αS up·down 9개 곡선이 전부 겹쳐 보인다.

## 확인 순서

1. **그림 출처**: `HNWR/data/corrections/zpt/plots/dy_zpt_nlo_lo_Zpt_genZ_HT40_2024.pdf` ← `HNWR/scripts/make_dy_zpt_nlo_lo.py` (811줄).
   입력은 `DYGenZpT/2024` 의 `<syst>/<variant>` 히스토그램, syst ∈ {Central, ScaleWeight_mu{R,F}_{Up,Down}, PDF_{Up,Down}, AlphaS_{Up,Down}}.
   설계 (스크립트 docstring): "LO is held fixed; the systematic band comes entirely from theory variations of the NLO numerator".
2. **weight 가 실제로 걸렸나**: 스크립트 끝에 sanity 출력이 있다 — variation 별 NLO 총 yield 편차, 0 이면 "identical to Central, weight likely not applied" 를 붙인다.
   `run_log_zpt.txt` (사본) 568–576행, `Zpt_genZ_HT40`:
   ```
   LO=6.976e+07  NLO=4.986e+07  K=0.7148
   ScaleWeight_muR_Up -1.20%   muR_Down +1.49%   muF_Up +3.08%   muF_Down -5.01%
   PDF_Up +4.21%   PDF_Down -4.21%   AlphaS_Up +1.38%   AlphaS_Down -1.67%
   ```
   → weight 는 적용돼 있다. 경고 flag 없음.
3. **그럼 왜 안 보이나**: C 는 **shape-only** 로 정규화된다 (`meta.normalization = "shape-only"`, `norm_min_pt_gev = 50`).
   각 variation 곡선도 같은 방식으로 pT>50 에서 DY yield 를 보존하도록 정규화되므로, 위의 −5~+4% 는 대부분 (pT 에 평평한 normalization 성분) 나눠져 없어진다.
   남는 것은 variation 이 pT 에 따라 다르게 작용하는 부분뿐.
4. **남는 크기를 JSON 에서 직접 계산** (`check_zpt_syst_size.py` → `.out`):
   ```
   QCDScale      max|up| 0.87%  max|down| 0.49%   꼬리 3 bin: up [0.46 0.61 0.87]  down [-0.25 -0.32 -0.49]
   QCDPDFError   max|up| 0.82%  max|down| 0.89%                up [-0.67 -0.77 -0.82] down [0.73 0.84 0.89]
   QCDPDFAlphaS  max|up| 0.25%  max|down| 0.53%                up [-0.14 -0.20 -0.25] down [0.32 0.42 0.53]
   TOTAL         max 1.36%                                     ±[0.92 1.12 1.36]
   MC stat (꼬리 3 bin) [0.17 0.33 0.68] %      C = [0.922 0.840 0.733]
   ```
   → 최대 1.4% (500–1000 GeV bin). y축 0–1.8 인 그림에서는 선 굵기 안이다. **버그가 아니라 정규화 방식의 결과.**

## 덧붙인 판단 (band 가 작게 잡힐 수 있는 요인)

- QCD scale 은 μR, μF 를 **따로** 움직인 4점의 envelope 이다 (`SCALE_DIRS`). 같이 움직이는 (2,2), (0.5,0.5) 는 없다 — 7-point 가 아님. 보통 shape 효과는 상관 변화에서 더 크다.
- LO 분모는 고정 (LO 의 scale 불확도는 band 에 없음).
- shape-only 를 끄는 옵션은 `--absolute` (inclusive K-factor 유지). 그러면 variation 이 수 % 로 보이지만, DY 의 전체 rate 는 fit 의 `R_DY_*` rateParam 이 띄우므로 normalization 성분을 nuisance 로 또 넣으면 중복 방향이 생긴다 — shape-only 선택 자체는 합리적.
- 그림에 variation/central 비율 패널을 달면 1% 가 보이게 할 수 있다 (제안만 하고 그리지는 않았다).

## 관련: C 의 분자가 POWHEG 라는 점
C 는 gen-level Z pT 의 비율이라 ME jet 수의 영향이 작지만, 같은 POWHEG 샘플을 reco-level mlljj 비교에 쓰면 크게 어긋난다 (→ `../04_nlo_pseudodata/`).
HT^LHE>40 요구 때문에 pT≲50 에서 분자가 비는 것도 같은 원인 (POWHEG 는 LHE parton 이 최대 1개라 HT^LHE ≈ Z pT).
