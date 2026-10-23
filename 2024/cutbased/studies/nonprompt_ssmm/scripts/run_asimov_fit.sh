#!/usr/bin/env bash
# Run on tamsa2 (native EL9 combine). args: <card dir> [extra combine opts]
# Fits the Asimov data_obs written by make_asimov_cards.py (never real data):
#   MultiDimFit r (+ the 68% interval), FitDiagnostics s+b for pulls/constraints.
set -uo pipefail
D=$1; shift
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
cd $D
text2workspace.py card.txt -o ws.root > t2w.log 2>&1 || { echo T2W_FAILED; tail -20 t2w.log; exit 1; }
OPT="--cminDefaultMinimizerStrategy 1 --cminDefaultMinimizerTolerance 0.01 --rMin -5 --rMax 10"
combine -M MultiDimFit ws.root -n .r --algo singles $OPT "$@" > mdf.log 2>&1; echo "mdf rc=$?"
combine -M FitDiagnostics ws.root -n .fd $OPT --saveWithUncertainties --ignoreCovWarning "$@" > fd.log 2>&1; echo "fd rc=$?"
python3 - <<'PY'
import ROOT, json
ROOT.gROOT.SetBatch(True)
out = {}
f = ROOT.TFile.Open("higgsCombine.r.MultiDimFit.mH120.root")
t = f.Get("limit")
vals = [(e.r, e.quantileExpected) for e in t]
out["r_mdf"] = vals
fd = ROOT.TFile.Open("fitDiagnostics.fd.root")
for fitname in ("fit_s", "fit_b"):
    fr = fd.Get(fitname)
    if not fr or not fr.InheritsFrom("RooFitResult"):
        out[fitname] = "missing"; continue
    pars = fr.floatParsFinal()
    out[fitname] = {"status": fr.status(), "covQual": fr.covQual(),
                    "pars": {pars.at(i).GetName(): [pars.at(i).getVal(), pars.at(i).getError()]
                             for i in range(pars.getSize()) if not pars.at(i).GetName().startswith("prop_bin")}}
json.dump(out, open("fit_result.json", "w"), indent=1)
print(json.dumps({k: (v if k == "r_mdf" else {kk: vv for kk, vv in v.items() if kk != "pars"} if isinstance(v, dict) else v) for k, v in out.items()}))
PY
