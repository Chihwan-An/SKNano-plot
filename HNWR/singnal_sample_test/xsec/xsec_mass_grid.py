#!/usr/bin/env python3
"""
xsec_mass_grid.py — (m_WR, m_N) 평면의 이론 cross section 맵 + "최소 3 event" 경계선.

  * x = m_WR, y = m_N, color = sigma [fb]  (CommonSampleInfo.json 의 WR*N*{EE,MM})
  * 빨간 실선 = 기대 event 수 mu = sigma * L 가 3 이 되는 지점
                (선의 왼쪽/아래 = mu > 3, 즉 signal 이 최소 3개는 나오는 영역)
  * L = 500 fb^-1 과 137 fb^-1 두 경우
  * 빨간 선 주위의 띠 = n = 3 observed 에 대한 Poisson 통계오차
    (Garwood central interval) 1 sigma / 2 sigma

xsec 은 EE / MM 이 완전히 동일하므로 그림은 채널당 한 장이 아니라 한 장이면 된다.
"""

import argparse
import json
import os
import re

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.interpolate import griddata
from scipy.stats import chi2

XSEC_JSON = ("/u/user/snu202527803/SKNanoAnalyzer/data/Run3_v12_Run2_v9"
             "/2022/Sample/CommonSampleInfo.json")
SAMPLE_RE = re.compile(r"^WR(\d+)N(\d+)(EE|MM)$")

# HEPData 114866 (CMS W_R -> lN, 138 fb^-1 @ 13 TeV) Figure 7.
# values[i]['y'][0] = observed 95% CL UL on sigma*B / theory  -> r = 1 이 exclusion 경계.
HEPDATA = {"EE": "e.json", "MM": "mu.json"}
HEPDATA_LABEL = r"CMS obs. 95% CL excl. (138 fb$^{-1}$, 13 TeV)"

N_TARGET = 3          # "signal 이 최소 N_TARGET 개"
LUMIS_FB = [500.0, 137.0]


# ------------------------------------------------------------------ statistics
def poisson_interval(n, cl):
    """관측 n event 에 대한 Poisson central (Garwood) confidence interval."""
    a = 1.0 - cl
    lo = 0.0 if n == 0 else 0.5 * chi2.ppf(a / 2.0, 2 * n)
    hi = 0.5 * chi2.ppf(1.0 - a / 2.0, 2 * n + 2)
    return lo, hi


CL_1SIG = 0.682689492
CL_2SIG = 0.954499736


# ------------------------------------------------------------------ input data
def load_xsec(path=XSEC_JSON, channel="EE"):
    """{(m_WR, m_N): sigma_fb}."""
    with open(path) as f:
        info = json.load(f)
    out = {}
    for key, val in info.items():
        m = SAMPLE_RE.match(key)
        if not m or m.group(3) != channel:
            continue
        out[(int(m.group(1)), int(m.group(2)))] = float(val["xsec"]) * 1e3  # pb -> fb
    if not out:
        raise RuntimeError(f"No WR*N*{channel} keys in {path}")
    return out


def load_hepdata_limit(channel, which=0, basedir=None):
    """HEPData Fig.7 표에서 {(m_WR, m_N): r} 를 읽는다. which=0 observed, 1 expected."""
    basedir = basedir or os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(basedir, HEPDATA[channel])
    if not os.path.exists(path):
        return None
    with open(path) as f:
        tab = json.load(f)
    return {(float(r["x"][0]["value"]), float(r["x"][1]["value"])):
            float(r["y"][which]["value"]) for r in tab["values"]}


def interp_to(grid, WR, MN):
    """{(m_WR, m_N): v} 를 (m_WR, m_N/m_WR) 좌표 log 선형보간으로 WR/MN 격자에 얹는다."""
    pts = np.array(sorted(grid))
    wr, mn = pts[:, 0], pts[:, 1]
    val = np.log10([grid[tuple(p)] for p in pts])
    src = np.column_stack([wr / 1000.0, mn / wr])
    dst = np.column_stack([WR.ravel() / 1000.0, (MN / WR).ravel()])
    return 10.0 ** griddata(src, val, dst, method="linear").reshape(WR.shape)


def interpolate(xsec, n_wr=601, n_mn=391):
    """log10(sigma) 를 (m_WR, m_N/m_WR) 좌표에서 선형보간해 촘촘한 격자로 만든다.

    m_WR column 이 7개(1 TeV 간격)뿐이라 (m_WR, m_N) 로 바로 보간하면
    kinematic edge (m_N -> m_WR) 근처가 심하게 왜곡된다. 비율 좌표를 쓰면
    sample 영역이 거의 직사각형이 되어 보간이 안정적이다.
    """
    pts = np.array(sorted(xsec))
    wr, mn = pts[:, 0].astype(float), pts[:, 1].astype(float)
    val = np.log10([xsec[tuple(p)] for p in pts])

    src = np.column_stack([wr / 1000.0, mn / wr])

    wr_ax = np.linspace(wr.min(), wr.max(), n_wr)
    mn_ax = np.linspace(mn.min(), mn.max(), n_mn)
    WR, MN = np.meshgrid(wr_ax, mn_ax)
    dst = np.column_stack([WR.ravel() / 1000.0, (MN / WR).ravel()])

    Z = griddata(src, val, dst, method="linear").reshape(WR.shape)
    # sample 이 존재하는 삼각형 밖은 그리지 않는다 (m_N <= m_WR - 100)
    Z[MN > WR - 100.0] = np.nan
    return WR, MN, 10.0 ** Z, (wr, mn)


# ---------------------------------------------------------------------- figure
def make_figure(outpath, channel="EE", n_target=N_TARGET, lumis=LUMIS_FB,
                show_points=False, n_thin=1, show_bands=False,
                show_limit=True):
    xsec = load_xsec(channel=channel)
    WR, MN, SIG, (pwr, pmn) = interpolate(xsec)

    lo1, hi1 = poisson_interval(n_target, CL_1SIG)
    lo2, hi2 = poisson_interval(n_target, CL_2SIG)

    fig, ax = plt.subplots(figsize=(9.2, 7.0))

    finite = SIG[np.isfinite(SIG)]
    mesh = ax.pcolormesh(WR, MN, np.ma.masked_invalid(SIG), cmap="viridis",
                         norm=LogNorm(vmin=finite.min(), vmax=finite.max()),
                         shading="auto", rasterized=True)
    cb = fig.colorbar(mesh, ax=ax, pad=0.015)
    cb.set_label(r"$\sigma(pp \to W_R \to \ell N \to \ell\ell jj)$  [fb]")

    if show_points:
        ax.plot(pwr, pmn, ls="none", marker=".", ms=1.8, color="white",
                alpha=0.35, zorder=2)

    styles = {500.0: dict(ls="-", lw=2.4), 137.0: dict(ls="--", lw=2.4)}
    handles = []
    for lumi in lumis:
        MU = SIG * lumi  # sigma[fb] * L[fb^-1]
        st = styles.get(lumi, dict(ls="-", lw=2.2))

        if show_bands:
            # 2 sigma -> 1 sigma 순으로 깔아야 진한 띠가 위에 온다
            ax.contourf(WR, MN, MU, levels=[lo2, hi2], colors=["red"],
                        alpha=0.13, zorder=3)
            ax.contourf(WR, MN, MU, levels=[lo1, hi1], colors=["red"],
                        alpha=0.22, zorder=4)
        cs = ax.contour(WR, MN, MU, levels=[float(n_target)], colors="red",
                        zorder=5, **st)
        ax.clabel(cs, fmt={float(n_target): rf"{lumi:.0f} fb$^{{-1}}$"},
                  inline=True, fontsize=10, colors="red")
        handles.append(Line2D([], [], color="red",
                              label=rf"$\mu = {n_target}$  ({lumi:.0f} fb$^{{-1}}$)", **st))

        # 참고용: "최소 1 event" 경계 — 옅은 점선만 (band 없음)
        if n_thin and n_thin != n_target:
            ax.contour(WR, MN, MU, levels=[float(n_thin)], colors="red",
                       linestyles=":", linewidths=1.1, alpha=0.45, zorder=5)

    if n_thin and n_thin != n_target:
        handles.append(Line2D([], [], color="red", ls=":", lw=1.1, alpha=0.45,
                              label=rf"$\mu = {n_thin}$  (both $L$)"))

    # ---- Run 2 observed 95% CL exclusion (HEPData 114866, 138 fb^-1 @ 13 TeV)
    lim = load_hepdata_limit(channel) if show_limit else None
    if lim:
        R = interp_to(lim, WR, MN)
        ax.contourf(WR, MN, R, levels=[R[np.isfinite(R)].min(), 1.0],
                    colors="none", hatches=["///"], zorder=6)
        ax.contour(WR, MN, R, levels=[1.0], colors="black", linewidths=2.2,
                   zorder=7)
        handles.append(Line2D([], [], color="black", lw=2.2,
                              label=HEPDATA_LABEL))

    if show_bands:
        handles += [
            Patch(facecolor="red", alpha=0.22, label=r"stat. $1\sigma$"),
            Patch(facecolor="red", alpha=0.13, label=r"stat. $2\sigma$"),
        ]
    leg = ax.legend(handles=handles, loc="upper left", framealpha=0.85,
                    fontsize=10)
    leg.set_zorder(10)

    ax.plot([2000, 8000], [2000, 8000], color="gray", lw=1.0, ls=":")
    ax.text(7000, 7150, r"$m_N = m_{W_R}$", color="gray", fontsize=9,
            rotation=38, ha="center", va="bottom")

    ax.set_xlabel(r"$m_{W_R}$  [GeV]")
    ax.set_ylabel(r"$m_{N}$  [GeV]")
    ax.set_xlim(2000, 8000)
    ax.set_ylim(0, 8000)
    ax.set_title(rf"$W_R \to \ell N \to \ell\ell jj$ ({channel}) — "
                 rf"$\mu = \sigma L \geq {n_target}$ below the red line",
                 fontsize=12, loc="left")
    ax.set_title("13.6 TeV", fontsize=11, loc="right")

    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    fig.savefig(outpath.replace(".png", ".pdf"))
    plt.close(fig)
    print(f"[xsec_mass_grid] wrote {outpath}")
    return lo1, hi1, lo2, hi2


# ------------------------------------------------------------------- boundary
def _crossing(mns, mu, level):
    """mu(m_N) 가 level 을 아래로 통과하는 m_N. log(mu) 선형보간, 마지막 교차점 사용."""
    idx = np.nonzero((mu[:-1] >= level) & (mu[1:] < level))[0]
    if len(idx) == 0:
        return np.nan            # 전 구간에서 mu >= level (또는 전 구간 mu < level)
    i = idx[-1]
    y0, y1 = np.log(mu[i]), np.log(mu[i + 1])
    t = (np.log(level) - y0) / (y1 - y0)
    return float(mns[i] + t * (mns[i + 1] - mns[i]))


def dump_boundary(csvpath, channel="EE", n_target=N_TARGET, lumis=LUMIS_FB):
    """m_WR column 마다 mu = n_target (및 ±1,2 sigma) 이 되는 m_N 을 CSV 로."""
    xsec = load_xsec(channel=channel)
    lo1, hi1 = poisson_interval(n_target, CL_1SIG)
    lo2, hi2 = poisson_interval(n_target, CL_2SIG)
    levels = [("mu_2sig_lo", lo2), ("mu_1sig_lo", lo1),
              ("mu_nominal", float(n_target)),
              ("mu_1sig_hi", hi1), ("mu_2sig_hi", hi2)]

    wrs = sorted({w for w, _ in xsec})
    rows = []
    for lumi in lumis:
        for wr in wrs:
            mns = np.array(sorted(n for w, n in xsec if w == wr), dtype=float)
            mu = np.array([xsec[(wr, int(n))] * lumi for n in mns])
            row = {"lumi_fb": lumi, "m_WR": wr}
            for name, lev in levels:
                row[name] = _crossing(mns, mu, lev)
            rows.append(row)

    cols = ["lumi_fb", "m_WR"] + [n for n, _ in levels]
    with open(csvpath, "w") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join("" if isinstance(r[c], float) and np.isnan(r[c])
                             else (f"{r[c]:.6g}" if isinstance(r[c], float) else str(r[c]))
                             for c in cols) + "\n")
    print(f"[xsec_mass_grid] wrote {csvpath}")
    for r in rows:
        if np.isnan(r["mu_nominal"]):
            txt = "no crossing (whole m_N range passes)"
        else:
            def _f(k):
                return "-" if np.isnan(r[k]) else "%.0f" % r[k]
            txt = ("%.0f GeV   [1sig: %s - %s,  2sig: %s - %s]"
                   % (r["mu_nominal"], _f("mu_1sig_hi"), _f("mu_1sig_lo"),
                      _f("mu_2sig_hi"), _f("mu_2sig_lo")))
        print("  L=%5.0f fb-1  m_WR=%5d  m_N(mu=%d) = %s"
              % (r["lumi_fb"], r["m_WR"], n_target, txt))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default=os.path.dirname(os.path.abspath(__file__)))
    p.add_argument("--channel", default="EE", choices=["EE", "MM"])
    p.add_argument("--n-target", type=int, default=N_TARGET)
    p.add_argument("--points", action="store_true",
                   help="sample mass point 을 흰 점으로 덧그린다")
    p.add_argument("--n-thin", type=int, default=1,
                   help="옅은 점선으로만 표시할 event 수 (0 이면 끔)")
    p.add_argument("--bands", action="store_true",
                   help="Poisson stat 1/2 sigma 띠를 그린다 (기본은 끔)")
    p.add_argument("--no-limit", action="store_true",
                   help="Run 2 observed exclusion (HEPData) 를 안 그린다")
    a = p.parse_args()

    os.makedirs(a.outdir, exist_ok=True)
    tag = f"n{a.n_target}_{a.channel}"
    lo1, hi1, lo2, hi2 = make_figure(
        os.path.join(a.outdir, f"xsec_mass_grid_{tag}.png"),
        channel=a.channel, n_target=a.n_target, show_points=a.points,
        n_thin=a.n_thin, show_bands=a.bands, show_limit=not a.no_limit)
    print(f"[xsec_mass_grid] Poisson (n={a.n_target}): "
          f"1sig [{lo1:.3f}, {hi1:.3f}], 2sig [{lo2:.3f}, {hi2:.3f}]")
    dump_boundary(os.path.join(a.outdir, f"xsec_mass_grid_{tag}_boundary.csv"),
                  channel=a.channel, n_target=a.n_target)


if __name__ == "__main__":
    main()
