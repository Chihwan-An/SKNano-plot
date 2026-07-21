# HNWR — 오브젝트 보정(corrections) 적용 현황

작성: 2026-07-21. 대상 코드:
`AnalyzerTools/src/MyCorrection.cc`, `Analyzers/src/AnalyzerCore.cc`, `DataFormats/src`,
`Analyzers/src/Reproduce20_002_copy.cc`, `Analyzers/src/HNWR_BDT_presel.cc`.

HNWR은 **Run3 (2022, 2022EE, 2023, 2023BPix)** 분석이므로, 아래에서 "Run3" 항목이 실제 적용 대상이다.

> **주의**: 이 문서에 기록된 변경사항은 **컴파일 검증되지 않았다.** `./scripts/build.sh` 후 확인 필요.

---

## 0. 요약

| 상태 | 항목 |
|---|---|
| ✅ 원래부터 정상 | Jet JES(nominal+syst), Electron/Muon Reco·ID·Trigger SF, Jet/FatJet ID 플래그, Jet veto map |
| 🔧 이번에 수정 | Jet JER nominal, Electron scale nominal(DATA), Electron smearing nominal(MC) + 난수 시드, FatJet JES, FatJet JER, FatJet `rawPt`/`originalPt`, `GetFJESUncertainty` cset 버그, `SmearJets` 매칭 인덱스 버그 |
| 🔧 이번에 추가 (Muon POG) | Muon Rochester(pT<200), GE momentum scale(DATA, pT>200), high-pT resolution smearing(MC, pT>200) — 아래 §2 |
| ❗ 미해결 | `ScaleJets`가 JES 소스를 곱셈 합성 (아래 §5), muon resolution syst factor 미확보 (§2.3) |

---

## 1. Electron

EGM의 **Scale & Smearing (SS)** 은 한 패키지의 두 파트다. 혼동하기 쉬우므로 먼저 정리한다.

- **Scale** = 에너지 스케일 보정 → **DATA에만** 적용
- **Smearing** = 에너지 해상도(resolution) 보정 → **MC에만** 적용

즉 "Resolution"은 Smearing의 다른 이름이며 별개 항목이 아니다.
원리: *데이터가 기준이고 MC를 데이터에 맞춘다. 단 스케일만은 데이터 쪽을 고친다.*

### 1.1 Run2 (NanoAODv9) — 원래부터 전부 정상

| 대상 | 파트 | nominal | 변주 |
|---|---|---|---|
| DATA | Scale | NanoAOD 선적용 → 코드에서 할 일 없음 | 없음(정의상) |
| DATA | Smearing | 해당 없음 | — |
| MC | Scale | 1.0 (MC는 스케일을 안 건드림) | `EGM_ScaleUnc.json` up/down |
| MC | Smearing | NanoAOD 선적용 | `Electron_dEsigmaUp/Down` |

`EGM_ScaleUnc.json.gz`는 **불확실성만** 들어있는 파일이고, Run3 NanoAOD에는 `dEsigma` 브랜치 자체가 없다
(`SKNanoLoader.cc:922-923`은 Run2 전용 블록). 이 비대칭이 Run2/Run3 취급이 다른 근거다.

### 1.2 Run3 (NanoAODv12/v13) — nominal 두 칸이 비어 있었음 → **수정함**

`POG/EGM/<era>/electronSS.json.gz` 실측 내용:

| era | `Scale/total_correction` | `Smearing/rho` |
|---|---|---|
| 2022 | 0.981 – 1.022 (평균 1.0013, 7,416 bin) | 0.0019 – 0.0233 |
| 2022EE | 0.970 – 1.041 (평균 1.0033, 11,016 bin) | 0.0105 – 0.0264 |
| 2023 | 0.970 – 1.038 (평균 1.0036, 9,156 bin) | 0.0123 – 0.0388 |
| 2023BPix | **0.894** – 1.056 (평균 0.9926, 3,528 bin) | 0.0090 – 0.0452 |

EGM이 `total_correction`(nominal)을 직접 배포한다는 것 자체가 **Run3 NanoAOD에 SS가 선적용돼 있지 않다**는 근거다.

#### (a) DATA scale nominal — 신규 구현

| 위치 | 내용 |
|---|---|
| `MyCorrection.h:59-61` | `GetElectronScaleCorr(scEta, seedGain, runNumber, r9, pt)` 선언 |
| `MyCorrection.cc:448-468` | 구현. `!IsDATA` 또는 `Run != 3`이면 1.0 반환 (MC 및 Run2 이중적용 방지) |
| `AnalyzerCore.cc:775-781` | `GetAllElectrons`에서 `Electron_pt[i] * egmScale` |

AK4 제트의 JES nominal을 `GetAllJets`에서 거는 것과 동일한 위치·패턴.

#### (b) MC smearing nominal — 신규 적용 + 난수 시드 수정

기존에 `SmearElectrons`의 `syst=="nom"` 분기(및 `GetElectronSmearUnc`의 `variation::nom`)는
**존재했으나 아무도 호출하지 않았다.**

| 위치 | 내용 |
|---|---|
| `AnalyzerCore.cc:4-21` | `ElectronSmearSeed(event, scEta, phi)` — splitmix64 해시 |
| `AnalyzerCore.cc:846-855` | `GetAllElectrons`에서 MC·Run3 nominal smearing 적용 |
| `AnalyzerCore.cc:937-963` | `SmearElectrons` Run3 — 아래 참조 |

**난수 시드 문제 (기존 버그)**

```cpp
// 수정 전
GetElectronSmearUnc(electron, nom, int(electron.Rho()));   // 시드
TRandom3 rng(seed); return rng.Gaus(1.0, rho);             // 매 호출 새로 생성, 첫 draw만 사용
```

`Rho()`는 `fixedGridRhoFastjetAll` — **이벤트당 하나**, 값 범위 10~50. `int()`로 자르면:

1. 전 데이터셋의 서로 다른 시드가 **수십 개뿐** → smearing factor가 Gaussian이 아니라 **빗살(comb) 분포**
2. 같은 이벤트의 모든 전자가 **동일한 시드 → 동일한 pull** (Z→ee의 두 전자가 같은 방향으로 흔들림)
3. `TRandom3`를 매번 새로 만들고 첫 draw만 쓰므로 같은 시드면 **항상 같은 난수**

수정: 시드를 `(EventNumber, scEta, phi)` 해시로 교체. `scEta`/`phi`는 어떤 에너지 보정에도
변하지 않으므로 **전자별 고유 + 재현 가능**하다.

**이중 스미어링 방지**

nominal을 `GetAllElectrons`에서 걸었으므로, `SmearElectrons(up/down)`가 그 위에 다시 Gaussian을
곱하면 이중 적용이 된다. 따라서 Run3 경로는 **비율만** 적용한다:

```cpp
seed       = ElectronSmearSeed(EventNumber, scEta, phi);   // nom/up/down 동일 시드
nom_factor = GetElectronSmearUnc(el, nom,  seed);
var_factor = GetElectronSmearUnc(el, var,  seed);
pt        *= var_factor / nom_factor;
```

`TRandom3`는 같은 시드면 같은 표준정규 `z`를 내고 폭만 스케일되므로,
`factor = 1 + z·rho`, `factor_var = 1 + z·(rho±err)` 가 되어 변주가 **coherent shift**가 된다
(독립적 재추첨이 아님).

### 1.3 "굳이 안 해도 되는 것" — 비어 있어도 정상

1. **DATA에 smearing** — 데이터가 기준. `GetElectronSmearUnc`의 `if (IsDATA) return 1.0;` 정상
2. **MC에 scale nominal** — `if (syst==nom) return 1.;` 정상
3. **DATA의 scale 불확실성** — nuisance는 MC 템플릿에만. `if (IsDATA) return 1.0;` 정상
4. **Run2의 scale/smearing nominal** — NanoAOD에 이미 적용됨. 재적용은 이중 적용

### 1.4 남은 확인 사항

- **HEEP 고-pT 전자에 EGM SS가 유효한가.** EGM SS는 표준 GSF 전자 기준으로 유도되었고
  HNWR은 `pt>53`의 HEEP ID를 쓴다. 적용 범위를 EGM 문서로 확인 필요.
- **Scale JSON의 `run` 축은 `flow=error`** 다 (eta/r9 축은 `clamp`). era 정의를 벗어난 run이
  섞이면 correctionlib이 throw → `safeEvaluate`가 `exit(EXIT_FAILURE)`로 잡을 죽인다.
  조용히 틀리는 것보다 낫지만, 첫 DATA 잡에서 확인할 것.

---

## 2. Muon

| 항목 | MyCorrection 구현 | 적용 여부 | 비고 |
|---|---|---|---|
| Reco SF | `GetMuonRECOSF` | ✅ | — |
| ID SF | `GetMuonIDSF` | ✅ | `NUM_HighPtID_DEN_GlobalMuonProbes` |
| ISO SF | `GetMuonIDSF` 재사용 | ✅ | `NUM_probe_LooseRelTkIso_DEN_HighPtProbes` |
| Trigger SF | `GetMuonTriggerSF` | ✅ | `NUM_HLT_DEN_HighPtLooseRelIsoProbes` |
| **Rochester** | `GetMuonScaleSF` | 🔧 **pT<200** | scale(DATA) / scale+smearing(MC) |
| **TuneP** | — (DataFormats) | 🔧 **pT>200** | `pt = Muon_pt * Muon_tunepRelPt` |
| **GE momentum scale** | 🔧 `GetMuonGEScaledPt` | 🔧 **DATA, pT>200** | 아래 §2.1 |
| **High-pT resolution** | 🔧 `GetMuonHighPtSmearFactor` | 🔧 **MC, pT>200** | 아래 §2.2 |

### 2.0 200 GeV 분기 — POG 권장안 (approach 1)

원문: *"muons with pT < 200 GeV are corrected using the medium pT scale and smearing
corrections ... muons with pT > 200 GeV ..."* 이고, Run3 절에서
*"the recommendation for Run3 is to **correct the transverse momentum** of high pT muons ...
using the values derived from the GE method"* 로 고-pT도 보정하도록 바뀌었다.

따라서 `GetAllMuons`는 **TuneP pT를 기준으로 두 regime으로 분기**한다:

| regime | 사용 momentum | DATA | MC |
|---|---|---|---|
| **pT < 200** | tracker/PF `Muon_pt` | Rochester scale | Rochester scale+smearing |
| **pT > 200** | TuneP | TuneP → **GE 보정** | TuneP → **resolution smearing** |

Rochester 파일은 Run3 전 era 존재 확인함 (`external/RoccoR/RoccoR{2022,2022EE,2023,2023BPix}.txt`).

> ⚠️ 두 regime이 **서로 다른 momentum estimator**를 쓰므로 200 GeV에서 discontinuity가
> 생길 수 있다. 뮤온 pT 및 m(lljj) 분포에 kink가 없는지 확인할 것.
> `plots/muon_rochester/`와 `plots/muon_tunep/`가 각 regime을 따로 보여준다.

Rochester의 MC smearing 난수 시드도 기존 `int(muon.Pt()/muon.Eta())`에서
`ObjectSmearSeed(EventNumber, eta, phi)`로 교체했다 — 전자와 동일한 시드 버그였다.
`GetMuonScaleSF`에 `seed` 인자를 추가했다.

### 2.1 Generalized Endpoint (GE) — momentum scale

출처: Muon POG wiki "High pT: Momentum Scale", 방법론 AN-2018/008.

트래커가 측정하는 양은 pT가 아니라 signed curvature `k = q/pT`이고, misalignment weak mode는
curvature에 **가법적 상수 offset** `κ_b(φ, η)`로 들어간다. pT로 풀면:

```
pT_corr = pT_raw / (1 - q · κ_b · pT_raw)        (pT in TeV, κ_b in TeV⁻¹)
```

curvature 공간에서는 charge-independent한 단일 shift지만 pT 공간에서는 `q`가 나타나
μ⁺/μ⁻가 **반대 방향**으로 밀린다 — 이게 GE가 charge-dependent bias를 잡는 원리다.

| 구현 | 위치 |
|---|---|
| κ_b 맵 (era × 3 φ × 6 η, 값+σ) | `MyCorrection.cc` 익명 namespace `GE_KAPPA` |
| 보정 함수 | `MyCorrection::GetMuonGEScaledPt` |
| 적용 | `AnalyzerCore.cc` `GetAllMuons`, TuneP 직후, DATA·pT≥200 |

주의해서 구현한 부분:
- **η는 부호를 유지**한다 (|η|로 접지 않음). φ는 도 단위 3구간.
- **systematic은 κ 단계에서 ±σ**를 흔들어 공식을 다시 통과시킨다. pT에 직접 %를 적용하면
  pT 의존성이 틀린다. 결과를 `SetMomentumScaleUpDown`에 저장하므로 `ScaleMuons("up"/"down")`이
  이제 **정상 동작한다** (기존에는 미초기화 값을 읽던 버그).
- **극점 가드**: `|1 - q·κ·pT| < 0.1`이면 보정을 포기하고 raw pT를 유지하며 경고를 찍는다.
  2022EE/2023의 `2.1<η<2.4` 셀은 κ가 −0.48, −0.36으로 커서 pT 2 TeV에서 발산한다.

### 2.2 High-pT resolution smearing (MC)

```
p → p · (1 + N(0, σ(p,η) · f))
σ(p,η) = a0 + a1·p + a2·p² + a3·p³        (p in GeV, |η| 2 bins)
f = sqrt((1+x)² − 1)                       (x = 목표 degradation)
```

smearing은 **한 방향으로만** 가능하다(난수를 더해 해상도를 좋게 만들 수 없다). 따라서 MC가
이미 data보다 나쁜 영역은 `f = 0`으로 두고 아무것도 하지 않는다.

| era | central (\|η\|<1.2) | forward (1.2<\|η\|<2.4) |
|---|---|---|
| 2022 | 없음 | 5% → f=0.32 |
| 2022EE | 5% → f=0.32 | 10% → f=0.46 |
| 2023 | 5% → f=0.32 | 10% → f=0.46 |
| 2023BPix | 없음 | 15% → f=0.568 |

난수 시드는 전자와 동일하게 `ObjectSmearSeed(EventNumber, eta, phi)` (splitmix64) —
뮤온별 고유 + 재현 가능. §1.2(b)의 시드 논의가 그대로 적용된다.

### 2.3 ⚠️ 미해결 — 결과에 쓰기 전 반드시 확인

이 네 가지는 스펙 자체에 명시가 없거나 자료가 없다. `MyCorrection.cc`의 함수 위 주석에도
동일하게 적어 두었다.

1. ~~GE 보정의 적용 대상~~ → **해결.** 원문 *"The GE method injects a range of additive
   biases (κb) ... **to the simulation** and minimize the difference **from data** in the
   q/pT distribution"* — κ_b는 MC에 주입해서 data를 재현시키는 값이므로 **bias는 data가
   가진 성질**이다. 따라서 data에서 제거하는 것이 맞고, 부호는 `k_true = k_meas − κ_b`
   → `pT_corr = pT/(1 − q·κ·pT)`. 구현과 일치한다.
2. **smearing 공식의 `p`가 momentum인지 pT인지.** wiki 문구 그대로 **전체 momentum `p`** 로
   구현했다. 계수 크기는 둘 중 어느 쪽으로도 말이 되므로 여전히 확인 필요.
3. **Resolution systematic factor 수치 미확보.** 원문에도 해당 수치가 수식 이미지로만 있어
   텍스트에 안 잡혔다 (*"The values of are:"* 로 비어 있음). nominal smearing만 구현했고
   syst는 TODO. `GetMuonHighPtResolution`을 public으로 노출해 두었으므로 값만 확보되면 바로
   붙일 수 있다.
4. ~~2024/2025 κ_b 맵~~ → **현재 불필요.** 해당 era는 `GE_KAPPA`에 없어 보정이 no-op이 된다.

### 2.4 남은 작업

- **200 GeV 경계 검증**: §2.0대로 두 regime을 구현했으나 서로 다른 momentum estimator를
  쓰므로 경계에서 discontinuity가 생길 수 있다. 뮤온 pT·m(lljj) 분포의 kink를 확인할 것.
- **500 GeV 이상 sanity check** (wiki 필수 권고): signal candidate 뮤온이 500 GeV를 넘으므로,
  측정된 scale bias만큼 pT를 수동 shift해서 limit·m(lljj) shape가 얼마나 움직이는지 확인해야
  한다. 위 systematic이 개별 event의 큰 scale bias를 커버하지 못한다. WR 질량 TeV 스케일
  탐색이므로 **반드시 수행**.
- scale/smearing nuisance를 Combine datacard에 독립 shape systematic으로 등록.

---

## 3. Jet (AK4)

| 항목 | nominal | 변주 | 상태 |
|---|---|---|---|
| **JES** | ✅ `GetAllJets`가 raw pT부터 재보정 (`Jet_pt*(1-rawFactor)*JESSF`) | ✅ `ScaleJets` | 원래부터 정상 |
| **JER** | 🔧 **이번에 추가** | ✅ `SmearJets` | 아래 참조 |
| Jet ID | ✅ `Jet::SetJetID` (NanoAODv12 bit 방식) | — | SF는 HNWR 미사용 |
| Jet veto map | ✅ `IsJetVetoZone` | — | — |

### 3.1 JER nominal 누락 (수정함)

**증상**: `SmearJets`가 `JER_Up`/`JER_Down`일 때만 호출되어 Central이 un-smeared였다.

| 수정 전 템플릿 | 제트 pT |
|---|---|
| Central | **un-smeared** (해상도가 데이터보다 좋음) |
| JER_Up | smeared with SF_up |
| JER_Down | smeared with SF_down |

→ Up/Down이 Central을 감싸지 않고 **둘 다 넓어지는 쪽**으로 간다. JER systematic이
"JER 불확실성"이 아니라 사실상 **"smearing 적용 vs 미적용"** 을 측정하고 있었다.

**누락이지 설계가 아니라는 근거:**

1. NanoAOD의 `Jet_pt`에는 JEC은 있으나 **JER smearing은 없다** (JME POG 필수 권고)
2. `Reproduce20_002_copy_SELECTION_NOTES.md:29`가 *"MC는 추가로 SmearJets(JER) 적용"* 이라고
   **문서에 써 있는데 코드가 안 그랬다**
3. `FullHadronicTriggerTnP.cc:51`은 같은 프레임워크에서 MC면 무조건 nominal smearing을 건다
4. `SmearJets`의 backward-smearing 로직(`GetUnsmearedP4`)은 *"nominal로 이미 스미어된 제트를
   되돌린 뒤 변주로 재스미어"* 워크플로우용이다. nominal이 없으면 그 분기는 **죽은 코드**다
5. 결정적: `ScaleJets`의 에러 메시지가
   *"Since all jets in MC are smeared when calling GetAllJets(), UnsmearedP4 should have been set
   by SmearJets"* — **코드 자신이 nominal smearing을 전제**하고 있었다

**수정 내용** (`Reproduce20_002_copy.cc:1043-1062`, `HNWR_BDT_presel.cc:147-168`):

```cpp
if (!IsDATA) {
    RVec<GenJet> genjets = GetAllGenJets();
    MyCorrection::variation jer_var = MyCorrection::variation::nom;   // MC면 항상 nominal
    if (this_syst.Contains("JER_Up"))        jer_var = MyCorrection::variation::up;
    else if (this_syst.Contains("JER_Down")) jer_var = MyCorrection::variation::down;
    jets = SmearJets(jets, genjets, jer_var, "total");

    // JES는 else-if 체인에서 분리 -> JES 변주에도 nominal JER이 먼저 걸린다
    if (this_syst.Contains("JES_Up"))        jets = ScaleJets(jets, ...::up,   "total");
    else if (this_syst.Contains("JES_Down")) jets = ScaleJets(jets, ...::down, "total");
}
```

부수 효과: `GetAllGenJets()`가 매 MC 이벤트마다 호출된다 (이전엔 JER 변주 때만). CPU 소폭 증가.

### 3.2 GenJet 매칭 인덱스 버그 (수정함)

`AnalyzerCore.cc:260`

```cpp
// 수정 전:  if (matched_idx[i] >  0 && ...)
// 수정 후:  if (matched_idx[i] >= 0 && matched_idx[i] < static_cast<int>(genjets.size()))
```

`GenJetMatching`은 unmatched에 **-999**를 넣는다. 따라서 **genjet 인덱스 0에 매칭된 제트가
unmatched로 취급**되어 scaling method 대신 stochastic method를 받고 있었다.
JER nominal을 켠 지금부터 실제로 영향을 준다.

---

## 4. FatJet (AK8)

### 4.1 수정 전 상태

| 항목 | 상태 |
|---|---|
| pt/eta/phi/mass | NanoAOD `FatJet_pt` 그대로 (**JEC 재보정 없음** — 블록 주석 처리) |
| JES | ❌ 주석 처리 |
| JER | ❌ `SmearFatJets` 함수 전체가 주석, 헤더 선언도 주석 |
| `JME_FJER_GT` | ❌ **선언만 되고 어디서도 채워지지 않음** → 호출 시 `std::out_of_range` |
| `GetFJESUncertainty` | ❌ AK8 키를 **AK4용 `cset_jerc`** 에서 조회 → 키 없음 |
| `jet_rawPt`, `jet_originalPt` | ❌ **생성자 초기화도 setter 호출도 없음** → 미초기화 메모리 |
| area/sdMass/lsf3/btag/PNet/tau/jetId | ✅ 정상 (NanoAOD 실제 값) |

`jet_rawPt`/`jet_originalPt`는 BDT ntuple에 그대로 기록되고 있었다
(`HNWR_BDT_presel.cc` `fatjet{N}_rawPt`, `fatjet{N}_originalPt`) → **쓰레기값 브랜치**.
AK4 `Jet`은 `GetAllJets`에서 둘 다 세팅하므로 정상이고, FatJet만 누락이었다.

### 4.2 수정 내용

| 위치 | 내용 |
|---|---|
| `MyCorrection.cc:81-89` | **`JME_FJER_GT` 채움**. 키는 `POG/JME/<era>/fatJet_jerc.json.gz`에서 확인 |
| `MyCorrection.cc` (DATA/MC 블록) | `JME_FJES_GT`에 Run2 4개 era 추가 (기존엔 Run3만) |
| `MyCorrection.cc:1379` | `GetFJESUncertainty` → `cset_jerc_fatjet` 로 수정 |
| `FatJet.h:44-52` | `SetUnsmearedP4`/`GetUnsmearedP4` + `j_unsmearedP4` 멤버 |
| `FatJet.cc` 생성자 | `jet_rawPt`, `jet_originalPt`, `j_unsmearedP4` 초기화 |
| `AnalyzerCore.cc:1385-1393` | `GetAllFatJets`에서 raw pT부터 JES 재적용 + `SetRawPt`/`SetOriginalPt` |
| `AnalyzerCore.cc:1409` | `GetAllGenJetAK8()` 신규 |
| `AnalyzerCore.cc:293` | `GenJetAK8Matching()` — AK8용 **dR=0.4** (AK4는 0.2) |
| `AnalyzerCore.cc:329` | `SmearFatJets()` 구현 |
| `AnalyzerCore.cc:369` | `ScaleFatJets()` 구현 |
| 두 analyzer | `SmearFatJets`/`ScaleFatJets` 호출 연결 |

**주의점**

- `SmearFatJets`/`ScaleFatJets`는 주석 해제가 아니라 **재작성**이다. 원본 주석 코드는
  존재하지 않는 `GenJetAK8` 타입과 시그니처가 안 맞는 `GenJetMatching`을 참조했다.
- `GetAllGenJetAK8()`은 **kinematics만** 채운다. `GenJetAK8_partonFlavour`는 `SKNanoLoader`에서
  `SetBranchAddress`가 안 되어 있어 읽으면 미초기화 값이 나온다. JER 매칭엔 불필요.
- `ScaleFatJets`의 기본 source는 **`"Total"`**(대문자) — JSON의 실제 envelope 키.
- `SmearFatJets`의 `gRandom` 시드는 `int(MET_pt*1e6)+1`로 AK4(`SmearJets`)와 어긋나게 두어
  두 컬렉션이 같은 난수 스트림을 공유하지 않게 했다.

### 4.3 참고: FatJet JER GT 키

```
2022       Summer22_22Sep2023_JRV1_MC_######_AK8PFPuppi
2022EE     Summer22EE_22Sep2023_JRV1_MC_######_AK8PFPuppi
2023       Summer23Prompt23_RunCv1234_JRV1_MC_######_AK8PFPuppi
2023BPix   Summer23BPixPrompt23_RunD_JRV1_MC_######_AK8PFPuppi
```
(`######` → `PtResolution` 또는 `ScaleFactor`. AK4의 `JME_JER_GT`와 완전 대응.)

---

## 5. 미해결 — `ScaleJets`의 JES 소스 합성

`AnalyzerCore::ScaleJets`는 `source == "total"`일 때 개별 소스 ~22개를 **순차 곱셈**한다:

```cpp
for (const auto &it: syst_sources) {
    this_jet *= myCorr->GetJESUncertainty(..., syst, it);   // 곱셈 누적
}
```

quadrature 합이 아니라 곱이고, JSON에 존재하는 `Total` 키를 쓰지 않는다.
**JES 불확실성이 과대평가되고 있을 가능성이 크다.** 기존 동작이라 이번엔 건드리지 않았다.
(FatJet 쪽 `ScaleFatJets`는 `Total` 키를 쓰도록 새로 만들었으므로 AK4와 관례가 다르다.)

---

## 6. 변경 파일 목록

```
AnalyzerTools/include/MyCorrection.h     GetElectronScaleCorr 선언
AnalyzerTools/src/MyCorrection.cc        GetElectronScaleCorr 구현, JME_FJER_GT 채움,
                                         JME_FJES_GT Run2 추가, GetFJESUncertainty cset 수정
Analyzers/include/AnalyzerCore.h         GetAllGenJetAK8 / GenJetAK8Matching /
                                         SmearFatJets / ScaleFatJets 선언
Analyzers/src/AnalyzerCore.cc            ElectronSmearSeed, 전자 scale/smear nominal,
                                         SmearElectrons 비율화, FatJet JES/JER,
                                         SmearJets 인덱스 버그
Analyzers/src/HNWR_BDT_presel.cc         JER nominal, FatJet JES/JER 연결
Analyzers/src/Reproduce20_002_copy.cc    JER nominal, FatJet JES/JER 연결,
                                         fatjets 선언 위치 이동
DataFormats/include/FatJet.h             UnsmearedP4 접근자 + 멤버
DataFormats/src/FatJet.cc                rawPt/originalPt/unsmearedP4 초기화
```

> `Reproduce20_002_copy.cc`의 diff 대부분(트리거 SF 테이블 RMS-method 갱신 등)과
> `plots` 서브모듈 포인터 변경은 **이번 작업과 무관한 기존 미커밋 변경**이다.

---

## 7. 후속 작업

### 필수
1. **빌드** — 미검증. `FatJet`에 멤버(`j_unsmearedP4`)를 추가했으므로 ROOT dictionary 재생성 확인.
2. **BDT 재학습 + 템플릿·리밋 재생산** — MC(JER, 전자 smearing, FatJet JES/JER)와
   DATA(전자 scale)가 모두 바뀐다.

### 검증 도구

`shape_plots/` — 각 보정의 before/after 분포를 자동 생성한다.
`AnalyzerCore::FillCorrShape`가 보정 지점마다 `CorrShapes/<tag>/<var>_{before,after,factor}`를
채우고(`--userflags corrShapes`일 때만), `shape_plots/make_shape_plots.py`가 태그별 폴더에
overlay+ratio PNG를 쓴다. 사용법은 [`shape_plots/README.md`](shape_plots/README.md) 참조.

### 검증 포인트
| 대상 | 확인 방법 | 기대 |
|---|---|---|
| Electron scale (DATA) | Z peak **위치** | 데이터 peak이 MC 쪽으로 이동 |
| Electron smearing (MC) | Z peak **폭** | MC 폭이 넓어져 데이터와 일치 |
| Jet JER | Central jet pT 분포 | 해상도 꼬리가 넓어짐, JER Up/Down이 Central을 감쌈 |
| FatJet JES/JER | `msoftdrop` 분포, boosted SR yield | — |
| Scale JSON run 범위 | 첫 DATA 잡 로그 | `GetElectronScaleCorr` 관련 exit 없어야 함 |

### 검토 대기
- HEEP 고-pT 전자에 EGM SS 적용 타당성 (§1.4)
- `ScaleJets`의 JES 소스 곱셈 합성 (§5)
- `ScaleMuons`의 미초기화 `MomentumScaleUp/Down` (§2)
