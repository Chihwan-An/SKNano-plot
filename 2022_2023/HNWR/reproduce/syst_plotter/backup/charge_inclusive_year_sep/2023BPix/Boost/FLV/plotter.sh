#!/usr/bin/env bash
# Boosted Flavor CR - EMJ (electron + muon-jet), using EE.py 

python EE.py  --hist "Obj_PU_leading_fatjet_pt_boosted_e_mujet_Flavor_CR" --ymin 1e-1 --ymax 3e3 --output BoostFLVEMJ_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Leading Fat Jet p_{T} (GeV)" --bins "200,400,600,800,1000,2000" --rmin 0 --rmax 2.5

python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_Fatjet_SDMass" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_fatjet_SDMass --xmin 0 --xmax 200 --xlabel "Fat Jet Soft Drop Mass (GeV)" --rebin 5 --rmin 0 --rmax 2.5


python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_LeadingLepEta" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Leading Lepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SubLeadingLepEta" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Subleading Lepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_Fatjet_Eta" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_fatjet_eta --xmin -2.5 --xmax 2.5 --xlabel "Fat Jet #eta" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_Fatjet_Phi" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Fat Jet #phi" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_DeltaR_LeadLep_Fatjet" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "#DeltaR(lead lep, fat jet)" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_LeadLep_LSF" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_leadlep_lsf --xmin 0 --xmax 1 --xlabel "Lead Lep LSF" --rebin 5 --rmin 0 --rmax 2.5
#python EE.py  --hist "Obj_PU_Boosted_Flavor_CR e_mujet_mll" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_mll --xmin 0 --xmax 1000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.5

python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_WRpt" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_WR_pt --xmin 0 --xmax 1000 --xlabel "WR p_{T} (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_mass" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_dilepton_mass --xmin 0 --xmax 2000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_eta" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_dilepton_eta --xmin -5 --xmax 5 --xlabel "Dilepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_phi" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Dilepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_WR_eta" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_WR_eta --xmin -5 --xmax 5 --xlabel "WR #eta" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_WR_phi" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "WR #phi" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_LeadingLepPhi" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Leading Lepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SubLeadingLepPhi" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Lepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_Fatjet_lsf3" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Fat Jet LSF3" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_dphi_leadlep_fatjet" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "#Delta#phi(lead lep, fat jet)" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_boosted_Flavor_CR_e_mujet_pvgood" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_punum --xmin 0 --xmax 80 --xlabel "Number of Pileup Vertices" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_jetnum" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_jetnum --xmin 0 --xmax 5 --xlabel "Number of Jets" --rmin 0 --rmax 2.5

python EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_e_mujet_Flavor_CR" --ymin 1 --ymax 2e3 --output BoostFLVEMJ_mlljj --xmin 800 --xmax 4000 --xlabel "m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_LeadingLepPt" --ymin 1 --ymax 1e6 --output BoostFLVEMJ_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)" --bins "50,90,130,170,210,250,290,310,350,390,430,470,510,550,590,630,670,710,750,790,830,870,910,950,1000,2000" --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SubLeadingLepPt" --ymin 1 --ymax 1e6 --output BoostFLVEMJ_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Subleading Lepton p_{T} (GeV)" --bins "50,70,90,110,130,150,170,190,210,230,250,270,290,310,330,350,370,390,410,430,450,470,490,500" --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_pt(ll)_boosted_e_mujet_Flavor_CR" --ymin 1 --ymax 1e5 --output BoostFLVEMJ_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Dilepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_Fatjet_pt" --ymin 1 --ymax 1e5 --output BoostFLVEMJ_fatjet_pt --xmin 0 --xmax 1000 --xlabel "Fat Jet p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0



### Same sign 
python EE.py  --hist "Obj_PU_leading_fatjet_pt_boosted_e_mujet_SS_Flavor_CR" --ymin 1e-1 --ymax 3e3 --output BoostFLVEMJ_SS_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Same sign Leading Fat Jet p_{T} (GeV)" --bins "200,400,600,800,1000,2000" --rmin 0 --rmax 2.5

python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_Fatjet_SDMass" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_fatjet_SDMass --xmin 0 --xmax 200 --xlabel "Same sign Fat Jet Soft Drop Mass (GeV)" --rebin 5 --rmin 0 --rmax 2.5


python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_LeadingLepEta" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Leading Lepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_SubLeadingLepEta" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Subleading Lepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_Fatjet_Eta" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_fatjet_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Fat Jet #eta" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_Fatjet_Phi" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Fat Jet #phi" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_DeltaR_LeadLep_Fatjet" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "Same sign #DeltaR(lead lep, fat jet)" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_LeadLep_LSF" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_leadlep_lsf --xmin 0 --xmax 1 --xlabel "Same sign Lead Lep LSF" --rebin 5 --rmin 0 --rmax 2.5
#python EE.py  --hist "Obj_PU_Boosted_Flavor_CR e_mujet_SS_mll" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_mll --xmin 0 --xmax 1000 --xlabel "Same sign m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.5

python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_WRpt" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_WR_pt --xmin 0 --xmax 1000 --xlabel "Same sign WR p_{T} (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_mass" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_dilepton_mass --xmin 0 --xmax 2000 --xlabel "Same sign m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_eta" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Same sign Dilepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_phi" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Dilepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_WR_eta" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_WR_eta --xmin -5 --xmax 5 --xlabel "Same sign WR #eta" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_WR_phi" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign WR #phi" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_LeadingLepPhi" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Leading Lepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_SubLeadingLepPhi" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Subleading Lepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_Fatjet_lsf3" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Same sign Fat Jet LSF3" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_dphi_leadlep_fatjet" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "Same sign #Delta#phi(lead lep, fat jet)" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_boosted_Flavor_CR_e_mujet_SS_pvgood" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_punum --xmin 0 --xmax 80 --xlabel "Same sign Number of Pileup Vertices" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_jetnum" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_SS_jetnum --xmin 0 --xmax 5 --xlabel "Same sign Number of Jets" --rmin 0 --rmax 2.5

python EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_e_mujet_SS_Flavor_CR" --ymin 1 --ymax 2e3 --output BoostFLVEMJ_SS_mlljj --xmin 800 --xmax 4000 --xlabel "Same sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_LeadingLepPt" --ymin 1 --ymax 1e6 --output BoostFLVEMJ_SS_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Same sign Leading Lepton p_{T} (GeV)" --bins "50,90,130,170,210,250,290,310,350,390,430,470,510,550,590,630,670,710,750,790,830,870,910,950,1000,2000" --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_SubLeadingLepPt" --ymin 1 --ymax 1e6 --output BoostFLVEMJ_SS_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Same sign Subleading Lepton p_{T} (GeV)" --bins "50,70,90,110,130,150,170,190,210,230,250,270,290,310,330,350,370,390,410,430,450,470,490,500" --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_pt(ll)_boosted_e_mujet_SS_Flavor_CR" --ymin 1 --ymax 1e3 --output BoostFLVEMJ_SS_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Same sign Dilepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_SS_Fatjet_pt" --ymin 1 --ymax 1e5 --output BoostFLVEMJ_SS_fatjet_pt --xmin 0 --xmax 1000 --xlabel "Same sign Fat Jet p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0



### Other sign 
python EE.py  --hist "Obj_PU_leading_fatjet_pt_boosted_e_mujet_OS_Flavor_CR" --ymin 1e-1 --ymax 3e3 --output BoostFLVEMJ_OS_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Leading Fat Jet p_{T} (GeV)" --bins "200,400,600,800,1000,2000" --rmin 0 --rmax 2.5

python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_Fatjet_SDMass" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_fatjet_SDMass --xmin 0 --xmax 200 --xlabel "Other sign Fat Jet Soft Drop Mass (GeV)" --rebin 5 --rmin 0 --rmax 2.5


python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_LeadingLepEta" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Leading Lepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_SubLeadingLepEta" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Subleading Lepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_Fatjet_Eta" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_fatjet_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Fat Jet #eta" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_Fatjet_Phi" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Fat Jet #phi" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_DeltaR_LeadLep_Fatjet" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "Other sign #DeltaR(lead lep, fat jet)" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_LeadLep_LSF" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_leadlep_lsf --xmin 0 --xmax 1 --xlabel "Other sign Lead Lep LSF" --rebin 5 --rmin 0 --rmax 2.5
#python EE.py  --hist "Obj_PU_Boosted_Flavor_CR e_mujet_OS_mll" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_mll --xmin 0 --xmax 1000 --xlabel "Other sign m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.5

python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_WRpt" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_WR_pt --xmin 0 --xmax 1000 --xlabel "Other sign WR p_{T} (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_mass" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_dilepton_mass --xmin 0 --xmax 2000 --xlabel "Other sign m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_eta" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Other sign Dilepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_phi" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Dilepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_WR_eta" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_WR_eta --xmin -5 --xmax 5 --xlabel "Other sign WR #eta" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_WR_phi" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign WR #phi" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_LeadingLepPhi" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Leading Lepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_SubLeadingLepPhi" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Subleading Lepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_Fatjet_lsf3" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Other sign Fat Jet LSF3" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_dphi_leadlep_fatjet" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "Other sign #Delta#phi(lead lep, fat jet)" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_boosted_Flavor_CR_e_mujet_OS_pvgood" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_punum --xmin 0 --xmax 80 --xlabel "Other sign Number of Pileup Vertices" --rebin 5 --rmin 0 --rmax 2.5
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_jetnum" --ymin 1e-1 --ymax 1e5 --output BoostFLVEMJ_OS_jetnum --xmin 0 --xmax 5 --xlabel "Other sign Number of Jets" --rmin 0 --rmax 2.5

python EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_e_mujet_OS_Flavor_CR" --ymin 1 --ymax 2e3 --output BoostFLVEMJ_OS_mlljj --xmin 800 --xmax 4000 --xlabel "Other sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_LeadingLepPt" --ymin 1 --ymax 1e6 --output BoostFLVEMJ_OS_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Other sign Leading Lepton p_{T} (GeV)" --bins "50,90,130,170,210,250,290,310,350,390,430,470,510,550,590,630,670,710,750,790,830,870,910,950,1000,2000" --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_SubLeadingLepPt" --ymin 1 --ymax 1e6 --output BoostFLVEMJ_OS_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Other sign Subleading Lepton p_{T} (GeV)" --bins "50,70,90,110,130,150,170,190,210,230,250,270,290,310,330,350,370,390,410,430,450,470,490,500" --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_pt(ll)_boosted_e_mujet_OS_Flavor_CR" --ymin 1 --ymax 1e5 --output BoostFLVEMJ_OS_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Other sign Dilepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python EE.py  --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_OS_Fatjet_pt" --ymin 1 --ymax 1e5 --output BoostFLVEMJ_OS_fatjet_pt --xmin 0 --xmax 1000 --xlabel "Other sign Fat Jet p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0




# Boosted Flavor CR - MEJ (muon + electron-jets), using MM.py 

python MM.py  --hist "Obj_PU_leading_fatjet_pt_boosted_mu_ejets_Flavor_CR" --ymin 1e-1 --ymax 3e3 --output BoostFLVMEJ_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Leading Fat Jet p_{T} (GeV)" --bins "200,400,600,800,1000,2000" --rmin 0 --rmax 2.5

python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_Fatjet_SDMass" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_fatjet_SDMass --xmin 0 --xmax 200 --xlabel "Fat Jet Soft Drop Mass (GeV)" --rebin 5 --rmin 0 --rmax 2.5


python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_LeadingLepEta" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Leading Lepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SubLeadingLepEta" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Subleading Lepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_Fatjet_Eta" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_fatjet_eta --xmin -2.5 --xmax 2.5 --xlabel "Fat Jet #eta" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_Fatjet_Phi" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Fat Jet #phi" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_DeltaR_LeadLep_Fatjet" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "#DeltaR(lead lep, fat jet)" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_LeadLep_LSF" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_leadlep_lsf --xmin 0 --xmax 1 --xlabel "Lead Lep LSF" --rebin 5 --rmin 0 --rmax 2.5
#python MM.py  --hist "Obj_PU_Boosted_Flavor_CR mu_ejets_mll" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_mll --xmin 0 --xmax 1000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.5

python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_WRpt" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_WR_pt --xmin 0 --xmax 1000 --xlabel "WR p_{T} (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_mass" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_dilepton_mass --xmin 0 --xmax 2000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_eta" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_dilepton_eta --xmin -5 --xmax 5 --xlabel "Dilepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_phi" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Dilepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_WR_eta" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_WR_eta --xmin -5 --xmax 5 --xlabel "WR #eta" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_WR_phi" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "WR #phi" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_LeadingLepPhi" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Leading Lepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SubLeadingLepPhi" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Lepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_Fatjet_lsf3" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Fat Jet LSF3" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_dphi_leadlep_fatjet" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "#Delta#phi(lead lep, fat jet)" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_boosted_Flavor_CR_mu_ejet_pvgood" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_punum --xmin 0 --xmax 80 --xlabel "Number of Pileup Vertices" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_jetnum" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_jetnum --xmin 0 --xmax 5 --xlabel "Number of Jets" --rmin 0 --rmax 2.5

python MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_mu_ejets_Flavor_CR" --ymin 1 --ymax 2e3 --output BoostFLVMEJ_mlljj --xmin 800 --xmax 4000 --xlabel "m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_pt(ll)_boosted_mu_ejets_Flavor_CR" --ymin 1 --ymax 1e5 --output BoostFLVMEJ_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Dilepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_LeadingLepPt" --ymin 1 --ymax 1e6 --output BoostFLVMEJ_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)" --bins "50,90,130,170,210,250,290,310,350,390,430,470,510,550,590,630,670,710,750,790,830,870,910,950,1000" --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SubLeadingLepPt" --ymin 1 --ymax 1e5 --output BoostFLVMEJ_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Subleading Lepton p_{T} (GeV)" --bins "50,70,90,110,130,150,170,190,210,230,250,270,290,310,330,350,370,390,410,430,450,470,490,500" --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_Fatjet_pt" --ymin 1 --ymax 1e5 --output BoostFLVMEJ_fatjet_pt --xmin 0 --xmax 1000 --xlabel "Fat Jet p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0



### same sign 

python MM.py  --hist "Obj_PU_leading_fatjet_pt_boosted_mu_ejets_SS_Flavor_CR" --ymin 1e-1 --ymax 3e3 --output BoostFLVMEJ_SS_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Same sign Leading Fat Jet p_{T} (GeV)" --bins "200,400,600,800,1000,2000" --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_Fatjet_SDMass" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_fatjet_SDMass --xmin 0 --xmax 200 --xlabel "Same sign Fat Jet Soft Drop Mass (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_LeadingLepEta" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Leading Lepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_SubLeadingLepEta" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Subleading Lepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_Fatjet_Eta" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_fatjet_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Fat Jet #eta" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_Fatjet_Phi" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Fat Jet #phi" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_DeltaR_LeadLep_Fatjet" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "Same sign #DeltaR(lead lep, fat jet)" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_LeadLep_LSF" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_leadlep_lsf --xmin 0 --xmax 1 --xlabel "Same sign Lead Lep LSF" --rebin 5 --rmin 0 --rmax 2.5
#python MM.py  --hist "Obj_PU_Boosted_Flavor_CR mu_ejets_SS_mll" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_mll --xmin 0 --xmax 1000 --xlabel "Same sign m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.5

python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_WRpt" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_WR_pt --xmin 0 --xmax 1000 --xlabel "Same sign WR p_{T} (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_mass" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_dilepton_mass --xmin 0 --xmax 2000 --xlabel "Same sign m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_eta" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Same sign Dilepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_phi" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Dilepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_WR_eta" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_WR_eta --xmin -5 --xmax 5 --xlabel "Same sign WR #eta" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_WR_phi" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign WR #phi" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_LeadingLepPhi" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Leading Lepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_SubLeadingLepPhi" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Subleading Lepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_Fatjet_lsf3" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Same sign Fat Jet LSF3" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_dphi_leadlep_fatjet" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "Same sign #Delta#phi(lead lep, fat jet)" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_boosted_Flavor_CR_mu_ejet_pvgood" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_punum --xmin 0 --xmax 80 --xlabel "Same sign Number of Pileup Vertices" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_jetnum" --ymin 1e-1 --ymax 1e3 --output BoostFLVMEJ_SS_jetnum --xmin 0 --xmax 5 --xlabel "Same sign Number of Jets" --rmin 0 --rmax 2.5

python MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_mu_ejets_SS_Flavor_CR" --ymin 1 --ymax 2e3 --output BoostFLVMEJ_SS_mlljj --xmin 800 --xmax 4000 --xlabel "Same sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_pt(ll)_boosted_mu_ejets_SS_Flavor_CR" --ymin 1 --ymax 1e3 --output BoostFLVMEJ_SS_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Same sign Dilepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_LeadingLepPt" --ymin 1 --ymax 1e6 --output BoostFLVMEJ_SS_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Same sign Leading Lepton p_{T} (GeV)" --bins "50,90,130,170,210,250,290,310,350,390,430,470,510,550,590,630,670,710,750,790,830,870,910,950,1000" --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_SubLeadingLepPt" --ymin 1 --ymax 1e3 --output BoostFLVMEJ_SS_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Same sign Subleading Lepton p_{T} (GeV)" --bins "50,70,90,110,130,150,170,190,210,230,250,270,290,310,330,350,370,390,410,430,450,470,490,500" --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_SS_Fatjet_pt" --ymin 1 --ymax 1e3 --output BoostFLVMEJ_SS_fatjet_pt --xmin 0 --xmax 1000 --xlabel "Same sign Fat Jet p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0



### other sign 

python MM.py  --hist "Obj_PU_leading_fatjet_pt_boosted_mu_ejets_OS_Flavor_CR" --ymin 1e-1 --ymax 3e3 --output BoostFLVMEJ_OS_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Other sign Leading Fat Jet p_{T} (GeV)" --bins "200,400,600,800,1000,2000" --rmin 0 --rmax 2.5

python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_Fatjet_SDMass" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_fatjet_SDMass --xmin 0 --xmax 200 --xlabel "Other sign Fat Jet Soft Drop Mass (GeV)" --rebin 5 --rmin 0 --rmax 2.5


python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_LeadingLepEta" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Leading Lepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_SubLeadingLepEta" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Subleading Lepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_Fatjet_Eta" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_fatjet_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Fat Jet #eta" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_Fatjet_Phi" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Fat Jet #phi" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_DeltaR_LeadLep_Fatjet" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "Other sign #DeltaR(lead lep, fat jet)" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_LeadLep_LSF" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_leadlep_lsf --xmin 0 --xmax 1 --xlabel "Other sign Lead Lep LSF" --rebin 5 --rmin 0 --rmax 2.5
#python MM.py  --hist "Obj_PU_Boosted_Flavor_CR mu_ejets_OS_mll" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_mll --xmin 0 --xmax 1000 --xlabel "Other sign m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.5

python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_WRpt" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_WR_pt --xmin 0 --xmax 1000 --xlabel "Other sign WR p_{T} (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_mass" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_dilepton_mass --xmin 0 --xmax 2000 --xlabel "Other sign m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_eta" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Other sign Dilepton #eta" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_phi" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Dilepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_WR_eta" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_WR_eta --xmin -5 --xmax 5 --xlabel "Other sign WR #eta" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_WR_phi" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign WR #phi" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_LeadingLepPhi" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Leading Lepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_SubLeadingLepPhi" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Subleading Lepton #phi" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_Fatjet_lsf3" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Other sign Fat Jet LSF3" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_dphi_leadlep_fatjet" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "Other sign #Delta#phi(lead lep, fat jet)" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_boosted_Flavor_CR_mu_ejet_pvgood" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_punum --xmin 0 --xmax 80 --xlabel "Other sign Number of Pileup Vertices" --rebin 5 --rmin 0 --rmax 2.5
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_jetnum" --ymin 1e-1 --ymax 1e5 --output BoostFLVMEJ_OS_jetnum --xmin 0 --xmax 5 --xlabel "Other sign Number of Jets" --rmin 0 --rmax 2.5

python MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_mu_ejets_OS_Flavor_CR" --ymin 1 --ymax 2e3 --output BoostFLVMEJ_OS_mlljj --xmin 800 --xmax 4000 --xlabel "Other sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_pt(ll)_boosted_mu_ejets_OS_Flavor_CR" --ymin 1 --ymax 1e5 --output BoostFLVMEJ_OS_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Other sign Dilepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_LeadingLepPt" --ymin 1 --ymax 1e6 --output BoostFLVMEJ_OS_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Other sign Leading Lepton p_{T} (GeV)" --bins "50,90,130,170,210,250,290,310,350,390,430,470,510,550,590,630,670,710,750,790,830,870,910,950,1000" --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_SubLeadingLepPt" --ymin 1 --ymax 1e5 --output BoostFLVMEJ_OS_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Other sign Subleading Lepton p_{T} (GeV)" --bins "50,70,90,110,130,150,170,190,210,230,250,270,290,310,330,350,370,390,410,430,450,470,490,500" --rmin 0 --rmax 2.0
python MM.py  --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_OS_Fatjet_pt" --ymin 1 --ymax 1e5 --output BoostFLVMEJ_OS_fatjet_pt --xmin 0 --xmax 1000 --xlabel "Other sign Fat Jet p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0

