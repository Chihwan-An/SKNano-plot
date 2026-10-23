set -uo pipefail
source /cvmfs/cms.cern.ch/cmsset_default.sh; cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src; eval $(scramv1 runtime -sh)
cd /data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test
python3 - <<'PY'
import ROOT
f=ROOT.TFile.Open("cbv15dc/shapes_2024_dc_cr_fixstream.root")
for ch in ["rFlvCR","bFlvEMuCR","bFlvMuECR","rDYMuMuCR_OS","bDYEECR"]:
    d=f.Get(ch); y={n:d.Get(n).Integral() for n in ["data_obs","TT","DYJets","Nonprompt","Others"]}
    print("FIXED",ch,{k:round(v,1) for k,v in y.items()})
PY
E=3132
python3 scripts/cbv15_dc_cards.py --shapes cbv15dc/shapes_2024_dc.root --shapes-mm cbv15dc/shapes_2024_dc_mm.root --shapes-cr cbv15dc/shapes_2024_dc_cr.root --ddss cbv15dc/ddss_ee_2024_an2rf_$E.root --edges-json cbv15dc/edges_an2_$E.json --shapes-override cbv15dc/shapes_2024_dc_cr_fixstream.root --tag cbv15_an2_ref_fixstream 2>&1 | grep -v "^$" | tail -6
echo BUILD_DONE
