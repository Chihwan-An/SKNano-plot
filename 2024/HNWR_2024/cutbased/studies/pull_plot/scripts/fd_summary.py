#!/usr/bin/env python3
"""FitDiagnostics fit_b summary: baseline vs +MassSlopeDY/TT, EE and MM cards. Needs PyROOT (run in CMSSW).
Writes results/fitdiag_slope.md: selected params (value +- Hesse error), every constrained nuisance with |pull|>1 or
error<0.7, and correlations of JES_2024 with the slope / DY-R / rateParams."""
import ROOT, os
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = {("EE", "base"): f"{H}/combine/EE/out/fitDiagnostics.fdtest.root", ("EE", "slope"): f"{H}/combine/EE/out/fitDiagnostics.fdslope.root",
     ("MM", "base"): f"{H}/combine/MM/out/fitDiagnostics.fdbase.root", ("MM", "slope"): f"{H}/combine/MM/out/fitDiagnostics.fdslope.root"}
SEL = ["JES_2024", "MassSlopeDY", "MassSlopeTT", "ResolvedDYReshapeBin1", "ResolvedDYReshapeBin2", "ResolvedDYReshapeBin3",
       "ResolvedDYReshapeBin4", "ResolvedDYReshapeBin5", "ResolvedDYReshapeBin6", "MuonTrig_2024", "OthersNorm_2024",
       "Pileup_2024", "JER_2024", "R_DY_Resolved_2024", "R_TT_Resolved_2024", "R_DY_Boosted_2024", "R_TT_Boosted_EE_2024"]
R = {}
for k, p in F.items():
    f = ROOT.TFile.Open(p); r = f.Get("fit_b"); R[k] = (r, f)
L = ["# FitDiagnostics fit_b: baseline vs + MassSlopeDY / MassSlopeTT (K = 10 % tilt per sigma, 800 GeV -> 3 TeV)", "",
     "status / covQual: " + ", ".join(f"{k[0]} {k[1]} {v[0].status()}/{v[0].covQual()}" for k, v in R.items()), "",
     "| param | EE base | EE +slope | MM base | MM +slope |", "|---|---|---|---|---|"]
for n in SEL:
    row = []
    for k in [("EE", "base"), ("EE", "slope"), ("MM", "base"), ("MM", "slope")]:
        v = R[k][0].floatParsFinal().find(n)
        row.append("-" if not v else f"{v.getVal():+.2f} ± {v.getError():.2f}")
    L.append(f"| {n} | " + " | ".join(row) + " |")
for k in [("EE", "slope"), ("MM", "slope"), ("EE", "base"), ("MM", "base")]:
    r = R[k][0]; fl = r.floatParsFinal()
    bad = []
    for i in range(fl.getSize()):
        v = fl.at(i); n = v.GetName()
        if n.startswith(("R_", "prop_bin", "r")) and not n.startswith("ResolvedDY"): continue
        if abs(v.getVal()) > 1 or v.getError() < 0.7: bad.append(f"{n} {v.getVal():+.2f} ({v.getError():.2f})")
    L += ["", f"{k[0]} {k[1]}: |pull|>1 or error<0.7 -> " + (", ".join(bad) or "none")]
L += ["", "## correlations with JES_2024", "", "| param | EE base | EE +slope | MM base | MM +slope |", "|---|---|---|---|---|"]
for n in ["MassSlopeDY", "MassSlopeTT", "ResolvedDYReshapeBin4", "ResolvedDYReshapeBin2", "MuonTrig_2024", "R_DY_Resolved_2024", "R_TT_Resolved_2024"]:
    row = []
    for k in [("EE", "base"), ("EE", "slope"), ("MM", "base"), ("MM", "slope")]:
        r = R[k][0]
        try: row.append(f"{r.correlation('JES_2024', n):+.2f}" if r.floatParsFinal().find(n) else "-")
        except Exception: row.append("-")
    L.append(f"| {n} | " + " | ".join(row) + " |")
open(f"{H}/results/fitdiag_slope.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
