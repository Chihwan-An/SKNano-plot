#!/usr/bin/env python3
"""gen Z pT shape FxFx vs LO (madgraphMLM) per hadron-level jet category, incl. the boosted-like ones:
  Incl        all events                          GenJ2      >= 2 AK4 GenJets (pT>40, |eta|<2.5, dR(lep)>0.4)
  GenJ2noFJ   >= 2 AK4 GenJets and no AK8 GenJet   GenFJ1     >= 1 AK8 GenJet (pT>200, |eta|<2.4, dR(lep)>0.8)
  GenFJ1x     >= 1 AK8 GenJet and < 2 AK4 GenJets (fails the resolved topology)
Same conventions as make_dy_gen_compare.py: LHE_HT > 40 on both, unit-normalised in the window, ratio FxFx/LO."""
import argparse, importlib.util, json, os
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
S = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/HNWR/scripts"
_s = importlib.util.spec_from_file_location("_n", os.path.join(S, "make_dy_zpt_njet.py")); N = importlib.util.module_from_spec(_s); _s.loader.exec_module(N)
ap = argparse.ArgumentParser(); ap.add_argument("--base", default="/gv0/Users/achihwan/SKNanoOutput_dynew/DYGenZpT"); ap.add_argument("--era", default="2024")
ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")); a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
lumi = N.Z.LUMI[a.era] * 1000.0; _, LO = N.Z.samples_for(a.era)
TAGS = {"Incl": ("all events", "0.3", "-"), "GenJ2": (r"$\geq$2 AK4 GenJets", "tab:red", "-"), "GenJ2noFJ": (r"$\geq$2 AK4, no AK8", "tab:orange", "--"),
        "GenFJ1": (r"$\geq$1 AK8 GenJet (pT>200)", "tab:blue", "-"), "GenFJ1x": (r"$\geq$1 AK8 and <2 AK4", "tab:green", "--")}
EDGES = np.array([0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 1000, 1500, 2500.])
WIN = {"mll60to150": (60, 150), "mllAll": (0, 8000), "mllGt400": (400, 8000)}
rep = {}
for wname, (mlo, mhi) in WIN.items():
    fig, (ax, rax) = plt.subplots(2, 1, figsize=(8, 8.4), sharex=True, gridspec_kw=dict(height_ratios=[2, 1.3], hspace=0.05))
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    for tag, (lab, col, ls) in TAGS.items():
        lo = N.load(a.base, a.era, LO, "Central", N.hname(tag), lumi, mlo, mhi); fx = N.load(a.base, a.era, N.FXFX, "Central", N.hname(tag), lumi, mlo, mhi)
        if lo is None or fx is None: print("missing", tag); continue
        src = lo[2]; l, lv, f, fv = (N.rebin(x, src, EDGES) for x in (lo[0], lo[1], fx[0], fx[1]))
        w = np.diff(EDGES); c = np.sqrt(np.maximum(EDGES[:-1], 5) * EDGES[1:])
        K = f.sum() / l.sum(); r = np.where(l > 0, (f / f.sum()) / np.where(l > 0, l / l.sum(), 1), np.nan)
        re = np.abs(r) * np.sqrt(np.where(f > 0, fv / np.maximum(f, 1e-12) ** 2, 0) + np.where(l > 0, lv / np.maximum(l, 1e-12) ** 2, 0))
        ax.step(EDGES, np.r_[l / l.sum() / w, (l / l.sum() / w)[-1]], where="post", color=col, ls=ls, lw=1.4, label=f"{lab}: LO (FxFx dotted)")
        ax.step(EDGES, np.r_[f / f.sum() / w, (f / f.sum() / w)[-1]], where="post", color=col, ls=":", lw=1.4)
        rax.errorbar(c, r, np.nan_to_num(re), fmt="o" + ls, ms=3.5, color=col, lw=1.2, label=f"{lab}   K={K:.2f}, N_FxFx={f.sum():.2e}")
        ax2.errorbar(c, r * K, np.nan_to_num(re * K), fmt="o" + ls, ms=3.5, color=col, lw=1.2, label=f"{lab}   (raw, K={K:.2f})")
        rep.setdefault(wname, {})[tag] = dict(edges=EDGES.tolist(), shape_ratio=r.tolist(), err=re.tolist(), K=float(K), lo=l.tolist(), fxfx=f.tolist(), frac_lo=float(l.sum()), frac_fx=float(f.sum()))
    ax.set_yscale("log"); ax.set_ylabel("unit-normalised / GeV"); ax.legend(fontsize=8); ax.set_title(f"DY gen $p_T(Z)$ shape, {a.era}: $H_T^{{LHE}}>40$, m(ll) {mlo:.0f}-{mhi:.0f}, per jet category", fontsize=10)
    rax.axhline(1, color="k", lw=0.8, ls=":"); rax.set_ylim(0.3, 1.5); rax.set_ylabel("FxFx / LO (shape)"); rax.set_xlabel("gen $p_T(Z)$ [GeV]"); rax.legend(fontsize=7); rax.set_xscale("symlog", linthresh=100); rax.set_xlim(0, 2500)
    fig.savefig(f"{a.out}/zpt_shape_ratio_by_jetcat_{wname}_{a.era}.png", dpi=130); fig.savefig(f"{a.out}/zpt_shape_ratio_by_jetcat_{wname}_{a.era}.pdf"); plt.close(fig)
    ax2.axhline(1, color="k", lw=0.8, ls=":"); ax2.set_ylim(0.3, 1.8); ax2.set_ylabel("FxFx / LO (absolute, not normalised)"); ax2.set_xlabel("gen $p_T(Z)$ [GeV]"); ax2.set_xscale("symlog", linthresh=100); ax2.set_xlim(0, 2500); ax2.legend(fontsize=7)
    ax2.set_title(f"absolute NLO/LO per jet category, m(ll) {mlo:.0f}-{mhi:.0f}", fontsize=10); fig2.tight_layout(); fig2.savefig(f"{a.out}/zpt_abs_ratio_by_jetcat_{wname}_{a.era}.png", dpi=130); plt.close(fig2)
    print(f"\n== m(ll) {mlo:.0f}-{mhi:.0f}: FxFx/LO shape ratio (K = absolute FxFx/LO)")
    print("%-12s %6s %8s" % ("cat", "K", "fracLO") + "".join("%9s" % f"{EDGES[k]:.0f}-{EDGES[k+1]:.0f}" for k in range(len(EDGES) - 1)))
    tot = rep[wname]["Incl"]["frac_lo"]
    for tag, x in rep[wname].items(): print("%-12s %6.3f %7.1f%%" % (tag, x["K"], 100 * x["frac_lo"] / tot) + "".join("%9s" % (f"{v:.2f}" if np.isfinite(v) else "-") for v in x["shape_ratio"]))
json.dump(rep, open(f"{a.out}/zpt_ratio_by_jetcat_{a.era}.json", "w"), indent=1); print("wrote", a.out)
