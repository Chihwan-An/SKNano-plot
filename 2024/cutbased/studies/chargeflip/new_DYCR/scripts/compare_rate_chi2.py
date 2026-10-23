#!/usr/bin/env python3
"""LO (madgraphMLM HT-binned, new DY correction) vs NLO (aMC@NLO FxFx) vs the previous baseline:
flip rate P(|eta_SC|, pT), energy shift f and its chi2, MC closure.  Inputs = chargeflip_ptshift.py jsons.
    compare_rate_chi2.py --lo f.json --nlo f.json [--old f.json] --out DIR"""
import argparse, json, os
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
ap = argparse.ArgumentParser(); ap.add_argument("--lo", required=True); ap.add_argument("--nlo", required=True)
ap.add_argument("--old", default=None); ap.add_argument("--out", required=True); a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
J = {"LO new DY": json.load(open(a.lo)), "NLO FxFx": json.load(open(a.nlo))}
if a.old: J["LO old (baseline)"] = json.load(open(a.old))
ref = J["LO new DY"]; pt = np.array(ref["pt_edges"]); lab = [f"{int(x)}-{int(y)}" for x, y in zip(pt[:-1], pt[1:])]
eta = list(ref["rate_regions"]); L = ["# Charge-flip rate and energy-shift chi2: LO vs NLO\n"]

L.append("## Flip rate P x 1e3 (stat), per |eta_SC| x pT [GeV]\n")
pulls = []
for i, r in enumerate(eta):
    L.append(f"### {r}\n"); L.append("| sample | " + " | ".join(lab) + " |"); L.append("|---|" + "---|" * len(lab))
    for k, d in J.items():
        P, E = np.array(d["P"])[i], np.array(d["P_err"])[i]
        L.append(f"| {k} | " + " | ".join(f"{1e3*p:.3f} ± {1e3*e:.3f}" for p, e in zip(P, E)) + " |")
    P0, E0 = np.array(ref["P"])[i], np.array(ref["P_err"])[i]; P1, E1 = np.array(J["NLO FxFx"]["P"])[i], np.array(J["NLO FxFx"]["P_err"])[i]
    ok = (P0 > 0) & (P1 > 0)
    rat = np.where(ok, P1 / np.where(P0 > 0, P0, 1), np.nan); rer = rat * np.sqrt((E0 / np.where(P0 > 0, P0, 1)) ** 2 + (E1 / np.where(P1 > 0, P1, 1)) ** 2)
    pl = np.where(ok, (P1 - P0) / np.sqrt(E0 ** 2 + E1 ** 2 + 1e-300), np.nan); pulls += [x for x in pl if np.isfinite(x)]
    L.append("| **NLO / LO** | " + " | ".join(f"{x:.3f} ± {e:.3f}" if np.isfinite(x) else "–" for x, e in zip(rat, rer)) + " |")
    L.append("| pull | " + " | ".join(f"{x:+.2f}" if np.isfinite(x) else "–" for x in pl) + " |\n")
pulls = np.array(pulls)
L.append(f"**Rate comparison NLO vs LO: chi2 = {np.sum(pulls**2):.1f} / {len(pulls)} bins, mean pull {pulls.mean():+.2f}, rms {pulls.std():.2f}.**\n")

L.append("## Energy shift f and chi2 (response of flipped vs OS-prompt electrons)\n")
for r in ref["shift"]:
    L.append(f"### {r}\n"); L.append("| sample | quantity | " + " | ".join(lab) + " |"); L.append("|---|---|" + "---|" * len(lab))
    for k, d in J.items():
        rows = d["shift"][r]
        L.append(f"| {k} | f [1σ] | " + " | ".join((f"{x['f']:.3f} [{x['f_lo']:.3f}, {x['f_hi']:.3f}]" if x.get("f_lo") is not None else "–") for x in rows) + " |")
        L.append(f"| {k} | chi2_min / ndf | " + " | ".join((f"{x['chi2_min']:.1f} / {x['ndf']}" if "chi2_min" in x else "–") for x in rows) + " |")
        L.append(f"| {k} | chi2(f=1) | " + " | ".join((f"{x['chi2_at_1']:.1f}" if "chi2_at_1" in x else "–") for x in rows) + " |")
        L.append(f"| {k} | N_flip | " + " | ".join(str(x["n_flip"]) for x in rows) + " |")
    L.append("")
L.append("## MC closure (OS MC x W vs SS MC)\n")
for k, d in J.items(): L.append(f"- {k}: `{json.dumps(d.get('closure'))[:600]}`")
open(os.path.join(a.out, "rate_chi2_LO_vs_NLO.md"), "w").write("\n".join(L) + "\n"); print("\n".join(L))

fig, axs = plt.subplots(2, len(eta), figsize=(4 * len(eta), 6.5), sharex=True, gridspec_kw=dict(height_ratios=[3, 1.3]))
c = 0.5 * (pt[:-1] + pt[1:]); col = {"LO new DY": "tab:red", "NLO FxFx": "tab:blue", "LO old (baseline)": "0.5"}
for i, r in enumerate(eta):
    for k, d in J.items():
        P, E = np.array(d["P"])[i], np.array(d["P_err"])[i]; m = P > 0
        axs[0, i].errorbar(c[m], P[m], E[m], fmt="o-" if "old" not in k else "s--", ms=4, color=col[k], label=k)
        if k != "LO new DY":
            P0, E0 = np.array(ref["P"])[i], np.array(ref["P_err"])[i]; mm = m & (P0 > 0)
            axs[1, i].errorbar(c[mm], P[mm] / P0[mm], (P[mm] / P0[mm]) * np.sqrt((E[mm] / P[mm]) ** 2 + (E0[mm] / P0[mm]) ** 2), fmt="o", ms=4, color=col[k])
    axs[0, i].set_title(f"|eta_SC| {r}"); axs[0, i].set_xscale("log"); axs[0, i].set_yscale("log"); axs[1, i].axhline(1, color="k", lw=0.8)
    axs[1, i].set_ylim(0.5, 1.5); axs[1, i].set_xlabel("electron pT [GeV]")
axs[0, 0].set_ylabel("flip rate P"); axs[1, 0].set_ylabel("/ LO new DY"); axs[0, 0].legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(a.out, "rate_LO_vs_NLO.png"), dpi=120); fig.savefig(os.path.join(a.out, "rate_LO_vs_NLO.pdf"))
