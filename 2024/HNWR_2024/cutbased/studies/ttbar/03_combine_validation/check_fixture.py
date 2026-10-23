#!/usr/bin/env python3
"""Read the FitDiagnostics outputs of run_fixture.sh and apply the pass criteria of spec 10.1(7), 10.2, 10.3."""
import sys, json, ROOT
ROOT.gROOT.SetBatch(True)
d = sys.argv[1]; res = {}; ok = True
for var in ("A", "B"):
    f = ROOT.TFile.Open(f"{d}/fitDiagnostics.CRonly_{var}.root"); fb = f.Get("fit_b")
    b = fb.floatParsFinal().find("beta_top"); top = f.Get("shapes_fit_b/SR_EE/Top")
    res[var] = {"beta": b.getVal(), "beta_err": b.getError(), "status": fb.status(), "covQual": fb.covQual(),
                "SR_Top_postfit": [top.GetBinContent(i) for i in (1, 2, 3)]}
    f.Close()
res["checks"] = {
    "beta_recovered_1.2": abs(res["A"]["beta"] - 1.2) < 1e-3,
    "SR_Top_48_24_12": all(abs(x - y) < 0.05 for x, y in zip(res["A"]["SR_Top_postfit"], [48, 24, 12])),
    "masked_SR_obs_irrelevant": abs(res["A"]["beta"] - res["B"]["beta"]) < 1e-6 and abs(res["A"]["beta_err"] - res["B"]["beta_err"]) < 1e-6,
    "naive_stat_err": (1300 ** 0.5) / 1000.0,
}
# 10.1(7): beta 1 -> 1.1 scales every linked Top expectation by 10% and nothing else
f = ROOT.TFile.Open(f"{d}/ws_A.root"); w = f.Get("w")
FUNCS = [f.GetName() for f in w.allFunctions() if f.GetName().startswith("n_exp_")]
FINAL = {}                        # per (bin, proc): prefer the n_exp_final_* product (carries the rateParam) over n_exp_*
for n in FUNCS:
    key = n.replace("n_exp_final_", "").replace("n_exp_", "")
    if key not in FINAL or n.startswith("n_exp_final_"): FINAL[key] = n
def yields():
    return {n: w.function(n).getVal() for n in FINAL.values()}
w.var("beta_top").setVal(1.0); y0 = yields(); w.var("beta_top").setVal(1.1); y1 = yields()
res["scaling_beta_1_to_1.1"] = {n: y1[n] / y0[n] for n in y0}
res["checks"]["top_scaled_10pct_only"] = all(abs(r - (1.1 if n.endswith("proc_Top") else 1.0)) < 1e-9 for n, r in res["scaling_beta_1_to_1.1"].items()) and sum(n.endswith("proc_Top") for n in y0) == 2
res["workspace"] = {"mask_vars": [v for v in ("mask_CR_EM", "mask_SR_EE") if w.var(v)], "n_beta_vars": sum(1 for v in w.allVars() if v.GetName().startswith("beta_top"))}
res["PASS"] = all(v for k, v in res["checks"].items() if isinstance(v, bool)) and len(res["workspace"]["mask_vars"]) == 2 and res["workspace"]["n_beta_vars"] == 1
json.dump(res, open(f"{d}/fixture_result.json", "w"), indent=1); print(json.dumps(res, indent=1))
