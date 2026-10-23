#!/usr/bin/env python3
"""Fake-factor estimate as a smooth mlljj shape (method B), tested in the DY CR mumu SS with data.

  ff_shape_fit.py [--k 1.27] [--lmax 0.4] [--region dycr]
    1. data mlljj distributions of iso-TT / TL / LT / LL (raw counts), L: 0.1<=TkRelIso<lmax
    2. the fail events weighted by the fake factor (F = k f/(1-f), |eta| map from the FOLOW MC, one pT bin):
       TL x F(sub), LT x F(lead), LL x (-F1 F2), their sum (= fake estimate), vs data TT - prompt MC (PP)
    3. binned chi2 fits of the weighted fail distribution (errors = sqrt(sum w^2) + prompt-subtraction stat) with
         expo   N exp(-b (m-800)/1000)
         power  N (m/800)^-b
         dijet  N (1-x)^b / x^c,  x = m/13600
       -> fitted curves with 68% bands (parameter covariance), extrapolated to 6 TeV; chi2/ndf; integral per card bin
  -> out/nonprompt_ssmm/dycr/ffshape_<region>.{png,pdf}, results/21_ffshape_<region>.txt
"""
import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import mplhep as hep  # noqa: E402
import numpy as np  # noqa: E402
import ROOT  # noqa: E402

import dycr_analysis as DA  # noqa: E402
import folib as L  # noqa: E402
import fr_mll60300 as FR  # noqa: E402
from plot_dycr_ffapply import ff_weights  # noqa: E402

hep.style.use("CMS")
EDGES = np.array([800, 900, 1000, 1100, 1200, 1350, 1500, 1700, 2000, 2400, 3000, 4000], float)
X0 = 800.0


# densities (events/GeV) as ROOT formulas; X0 = 800 GeV, sqrt(s) = 13.6 TeV
FORMULAS = {
    "expo": ("[0]*exp(-[1]*(x-800.)/1000.)", [1e-2, 2.0]),
    "power": ("[0]*pow(x/800., -[1])", [1e-2, 4.0]),
    "dijet": ("[0]*pow((1-x/13600.)/(1-800./13600.), [1])/pow(x/800., [2])", [1e-2, 5.0, 4.0]),
}


def make_fn(expr, npar):
    tf = ROOT.TF1("tmp_eval", expr, 0, 20000)

    def fn(m, *p):
        for i, v in enumerate(p):
            tf.SetParameter(i, float(v))
        return np.array([tf.Eval(float(v)) for v in np.atleast_1d(m)])
    return fn


FUNCS = {k: (make_fn(e, len(p0)), p0) for k, (e, p0) in FORMULAS.items()}


def density_fit(edges, y, e):
    """chi2 fit of the density (content/width at the bin centre) with ROOT; returns popt, cov, chi2, ndf."""
    ctr = 0.5 * (edges[:-1] + edges[1:]); wid = np.diff(edges)
    ok = e > 1e-2 * np.max(e)   # drop empty bins (a ~0 error would dominate the chi2)
    g = ROOT.TGraphErrors(int(ok.sum()), ctr[ok].astype(float), (y / wid)[ok].astype(float),
                          np.zeros(int(ok.sum())), (e / wid)[ok].astype(float))
    res = {}
    for name, (expr, p0) in FORMULAS.items():
        tf = ROOT.TF1(f"fit_{name}", expr, edges[0], edges[-1])
        p0 = list(p0); p0[0] = max(float(y[0] / wid[0]), 1e-4)
        for i, v in enumerate(p0):
            tf.SetParameter(i, v)
        r = g.Fit(tf, "SQN0")
        if int(r) != 0 and not r.IsValid():
            res[name] = (None, None, np.nan, 0); continue
        npar = len(p0)
        popt = np.array([tf.GetParameter(i) for i in range(npar)])
        cm = r.GetCovarianceMatrix()
        pcov = np.array([[cm(i, j) for j in range(npar)] for i in range(npar)])
        res[name] = (popt, pcov, r.Chi2(), r.Ndf())
    return res


def band(fn, popt, pcov, m, ntoy=500, rng=np.random.default_rng(3)):
    toys = rng.multivariate_normal(popt, pcov, size=ntoy)
    vals = np.array([fn(m, *t) for t in toys])
    return np.percentile(vals, [16, 84], axis=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=float, default=1.27)
    ap.add_argument("--lmax", type=float, default=0.4)
    a = ap.parse_args()
    FR.PT = [53.0, 4000.0]
    lo, _ = FR.load()
    rm = FR.fmap(lo, lo["base"] & ~lo["data"] & (lo["mll"] > 60) & (lo["mll"] < 300), a.lmax)
    del lo
    d, _ = DA.load_dy()
    sel = d["base"] & d["ss"]
    D, M = sel & d["data"], sel & ~d["data"] & ~d["qcd"]
    iso1, iso2 = d["mu1_tkRelIso"], d["mu2_tkRelIso"]
    inL = ((d["cat"] == "TT") | ((d["cat"] == "TL") & (iso2 < a.lmax)) | ((d["cat"] == "LT") & (iso1 < a.lmax))
           | ((d["cat"] == "LL") & (iso1 < a.lmax) & (iso2 < a.lmax)))
    x = d["mlljj"]
    wD = ff_weights(d, D, rm, a.k, a.lmax)
    wP = ff_weights(d, M & (d["pair"] == "PP"), rm, a.k, a.lmax)
    txt = [f"# DY CR mumu SS, data. map |eta| {FR.ETA} f=" + " ".join(f"{v:.3f}" for v in rm.r[0]) + f", L<{a.lmax}, k={a.k}"]

    fig, axes = plt.subplots(1, 3, figsize=(30, 9))
    # 1. raw counts
    ax = axes[0]
    for c, col in (("TT", "black"), ("TL", "#e42536"), ("LT", "#f89c20"), ("LL", "#5790fc")):
        h = np.histogram(x[D & (d["cat"] == c) & inL], EDGES)[0]
        hep.histplot(h, EDGES, yerr=np.sqrt(h), histtype="errorbar", color=col, label=f"data iso-{c} ({h.sum()})", ax=ax)
        txt.append(f"raw data {c}: " + " ".join(str(v) for v in h) + f"  total {h.sum()}")
    ax.set_yscale("log"); ax.set_ylabel("events / bin"); ax.set_xlabel(r"$m_{\mu\mu jj}$ (GeV)")
    ax.legend(fontsize=15); ax.text(0.03, 0.03, "raw counts, L: 0.1<=TkRelIso<%g" % a.lmax, transform=ax.transAxes, fontsize=14)
    # 2. weighted
    ax = axes[1]
    comps = {}
    for c, col in (("TL", "#e42536"), ("LT", "#f89c20"), ("LL", "#5790fc")):
        m = D & (d["cat"] == c)
        comps[c] = np.histogram(x[m], EDGES, weights=wD[m])[0]
        hep.histplot(comps[c], EDGES, histtype="step", color=col, lw=2, label=f"{c} x F" + (" (negative)" if c == "LL" else ""), ax=ax)
    pp = np.histogram(x, EDGES, weights=wP)[0]
    fake = comps["TL"] + comps["LT"] + comps["LL"] - pp
    fake_e = np.sqrt(np.histogram(x, EDGES, weights=wD ** 2)[0] + np.histogram(x, EDGES, weights=wP ** 2)[0])
    obsTT = np.histogram(x[D & (d["cat"] == "TT")], EDGES)[0].astype(float)
    mp = M & (d["cat"] == "TT") & (d["pair"] == "PP")
    promptTT = np.histogram(x[mp], EDGES, weights=d["weight"][mp])[0]
    hep.histplot(fake, EDGES, yerr=fake_e, histtype="errorbar", color="#9c9ca1", label=f"fake estimate ({fake.sum():.1f})", ax=ax, marker="s")
    hep.histplot(obsTT - promptTT, EDGES, yerr=np.sqrt(obsTT), histtype="errorbar", color="black",
                 label=f"data TT - prompt MC ({(obsTT - promptTT).sum():.1f})", ax=ax)
    ax.set_yscale("log"); ax.set_ylim(0.01, max(fake.max(), obsTT.max()) * 5)
    ax.set_ylabel("events / bin"); ax.set_xlabel(r"$m_{\mu\mu jj}$ (GeV)"); ax.legend(fontsize=14)
    txt.append("fake estimate per bin: " + " ".join(f"{v:.2f}±{e:.2f}" for v, e in zip(fake, fake_e)))
    txt.append("data TT - prompt MC:   " + " ".join(f"{v:.2f}" for v in obsTT - promptTT))
    # 3. fits of the fake estimate
    ax = axes[2]
    wid = np.diff(EDGES)
    ctr = 0.5 * (EDGES[:-1] + EDGES[1:])
    ax.errorbar(ctr, fake / wid, yerr=fake_e / wid, xerr=wid / 2, fmt="s", color="#9c9ca1", label="fake estimate / GeV")
    ax.errorbar(ctr + 10, (obsTT - promptTT) / wid, yerr=np.sqrt(obsTT) / wid, fmt="o", color="black", label="data TT - prompt MC / GeV")
    res = density_fit(EDGES, fake, fake_e)
    mm = np.linspace(800, 6000, 400)
    fcol = {"expo": "#e42536", "power": "#5790fc", "dijet": "#2ca02c"}
    card = np.array([800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 8000], float)
    for name, (popt, pcov, chi2, ndf) in res.items():
        if popt is None:
            continue
        fn = FUNCS[name][0]
        lo_, hi_ = band(fn, popt, pcov, mm)
        ax.plot(mm, fn(mm, *popt), color=fcol[name], lw=2, label=f"{name}: $\\chi^2$/ndf {chi2:.1f}/{ndf}")
        ax.fill_between(mm, lo_, hi_, color=fcol[name], alpha=0.2)
        ints = []
        for i in range(len(card) - 1):
            mg = np.linspace(card[i], card[i + 1], 200)
            ints.append(np.trapezoid(fn(mg, *popt), mg) if hasattr(np, 'trapezoid') else np.trapz(fn(mg, *popt), mg))
        txt.append(f"fit {name}: pars {np.round(popt, 4).tolist()} chi2/ndf {chi2:.2f}/{ndf}; integral per card bin "
                   + " ".join(f"{v:.3f}" for v in ints) + f"  (sum {sum(ints):.2f}, fake hist sum {fake.sum():.2f})")
    ax.set_yscale("log"); ax.set_xlim(800, 6000); ax.set_ylim(1e-6, 1)
    ax.set_xlabel(r"$m_{\mu\mu jj}$ (GeV)"); ax.set_ylabel("events / GeV"); ax.legend(fontsize=13)
    for axx in axes:
        hep.cms.label(ax=axx, label="Preliminary", data=True, lumi=109.8, com=13.6, fontsize=15)
    od = os.path.join(L.PLOTS, "dycr"); os.makedirs(od, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(od, f"ffshape_dycr.{ext}"), bbox_inches="tight")
    out = os.path.join(L.RESULTS, "21_ffshape_dycr.txt")
    open(out, "w").write("\n".join(txt) + "\n")
    print("\n".join(txt)); print("wrote", out)


if __name__ == "__main__":
    sys.exit(main())
