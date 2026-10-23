source /cvmfs/cms.cern.ch/cmsset_default.sh; cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
P=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/studies/pull_plot; cd $P/combine/EE/out
W=$P/combine/EE/base/ws.root
BINS=$(awk '$1=="bin"{for(i=2;i<=NF;i++) print $i; exit}' $P/combine/EE/base/card.txt)
SP="r=0"; FR="r"; for b in $BINS; do SP="$SP,mask_$b=0"; FR="$FR,mask_$b"; done
C="--cminDefaultMinimizerStrategy 1 --cminDefaultMinimizerTolerance 0.1 --cminFallbackAlgo Minuit2,Migrad,0:0.5"
for start in 0 2.9 5.5; do
  combine -M MultiDimFit $W -n .chk$start --algo none --redefineSignalPOIs JES_2024 -P JES_2024 --setParameterRanges JES_2024=-1,6 --setParameters $SP,JES_2024=$start --freezeParameters $FR $C --saveNLL > chk_$start.log 2>&1
  python3 -c "
import ROOT; f=ROOT.TFile('higgsCombine.chk$start.MultiDimFit.mH120.root'); t=f.Get('limit'); t.GetEntry(0); print('start $start -> JES', round(t.JES_2024,3), 'nll', t.nll, t.nll0 if hasattr(t,'nll0') else '')"
done
for jes in 2.9 5.5; do
  combine -M MultiDimFit $W -n .fix$jes --algo none --setParameters $SP,JES_2024=$jes --freezeParameters $FR,JES_2024 $C --saveNLL > fix_$jes.log 2>&1
  python3 -c "
import ROOT; f=ROOT.TFile('higgsCombine.fix$jes.MultiDimFit.mH120.root'); t=f.Get('limit'); t.GetEntry(0); print('JES fixed $jes: nll', t.nll)"
done
