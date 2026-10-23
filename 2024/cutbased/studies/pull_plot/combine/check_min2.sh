source /cvmfs/cms.cern.ch/cmsset_default.sh; cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
P=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/studies/pull_plot; cd $P/combine/EE/out
W=$P/combine/EE/base/ws.root
BINS=$(awk '$1=="bin"{for(i=2;i<=NF;i++) print $i; exit}' $P/combine/EE/base/card.txt)
SP="r=0"; FR="r"; for b in $BINS; do SP="$SP,mask_$b=0"; FR="$FR,mask_$b"; done
C="--cminDefaultMinimizerStrategy 1 --cminDefaultMinimizerTolerance 0.1 --cminFallbackAlgo Minuit2,Migrad,0:0.5 --cminFallbackAlgo Minuit2,Migrad,0:1.0 --X-rtd MINIMIZER_analytic"
for s in 0 5.5; do
  combine -M FitDiagnostics $W -n .start$s --setParameters $SP,JES_2024=$s --setParameterRanges JES_2024=-1,8 --freezeParameters $FR --skipSBFit $C > fd_start$s.log 2>&1
done
python3 - <<'PY'
import ROOT
for s in ["0","5.5"]:
    f=ROOT.TFile(f"fitDiagnostics.start{s}.root"); r=f.Get("fit_b")
    print("start",s,"status",r.status(),"covQual",r.covQual(),"JES",round(r.floatParsFinal().find("JES_2024").getVal(),3),"minNll",r.minNll())
PY
# absolute NLL comparison: evaluate NLL of the same model at the two best-fit points with a fixed-parameter MultiDimFit (nothing floats but r frozen)
PY2=$(cat <<'PY'
import ROOT,sys
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
f=ROOT.TFile(sys.argv[1]); w=f.Get("w"); mc=w.obj("ModelConfig")
data=w.data("data_obs"); pdf=mc.GetPdf()
for s in ["0","5.5"]:
    fd=ROOT.TFile(f"fitDiagnostics.start{s}.root"); r=fd.Get("fit_b")
    allv=w.allVars(); 
    for a in [r.floatParsFinal(), r.constPars()]:
        for i in range(a.getSize()):
            v=a.at(i); t=allv.find(v.GetName())
            if t: t.setVal(v.getVal())
    nll=pdf.createNLL(data, ROOT.RooFit.Constrain(mc.GetNuisanceParameters()), ROOT.RooFit.Offset(False))
    print("start",s,"absolute NLL",nll.getVal(), "JES", allv.find("JES_2024").getVal())
PY
)
python3 -c "$PY2" $W 2>&1 | grep -v "^\[#" | tail -3
