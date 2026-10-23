# 04. AN2019_083 Appendix J 의 2024 재현 (옛 eμ data-driven 방법)

참고문헌: `/data9/Users/achihwan/AN/AN-26-120/example/AN2019_083_v21.pdf`, App. J = 인쇄 p.143–153 (PDF p.145–155 이후).
**이것은 AN 의 최종 방법이 아니다.** 최종은 §5.2 의 simultaneous fit (→ 02, 03). App. J 는 이전 분석의 방법:

    N_tt(same flavor) = [ N_data(eμ) − N_other bkg^MC(eμ) ] × R_{ee,μμ/eμ}        (AN Eq. 6)

여기서 구한 R 이나 closure uncertainty 는 fit 에 들어가지 않는다. 사용자의 요청 ("Appendix J 플랏을 그대로 따라") 에 따라 cross-check 로 재현했다.

입력·region·weight 는 `../01_inputs_and_selection/NOTES.md`. 이 폴더:
`scripts/` (생성 코드 2개), `hists/` (중간 히스토그램 ROOT + 로그; `_wrongnominal` 은 weight 함정 전 버전), `plots/` (그림 20 + JSON), `tables/` (tex 표 2개).

## AN 의 그림/표 ↔ 여기 산출물

| AN2019_083 | 내용 | 2024 산출물 |
|---|---|---|
| Table 54 | flavor sideband 의 signal/배경 (%) | `tables/signal_contamination_2024.tex` |
| Fig. 97 | resolved SR/eμ 비율 (tt MC), low/high, 상수 fit | `plots/ratio_resolved_{low,high}.png` |
| Fig. 98 | boosted μ-jet: μμ/eμ | `plots/ratio_boosted_mujet_{low,high}.png` |
| Fig. 99 | boosted e-jet: ee/μe | `plots/ratio_boosted_ejet_{low,high}.png` |
| Table 55 | 상수 fit 결과 | `tables/emu_ratio_fit_2024.tex` |
| Fig. 100–102 | eμ sideband data vs MC, low/high | `plots/{Res_EM,Boost_EMJ,Boost_MEJ}_{low,high}.png` |
| Fig. 103–104 | low-mass same-flavor 영역, data-driven tt | `plots/lowmass_dd_{Res,Boost}_{EE,MM}.png` |
| Fig. 105–128 | obs/pred, eμ syst 5–60% | `plots/obs_pred_{Res,Boost}_{EE,MM}.png` (각 12 panel) |

AN 은 연도 3개 × 패널이지만 여기는 2024 하나. AN 의 low-mass 그림은 사실상 1-bin 인데, 여기서는 200–800 을 100 GeV bin 으로 그렸다.
그림 형식: stack 은 기존 `plotter._draw` (CMS 헤더, ratio pad 0.5–1.5). 비율 / obs-pred 그림은 plotter 에 없는 종류라 AN 스타일을 ROOT 로 그렸다.

## 1. 비율 R (tt+tW MC) — Table 55 대응

`R(m) = TT[same-flavor region](m) / TT[eμ sideband](m)`, TH1::Divide (분자·분모는 같은 MC 샘플의 서로 다른 event 라 독립), `pol0` fit.
TT 는 ttbar+tW 그룹 (AN 은 "tt MC" 라고 쓰지만 범례는 tt+tW 이고, 뺄 "다른 배경" 에 tW 가 없으므로 같은 정의로 봤다).
boosted 짝은 **AN 방식** (jet 안 lepton flavor 유지): μμ ↔ e+μ-jet (`Boost_EMJ`), ee ↔ μ+e-jet (`Boost_MEJ`).

| | resolved ee/eμ | resolved μμ/eμ | boosted ee/μe | boosted μμ/eμ |
|---|---|---|---|---|
| m > 800 | 0.450 ± 0.003 (χ²/ndf 10.8/8) | 0.629 ± 0.003 (28.2/8) | 0.937 ± 0.012 (5.0/4) | 1.212 ± 0.014 (0.3/4) |
| m ≤ 800 | 0.449 ± 0.001 (13.8/5) | 0.600 ± 0.001 (27.2/5) | 0.937 ± 0.004 (18.3/5) | 1.182 ± 0.004 (28.6/5) |

Run 2 (2018) 값과 비교: resolved 0.432/0.651 (high), boosted 0.815/1.271. 같은 크기. ee/eμ ≈ 0.45 < 0.5 는 electron 효율이 muon 보다 낮아서,
μμ/eμ > 0.5 는 그 반대. boosted 가 1 근처인 것은 분모도 "tight 1 + jet 안 loose 1" 구조라 조합 인자 2 가 없어서.
상수 fit 의 χ² 가 나쁜 곳 (resolved μμ, low-mass boosted) 은 비율이 질량에 따라 수 % 올라간다. low/high 차이는 5% 이내.

(weight 수정 전 값은 0.460/0.626/0.934/1.233 — 비율이라 거의 안 변했다.)

## 2. signal contamination — Table 54 대응

high-mass sideband 에서 `signal yield / 전체 배경 MC` (%). ntuple 에 있는 signal 은 28점 (ee 14, μμ 14; mWR 1–7 TeV, mN = 200 또는 mWR/2).
signal weight 도 `weight_Central`, 배경과 같은 정규화 (σ×L) 라고 가정했다 (따로 검증하지 않음).

요점:
- resolved eμ, 그리고 "signal lepton 과 jet 안 lepton flavor 가 다른" sideband: mWR ≥ 3 TeV 에서 < 0.1%.
- **ee signal 은 e+μ-jet sideband 에 들어간다**: (2000,200) 3.52%, (2000,1000) 3.91%, (3000,200) 0.56%, (3000,1500) 0.71%, (4000,·) 0.12%.
  μμ signal 은 μ+e-jet 에: (2000,200) 1.10%, (2000,1000) 1.46%, (3000,200) 0.04%. N 후보 jet 안의 nonprompt 반대-flavor lepton 때문.
- mWR = 1 TeV (이미 배제된 질량) 에서는 36% / 24% 까지.
- 의미: production card 는 ee SR 을 e+μ-jet CR 에 묶는데 (02 §2), 바로 그 CR 이 ee signal 로 오염된다. AN 방식 짝에서는 ~0.01%.
  card 의 CR 에는 signal process 가 없으므로 이 오염은 현재 모델에서 무시되고 있다. 3 TeV 이상에서는 1% 미만이라 실질 영향은 작다.

## 3. eμ sideband data vs MC — Fig. 100–102 대응

band = MC stat ⊕ weight 형 syst (각 syst 의 max(|up−nom|,|down−nom|) 를 bin 별로 quadrature 합; 그룹 합에 대해 계산).
JES/JER/scale/res 는 이 ntuple 의 CR 에 없어서 빠져 있다 (01 §4).

- resolved eμ high-mass: data/MC 가 질량에 따라 **0.95 → 1.02 → 1.10 → 1.19 → 1.12 → 1.42 → 1.35 → 1.33 → 1.20** (bin 순).
  전체로는 1.04 (card 기준 3623/3469). β 하나로는 못 잡는 shape. top-pT 모델링 또는 JES 후보 — 미조사.
- low-mass / boosted 는 그림 참조.

## 4. low-mass closure — Fig. 103–104 대응

`tt_dd(m) = [data_eμ(m) − (DY+Nonprompt+Others)_eμ^MC(m)] × R_low` (bin 별 shape 은 eμ 데이터에서, R 은 상수).
prediction = tt_dd + same-flavor 영역의 DY/Nonprompt/Others MC. (`plots/emu_method_2024.json` 의 `lowmass_closure`.)

| region | R_low | obs/pred 전체 | bin 별 (200–800, 100 GeV) | tt_dd / tt_MC | tt_dd 비중 |
|---|---|---|---|---|---|
| Res_EE | 0.4495 | 1.017 | 0.61, 0.94, 0.98, 1.04, 1.03, 1.08 | 0.913 | 0.80 |
| Res_MM | 0.6001 | 1.075 | 0.89, 1.04, 1.05, 1.08, 1.09, 1.11 | 0.913 | 0.80 |
| Boost_EE | 0.9374 | 1.521 | 1.08, 1.36, 1.66, 1.68, 1.51, 1.54 | 1.192 | 0.30 |
| Boost_MM | 1.1821 | 1.452 | 1.24, 1.70, 1.62, 1.36, 1.24, 1.17 | 1.175 | 0.38 |

원자료 (obs / pred / tt_dd / tt_mc, bin 순):
```
Res_EE   obs [5,1887,5321,5579,4322,3087]   pred [8.1,2011.1,5435.1,5368.5,4179.2,2863.7]  tt_dd [7.1,1631.1,4420.8,4312.2,3279.8,2173.0]  tt_mc [7.4,1851.1,4975.4,4803.0,3426.4,2271.7]
Res_MM   obs [10,2805,7575,7712,6023,4180]  pred [11.3,2690.8,7205.3,7133.0,5516.9,3766.1] tt_dd [9.4,2177.6,5902.1,5757.1,4378.8,2901.1]  tt_mc [10.5,2474.8,6616.0,6357.3,4604.6,3082.1]
Boost_EE obs [1495,5883,9109,5701,3068,1746] pred [1383.9,4329.3,5482.9,3399.4,2025.4,1130.1] tt_dd [413.0,1310.9,1583.2,932.6,636.7,374.0]  tt_mc [128.9,784.6,1453.2,1065.3,620.7,352.7]
Boost_MM obs [142,3779,9995,6677,3731,2137]  pred [114.8,2223.1,6165.9,4901.3,2997.1,1820.0] tt_dd [37.6,823.8,2202.6,1878.5,1177.8,744.3]   tt_mc [40.2,847.2,1985.2,1526.5,917.5,525.3]
```
해석:
- resolved: 닫힌다. 300 GeV 이상 모든 bin 이 0.94–1.11. 첫 bin (200–300) 은 event 5–10 개라 통계적으로 무의미.
  low-mass 에서 MC 의 tt 는 데이터 기반보다 9% 많다 (tt_dd/tt_mc 0.91). obs/pred 가 질량에 따라 0.94→1.08 로 완만히 오르는 경향은 있다.
- boosted: 1.45–1.52 로 안 닫힌다. 그런데 tt_dd 는 예측의 30–38% 뿐이고 나머지는 DY + Nonprompt MC 다. tt_dd 에 60% 를 줘도 예측은 20% 만 움직인다.
  → eμ 방법의 문제가 아니라 **low mlJ 의 DY / nonprompt 모델링** 문제로 읽었다. DY 쪽 boosted CR2 closure (1.28 / 1.11) 와 같은 방향.
  (이 ntuple 의 DY 가 어떤 보정 상태인지 — column `dy_jetpt_r` 가 있는 것으로 보아 R 포함으로 추정 — 는 확인하지 않았다.)

## 5. eμ syst scan — Fig. 105–128 대응

panel 마다 X = 5,10,…,60%. 주황 = 예측의 stat 오차 / pred, 회색 = √(stat² + (X% × tt_dd)²) / pred, 점 = obs/pred (오차 √obs/pred).
- resolved: 300 GeV 이상 전 bin 을 덮는 최소값은 **15%** (tt_dd 비중 0.8 × 15% = 12%; 최대 편차 +11%). Run 2 는 20%.
- boosted: 60% 까지 어떤 값도 못 덮는다 (위 이유). Run 2 는 30%.

## 6. 스크립트 구조 메모

`make_emu_method_hists_2024.py`: 파일 × region 마다 `ROOT.RDataFrame(tree, file)` 하나, `Filter` (low/high) → `Define mfit` (overflow fold) →
`Histo1D` 를 nominal + syst weight 별로 book, 한 번에 실행 (`EnableImplicitMT(8)`). 출력 key = `<region>/<low|high>/<group>[_<syst>_Up|Down]`, `data_obs`, `sig_<point>`.
signal 은 flavor sideband 에서만, same-flavor high-mass 데이터는 읽지 않음.

`make_emu_method_plots_2024.py`: (1) 비율+fit → `OUT["ratio_fit"]`, (2) sideband stack (`draw_stack` = `plotter._draw` 래퍼, `config.BACKGROUND_GROUPS` 를 임시 교체해 범례 변경),
(3) closure + scan, (4) 표 2개 + JSON. 시행착오: 히스토그램 누적을 `nom.Add(h) or nom` 으로 썼다가 `Add` 가 True 를 반환해 bool 이 되는 버그 → `acc()` 헬퍼로 교체.
