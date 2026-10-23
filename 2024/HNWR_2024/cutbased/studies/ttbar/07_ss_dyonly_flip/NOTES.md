# 07. SS 를 DY 만 charge-misID 로 추정하기 (2026-09-22)

## 제안

현재 EE same-sign 템플릿(`--ddss`)은

```python
# chargeflip_ddss.py
os_  = sel & isdata & ~d["ss"]     # OS 데이터 전체
Flip = fill(m_lljj[os_], w)        # 전부에 flip weight 를 곱함
```

즉 **OS 데이터 전체**에 flip 확률을 곱해 SS 를 예측한다. 그런데 resolved EE SR 의 OS 구성은
**TT 1413 vs DY 752** 로 ttbar 가 더 많다. 그래서 `Flip` 템플릿의 대부분이 ttbar 에서 오는데
그 부분이 β(`R_TT_Resolved_2024`) 보정을 전혀 안 받는다.

ttbar 가 이제 eμ flavour CR 로 잘 정규화되므로(03 §4), **charge-misID 는 DY 에만 쓰고 ttbar 는
MC × β 로 가져오자**는 것이 제안이다.

## 구현 (`chargeflip_ddss_dyonly.py --dy-only`)

```
Flip_DY = (OS 데이터 − 비DY OS MC) × w        # 같은 per-event weight 로 MC 차감
TT / Nonprompt / Others in SS = 전체 SS MC (flip + non-flip)   ← R_TT_Resolved_2024 가 TT 를 스케일
DYJets in SS = non-flip 만                    # flip 은 Flip_DY 에 들어 있음
```

## 시행착오 — MC 의 flip rate 에는 SF 가 안 들어 있다

그대로 돌리면 SR 예측이 **13.9% 줄었다** (136.8 → 117.8). 원인을 찾으려고 두 수를 비교했다:

```
데이터 기반으로 차감한 비DY flip : 56.9
MC 가 자체적으로 가진 gen-flip 비DY SS : 37.9
비율 56.9 / 37.9 = 1.50
```

그리고 method json 의 측정된 flip SF 가 **barrel 1.458 ± 0.038 / endcap 1.468 ± 0.024**
(pair 범주로는 BB 1.426 / EE 1.451 / BE 1.454) 다. **1.50 ≈ SF.**

즉 SF 는 "데이터/MC charge-flip rate" 이고 데이터 기반 예측에는 이미 들어가 있지만, raw SS MC
에는 안 들어가 있다. `--dy-only` 가 TT 를 raw MC 로 가져오면 정확히 그 SF 만큼 적게 센다.
→ gen-flip 된 MC event 에 flip 된 전자의 region SF 를 곱하도록 고쳤다 (`flip_sf_weight`).
`--no-flip-sf` 로 끄고 비교할 수 있다.

## 결과 — 두 방법이 1% 안에서 일치한다

`rEESR_SS` (SR, m_lljj 800-8000, an2 edge 3132)

| 성분 | baseline (현행) | DY-only | **DY-only + flip SF** |
|---|---|---|---|
| Flip (데이터 기반) | 95.2 | 38.3 | 38.3 |
| TT | 5.7 (non-flip 만) | 39.8 | **55.7** |
| DYJets | 8.7 | 8.7 | 8.7 |
| Nonprompt | 14.6 | 14.7 | 14.7 |
| Others | 12.6 | 16.3 | 18.1 |
| **합계** | **136.8** | 117.8 (−13.9%) | **135.4 (−1.0%)** |

`rDYEECR_SS` (SS DY CR — **실데이터가 있는 closure 영역**)

| | baseline | DY-only | DY-only + flip SF |
|---|---|---|---|
| 예측 | 1104.0 | 1090.3 | **1104.6** |
| 데이터 | 1174.0 | 〃 | 〃 |
| **data/pred** | **1.063** | 1.077 | **1.063** |

**비DY flip: 데이터 기반 차감 56.9 vs MC gen-flip × SF 55.5 — 2.5% 일치.**

## 해석

1. **두 방법이 같은 답을 준다.** SS 예측이 SR 에서 1.0%, DY CR closure 에서 소수 셋째 자리까지
   같다. Z peak 에서 잰 SF 가 ttbar 가 지배하는 SR 까지 제대로 전달된다는 뜻이고,
   charge-flip 방법의 내부 정합성 검증이 하나 늘었다.
2. **얻는 것**: SS 영역의 TT 가 5.7 (제약 없음, `TTNonFlipNorm` lnN 1.3) 에서 55.7 로 바뀌고,
   그 중 flip 성분이 β 로 스케일된다. 즉 **SS 의 최대 비DY 성분이 eμ flavour CR 로 통제된다.**
   또 SS 템플릿의 OS SR 실데이터 의존도가 줄어든다 (현행은 OS SR 데이터를 그대로 읽어 만든다).
3. **치르는 것**: SS 예측이 MC flip rate × SF 에 의존하게 된다. SF 불확도(barrel 2.6% /
   endcap 1.6%)가 그만큼 들어온다. 현행은 그 부분을 데이터가 직접 정한다.
4. **덤으로 보이는 것**: DY CR closure 가 두 방법 모두 **1.063** 이다. 카드의
   `FlipClosure_2024 lnN 1.05` 보다 큰 6.3% 어긋남이다 — 별개 항목으로 확인 필요.

## 검증 — 뺀 나머지가 정말 DY 인가 (`check_dy_flip.py`)

`--dy-only` 의 Flip 은 `Flip(OS 데이터) − Flip(비DY OS MC)` 다. 그게 정말 DY 라면
`Flip(OS DY MC)` 와 맞아야 한다.

| | rEESR_SS (SR) | rDYEECR_SS (DY CR) |
|---|---|---|
| OS 원 yield: 데이터 / MC 합 | 2284.0 / 2311.6 | 35120.0 / 36078.4 |
| OS MC 구성: DY / 비DY | 758.9 / **1552.6** | 33801.6 / 2276.8 |
| Flip(OS 데이터) | 95.23 | 1056.39 |
| − Flip(비DY OS MC) | 56.93 | 44.44 |
| **= 데이터 기반 DY flip** | **38.31** | **1011.95** |
| Flip(OS DY MC) 직접 | 31.52 | 1025.82 |
| **비 = OS 의 DY data/MC** | **1.215** | **0.986** |

**DY CR 에서는 0.986 으로 맞고 SR 에서는 1.215 로 어긋난다.**

주의해서 읽을 것: SR OS 는 **비DY 가 DY 의 2배**(1552.6 vs 758.9)라 뺄셈 오차가 증폭된다.
게다가 그 비DY 의 대부분이 TT 인데 fit 은 TT 를 β=0.90 으로 내려 잡는다 — β 를 적용해 빼면
뺄 양이 줄어 이 비는 더 올라간다. 즉 이 1.215 는 "SR 에서 DY 가 20% 많다"는 측정이라기보다
**뺄셈 기반 방법이 SR 에서는 통계적으로 불안정하다**는 신호로 읽는 것이 맞다.
DY 가 94% 인 DY CR 에서 0.986 이 나오는 것과 대비된다.
실무 영향은 작다 — SS 총예측 135.4 중 Flip 이 38.3 이고 그 20% 는 8 event.

## 플랏 (`plots/`)

**DY-only 만 그린다.** 전체 flip(현행)은 플랏에서 뺐다 — 비교 수치는 위 표에 남아 있다.

| 파일 | 내용 |
|---|---|
| `ss_template_rEESR_SS.png(.pdf)` | SR same-sign, 총 135.4. 아래 pad = `DY flip / total` |
| `ss_template_rDYEECR_SS.png(.pdf)` | DY CR same-sign, 총 1104.6 vs 데이터 1174.0. 아래 pad = **Data / MC** |

**SR 의 아래 pad 가 data/MC 가 아닌 이유**: `rEESR_SS` 는 signal region 이고 blind 다
(WR5000-N2500 신호가 5.1 event 들어간다). 파일의 `data_obs` 는 예측 자신이라
(135.42 = 성분 합, 소수점까지 일치) data/MC 를 그리면 전 bin 1.000 인 무의미한 선이 된다.
실제 SS SR 데이터를 dump 에서 꺼내면 그릴 수 있지만 그것은 **unblind** 다 — 하지 않기로 했다
(2026-09-23 결정). 대신 예측 중 데이터 기반 성분의 비중을 보여 준다.

그림에서 바로 보이는 것:
- SR 에서 `DY flip / total` 이 저질량 0.2 → 고질량 0.7. 나머지를 ttbar(주황)가 채우고,
  그 ttbar 는 `R_TT_Resolved_2024` 가 스케일한다. 즉 **SS 예측의 주도권이 flip weight 에서 β 로 넘어간다.**
  (현행 전체-flip 방식에서는 이 비중이 0.65~0.85 였다.)
- DY CR 의 data/MC 는 전체 1.063, bin 별로는 1800-2000 에서 1.4 까지 튄다.

## 아직 안 한 것

- 이 템플릿으로 카드를 다시 만들어 fit / limit 을 돌리지 않았다. 위는 템플릿 수준 비교다.
- systematic 변주(`Flip_FlipSF_*`, `Flip_FlipPstat_*`)는 차감을 거쳐 생성되지만 검증 안 했다.
- boosted EE SS (`bEESR_SS`) 에는 적용 안 했다.

## 재현

```bash
bash run_dyonly.sh       # baseline + DY-only (SF 없음)
bash run_dyonly_sf.sh    # DY-only + flip SF   <- 권장
```
