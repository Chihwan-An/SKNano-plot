#!/usr/bin/env python3
"""출력 파일 이름 -> 폴더 경로.

v13 의 charge_inclusive_year_combined 산출물과 같은 계층을 쓴다.

  out/<Boost|Resolve>/<리전>/<flavour>/<오브젝트>/<OS|SS|Inclusive>/

v13 은 플롯을 리전 폴더에 평평하게 떨군 뒤 organize_files.py 로 나중에 옮겼다.
그래서 (a) 스크립트를 안 돌리면 정리가 안 되고, (b) 이어서 돌릴 때 쓰는
--skip-existing 이 이미 옮겨간 png 를 못 찾아 전부 다시 그렸다. 이제 plotter 가
처음부터 최종 위치에 쓰고, organize_files.py 는 예전 산출물 정리용으로만 남는다.
"""

import os
import re

import config

# 파일명의 flavour 태그 -> 폴더명
FLAVOR_MAP = {
    "EMJ": "E_Mu",
    "MEJ": "Mu_E",
    "MM":  "MM",
    "EE":  "EE",
    "EM":  "E_Mu",
}

# 긴 태그부터 확인해야 EM 이 EMJ 를 가로채지 않는다.
FLAVOR_ORDER = ("EMJ", "MEJ", "MM", "EE", "EM")

# 플롯 하나가 파일 셋을 만든다: <out>.tsv, <out>_integrated.tsv, <out>_plot.png.
# 이미 붙은 파일명을 넘겨도 같은 폴더가 나오도록 접미사를 떼고 본다.
NAME_SUFFIXES = ("_plot", "_integrated")

# 리전 prefix 는 서로 접두사 관계다 (BoostDY ⊂ BoostDYCR1). 긴 것부터 본다.
_PREFIXES = sorted((r["prefix"] for r in config.REGIONS), key=len, reverse=True)


def classify_variable(var):
    """변수명 -> 오브젝트 타입 폴더 (OS_/SS_ prefix 는 떼고 판단)."""
    pure = re.sub(r"^(OS_|SS_)(tight_)?", "", var)

    if pure in ("punum", "pv", "pvgood"):
        return "pileup"
    if re.match(r"(leading|subleading)_lep_", pure) or pure == "leadlep_lsf":
        return "lepton"
    if re.match(r"(leading|subleading)_(jet|fatjet)", pure):
        return "jet"
    if re.match(r"fatjet_|j1j2_|deltaR_|dphi_", pure) or pure == "jetnum":
        return "jet"
    # BoostSR*_Dilepton_pt 처럼 대문자로 쓴 것도 있어 대소문자를 가리지 않는다.
    if re.match(r"[Dd]ilepton_", pure) or pure in ("mll", "ll_pt", "pt", "eta", "phi", "mass"):
        return "dilepton"
    # HT = pT(l1)+pT(l2)+pT(j1)+pT(j2) (HNWR userflag HTHist, 2026-10-02)
    if re.match(r"WR_|WRMass|mlljj|l1j1j2_|l2j1j2_", pure) or pure == "HT":
        return "jet_lepton"
    return "other"


def sign_of(var):
    """변수명 -> OS / SS / Inclusive."""
    # OS_tight_/SS_tight_: both leptons pass the tight-charge requirement
    # (HNWR DYCR_*_{OS,SS}_2e_tight_* / _{OS,SS}_tight_*), own folders next to OS/SS.
    if var.startswith("OS_tight_"):
        return "OS_tight"
    if var.startswith("SS_tight_"):
        return "SS_tight"
    if var.startswith("OS_"):
        return "OS"
    if var.startswith("SS_"):
        return "SS"
    return "Inclusive"


def split_name(name, prefix=None):
    """'BoostSREE_WRMass' -> ('EE', 'WRMass'). 못 알아보면 (None, None).

    prefix 를 주면 그 리전만, 안 주면 config.REGIONS 의 prefix 를 긴 것부터
    시도한다. 확장자와 _plot/_integrated 접미사는 떼고 본다.
    """
    stem = os.path.splitext(name)[0]
    for suffix in NAME_SUFFIXES:
        if stem.endswith(suffix):
            stem = stem[:-len(suffix)]
            break

    for pref in ([prefix] if prefix else _PREFIXES):
        if not stem.startswith(pref):
            continue
        rest = stem[len(pref):]
        for tag in FLAVOR_ORDER:
            if rest.startswith(tag + "_"):
                return tag, rest[len(tag) + 1:]
    return None, None


def subdir(name, prefix=None):
    """'BoostSREE_WRMass' -> 'EE/jet_lepton/Inclusive'. 못 알아보면 None.

    None 을 돌려주면 부르는 쪽이 리전 폴더에 그대로 쓴다 — 분류를 못 한다고
    플롯을 잃는 것보다 낫다.
    """
    tag, var = split_name(name, prefix)
    if tag is None:
        return None
    flavour = FLAVOR_MAP.get(tag)
    if flavour is None:
        return None
    return os.path.join(flavour, classify_variable(var), sign_of(var))


def resolve_outdir(outdir, name, prefix=None):
    """(리전 폴더, 출력 이름) -> 실제로 쓸 폴더. 없으면 만든다."""
    sub = subdir(name, prefix)
    dest = os.path.join(outdir, sub) if sub else outdir
    os.makedirs(dest, exist_ok=True)
    return dest
