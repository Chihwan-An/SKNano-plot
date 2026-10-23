# CR1 → CR2 전이 검증 (D6)

**질문.** jet-pT 보정 R은 DY CR(60 < m_ℓℓ < 150, Z 피크 지배)에서 유도해
m_ℓℓ > 200/400인 SR에 적용한다. 이 m_ℓℓ 외삽이 정당한가?

CR을 m_ℓℓ로 쪼갠다: **CR1 = 60–100, CR2 = 100–150** (`DYCR1_*`/`DYCR2_*`).
두 갈래로 답한다:

| 폴더 | 내용 | 스크립트 |
|---|---|---|
| `jetpt_R/` | CR1·CR2에서 R을 독립 유도해 R(CR2)/R(CR1) 비교 (jet-pT 축, 에러바) | `make_cr1_cr2_validation.py` |
| `mlljj/` | 판별 변수 축 보정 전/후: resolved m_lljj, boosted m(ℓJ), CR1(자체)·CR2(전이) | `make_cr1_cr2_mlljj.py` (jetpt_R 실행 후) |

`mlljj/`는 **syst_plotter 형식** (`plots/HNWR/reproduce/syst_plotter/integrated/
charge_inclusive_year_combined`의 EE.py + plotter.sh 그대로: CMS 스타일 스택,
Data/MC ratio, Stat/Stat⊕Syst 밴드, binning·축·라벨·네이밍 동일). 플랏에 χ²
표기는 없다 (수치는 run_log/json에만). boosted 히스토그램 이름은 `mlljj`지만
실제 채워지는 값은 `LeadLep + fatjet` 질량 = **m(ℓJ)** 다
(`Reproduce20_002_copy.cc:2091,2156`).

## 방법 핵심 — 재생산 없는 정확한 R 제거/재적용

보정 전 DY는 디스크에 없다. `DYReshapeBinK_Up` 변주가 해결한다: BinK_Up은
**R lookup bin i = K−1**의 이벤트만 σ_i 움직인 복사본이므로

```
G_i = (H_BinK_Up − H_central) / σ_i     ← lookup bin i의 R-프리 기여 (정확)
H_before = Σ G_i,   H_after(R′) = Σ R′_i G_i    (여기서 R′ = CR1-only R)
```

변주가 없는 마지막 bin은 잔여항으로 복원 (선택컷상 G₀ = 0). 히스토그램 축과
무관하게 성립하므로 mlljj 축에도, boosted의 lookup 변수 불일치에도 정확하다.
"after"의 Syst 밴드 = non-DY 규격화(TT 10%/Nonprompt 100%/Others 50%) ⊕
R_CR1 오차의 G-전파.

### 이 과정에서 발견한 analyzer 결함 2건 (별도 수정 필요)

1. **DYReshape nuisance off-by-one** — `GetJetPtR(..., b, d)`에 0-based `b`,
   이름은 `Bin{b+1}`. **Bin1은 NaN bin(0)을 겨냥한 죽은 변주**(=Central),
   **마지막 R bin(resolved 800–2000, boosted 600–2000)은 변주 없음** →
   데이터카드에 no-op nuisance 1 + 커버 안 되는 bin 1. (`.cc:3099-3117`)
2. **boosted R lookup 변수 불일치** — 적용은 `fatjets[0].Pt()`(LSF 무관 선두
   AK8), 유도 축은 HNFatJet pT. BinK_Up 변주가 축상 다른 bin으로 새는 것으로
   실증. resolved는 일치.

## 결과 (2026-07-29, **7/29 full 재생산(56/56, 15:29 완료) 기준**, 4 era 합)

### jetpt_R — R(CR2)/R(CR1): **전이 성립**

| 영역 | ⟨R2/R1⟩ | 비고 |
|---|---|---|
| resolved combined | 1.032 ± 0.029 | 전 bin 2σ 안, per-era 전부 일관 |
| boosted combined | 1.264 ± 0.141 | +1.9σ 규격화 오프셋, 통계 한계 |

CR2 data < 10인 bin은 비교에서 제외(open 마커). stat은 CR 간 독립, non-DY
xsec은 CR 간 correlated 전파. 정량 수치는 `jetpt_R/run_log.txt`.

### mlljj — 판별 변수 축 전/후 (data/MC)

- **resolved CR1** (자체): before가 이미 ~1 (새 프로덕션에서 DY 규격화가
  내려온 결과), after는 저질량 유지·고질량 +10–30% 위로 밀림 (EE 2800–3200
  bin 1.36).
- **resolved CR2** (전이): before·after 모두 저질량 ~1. EE 고질량 상승
  (before 1.3–1.6)은 after에서 커짐 (1.45–1.98) — 통계 한계 영역.
- **boosted CR1** (자체): before 0.8–0.9 → after 저질량 ~1 회복, 그러나
  **m(ℓJ) 기울기 잔존** (1500 GeV 위 1.3–1.45). fatjet-pT 기반 보정이 질량
  축 misshape를 다 못 잡음 — 결함 2와 무관하지 않을 수 있음.
- **boosted CR2** (전이): EE after 1.25–1.55 위로, MM after ~1 (1600–1800
  bin 0.70 제외). era당 데이터 52–159 이벤트라 통계 지배.

## 부수 발견 — 전달 R과 프로덕션의 불일치 (계속 미해결, **재생산 후 커짐**)

CR1+CR2로 재유도한 R이 `corrections/jetpt`의 전달 R보다 **~+5–19% (거의
uniform)** 높다 — 7/29 재생산에서 DY 수율이 한 번 더 내려가면서 7/28 대비
차이가 커지고 평평해졌다. 전달 R을 새 프로덕션 기준으로 재유도하지 않으면
datacard 정규화가 수 % 어긋난다. 수치: `jetpt_R/run_log.txt` sanity 2.

## 파일

```
make_cr1_cr2_validation.py   jet-pT R 유도·비교 → jetpt_R/
make_cr1_cr2_mlljj.py        판별 변수 전/후 (syst_plotter 형식) → mlljj/
jetpt_R/{cr1_cr2_validation.json, run_log.txt, plots/r_cr1_vs_cr2_{cat}_{era}}
mlljj/plots/{Resolve|Boost}DYCR{1|2}{EE|MM}_mlljj_{beforeR|afterR}_plot.{png,pdf}
mlljj/plots/*.tsv            플랏별 bin 표 (syst_plotter 열 구성)
mlljj/{cr1r_applied_mlljj.json, run_log.txt}
```

재실행: 각 스크립트를 `/data6/Users/achihwan/micromamba/envs/Nano/bin/python`으로
(validation → mlljj 순). DYMLL 재생산이 도는 중이면 끝난 뒤 돌릴 것.
