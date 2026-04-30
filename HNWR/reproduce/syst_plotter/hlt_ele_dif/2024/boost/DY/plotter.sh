#!/usr/bin/env bash
# Boosted DY CR - EE
python EE.py --signal-scale 1.0 --hist "Obj_PU_pt(ll)_boosted_DY_CR_EE" --ymin 10 --ymax 1e5 --output BoostDYEE_pt --xmin 0 --xmax 1000 --xlabel "Dilepton p_{T} (GeV)" --rebin 50 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_leading_fatjet_pt_boosted_DY_CR_EE" --ymin 3 --ymax 3e3 --output BoostDYEE_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Leading Fat Jet p_{T} (GeV)" --bins "200,400,600,800,1000,2000" --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_mlljj --xmin 800 --xmax 8000 --xlabel "m(lljj) (GeV)" --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_leading_lep_pt_boosted_DY_CR_EE" --ymin 3 --ymax 3e3 --output BoostDYEE_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)" --bins "0,100,200,300,400,500,1000,2000" --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_subleading_lep_pt_boosted_DY_CR_EE" --ymin 3 --ymax 3e3 --output BoostDYEE_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Subleading Lepton p_{T} (GeV)" --bins "0,50,100,150,200,250,300,500,1000" --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_mass_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_mass --xmin 0 --xmax 1000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_eta_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_eta --xmin -5 --xmax 5 --xlabel "Dilepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_phi_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_phi --xmin -3.14 --xmax 3.14 --xlabel "Dilepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_fatjet_eta_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_fatjet_eta --xmin -2.4 --xmax 2.4 --xlabel "Fat Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_fatjet_phi_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Fat Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_fatjet_SDM_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_fatjet_SDM --xmin 0 --xmax 200 --xlabel "Fat Jet Soft Drop Mass (GeV)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_mll_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_mll --xmin 0 --xmax 1000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_WR_pt_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_WR_pt --xmin 0 --xmax 2000 --xlabel "WR p_{T} (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_WR_eta_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_WR_eta --xmin -5 --xmax 5 --xlabel "WR #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_WR_phi_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "WR #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_leading_lep_eta_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Leading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_leading_lep_phi_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Leading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_subleading_lep_eta_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Subleading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_subleading_lep_phi_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_fatjet_lsf3_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Fat Jet LSF3" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_deltaR_leadlep_fatjet_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "#DeltaR(lead lep, fat jet)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_dphi_leadlep_fatjet_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "#Delta#phi(lead lep, fat jet)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_punum_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_punum --xmin 0 --xmax 80 --xlabel "Number of Pileup Vertices" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_jetnum_boosted_DY_CR_EE" --ymin 3 --ymax 1e4 --output BoostDYEE_jetnum --xmin 0 --xmax 20 --xlabel "Number of Jets" --rmin 0.7 --rmax 1.3

# Boosted DY CR - MM
python MM.py --signal-scale 1.0 --hist "Obj_PU_pt(ll)_boosted_DY_CR_MM" --ymin 10 --ymax 1e5 --output BoostDYMM_pt --xmin 0 --xmax 1000 --xlabel "Dilepton p_{T} (GeV)" --rebin 50 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_leading_fatjet_pt_boosted_DY_CR_MM" --ymin 3 --ymax 3e3 --output BoostDYMM_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "Leading Fat Jet p_{T} (GeV)" --bins "200,400,600,800,1000,2000" --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_mlljj --xmin 800 --xmax 8000 --xlabel "m(lljj) (GeV)" --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_leading_lep_pt_boosted_DY_CR_MM" --ymin 3 --ymax 3e3 --output BoostDYMM_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)" --bins "0,100,200,300,400,500,1000,2000" --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_subleading_lep_pt_boosted_DY_CR_MM" --ymin 3 --ymax 3e3 --output BoostDYMM_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Subleading Lepton p_{T} (GeV)" --bins "0,50,100,150,200,250,300,500,1000" --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_mass_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_mass --xmin 0 --xmax 1000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_eta_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_eta --xmin -5 --xmax 5 --xlabel "Dilepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_phi_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_phi --xmin -3.14 --xmax 3.14 --xlabel "Dilepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_fatjet_eta_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_fatjet_eta --xmin -2.4 --xmax 2.4 --xlabel "Fat Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_fatjet_phi_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_fatjet_phi --xmin -3.14 --xmax 3.14 --xlabel "Fat Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_fatjet_SDM_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_fatjet_SDM --xmin 0 --xmax 200 --xlabel "Fat Jet Soft Drop Mass (GeV)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_mll_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_mll --xmin 0 --xmax 1000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_WR_pt_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_WR_pt --xmin 0 --xmax 2000 --xlabel "WR p_{T} (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_WR_eta_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_WR_eta --xmin -5 --xmax 5 --xlabel "WR #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_WR_phi_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_WR_phi --xmin -3.14 --xmax 3.14 --xlabel "WR #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_leading_lep_eta_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Leading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_leading_lep_phi_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Leading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_subleading_lep_eta_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Subleading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_subleading_lep_phi_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_fatjet_lsf3_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_fatjet_lsf3 --xmin 0 --xmax 1 --xlabel "Fat Jet LSF3" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_deltaR_leadlep_fatjet_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_deltaR_leadlep_fatjet --xmin 0 --xmax 5 --xlabel "#DeltaR(lead lep, fat jet)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_dphi_leadlep_fatjet_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_dphi_leadlep_fatjet --xmin 0 --xmax 3.14 --xlabel "#Delta#phi(lead lep, fat jet)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_punum_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_punum --xmin 0 --xmax 80 --xlabel "Number of Pileup Vertices" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_jetnum_boosted_DY_CR_MM" --ymin 3 --ymax 1e4 --output BoostDYMM_jetnum --xmin 0 --xmax 20 --xlabel "Number of Jets" --rmin 0.7 --rmax 1.3
