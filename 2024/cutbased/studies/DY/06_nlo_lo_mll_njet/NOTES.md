# 06. NLO vs LO 를 젯 갯수별로 — gen m(ll) 과 gen Z pT

## 질문 (2026-09-20)
"C 는 젯 갯수에 영향을 많이 받을 텐데 젯 갯수는 신경 안 쓰고 하나?" → 안 쓴다.
`DYGenZpT` 의 variant 는 gen Z 정의 3 종 × HT40 유무 × m(ll) 분할 3 종뿐이고, `HNWR.cc` 의 lookup 도 `C(gen Z pT)` 1 차원이다.
이어서: "normalization 과 mll shape 이 일치하는지, NLO/LO 의 inclusive 와 1jet 각각 gen m(ll) 로 그려봐", "2 jet 도 틀릴 건 알지만 그려봐".

## 왜 이게 문제인가

C 의 분자는 POWHEG (LHE parton 0 또는 1), 분모는 madgraphMLM (4 까지 merge) 이다. 그래서:

- **`LHE_HT > 40` 이 NLO 쪽에서 크게 자른다.** LO HT-binned 세트는 HT ≥ 40 이 샘플 정의라 컷이 아무것도 안 한다.
  `run_log_zpt.txt`:
  ```
  Zpt_genZ       LO=6.976e+07  NLO=4.929e+08  K=7.0655
  Zpt_genZ_HT40  LO=6.976e+07  NLO=4.986e+07  K=0.7148
  ```
  **주의 — 이 줄은 전 구간 합이다** (pT ≥ 50 합이 아니다; 9/20 에 히스토그램에서 직접 확인).
  실제로 재보면:
  ```
  NLO  sum(all)=4.9287e+08  sum(pT>=50)=3.8329e+07        (HT 컷 없음)
  NLO  sum(all)=4.9863e+07  sum(pT>=50)=3.5428e+07        (HT>40)
  ```
  즉 HT>40 은 **전체의 90% 를 자르지만 그건 거의 전부 저 pT 구간이고, Z pT>50 위에서는 8% 만 자른다.**
  그리고 **Born 을 자르는 게 아니다** — POWHEG 의 `LHE_Njets` 는 0 이 0.5%, 1 이 99.5% 다 (아래 표).
  HT 컷이 없애는 것은 LHE parton 이 하나이되 그게 물렁한 이벤트다.
  따라서 shape-only 정규화가 나누는 계수는 0.71 이 아니라 **pT≥50 에서의 0.989** 다.
- 그래도 결론은 같다: 배포되는 C 는 실질적으로 "NLO ME parton 1 개" vs "LO MLM parton 1–4 개" 의 비다.
- 그런데 분석 영역은 resolved 가 젯 2 개 이상이다. **POWHEG 는 거기 ME 가 없다** — 두 번째 젯은 전부 parton shower.
  04 번 study 가 reco 레벨에서 본 붕괴 (DY CR 에서 NLO/LO 0.70 → 0.05) 와 같은 뿌리다.
- 단, `HT > 40` 과 `Njets >= 1` 은 같은 컷이 아니다 (parton pT < 40 인 1-parton 이벤트는 전자만 탈락).
  그래서 아래 히스토그램은 **모든 multiplicity bin 에서 HT 컷 있는 것과 없는 것을 둘 다** 채운다.

## 이번에 한 것 — 코드만, 프로덕션은 대기

**아날라이저** (`HNWR/src/DYGenZpT.cc`, `include/HNWR/DYGenZpT.h`):
- `MllBins()` 추가 — 0/50 부터 5 GeV (–120), 10 (–200), 25 (–500), 50 (–1000), 250 (–2000), 그다음 2000/3000/4000/6000/8000.
  첫 bin (0–50) 은 생성 범위 아래로 새는 이벤트를 잡는 용도.
- `LHE_Njets` 를 읽어 `Njet0 / Njet1 / Njet2 / Njet3plus` 태그를 만든다. 필드가 없는 샘플이면 `valid()` 로 걸러 경고 한 번만 찍고 njet 히스토그램만 비운다.
  (2024 NanoAODv15 RNTuple 의 DY LO·NLO 양쪽에 `LHE_Njets` 존재 확인함 — `data/Run3_v15_Run2_v15/generated_branch_decls.inc:1617`.)
- 새 히스토그램 (기존 Zpt 채우기와 같은 syst 루프 안, 같은 flav_ok = Z→ee/μμ 요구):
  ```
  Mll_genZ            Mll_genZ_Njet{0,1,2,3plus}
  Mll_genZ_HT40       Mll_genZ_HT40_Njet{0,1,2,3plus}
  Zpt_genZ_Njet{0,1,2,3plus}        Zpt_genZ_HT40_Njet{0,1,2,3plus}
  LHENjets_genZ       LHENjets_genZ_HT40
  ```
  (pT 축 분할은 사용자 요청 2026-09-20: "ZPT 도 jet 빈 별로 Z pt > 50 부터". 기존 `ZptBins()` 를 그대로 쓰므로
  C 자체를 multiplicity 별로 다시 만들 수 있다.)
- syntax-only 통과 (`compile_commands.json` 의 명령에서 `-c/-o` 만 빼고 `-fsyntax-only`). **빌드는 사용자가 tamsa2 에서.**

**플랏** (`HNWR/scripts/make_dy_nlo_lo_mll.py`, 신규):
- 샘플 목록 · 루미 · 히스토그램 리더를 `make_dy_zpt_nlo_lo.py` 에서 import 한다 (드리프트 방지).
- 그림 4 장 (`{mll,zpt}` × `{_incl,_HT40}`), 각 4 열 = inclusive / Njet1 / Njet2 / Njet3plus.
  pT 그림은 50 GeV 부터 그린다 (그 아래는 C 가 1 로 고정되는 구간).
  위 = events/GeV (log-log, NLO 검정 · LO 빨강), 아래 = NLO/LO + integral 비 수평선.
  Njet0 은 json 에만 (LO 가 구조적으로 비어 패널이 빈다).
- normalization 표를 stdout 으로: total / 50–120 / 120–200 / 200+ 각각의 integral NLO/LO.
- 합성 입력으로 draw 경로까지 검증함 (`/tmp/claude-5596/mll_fake/`). **실데이터 수치 아님.**

## 읽는 법
- **Njet1**: 양쪽 다 ME 가 있는 유일한 multiplicity. 여기서의 비는 K-factor 로 읽어도 되고, ratio 에 기울기가 있으면
  그건 "C 가 m(ll) 에 의존한다" 는 진짜 진술이다.
- **Njet0**: LO 가 구조적으로 못 채운다. NLO 샘플의 몇 %가 거기 사는지 (= HT40 이 뭘 잘라내는지) 보는 용도.
- **Njet2 이상**: POWHEG 쪽은 shower. 분석이 선택하는 영역이라 그리긴 하지만, NLO 예측이 아니라 shower 를 재는 것이다.

## 상태 (2026-09-20)

빌드·제출 완료 (tamsa2, Claude 가 실행):
```
./scripts/rebuild.sh                                   # REBUILD_EXIT=0
python python/SKNano.py -a DYGenZpT -i ./Nano15_Analyzers/HNWR/scripts/DYGenZpT_2024.txt \
    -e 2024 -n 50 --nmax 100 --memory 4096 --batchname DYGenZpT_MllNjet
```
- runlog `/gv0/Users/achihwan/SKNanoRunlog/2026_09_20_215244_DYGenZpT/`, 32 샘플 (리스트와 일치), 1099 job.
- `--hadd-ncpu` 는 CLI 에서 없어졌다 (8/21 provenance 에는 있었음) → 뺐다.
- `--memory 4096 --nmax 100` 은 condor I/O throttle 경험칙 (원 제출은 2048/500).
- 빌드 확인: `strings install/redhat/lib/libHNWR.so` 에 `Mll_genZ`, `Zpt_genZ_HT40_`, `LHENjets_genZ`, `Njet1`, `Njet3plus` 전부 존재.

## 결과 (2026-09-20, `plots/`)

### 1. 두 생성기의 multiplicity 가 거의 겹치지 않는다 — 이게 핵심

lumi 가중 합, `LHENjets_genZ*`:
```
                    Njets=0   1        2        3        4
NLO (POWHEG)  no HT  0.0051   0.9949   -        -        -
NLO (POWHEG)  HT40   -        1.0000   -        -        -
LO  (MLM)     둘 다  -        0.3696   0.4328   0.1344   0.0632
```
- POWHEG 는 0 또는 1 뿐이고, HT>40 뒤에는 **100% 가 Njets==1**.
- MLM 은 0 이 아예 없고 (HT≥40 이 샘플 정의), **1 이 37% 뿐, 나머지 63% 가 ≥2**.
- **겹치는 bin 은 Njets==1 하나뿐이다.** 분석이 쓰는 LO 샘플의 2/3 는 POWHEG 에 대응물이 없다.

### 2. Njets==1 에서의 비는 2 이고, pT 에 따라 10 까지 간다

```
integral NLO/LO (HT40)        all(>50)   50-100   100-250  250-500  500+
  Zpt  inclusive               0.9885    0.9714   1.0737   0.8944   0.7201
  Zpt  Njets==1                2.1124    1.9142   3.5909   6.3519  10.9185

integral NLO/LO (HT40)        all(>50)   50-120   120-200  200+
  Mll  inclusive               0.7166    0.7140   0.8579   1.0059
  Mll  Njets==1                1.9384    1.9345   2.1019   2.4225
```
- inclusive 는 pT>50 에서 0.99 로 거의 1 이다. 그런데 **그건 MLM 의 ≥2-parton 63% 가
  POWHEG 의 parton 하나가 못 채우는 것을 대신 채워 주기 때문**이지, NLO K-factor 가 1 이라서가 아니다.
- 같은 multiplicity (1 parton) 로 맞춰 놓고 보면 NLO 가 LO 의 **2.1 배**이고, Z pT 가 올라가면 **10 배**까지 벌어진다.
  MLM 은 고-pT Z 를 ≥2 parton 쪽으로 보내고 POWHEG 는 parton 하나로 만들어야 하니 당연한 방향이다.

### 3. 그래서 C 의 pT 모양은 "NLO/LO QCD 보정" 이 아니라 "두 생성기가 젯 multiplicity 를 나누는 방식" 이다

inclusive 곡선 (그림 1 열) 은 우리가 아는 C 모양 그대로다 — 110 GeV 에서 1.07, 250–500 에서 0.89, 500+ 에서 0.72.
그 하강은 POWHEG 가 고-pT 를 parton 하나로 감당하지 못해서 생기는 것과 분리되지 않는다.

**한계**: MLM 의 `LHE_Njets` 는 merging veto **이전** 의 ME multiplicity 이고, 물리적 예측은 multiplicity 합이다.
따라서 Njets==1 의 비 2.1 을 그대로 K-factor 로 읽으면 안 된다. 이 분할은 **문제의 크기를 재는 진단**이지 보정이 아니다.
고치려면 FxFx 분자가 필요하다 (→ `../04_nlo_pseudodata/`).

## 남은 것
1. 위 2 번의 크기를 C 의 SR 외삽 systematic 으로 얹을지 판단. SR 은 ≥2 젯이고 C 는 사실상 1-parton 비교에서 나왔다.
2. FxFx 가 생기면 분자만 바꿔 같은 그림을 다시 (스크립트 그대로 돌아간다).
3. `01_zpt_correction_systematics/NOTES.md` 의 "K=0.7148 = pT>50 정규화" 표현 수정 필요 (위 참조).
   Njet≥2 의 어긋남은 FxFx 없이는 못 고친다 → `../04_nlo_pseudodata/` 와 같은 병목.

관련: [[../01_zpt_correction_systematics]], [[../04_nlo_pseudodata]], `HNWR/docs/DY_CORRECTIONS_EXPLAINED.md`
(그 문서 §0 "보정이 꺼져 있다" 는 stale — `HNWR.cc:40 kTempNoTheoryDYSyst` 는 지금 `false` 다).
