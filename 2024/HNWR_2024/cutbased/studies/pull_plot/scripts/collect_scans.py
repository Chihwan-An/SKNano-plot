#!/usr/bin/env python3
"""Collect the JES_2024 likelihood scans (combine/<CH>/out/higgsCombine.<tag>.p*.MultiDimFit.mH120.root) and the
FitDiagnostics of the slope card, write results/scans.md + plots.

With JES_2024 promoted to POI, MultiDimFit drops its Gaussian constraint (checked: the prior-less minimum is 5.5
while FitDiagnostics of the same model, started at 0 or 5.5, returns 2.91 with the same NLL). So each scan is the
DATA-ONLY profile  q_data(theta) = 2 dNLL  (all other nuisances profiled with their priors), and
    q_prior(theta) = q_data(theta) + theta^2        (re-minimised)
is the profile of the full fit. The minimum of q_prior must reproduce the FitDiagnostics pull (closure check).
"""
import glob, os, re
import numpy as np
import uproot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESC = {
    "base.full": "full card (baseline)",
    "base.noMuMuOS": "- rDYMuMuCR_OS", "base.noEEOS": "- rDYEECR_OS", "base.noFlv": "- rFlvCR",
    "base.only3res": "only rFlvCR + rDYEECR_OS + rDYMuMuCR_OS",
    "base.onlyMuMuOS": "only rDYMuMuCR_OS", "base.onlyEEOS": "only rDYEECR_OS", "base.onlyFlv": "only rFlvCR",
    "base.onlySR": "only SR channels (Asimov)",
    "base.frzDYR": "full, DY R bins 1-6 + MuonTrig frozen",
    "base.onlyJES": "full, every constrained nuisance frozen except JES",
    "slope.full": "full + MassSlopeDY/TT", "slope.only3res": "3 resolved CRs + MassSlopeDY/TT",
}


def load_scan(ch, tag):
    xs, ys = [], []
    for f in glob.glob(f"{H}/combine/{ch}/out/higgsCombine.{tag}.p*.MultiDimFit.mH120.root"):
        t = uproot.open(f)["limit"]; a = t.arrays(["JES_2024", "deltaNLL", "quantileExpected"], library="np")
        m = a["quantileExpected"] > -0.5   # drop the best-fit row (-1 is the fit, kept separately)
        xs.append(a["JES_2024"][m]); ys.append(a["deltaNLL"][m])
        b = a["quantileExpected"] <= -0.5
        if b.any(): xs.append(a["JES_2024"][b]); ys.append(a["deltaNLL"][b])
    if not xs: return None
    x = np.concatenate(xs)
    if len(x) < 40 or np.min(np.concatenate(ys)) < -1e-3: return "failed"   # initial fit did not find the minimum
    y = np.concatenate(ys); o = np.argsort(x); x, y = x[o], 2 * y[o]
    ok = np.isfinite(y) & (y < 1e3)
    return x[ok], y[ok]


def interval(x, q):
    """best and +-1 sigma (q - qmin = 1) by linear interpolation on a fine grid"""
    xf = np.linspace(x.min(), x.max(), 4001); qf = np.interp(xf, x, q); i = int(np.argmin(qf)); qm = qf[i]
    inside = xf[qf <= qm + 1]
    lo, hi = inside.min(), inside.max()
    return xf[i], xf[i] - lo, hi - xf[i], qm, (lo <= x.min() + 1e-6), (hi >= x.max() - 1e-6)


def fitdiag(path, names):
    try:
        f = uproot.open(path); t = f["tree_fit_b"].arrays(library="np")
    except Exception as e:
        return None
    out = {}
    for n in names:
        if n in t: out[n] = (float(t[n][0]), float(t[n + "_Err"][0]) if n + "_Err" in t else np.nan)
    out["fit_status"] = int(t["fit_status"][0]) if "fit_status" in t else None
    return out


def main():
    os.makedirs(f"{H}/results", exist_ok=True)
    L = ["# JES_2024 likelihood scans (combine), v2 card", "",
         "data-only = JES prior removed (JES as POI); with prior = data-only + theta^2. Width = half of the q-1 interval.",
         "A 'with prior' width below 1 means the data constrains JES beyond its prior. '(edge)' = interval hits the scan range [-1, 9].", ""]
    curves = {}
    for ch in ["EE", "MM"]:
        L += [f"## {ch} card", "", "| scan | data-only best | -err | +err | with prior best | -err | +err | q_prior(0) - min |",
              "|---|---|---|---|---|---|---|---|"]
        for tag, d in DESC.items():
            s = load_scan(ch, tag)
            if s is None: continue
            if isinstance(s, str):
                L.append(f"| {d} | scan failed | | | | | | |"); continue
            x, q = s; qp = q + x ** 2
            b, el, eh, qm, elo, ehi = interval(x, q); bp, elp, ehp, qmp, *_ = interval(x, qp)
            q0 = float(np.interp(0.0, x, qp)) - qmp
            e1 = " (edge)" if elo or ehi else ""
            L.append(f"| {d} | **{b:+.2f}** | {el:.2f} | {eh:.2f}{e1} | **{bp:+.2f}** | {elp:.2f} | {ehp:.2f} | {q0:.1f} |")
            curves[(ch, tag)] = (x, q, qp)
        L.append("")
    # FitDiagnostics comparison (baseline vs slope)
    names = ["JES_2024", "MassSlopeDY", "MassSlopeTT", "ResolvedDYReshapeBin2", "ResolvedDYReshapeBin4", "ResolvedDYReshapeBin5",
             "MuonTrig_2024", "OthersNorm_2024", "R_DY_Resolved_2024", "R_TT_Resolved_2024", "R_DY_Boosted_2024"]
    base_fd = {"EE": f"{H}/combine/EE/out/fitDiagnostics.fdtest.root", "MM": f"{H}/combine/MM/out/fitDiagnostics.fd.root"}
    L += ["## FitDiagnostics (b-only, CR data + SR Asimov): baseline vs + MassSlopeDY/TT", "",
          "| param | EE base | EE +slope | MM base | MM +slope |", "|---|---|---|---|---|"]
    R = {("EE", "base"): fitdiag(base_fd["EE"], names), ("EE", "slope"): fitdiag(f"{H}/combine/EE/out/fitDiagnostics.fd.root", names)}
    # MM base fd sits next to MM slope fd with the same tag; the job writes into combine/MM/out for both VARs -> tags differ by VAR? no:
    # both MM jobs use tag 'fd'; the second to finish overwrites. They are distinguished in jobs.txt by running base and slope
    # with different tags below if needed.
    R[("MM", "base")] = fitdiag(f"{H}/combine/MM/out/fitDiagnostics.fdbase.root", names)
    R[("MM", "slope")] = fitdiag(f"{H}/combine/MM/out/fitDiagnostics.fdslope.root", names)
    R[("EE", "slope")] = fitdiag(f"{H}/combine/EE/out/fitDiagnostics.fdslope.root", names) or R[("EE", "slope")]
    for n in names + ["fit_status"]:
        row = []
        for k in [("EE", "base"), ("EE", "slope"), ("MM", "base"), ("MM", "slope")]:
            v = (R.get(k) or {}).get(n)
            row.append("-" if v is None else (str(v) if n == "fit_status" else f"{v[0]:+.2f} ± {v[1]:.2f}"))
        L.append(f"| {n} | " + " | ".join(row) + " |")
    md = "\n".join(L) + "\n"; open(f"{H}/results/scans.md", "w").write(md); print(md)

    for ch in ["EE", "MM"]:
        fig, axs = plt.subplots(1, 2, figsize=(13, 5))
        for (c, tag), (x, q, qp) in curves.items():
            if c != ch: continue
            lw = 2.4 if tag in ("base.full", "slope.full") else 1.2
            ls = "-" if tag.startswith("base.full") or tag.startswith("slope") else "--"
            axs[0].plot(x, q - q.min(), lw=lw, ls=ls, label=DESC[tag]); axs[1].plot(x, qp - qp.min(), lw=lw, ls=ls, label=DESC[tag])
        for ax, t in zip(axs, ["data only (JES prior removed)", "with JES prior (= full fit)"]):
            ax.axhline(1, color="gray", lw=0.8); ax.axhline(4, color="gray", lw=0.5, ls=":"); ax.axvline(0, color="k", lw=0.8)
            ax.set_ylim(0, 15); ax.set_xlim(-1, 9); ax.set_xlabel("JES_2024 (theta)"); ax.set_ylabel("2 dNLL"); ax.set_title(f"{ch} card: {t}")
        axs[1].plot(np.linspace(-1, 9, 100), np.linspace(-1, 9, 100) ** 2, color="k", lw=0.8, ls=":", label="prior only (theta^2)")
        axs[1].legend(fontsize=7, loc="upper left")
        fig.tight_layout(); fig.savefig(f"{H}/results/jes_scan_{ch}.png", dpi=130); plt.close(fig)
    print("wrote", f"{H}/results")


if __name__ == "__main__":
    main()
