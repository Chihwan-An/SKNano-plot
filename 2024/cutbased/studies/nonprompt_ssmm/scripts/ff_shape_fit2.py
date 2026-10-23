#!/usr/bin/env python3
"""Method B, second pass: smooth mlljj shape of the fake-factor estimate in the DY CR mumu SS (data),
two ways, four functions (expo, power, dijet, expo2):
  (a) coarse bins 800/1000/1200/1500/2000/3000, chi2 fit of bin integrals (ROOT, option I)
  (b) unbinned weighted likelihood (RooFit, SumW2Error): per-event weight = F k (LL and prompt subtraction
      negative); shape fitted on [800, 4000], normalisation N = sum of weights (+- sqrt(sum w^2))
Outputs integrals per card bin (with 68% bands from the parameter covariance and N stat) compared with the
histogram estimate and with data TT - prompt MC.
  -> out/nonprompt_ssmm/dycr/ffshape2_dycr.{png,pdf}, results/22_ffshape2_dycr.txt
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
ROOT.gErrorIgnoreLevel = ROOT.kError
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.ERROR)
LO, HI = 800.0, 4000.0
COARSE = np.array([800, 1000, 1200, 1500, 2000, 3000], float)
CARD = np.array([800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 4000], float)
# density shapes in x = mlljj; parameters p0.. (normalisation handled separately)
SHAPES = {
    "expo":  ("exp(-{b}*(XM-800.)/1000.)", [("b", 4.0, 0.1, 20.0)]),
    "power": ("pow(XM/800., -{b})", [("b", 6.0, 0.5, 30.0)]),
    "dijet": ("pow((1-XM/13600.)/(1-800./13600.), {b})/pow(XM/800., {c})", [("b", 20.0, -50.0, 200.0), ("c", 2.0, -10.0, 20.0)]),
    "expo2": ("exp(-{b}*(XM-800.)/1000.-{c}*pow((XM-800.)/1000.,2))", [("b", 2.5, -5.0, 20.0), ("c", 1.0, -3.0, 10.0)]),
}
FCOL = {"expo": "#e42536", "power": "#5790fc", "dijet": "#2ca02c", "expo2": "#964a8b"}


def tf1_expr(name):
    expr, pars = SHAPES[name]
    return "[0]*" + expr.format(**{p[0]: f"[{i + 1}]" for i, p in enumerate(pars)}).replace("XM", "x")


def shape_eval(name, pvals, m):
    tf = ROOT.TF1("ev", "1*" + SHAPES[name][0].format(**{p[0]: f"[{i}]" for i, p in enumerate(SHAPES[name][1])}).replace("XM", "x"), 0, 20000)
    for i, v in enumerate(pvals):
        tf.SetParameter(i, float(v))
    return np.array([tf.Eval(float(v)) for v in np.atleast_1d(m)]), tf


def bin_integrals(name, pvals, edges, norm):
    _, tf = shape_eval(name, pvals, [LO])
    tot = tf.Integral(LO, HI)
    return np.array([norm * tf.Integral(edges[i], edges[i + 1]) / tot for i in range(len(edges) - 1)])


def coarse_fit(y, e):
    h = ROOT.TH1D("hc", "", len(COARSE) - 1, COARSE)
    for i in range(len(y)):
        w = COARSE[i + 1] - COARSE[i]
        h.SetBinContent(i + 1, y[i] / w); h.SetBinError(i + 1, e[i] / w if e[i] > 1e-2 * e.max() else 0)
    out = {}
    for name, (_, pars) in SHAPES.items():
        tf = ROOT.TF1("fc_" + name, tf1_expr(name), LO, COARSE[-1])
        tf.SetParameter(0, max(y[0] / 200.0, 1e-4))
        for i, p in enumerate(pars):
            tf.SetParameter(i + 1, p[1]); tf.SetParLimits(i + 1, p[2], p[3])
        best = None
        for scale in (1.0, 0.5, 2.0):   # a few starting points
            for i, p in enumerate(pars):
                tf.SetParameter(i + 1, p[1] * scale)
            r = h.Fit(tf, "SQN0I", "", LO, COARSE[-1])
            if r.IsValid() and (best is None or r.Chi2() < best[2]):
                n = len(pars) + 1
                pv = np.array([tf.GetParameter(i) for i in range(n)])
                cm = r.GetCovarianceMatrix()
                cov = np.array([[cm(i, j) for j in range(n)] for i in range(n)])
                best = (pv, cov, r.Chi2(), r.Ndf())
        out[name] = best
    return out


def unbinned_fit(m, w):
    x = ROOT.RooRealVar("x", "mlljj", LO, HI)
    wv = ROOT.RooRealVar("w", "w", -100, 100)
    ds = ROOT.RooDataSet("ds", "", ROOT.RooArgSet(x, wv), ROOT.RooFit.WeightVar(wv))
    for mi, wi in zip(m, w):
        if LO <= mi < HI and wi != 0:
            x.setVal(float(mi)); wv.setVal(float(wi)); ds.add(ROOT.RooArgSet(x, wv), float(wi))
    out, keep = {}, []
    for name, (expr, pars) in SHAPES.items():
        vs = [ROOT.RooRealVar(f"{name}_{p[0]}", p[0], p[1], p[2], p[3]) for p in pars]
        keep += vs
        al = ROOT.RooArgList(x); [al.add(v) for v in vs]
        fexpr = expr.format(**{p[0]: f"@{i + 1}" for i, p in enumerate(pars)}).replace("XM", "@0")
        pdf = ROOT.RooGenericPdf(f"pdf_{name}", fexpr, al)
        keep.append(pdf)
        r = pdf.fitTo(ds, ROOT.RooFit.SumW2Error(True), ROOT.RooFit.Save(True), ROOT.RooFit.PrintLevel(-1),
                      ROOT.RooFit.Minimizer("Minuit2", "migrad"))
        n = len(pars)
        pv = np.array([v.getVal() for v in vs])
        cm = r.covarianceMatrix()
        cov = np.array([[cm[i][j] for j in range(n)] for i in range(n)])
        out[name] = (pv, cov, r.status(), r.minNll())
    return out


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
    wD = ff_weights(d, D, rm, a.k, a.lmax)
    wP = ff_weights(d, M & (d["pair"] == "PP"), rm, a.k, a.lmax)
    use = (wD != 0) | (wP != 0)
    mev = d["mlljj"][use]
    wev = (wD - wP)[use]
    N, Ne = wev.sum(), np.sqrt((wev ** 2).sum())
    obs = np.histogram(d["mlljj"][D & (d["cat"] == "TT")], CARD)[0].astype(float)
    mp = M & (d["cat"] == "TT") & (d["pair"] == "PP")
    obs -= np.histogram(d["mlljj"][mp], CARD, weights=d["weight"][mp])[0]
    hist_card = np.histogram(mev, CARD, weights=wev)[0]
    hist_card_e = np.sqrt(np.histogram(mev, CARD, weights=wev ** 2)[0])
    yc = np.histogram(mev, COARSE, weights=wev)[0]; ec = np.sqrt(np.histogram(mev, COARSE, weights=wev ** 2)[0])
    txt = [f"# DY CR mumu SS data; fake weights F k (k={a.k}, L<{a.lmax}), events {use.sum()}, N = {N:.2f} +- {Ne:.2f}",
           "card bins: " + " ".join(f"{int(v)}" for v in CARD),
           "histogram   : " + " ".join(f"{v:6.2f}" for v in hist_card),
           "  hist err  : " + " ".join(f"{v:6.2f}" for v in hist_card_e),
           "data TT-PP  : " + " ".join(f"{v:6.2f}" for v in obs),
           "coarse bins: " + " ".join(str(int(v)) for v in COARSE) + "  content " + " ".join(f"{v:.2f}±{e:.2f}" for v, e in zip(yc, ec))]
    rng = np.random.default_rng(11)
    cres = coarse_fit(yc, ec)
    ures = unbinned_fit(mev, wev)
    fig, axes = plt.subplots(1, 2, figsize=(22, 9), sharey=True)
    mm = np.linspace(LO, HI, 300)
    fine = np.array([800, 900, 1000, 1100, 1200, 1350, 1500, 1700, 2000, 2400, 3000, 4000], float)
    hf = np.histogram(mev, fine, weights=wev)[0]; hfe = np.sqrt(np.histogram(mev, fine, weights=wev ** 2)[0])
    for ax, (title, res, kind) in zip(axes, (("(a) coarse-bin chi2 fit", cres, "coarse"), ("(b) unbinned weighted likelihood", ures, "unbinned"))):
        wid = np.diff(fine); ctr = 0.5 * (fine[:-1] + fine[1:])
        ax.errorbar(ctr, hf / wid, yerr=hfe / wid, xerr=wid / 2, fmt="s", color="#9c9ca1", label="fake estimate (fine bins)")
        if kind == "coarse":
            cw = np.diff(COARSE); cc = 0.5 * (COARSE[:-1] + COARSE[1:])
            ax.errorbar(cc, yc / cw, yerr=ec / cw, xerr=cw / 2, fmt="D", color="black", mfc="none", label="fitted coarse bins")
        txt.append(f"\n## {title}")
        for name, r in res.items():
            if r is None or r[0] is None:
                txt.append(f"  {name}: fit failed"); continue
            if kind == "coarse":
                pv, cov, chi2, ndf = r
                shape_p, norm_fn = pv[1:], None
                toys = rng.multivariate_normal(pv, cov, size=300)
                curve = lambda t: t[0] * shape_eval(name, t[1:], mm)[0]  # noqa: E731
                cen = curve(pv)
                ints = bin_integrals(name, pv[1:], CARD, 1.0) * (pv[0] * shape_eval(name, pv[1:], [LO])[1].Integral(LO, HI))
                tint = np.array([bin_integrals(name, t[1:], CARD, 1.0) * (t[0] * shape_eval(name, t[1:], [LO])[1].Integral(LO, HI)) for t in toys[:100]])
                lab = f"{name}: $\\chi^2$/ndf {chi2:.1f}/{ndf}"
            else:
                pv, cov, status, nll = r
                _, tf = shape_eval(name, pv, [LO]); tot = tf.Integral(LO, HI)
                cen = N * shape_eval(name, pv, mm)[0] / tot
                ints = bin_integrals(name, pv, CARD, N)
                toys = rng.multivariate_normal(pv, cov, size=100)
                Ns = rng.normal(N, Ne, size=100)
                tint = np.array([bin_integrals(name, t, CARD, n) for t, n in zip(toys, Ns)])
                curve = None
                lab = f"{name}: status {status}"
            lo_, hi_ = np.percentile(tint, [16, 84], axis=0)
            ax.plot(mm, cen, color=FCOL[name], lw=2, label=lab)
            txt.append(f"  {name:6s} pars {np.round(pv, 4).tolist()}  {lab.split(': ')[1]}")
            txt.append("     per card bin: " + " ".join(f"{v:6.3f}" for v in ints) + f"   (sum {ints.sum():.2f})")
            txt.append("     68% band   : " + " ".join(f"{l:.3f}-{h:.3f}" for l, h in zip(lo_, hi_)))
        ax.set_yscale("log"); ax.set_ylim(1e-6, 1); ax.set_xlim(LO, HI)
        ax.set_xlabel(r"$m_{\mu\mu jj}$ (GeV)"); ax.text(0.04, 0.05, title, transform=ax.transAxes, fontsize=17)
        ax.legend(fontsize=13, loc="upper right")
        hep.cms.label(ax=ax, label="Preliminary", data=True, lumi=109.8, com=13.6, fontsize=15)
    axes[0].set_ylabel("fake events / GeV")
    od = os.path.join(L.PLOTS, "dycr"); os.makedirs(od, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(od, f"ffshape2_dycr.{ext}"), bbox_inches="tight")
    out = os.path.join(L.RESULTS, "22_ffshape2_dycr.txt")
    open(out, "w").write("\n".join(txt) + "\n")
    print("\n".join(txt)); print("wrote", out)


if __name__ == "__main__":
    sys.exit(main())
