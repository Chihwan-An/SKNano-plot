#!/usr/bin/env python3
"""
grid_common.py — (m_WR, m_N) mass-grid 스터디 공용 도구.

cutbased_grid.py 와 bdt_grid.py 가 공유한다:
  * 이론 cross section 로드            -> load_xsec()
  * Asimov significance                -> asimov_z(), binned_asimov_z()
  * 2D mass-grid 플롯                  -> draw_grid(), make_grid_figure()
  * mass point별 수치 CSV 덤프         -> save_csv()

플롯 스타일은 ../../cutflow/tb_fraction_grid.py:draw_grid() 를 따른다 (scatter +
셀별 값 주석). WR 3000/5000/7000 열은 N 점이 1~2개뿐이라 grid가 불규칙해서
pcolormesh보다 scatter가 안전하다. --style mesh 로 check.ipynb 방식도 쓸 수 있다.
"""

import csv
import json
import os
import re

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

# 2022 + 2022EE + 2023 + 2023BPix. cut-based(combined_22_23/merged)와
# BDT(HNWR_BDT_presel 4 era 합)가 모두 이 값을 쓴다.
LUMI_FB = 62.31
LUMI_LABEL = rf"{LUMI_FB:.2f} fb$^{{-1}}$ (13.6 TeV)"

# xsec은 era에 무관하므로 아무 era의 CommonSampleInfo나 같다.
XSEC_JSON = ("/data6/Users/achihwan/SKNanoAnalyzer-v13/data/Run3_v12_Run2_v9"
             "/2022/Sample/CommonSampleInfo.json")

# 파일명 WR{mWR}N{mN}{EE|MM}.root
SAMPLE_RE = re.compile(r"^WR(\d+)N(\d+)(EE|MM)$")

CHANNELS = ("EE", "MM")
REGIONS = ("total", "boost", "resolve")


# ---------------------------------------------------------------- cross section
def load_xsec(path=XSEC_JSON):
    """{(mWR, mN, channel): xsec_pb} 를 돌려준다."""
    with open(path) as f:
        info = json.load(f)

    xsec = {}
    for key, val in info.items():
        m = SAMPLE_RE.match(key)
        if not m:
            continue
        xsec[(int(m.group(1)), int(m.group(2)), m.group(3))] = float(val["xsec"])
    if not xsec:
        raise RuntimeError(f"No WR*N*{{EE,MM}} keys found in {path}")
    return xsec


# ---------------------------------------------------------------- significance
def asimov_z(s, b):
    """스칼라 Asimov median discovery significance. s<=0 또는 b<=0 이면 0."""
    s = float(s)
    b = float(b)
    if s <= 0.0 or b <= 0.0:
        return 0.0
    return float(np.sqrt(2.0 * ((s + b) * np.log1p(s / b) - s)))


def binned_asimov_z(s_arr, b_arr):
    """bin별 Asimov Z를 quadrature 합산 (shape 정보를 쓰는 significance)."""
    s_arr = np.asarray(s_arr, dtype=float)
    b_arr = np.asarray(b_arr, dtype=float)
    z2 = 0.0
    for s, b in zip(s_arr, b_arr):
        z2 += asimov_z(s, b) ** 2
    return float(np.sqrt(z2))


def combine_z(*zs):
    """직교 영역(boost/resolve)의 Z를 합친다."""
    return float(np.sqrt(sum(float(z) ** 2 for z in zs)))


# ---------------------------------------------------------------- 플롯
def stamp_lumi(fig, label=LUMI_LABEL):
    fig.text(0.995, 0.995, label, ha="right", va="bottom", fontsize=12)


def _make_norm(values, logz, vmin=None, vmax=None):
    finite = values[np.isfinite(values)]
    if logz:
        finite = finite[finite > 0]
    if finite.size == 0:
        return None
    lo = finite.min() if vmin is None else vmin
    hi = finite.max() if vmax is None else vmax
    if lo == hi:
        hi = lo * 1.001 + 1e-12
    return mcolors.LogNorm(vmin=lo, vmax=hi) if logz else mcolors.Normalize(vmin=lo, vmax=hi)


def _fmt(value, kind):
    if kind == "percent":
        return f"{value * 100:.1f}"
    if kind == "sci":
        return f"{value:.2g}"
    return f"{value:.2f}"


def draw_grid(ax, rows, key, title, cbar_label, cmap="viridis", logz=False,
              norm=None, annotate=True, annotate_kind="percent", style="scatter",
              marker_size=110, annotate_fontsize=4.5, categorical_x=True):
    """(mWR, mN) 평면에 rows[i][key] 를 색으로 그린다.

    rows: [{'mWR':…, 'mN':…, key:…}, …]
    style: 'scatter' (기본) 또는 'mesh' (pcolormesh).
           mesh의 shading='nearest'는 N 점이 드문 열의 셀을 세로로 크게 늘려
           실제로 스캔하지 않은 영역까지 칠한다. 그래서 실제 샘플 위치를 그대로
           보여 주는 scatter가 기본이다.
    categorical_x: WR 값을 실제 질량 축이 아니라 균등 간격 슬롯에 놓는다.
           스캔한 WR 값이 2000/4000/6000/8000 넷뿐이라 실제 축을 쓰면 빈 공간만
           넓어진다. 눈금 라벨에는 원래 질량을 쓴다.
    """
    if not rows:
        ax.text(0.5, 0.5, "no data", ha="center", va="center", transform=ax.transAxes)
        ax.set_title(title, fontsize=11, fontweight="bold")
        return None

    x = np.array([r["mWR"] for r in rows], dtype=float)
    y = np.array([r["mN"] for r in rows], dtype=float)
    c = np.array([r.get(key, np.nan) for r in rows], dtype=float)

    wr_values = np.array(sorted(set(x)))
    if categorical_x:
        slot = {v: i for i, v in enumerate(wr_values)}
        x = np.array([slot[v] for v in x], dtype=float)

    if norm is None:
        norm = _make_norm(c, logz)
    if norm is None:
        ax.text(0.5, 0.5, "all values invalid", ha="center", va="center",
                transform=ax.transAxes)
        ax.set_title(title, fontsize=11, fontweight="bold")
        return None

    good = np.isfinite(c)
    if logz:
        good &= c > 0

    if style == "mesh":
        xs = np.array(sorted(set(x)))
        ys = np.array(sorted(set(y)))
        grid = np.full((len(ys), len(xs)), np.nan)
        xi = {v: i for i, v in enumerate(xs)}
        yi = {v: i for i, v in enumerate(ys)}
        for gx, gy, gc in zip(x, y, c):
            grid[yi[gy], xi[gx]] = gc
        mesh = ax.pcolormesh(xs, ys, np.ma.masked_invalid(grid), shading="nearest",
                             cmap=cmap, norm=norm)
    else:
        mesh = ax.scatter(x[good], y[good], c=c[good], s=marker_size, cmap=cmap,
                          norm=norm, edgecolors="black", linewidths=0.3)

    if annotate:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        for gx, gy, gc in zip(x, y, c):
            if not np.isfinite(gc) or (logz and gc <= 0):
                continue
            rgba = sm.to_rgba(gc)
            lum = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
            ax.annotate(_fmt(gc, annotate_kind), (gx, gy), fontsize=annotate_fontsize,
                        ha="center", va="center",
                        color="white" if lum < 0.5 else "black")

    if categorical_x:
        ax.set_xticks(np.arange(len(wr_values)))
        ax.set_xticklabels([f"{int(v)}" for v in wr_values])
        ax.set_xlim(-0.5, len(wr_values) - 0.5)
    ax.set_xlabel(r"$m_{W_R}$ [GeV]", fontsize=11)
    ax.set_ylabel(r"$m_{N}$ [GeV]", fontsize=11)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.3)

    cb = plt.colorbar(mesh, ax=ax)
    cb.set_label(cbar_label, fontsize=10)
    return mesh


def make_grid_figure(rows, key, title, cbar_label, outpath, cmap="viridis",
                     logz=False, norm=None, annotate=True,
                     annotate_kind="percent", style="scatter", categorical_x=True):
    """단일 패널 PNG 하나를 쓴다."""
    # WR8000 열은 N 점이 40개(200 GeV 간격)라 세로로 길어야 라벨이 읽힌다.
    fig, ax = plt.subplots(figsize=(8, 11))
    draw_grid(ax, rows, key, title, cbar_label, cmap=cmap, logz=logz, norm=norm,
              annotate=annotate, annotate_kind=annotate_kind, style=style,
              marker_size=200, annotate_fontsize=5.5, categorical_x=categorical_x)
    stamp_lumi(fig)
    fig.tight_layout()
    os.makedirs(os.path.dirname(outpath) or ".", exist_ok=True)
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {outpath}  ({len(rows)} mass points)")


def shared_norm(rows_by_channel, key, logz=False):
    """EE/MM 두 채널에 공통으로 쓸 color scale (채널 간 비교가 되도록)."""
    vals = []
    for rows in rows_by_channel:
        vals.extend(r.get(key, np.nan) for r in rows)
    return _make_norm(np.array(vals, dtype=float), logz)


# ---------------------------------------------------------------- CSV
def save_csv(rows, path, columns):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in sorted(rows, key=lambda r: (r["channel"], r["mWR"], r["mN"])):
            writer.writerow({c: row.get(c, "") for c in columns})
    print(f"[OK] {path}  ({len(rows)} rows)")


# ---------------------------------------------------------------- grid 필터
def parse_masspoint(stem):
    """'WR2000N1000EE' -> (2000, 1000, 'EE'), 아니면 None."""
    m = SAMPLE_RE.match(stem)
    return (int(m.group(1)), int(m.group(2)), m.group(3)) if m else None


# 제대로 스캔한 WR 값. 3000/5000/7000 은 N 점이 1~2개뿐인 단발 probe라
# (WR3000N200/N1500, WR5000N200/N2500, WR7000N200/N3500) 기본 플롯에서 뺀다.
DEFAULT_WR = (2000, 4000, 6000, 8000)


# cut-based(114점)와 BDT(100점)의 교집합. --grid common 에서 쓴다.
# BDT는 WR 2000/4000/6000/8000 × 홀수-백 N 만 학습돼 있다.
def in_common_grid(mWR, mN):
    return mWR in DEFAULT_WR and (mN % 200) == 100
