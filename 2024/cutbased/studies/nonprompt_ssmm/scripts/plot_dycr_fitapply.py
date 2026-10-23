#!/usr/bin/env python3
"""DY CR mumu SS data vs background where the MC nonprompt is replaced by the SMOOTH fake estimate:
fake(mlljj) = N x shape(mlljj), shape from the unbinned weighted-likelihood fit of the fake-factor-weighted fail
events (ff_shape_fit2.py), N = sum of the weights. Prompt part = MC with both muons truth-prompt.
  stat band : prompt MC sum w^2  +  fake (fit-parameter covariance and N stat, toys)
  func band : envelope of the four fit functions (shown separately)
  -> out/nonprompt_ssmm/dycr/dycr_ss_fitapply.{png,pdf}, results/23_dycr_fitapply.txt
"""
import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import mplhep as hep  # noqa: E402
import numpy as np  # noqa: E402

import dycr_analysis as DA  # noqa: E402
import ff_shape_fit2 as SF  # noqa: E402
import folib as L  # noqa: E402
import fr_mll60300 as FR  # noqa: E402
from plot_dycr_ffapply import GROUP, GCOL, ff_weights  # noqa: E402

hep.style.use("CMS")
EDGES = np.array([800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3800, 5000, 8000], float)   # plot binning (specs/tightcharge/Resolve_DY_MM_alltc.txt)
SF.HI = 8000.0   # pdf domain / normalisation range of the unbinned fit extended to 8 TeV


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=float, default=1.27)
    ap.add_argument("--lmax", type=float, default=0.4)
    ap.add_argument("--func", default="expo")
    ap.add_argument("--drop", default="power", help="comma-separated fit functions left out of the envelope (worst fit quality)")
    a = ap.parse_args()
    FR.PT = [53.0, 4000.0]
    lo, _ = FR.load()
    rm = FR.fmap(lo, lo["base"] & ~lo["data"] & (lo["mll"] > 60) & (lo["mll"] < 300), a.lmax)
    del lo
    d, _ = DA.load_dy()
    sel = d["base"] & d["ss"]
    D, M = sel & d["data"], sel & ~d["data"] & ~d["qcd"]
    TT = d["cat"] == "TT"
    wD = ff_weights(d, D, rm, a.k, a.lmax)
    wP = ff_weights(d, M & (d["pair"] == "PP"), rm, a.k, a.lmax)
    use = (wD != 0) | (wP != 0)
    mev, wev = d["mlljj"][use], (wD - wP)[use]
    N, Ne = wev.sum(), np.sqrt((wev ** 2).sum())
    fits = SF.unbinned_fit(mev, wev)
    rng = np.random.default_rng(5)
    fake = {}
    for name, (pv, cov, status, _) in fits.items():
        cen = SF.bin_integrals(name, pv, EDGES, N)
        toys = np.array([SF.bin_integrals(name, t, EDGES, n)
                         for t, n in zip(rng.multivariate_normal(pv, cov, size=200), rng.normal(N, Ne, size=200))])
        fake[name] = (cen, toys.std(axis=0))
    fc, fe = fake[a.func]
    keep = {k: v for k, v in fake.items() if k not in a.drop.split(",")}
    env_lo = np.min([v[0] for v in keep.values()], axis=0)
    env_hi = np.max([v[0] for v in keep.values()], axis=0)

    x = d["mlljj"]
    hD = np.histogram(x[D & TT], EDGES)[0].astype(float)
    stk, e2 = {}, 0.0
    for p, g in GROUP.items():
        mpp = M & TT & (d["proc"] == p) & (d["pair"] == "PP")
        stk[g] = stk.get(g, 0) + np.histogram(x[mpp], EDGES, weights=d["weight"][mpp])[0]
        e2 = e2 + np.histogram(x[mpp], EDGES, weights=d["weight"][mpp] ** 2)[0]
    stk["Fake (data, fit)"] = fc
    GCOL["Fake (data, fit)"] = "#9c9ca1"
    order = [g for g in ("Others", "Fake (data, fit)", "Nonprompt", "TT+tW", "DY") if g in stk]
    tot = sum(stk[g] for g in order)
    err = np.sqrt(e2 + fe ** 2)
    tot_func_lo = tot - fc + env_lo
    tot_func_hi = tot - fc + env_hi

    fig, (ax, rx) = plt.subplots(2, 1, figsize=(12, 12), gridspec_kw={"height_ratios": [3, 1.2]}, sharex=True)
    hep.histplot([stk[g] for g in order], EDGES, stack=True, histtype="fill", color=[GCOL[g] for g in order],
                 label=order, ax=ax, edgecolor="k", lw=0.5)
    ax.stairs(tot + err, EDGES, baseline=np.clip(tot - err, 1e-4, None), fill=True, color="none", hatch="////",
              edgecolor="grey", lw=0, label="bkg stat unc.")
    ax.stairs(tot_func_hi, EDGES, baseline=np.clip(tot_func_lo, 1e-4, None), fill=True, color="#e42536", alpha=0.25,
              lw=0, label="fit-function envelope (" + ",".join(keep) + ")")
    hep.histplot(hD, EDGES, yerr=np.sqrt(hD), histtype="errorbar", color="k", label="data", ax=ax)
    ax.set_yscale("log"); ax.set_ylim(1e-3, hD.max() * 300); ax.set_ylabel("events / bin")
    ax.legend(fontsize=14, ncol=2); ax.text(0.04, 0.05, f"DY CR $\\mu\\mu$ SS, fake = {a.func} fit x N", transform=ax.transAxes, fontsize=16)
    hep.cms.label(ax=ax, label="Preliminary", data=True, lumi=109.8, com=13.6, fontsize=15)
    with np.errstate(divide="ignore", invalid="ignore"):
        rel = np.where(tot > 0, err / tot, 0)
        rx.errorbar(0.5 * (EDGES[:-1] + EDGES[1:]), hD / tot, yerr=np.sqrt(hD) / tot, xerr=np.diff(EDGES) / 2, fmt="ko")
        rx.stairs(tot_func_hi / tot, EDGES, baseline=tot_func_lo / tot, fill=True, color="#e42536", alpha=0.25, lw=0)
    rx.stairs(1 + rel, EDGES, baseline=1 - rel, fill=True, color="none", hatch="////", edgecolor="grey", lw=0)
    rx.axhline(1, color="grey", ls="--"); rx.set_ylim(0, 2.5); rx.set_ylabel("data / bkg")
    rx.set_xlabel(r"$m_{\mu\mu jj}$ (GeV)")
    od = os.path.join(L.PLOTS, "dycr"); os.makedirs(od, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(od, f"dycr_ss_fitapply.{ext}"), bbox_inches="tight")
    txt = [f"# DY CR mumu SS, fake = {a.func} unbinned fit x N (N={N:.2f}±{Ne:.2f}), k={a.k}, L<{a.lmax}",
           "bins      : " + " ".join(f"{int(v)}" for v in EDGES),
           "data      : " + " ".join(f"{v:6.0f}" for v in hD),
           "prompt MC : " + " ".join(f"{v:6.2f}" for v in tot - fc),
           "fake fit  : " + " ".join(f"{v:6.2f}" for v in fc),
           "fake stat : " + " ".join(f"{v:6.2f}" for v in fe),
           "functions in envelope: " + ",".join(keep),
           "func env  : " + " ".join(f"{l:.2f}-{h:.2f}" for l, h in zip(env_lo, env_hi)),
           "total     : " + " ".join(f"{v:6.2f}" for v in tot),
           "rel stat  : " + " ".join(f"{100 * r:5.0f}%" for r in rel),
           f"sums: data {hD.sum():.0f}, bkg {tot.sum():.2f} ± {np.sqrt((err ** 2).sum()):.2f}"]
    out = os.path.join(L.RESULTS, "23_dycr_fitapply.txt")
    open(out, "w").write("\n".join(txt) + "\n")
    print("\n".join(txt)); print("wrote", out)


if __name__ == "__main__":
    sys.exit(main())
