# 03. DY CR1 → CR2 closure (jet-pT 보정 R 의 m_ll 외삽 검증)

## 질문
R 은 DY CR (60 < m_ll < 150, Z peak 지배) 에서 구해 m_ll > 400 (boosted 200) 인 SR 에 적용한다. 이 m_ll 방향 외삽이 정당한가?
SR 은 blinded 라 직접 볼 수 없으므로 CR 을 둘로 쪼갠다: **CR1 = 60–100, CR2 = 100–150**. CR1 에서 R 을 구해 CR2 에 적용하고 CR2 의 WR mass 를 데이터와 비교.
AN2019_083 Fig. 27–30 대응. 요청 (2026-09-18): "WR 에서 DY CR1 에서 구한 다음 DY CR2 에 적용하는 플랏도 있을 텐데 그것도 첨부하고, WR mass 에 대해 resolve boost 모두".

## 이 폴더

| 하위 | 내용 |
|---|---|
| `scripts/make_dycr12_closure.py` | chihwan 이 9/17 에 써 둔 원본 (matplotlib). 프로덕션 완료 대기 중이라 미실행 상태였음 |
| `scripts/make_dycr12_closure_cutbased_style.py` | 이번에 쓴 것. 계산은 같고 그리기만 `plotter._draw` |
| `2024_matplotlib_first_version/` | 원본 스크립트의 출력 (처음 노트에 넣었던 것) + `closure.log` |
| `2024_cutbased_format/` | 최종본 8장 (`DYCR2_{Resolve,Boost}{EE,MM}_{beforeR,afterR}_plot.png`) + `dycr12_R_CR1.json` — 노트 Fig. 19, 20 |
| `prior_2022_2023_CR1_2_validation/` | **2026-07-29 의 이전 작업** (2022–2023, v13 analyzer) 사본. 원본: `AN-25-020/chihwan/output/CR1_2_validation/` |

## 2024 — 방법

입력: `HNWR/DYCRStudy_RFlav_DYCRSplit_WeightSystOnly/2024` (75 root, 9/17 00:52–12:14 에 완료). userflag `DYCRSplit` 가 쓰는 히스토그램:
```
DYCR_ZptOnly/Central/DYCR{1,2}_<Resolved|Boosted>_<EE|MM>_jetpt_mlljj   TH2: x = leading (fat)jet pT (10 GeV bin), y = m(lljj)/m(lJ) (50 GeV bin)
```
`DYCR_ZptOnly` variant = C×κ_EW 는 걸렸고 R 은 안 걸린 DY. (boosted 의 `mlljj` 는 이름만 그렇고 값은 m(lJ).)

1. CR1 의 2D 히스토그램을 x 로 projection, 전달 R 과 같은 bin (`RBINS`: resolved 40/100/200/400/600/800/2000, boosted 200/400/600/2000) 으로 rebin.
2. `R_CR1(bin) = (data − [TT+Nonprompt+Others]) / DY`, **ee+μμ 합쳐서** (AN2019_083 방식; `--flav` 를 주면 flavour 별).
3. `DY_CR2^corr(m) = Σ_x R_CR1(x) · DY_CR2(x, m)` — 2D 라서 jet pT bin 별 weight 를 mass 축으로 정확히 옮길 수 있다.
4. CR2 의 mass (`MBINS`: resolved 800/1000/…/3200/8000, boosted 800/1000/1200/1500/1800/8000) 에서 data vs stack, R 적용 전/후.
그룹 분류는 `config.classify_sample`, 데이터 stream 은 `config.CHANNELS[ch]["data"]` (EE→EGamma, MM→Muon) — 즉 플로터와 같은 (올바른) 정의.

## 2024 — 결과 (`closure.log`, 두 버전 수치 동일)

```
Resolved R_CR1 = [1.799 1.546 1.324 1.184 1.112 0.884]      (전달 R (ee+μμ): 1.808 1.533 1.311 1.167 1.066 0.866)
Boosted  R_CR1 = [1.307 1.201 1.058]                         (전달 R:          1.319 1.212 1.062)
CR2 data/MC   Resolved EE 1.266 → 1.016   Resolved MM 1.307 → 1.047   Boosted EE 1.471 → 1.282   Boosted MM 1.241 → 1.107
χ²/bins (matplotlib 버전 그림에 표기)  Resolved EE 222.6/9 → 6.2/9,  Resolved MM 399.6/9 → 29.6/9,  Boosted EE 58.8/5 → 28.1/5
```
- CR1 의 R 은 전체 DY CR 의 전달 R 과 1–4% 이내로 같다 (CR1 이 통계를 지배하므로 당연).
- resolved: 닫힌다. ee 는 mass 전 구간에서 ~1, μμ 는 2 TeV 위 bin 들이 1.3 근처 (통계 작음).
- boosted: 개선되지만 1.1–1.3 이 남는다. ee 는 여러 bin 이 ratio pad 위 (>1.5). CR2 boosted 는 채널당 데이터 수백 event.
  같은 방향의 증상이 ttbar study 의 boosted low-mass closure (1.45–1.52) 에도 있다.

## 그림 형식에 대한 경위
1. 처음: 원본 matplotlib 스크립트를 그대로 실행 → 좌(before)/우(after) 2-panel PDF 4장을 노트에 넣음.
2. 사용자 지적: "플랏 그린 건 그전에 그린 형식으로 그려, 새로운 형식으로 그리지 말고".
3. 수정: 같은 계산에서 그룹별 TH1 (값 + **분산**; 원본은 분산을 안 읽었다) 을 만들어 `plotter._draw(args, tot, hdata, group_hists, g_syst, g_ratio_band, g_ratio_stat, ...)` 호출.
   band 는 `chargeflip_plots.stat_graphs(tot)` = **MC stat only** (이 프로덕션의 syst 는 전파 안 함). after 의 DY 분산은 Σ R² · var.
   범례의 "Stat ⊕ Syst Unc." 문구는 `_draw` 에 고정이라 그대로 찍힌다 → 노트 캡션에 "statistical uncertainty of the simulation only" 라고 명시.
   ratio pad 0.5–1.5, x 축은 마지막 bin (…–8000) 까지.
4. 노트: Fig. 19 (resolved), Fig. 20 (boosted), 각 2×2 (좌 before / 우 after, 위 ee / 아래 μμ). 5.1.3 본문의 TODO 를 위 수치로 교체.

실행:
```bash
cd plot/cutbased
PLOT_EXTRA_BINDS="/tmp:/tmp" ./condor/in_container.sh python3 studies/DY/03_cr1_to_cr2_closure/scripts/make_dycr12_closure_cutbased_style.py --out <DIR>   # ~5분
```

## 2022–2023 (7/29) 과의 비교 — `prior_2022_2023_CR1_2_validation/README.md`

같은 질문, 다른 방법:
- 그때는 R 을 뺀 DY 가 디스크에 없어서 **`DYReshapeBinK_Up` variation 으로 R 을 제거/재적용**했다:
  `G_i = (H_BinK_Up − H_central)/σ_i` 가 lookup bin i 의 R-free 기여 → `H_before = Σ G_i`, `H_after(R′) = Σ R′_i G_i`.
  2024 는 analyzer 가 2D 히스토그램을 직접 쓰므로 (`DYCRSplit`) 이 우회가 필요 없다.
- 두 갈래 결과: (a) `jetpt_R/` — R(CR2)/R(CR1): resolved 1.032 ± 0.029 (전 bin 2σ 안), boosted 1.264 ± 0.141 (+1.9σ).
  (b) `mlljj/` — mass 축 전/후 (syst_plotter 형식). boosted 는 m(lJ) 기울기 잔존.
- 그때 발견한 analyzer 결함 2건 (README 에 기록): ① DYReshape nuisance off-by-one (Bin1 이 죽은 variation, 마지막 R bin 은 variation 없음),
  ② boosted R 의 lookup 변수 불일치 (적용은 `fatjets[0].Pt()`, 유도는 HNFatJet pT). **2024 analyzer (Nano15 HNWR.cc) 에서 고쳐졌는지는 이번에 확인하지 않았다.**
- 2024 boosted 의 잔여 비닫힘 (1.11–1.28) 이 7/29 의 boosted +26% 와 같은 방향이라는 점은 주목할 만하다.

## 하지 않은 것
- `--flav` (per-flavour R_CR1) 버전 — nominal 이 per-flavour R (`RFlav`) 이므로 해 볼 가치가 있다.
- syst band 전파, R_CR1 의 오차 전파.
- R(CR2)/R(CR1) 를 jet pT 축에서 직접 비교하는 그림 (7/29 의 `jetpt_R/` 대응).

## 2024 — 새 jet별 C (FxFx/LO, `ZptNJet`) 로 재실행 (2026-09-22) — `2024_ZptNJet/`

입력: DY = `SKNanoOutput_dy3gen/HNWR/DYCRStudy_DYCRSplit_ZptOnly_ZptNJet_WeightSystOnly` (C×EW, R 없음), data·non-DY = `DYCRSplit_NoDYCorr`
(symlink 세트 `closure_ZptNJet_inputs/2024`; 스크립트는 non-DY 가 `DYCR_ZptOnly` twin 을 안 가지면 `Central` 로 fallback). `scripts/run_closure_zptnjet.sh` (condor).
```
Resolved R_CR1 = [1.885 1.582 1.316 1.161 1.092 0.872]      (옛 C: 1.799 1.546 1.324 1.184 1.112 0.884)
Boosted  R_CR1 = [1.198 1.060 0.965]                         (옛 C: 1.307 1.201 1.058)
CR2 data/MC   Resolved EE 1.266 → 1.015   Resolved MM 1.306 → 1.046   Boosted EE 1.389 → 1.293   Boosted MM 1.169 → 1.103
             (옛 C:       1.266 → 1.016               1.307 → 1.047               1.471 → 1.282               1.241 → 1.107)
```
- CR2 closure 는 C 종류와 무관: resolved 는 1.5% 안에서 닫히고, boosted 는 여전히 1.1–1.3 이 남는다.
- boosted 의 before 값이 옛 C 보다 낮은 것 (1.47→1.39) 은 jet별 C 가 boosted 에서 이미 normalization 을 맞추기 때문 (09 번 §6.4).
- 이 검증은 m_ll 60–100 → 100–150 외삽만 본다. SR (m_ll>400) 방향 외삽과 m_lljj 의존 (`chargeflip/new_DYCR/README.md` §6: m_lljj<800 에서 R 이 안 맞음) 은 검증하지 않는다.
