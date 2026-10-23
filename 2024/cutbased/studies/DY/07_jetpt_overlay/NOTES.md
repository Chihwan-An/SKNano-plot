# 07. R 의 양쪽을 겹쳐 본 그림 — (data − nonDY) vs DY MC, 4 개 영역

## 요청 (2026-09-20)
"jet pt reweight 도 jet pt 의 data − nonDY / DY MC 플랏을 직접 보고 싶어, 4 개 영역 다.
data − nonDY 한 거랑 DY MC 만 그린 거랑 겹쳐서, 서브플랏에는 ratio."

노트의 Fig. 16 은 R 곡선만 보여준다. 여기서는 몫이 아니라 **분자와 분모 자체**를 같은 축에 겹치고, 아래에 그 비 (= R) 를 놓았다.

## 스크립트
`HNWR/scripts/make_dy_jetpt_overlay.py` (신규). 입력 · 샘플 분류 · 뺄셈을 전부 `make_dy_jetpt_ratio.py` 에서 **import** 한다
(`collect`, `numerator_denominator`, `group_of`, `ratio`, `DISPLAY_EDGES`). 따라서 여기 그려진 곡선과 실제로 배포되는 보정이 어긋날 수 없다.
`SAMPLE_PREFIX` 만 모듈 전역으로 세팅해 준다 (`Skim_HNWR_`).

- 입력: `HNWR/2024` (data + non-DY), `jet_pt_reweight/ZptOnly_EWSF/2024` (DY, C×κ_EW 적용됨). meta 의 `dy_source` 와 동일.
- 위 패널: DY MC 빨강 step (+ MC stat 밴드), data − nonDY 검정 점. events/GeV 로 그려 가변 bin 왜곡 제거.
- 아래 패널: R = (data − nonDY)/DY, 그리고 **배포본 R** (`dy_jetpt_ratio.json` 의 rebinned) 을 파란 step 으로 겹침 → 교차검증.
- 두 가지 binning 을 각각 저장:
  - `rbins` — 배포 edge (`DISPLAY_EDGES`; resolved 40/100/200/400/600/800/2000, boosted 200/400/600/2000). fit 이 보는 것.
  - `fine` — 그 안의 모양을 보려고 더 잘게 (resolved 15 bin, boosted 9 bin).
- 첫 bin (0–40 / 0–200) 은 젯 pT 선택 아래라 DY 분모가 비어 있어 자동으로 버린다.

실행 (tamsa2, Nano15 env, ~1 분):
```bash
cd /data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers
python3 -u HNWR/scripts/make_dy_jetpt_overlay.py --out plot/cutbased/studies/DY/07_jetpt_overlay/plots
```
읽은 파일: data_e=16, data_m=16, dy=14, nondy_Others=20, nondy_TT=2, nondy_WJets=8.

## 결과 (2026-09-20)

배포 binning 에서의 R:
```
resolved EE  1.817 1.513 1.287 1.147 1.078 0.780
resolved MM  1.802 1.547 1.329 1.181 1.058 0.927
boosted  EE  1.385 1.245 1.130
boosted  MM  1.252 1.183 1.008
```
배포본 (`dy_jetpt_ratio.json`) 과 bin 마다 일치한다 — 파란 선이 점 위에 그대로 앉는다. 노트 Table 15 의 per-flavour 값
(resolved 마지막 bin ee 0.78 / μμ 0.93) 과도 맞는다.

fine binning 에서 보이는 것:
```
resolved EE  2.094 1.938 1.745 1.695 1.540 1.463 1.379 1.310 1.208 1.157 1.120 1.078 0.790 0.772 0.638
resolved MM  1.903 1.850 1.774 1.707 1.528 1.520 1.431 1.345 1.248 1.204 1.121 1.058 0.974 0.852 0.583
boosted  EE  1.493 1.597 1.278 1.258 1.263 1.213 1.148 1.060 1.097
boosted  MM  1.474 1.308 1.096 1.214 1.171 1.202 1.052 0.921 0.794
```
- **resolved 는 매끄럽게 단조 감소**한다 (40 GeV 의 ~2.0 에서 2 TeV 의 ~0.6). 배포 bin 안에서 계단이 튀지 않으므로 6 bin 이 모양을 제대로 잡고 있다.
- **첫 배포 bin (40–100) 안에서는 2.09 → 1.75 로 꽤 움직인다.** 평평하지 않은 구간을 한 bin 으로 덮고 있다는 뜻이고,
  그 bin 안의 젯 pT 분포가 CR 과 SR 에서 다르면 그만큼 어긋난다.
- **마지막 구간이 ee 와 μμ 에서 갈린다** (800–2000 에서 ee 0.78 / μμ 0.93, fine 으로 보면 ee 0.79/0.77/0.64 vs μμ 0.97/0.85/0.58).
  per-flavour R (`RFlav`) 을 쓰는 이유가 이것이다. 통계가 작아 (ee 마지막 bin 은 events/GeV 10⁻² 수준) 오차막대가 크다.
- **boosted 는 200–300 에서 1.5 로 시작해 1 로 내려온다.** 배포 bin 이 3 개뿐이라 첫 bin (200–400) 안의 1.49 → 1.28 변화를 1.385 하나로 덮는다.
  03 번의 boosted CR2 비닫힘 (1.11–1.28) 과 같이 볼 것.

## 남은 것
- fine binning 의 구조가 유의한지 (특히 resolved 첫 bin 안의 기울기, boosted 첫 bin) → 배포 edge 재조정 여부 판단.
  다만 edge 는 non-DY 오염 f = N/(D−N) 기준으로 정해졌다 (`make_nondy_contamination.py`) — 잘게 쪼개면 오염이 큰 bin 이 살아난다.
- 이 그림들을 노트에 넣을지 (Fig. 16 옆 보조 그림으로).

관련: [[../03_cr1_to_cr2_closure]], `HNWR/docs/DY_CORRECTIONS_EXPLAINED.md` §3, 노트 Fig. 16 / Table 15.
