#!/usr/bin/env bash
# Resolved DY CR - EE
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Dilepton p_{T} (GeV)" --rmin 0 --rmax 2.0 --rebin 5
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_leading_jet_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_leading_jet_pt --xmin 0 --xmax 2000 --xlabel "Leading Jet p_{T} (GeV)" --rebin 10 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_subleading_jet_pt" --ymin 1 --ymax 1e4 --output ResolveDYEE_subleading_jet_pt --xmin 0 --xmax 500 --xlabel "Subleading Jet p_{T} (GeV)" --rebin 2 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_mlljj" --ymin 1 --ymax 1e6 --output ResolveDYEE_mlljj --xmin 800 --xmax 4000 --xlabel "m(lljj) (GeV)" --rebin 20 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_leading_lep_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_subleading_lep_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_subleading_lep_pt --xmin 0 --xmax 400 --xlabel "Subleading Lepton p_{T} (GeV)"   --rebin 10 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_mass" --ymin 1 --ymax 1e6 --output ResolveDYEE_dilepton_mass --xmin 0 --xmax 200 --xlabel "m(ll) (GeV)" --rebin 1 --rmin 0 --rmax 2.0   

python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_dilepton_eta --xmin -5 --xmax 5 --xlabel "Dilepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Dilepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_leading_jet_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_leading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Leading Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_leading_jet_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_leading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Leading Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_subleading_jet_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_subleading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Subleading Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_subleading_jet_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_subleading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_j1j2_mass" --ymin 1 --ymax 1e6 --output ResolveDYEE_j1j2_mass --xmin 0 --xmax 1000 --xlabel "Dijet Mass (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_j1j2_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_j1j2_pt --xmin 0 --xmax 1000 --xlabel "Dijet p_{T} (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_j1j2_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_j1j2_eta --xmin -5 --xmax 5 --xlabel "Dijet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_j1j2_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Dijet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_l1j1j2_mass" --ymin 1 --ymax 1e6 --output ResolveDYEE_l1j1j2_mass --xmin 0 --xmax 2000 --xlabel "m(l1jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_l1j1j2_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_l1j1j2_pt --xmin 0 --xmax 1000 --xlabel "p_{T}(l1jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_l1j1j2_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_l1j1j2_eta --xmin -5 --xmax 5 --xlabel "#eta(l1jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_l1j1j2_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_l1j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "#phi(l1jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_l2j1j2_mass" --ymin 1 --ymax 1e6 --output ResolveDYEE_l2j1j2_mass --xmin 0 --xmax 2000 --xlabel "m(l2jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_l2j1j2_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_l2j1j2_pt --xmin 0 --xmax 1000 --xlabel "p_{T}(l2jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_l2j1j2_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_l2j1j2_eta --xmin -5 --xmax 5 --xlabel "#eta(l2jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_l2j1j2_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_l2j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "#phi(l2jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_mlljj_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_mlljj_pt --xmin 0 --xmax 1000 --xlabel "WR p_{T} (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_mlljj_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_mlljj_eta --xmin -5 --xmax 5 --xlabel "WR #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_mlljj_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_mlljj_phi --xmin -3.14 --xmax 3.14 --xlabel "WR #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_leading_lep_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Leading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_leading_lep_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Leading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_subleading_lep_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Subleading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_subleading_lep_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_jetnum" --ymin 1 --ymax 1e8 --output ResolveDYEE_jetnum --xmin 0 --xmax 5 --xlabel "Number of Jets" --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_pvgood" --ymin 1 --ymax 1e6 --output ResolveDYEE_punum --xmin 0 --xmax 80 --xlabel "Number of Pileup Vertices" --rebin 2 --rmin 0.7 --rmax 1.3

## same sign 
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_pt" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Same sign Dilepton p_{T} (GeV)" --rmin 0 --rmax 2.0 --rebin 5
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_leading_jet_pt" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_leading_jet_pt --xmin 0 --xmax 2000 --xlabel "Same sign Leading Jet p_{T} (GeV)" --rebin 10 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_subleading_jet_pt" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_subleading_jet_pt --xmin 0 --xmax 500 --xlabel "Same sign Subleading Jet p_{T} (GeV)" --rebin 2 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_mlljj" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_mlljj --xmin 800 --xmax 4000 --xlabel "Same sign m(lljj) (GeV)" --rebin 20 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_leading_lep_pt" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Same sign Leading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_subleading_lep_pt" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_subleading_lep_pt --xmin 0 --xmax 400 --xlabel "Same sign Subleading Lepton p_{T} (GeV)"   --rebin 10 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_mass" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_dilepton_mass --xmin 0 --xmax 200 --xlabel "Same sign m(ll) (GeV)" --rebin 1 --rmin 0 --rmax 2.0   

python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_eta" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Same sign Dilepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_phi" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Dilepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_leading_jet_eta" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_leading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Leading Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_leading_jet_phi" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_leading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Leading Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_subleading_jet_eta" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_subleading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Subleading Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_subleading_jet_phi" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_subleading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Subleading Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_j1j2_mass" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_j1j2_mass --xmin 0 --xmax 1000 --xlabel "Same sign Dijet Mass (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_j1j2_pt" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_j1j2_pt --xmin 0 --xmax 1000 --xlabel "Same sign Dijet p_{T} (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_j1j2_eta" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_j1j2_eta --xmin -5 --xmax 5 --xlabel "Same sign Dijet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_j1j2_phi" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Dijet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_l1j1j2_mass" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_l1j1j2_mass --xmin 0 --xmax 2000 --xlabel "Same sign m(l1jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_l1j1j2_pt" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_l1j1j2_pt --xmin 0 --xmax 1000 --xlabel "Same sign p_{T}(l1jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_l1j1j2_eta" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_l1j1j2_eta --xmin -5 --xmax 5 --xlabel "Same sign #eta(l1jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_l1j1j2_phi" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_l1j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign #phi(l1jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_l2j1j2_mass" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_l2j1j2_mass --xmin 0 --xmax 2000 --xlabel "Same sign m(l2jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_l2j1j2_pt" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_l2j1j2_pt --xmin 0 --xmax 1000 --xlabel "Same sign p_{T}(l2jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_l2j1j2_eta" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_l2j1j2_eta --xmin -5 --xmax 5 --xlabel "Same sign #eta(l2jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_l2j1j2_phi" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_l2j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign #phi(l2jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_mlljj_pt" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_mlljj_pt --xmin 0 --xmax 1000 --xlabel "Same sign WR p_{T} (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_mlljj_eta" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_mlljj_eta --xmin -5 --xmax 5 --xlabel "Same sign WR #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_mlljj_phi" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_mlljj_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign WR #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_leading_lep_eta" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Leading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_leading_lep_phi" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Leading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_subleading_lep_eta" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Subleading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_subleading_lep_phi" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Subleading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_jetnum" --ymin 1 --ymax 1e8 --output ResolveDYEE_SS_jetnum --xmin 0 --xmax 5 --xlabel "Same sign Number of Jets" --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_pvgood" --ymin 1 --ymax 1e4 --output ResolveDYEE_SS_punum --xmin 0 --xmax 80 --xlabel "Same sign Number of Pileup Vertices" --rebin 2 --rmin 0.7 --rmax 1.3


## other sign 
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Other sign Dilepton p_{T} (GeV)" --rmin 0 --rmax 2.0 --rebin 5
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_leading_jet_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_leading_jet_pt --xmin 0 --xmax 2000 --xlabel "Other sign Leading Jet p_{T} (GeV)" --rebin 10 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_subleading_jet_pt" --ymin 1 --ymax 1e4 --output ResolveDYEE_OS_subleading_jet_pt --xmin 0 --xmax 500 --xlabel "Other sign Subleading Jet p_{T} (GeV)" --rebin 2 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_mlljj" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_mlljj --xmin 800 --xmax 4000 --xlabel "Other sign m(lljj) (GeV)" --rebin 20 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_leading_lep_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Other sign Leading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_subleading_lep_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_subleading_lep_pt --xmin 0 --xmax 400 --xlabel "Other sign Subleading Lepton p_{T} (GeV)"   --rebin 10 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_mass" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_dilepton_mass --xmin 0 --xmax 200 --xlabel "Other sign m(ll) (GeV)" --rebin 1 --rmin 0 --rmax 2.0   

python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Other sign Dilepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Dilepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_leading_jet_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_leading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Leading Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_leading_jet_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_leading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Leading Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_subleading_jet_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_subleading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Subleading Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_subleading_jet_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_subleading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Subleading Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_j1j2_mass" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_j1j2_mass --xmin 0 --xmax 1000 --xlabel "Other sign Dijet Mass (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_j1j2_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_j1j2_pt --xmin 0 --xmax 1000 --xlabel "Other sign Dijet p_{T} (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_j1j2_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_j1j2_eta --xmin -5 --xmax 5 --xlabel "Other sign Dijet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_j1j2_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Dijet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_l1j1j2_mass" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_l1j1j2_mass --xmin 0 --xmax 2000 --xlabel "Other sign m(l1jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_l1j1j2_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_l1j1j2_pt --xmin 0 --xmax 1000 --xlabel "Other sign p_{T}(l1jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_l1j1j2_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_l1j1j2_eta --xmin -5 --xmax 5 --xlabel "Other sign #eta(l1jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_l1j1j2_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_l1j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign #phi(l1jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_l2j1j2_mass" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_l2j1j2_mass --xmin 0 --xmax 2000 --xlabel "Other sign m(l2jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_l2j1j2_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_l2j1j2_pt --xmin 0 --xmax 1000 --xlabel "Other sign p_{T}(l2jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_l2j1j2_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_l2j1j2_eta --xmin -5 --xmax 5 --xlabel "Other sign #eta(l2jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_l2j1j2_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_l2j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign #phi(l2jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_mlljj_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_mlljj_pt --xmin 0 --xmax 1000 --xlabel "Other sign WR p_{T} (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_mlljj_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_mlljj_eta --xmin -5 --xmax 5 --xlabel "Other sign WR #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_mlljj_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_mlljj_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign WR #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_leading_lep_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Leading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_leading_lep_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Leading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_subleading_lep_eta" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Subleading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_subleading_lep_phi" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Subleading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_jetnum" --ymin 1 --ymax 1e8 --output ResolveDYEE_OS_jetnum --xmin 0 --xmax 5 --xlabel "Other sign Number of Jets" --rmin 0.7 --rmax 1.3
python EE.py  --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_pvgood" --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_punum --xmin 0 --xmax 80 --xlabel "Other sign Number of Pileup Vertices" --rebin 2 --rmin 0.7 --rmax 1.3




# Resolved DY CR - MM
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Dilepton p_{T} (GeV)" --rmin 0 --rmax 2.0 --rebin 5
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_leading_jet_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_leading_jet_pt --xmin 0 --xmax 2000 --xlabel "Leading Jet p_{T} (GeV)" --rebin 10 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_subleading_jet_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_subleading_jet_pt --xmin 0 --xmax 500 --xlabel "Subleading Jet p_{T} (GeV)" --rebin 2 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_mlljj" --ymin 1 --ymax 1e6 --output ResolveDYMM_mlljj --xmin 800 --xmax 4000 --xlabel "m(lljj) (GeV)" --rebin 20 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_leading_lep_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_subleading_lep_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_subleading_lep_pt --xmin 0 --xmax 1000 --xlabel "Subleading Lepton p_{T} (GeV)" --rebin 10 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_mass" --ymin 1 --ymax 1e6 --output ResolveDYMM_dilepton_mass --xmin 0 --xmax 200 --xlabel "m(ll) (GeV)" --rebin 10 --rmin 0 --rmax 2.0

python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_dilepton_eta --xmin -5 --xmax 5 --xlabel "Dilepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Dilepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_leading_jet_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_leading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Leading Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_leading_jet_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_leading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Leading Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_subleading_jet_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_subleading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Subleading Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_subleading_jet_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_subleading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_j1j2_mass" --ymin 1 --ymax 1e6 --output ResolveDYMM_j1j2_mass --xmin 0 --xmax 1000 --xlabel "Dijet Mass (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_j1j2_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_j1j2_pt --xmin 0 --xmax 1000 --xlabel "Dijet p_{T} (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_j1j2_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_j1j2_eta --xmin -5 --xmax 5 --xlabel "Dijet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_j1j2_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Dijet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_l1j1j2_mass" --ymin 1 --ymax 1e6 --output ResolveDYMM_l1j1j2_mass --xmin 0 --xmax 2000 --xlabel "m(l1jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_l1j1j2_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_l1j1j2_pt --xmin 0 --xmax 1000 --xlabel "p_{T}(l1jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_l1j1j2_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_l1j1j2_eta --xmin -5 --xmax 5 --xlabel "#eta(l1jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_l1j1j2_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_l1j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "#phi(l1jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_l2j1j2_mass" --ymin 1 --ymax 1e6 --output ResolveDYMM_l2j1j2_mass --xmin 0 --xmax 2000 --xlabel "m(l2jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_l2j1j2_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_l2j1j2_pt --xmin 0 --xmax 1000 --xlabel "p_{T}(l2jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_l2j1j2_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_l2j1j2_eta --xmin -5 --xmax 5 --xlabel "#eta(l2jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_l2j1j2_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_l2j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "#phi(l2jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_mlljj_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_mlljj_pt --xmin 0 --xmax 1000 --xlabel "WR p_{T} (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_mlljj_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_mlljj_eta --xmin -5 --xmax 5 --xlabel "WR #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_mlljj_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_mlljj_phi --xmin -3.14 --xmax 3.14 --xlabel "WR #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_leading_lep_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Leading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_leading_lep_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Leading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_subleading_lep_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Subleading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_subleading_lep_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_jetnum" --ymin 1 --ymax 1e8 --output ResolveDYMM_jetnum --xmin 0 --xmax 5 --xlabel "Number of Jets" --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_pvgood" --ymin 1 --ymax 1e6 --output ResolveDYMM_punum --xmin 0 --xmax 80 --xlabel "Number of Pileup Vertices" --rebin 2 --rmin 0.7 --rmax 1.3


## smae sign 
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_pt" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Same sign Dilepton p_{T} (GeV)" --rmin 0 --rmax 2.0 --rebin 5
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_leading_jet_pt" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_leading_jet_pt --xmin 0 --xmax 2000 --xlabel "Same sign Leading Jet p_{T} (GeV)" --rebin 10 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_subleading_jet_pt" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_subleading_jet_pt --xmin 0 --xmax 500 --xlabel "Same sign Subleading Jet p_{T} (GeV)" --rebin 2 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_mlljj" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_mlljj --xmin 800 --xmax 4000 --xlabel "Same sign m(lljj) (GeV)" --rebin 20 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_leading_lep_pt" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Same sign Leading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_subleading_lep_pt" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_subleading_lep_pt --xmin 0 --xmax 1000 --xlabel "Same sign Subleading Lepton p_{T} (GeV)" --rebin 10 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_mass" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_dilepton_mass --xmin 0 --xmax 200 --xlabel "Same sign m(ll) (GeV)" --rebin 10 --rmin 0 --rmax 2.0

python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_eta" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Same sign Dilepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_phi" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Dilepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_leading_jet_eta" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_leading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Leading Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_leading_jet_phi" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_leading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Leading Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_subleading_jet_eta" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_subleading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Subleading Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_subleading_jet_phi" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_subleading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Subleading Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_j1j2_mass" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_j1j2_mass --xmin 0 --xmax 1000 --xlabel "Same sign Dijet Mass (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_j1j2_pt" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_j1j2_pt --xmin 0 --xmax 1000 --xlabel "Same sign Dijet p_{T} (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_j1j2_eta" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_j1j2_eta --xmin -5 --xmax 5 --xlabel "Same sign Dijet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_j1j2_phi" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Dijet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_l1j1j2_mass" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_l1j1j2_mass --xmin 0 --xmax 2000 --xlabel "Same sign m(l1jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_l1j1j2_pt" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_l1j1j2_pt --xmin 0 --xmax 1000 --xlabel "Same sign p_{T}(l1jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_l1j1j2_eta" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_l1j1j2_eta --xmin -5 --xmax 5 --xlabel "Same sign #eta(l1jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_l1j1j2_phi" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_l1j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign #phi(l1jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_l2j1j2_mass" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_l2j1j2_mass --xmin 0 --xmax 2000 --xlabel "Same sign m(l2jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_l2j1j2_pt" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_l2j1j2_pt --xmin 0 --xmax 1000 --xlabel "Same sign p_{T}(l2jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_l2j1j2_eta" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_l2j1j2_eta --xmin -5 --xmax 5 --xlabel "Same sign #eta(l2jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_l2j1j2_phi" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_l2j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign #phi(l2jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_mlljj_pt" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_mlljj_pt --xmin 0 --xmax 1000 --xlabel "Same sign WR p_{T} (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_mlljj_eta" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_mlljj_eta --xmin -5 --xmax 5 --xlabel "Same sign WR #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_mlljj_phi" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_mlljj_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign WR #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_leading_lep_eta" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Leading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_leading_lep_phi" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Leading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_subleading_lep_eta" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Subleading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_subleading_lep_phi" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Subleading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_jetnum" --ymin 1 --ymax 1e8 --output ResolveDYMM_SS_jetnum --xmin 0 --xmax 5 --xlabel "Same sign Number of Jets" --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_SS_pvgood" --ymin 1 --ymax 1e4 --output ResolveDYMM_SS_punum --xmin 0 --xmax 80 --xlabel "Same sign Number of Pileup Vertices" --rebin 2 --rmin 0.7 --rmax 1.3


## other sign 

python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Other sign Dilepton p_{T} (GeV)" --rmin 0 --rmax 2.0 --rebin 5
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_leading_jet_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_leading_jet_pt --xmin 0 --xmax 2000 --xlabel "Other sign Leading Jet p_{T} (GeV)" --rebin 10 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_subleading_jet_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_subleading_jet_pt --xmin 0 --xmax 500 --xlabel "Other sign Subleading Jet p_{T} (GeV)" --rebin 2 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_mlljj" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_mlljj --xmin 800 --xmax 4000 --xlabel "Other sign m(lljj) (GeV)" --rebin 20 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_leading_lep_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Other sign Leading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_subleading_lep_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_subleading_lep_pt --xmin 0 --xmax 1000 --xlabel "Other sign Subleading Lepton p_{T} (GeV)" --rebin 10 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_mass" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_dilepton_mass --xmin 0 --xmax 200 --xlabel "Other sign m(ll) (GeV)" --rebin 10 --rmin 0 --rmax 2.0

python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Other sign Dilepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Dilepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_leading_jet_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_leading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Leading Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_leading_jet_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_leading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Leading Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_subleading_jet_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_subleading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Subleading Jet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_subleading_jet_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_subleading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Subleading Jet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_j1j2_mass" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_j1j2_mass --xmin 0 --xmax 1000 --xlabel "Other sign Dijet Mass (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_j1j2_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_j1j2_pt --xmin 0 --xmax 1000 --xlabel "Other sign Dijet p_{T} (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_j1j2_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_j1j2_eta --xmin -5 --xmax 5 --xlabel "Other sign Dijet #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_j1j2_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Dijet #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_l1j1j2_mass" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_l1j1j2_mass --xmin 0 --xmax 2000 --xlabel "Other sign m(l1jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_l1j1j2_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_l1j1j2_pt --xmin 0 --xmax 1000 --xlabel "Other sign p_{T}(l1jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_l1j1j2_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_l1j1j2_eta --xmin -5 --xmax 5 --xlabel "Other sign #eta(l1jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_l1j1j2_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_l1j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign #phi(l1jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_l2j1j2_mass" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_l2j1j2_mass --xmin 0 --xmax 2000 --xlabel "Other sign m(l2jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_l2j1j2_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_l2j1j2_pt --xmin 0 --xmax 1000 --xlabel "Other sign p_{T}(l2jj) (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_l2j1j2_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_l2j1j2_eta --xmin -5 --xmax 5 --xlabel "Other sign #eta(l2jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_l2j1j2_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_l2j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign #phi(l2jj)" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_mlljj_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_mlljj_pt --xmin 0 --xmax 1000 --xlabel "Other sign WR p_{T} (GeV)" --rebin 5 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_mlljj_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_mlljj_eta --xmin -5 --xmax 5 --xlabel "Other sign WR #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_mlljj_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_mlljj_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign WR #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_leading_lep_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Leading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_leading_lep_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Leading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_subleading_lep_eta" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Subleading Lepton #eta" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_subleading_lep_phi" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Subleading Lepton #phi" --rebin 2 --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_jetnum" --ymin 1 --ymax 1e8 --output ResolveDYMM_OS_jetnum --xmin 0 --xmax 5 --xlabel "Other sign Number of Jets" --rmin 0.7 --rmax 1.3
python MM.py  --hist "Obj_PU_Corr_DYCR_Resolved_MM_OS_pvgood" --ymin 1 --ymax 1e6 --output ResolveDYMM_OS_punum --xmin 0 --xmax 80 --xlabel "Other sign Number of Pileup Vertices" --rebin 2 --rmin 0.7 --rmax 1.3
