#!/usr/bin/env bash
# Real-data CR-only fit of the Top normalisation (spec 8.4): every SR channel masked, r = 0 frozen, R_TT_* floating.
#   bash run_cronly_fit.sh <scenario tag> <EE|MM> <mass point, e.g. WR5000_N2500> [WORKDIR]
set -uo pipefail
TAG=$1; CH=$2; MP=$3; HERE=$(cd "$(dirname "$0")" && pwd); W=${4:-$HERE/work_cronly}/${TAG}_${CH}_${MP}
SCEN=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/combine/scenarios/test/$TAG
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
mkdir -p $W; cd $W
cp $SCEN/datacards/2024/$CH/card_$MP.txt card.txt
sed -i "s#^shapes \(.*\) \(\S*shapes_2024_[^ ]*\.root\) #shapes \1 $SCEN/$(basename $SCEN/shapes_2024_*.root) #" card.txt
BINS=$(awk '$1=="bin"{for(i=2;i<=NF;i++) print $i; exit}' card.txt)
SR=$(echo "$BINS" | grep "SR" | sort -u); CRS=$(echo "$BINS" | grep -v "SR" | sort -u)
SETP="r=0"; FRZ="r"
for b in $SR;  do SETP="$SETP,mask_$b=1"; FRZ="$FRZ,mask_$b"; done
for b in $CRS; do SETP="$SETP,mask_$b=0"; FRZ="$FRZ,mask_$b"; done
echo "masked SR channels: $(echo $SR | tr '\n' ' ')"; echo "fitted CR channels: $(echo $CRS | tr '\n' ' ')"
[ -f ws.root ] || text2workspace.py card.txt -o ws.root --channel-masks > t2w.log 2>&1 || { echo T2W_FAILED; tail -5 t2w.log; exit 1; }
combine -M FitDiagnostics ws.root -n .CRonly --setParameters $SETP --freezeParameters $FRZ \
  --skipSBFit --saveShapes --saveNormalizations --saveWithUncertainties \
  --cminDefaultMinimizerStrategy 1 --cminDefaultMinimizerTolerance 0.1 --cminFallbackAlgo Minuit2,Migrad,0:0.5 --cminFallbackAlgo Minuit2,Migrad,0:1.0 > fit.log 2>&1
echo "fit rc=$?"
python3 - <<'PY'
import ROOT, json
f = ROOT.TFile.Open("fitDiagnostics.CRonly.root"); fb = f.Get("fit_b")
if not fb or not fb.InheritsFrom("RooFitResult"): raise SystemExit("FIT_FAILED: no fit_b in fitDiagnostics.CRonly.root (see fit.log)")
out = {"status": fb.status(), "covQual": fb.covQual(), "minNll": fb.minNll(), "rateParams": {}, "largest_pulls": []}
pars = fb.floatParsFinal(); pre = f.Get("nuisances_prefit")
for i in range(pars.getSize()):
    p = pars.at(i); n = p.GetName()
    if n.startswith(("R_TT", "R_DY")):
        out["rateParams"][n] = {"val": round(p.getVal(), 4), "err": round(p.getError(), 4), "lo": p.getMin(), "hi": p.getMax(),
                                "at_boundary": abs(p.getVal() - p.getMin()) < 1e-3 or abs(p.getVal() - p.getMax()) < 1e-3}
    elif pre and pre.find(n) and not n.startswith("prop_bin"):
        q = pre.find(n); s = q.getError()
        if s > 0: out["largest_pulls"].append((round((p.getVal() - q.getVal()) / s, 2), n, round(p.getError() / s, 2)))
out["largest_pulls"] = sorted(out["largest_pulls"], key=lambda t: -abs(t[0]))[:8]
cor = {}
for a in out["rateParams"]:
    for b in out["rateParams"]:
        if a < b: cor[f"{a}|{b}"] = round(fb.correlation(a, b), 3)
out["rateParam_correlations"] = cor
json.dump(out, open("cronly_result.json", "w"), indent=1); print(json.dumps(out, indent=1))
PY
