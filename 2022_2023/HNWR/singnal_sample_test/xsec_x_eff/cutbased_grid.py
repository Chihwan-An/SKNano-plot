#!/usr/bin/env python3
"""
cutbased_grid.py — cut-based 분석의 (m_WR, m_N) 2D mass-grid 요약.

채널(EE, MM)마다 아래를 그리고 CSV로 남긴다:
  * acceptance         : total / boosted / resolved
  * cross section × acceptance (fb)
  * Asimov significance: SR 전체 yield 기준, Z_total = sqrt(Z_boost^2 + Z_resolve^2)

정의
----
  denom      = Central/Cutflow_for_reseolved_SR.values()[1]   # 모든 이벤트 (= xsec x L_eff)
  S_boost    = integral( Central/SR_Boosted_<CH>_mlljj )      # 최종 boosted SR yield
  S_resolve  = integral( Central/SR_Resolved_<CH>_mlljj )     # 최종 resolved SR yield
  A_<reg>    = S_<reg> / denom,   A_total = A_boost + A_resolve

cutflow bin 대신 SR_*_mlljj 적분을 쓰는 이유: cutflow 히스토그램은 flavor-inclusive라
채널 분리가 안 되고 마지막 scale factor 적용 전 값이다. SR_*_mlljj는 채널별로 나뉘어
있고 SF가 모두 반영된 최종 SR yield다.

주의: FillHist(name, binN, ...) 는 값 binN 을 ROOT bin index binN 에 넣으므로
values()[0] 은 항상 비어 있다 -> "All" 은 index 1.

Usage:
  python cutbased_grid.py --outdir output/cutbased
  python cutbased_grid.py --outdir output/cutbased_common --grid common
"""

import argparse
import os
import re

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import numpy as np
import uproot

import grid_common as gc

SIG_DIR = "/gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy/combined_22_23/merged"
BKG_DIR = SIG_DIR

DENOM_HIST = "Central/Cutflow_for_reseolved_SR"
SR_HIST = {
    "boost":   "Central/SR_Boosted_{ch}_mlljj",
    "resolve": "Central/SR_Resolved_{ch}_mlljj",
}

# 배경 합산에서 제외할 파일명 토큰.
#   EGamma/Muon/SingleMuon = data,  Skim = 스킴 산출물,
#   DYJets = inclusive aMC@NLO 샘플 (HT-binned DYMLL* 와 이중계산됨).
# plots/HNWR/reproduce/syst_plotter/integrated/plotter_file/year_sep/EE.py:44 와 같은 규약.
BKG_EXCLUDE = ("Skim", "EGamma", "Muon", "SingleMuon", "DYJets")

FILE_RE = re.compile(r"^(WR\d+N\d+(?:EE|MM))\.root$")

# denom/L 이 이론 xsec의 이 비율보다 낮으면 merge에 era가 빠진 것으로 보고
# significance를 비운다 (S만 lumi가 모자라고 B는 full lumi라 Z가 왜곡되므로).
# acceptance와 sigma x A 는 비율이라 그대로 유효하다.
MIN_LUMI_FRAC = 0.95

CSV_COLUMNS = [
    "method", "channel", "mWR", "mN", "xsec_pb", "denom", "denom_over_lumi_pb",
    "lumi_frac", "s_boost", "s_resolve", "s_total",
    "b_boost", "b_resolve",
    "acc_boost", "acc_resolve", "acc_total",
    "acc_boost_pct", "acc_resolve_pct", "acc_total_pct",
    "xsec_acc_boost_fb", "xsec_acc_resolve_fb", "xsec_acc_total_fb",
    "z_boost", "z_resolve", "z_total",
    "z_boost_shape", "z_resolve_shape", "z_total_shape",
]

# mlljj shape Z용 rebin. 원본 히스토그램은 0-8000 GeV를 1 GeV로 자른 8000 bin이라
# bin당 배경이 0에 가까워 그대로는 Asimov Z가 발산한다. BDT 쪽의 "score bin 합산 Z"와
# 같은 축에서 비교하려면 shape 정보를 남기되 통계가 있는 폭으로 묶어야 한다.
# 먼저 SHAPE_BINS 개로 균등 rebin한 뒤, 배경이 MIN_SHAPE_BKG 미만인 bin은
# 이웃과 합친다 (BDT 템플릿의 background Neff 가드와 같은 취지 —
# make_fit_template.py:apply_neff_guard).
SHAPE_BINS = 160
MIN_SHAPE_BKG = 1.0


def hist_values(directory, name):
    """flow 포함 bin 값 배열. 히스토그램이 없으면 None (= 이벤트 0개)."""
    try:
        hist = directory[name]
    except (KeyError, uproot.KeyInFileError):
        return None
    return np.asarray(hist.values(flow=True), dtype=float)


def hist_integral(directory, name):
    """overflow/underflow 포함 적분. 히스토그램이 없으면 0.0."""
    vals = hist_values(directory, name)
    return 0.0 if vals is None else float(vals.sum())


def rebin(values, nbins):
    """flow 포함 배열을 nbins 개로 균등 묶음 (남는 bin은 마지막에 붙인다)."""
    values = np.asarray(values, dtype=float)
    step = max(1, len(values) // nbins)
    out = [values[i:i + step].sum() for i in range(0, len(values), step)]
    if len(out) > nbins:
        head, tail = out[:nbins - 1], out[nbins - 1:]
        out = head + [float(np.sum(tail))]
    return np.asarray(out, dtype=float)


def merge_groups(bkg_vals, min_bkg=MIN_SHAPE_BKG):
    """배경이 min_bkg 이상 쌓일 때까지 연속 bin을 묶는 그룹 경계 [(lo, hi), …].

    이 그룹은 배경만 보고 정하므로 mass point에 무관하고, 모든 신호에 같은 비닝이
    적용된다. 남는 꼬리는 마지막 그룹에 붙인다.
    """
    groups = []
    start = 0
    acc = 0.0
    for i, v in enumerate(bkg_vals):
        acc += float(v)
        if acc >= min_bkg:
            groups.append((start, i + 1))
            start = i + 1
            acc = 0.0
    if start < len(bkg_vals):
        if groups:
            groups[-1] = (groups[-1][0], len(bkg_vals))
        else:
            groups = [(0, len(bkg_vals))]
    return groups


def apply_groups(vals, groups):
    return np.asarray([float(np.sum(vals[lo:hi])) for lo, hi in groups], dtype=float)


def read_signal(path, channel, shape_bins):
    """(denom, {region: (yield, rebinned mlljj)}). 읽을 수 없으면 None."""
    try:
        with uproot.open(path) as f:
            if "Central" not in f:
                print(f"[WARN] no 'Central' directory: {path}")
                return None
            denom = float(np.asarray(f[DENOM_HIST].values(), dtype=float)[1])
            out = {}
            for region in ("boost", "resolve"):
                vals = hist_values(f, SR_HIST[region].format(ch=channel))
                if vals is None:
                    out[region] = (0.0, np.zeros(shape_bins))
                else:
                    out[region] = (float(vals.sum()), rebin(vals, shape_bins))
    except Exception as exc:                                    # noqa: BLE001
        print(f"[WARN] failed to read {path}: {exc}")
        return None
    return denom, out


def list_background_files(bkg_dir):
    files = []
    for name in sorted(os.listdir(bkg_dir)):
        if not name.endswith(".root") or name.startswith("WR"):
            continue
        if any(tok in name for tok in BKG_EXCLUDE):
            continue
        files.append(os.path.join(bkg_dir, name))
    return files


def load_background(bkg_dir, shape_bins):
    """{(channel, region): (yield, rebinned mlljj)} — mass point에 무관하므로 한 번만."""
    files = list_background_files(bkg_dir)
    if not files:
        raise RuntimeError(f"No background ROOT files under {bkg_dir}")

    keys = [(ch, reg) for ch in gc.CHANNELS for reg in ("boost", "resolve")]
    totals = {k: 0.0 for k in keys}
    shapes = {k: np.zeros(shape_bins) for k in keys}
    for path in files:
        try:
            with uproot.open(path) as f:
                if "Central" not in f:
                    continue
                for ch, reg in keys:
                    vals = hist_values(f, SR_HIST[reg].format(ch=ch))
                    if vals is None:
                        continue
                    totals[(ch, reg)] += float(vals.sum())
                    shapes[(ch, reg)] += rebin(vals, shape_bins)
        except Exception as exc:                                # noqa: BLE001
            print(f"[WARN] failed to read background {path}: {exc}")

    print(f"[INFO] background: {len(files)} MC files")
    out = {}
    for key in keys:
        groups = merge_groups(shapes[key])
        out[key] = (totals[key], apply_groups(shapes[key], groups), groups)
        print(f"       B[{key[0]}, {key[1]}] = {totals[key]:.1f}"
              f"   ({len(groups)} shape bins after the B>={MIN_SHAPE_BKG:g} merge)")
    return out


def collect(sig_dir, bkg_dir, xsec, grid, check_xsec, shape_bins=SHAPE_BINS,
            wr_values=None):
    bkg = load_background(bkg_dir, shape_bins)

    rows = []
    warned = 0
    for name in sorted(os.listdir(sig_dir)):
        m = FILE_RE.match(name)
        if not m:
            continue
        parsed = gc.parse_masspoint(m.group(1))
        if parsed is None:
            continue
        mWR, mN, channel = parsed
        if wr_values and mWR not in wr_values:
            continue
        if grid == "common" and not gc.in_common_grid(mWR, mN):
            continue

        res = read_signal(os.path.join(sig_dir, name), channel, shape_bins)
        if res is None:
            continue
        denom, sig_hist = res
        s_boost = sig_hist["boost"][0]
        s_resolve = sig_hist["resolve"][0]
        if denom <= 0:
            print(f"[WARN] empty denominator for {name}")
            continue

        sigma = xsec.get((mWR, mN, channel))
        if sigma is None:
            print(f"[WARN] no xsec for WR{mWR}N{mN}{channel}")
            continue

        acc_boost = s_boost / denom
        acc_resolve = s_resolve / denom
        acc_total = acc_boost + acc_resolve

        z_boost = gc.asimov_z(s_boost, bkg[(channel, "boost")][0])
        z_resolve = gc.asimov_z(s_resolve, bkg[(channel, "resolve")][0])
        z_boost_shape = gc.binned_asimov_z(
            apply_groups(sig_hist["boost"][1], bkg[(channel, "boost")][2]),
            bkg[(channel, "boost")][1])
        z_resolve_shape = gc.binned_asimov_z(
            apply_groups(sig_hist["resolve"][1], bkg[(channel, "resolve")][2]),
            bkg[(channel, "resolve")][1])

        denom_over_lumi = denom / (gc.LUMI_FB * 1000.0)          # pb
        lumi_frac = denom_over_lumi / sigma if sigma > 0 else np.nan
        if lumi_frac < MIN_LUMI_FRAC:
            print(f"[WARN] WR{mWR}N{mN}{channel}: only {lumi_frac * 100:.0f}% of the "
                  f"expected luminosity is present (incomplete merge) — Z left blank")
            z_boost = z_resolve = np.nan
            z_boost_shape = z_resolve_shape = np.nan
        if check_xsec and sigma > 0:
            dev = abs(denom_over_lumi - sigma) / sigma
            if dev > 0.01:
                warned += 1
                print(f"[CHECK] WR{mWR}N{mN}{channel}: denom/L = {denom_over_lumi:.5g} pb "
                      f"vs xsec = {sigma:.5g} pb  ({dev * 100:.1f}% off)")

        rows.append({
            "method": "cutbased",
            "channel": channel, "mWR": mWR, "mN": mN,
            "xsec_pb": sigma, "denom": denom, "denom_over_lumi_pb": denom_over_lumi,
            "lumi_frac": lumi_frac,
            "s_boost": s_boost, "s_resolve": s_resolve, "s_total": s_boost + s_resolve,
            "b_boost": bkg[(channel, "boost")][0],
            "b_resolve": bkg[(channel, "resolve")][0],
            "acc_boost": acc_boost, "acc_resolve": acc_resolve, "acc_total": acc_total,
            "acc_boost_pct": acc_boost * 100.0,
            "acc_resolve_pct": acc_resolve * 100.0,
            "acc_total_pct": acc_total * 100.0,
            "xsec_acc_boost_fb": sigma * acc_boost * 1000.0,
            "xsec_acc_resolve_fb": sigma * acc_resolve * 1000.0,
            "xsec_acc_total_fb": sigma * acc_total * 1000.0,
            "z_boost": z_boost, "z_resolve": z_resolve,
            "z_total": gc.combine_z(z_boost, z_resolve),
            # BDT의 "score bin 합산 Z"와 같은 축에서 비교하기 위한 mlljj shape Z.
            # 플롯에는 쓰지 않고 CSV에만 남긴다.
            "z_boost_shape": z_boost_shape, "z_resolve_shape": z_resolve_shape,
            "z_total_shape": gc.combine_z(z_boost_shape, z_resolve_shape),
        })

    if check_xsec:
        print(f"[CHECK] {warned}/{len(rows)} points deviate from the theory xsec by >1%")
    return rows


# ------------------------------------------------------------------ 플롯
PLOTS = [
    # (key, 파일명 조각, 제목 조각, colorbar 라벨, log?, 주석 형식, cmap)
    ("acc_total_pct",   "acceptance_total",   "Total acceptance",
     "Acceptance [%]", False, "plain", "magma"),
    ("acc_boost_pct",   "acceptance_boost",   "Boosted acceptance",
     "Acceptance [%]", False, "plain", "magma"),
    ("acc_resolve_pct", "acceptance_resolve", "Resolved acceptance",
     "Acceptance [%]", False, "plain", "magma"),
    ("xsec_acc_total_fb",   "xsec_times_acc_total",   r"$\sigma\times A$ (total)",
     r"$\sigma\times A$ [fb]", True, "sci", "viridis"),
    ("xsec_acc_boost_fb",   "xsec_times_acc_boost",   r"$\sigma\times A$ (boosted)",
     r"$\sigma\times A$ [fb]", True, "sci", "viridis"),
    ("xsec_acc_resolve_fb", "xsec_times_acc_resolve", r"$\sigma\times A$ (resolved)",
     r"$\sigma\times A$ [fb]", True, "sci", "viridis"),
    ("z_total", "significance_total", "Asimov significance (total)",
     r"Asimov $Z$", True, "sci", "plasma"),
]


def make_plots(rows, outdir, style, label="Cut-based"):
    by_channel = {ch: [r for r in rows if r["channel"] == ch] for ch in gc.CHANNELS}

    for key, fname, title, cbar, logz, kind, cmap in PLOTS:
        norm = gc.shared_norm(by_channel.values(), key, logz=logz)
        for ch in gc.CHANNELS:
            if not by_channel[ch]:
                continue
            gc.make_grid_figure(
                by_channel[ch], key,
                f"{label} — {title}  ({ch})", cbar,
                os.path.join(outdir, f"{fname}_{ch}.png"),
                cmap=cmap, logz=logz, norm=norm, annotate_kind=kind, style=style,
            )

    make_summary(by_channel, outdir, style, label)


def make_summary(by_channel, outdir, style, label):
    import matplotlib.pyplot as plt

    for ch, rows in by_channel.items():
        if not rows:
            continue
        fig, axes = plt.subplots(2, 4, figsize=(28, 20))
        flat = axes.flatten()
        for ax, (key, _f, title, cbar, logz, kind, cmap) in zip(flat, PLOTS):
            gc.draw_grid(ax, rows, key, title, cbar, cmap=cmap, logz=logz,
                         annotate_kind=kind, style=style, annotate_fontsize=5.0)
        flat[len(PLOTS)].axis("off")
        fig.suptitle(f"{label} mass-grid summary — {ch}", fontsize=17, fontweight="bold")
        gc.stamp_lumi(fig)
        fig.tight_layout(rect=(0, 0, 1, 0.96))
        path = os.path.join(outdir, f"summary_{ch}.png")
        fig.savefig(path, dpi=130, bbox_inches="tight")
        plt.close(fig)
        print(f"[OK] {path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sig-dir", default=SIG_DIR)
    ap.add_argument("--bkg-dir", default=BKG_DIR)
    ap.add_argument("--outdir", default="output/cutbased")
    ap.add_argument("--style", default="scatter", choices=["scatter", "mesh"])
    ap.add_argument("--grid", default="all", choices=["all", "common"],
                    help="'common' = BDT와 겹치는 mass point만 (WR 2000/4000/6000/8000 x 홀수-백 N)")
    ap.add_argument("--check-xsec", action="store_true",
                    help="denom/L 이 이론 xsec과 1% 이내로 맞는지 검사")
    ap.add_argument("--shape-bins", type=int, default=SHAPE_BINS,
                    help="CSV의 z_*_shape 용 mlljj rebin 개수 (0-8000 GeV 균등)")
    ap.add_argument("--wr", nargs="+", type=int, default=list(gc.DEFAULT_WR),
                    help="쓸 m_WR 값. 기본은 제대로 스캔한 2000/4000/6000/8000 "
                         "(3000/5000/7000은 N 점이 1~2개뿐이라 제외). "
                         "0 을 주면 전부 포함")
    ap.add_argument("--csv-only", action="store_true")
    args = ap.parse_args()

    wr_values = None if args.wr == [0] else set(args.wr)
    xsec = gc.load_xsec()
    rows = collect(args.sig_dir, args.bkg_dir, xsec, args.grid, args.check_xsec,
                   shape_bins=args.shape_bins, wr_values=wr_values)
    if not rows:
        raise SystemExit("no mass points collected")

    os.makedirs(args.outdir, exist_ok=True)
    gc.save_csv(rows, os.path.join(args.outdir, "cutbased_grid.csv"), CSV_COLUMNS)
    if not args.csv_only:
        make_plots(rows, args.outdir, args.style)


if __name__ == "__main__":
    main()
