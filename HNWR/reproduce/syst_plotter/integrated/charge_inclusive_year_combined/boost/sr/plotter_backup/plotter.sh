#!/usr/bin/env bash
# Boosted SR - EE (sign inclusive)


#python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_mass_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_dilepton_mass --xmin 0 --xmax 2000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_eta_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_dilepton_eta --xmin -5 --xmax 5 --xlabel "Dilepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_phi_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Dilepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_eta_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_fatjet_eta --xmin -2.4 --xmax 2.4 --xlabel "Fat Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_phi_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Fat Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_SDM_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_fatjet_SDM --xmin 0 --xmax 200 --xlabel "Fat Jet Soft Drop Mass (GeV)" --rebin 2 --rmin 0.7 --rmax 1.3

python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_pt_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_WR_pt --xmin 0 --xmax 8000 --xlabel "WR p_{T} (GeV)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_eta_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_WR_eta --xmin -5 --xmax 5 --xlabel "WR #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_phi_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "WR #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_lep_eta_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Leading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_lep_phi_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Leading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_subleading_lep_eta_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Subleading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_subleading_lep_phi_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_lsf3_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Fat Jet LSF3" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_deltaR_leadlep_fatjet_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "#DeltaR(lead lep, fat jet)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_dphi_leadlep_fatjet_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "#Delta#phi(lead lep, fat jet)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_pvgood_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_punum --xmin 0 --xmax 80 --xlabel "Number of Pileup Vertices" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_jetnum_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_jetnum --xmin 0 --xmax 20 --xlabel "Number of Jets" --rmin 0.7 --rmax 1.3

python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WRMass_ee" --ymin 1 --ymax 1e5 --output BoostSREE_WRMass --xmin 800 --xmax 4000 --xlabel "m(lljj) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_Dilepton_Pt_ee" --ymin 1 --ymax 1e5 --output BoostSREE_Dilepton_pt --xmin 0 --xmax 1000 --xlabel "p_{T}^{ll} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_LeadingLepPt_ee" --ymin 1 --ymax 1e5 --output BoostSREE_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)" --bins "0,50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000" --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_SubLeadingLepPt_ee" --ymin 1 --ymax 1e5 --output BoostSREE_subleading_lep_pt --xmin 0 --xmax 1000 --xlabel "Subleading Lepton p_{T} (GeV)" --bins "0,50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000" --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_mll_ee" --ymin 1 --ymax 1e5 --output BoostSREE_dilepton_mass --xmin 0 --xmax 2000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_leading_fatjet_pt_boosted_ee" --ymin 1 --ymax 1e5 --output BoostSREE_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "p_{T}^{J} (GeV)" --bins "0,200,400,600,800,1000,2000"--rmin 0 --rmax 2.0


# Boosted SR - EE SS
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_eta_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Same sign Dilepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_phi_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Dilepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_eta_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_fatjet_eta --xmin -2.4 --xmax 2.4 --xlabel "Same sign Fat Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_phi_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Fat Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_SDM_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_fatjet_SDM --xmin 0 --xmax 200 --xlabel "Same sign Fat Jet Soft Drop Mass (GeV)" --rebin 2 --rmin 0.7 --rmax 1.3

python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_pt_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_WR_pt --xmin 0 --xmax 8000 --xlabel "Same sign WR p_{T} (GeV)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_eta_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_WR_eta --xmin -5 --xmax 5 --xlabel "Same sign WR #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_phi_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign WR #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_lep_eta_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Leading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_lep_phi_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Leading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_subleading_lep_eta_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Subleading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_subleading_lep_phi_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Subleading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_lsf3_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Same sign Fat Jet LSF3" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_deltaR_leadlep_fatjet_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "Same sign #DeltaR(lead lep, fat jet)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_dphi_leadlep_fatjet_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "Same sign #Delta#phi(lead lep, fat jet)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_pvgood_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_punum --xmin 0 --xmax 80 --xlabel "Same sign Number of Pileup Vertices" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_jetnum_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_jetnum --xmin 0 --xmax 20 --xlabel "Same sign Number of Jets" --rmin 0.7 --rmax 1.3

python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WRMass_ee_SS" --ymin 1 --ymax 1e5 --output BoostSREE_SS_WRMass --xmin 800 --xmax 4000 --xlabel "Same sign m(lljj) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_Dilepton_Pt_ee_SS" --ymin 1 --ymax 1e5 --output BoostSREE_SS_Dilepton_pt --xmin 0 --xmax 1000 --xlabel "Same sign p_{T}^{ll} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_LeadingLepPt_ee_SS" --ymin 1 --ymax 1e5 --output BoostSREE_SS_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Same sign Leading Lepton p_{T} (GeV)" --bins "0,50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000" --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_SubLeadingLepPt_ee_SS" --ymin 1 --ymax 1e5 --output BoostSREE_SS_subleading_lep_pt --xmin 0 --xmax 1000 --xlabel "Same sign Subleading Lepton p_{T} (GeV)" --bins "0,50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000" --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_mll_ee_SS" --ymin 1 --ymax 1e5 --output BoostSREE_SS_dilepton_mass --xmin 0 --xmax 2000 --xlabel "Same sign m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_leading_fatjet_pt_boosted_ee_SS" --ymin 1 --ymax 1e5 --output BoostSREE_SS_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Same sign p_{T}^{J} (GeV)" --bins "0,200,400,600,800,1000,2000"--rmin 0 --rmax 2.0

# Boosted SR - EE OS
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_eta_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Other Dilepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_phi_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Dilepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_eta_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_fatjet_eta --xmin -2.4 --xmax 2.4 --xlabel "Other sign Fat Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_phi_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Fat Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_SDM_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_fatjet_SDM --xmin 0 --xmax 200 --xlabel "Other sign Fat Jet Soft Drop Mass (GeV)" --rebin 2 --rmin 0.7 --rmax 1.3

python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_pt_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_WR_pt --xmin 0 --xmax 8000 --xlabel "Other sign WR p_{T} (GeV)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_eta_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_WR_eta --xmin -5 --xmax 5 --xlabel "Other sign WR #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_phi_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign WR #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_lep_eta_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Leading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_lep_phi_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Leading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_subleading_lep_eta_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Subleading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_subleading_lep_phi_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Subleading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_lsf3_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Other sign Fat Jet LSF3" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_deltaR_leadlep_fatjet_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "Other sign #DeltaR(lead lep, fat jet)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_dphi_leadlep_fatjet_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "Other sign #Delta#phi(lead lep, fat jet)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_pvgood_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_punum --xmin 0 --xmax 80 --xlabel "Other sign Number of Pileup Vertices" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_jetnum_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_jetnum --xmin 0 --xmax 20 --xlabel "Other sign Number of Jets" --rmin 0.7 --rmax 1.3

python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WRMass_ee_OS" --ymin 1 --ymax 1e5 --output BoostSREE_OS_WRMass --xmin 800 --xmax 4000 --xlabel "Other sign m(lljj) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_Dilepton_Pt_ee_OS" --ymin 1 --ymax 1e5 --output BoostSREE_OS_Dilepton_pt --xmin 0 --xmax 1000 --xlabel "Other sign p_{T}^{ll} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_LeadingLepPt_ee_OS" --ymin 1 --ymax 1e5 --output BoostSREE_OS_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Other sign Leading Lepton p_{T} (GeV)" --bins "0,50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000" --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_SubLeadingLepPt_ee_OS" --ymin 1 --ymax 1e5 --output BoostSREE_OS_subleading_lep_pt --xmin 0 --xmax 1000 --xlabel "Other sign Subleading Lepton p_{T} (GeV)" --bins "0,50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000" --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_mll_ee_OS" --ymin 1 --ymax 1e5 --output BoostSREE_OS_dilepton_mass --xmin 0 --xmax 2000 --xlabel "Other sign m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_leading_fatjet_pt_boosted_ee_OS" --ymin 1 --ymax 1e5 --output BoostSREE_OS_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Other sign p_{T}^{J} (GeV)" --bins "0,200,400,600,800,1000,2000"--rmin 0 --rmax 2.0

# Boosted SR - MM (sign inclusive)

#python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_mass_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_mass --xmin 0 --xmax 2000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_eta_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_dilepton_eta --xmin -5 --xmax 5 --xlabel "Dilepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_phi_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Dilepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_eta_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_fatjet_eta --xmin -2.4 --xmax 2.4 --xlabel "Fat Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_phi_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Fat Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_SDM_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_fatjet_SDM --xmin 0 --xmax 200 --xlabel "Fat Jet Soft Drop Mass (GeV)" --rebin 2 --rmin 0.7 --rmax 1.3

python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_pt_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_WR_pt --xmin 0 --xmax 8000 --xlabel "WR p_{T} (GeV)" --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_eta_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_WR_eta --xmin -5 --xmax 5 --xlabel "WR #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_phi_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "WR #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_lep_eta_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Leading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_lep_phi_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Leading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_subleading_lep_eta_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Subleading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_subleading_lep_phi_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_lsf3_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Fat Jet LSF3" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_deltaR_leadlep_fatjet_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "#DeltaR(lead lep, fat jet)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_dphi_leadlep_fatjet_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "#Delta#phi(lead lep, fat jet)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_pvgood_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_punum --xmin 0 --xmax 80 --xlabel "Number of Pileup Vertices" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_jetnum_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_jetnum --xmin 0 --xmax 20 --xlabel "Number of Jets" --rmin 0.7 --rmax 1.3

python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_WRMass_mumu" --ymin 1 --ymax 1e5 --output BoostSRMM_WRMass --xmin 800 --xmax 4000 --xlabel "m(lljj) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_Dilepton_Pt_mumu" --ymin 1 --ymax 1e5 --output BoostSRMM_Dilepton_pt --xmin 0 --xmax 1000 --xlabel "m(lljj) (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_LeadingLepPt_mumu" --ymin 1 --ymax 1e5 --output BoostSRMM_LeadingLepPt --xmin 0 --xmax 1000 --xlabel "m(lljj) (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_SubLeadingLepPt_mumu" --ymin 1 --ymax 1e5 --output BoostSRMM_SubLeadingLepPt --xmin 0 --xmax 1000 --xlabel "m(lljj) (GeV)" --rebin 20 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_mll_mumu" --ymin 1 --ymax 1e5 --output BoostSRMM_dilepton_mass --xmin 0 --xmax 2000 --xlabel "m(lljj) (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_fatjet_pt_boosted_mumu" --ymin 1 --ymax 1e5 --output BoostSRMM_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "m(lljj) (GeV)" --rebin 50 --rmin 0 --rmax 2.0


# Boosted SR - MM SS
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_eta_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Same sign Dilepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_phi_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Dilepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_eta_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_fatjet_eta --xmin -2.4 --xmax 2.4 --xlabel "Same sign Fat Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_phi_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Fat Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_SDM_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_fatjet_SDM --xmin 0 --xmax 200 --xlabel "Same sign Fat Jet Soft Drop Mass (GeV)" --rebin 2 --rmin 0.7 --rmax 1.3

python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_pt_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_WR_pt --xmin 0 --xmax 8000 --xlabel "Same sign WR p_{T} (GeV)" --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_eta_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_WR_eta --xmin -5 --xmax 5 --xlabel "Same sign WR #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_phi_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign WR #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_lep_eta_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Leading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_lep_phi_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Leading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_subleading_lep_eta_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Subleading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_subleading_lep_phi_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Subleading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_lsf3_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Same sign Fat Jet LSF3" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_deltaR_leadlep_fatjet_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "Same sign #DeltaR(lead lep, fat jet)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_dphi_leadlep_fatjet_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "Same sign #Delta#phi(lead lep, fat jet)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_pvgood_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_punum --xmin 0 --xmax 80 --xlabel "Same sign Number of Pileup Vertices" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_jetnum_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_jetnum --xmin 0 --xmax 20 --xlabel "Same sign Number of Jets" --rmin 0.7 --rmax 1.3

python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_WRMass_mumu_SS" --ymin 1 --ymax 1e5 --output BoostSRMM_SS_WRMass --xmin 800 --xmax 4000 --xlabel "Same sign m(lljj) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_Dilepton_Pt_mumu_SS" --ymin 1 --ymax 1e5 --output BoostSRMM_SS_Dilepton_pt --xmin 0 --xmax 1000 --xlabel "Same sign m(lljj) (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_LeadingLepPt_mumu_SS" --ymin 1 --ymax 1e5 --output BoostSRMM_SS_LeadingLepPt --xmin 0 --xmax 1000 --xlabel "Same sign m(lljj) (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_SubLeadingLepPt_mumu_SS" --ymin 1 --ymax 1e5 --output BoostSRMM_SS_SubLeadingLepPt --xmin 0 --xmax 1000 --xlabel "Same sign m(lljj) (GeV)" --rebin 20 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_mll_mumu_SS" --ymin 1 --ymax 1e5 --output BoostSRMM_SS_dilepton_mass --xmin 0 --xmax 2000 --xlabel "Same sign m(lljj) (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_fatjet_pt_boosted_mumu_SS" --ymin 1 --ymax 1e5 --output BoostSRMM_SS_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Same sign m(lljj) (GeV)" --rebin 50 --rmin 0 --rmax 2.0

# Boosted SR - MM OS
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_eta_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Other sign Dilepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_phi_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Dilepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_eta_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_fatjet_eta --xmin -2.4 --xmax 2.4 --xlabel "Other sign Fat Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_phi_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Fat Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_SDM_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_fatjet_SDM --xmin 0 --xmax 200 --xlabel "Other sign Fat Jet Soft Drop Mass (GeV)" --rebin 2 --rmin 0.7 --rmax 1.3

python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_pt_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_WR_pt --xmin 0 --xmax 8000 --xlabel "Other sign WR p_{T} (GeV)" --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_eta_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_WR_eta --xmin -5 --xmax 5 --xlabel "Other sign WR #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_phi_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign WR #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_lep_eta_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Leading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_lep_phi_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Leading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_subleading_lep_eta_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Subleading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_subleading_lep_phi_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Subleading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_lsf3_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Other sign Fat Jet LSF3" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_deltaR_leadlep_fatjet_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "Other sign #DeltaR(lead lep, fat jet)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_dphi_leadlep_fatjet_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "Other sign #Delta#phi(lead lep, fat jet)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_pvgood_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_punum --xmin 0 --xmax 80 --xlabel "Other sign Number of Pileup Vertices" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_jetnum_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_jetnum --xmin 0 --xmax 20 --xlabel "Other sign Number of Jets" --rmin 0.7 --rmax 1.3

python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_WRMass_mumu_OS" --ymin 1 --ymax 1e5 --output BoostSRMM_OS_WRMass --xmin 800 --xmax 4000 --xlabel "Other sign m(lljj) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_Dilepton_Pt_mumu_OS" --ymin 1 --ymax 1e5 --output BoostSRMM_OS_Dilepton_pt --xmin 0 --xmax 1000 --xlabel "Other sign m(lljj) (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_LeadingLepPt_mumu_OS" --ymin 1 --ymax 1e5 --output BoostSRMM_OS_LeadingLepPt --xmin 0 --xmax 1000 --xlabel "Other sign m(lljj) (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_SubLeadingLepPt_mumu_OS" --ymin 1 --ymax 1e5 --output BoostSRMM_OS_SubLeadingLepPt --xmin 0 --xmax 1000 --xlabel "Other sign m(lljj) (GeV)" --rebin 20 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_mll_mumu_OS" --ymin 1 --ymax 1e5 --output BoostSRMM_OS_dilepton_mass --xmin 0 --xmax 2000 --xlabel "Other sign m(lljj) (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_fatjet_pt_boosted_mumu_OS" --ymin 1 --ymax 1e5 --output BoostSRMM_OS_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Other sign m(lljj) (GeV)" --rebin 50 --rmin 0 --rmax 2.0
