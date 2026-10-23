#!/usr/bin/env python3
"""DY CR mumu SS (60<=mll<150, mlljj>800, FO baseline, iso-TT): data vs background BEFORE and AFTER replacing
the MC nonprompt by the data-driven fake-factor estimate.
  before: MC stack by sample group (DY / TT+tW / Nonprompt = TTLJ+W+jets+ST / Others = VV+ttV+VVV), all truth
  after : MC with both muons truth-prompt (PP) only, same groups, + Fake (data) =
          sum_data(fail) w_FF - sum_MC(fail, PP) w_FF   with F = k f/(1-f)
  map: MC truth-F fake rate from the FOLOW production (60<mll<300, SS+OS), |eta| 0/0.8/1.5/2.0/2.4, one pT bin,
       T: TkRelIso<0.1, L: 0.1<=TkRelIso<LMAX; k = data calibration (default 1.27, mll 60-300).
  -> out/nonprompt_ssmm/dycr/dycr_ss_ffapply[_k<k>].{png,pdf}, results/19_dycr_ffapply.txt
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
import fr_mll60300 as FR  # noqa: E402
import folib as L  # noqa: E402

hep.style.use("CMS")
GROUP = {"DY": "DY", "TTLL": "TT+tW", "tW": "TT+tW", "TTLJ": "Nonprompt", "W+jets(HT)": "Nonprompt",
         "ST s/t": "Nonprompt", "VV": "Others", "ttV": "Others", "VVV": "Others"}
GCOL = {"DY": "#ffd700", "TT+tW": "#e42536", "Nonprompt": "#2ca02c", "Others": "#5790fc", "Fake (data)": "#9c9ca1"}
VARS = [("mlljj", r"$m_{\mu\mu jj}$ (GeV)", np.array([800, 1000, 1200, 1500, 2000, 3000], float), lambda d: d["mlljj"]),
        ("lead_pt", r"leading $\mu$ $p_T$ (GeV)", np.array([53, 80, 120, 200, 300, 500, 1000], float), lambda d: d["mu1_pt"]),
        ("sub_pt", r"subleading $\mu$ $p_T$ (GeV)", np.array([53, 60, 80, 120, 200, 400], float), lambda d: d["mu2_pt"])]


def ff_weights(d, m, rm, k, lmax):
    """F = k f/(1-f) of the failing muon(s); fail muons must have iso < lmax."""
    ok = m & (d["cat"] != "TT")
    ok &= ~np.isin(d["cat"], ["LT", "LL"]) | (d["mu1_tkRelIso"] < lmax)
    ok &= ~np.isin(d["cat"], ["TL", "LL"]) | (d["mu2_tkRelIso"] < lmax)
    f1 = rm.lookup(d["mu1_pt"], d["mu1_eta"]); f2 = rm.lookup(d["mu2_pt"], d["mu2_eta"])
    F1 = k * f1 / (1 - f1); F2 = k * f2 / (1 - f2)
    c = d["cat"]
    fac = np.where(c == "TL", F2, np.where(c == "LT", F1, np.where(c == "LL", -F1 * F2, 0.0)))
    return np.where(ok, d["weight"] * fac, 0.0)


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
    TT = d["cat"] == "TT"
    wff_D = ff_weights(d, D, rm, a.k, a.lmax)
    wff_P = ff_weights(d, M & (d["pair"] == "PP"), rm, a.k, a.lmax)
    txt = [f"# DY CR mumu SS, FO baseline, iso-TT. map mll 60-300 MC, |eta| {FR.ETA}, L<{a.lmax}, k={a.k}",
           "# map f per |eta| bin: " + " ".join(f"{x:.3f}" for x in rm.r[0])]
    fig, axes = plt.subplots(4, 3, figsize=(27, 22), gridspec_kw={"height_ratios": [3, 1, 3, 1]}, sharex="col")
    for c, (vn, xl, edges, fx) in enumerate(VARS):
        x = fx(d)
        hD = np.histogram(x[D & TT], edges)[0].astype(float)
        before, after = {}, {}
        e2b, e2a = 0.0, 0.0   # sum of w^2 of the MC stack (stat error band)
        for p, g in GROUP.items():
            mp = M & TT & (d["proc"] == p)
            before[g] = before.get(g, 0) + np.histogram(x[mp], edges, weights=d["weight"][mp])[0]
            e2b = e2b + np.histogram(x[mp], edges, weights=d["weight"][mp] ** 2)[0]
            mpp = mp & (d["pair"] == "PP")
            after[g] = after.get(g, 0) + np.histogram(x[mpp], edges, weights=d["weight"][mpp])[0]
            e2a = e2a + np.histogram(x[mpp], edges, weights=d["weight"][mpp] ** 2)[0]
        fake = np.histogram(x, edges, weights=wff_D)[0] - np.histogram(x, edges, weights=wff_P)[0]
        fake_e2 = np.histogram(x, edges, weights=wff_D ** 2)[0] + np.histogram(x, edges, weights=wff_P ** 2)[0]
        after["Fake (data)"] = fake
        e2a = e2a + fake_e2   # after: MC (prompt) stat + fake-estimate stat (data fail + prompt subtraction)
        for row, (lab, stk, e2) in enumerate((("before: MC nonprompt", before, e2b), ("after: data-driven fake", after, e2a))):
            ax, rx = axes[2 * row, c], axes[2 * row + 1, c]
            order = [g for g in ("Others", "Fake (data)", "Nonprompt", "TT+tW", "DY") if g in stk]
            hep.histplot([stk[g] for g in order], edges, stack=True, histtype="fill", color=[GCOL[g] for g in order],
                         label=order, ax=ax, edgecolor="k", lw=0.5)
            tot = sum(stk[g] for g in order)
            err = np.sqrt(e2)
            ax.stairs(tot + err, edges, baseline=np.clip(tot - err, 1e-3, None), fill=True, color="none",
                      hatch="////", edgecolor="grey", lw=0, label="bkg stat unc.")
            hep.histplot(hD, edges, yerr=np.sqrt(hD), histtype="errorbar", color="k", label="data", ax=ax)
            ax.set_yscale("log"); ax.set_ylim(0.1, max(hD.max(), tot.max()) * 30)
            ax.text(0.04, 0.92, lab, transform=ax.transAxes, fontsize=18)
            ax.legend(loc="upper right", fontsize=13, ncol=2)
            with np.errstate(divide="ignore", invalid="ignore"):
                rx.errorbar(0.5 * (edges[:-1] + edges[1:]), hD / tot, yerr=np.sqrt(hD) / tot, fmt="ko")
            with np.errstate(divide="ignore", invalid="ignore"):
                rel = np.where(tot > 0, err / tot, 0)
            rx.stairs(1 + rel, edges, baseline=1 - rel, fill=True, color="none", hatch="////", edgecolor="grey", lw=0)
            rx.axhline(1, color="grey", ls="--"); rx.set_ylim(0, 2); rx.set_ylabel("data / bkg", fontsize=16)
            ax.set_ylabel("events / bin")
            hep.cms.label(ax=ax, label="Preliminary", data=True, lumi=109.8, com=13.6, fontsize=15)
            txt.append(f"{vn} {lab:25s} data {hD.sum():.0f}  bkg {tot.sum():.1f} ± {np.sqrt(e2.sum()):.1f}(stat)  "
                       + "  ".join(f"{g} {stk[g].sum():.1f}" for g in order)
                       + (f"  (fake stat ±{np.sqrt(fake_e2.sum()):.1f})" if 'Fake (data)' in stk else ""))
        axes[3, c].set_xlabel(xl)
    od = os.path.join(L.PLOTS, "dycr"); os.makedirs(od, exist_ok=True)
    tag = f"_k{a.k:g}" if a.k != 1.27 else ""
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(od, f"dycr_ss_ffapply{tag}.{ext}"), bbox_inches="tight")
    out = os.path.join(L.RESULTS, f"19_dycr_ffapply{tag}.txt")
    open(out, "w").write("\n".join(txt) + "\n")
    print("\n".join(txt)); print("wrote", out)


if __name__ == "__main__":
    sys.exit(main())
