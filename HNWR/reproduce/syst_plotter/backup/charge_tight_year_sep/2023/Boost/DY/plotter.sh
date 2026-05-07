#!/usr/bin/env bash
# Boosted DY CR - EE
python EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_mlljj --xmin 800 --xmax 4000 --xlabel "m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_mll_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_dilepton_mass --xmin 0 --xmax 200 --xlabel "m(ll) (GeV)" --rebin 1 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_leading_fatjet_pt_boosted_DY_CR_EE" --ymin 1 --ymax 3e5 --output BoostDYEE_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Leading Fat Jet p_{T} (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_leading_lep_pt_boosted_DY_CR_EE" --ymin 1 --ymax 3e5 --output BoostDYEE_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_subleading_lep_pt_boosted_DY_CR_EE" --ymin 1 --ymax 3e5 --output BoostDYEE_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Subleading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0

python EE.py  --hist "Obj_PU_eta_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_dilepton_eta --xmin -5 --xmax 5 --xlabel "Dilepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_phi_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Dilepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_fatjet_eta_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_fatjet_eta --xmin -2.4 --xmax 2.4 --xlabel "Fat Jet #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_fatjet_phi_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Fat Jet #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_fatjet_SDM_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_fatjet_SDM --xmin 0 --xmax 300 --xlabel "Fat Jet Soft Drop Mass (GeV)" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_mll_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_dilepton_mass --xmin 0 --xmax 200 --xlabel "m(ll) (GeV)" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_WR_pt_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_WR_pt --xmin 0 --xmax 800 --xlabel "WR p_{T} (GeV)" --rebin 5 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_WR_eta_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_WR_eta --xmin -5 --xmax 5 --xlabel "WR #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_WR_phi_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "WR #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_leading_lep_eta_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Leading Lepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_leading_lep_phi_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Leading Lepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_subleading_lep_eta_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Subleading Lepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_subleading_lep_phi_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Lepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_fatjet_lsf3_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Fat Jet LSF3" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_deltaR_leadlep_fatjet_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "#DeltaR(lead lep, fat jet)" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_dphi_leadlep_fatjet_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "#Delta#phi(lead lep, fat jet)" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_pvgood_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_punum --xmin 0 --xmax 80 --xlabel "Number of Pileup Vertices" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_jetnum_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_jetnum --xmin 0 --xmax 5 --xlabel "Number of Jets" --rmin 0.5 --rmax 1.5 --rebin 1 

### Same sign 
python EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_mlljj --xmin 800 --xmax 4000 --xlabel "Same sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_mll_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_dilepton_mass --xmin 0 --xmax 200 --xlabel "Same sign m(ll) (GeV)" --rebin 1 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_leading_fatjet_pt_boosted_DY_CR_EE_SS" --ymin 1 --ymax 3e3 --output BoostDYEE_SS_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Same sign Leading Fat Jet p_{T} (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_leading_lep_pt_boosted_DY_CR_EE_SS" --ymin 1 --ymax 3e3 --output BoostDYEE_SS_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Same sign Leading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_subleading_lep_pt_boosted_DY_CR_EE_SS" --ymin 1 --ymax 3e3 --output BoostDYEE_SS_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Same sign Subleading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0

python EE.py  --hist "Obj_PU_eta_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Same sign Dilepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_phi_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Dilepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_fatjet_eta_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_fatjet_eta --xmin -2.4 --xmax 2.4 --xlabel "Same sign Fat Jet #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_fatjet_phi_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Fat Jet #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_fatjet_SDM_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_fatjet_SDM --xmin 0 --xmax 300 --xlabel "Same sign Fat Jet Soft Drop Mass (GeV)" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_mll_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_dilepton_mass --xmin 0 --xmax 200 --xlabel "Same sign m(ll) (GeV)" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_WR_pt_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_WR_pt --xmin 0 --xmax 800 --xlabel "Same sign WR p_{T} (GeV)" --rebin 5 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_WR_eta_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_WR_eta --xmin -5 --xmax 5 --xlabel "Same sign WR #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_WR_phi_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign WR #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_leading_lep_eta_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Leading Lepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_leading_lep_phi_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Leading Lepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_subleading_lep_eta_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Subleading Lepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_subleading_lep_phi_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Subleading Lepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_fatjet_lsf3_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Same sign Fat Jet LSF3" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_deltaR_leadlep_fatjet_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "Same sign #DeltaR(lead lep, fat jet)" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_dphi_leadlep_fatjet_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "Same sign #Delta#phi(lead lep, fat jet)" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_pvgood_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_punum --xmin 0 --xmax 80 --xlabel "Same sign Number of Pileup Vertices" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_jetnum_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_jetnum --xmin 0 --xmax 5 --xlabel "Same sign Number of Jets" --rmin 0.5 --rmax 1.5 --rebin 1 


### Other Sign 
python EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_mlljj --xmin 800 --xmax 4000 --xlabel "Other sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_mll_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_dilepton_mass --xmin 0 --xmax 200 --xlabel "Other sign m(ll) (GeV)" --rebin 1 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_leading_fatjet_pt_boosted_DY_CR_EE_OS" --ymin 1 --ymax 3e5 --output BoostDYEE_OS_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Other sign Leading Fat Jet p_{T} (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_leading_lep_pt_boosted_DY_CR_EE_OS" --ymin 1 --ymax 3e5 --output BoostDYEE_OS_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Other sign Leading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_subleading_lep_pt_boosted_DY_CR_EE_OS" --ymin 1 --ymax 3e5 --output BoostDYEE_OS_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Other sign Subleading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0

python EE.py  --hist "Obj_PU_eta_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Other sign Dilepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_phi_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Dilepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_fatjet_eta_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_fatjet_eta --xmin -2.4 --xmax 2.4 --xlabel "Other sign Fat Jet #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_fatjet_phi_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Fat Jet #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_fatjet_SDM_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_fatjet_SDM --xmin 0 --xmax 300 --xlabel "Other sign Fat Jet Soft Drop Mass (GeV)" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_mll_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_dilepton_mass --xmin 0 --xmax 200 --xlabel "Other sign m(ll) (GeV)" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_WR_pt_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_WR_pt --xmin 0 --xmax 800 --xlabel "Other sign WR p_{T} (GeV)" --rebin 5 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_WR_eta_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_WR_eta --xmin -5 --xmax 5 --xlabel "Other sign WR #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_WR_phi_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign WR #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_leading_lep_eta_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Leading Lepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_leading_lep_phi_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Leading Lepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_subleading_lep_eta_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Subleading Lepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_subleading_lep_phi_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Subleading Lepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_fatjet_lsf3_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Other sign Fat Jet LSF3" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_deltaR_leadlep_fatjet_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "Other sign #DeltaR(lead lep, fat jet)" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_dphi_leadlep_fatjet_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "Other sign #Delta#phi(lead lep, fat jet)" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_pvgood_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_punum --xmin 0 --xmax 80 --xlabel "Other sign Number of Pileup Vertices" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py  --hist "Obj_PU_jetnum_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e6 --output BoostDYEE_OS_jetnum --xmin 0 --xmax 5 --xlabel "Other sign Number of Jets" --rmin 0.5 --rmax 1.5 --rebin 1 



# Boosted DY CR - MM
python MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_mlljj --xmin 800 --xmax 4000 --xlabel "m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_mll_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_dilepton_mass --xmin 0 --xmax 200 --xlabel "m(ll) (GeV)" --rebin 1 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_leading_fatjet_pt_boosted_DY_CR_MM" --ymin 1 --ymax 3e5 --output BoostDYMM_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Leading Fat Jet p_{T} (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_leading_lep_pt_boosted_DY_CR_MM" --ymin 1 --ymax 3e5 --output BoostDYMM_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_subleading_lep_pt_boosted_DY_CR_MM" --ymin 1 --ymax 3e5 --output BoostDYMM_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Subleading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0

python MM.py  --hist "Obj_PU_eta_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_dilepton_eta --xmin -5 --xmax 5 --xlabel "Dilepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_phi_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Dilepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_fatjet_eta_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_fatjet_eta --xmin -2.4 --xmax 2.4 --xlabel "Fat Jet #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_fatjet_phi_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Fat Jet #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_fatjet_SDM_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_fatjet_SDM --xmin 0 --xmax 300 --xlabel "Fat Jet Soft Drop Mass (GeV)" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_mll_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_dilepton_mass --xmin 0 --xmax 200 --xlabel "m(ll) (GeV)" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_WR_pt_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_WR_pt --xmin 0 --xmax 800 --xlabel "WR p_{T} (GeV)" --rebin 5 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_WR_eta_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_WR_eta --xmin -5 --xmax 5 --xlabel "WR #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_WR_phi_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "WR #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_leading_lep_eta_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Leading Lepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_leading_lep_phi_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Leading Lepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_subleading_lep_eta_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Subleading Lepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_subleading_lep_phi_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Lepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_fatjet_lsf3_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Fat Jet LSF3" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_deltaR_leadlep_fatjet_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "#DeltaR(lead lep, fat jet)" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_dphi_leadlep_fatjet_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "#Delta#phi(lead lep, fat jet)" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_pvgood_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_punum --xmin 0 --xmax 80 --xlabel "Number of Pileup Vertices" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_jetnum_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_jetnum --xmin 0 --xmax 5 --xlabel "Number of Jets" --rmin 0.5 --rmax 1.5 --rebin 1

### Same sign 
python MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_mlljj --xmin 800 --xmax 4000 --xlabel "Same sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_mll_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_dilepton_mass --xmin 0 --xmax 200 --xlabel "Same sign m(ll) (GeV)" --rebin 1 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_leading_fatjet_pt_boosted_DY_CR_MM_SS" --ymin 1 --ymax 3e3 --output BoostDYMM_SS_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Same sign Leading Fat Jet p_{T} (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_leading_lep_pt_boosted_DY_CR_MM_SS" --ymin 1 --ymax 3e3 --output BoostDYMM_SS_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Same sign Leading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_subleading_lep_pt_boosted_DY_CR_MM_SS" --ymin 1 --ymax 3e3 --output BoostDYMM_SS_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Same sign Subleading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0

python MM.py  --hist "Obj_PU_eta_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Same sign Dilepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_phi_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Dilepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_fatjet_eta_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_fatjet_eta --xmin -2.4 --xmax 2.4 --xlabel "Same sign Fat Jet #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_fatjet_phi_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Fat Jet #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_fatjet_SDM_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_fatjet_SDM --xmin 0 --xmax 300 --xlabel "Same sign Fat Jet Soft Drop Mass (GeV)" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_mll_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_dilepton_mass --xmin 0 --xmax 200 --xlabel "Same sign m(ll) (GeV)" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_WR_pt_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_WR_pt --xmin 0 --xmax 800 --xlabel "Same sign WR p_{T} (GeV)" --rebin 5 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_WR_eta_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_WR_eta --xmin -5 --xmax 5 --xlabel "Same sign WR #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_WR_phi_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign WR #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_leading_lep_eta_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Leading Lepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_leading_lep_phi_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Leading Lepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_subleading_lep_eta_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Subleading Lepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_subleading_lep_phi_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Subleading Lepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_fatjet_lsf3_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Same sign Fat Jet LSF3" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_deltaR_leadlep_fatjet_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "Same sign #DeltaR(lead lep, fat jet)" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_dphi_leadlep_fatjet_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "Same sign #Delta#phi(lead lep, fat jet)" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_pvgood_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_punum --xmin 0 --xmax 80 --xlabel "Same sign Number of Pileup Vertices" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_jetnum_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_jetnum --xmin 0 --xmax 5 --xlabel "Same sign Number of Jets" --rmin 0.5 --rmax 1.5 --rebin 1


### Other sign

python MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_mlljj --xmin 800 --xmax 4000 --xlabel "Other sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_mll_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_dilepton_mass --xmin 0 --xmax 200 --xlabel "Other sign m(ll) (GeV)" --rebin 1 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_leading_fatjet_pt_boosted_DY_CR_MM_OS" --ymin 1 --ymax 3e5 --output BoostDYMM_OS_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Other sign Leading Fat Jet p_{T} (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_leading_lep_pt_boosted_DY_CR_MM_OS" --ymin 1 --ymax 3e5 --output BoostDYMM_OS_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Other sign Leading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_subleading_lep_pt_boosted_DY_CR_MM_OS" --ymin 1 --ymax 3e5 --output BoostDYMM_OS_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Other sign Subleading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0

python MM.py  --hist "Obj_PU_eta_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Other sign Dilepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_phi_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Dilepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_fatjet_eta_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_fatjet_eta --xmin -2.4 --xmax 2.4 --xlabel "Other sign Fat Jet #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_fatjet_phi_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Fat Jet #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_fatjet_SDM_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_fatjet_SDM --xmin 0 --xmax 300 --xlabel "Other sign Fat Jet Soft Drop Mass (GeV)" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_mll_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_dilepton_mass --xmin 0 --xmax 200 --xlabel "Other sign m(ll) (GeV)" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_WR_pt_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_WR_pt --xmin 0 --xmax 800 --xlabel "Other sign WR p_{T} (GeV)" --rebin 5 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_WR_eta_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_WR_eta --xmin -5 --xmax 5 --xlabel "Other sign WR #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_WR_phi_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign WR #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_leading_lep_eta_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Leading Lepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_leading_lep_phi_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Leading Lepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_subleading_lep_eta_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Subleading Lepton #eta" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_subleading_lep_phi_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Subleading Lepton #phi" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_fatjet_lsf3_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Other sign Fat Jet LSF3" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_deltaR_leadlep_fatjet_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "Other sign #DeltaR(lead lep, fat jet)" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_dphi_leadlep_fatjet_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "Other sign #Delta#phi(lead lep, fat jet)" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_pvgood_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_punum --xmin 0 --xmax 80 --xlabel "Other sign Number of Pileup Vertices" --rebin 2 --rmin 0.5 --rmax 1.5
python MM.py  --hist "Obj_PU_jetnum_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e6 --output BoostDYMM_OS_jetnum --xmin 0 --xmax 5 --xlabel "Other sign Number of Jets" --rmin 0.5 --rmax 1.5 --rebin 1
