# 11. boosted 용 jet 카테고리: AK8 GenJet 으로 나눈 FxFx/LO Z pT 모양 (2026-09-22)

질문: jet별 C 는 AK4 GenJet (pT>40) 수로만 나눴다. boosted (fat jet 1 개, resolved 실패) 는 따로 봐야 하지 않나?
그냥 inclusive 와 차이가 많이 나나 (resolved / boosted 둘 다)?

## 한 것
`DYGenZpT` 에 AK8 GenJet 카테고리 추가 (raw branch `nGenJetAK8`, `GenJetAK8_{pt,eta,phi}`; pT > 200, |η| < 2.4, hard-process 렙톤과 ΔR > 0.8):
`Zpt_mll_genZ_HT40_GenFJ1` (≥1 AK8), `_GenFJ0`, `_GenFJ1x` (≥1 AK8 **이고** AK4 GenJet < 2 = resolved topology 실패), `_GenJ2noFJ` (AK4 ≥2, AK8 없음).
theory member 는 `GenFJ1`, `GenFJ1x` 에 채움. 프로덕션 `SKNanoOutput_dynew/DYGenZpT/2024` (LO 14 + FxFx 2, batch `DYGenZpT_fj_*`).
그림·표: `make_zpt_fatjet_compare.py` → `plots/zpt_shape_ratio_by_jetcat_{mll60to150,mllAll,mllGt400}_2024.png`, `zpt_abs_ratio_by_jetcat_*`, `run.log`, json.

## 결과 (m_ll 60–150, FxFx/LO shape ratio; K = 절대 FxFx/LO, fracLO = LO 이벤트 중 비중)
```
cat            K   fracLO   0-50 50-100 100-150 200-250 300-350 400-450 500-600 600-700 700-800 800-1000 1000-1500
Incl        1.023  100%     0.90  1.06   1.22    1.20    1.15    1.10    1.06    1.00    0.94    0.89     0.86
GenJ2       1.292   10.8%   1.00  1.00   1.00    0.98    0.94    0.89    0.84    0.80    0.78    0.70     0.66
GenFJ1      1.171    1.7%   1.02  1.01   1.00    0.99    1.00    0.97    0.92    0.88    0.82    0.78     0.75
GenFJ1x     1.160    0.5%   1.02  1.04   1.04    0.99    0.97    0.94    0.93    0.87    0.72    0.79     0.84
GenJ2noFJ   1.306    9.6%   0.99  1.00   1.01    1.06    1.02    1.05    0.87    (FxFx 통계 소진)
```
- **GenFJ1 (fat jet ≥1) 은 GenJ2 와 같은 꼴** — 400 GeV 까지 1.00, 그 위에서 떨어짐. 다만 GenJ2 보다 완만하다: 500–600 에서 0.92 vs 0.84,
  800–1000 에서 0.78 vs 0.70 (8–10%). Incl 과의 차이는 15% (500–600: 1.06 vs 0.92).
- **exclusive 정의 (GenFJ1x) 는 GenFJ1 과 통계 안에서 같다** (LO 의 0.5% 뿐이라 700 GeV 위는 흔들림). 굳이 exclusive 로 나눌 이득이 없다.
- GenJ2noFJ 는 500 GeV 위에서 FxFx 통계가 없다 — 고-pT 의 ≥2 jet 이벤트는 대부분 fat jet 도 같이 있다.
- normalization: K_GenFJ1 = 1.17 (GenJ2 1.29, Incl 1.02). 이 차이는 shape-only 정규화 + R + rateParam 이 흡수.
- m_ll > 400 은 FxFx 통계가 부족해 (GenFJ1 이 LO 의 9.6%, bin 오차 10–30%) 판단 불가.

## reco 와의 대조 — boosted 의 진짜 문제
reco boosted DY CR 의 FxFx/LO (무보정, pT(ll) 200–700) 는 **0.94 / 0.88 / 0.88 / 0.87, 합 0.875** 인데, gen GenFJ1 의 절대비 (K × shape) 는 같은 pT 에서 1.17 → 1.03 이다.
gen 에서는 FxFx 가 LO 보다 10–17% **많고** reco 에서는 12% **적다** → 약 25% 가 boosted reco 선택 (fat jet 재구성·substructure·LSF 등) 에서 생긴다.
resolved 는 gen (Incl 절대비 1.17→1.02) 과 reco (1.20→1.12) 가 비슷하다. 즉 boosted 에서 generator 차이의 대부분은 Z pT 나 gen jet 수가 아니라
**fat jet 을 만드는 방식 (MLM 4-parton vs NLO+shower) 의 차이** 이고, 그것은 C 로는 못 잡고 boosted R 과 `R_DY_Boosted` 가 흡수한다.

## 결론
- boosted 용 C 를 AK8 카테고리로 따로 만들 필요는 크지 않다: GenFJ1 의 모양은 GenJ2 와 10% 안이고, 그 차이는 R 이 흡수한다.
  분류를 바꿔 얻는 것보다 (LO 0.5–1.7% 의 통계, 코드 분기) 비용이 크다.
- boosted 에서 남는 문제는 reco 선택 단계의 generator 차이 (~25%) 이고, 이것은 boosted R 의 유도 영역 (DY CR) 과 SR 이 같은 fat jet 선택을 공유한다는 가정에 기대고 있다.
  검증하려면 FxFx pseudo-data 의 boosted CR vs SR (10 번 §B: 0.94 → 0.91, 3%) 이 지금 있는 유일한 근거다.
