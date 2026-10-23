# 08. C(pT | m(ll)) — m(ll) bin 별로 LO 에 normalize 한 Z-pT 보정과 theory error 재구현

## 요청 (2026-09-21)
"둘 다 HT > 40 에서 Z pT 는 50 부터. mll 별 normalization 은 LO 로 맞춘다 (어차피 LO 에 곱하고 LO 는 NNLO 로 스케일돼 있다).
mll bin 을 적당히 잘게 쪼개 NLO 를 LO 에 맞추고, 그 상태에서 mll 별 Z pT 값을 구한다. 그다음 theory error 를 제대로 구현 — 전엔 이상할 정도로 작았다."
"pdf unc 는 미리 한 번 돌려서 값을 얻어야 하지 않았나?"

배경은 `../06_nlo_lo_mll_njet/NOTES.md`: njet 분할은 MLM merging 때문에 인위적이라 보정에 못 쓰고, njet inclusive 로 두되 m(ll) 로 나누는 것이 맞는 방향.

## 한 것

**아날라이저** `HNWR/src/DYGenZpT.cc` (+ `.h`): 선택은 배포본과 동일 (Z→ee/μμ, `LHE_HT>40`, `FindGenZ`).
- `Zpt_mll_genZ_HT40` TH2 (x = gen Z pT: 0/50 부터 5 GeV –200, 10 –500, 50 –1000, …; y = gen m(ll) 22 bin). 기존 syst 루프의 모든 디렉토리에 채움.
- `Theory/Scale_{0..8}/`, `Theory/PDF_{0..102}/` 에 같은 TH2 를 **member 하나당 하나씩** (pT ≥ 50 만). NanoAOD 순서: Scale [4] nominal, [2]·[6] 은 반상관 쌍; PDF 0 central, 1–100 Hessian, 101/102 αS (LHA 325300–325402).
- smoke test (DYto2E_MLL6000toInf, reduction 20) 로 중첩 디렉토리와 `Central(pT≥50) = Scale_4 = PDF_0` 확인 후 본 제출.
  runlog `2026_09_21_001056_DYGenZpT`, 32 샘플 / 1099 job, 00:10 제출 → 01:23 완료, err 0.

**유도** `HNWR/scripts/make_dy_zpt_mll.py` (신규) → `HNWR/data/corrections/zpt/dy_zpt_nlo_lo_mll.{json,root}` + `plots/dy_zpt_mll_{slices,overlay}_2024`.
배포 중인 1D `dy_zpt_nlo_lo.*` 는 건드리지 않았고, `HNWR.cc` 의 lookup 도 그대로다 (적용은 미결정 — 아래).
- `C_m(pT) = [NLO/LO] / K_m`, `K_m = Σ_{pT≥50} NLO / Σ_{pT≥50} LO` (slice 별). 마지막 pT bin 은 >500 열린 bin → **`Σ LO·C / Σ LO = 1.000000` 이 모든 slice 에서 성립** (로그의 closure 줄).
- slice: 50/80/100/120/150/200/300/400/600/800/1000/∞. 1000–1500 과 >1500 은 최악 bin 통계오차 15% 로 자동 병합 (`--max-tail-err 0.10`, 최상위 slice 의 모든 pT bin 기준).
- theory: member 마다 같은 유도를 거쳐 C_X 를 만들고 (각자 자기 slice 에서 LO 에 normalize) **C 위에서 bin 별로** — scale 7-point envelope (k ∈ {0,1,3,5,7,8} − C_4), PDF Hessian √Σ(C_i−C_0)², αS (C_102−C_101)/2. 이전 방식 (4-point, per-event PDF) 도 같은 표에 "legacy" 로.

**PDF 사전 패스에 대해**: 기억하신 것은 `make_theory_norm_k.py` → `TheoryNormK.json` → `GetTheoryNormK` 로, **signal** 의 theory nuisance 가 acceptance 만 담게 하려고 Runs tree 의 `LHEPdfSumw` 로 inclusive 정규화를 미리 구하는 장치다 (background 는 표에 없음 — docstring).
여기서는 member 마다 slice 별로 LO 에 normalize 하므로 같은 일이 더 잘게 일어난다. K_var 로 또 나누면 이중이다. 따라서 불필요.

## 결과

### C 의 꼬리가 m(ll) 에 따라 크게 다르다
```
pT \ m(ll)   50-80  80-100 100-120 120-150 150-200 200-300 300-400 400-600 600-800 800-1000  >1000
250-350      0.899  0.908  0.950   1.037   1.051   1.066   1.080   1.104   1.066   0.955    0.815
350-500      0.809  0.821  0.859   0.958   0.978   1.001   1.051   1.063   1.036   0.959    0.825
>500         0.672  0.706  0.762   0.828   0.846   0.883   0.885   0.940   0.932   0.846    0.732
K_m          0.923  0.989  1.034   1.063   1.149   1.162   1.181   1.188   1.230   1.316    1.585     (나눠 없앰, 적용 안 함)
```
- 배포본 (inclusive = 사실상 80–100) 은 >500 에서 0.73. resolved SR (m_ll > 400) 에 맞는 값은 **0.93–0.94**, boosted (m_ll > 200) 는 0.88. 즉 지금은 SR 의 고-pT DY 를 ~25% 과하게 깎고 있다.
- Z peak 안에서도 움직인다 (50–80: 0.67, 100–120: 0.76) — DY CR 은 60–150 이라 CR 안에서도 단일 곡선이 아니다.
- >1000 slice 는 저 pT 에서 C 가 1.3 이상으로 튄다 (5 GeV bin 에 통계 4%). 고질량 slice 는 pT bin 을 더 굵게 잡아야 한다 — 미구현.
- K_m 은 0.92 → 1.59 로 올라간다. LO 에 맞추기로 했으므로 적용하지 않지만, LO 의 m(ll) 모양이 NLO 대비 고질량에서 낮다는 뜻이므로 기록해 둔다.

### theory error: 제대로 구현해도 작다 — 구현이 아니라 생성기 weight 의 한계
```
max |δC/C| [%]      50-80 80-100 100-120 120-150 150-200 200-300 300-400 400-600 600-800 800-1000 >1000
new  QCDScale        1.34  0.74   0.64    1.51    0.83    0.61    0.37    0.28    0.10    0.06    0.05
new  PDF (Hessian)   1.41  1.37   1.28    1.01    1.12    0.99    0.79    0.86    0.48    0.38    0.90
new  alpha_S         0.45  0.37   0.39    0.24    0.32    0.27    0.20    0.09    0.13    0.05    0.05
legacy QCDScale      1.26  0.61   0.64    1.10    0.52    0.38    0.23    0.13    0.09    0.05    0.03
legacy PDF           0.78  0.92   1.03    0.95    1.04    1.01    1.09    0.91    0.52    0.44    0.53
MC stat (max)        4.44  0.77   3.21    1.62    1.65    1.60    2.21    1.84    3.39    4.26    ~5
```
- 7-point 와 bin 별 Hessian 으로 바꿔도 ≤ 1.5%. Z peak 의 PDF 는 0.9 → 1.4% 로 커졌고 (per-event 방식이 shape 을 뭉갰던 것), scale 은 거의 그대로.
- variation 이 작은 게 아니라 **거의 전부 normalization** 이다: K_X/K_nom − 1 이 scale 에서 −6.7 ~ +3.9% (50–80), 그리고 m(ll) 에 따라 부호가 바뀐다 (muF=0.5: −6.7% → +1.7%). 이건 slice 별 normalization 이 의도적으로 없애는 성분이다.
- POWHEG 의 LHE scale weight 는 B̄ (inclusive) 를 재가중하고 hardest-emission 의 모양은 거의 안 건드린다. 그래서 pT *shape* 에 대한 weight 기반 band 는 생성기 구조상 작다. 꼬리를 1% 로 안다는 뜻이 아니다.

### 현실적인 크기: FxFx 와 POWHEG 의 차이 = 30%
배포 ROOT 파일에 v13 era (2022–2023, 분자 = aMC@NLO **FxFx**) 의 같은 variant `Zpt_hardproc_HT40` 이 seed 로 들어 있다. 정규화 규약이 달라 모양만 비교 (500–1000 / 100–120):
```
                 FxFx 2022  2022EE  2023  2023BPix    POWHEG 2024
inclusive          0.846    0.862   0.838   0.834        0.650
M50to120           0.841    0.862   0.832   0.837        0.637
M120to200          0.976    0.903   0.902   0.892        0.670
M200toInf          0.827    0.781   0.860   0.648        0.722   (FxFx 쪽 통계 작음)
```
- 같은 √s, 같은 계열의 LO 분모인데 **FxFx 의 꼬리가 POWHEG 보다 30% 높다** (0.845 vs 0.650). 2 jet 까지 NLO ME 가 있는 FxFx 가 이 영역에서 더 믿을 만하다.
- 방향이 m(ll) slice 결과와 같다: 2024 POWHEG 기반 C 는 고-pT 를 너무 깎는다.
- 따라서 C 의 꼬리에 대한 실질적 불확도는 weight band (1.5%) 가 아니라 이 생성기 차이 (~30%) 다.

## 결정이 필요한 것
1. 2024 의 C 를 무엇으로 할지: (a) 지금 1D POWHEG 그대로, (b) 이번 `C(pT | m_ll)`, (c) 2022–2023 FxFx 곡선의 모양을 2024 에 차용, (d) 2024 FxFx ntuple 확보 후 재유도. (b) 와 (c) 는 조합 가능.
2. C 의 shape systematic 을 generator 차이 (FxFx − POWHEG) 로 잡을지.
3. 적용하려면 `HNWR::LoadDYCorrections` / `FindBin` 의 2D lookup → `jet_pt_reweight` 재생산 → R 재유도 → HNWR 재생산. R 이 C 의 잔차를 CR 에서 흡수하므로 SR 효과는 C 변화보다 작게 나올 수 있다 — 돌려 봐야 안다.
4. K_m 의 m(ll) 의존 (0.92 → 1.59) 을 systematic 으로 둘지.
5. 고질량 slice 의 pT bin 을 굵게 (스크립트 개선).
