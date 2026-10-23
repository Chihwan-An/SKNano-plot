# 05. DY 와 연결된 노트 (AN-25-020) 수정 내역과 미해결 사항

노트 소스는 `/data9/Users/achihwan/25-020/AN-25-020/` (`tex/*.tex`; `output/AN-25-020_temp.tex` 는 tdr 가 매번 새로 만드는 파일이라 직접 고치면 안 됨).
빌드: `eval "$(utils/tdr runtime -sh)" && tdr --temp_dir=output --style=an b AN-25-020.tex` (2026-09-19 현재 76쪽, 오류·미정의 참조 없음).
**커밋은 하나도 하지 않았다** — 전부 working tree.

## 1. 5장 (Background Estimation) 을 chihwan draft 6장으로 교체
- `tex/05_backgrounds.tex` ← `chihwan/tex/05_backgrounds.tex` (916줄) 에서 draft 의 6.3.0.1 "Charge-sign categories and partial unblinding",
  6.3.0.2 "Expected sensitivity" (493–585행, 표 2 + 그림 2 포함) 를 뺀 것.
- 같이 고친 것: 제목 "(draft)" 제거, `sec:backgrounds` label 유지, draft 섹션 참조 → 노트 label (`sec:SMbkg_datasets`, `sec:objects`, `sec:event_selection`),
  도입부 blinding 문장 ("… negative-charge categories … data are shown" → "Signal regions are blinded."),
  5.4절의 "negative-sign signal categories of Sec. 5.3" 문장 (뺀 paragraph 를 가리켜서 → "It is a nonprompt component …").
- 그림 66개 → `fig/05_backgrounds/2024/`, 표 11개 → `tables/05_backgrounds/2024/`, bib 3개 (`bib:AN19083`, `bib:AN19206`, `Lindert:2017olm`) → `AN-25-020.bib`, `\TODO` 매크로 → `tex/macros.tex`.
- 이후 추가: Fig. 19–20 (03), Fig. 21 (04), ratio 재플랏 (02). 5.4 의 charge-flip DY CR 그림 (Fig. 29–30) 은 keepTT 버전으로 교체, SR 그림 (옛 Fig. 31) 삭제.
- 5.2 (Top quark background) 는 한때 새로 썼다가 원문으로 되돌림 → `../../ttbar/05_an_text_removed_from_note/`.

## 2. Table 8 (MC 샘플) 의 DY / W — **미해결**
- 요청으로 DY, W+jets 행을 chihwan `bkg_samples.tex` 의 HT-binned LO 샘플로 교체 (DY 14, W 12 행, σ 값 그대로), diboson 도 powheg NLO 10개로 교체.
  본문의 "DY samples are normalized using the inclusive NNLO cross-section" 문장을 LO HT-binned 설명으로 바꿈.
- **문제**: chihwan 표는 2023 (Run3Summer23) 이름 규칙이다. 2024 의 실제 이름은 다르다 — 입력 디렉토리에서 확인:
  ```
  2023 식 (지금 Table 8):  DYto2L-4Jets_MLL-120_HT-100to400_TuneCP5_13p6TeV_madgraphMLM-pythia8
  2024 실제:               DYto2L-4Jets_Bin-HT-100to400-MLL-120_TuneCP5_13p6TeV_madgraphMLM-pythia8
                           WtoLNu-4Jets_Bin-HT-100to400-MLNu-0to120_TuneCP5_13p6TeV_madgraphMLM-pythia8
  ```
  (`/gv0/DATA/SKNano/NanoAODv15_RNTuple/2024/` 와 `HNWR/RFlav/2024/Skim_HNWR_*` 파일 이름.) HT bin 도 다르다: 2024 DY 는 40to70/70to100/100to400/400to800/800to1500/1500to2500/2500 × MLL 4to50/50to120/120,
  W 는 40to100/… × MLNu 0to120/120 + MLNu mass-binned. 표의 각주는 `RunIII2024Summer24NanoAODv15` 인데 이름은 2023 식인 상태. σ 값이 2024 DB (`CommonSampleInfo.json`) 와 같은지도 미확인.
- DAS 조회는 grid proxy 가 없어 못 했다. 고치려면 위 디렉토리 이름을 기준으로 Table 8 을 다시 쓰면 된다.

## 3. DY 와 관련된 그 밖의 발견
- **card 체인의 DY CR 에 데이터 누수** (플로터가 아니라 `post_processor_chsplit.py`): 반대 stream 의 데이터 파일이 `Others` 로 들어가
  rDYMuMuCR_OS +2663, rDYEECR_OS +997, bDYMuMuCR +374, bDYEECR +184. 9/19 에 고쳤고 CR 은 재생성 (`shapes_2024_dc_cr_fixstream.root`).
  수정 후 rDYMuMuCR_OS: data 52218, DY 47887.5, TT 1826.5, Nonprompt 78.2, Others 1314.6 (data/MC 1.02). 상세: `../../ttbar/02_production_card_audit/NOTES.md`.
- 수정 시나리오의 실데이터 CR-only fit 에서 `R_DY_Resolved = 0.850 ± 0.023`, `R_DY_Boosted = 0.875 ± 0.050`, **JES +3.34σ (제약 0.46)**, `ResolvedDYReshapeBin4 +2.34σ`.
  DY CR 의 jet pT 축 잔차를 JES 가 흡수하고 rate parameter 가 보상하는 구조. 상세: `../../ttbar/03_combine_validation/NOTES.md` §2.
- 7/29 작업에서 찾은 analyzer 결함 2건 (DYReshape off-by-one, boosted R lookup 변수 불일치) 이 2024 analyzer 에서 고쳐졌는지 미확인 (03).
- SR m(ll) 히스토그램이 0–2000 GeV 로 booking (`HNWR.cc:3518,3569`) — x 축 확장은 재처리 필요 (02 말미).

## 4. DY 관련 남은 일 (우선순위 순)
1. Table 8 을 2024 실제 샘플 이름으로 교정.
2. 2024 FxFx DY ntuple 확보 → NLO pseudo-data 검증 재수행 (04).
3. boosted 의 비닫힘 추적: CR2 closure 1.11–1.28 (03), low-m(lJ) 1.45–1.52 (ttbar 04), 7/29 의 boosted R2/R1 1.26 — 셋이 같은 방향.
   후보: boosted R 의 lookup 변수, in-jet loose lepton 효율의 data/MC, nonprompt MC.
4. per-flavour (`--flav`) CR1→CR2 closure, syst band 전파.
5. Fig. 10 에 variation/central 비율 패널 추가 여부, 7-point scale 로 확장 여부 (01).
6. `SOURCES.md` 의 프로덕션 표기 (`DYCRStudy_RFlav`) 와 실제 로그 (`DYCRStudy/2024`) 불일치 확인 (02).
