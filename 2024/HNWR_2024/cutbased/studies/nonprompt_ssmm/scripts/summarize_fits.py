#!/usr/bin/env python3
"""Table of all Asimov fits: r (MultiDimFit, 68%), fit status, and the nonprompt-model parameters (fit_s)."""
import glob, json, os, sys
base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fit")
suffix = sys.argv[1] if len(sys.argv) > 1 else ""
rows = ["# tag | r  -err +err | fit_s status/covQual | k_Low | tau | lam | N_Low | N_High   (value±postfit err; priors k_Low,tau,lam = 1 ± sigma)"]
for f in sorted(glob.glob(os.path.join(base, "*", "fit_result.json"))):
    tag = os.path.basename(os.path.dirname(f))
    if tag.startswith("_") or (suffix and not tag.endswith(suffix)) or (not suffix and tag.endswith("_QCD")):
        continue
    J = json.load(open(f)); r = J["r_mdf"]
    c, lo, hi = r[0][0], r[1][0], r[2][0]
    fs = J.get("fit_s"); pars = fs.get("pars", {}) if isinstance(fs, dict) else {}
    def p(n):
        return f"{pars[n][0]:.3f}±{pars[n][1]:.3f}" if n in pars else "-"
    st = f"{fs['status']}/{fs['covQual']}" if isinstance(fs, dict) else str(fs)
    rows.append(f"{tag:28s} | {c:7.3f} -{c - lo:.3f} +{hi - c:.3f} | {st:5s} | {p('k_Low')} | {p('tau')} | {p('lam')} | {p('N_Low')} | {p('N_High')}")
print("\n".join(rows))
