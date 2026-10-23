#!/usr/bin/env bash
# Boosted SR - EE (sign inclusive)
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_Dilepton_Pt_ee" --ymin 3 --ymax 1e5 --output BoostSREE_Dilepton_pt --xmin 0 --xmax 1000 --xlabel "p_{T}^{ll} (GeV)" --rebin 50 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_leading_fatjet_pt_boosted_ee" --ymin 3 --ymax 1e5 --output BoostSREE_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "p_{T}^{J} (GeV)" --bins "0,200,400,600,800,1000,2000" --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WRMass_ee" --ymin 3 --ymax 1e5 --output BoostSREE_WRMass --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_LeadingLepPt_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)" --bins "0,50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000" --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_SubLeadingLepPt_ee" --ymin 1e-1 --ymax 5e2 --output BoostSREE_subleading_lep_pt --xmin 0 --xmax 1000 --xlabel "Subleading Lepton p_{T} (GeV)" --bins "0,50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000" --rmin 0.7 --rmax 1.3
#python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_mass_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_dilepton_mass --xmin 0 --xmax 2000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_eta_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_dilepton_eta --xmin -5 --xmax 5 --xlabel "Dilepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_phi_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Dilepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_eta_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_fatjet_eta --xmin -2.4 --xmax 2.4 --xlabel "Fat Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_phi_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Fat Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_SDM_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_fatjet_SDM --xmin 0 --xmax 200 --xlabel "Fat Jet Soft Drop Mass (GeV)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_mll_ee" --ymin 1e-1 --ymax 1e5 --output BoostSREE_dilepton_mass --xmin 0 --xmax 2000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
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

# Boosted SR - EE SS
python EE.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_Dilepton_Pt_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_Dilepton_pt --xmin 0 --xmax 1000 --xlabel "p_{T}^{ll} (GeV)" --rebin 10 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_SR_leading_fatjet_pt_boosted_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "p_{T}^{J} (GeV)" --bins "0,200,400,600,800,1000,2000" --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_WRMass_ee_SS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_SS_WRMass --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1500,1800,8000" --rmin 0.7 --rmax 1.3

# Boosted SR - EE OS
python EE.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_Dilepton_Pt_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_Dilepton_pt --xmin 0 --xmax 1000 --xlabel "p_{T}^{ll} (GeV)" --rebin 10 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_SR_leading_fatjet_pt_boosted_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_leading_fatjet_pt  --xmin 0 --xmax 2000 --xlabel "p_{T}^{J} (GeV)" --bins "0,200,400,600,800,1000,2000" --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_WRMass_ee_OS" --ymin 1e-1 --ymax 1e5 --output BoostSREE_OS_WRMass --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1500,1800,8000" --rmin 0.7 --rmax 1.3

# Boosted SR - MM (sign inclusive)
python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_Dilepton_Pt_mumu" --ymin 3 --ymax 1e5 --output BoostSRMM_Dilepton_pt --xmin 0 --xmax 1000 --xlabel "p_{T}^{ll} (GeV)" --rebin 50 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_leading_fatjet_pt_boosted_mumu" --ymin 3 --ymax 1e5 --output BoostSRMM_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "p_{T}^{J} (GeV)" --bins "0,200,400,600,800,1000,2000" --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_WRMass_mumu" --ymin 3 --ymax 1e5 --output BoostSRMM_WRMass --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_LeadingLepPt_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)" --bins "0,50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000" --rmin 0.7 --rmax 1.3
#python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_mass_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_mass --xmin 0 --xmax 2000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_eta_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_dilepton_eta --xmin -5 --xmax 5 --xlabel "Dilepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_phi_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Dilepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_eta_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_fatjet_eta --xmin -2.4 --xmax 2.4 --xlabel "Fat Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_phi_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Fat Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_SDM_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_fatjet_SDM --xmin 0 --xmax 200 --xlabel "Fat Jet Soft Drop Mass (GeV)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_mll_mumu" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_dilepton_mass --xmin 0 --xmax 2000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
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

# Boosted SR - MM SS
python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_Dilepton_Pt_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_Dilepton_pt --xmin 0 --xmax 1000 --xlabel "p_{T}^{ll} (GeV)" --rebin 10 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_leading_fatjet_pt_boosted_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "p_{T}^{J} (GeV)" --bins "0,200,400,600,800,1000,2000" --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_WRMass_mumu_SS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_SS_WRMass --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1500,1800,8000" --rmin 0.7 --rmax 1.3

# Boosted SR - MM OS
python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_Dilepton_Pt_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_Dilepton_pt --xmin 0 --xmax 1000 --xlabel "p_{T}^{ll} (GeV)" --rebin 10 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_leading_fatjet_pt_boosted_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "p_{T}^{J} (GeV)" --bins "0,200,400,600,800,1000,2000" --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_WRMass_mumu_OS" --ymin 1e-1 --ymax 1e5 --output BoostSRMM_OS_WRMass --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1500,1800,8000" --rmin 0.7 --rmax 1.3
