#!/usr/bin/env python3
"""2026-09-30: AN figure cfrate_invpt with the flip rate above 1 TeV merged into the 400-1000 GeV bin
(style of BDT/SR/test/scripts/chargeflip_an_figures.py:cfrate_plot; the 1-2 TeV bin is not drawn, the 400-1000 value
is extended to 1/pT = 0 with a dashed line).  cfrate_invpt_merged.py --json <ptshift json> --out <png>"""
import argparse, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
ap = argparse.ArgumentParser(); ap.add_argument("--json", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
J = json.load(open(a.json))
P = np.array(J["P"])[:, :6]; Pe = np.array(J["P_err"])[:, :6]; pt = np.array(J["pt_edges"])[:7]; pc = np.sqrt(pt[:-1] * pt[1:])
assert pt[-2:].tolist() == [400.0, 1000.0]
regs = list(J["rate_regions"]); fig, axs = plt.subplots(2, 3, figsize=(13, 7.5))
for i, (ax, r) in enumerate(zip(axs.flat, regs)):
    ok = P[i] > 0
    ax.errorbar(1 / pc[ok], P[i][ok], Pe[i][ok], xerr=[1 / pc[ok] - 1 / pt[1:][ok], 1 / pt[:-1][ok] - 1 / pc[ok]], fmt="ko", ms=4, capsize=2)
    ax.hlines(P[i][5], 0.0, 1 / 1000., colors="k", linestyles="--", lw=1.2, label=r"$p_T > 1$ TeV: 400-1000 value")
    ax.fill_between([0.0, 1 / 1000.], P[i][5] - Pe[i][5], P[i][5] + Pe[i][5], color="gray", alpha=0.3, lw=0)
    ax.set_yscale("log"); ax.set_xlim(0, 0.02); ax.set_xlabel("1/pT [1/GeV]"); ax.set_ylabel("CF rate"); ax.set_title(f"|eta_SC| {r}"); ax.grid(alpha=0.3, which="both")
    for p_ in [1000, 400, 200, 100, 60]: ax.axvline(1 / p_, color="gray", lw=0.4, ls=":"); ax.text(1 / p_, ax.get_ylim()[0] * 1.2, str(p_), fontsize=7, rotation=90)
    if i == 0: ax.legend(fontsize=8, loc="upper right")
fig.suptitle("Charge-flip rate (DY MC, raw charge, numerator at pT/f); pT > 1 TeV uses the 400-1000 GeV value")
fig.tight_layout(); fig.savefig(a.out, dpi=120); fig.savefig(a.out.replace(".png", ".pdf")); print("wrote", a.out)
