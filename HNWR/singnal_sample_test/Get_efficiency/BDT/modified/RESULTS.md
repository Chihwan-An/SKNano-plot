# BDT presel 효율 개선 스터디 결과 (2026-08-05/06)

신호: 2023 WR4000/WR6000, N100/N300 (일부 N500), EE/MM.
모든 비율의 분모 = 해당 질량영역의 LHE(sumall) 이벤트 수 (unweighted).
offshell/onshell 경계 = 분석기 SetSignalFlags 정의: WR4000→2000, WR6000→4000 GeV.
"m<2000" 스터디는 모든 샘플에서 LHE mass < 2000 (진짜 soft 영역)을 뜻함.

## 1. 적용된 셀렉션 변경 (코드 반영 완료)

1. **팻젯 클리닝 lead-only** (HNWR_BDT_presel.cc, WRGenRecoMass::FillBDTPreselSR):
   all-tight → pT-leading tight 렙톤만 클리닝. N-side in-fatjet 렙톤이 tight를
   통과해도 N 팻젯이 살아남음. (측정: WR2000N300MM boosted 18→31% 등)
2. **NO-LOOSE boosted 후보** (동일 두 파일): boosted SR 후보에서
   extra-loose-lepton 및 SF mll>200 pair 요구 제거.
   후보 = !resolved && lead tight pT>60 + trigger(safe pT) && DR-veto && AK8>=1.
   sublead loose는 있으면 여전히 저장(BDT 입력), 없으면 nullptr
   (fillNtuple null-safe 처리: mll/dRll 등 = -999). DY/FLV CR은 불변.
   Cutflow_BDT_Boosted_raw bin 6/8은 informational로 전환.

### No-loose 실측 효율 (WRGenRecoMass BDTSR, TOTAL = off+on 가중)

| 샘플 | 이전 | 실측 | (상한 예측) |
|---|---|---|---|
| WR4000 N100 EE | 11.7% | **69.8%** | 80% |
| WR4000 N300 EE | 47.1% | **74.1%** | 93% |
| WR6000 N100 EE | 16.1% | **60.2%** | 72% |
| WR6000 N300 EE | 38.5% | **69.3%** | 84% |
| WR4000 N100 MM | 64.5% | 75.3% | 79% |
| WR6000 N100 MM | 53.1% | 65.0% | 70% |
| WR6000 N300 MM | 64.8% | 76.7% | 80% |

- onshell EE boosted: 3.1→76% (WR4000/6000 N100). 실측-예측 갭은 fatjet TightID·
  lead 클리닝·noise/jet-veto·trigger-safe 118 등 예측 미포함 컷 몫.
- **주의**: mll>200 DY 억제가 사라짐 → W+jets/semilep-TT 유입. 배경/significance
  스터디 전까지 잠정 채택. BDT는 재학습 필수 (no-sublead 이벤트의 mll 등 -999).
- **스킴 호환**: Skim_20002는 loose 요구가 없어 no-loose 셀렉션과 호환
  (신호/배경/데이터 스킴 전부 사용 가능). 단 HLT_Ele35 추가·전자 lead 60 변경은
  스킴 비호환 (트리거 OR·safe-pT 118이 스킴에 박혀 있음 → 그 변경 시 재스킴 필요).

## 2. 손실 원인 분해 (fail-cutflow, Get_efficiency/*_summary.png)

- offshell lost의 주인은 렙톤: N(tight)≠2가 지배하고, 그 속은
  2nd 렙톤 pT<53 (reco는 됨) > 미재구성 > (EE만) loose ID 실패.
  "loose는 통과, tight만 실패"는 ~7%p로 소수.
- onshell EE lost = in-fatjet 전자 (pT>53인데 loose ID 실패 21~48%p + 미재구성 16%p)
  → no-loose boosted가 이 몫을 회수 (fatjet이 렙톤 에너지를 이미 포함).
- boosted(구 셀렉션) 관점: cut-based는 No-AK8이 최대, BDT는 no-extra-loose가 최대였음.

## 3. m<2000 심층 (EE 중심)

- **토폴로지는 벌어져 있음**: ID-실패 2nd 전자 중 실제 젯과 dR<0.4는 N300 15%,
  N100 43%뿐 (self-jet 제외 후). 이전 99.6%는 self-jet 착시.
- 그러나 벌어진 ID-실패 후보의 mvaNoIso 중앙값 = -0.8~-1.0 (배경권)
  → **대부분 gen 전자와 매칭 안 되는 fake 슬롯**. 진짜 2nd 전자는
  "pT<53" 또는 "미재구성" 카테고리에 있음.
- gen sublead 전자 pT (m<2000): N100 피크 ~15-25 GeV (39-40%가 <53),
  N300 피크 40-70 (20%가 <53). reco 매칭 68-76% / 미재구성 24-32%.
  플롯: sublead_electron_pt_m2000.png, sublead_muon_pt_offshell.png (MM).

## 4. Sublead 회복 스터디 (m<2000, resolved 풀체인 에뮬레이션)

### 4a. tight ID 유지 + pT만 인하 → 거의 무효
| sub pT 컷 | EE N100/N300 | MM N100/N300 |
|---|---|---|
| 53(현재) | 4.7 / 28.8% | 7.7 / 39.2% |
| 20 | 5.7 / 30.9% (+1.0/+2.1%p) | 10.2 / 43.7% (+2.5/+4.5%p) |
- EE는 HEEP 내장 Et>35 때문에 30 이하 인하가 무의미 (30→20 이득 = 0).
- MM은 tkRelIso<0.1과 mll>200이 잠재량의 2/3를 깎음.

### 4b. ID 스캔 (gen-matched sublead, reco pT>20, m<2000; fake 제외)
- **EE 승자: cutBased Loose 75.6%** > mvaNoIso WP90 70.2 > Medium 68.4
  > mvaIso WP90 66.5 > ... > HEEP(현재) 56.6%.
- **MM: ID는 전부 97-99%** (looseId 99.3 최고) — 병목은 iso.
  **miniIsoLoose가 최선**: mediumId+miniIso>=1 = 96.6% vs 현재
  highPtId==2+tkRelIso<0.1 = 77.6% (pfIsoLoose 71.5%는 최악).
- ID만 바꾸고 pT 유지(>53)는 무효: WP90 OR → resolved 유입 +0.5~0.9%p
  (fake 지배 + 젯 근접).

### 4c. 최고 ID + sub pT>20 조합 (lead tight 유지) — 권장 조합
| 샘플 | EE (sub=cutBased Loose) | MM (sub=mediumId+miniIsoLoose) |
|---|---|---|
| WR4000 N100 | 4.7→8.5% (+3.8%p) | 7.7→13.9% (+6.2%p) |
| WR4000 N300 | 28.8→37.5% (+8.6%p) | 39.2→46.6% (+7.4%p) |
| WR6000 N100 | 4.8→8.3% (+3.6%p) | 7.6→13.2% (+5.6%p) |
| WR6000 N300 | 27.2→35.8% (+8.6%p) | 38.9→45.9% (+7.0%p) |
- tight-유지 대비 2~4배. 두 WP 모두 표준 POG SF 존재.
- 남는 몫: 미재구성 24-32% + mll>200/젯 컷.

## 5. 기타 측정

- **HLT_Ele35 추가 + 전자 lead 60**: offshell EE 사용가능 acceptance
  66-82% → 77-89% (+7-11%p). 스킴 비호환 주의(§1).
- MM sublead pT 스펙트럼 (offshell): N100 평평(~15-25 피크), 53→20 인하 시
  offshell 이벤트의 +10~14%p가 sublead-in-window로 들어옴.

## 6. 다음 단계 (TODO)

1. **배경 스터디**: no-loose(±sublead 완화) 셀렉션으로 DY/TTLJ/TTLL/WJets/ST
   yield 재기 (Skim_20002 사용 가능) → **significance (S/sqrt(B) 또는 BDT 후)**
   비교. 특히 mll>200 제거로 인한 W+jets/semilep-TT 유입 정량화.
2. no-loose 채택 확정 시: BDT ntuple 재생산 → 재학습 (missing-value 처리:
   no-sublead 이벤트 mll/dRll = -999) → 템플릿/리밋.
3. sublead 완화(§4c) 채택 여부: fake/charge-misID 배경 + SF 체계 검토 후
   resolved 쪽 별도 결정.
4. (보류) HLT_Ele35: 재스킴 필요라 비용 큼. sublead 완화보다 후순위.

## 7. 최종 조합 스터디 (full_config_study.py / .txt, 2026-08-06)

resolved_new = lead tight + sublead(EE cbLoose||HEEP / MM medium+miniIsoL||현tight) pT>20;
boosted = no-loose(!resolved && lead tight + trig + AK8). NanoAOD 에뮬레이션.

- **Onshell: 순수 카테고리 이동** — resolved +0.5~+14.7%p 증가분만큼 boosted가
  정확히 감소, TOT 변화 0.0% (그 이벤트들은 AK8 보유라 boosted가 이미 잡고 있었음).
- **Offshell: 소폭 순이득** — TOT +0.5~1.1%p (AK8 없는 이벤트가 resolved로 신규 유입).
  boosted는 -3~-8%p 감소.
- → resolved 확장의 가치는 총량이 아니라 **카테고리 최적화** (mlljj 분해능/배경 구조).
  분배 결정은 배경+significance 스터디로.
- **Boosted sublead capture** (요구 아님, BDT 입력 저장용; gen-matched, pT>53/>20):
  - MM: ID 무관 66~94% (looseId/highPtId>=1 근소 우위), pT 20 인하 시 off +8~10%p.
  - EE: onshell 2~9%뿐 (in-fatjet 전자, 어떤 표준 ID도 불가) — sublead 입력은
    대부분 -999가 정상이고 LSF 등 fatjet 변수가 정보를 대신해야 함.
    offshell은 최선 OR(cbL||HEEP||mvaNoIso90)+pT>20으로 40%.
  - 권장 저장용 loose: EE = cbL||HEEP||mvaNoIsoWP90, MM = looseId, 둘 다 pT>20
    (요구가 아니므로 배경 비용 없음).

## 8. 3-SR 테스트 분석기 (2026-08-06, 라이브 코드와 분리)

`Analyzers/src/HNWR_BDT_presel_3SR.cc` + `include/HNWR_BDT_presel_3SR.h` —
§7의 3-카테고리 구조를 구현한 독립 사본 (현행 HNWR_BDT_presel은 무변경):
- resolved: lead tight + ResSub sublead(pT>20; e POG_LOOSE||HEEP, mu Medium+MiniIsoLoose),
  mll>200, sublead 재클리닝 젯으로 4-object dR
- boosted(with-lep): capture pair(pT>20 확장 tier) mll>200 / boosted_nolep: capture 0개
- capture 있는데 mll<=200 → SR 없음(버림). 트리: SR_*_BDTTree_{resolved,boosted,boosted_nolep}
- 컴파일: 테스트 영역 AnalyzersLinkDef.hpp에 include+pragma 한 줄씩 추가 후 rebuild

## 파일 목록 (이 디렉토리)

- `lepton_recovery_study.py` → sublead_muon_pt_offshell.png,
  electron_id_comparison.png, results.txt
- `combined_recovery.py` → sublead_electron_pt_offshell.png, combined_recovery.txt
- `wr6000_priority.py` → wr6000_priority.txt (WR6000 우선순위)
- `wr6000_annotated.py` → WR6000_summary_annotated.png (수정 전 조합 추정)
- `no_loose_requirement/annotate_noloose.py` → WR{4000,6000}_summary_annotated.png
- `sublead_id_scan.py` → ID 스캔 (§4b)
- `sublead_electron_pt_m2000.png` (§3)
- 상위: `Get_efficiency/make_summary.py` → {cutbased,BDT}/WR*_summary.png
  (fail-cutflow + 렙톤 표; WRGenRecoMass 재실행 후 스크립트만 재실행하면 갱신)
