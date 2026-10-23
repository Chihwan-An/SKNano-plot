"""HNWR 2024 배경 플롯 설정.

경로/luminosity/샘플 그룹/systematic 목록/리전 정의를 한곳에 모아둔다.
새 산출물 경로나 lumi가 바뀌면 여기만 고치면 된다.
"""

import fnmatch
import os
import re

# --- 입력 -------------------------------------------------------------------
# SKNano.py 는 $SKNANO_OUTPUT/<Analyzer>/<Era>/<sample>.root 로 평평하게 떨군다.
# 2026-08-28: HNWR 을 `RFlav` userflag(채널별 DY R, 새 C·EW·R 보정)로 재생산한 산출물
# (HNWR/samplelists/hnwr_plot_samples_2024.txt: 배경+데이터 76 + 오버레이 시그널 4).
# 예전 보정(08-22/24 생산)은 HNWR/2024. 시그널 전체(228)는 거기에만 있다.
INPUT_DIR = "/gv0/Users/achihwan/SKNanoOutput/HNWR/FlipSFEM_combined_for_plots/2024"   # 2026-09-25 FlipSF(+EM) production

# 아날라이저를 skim 위에서 돌리면 산출물 이름 앞에 skim 이름이 붙는다
# (Skim_HNWR_TTto2L2Nu_TuneCP5.root). INPUT_DIR 에는 접두사 없는 7월 산출물이
# 아직 남아 있고 같은 샘플이 옛 이름으로도 들어와 있어서, 둘 다 읽으면 배경이
# 이중으로 쌓인다. 그래서 이 접두사가 붙은 파일만 쓰고, SAMPLE_RULES 매칭은
# 접두사를 뗀 이름으로 한다.
#
# 옛 평평한 산출물로 스모크 테스트할 때는 "" 로 둘 것.
INPUT_PREFIX = "Skim_HNWR_"

# 2026-09-24: W+jets 는 HT-binned 세트(WtoLNu_MLNu{0to120,120toInf}_HT*, MLNu 전 구간)만 쓴다
# (sample_groups.py 의 2026-08-24 stitching 결정). 이 세트와 VVV 는 skim 이 없어 원본에서 돌렸으므로
# 산출물에 INPUT_PREFIX 가 붙지 않는다 -> 접두사 없이도 받는다.
# MLNu>=120 만 있는 mass-binned 세트(WtoLNu-4Jets_Bin-MLNu-*)는 HT 세트와 겹치므로 버린다.
UNPREFIXED_GLOBS = ["WtoLNu_MLNu*_HT*", "WWW", "WWZ", "WZZ", "ZZZ"]
DROP_GLOBS = ["WtoLNu-4Jets_*"]

# 접두사를 통과했는데도 빼야 하는 stem (접두사 뗀 이름). 기본은 비어 있고,
# 같은 샘플이 병합본과 _partN 로 동시에 존재해 이중으로 쌓이는 경우에만 쓴다
# (DY/run_dycr.py --raw-input 이 채운다). AN 플롯 동작에는 영향이 없다.
EXCLUDE_STEMS = set()

# 시그널. 지금은 배경만 그리므로 통째로 뺀다 (2024 산출물에 228개 들어와 있다).
# 시그널을 스택에 올리게 되면 여기를 비우고 BACKGROUND_GROUPS 에 그룹을 만들 것.
SIGNAL_GLOBS = ["WRtoN*"]

# --- 표시 -------------------------------------------------------------------
# 2024 Golden JSON 기준. 갱신되면 이 한 줄만 고친다.
LUMI_LABEL = "109.8 fb^{-1} (13.6 TeV)"
CMS_SUBLABEL = "Work in progress"

# --- 배경 그룹 ---------------------------------------------------------------
# 색은 plotter 에서 ROOT 상수로 해석한다 (config 가 ROOT 를 import 하지 않도록).
BACKGROUND_GROUPS = {
    "DYJets":    ("kYellow",   "Drell-Yan"),
    "TT":        ("kRed",      "T#bar{T}+tW"),
    "Nonprompt": ("kGreen+2",  "Nonprompt"),
    "Others":    ("kBlue",     "Others"),
}

# 샘플 -> 그룹. 위에서부터 첫 일치가 이긴다.
#
# v13 플로터는 부분일치 dict 였고 순서에 의존해 WWtoLNu2Q 가 W+jets 로 빨려들어가는
# 사고가 있었다. 여기서는 glob 으로 명시하고, 어디에도 안 걸리는 파일은 조용히
# Others 로 넘기지 않고 경고한다.
#
# v13 이름(DYMLL*, WJet*)도 남겨둔 이유: 예전 산출물로 스모크 테스트가 가능해야 한다.
SAMPLE_RULES = [
    # --- Drell-Yan ---
    ("DYto2L-4Jets_*",        "DYJets"),     # v15 skim  (= DYto2L_MLL*_HT*)
    ("DYto2L_*",              "DYJets"),     # v15 평평한 산출물
    ("DYto2E_*",              "DYJets"),
    ("DYto2Mu_*",             "DYJets"),
    ("DYMLL*",                "DYJets"),     # v13 naming

    # --- ttV. ttbar 가 아니라 diboson 과 함께 Others 다 ---
    # 함정: TTLL_Bin-MLL-* 는 이름과 달리 ttbar 다이렙톤이 아니라 tt+Z(->ll) 이다
    # (skim JSON 의 PD 가 ttZtoLL_MLL*). v13 의 TTLL_powheg 와 이름이 비슷하니
    # 아래 TT 규칙보다 반드시 먼저 와야 한다.
    ("TTLL_Bin-MLL-*",        "Others"),     # = ttZtoLL_MLL4to50 / MLL50toInf
    ("TTLNu-EWK",             "Others"),     # = ttWtoLNu_EWK
    ("ttZto*",                "Others"),     # v13 naming
    ("ttWto*",                "Others"),

    # --- ttbar 다이렙톤 + tW ---
    ("TTto2L2Nu*",            "TT"),         # = TTLL_powheg
    ("TWminusto*",            "TT"),         # = ST_tW_top_Lep / _Semilep
    ("TbarWplusto*",          "TT"),         # = ST_tW_antitop_Lep / _Semilep
    ("TTLL_powheg",           "TT"),         # v13 naming 이하
    ("ST_tW_*",               "TT"),

    # --- Nonprompt (MC 기반; 데이터 구동 fake 추정이 아니다) ---
    ("TTtoLNu2Q*",            "Nonprompt"),  # = TTLJ_powheg
    ("*-t-channel*",          "Nonprompt"),  # = ST_tch_*  (T[bar]B[Q]toLNu-t-channel-4FS)
    ("*-s-channel*",          "Nonprompt"),  # = ST_sch_*
    # WtoLNu-4Jets_* (mass-binned, MLNu>=120) 은 DROP_GLOBS 로 버린다 — HT 세트만 쓴다.
    ("TTLJ_powheg",           "Nonprompt"),  # v13 naming 이하
    ("ST_tch_*",              "Nonprompt"),
    ("ST_sch_*",              "Nonprompt"),
    ("WtoLNu_*",              "Nonprompt"),
    ("WJet*",                 "Nonprompt"),

    # --- Others (diboson) ---
    ("WWto*",                 "Others"),
    ("WWW",                   "Others"),     # VVV (2026-09-24 추가)
    ("WWZ",                   "Others"),
    ("WZZ",                   "Others"),
    ("ZZZ",                   "Others"),
    ("WZto*",                 "Others"),
    ("ZZto*",                 "Others"),
]

# 2026-10-01: QCD MC 를 별도 그룹으로 쌓는 opt-in (PLOT_WITH_QCD=1). 기본 AN 플롯의
# TSV 헤더/범례가 바뀌지 않게 env 로만 켠다. QCD 는 skim 없이 원본에서 돌려 접두사가 없다.
# enrichment 이중계산은 입력 디렉토리에서 막는다 (EE: EM+bcToE, MM: Mu 만 symlink;
# HNWR/FlipSFEM_combined_for_plots_QCD{EE,MM}).
if os.environ.get("PLOT_WITH_QCD", "") in ("1", "true", "yes"):
    BACKGROUND_GROUPS["QCD"] = ("kOrange+1", "QCD (multijet)")
    SAMPLE_RULES.append(("QCD_*", "QCD"))
    UNPREFIXED_GLOBS.append("QCD_*")

# --- 시그널 오버레이 ---------------------------------------------------------
# 시그널은 배경 스택에 안 들어간다 (SIGNAL_GLOBS 로 MC 목록에서 통째로 빠진다).
# 아래는 그것과 별개로, 몇 개 질량점만 골라 스택 위에 선으로 겹쳐 그리는 설정이다.
#
# SR 에서만 그린다. SR 은 blind 라 ratio 패널이 가려져 있어서 오버레이가 그
# 플롯의 유일한 볼거리이기도 하다.
SIGNAL_REGIONS = ["Boost_sig", "Resolve_sig"]

# 채널 -> 시그널 파일의 flavour 태그. EE 는 WR->N e->ee jj, MM 은 뮤온 쪽.
SIGNAL_CHANNEL_TAG = {"EE": "WRtoNEltoElElJJ", "MM": "WRtoNMutoMuMuJJ"}

# 질량 표기는 전부 TeV 로 통일한다. "m_{W_{R}}=4 TeV, m_{N}=200 GeV" 처럼 한
# 라벨 안에서 단위가 갈리면 두 질량을 눈으로 비교할 때 1000 을 머리로 곱해야
# 한다. 200 GeV 는 0.2 TeV 로 적는다.
_SIGNAL_SUFFIX_RE = re.compile(r"MWR(\d+)_N(\d+)")


def mass_tev(gev):
    """GeV 수치 -> TeV 문자열. 200 -> '0.2', 4000 -> '4', 2100 -> '2.1'."""
    return f"{gev / 1000:g}"


def signal_label(suffix):
    """'MWR4000_N200' -> 'm_{W_{R}}=4 TeV, m_{N}=0.2 TeV'.

    라벨을 suffix 에서 만들기 때문에 질량점을 새로 넣어도 TeV 표기가 저절로
    따라온다. 형식을 못 알아보면 suffix 를 그대로 돌려준다.
    """
    m = _SIGNAL_SUFFIX_RE.fullmatch(suffix)
    if not m:
        return suffix
    wr, n = (int(g) for g in m.groups())
    return f"m_{{W_{{R}}}}={mass_tev(wr)} TeV, m_{{N}}={mass_tev(n)} TeV"


# 그릴 질량점. 명목 단면적 그대로 (배율 없음).
# 색은 배경 fill (노랑/빨강/초록/파랑) 및 Data 마커(검정 점)와 안 겹치게 골랐다.
# label 을 적으면 그게 쓰이고, 없으면 signal_label() 이 suffix 에서 만든다.
SIGNAL_POINTS = [
    dict(suffix="MWR4000_N2000", color="kBlack",     style=1),   # 실선
    dict(suffix="MWR4000_N200",  color="kMagenta+2", style=2),   # 점선
]
# PLOT_SIGNAL_POINTS="MWR4000_N200,MWR4000_N2000,..." 가 있으면 그 목록으로 바꾼다 (전역 기본값은 그대로).
_SIG_ENV = os.environ.get("PLOT_SIGNAL_POINTS", "").strip()
if _SIG_ENV:
    _SIG_STYLE = [("kBlack", 1), ("kMagenta+2", 2), ("kAzure+2", 1), ("kOrange+7", 2), ("kGray+2", 3), ("kCyan+2", 3)]
    SIGNAL_POINTS = [dict(suffix=sfx.strip(), color=_SIG_STYLE[i % len(_SIG_STYLE)][0], style=_SIG_STYLE[i % len(_SIG_STYLE)][1])
                     for i, sfx in enumerate(_SIG_ENV.split(",")) if sfx.strip()]

# --- 채널 -------------------------------------------------------------------
# data: 이 채널에서 Data 로 취급할 파일 glob. 그 외 데이터 스트림은 통째로 제외한다.
ALL_DATA_GLOBS = ["EGamma*", "Muon*", "SingleMuon*"]

CHANNELS = {
    "EE": {"data": ["EGamma*"],              "label": "ee"},
    "MM": {"data": ["Muon*", "SingleMuon*"], "label": "#mu#mu"},
}

# --- Systematics ------------------------------------------------------------
# 배경 band 에 들어가는 nuisance 전체. datacard 의 배경 모델과 일치시킨다.
#
# theory (ScaleWeight_muF/muR, AlphaS, PDF) 는 datacard 에서 시그널 전용이라 제외 —
# v13 플로터와 같은 선택이다.
#
# v13 목록에 있던 MiniIso 는 제거했다: MCLRSM.yaml 어디에도 없는 죽은 항목이라
# 매 플롯마다 파일을 한 번 더 열고 Central 로 되돌아오기만 했다.
#
# ZPtRw* 는 DY 전용이라 다른 샘플에는 디렉토리가 없다. 그 경우 plotter 가
# Central 로 대체하므로 해당 샘플의 variation 기여는 0 이 된다.
#
# ResolvedDYReshapeBin1-6 / BoostedDYReshapeBin1-3 은 뺐다 (2026-08-21): 8월
# 산출물에 디렉토리가 하나도 없다 (DY 파일의 top-level 키 51개를 직접 확인).
# 이름이 바뀐 게 아니라 안 만들어졌다. 아날라이저에서 R 을 끄는 건 ZptOnly
# userflag 인데 provenance 의 Userflags 는 비어 있으므로, 원래 나왔어야 하는데
# 안 나온 것으로 보인다. 산출물에 R nuisance 가 들어오면 다시 넣을 것.
SYST_LIST = [
    "Pileup",
    "ElectronID", "ElectronReco", "ElectronTrig",
    "ElectronChargeFlip",   # 2026-09-24: HNWR userflag FlipSF (flip SF on all MC, resolved EE); without it Up/Down = Central
    "MuonID", "MuonReco", "MuonTrig", "MuonIso",
    "JER", "JES",
    "ElectronScale", "ElectronRes", "MuonScale", "MuonRes",
    "LSF",
    "ZPtRw_MC_stat", "ZPtRwQCDScale", "ZPtRwQCDPDFError", "ZPtRwQCDPDFAlphaS",
    "ZPtRwEW1", "ZPtRwEW2", "ZPtRwEW3",
    # 2026-08-28: RFlav 재생산에는 R(jet pT) nuisance 디렉토리가 들어 있다 (위 08-21 메모 해제).
    "ResolvedDYReshapeBin1", "ResolvedDYReshapeBin2", "ResolvedDYReshapeBin3",
    "ResolvedDYReshapeBin4", "ResolvedDYReshapeBin5", "ResolvedDYReshapeBin6",
    "BoostedDYReshapeBin1", "BoostedDYReshapeBin2", "BoostedDYReshapeBin3",
]

# --- 리전 -------------------------------------------------------------------
# channels: (스크립트 채널, flavour 태그). flavour 태그는 출력 파일명에 들어가고
# organize_files.py 가 이걸로 폴더를 나눈다.
#
# label2 는 v13 에서 스크립트에 하드코딩된 기본값에 의존했고, plotter.sh 가
# --label2 를 한 번도 넘기지 않아 리전 10개 중 6개가 "Boosted DY CR" 로 잘못
# 찍혀 있었다. 이제 리전마다 명시한다.
REGIONS = [
    dict(key="Boost_DY",      dir="Boost/DY",      prefix="BoostDY",
         label2="Boosted DY CR",            channels=[("EE", "EE"), ("MM", "MM")]),
    dict(key="Boost_DYCR1",   dir="Boost/DYCR1",   prefix="BoostDYCR1",
         label2="Boosted DY CR1 (60-100)",  channels=[("EE", "EE"), ("MM", "MM")]),
    dict(key="Boost_DYCR2",   dir="Boost/DYCR2",   prefix="BoostDYCR2",
         label2="Boosted DY CR2 (100-150)", channels=[("EE", "EE"), ("MM", "MM")]),
    dict(key="Boost_FLV",     dir="Boost/FLV",     prefix="BoostFLV",
         label2="Boosted FLV CR",       channels=[("EE", "EMJ"), ("MM", "MEJ")]),
    dict(key="Boost_sig",     dir="Boost/sig",     prefix="BoostSR",
         label2="Boosted SR",               channels=[("EE", "EE"), ("MM", "MM")]),
    dict(key="Resolve_DY",    dir="Resolve/DY",    prefix="ResolveDY",
         label2="Resolved DY CR",           channels=[("EE", "EE"), ("MM", "MM")]),
    dict(key="Resolve_DYCR1", dir="Resolve/DYCR1", prefix="ResolveDYCR1",
         label2="Resolved DY CR1 (60-100)", channels=[("EE", "EE"), ("MM", "MM")]),
    dict(key="Resolve_DYCR2", dir="Resolve/DYCR2", prefix="ResolveDYCR2",
         label2="Resolved DY CR2 (100-150)", channels=[("EE", "EE"), ("MM", "MM")]),
    dict(key="Resolve_FLV",   dir="Resolve/FLV",   prefix="ResolveFLV",
         label2="Resolved FLV CR",      channels=[("MM", "EM")]),
    dict(key="Resolve_sig",   dir="Resolve/sig",   prefix="ResolveSR",
         label2="Resolved SR",              channels=[("EE", "EE"), ("MM", "MM")]),
]

# FLV 리전의 label1 은 채널이 아니라 최종상태로 정한다.
FLAVOUR_LABELS = {"EE": "ee", "MM": "#mu#mu", "EMJ": "e#mu", "MEJ": "#mu e", "EM": "e#mu"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPEC_DIR = os.path.join(BASE_DIR, "specs")
OUT_DIR = os.path.join(BASE_DIR, "out")


def region_by_key(key):
    for r in REGIONS:
        if r["key"] == key:
            return r
    raise KeyError(f"unknown region key: {key!r}")


def spec_jobs():
    """condor job 단위 목록. job 하나 = 스펙 파일 하나 = (리전, 채널)."""
    jobs = []
    for r in REGIONS:
        for script_ch, flavour in r["channels"]:
            name = f"{r['key']}_{flavour}"
            jobs.append(dict(
                name=name,
                region=r,
                channel=script_ch,
                flavour=flavour,
                label1=FLAVOUR_LABELS[flavour],
                label2=r["label2"],
                spec=os.path.join(SPEC_DIR, name + ".txt"),
                outdir=os.path.join(OUT_DIR, r["dir"]),
            ))
    return jobs


def job_by_name(name):
    for j in spec_jobs():
        if j["name"] == name:
            return j
    raise KeyError(f"unknown job: {name!r}. 가능한 값: "
                   + ", ".join(j["name"] for j in spec_jobs()))


def sample_stem(stem):
    """파일 stem -> 규칙 매칭에 쓸 이름. 이번 산출물이 아니면 None.

    INPUT_PREFIX 가 비어 있으면 아무것도 하지 않는다.
    """
    if INPUT_PREFIX and stem.startswith(INPUT_PREFIX):
        stem = stem[len(INPUT_PREFIX):]
    elif INPUT_PREFIX and not any(fnmatch.fnmatch(stem, g) for g in UNPREFIXED_GLOBS):
        return None
    if any(fnmatch.fnmatch(stem, g) for g in DROP_GLOBS):
        return None
    return stem


def is_signal(stem):
    return any(fnmatch.fnmatch(stem, g) for g in SIGNAL_GLOBS)


def signal_files(channel, input_dir=None):
    """SIGNAL_POINTS -> [(label, path, color, style)]. 없는 파일은 뺀다.

    파일이 빠져도 예외를 내지 않는다 — 부르는 쪽이 경고만 하고 나머지를 그린다.
    """
    tag = SIGNAL_CHANNEL_TAG.get(channel)
    if not tag:
        return []
    base = input_dir or INPUT_DIR
    out = []
    for pt in SIGNAL_POINTS:
        label = pt.get("label") or signal_label(pt["suffix"])
        fname = f"{INPUT_PREFIX}{tag}_{pt['suffix']}.root"
        path = os.path.join(base, fname)
        if os.path.isfile(path):
            out.append((label, path, pt["color"], pt["style"]))
        else:
            out.append((label, None, pt["color"], pt["style"]))
    return out


def classify_sample(stem):
    """파일 stem -> (group, matched_rule). 미분류면 (None, None)."""
    for pattern, group in SAMPLE_RULES:
        if fnmatch.fnmatch(stem, pattern):
            return group, pattern
    return None, None


def is_data(stem, globs=None):
    for g in (globs if globs is not None else ALL_DATA_GLOBS):
        if fnmatch.fnmatch(stem, g):
            return True
    return False
