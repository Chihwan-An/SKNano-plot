#!/usr/bin/env python3
"""
bdt_grid.py — BDT 분석의 (m_WR, m_N) 2D mass-grid 요약. cutbased_grid.py 의 짝.

채널(EE, MM)마다 아래를 그리고 CSV로 남긴다:
  * acceptance         : BDT score > 0.5 이상, total / boosted / resolved
  * cross section × acceptance (fb)
  * Asimov significance: score bin별 Z를 quadrature 합산, Z_total = sqrt(Z_b^2 + Z_r^2)

정의
----
  denom     = Sum_era Central/Cutflow.values()[0]          # 모든 이벤트 (= xsec x L_eff)
              (HNWR_BDT_presel ntuple. cut-based 와 달리 bin 0 부터 채운다)
  S_<cat>   = Sum_era Sum_{score>cut} signal               # fit template
  B_<cat>   = Sum_era Sum_{score>cut} (DYJets+TT+Nonprompt+Others)
  A_<cat>   = S_<cat> / denom,   A_total = A_boost + A_resolve

significance는 CSV에 세 가지를 모두 남긴다:
  z_<cat>_allbins  10 bin 전부의 bin별 Z를 quadrature 합산  <- 플롯에 쓰는 주값
  z_<cat>_gt0p5    score cut 위쪽 bin만 같은 방식으로 합산   (acceptance 정의와 정합)
  z_<cat>_incl     score cut 위쪽을 하나의 yield로 묶은 Z

검증됨 (WR2000N1100EE, 2023): presel Cutflow bin 6(resolved) = 751.62 이고
resolved fit template의 signal 총적분 = 751.622 -> 분모/분자가 같은 weighting 체계.

Usage:
  python bdt_grid.py --outdir output/bdt
  python bdt_grid.py --outdir output/bdt_common --grid common
"""

import argparse
import os
import re

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import numpy as np
import uproot

import grid_common as gc
from cutbased_grid import make_plots      # 플롯 세트(PLOTS)를 그대로 공유한다

TEMPLATE_BASE = ("/data6/Users/achihwan/SKNanoAnalyzer-v13/BDT/SR"
                 "/all_mass_point_uniform/nb10")
PRESEL_BASE = "/gv0/Users/achihwan/SKNanoOutput/HNWR_BDT_presel"
ERAS = ("2022", "2022EE", "2023", "2023BPix")

# BDT 쪽 카테고리/채널 이름 -> 이 스크립트의 공통 이름
CATEGORY = {"boost": "boosted", "resolve": "resolved"}
TEMPLATE_CHANNEL = {"EE": "electron", "MM": "muon"}

BACKGROUND_KEYS = ("DYJets", "TT", "Nonprompt", "Others")

# HNWR_BDT_presel 의 Central/Cutflow bin (Tools/scripts/cutflow.py:60 CUT_LABELS)
PRESEL_ALL_BIN = 0
PRESEL_SR_BIN = {"resolve": 6, "boost": 7}

TEMPLATE_RE = re.compile(r"^fit_template_(?:electron|muon)_(WR\d+N\d+)\.root$")

CSV_COLUMNS = [
    "method", "channel", "mWR", "mN", "score_cut", "xsec_pb",
    "denom", "denom_over_lumi_pb", "lumi_frac", "n_eras",
    "s_boost", "s_resolve", "s_total", "b_boost", "b_resolve",
    "acc_boost", "acc_resolve", "acc_total",
    "acc_boost_pct", "acc_resolve_pct", "acc_total_pct",
    "xsec_acc_boost_fb", "xsec_acc_resolve_fb", "xsec_acc_total_fb",
    "z_boost", "z_resolve", "z_total",
    "z_boost_allbins", "z_resolve_allbins", "z_total_allbins",
    "z_boost_gt0p5", "z_resolve_gt0p5", "z_total_gt0p5",
    "z_boost_incl", "z_resolve_incl", "z_total_incl",
    "presel_sr_boost", "presel_sr_resolve",
]

MIN_LUMI_FRAC = 0.95


def template_path(base, era, region, channel, masspoint):
    return os.path.join(base, era, "fit_templates", CATEGORY[region],
                        TEMPLATE_CHANNEL[channel],
                        f"fit_template_{TEMPLATE_CHANNEL[channel]}_{masspoint}.root")


def read_template(path):
    """(edges, signal, background) — 히스토그램이 없으면 None."""
    try:
        with uproot.open(path) as f:
            sig = np.asarray(f["signal"].values(), dtype=float)
            edges = np.asarray(f["signal"].axis().edges(), dtype=float)
            bkg = np.zeros_like(sig)
            for key in BACKGROUND_KEYS:
                if key in [k.split(";")[0] for k in f.keys()]:
                    bkg += np.asarray(f[key].values(), dtype=float)
    except Exception as exc:                                    # noqa: BLE001
        print(f"[WARN] failed to read {path}: {exc}")
        return None
    return edges, sig, bkg


def read_presel_cutflow(presel_base, era, channel, masspoint):
    """(all_events, SR_resolve, SR_boost) — 파일이 없으면 None."""
    path = os.path.join(presel_base, era, "sig", channel, f"{masspoint}{channel}.root")
    if not os.path.exists(path):
        return None
    try:
        with uproot.open(path) as f:
            vals = np.asarray(f["Central/Cutflow"].values(), dtype=float)
    except Exception as exc:                                    # noqa: BLE001
        print(f"[WARN] failed to read {path}: {exc}")
        return None
    return (vals[PRESEL_ALL_BIN],
            vals[PRESEL_SR_BIN["resolve"]],
            vals[PRESEL_SR_BIN["boost"]])


def list_masspoints(base, era, channel):
    """(era, channel) 에서 resolved/boosted 템플릿이 모두 있는 mass point stem."""
    stems = None
    for region in ("resolve", "boost"):
        d = os.path.join(base, era, "fit_templates", CATEGORY[region],
                         TEMPLATE_CHANNEL[channel])
        if not os.path.isdir(d):
            return set()
        here = {m.group(1) for m in
                (TEMPLATE_RE.match(n) for n in os.listdir(d)) if m}
        stems = here if stems is None else (stems & here)
    return stems or set()


def collect(base, presel_base, eras, channels, score_cut, xsec, grid, check_templates,
            wr_values=None):
    rows = []
    checked = 0

    for channel in channels:
        # era별 mass point 목록의 합집합 (era마다 빠진 점이 있을 수 있다)
        per_era = {e: list_masspoints(base, e, channel) for e in eras}
        all_stems = sorted(set().union(*per_era.values())) if per_era else []

        for stem in all_stems:
            m = re.match(r"^WR(\d+)N(\d+)$", stem)
            if not m:
                continue
            mWR, mN = int(m.group(1)), int(m.group(2))
            if wr_values and mWR not in wr_values:
                continue
            if grid == "common" and not gc.in_common_grid(mWR, mN):
                continue

            sigma = xsec.get((mWR, mN, channel))
            if sigma is None:
                print(f"[WARN] no xsec for {stem}{channel}")
                continue

            denom = 0.0
            n_eras = 0
            presel_sr = {"boost": 0.0, "resolve": 0.0}
            sig_bins = {"boost": None, "resolve": None}
            bkg_bins = {"boost": None, "resolve": None}
            edges = None
            missing = False

            for era in eras:
                if stem not in per_era[era]:
                    continue
                cut = read_presel_cutflow(presel_base, era, channel, stem)
                if cut is None:
                    print(f"[WARN] no presel ntuple for {stem}{channel} / {era}")
                    missing = True
                    continue
                denom += cut[0]
                presel_sr["resolve"] += cut[1]
                presel_sr["boost"] += cut[2]
                n_eras += 1

                for region in ("boost", "resolve"):
                    res = read_template(template_path(base, era, region, channel, stem))
                    if res is None:
                        missing = True
                        continue
                    e, s, b = res
                    edges = e if edges is None else edges
                    sig_bins[region] = s if sig_bins[region] is None else sig_bins[region] + s
                    bkg_bins[region] = b if bkg_bins[region] is None else bkg_bins[region] + b

            if denom <= 0 or edges is None or any(v is None for v in sig_bins.values()):
                print(f"[WARN] incomplete inputs for {stem}{channel} — skipped")
                continue
            if missing:
                print(f"[WARN] {stem}{channel}: some eras missing (used {n_eras}/{len(eras)})")

            # score > cut 인 bin (bin의 하한이 cut 이상)
            above = edges[:-1] >= score_cut - 1e-9

            acc, s_cut, b_cut = {}, {}, {}
            z_all, z_above, z_incl = {}, {}, {}
            for region in ("boost", "resolve"):
                s_arr, b_arr = sig_bins[region], bkg_bins[region]
                s_cut[region] = float(s_arr[above].sum())
                b_cut[region] = float(b_arr[above].sum())
                acc[region] = s_cut[region] / denom
                z_all[region] = gc.binned_asimov_z(s_arr, b_arr)
                z_above[region] = gc.binned_asimov_z(s_arr[above], b_arr[above])
                z_incl[region] = gc.asimov_z(s_cut[region], b_cut[region])

            if check_templates:
                # 템플릿 총적분이 presel cutflow의 SR bin과 맞는지 (전 bin 합)
                for region in ("boost", "resolve"):
                    tot = float(sig_bins[region].sum())
                    ref = presel_sr[region]
                    if ref > 0 and abs(tot - ref) / ref > 0.01:
                        print(f"[CHECK] {stem}{channel} {region}: template {tot:.4g} "
                              f"vs presel SR bin {ref:.4g}")
                        checked += 1

            denom_over_lumi = denom / (gc.LUMI_FB * 1000.0)
            lumi_frac = denom_over_lumi / sigma if sigma > 0 else np.nan
            if lumi_frac < MIN_LUMI_FRAC:
                print(f"[WARN] {stem}{channel}: only {lumi_frac * 100:.0f}% of the "
                      f"expected luminosity is present — Z left blank")
                for d in (z_all, z_above, z_incl):
                    d["boost"] = d["resolve"] = np.nan

            acc_total = acc["boost"] + acc["resolve"]
            rows.append({
                "method": "bdt", "channel": channel, "mWR": mWR, "mN": mN,
                "score_cut": score_cut, "xsec_pb": sigma,
                "denom": denom, "denom_over_lumi_pb": denom_over_lumi,
                "lumi_frac": lumi_frac, "n_eras": n_eras,
                "s_boost": s_cut["boost"], "s_resolve": s_cut["resolve"],
                "s_total": s_cut["boost"] + s_cut["resolve"],
                "b_boost": b_cut["boost"], "b_resolve": b_cut["resolve"],
                "acc_boost": acc["boost"], "acc_resolve": acc["resolve"],
                "acc_total": acc_total,
                "acc_boost_pct": acc["boost"] * 100.0,
                "acc_resolve_pct": acc["resolve"] * 100.0,
                "acc_total_pct": acc_total * 100.0,
                "xsec_acc_boost_fb": sigma * acc["boost"] * 1000.0,
                "xsec_acc_resolve_fb": sigma * acc["resolve"] * 1000.0,
                "xsec_acc_total_fb": sigma * acc_total * 1000.0,
                # 플롯에 쓰는 주값 = 전 bin quadrature 합산
                "z_boost": z_all["boost"], "z_resolve": z_all["resolve"],
                "z_total": gc.combine_z(z_all["boost"], z_all["resolve"]),
                "z_boost_allbins": z_all["boost"], "z_resolve_allbins": z_all["resolve"],
                "z_total_allbins": gc.combine_z(z_all["boost"], z_all["resolve"]),
                "z_boost_gt0p5": z_above["boost"], "z_resolve_gt0p5": z_above["resolve"],
                "z_total_gt0p5": gc.combine_z(z_above["boost"], z_above["resolve"]),
                "z_boost_incl": z_incl["boost"], "z_resolve_incl": z_incl["resolve"],
                "z_total_incl": gc.combine_z(z_incl["boost"], z_incl["resolve"]),
                "presel_sr_boost": presel_sr["boost"],
                "presel_sr_resolve": presel_sr["resolve"],
            })

    if check_templates:
        print(f"[CHECK] {checked} template/presel mismatches above 1%")
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--template-base", default=TEMPLATE_BASE)
    ap.add_argument("--presel-base", default=PRESEL_BASE)
    ap.add_argument("--eras", nargs="+", default=list(ERAS))
    ap.add_argument("--channels", nargs="+", default=list(gc.CHANNELS),
                    choices=list(gc.CHANNELS))
    ap.add_argument("--score-cut", type=float, default=0.5)
    ap.add_argument("--outdir", default="output/bdt")
    ap.add_argument("--style", default="scatter", choices=["scatter", "mesh"])
    ap.add_argument("--grid", default="all", choices=["all", "common"])
    ap.add_argument("--check-templates", action="store_true",
                    help="fit template 총적분이 presel Cutflow의 SR bin과 맞는지 검사")
    ap.add_argument("--wr", nargs="+", type=int, default=list(gc.DEFAULT_WR),
                    help="쓸 m_WR 값. 0 을 주면 전부 포함")
    ap.add_argument("--csv-only", action="store_true")
    args = ap.parse_args()

    wr_values = None if args.wr == [0] else set(args.wr)
    xsec = gc.load_xsec()
    rows = collect(args.template_base, args.presel_base, args.eras, args.channels,
                   args.score_cut, xsec, args.grid, args.check_templates,
                   wr_values=wr_values)
    if not rows:
        raise SystemExit("no mass points collected")

    os.makedirs(args.outdir, exist_ok=True)
    gc.save_csv(rows, os.path.join(args.outdir, "bdt_grid.csv"), CSV_COLUMNS)
    if not args.csv_only:
        make_plots(rows, args.outdir, args.style,
                   label=f"BDT (score > {args.score_cut:g})")


if __name__ == "__main__":
    main()
