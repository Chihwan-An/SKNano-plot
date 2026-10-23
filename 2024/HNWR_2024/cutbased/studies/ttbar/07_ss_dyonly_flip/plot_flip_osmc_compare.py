#!/usr/bin/env python3
"""2026-09-30: DY charge-flip template of the resolved EE same-sign regions from
  (a) OS data x w (card v3_ss3200, one entry per event), (b) OS data with the energy shift (two entries per event),
  (c) OS MC used as the OS data, with the energy shift  -- and the flip-weight closure on the simulation (SF = 1).
Outputs flip_template_compare.{pdf,png} and flip_mc_closure.{pdf,png} in --out.
    in_container.sh python3 plot_flip_osmc_compare.py --out <dir>
"""
import argparse, json, os
import numpy as np
import uproot
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

H = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(H, "plots_osmc")); a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
SRCS = {  # flip term for DY + ttbar (--flip-groups DY,TT), energy shift; the OS data of the SR are not used (blinded)
    "rDYEECR_SS": [("OS data", "ddss_dytt_sf_ss3200_merge1000_ptshift.root", "tab:blue", "s"),
                   ("OS MC as data", "ddss_dytt_sf_ss3200_merge1000_osmc_ptshift.root", "tab:red", "^")],
    "rEESR_SS": [("OS MC as data", "ddss_dytt_sf_ss3200_merge1000_osmc_ptshift.root", "tab:red", "^")]}
REG = [("rEESR_SS", "Resolved SR, $ee$ SS (OS simulation)"), ("rDYEECR_SS", "Resolved DY CR, $ee$ SS")]


def h(f, reg, name):
    x = uproot.open(os.path.join(H, f))[f"{reg}/{name}"]
    return x.values(), np.sqrt(x.variances()), x.axis().edges()


fig, axes = plt.subplots(2, 2, figsize=(12, 8), gridspec_kw=dict(height_ratios=[3, 1.3]), sharex="col")
for c, (reg, title) in enumerate(REG):
    SRC = SRCS[reg]; ref, _, ed = h(SRC[0][1], reg, "Flip"); x = np.arange(len(ref)); lab = [f"{int(ed[i])}-{int(ed[i + 1])}" for i in range(len(ref))]
    for k, (name, f, col, mk) in enumerate(SRC):
        v, e, _ = h(f, reg, "Flip")
        axes[0, c].errorbar(x + (k - 1) * 0.15, v, yerr=e, fmt=mk, color=col, label=f"{name}: {v.sum():.1f}")
        if k: axes[1, c].errorbar(x + (k - 1) * 0.15, v / ref, yerr=e / ref, fmt=mk, color=col)
    axes[0, c].set_yscale("log"); axes[0, c].set_title(title); axes[0, c].set_ylabel("charge-flip (DY + $t\\bar{t}$) events / bin"); axes[0, c].legend(fontsize=9)
    axes[1, c].axhline(1, color="k", lw=0.8); axes[1, c].set_ylim(0.6, 1.4); axes[1, c].set_ylabel("ratio to first entry")
    if len(SRC) == 1:       # single template: show its relative statistical uncertainty instead of a ratio
        v, e, _ = h(SRC[0][1], reg, "Flip")
        axes[1, c].bar(x, 2 * e / v, bottom=1 - e / v, width=0.6, color=SRC[0][2], alpha=0.35); axes[1, c].set_ylabel("rel. stat. unc.")
    axes[1, c].set_xticks(x); axes[1, c].set_xticklabels(lab, rotation=45, fontsize=8); axes[1, c].set_xlabel(r"$m_{\ell\ell jj}$ bin [GeV]")
fig.tight_layout()
for ext in ("pdf", "png"): fig.savefig(os.path.join(a.out, f"flip_template_compare.{ext}"))

C = json.load(open(os.path.join(H, "osmc_sr_closure.json")))
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
for c, (reg, title) in enumerate(REG):
    for lab, col, mk in (("DYTT", "tab:orange", "o"), ("all", "tab:purple", "s")):
        R = C[reg][lab]; p = np.array(R["pred_bins"]); t = np.array(R["truth_bins"]); te = np.array(R["truth_bins_err"])
        ok = t > 0; x = np.arange(len(p))
        axes[c].errorbar(x[ok] + (0.1 if lab == "all" else -0.1), p[ok] / t[ok], yerr=p[ok] * te[ok] / t[ok] ** 2, fmt=mk, color=col,
                         label=f"{'DY + ttbar' if lab == 'DYTT' else 'all backgrounds'}: {R['pred']:.1f} / {R['truth']:.1f} = {R['ratio']:.3f}")
    ed = C[reg]["DY"]["edges"]
    axes[c].axhline(1, color="k", lw=0.8); axes[c].set_ylim(0.4, 1.6); axes[c].set_title(title + " (simulation, SF = 1)")
    axes[c].set_ylabel(r"OS MC $\times w$ / flipped SS MC"); axes[c].legend(fontsize=9)
    axes[c].set_xticks(np.arange(len(ed) - 1)); axes[c].set_xticklabels([f"{int(ed[i])}-{int(ed[i + 1])}" for i in range(len(ed) - 1)], rotation=45, fontsize=8)
    axes[c].set_xlabel(r"$m_{\ell\ell jj}$ bin [GeV]")
fig.tight_layout()
for ext in ("pdf", "png"): fig.savefig(os.path.join(a.out, f"flip_mc_closure.{ext}"))
print("wrote", a.out)
