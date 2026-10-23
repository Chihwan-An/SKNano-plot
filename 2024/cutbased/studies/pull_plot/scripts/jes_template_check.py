#!/usr/bin/env python3
"""Which CR channel wants JES_2024 up, and how strongly -- from the card templates alone (no combine).

For every CR channel of the v2 card (data, not Asimov) this fits ONE nuisance, JES_2024 = theta, together with
the free rate parameters that act in that channel (R_DY_* on DYJets, R_TT_* on TT), by chi2 on the m_lljj bins:
    pred_b(theta, mu) = sum_p mu_p * N_p,b * (1 + theta * delta_p,b)        delta = Up/nom - 1 (theta>0), 1 - Down/nom (theta<0)
    chi2 = sum_b (data_b - pred_b)^2 / (data_b + sigma_MC,b^2)              no prior on theta
theta_hat and its +-1 (delta chi2 = 1) interval say what the channel alone asks for and how tightly it pins JES.
Also a joint fit of the three resolved CRs (rFlvCR, rDYEECR_OS, rDYMuMuCR_OS) with shared R_DY_Resolved / R_TT_Resolved.
Every other nuisance is held at 0 -- this is a single-knob picture, not the full fit.

  python3 jes_template_check.py [--shapes F] [--out DIR] [--syst JES_2024]
"""
import argparse, os
import numpy as np
import uproot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SHAPES = ("/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/combine/scenarios/test/"
          "cbv15_an2_ref_v2/shapes_2024_cbv15_an2_ref_v2.root")
PROCS = ["DYJets", "TT", "Nonprompt", "Others", "Flip"]   # Flip = data-driven SS flip (rDYEECR_SS); absent elsewhere
# free rate parameters per channel (from the v2 card rateParam lines)
FREE = {"rDYEECR_OS": ["DYJets", "TT"], "rDYMuMuCR_OS": ["DYJets", "TT"], "rDYMuMuCR_SS": ["DYJets"],
        "rDYEECR_SS": [], "rFlvCR": ["TT"], "bDYEECR": ["DYJets", "TT"], "bDYMuMuCR": ["DYJets", "TT"],
        "bFlvEMuCR": ["TT"], "bFlvMuECR": ["TT"]}
CHANNELS = list(FREE)
THETA = np.arange(-5.0, 15.0001, 0.01)


def load(f, ch, syst):
    d = f[ch]
    data = d["data_obs"].values()
    out = {"data": data, "edges": d["data_obs"].axis().edges(), "N": {}, "var": np.zeros_like(data), "up": {}, "dn": {}}
    for p in PROCS:
        if p not in d: continue
        h = d[p]; n = h.values(); out["N"][p] = n; out["var"] += h.errors() ** 2
        u = d[f"{p}_{syst}Up"].values() if f"{p}_{syst}Up" in d else n
        w = d[f"{p}_{syst}Down"].values() if f"{p}_{syst}Down" in d else n
        with np.errstate(divide="ignore", invalid="ignore"):
            out["up"][p] = np.where(n > 0, u / n - 1, 0.0); out["dn"][p] = np.where(n > 0, 1 - w / n, 0.0)
    return out


def templates(c, theta):
    return {p: c["N"][p] * (1 + theta * (c["up"][p] if theta >= 0 else c["dn"][p])) for p in c["N"]}


def chi2_profile(chs, free_map, shared=None):
    """chi2(theta) with the free norms profiled (weighted linear LS). shared: list of (name, [(ch, proc), ...])."""
    out = []
    for t in THETA:
        cols, rows_y, rows_w, fixed = {}, [], [], []
        # parameter list: shared names, else per-channel (ch, proc)
        pars = []
        if shared:
            pars = [s[0] for s in shared]
            owner = {cp: s[0] for s in shared for cp in s[1]}
        else:
            owner = {(ch, p): (ch, p) for ch in chs for p in free_map[ch]}
            pars = list(dict.fromkeys(owner.values()))
        A, y, w = [], [], []
        for ch in chs:
            c = C[ch]; T = templates(c, t); nb = len(c["data"])
            fixed_part = np.zeros(nb); colmat = np.zeros((nb, len(pars)))
            for p, v in T.items():
                k = owner.get((ch, p))
                if k is None: fixed_part += v
                else: colmat[:, pars.index(k)] += v
            sig2 = np.maximum(c["data"], 1.0) + c["var"]
            A.append(colmat); y.append(c["data"] - fixed_part); w.append(1 / sig2)
        A = np.vstack(A); y = np.concatenate(y); w = np.concatenate(w)
        if A.shape[1]:
            sw = np.sqrt(w); mu, *_ = np.linalg.lstsq(A * sw[:, None], y * sw, rcond=None)
            r = y - A @ mu
        else:
            mu, r = np.array([]), y
        out.append((float(np.sum(r * r * w)), mu))
    return np.array([o[0] for o in out]), [o[1] for o in out], pars


def summarize(chi2):
    i = int(np.argmin(chi2)); m = chi2[i]; th = THETA[i]
    inside = THETA[chi2 <= m + 1.0]
    lo, hi = (inside.min(), inside.max()) if len(inside) else (np.nan, np.nan)
    return th, th - lo, hi - th, m, chi2[np.argmin(np.abs(THETA))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shapes", default=SHAPES); ap.add_argument("--syst", default="JES_2024")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results"))
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    f = uproot.open(a.shapes)
    global C
    C = {ch: load(f, ch, a.syst) for ch in CHANNELS}
    L = [f"# {a.syst}: single-nuisance template fit per CR channel", "", f"shapes: `{a.shapes}`", "",
         "theta_hat = value this channel alone wants (other nuisances at 0, channel's free rateParams profiled, no prior).",
         "err = half width at delta chi2 = 1 (1.0 would equal the prior width). chi2(0) - chi2min = how much the channel prefers theta_hat over 0.", "",
         "| channel | nbins | data | free norms | theta_hat | -err | +err | chi2min | chi2(0) | delta |", "|---|---|---|---|---|---|---|---|---|---|"]
    curves = {}
    for ch in CHANNELS:
        chi2, mus, pars = chi2_profile([ch], FREE)
        th, el, eh, m, c0 = summarize(chi2); curves[ch] = chi2
        L.append(f"| {ch} | {len(C[ch]['data'])} | {C[ch]['data'].sum():.0f} | {','.join(FREE[ch]) or '-'} | **{th:+.2f}** | {el:.2f} | {eh:.2f} | {m:.1f} | {c0:.1f} | {c0 - m:.1f} |")
    # joint resolved fit with shared rateParams (what the combined fit does for these three)
    J = ["rFlvCR", "rDYEECR_OS", "rDYMuMuCR_OS"]
    shared = [("R_DY_Resolved", [("rDYEECR_OS", "DYJets"), ("rDYMuMuCR_OS", "DYJets")]),
              ("R_TT_Resolved", [("rFlvCR", "TT"), ("rDYEECR_OS", "TT"), ("rDYMuMuCR_OS", "TT")])]
    L += ["", "## joint resolved CRs, shared R_DY_Resolved / R_TT_Resolved", "",
          "| channels | theta_hat | -err | +err | chi2min | chi2(0) | R_DY | R_TT |", "|---|---|---|---|---|---|---|---|"]
    for sub in [J, ["rDYEECR_OS", "rDYMuMuCR_OS"], ["rFlvCR", "rDYEECR_OS"], ["rFlvCR", "rDYMuMuCR_OS"]]:
        sh = [(n, [cp for cp in l if cp[0] in sub]) for n, l in shared]; sh = [s for s in sh if s[1]]
        chi2, mus, pars = chi2_profile(sub, FREE, shared=sh)
        th, el, eh, m, c0 = summarize(chi2); mu = mus[int(np.argmin(chi2))]
        md = dict(zip(pars, mu)); curves["+".join(sub)] = chi2
        L.append(f"| {' + '.join(sub)} | **{th:+.2f}** | {el:.2f} | {eh:.2f} | {m:.1f} | {c0:.1f} | "
                 f"{md.get('R_DY_Resolved', float('nan')):.3f} | {md.get('R_TT_Resolved', float('nan')):.3f} |")
    # per-bin table for the three resolved CRs
    for ch in J + ["bDYMuMuCR", "bFlvMuECR"]:
        c = C[ch]; mc = sum(c["N"].values())
        L += ["", f"## {ch}: prefit per bin", "",
              "| m_lljj | data | MC | data/MC | JES Up (total MC) | JES Down | DY frac | TT frac |", "|---|---|---|---|---|---|---|---|"]
        up = sum(c["N"][p] * (1 + c["up"][p]) for p in c["N"]); dn = sum(c["N"][p] * (1 - c["dn"][p]) for p in c["N"])
        e = c["edges"]
        for i in range(len(mc)):
            L.append(f"| {e[i]:.0f}-{e[i+1]:.0f} | {c['data'][i]:.0f} | {mc[i]:.1f} | {c['data'][i]/mc[i]:.3f} ± {np.sqrt(c['data'][i])/mc[i]:.3f} | "
                     f"{up[i]/mc[i]-1:+.3f} | {dn[i]/mc[i]-1:+.3f} | {c['N'].get('DYJets', np.zeros_like(mc))[i]/mc[i]:.2f} | {c['N'].get('TT', np.zeros_like(mc))[i]/mc[i]:.2f} |")
    md = "\n".join(L) + "\n"; open(os.path.join(a.out, f"template_fit_{a.syst}.md"), "w").write(md); print(md)

    # plots: chi2 curves, and data/MC ratio vs the JES Up/Down shift for the resolved CRs
    fig, ax = plt.subplots(figsize=(7, 5))
    for k, v in curves.items():
        if k in CHANNELS and FREE[k] == [] and C[k]["data"].sum() < 50: continue
        ax.plot(THETA, v - v.min(), label=k, lw=2.2 if "+" in k else 1.2, ls="-" if "+" in k or k.startswith("r") else "--")
    ax.axhline(1, color="gray", lw=0.8); ax.axvline(0, color="gray", lw=0.8)
    ax.set_ylim(0, 12); ax.set_xlabel(f"{a.syst} (theta, prior 0 +- 1)"); ax.set_ylabel("delta chi2"); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(a.out, f"chi2_{a.syst}.png"), dpi=130); plt.close(fig)
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, ch in zip(axs, J):
        c = C[ch]; mc = sum(c["N"].values()); e = c["edges"]; x = np.arange(len(mc))
        up = sum(c["N"][p] * (1 + c["up"][p]) for p in c["N"]); dn = sum(c["N"][p] * (1 - c["dn"][p]) for p in c["N"])
        r = c["data"] / mc; er = np.sqrt(c["data"]) / mc
        ax.errorbar(x, r / (c["data"].sum() / mc.sum()), er / (c["data"].sum() / mc.sum()), fmt="ko", label="data/MC (norm. to total)")
        for th, col in [(1, "tab:red"), (2.9, "tab:orange")]:
            v = sum(c["N"][p] * (1 + th * c["up"][p]) for p in c["N"])
            ax.step(np.r_[x - 0.5, x[-1] + 0.5], np.r_[v / mc / (v.sum() / mc.sum()), (v / mc / (v.sum() / mc.sum()))[-1]],
                    where="post", color=col, label=f"JES {th:+.1f} sigma (shape)")
        ax.axhline(1, color="gray", lw=0.8); ax.set_xticks(x); ax.set_xticklabels([f"{e[i]:.0f}" for i in x], rotation=45, fontsize=7)
        ax.set_title(ch); ax.set_xlabel("m_lljj bin low edge (GeV)"); ax.set_ylim(0.7, 1.35); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(a.out, f"shape_vs_{a.syst}.png"), dpi=130); plt.close(fig)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
