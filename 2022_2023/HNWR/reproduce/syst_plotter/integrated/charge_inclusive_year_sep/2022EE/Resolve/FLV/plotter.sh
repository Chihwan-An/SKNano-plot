#!/usr/bin/env bash
DIR="$(cd "$(dirname "$0")" && pwd)"
# Resolved Flavor CR - EM

python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_ll_pt" --ymin 1 --ymax 1e5 --output ResolveFLVEM_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Dilepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_leading_jet_pt" --ymin 1 --ymax 1e5 --output ResolveFLVEM_leading_jet_pt --xmin 0 --xmax 2000 --xlabel "Leading Jet p_{T} (GeV)"  --rmin 0 --rmax 2.0 --rebin 50
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_subleading_jet_pt" --ymin 1 --ymax 1e5 --output ResolveFLVEM_subleading_jet_pt --xmin 0 --xmax 500 --xlabel "Subleading Jet p_{T} (GeV)" --rmin 0 --rmax 2.0 --rebin 20
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_mlljj" --ymin 1 --ymax 1e5 --output ResolveFLVEM_mlljj --xmin 800 --xmax 4000 --xlabel "m(lljj) (GeV)"  --rmin 0 --rmax 2.0 --rebin 100
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_leading_lep_pt" --ymin 1 --ymax 1e5 --output ResolveFLVEM_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)"  --rmin 0 --rmax 2.0 --rebin 50
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_subleading_lep_pt" --ymin 1 --ymax 1e5 --output ResolveFLVEM_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Subleading Lepton p_{T} (GeV)" --rmin 0 --rmax 2.0 --rebin 20 
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_mass" --ymin 1 --ymax 1e5 --output ResolveFLVEM_dilepton_mass --xmin 300 --xmax 800 --xlabel "m(ll) (GeV)" --rebin 1 --rmin 0 --rmax 2.0 

python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_dilepton_eta --xmin -5 --xmax 5 --xlabel "Dilepton #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Dilepton #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_leading_jet_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_leading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Leading Jet #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_leading_jet_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_leading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Leading Jet #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_subleading_jet_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_subleading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Subleading Jet #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_subleading_jet_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_subleading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Jet #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_j1j2_mass" --ymin 1 --ymax 1e4 --output ResolveFLVEM_j1j2_mass --xmin 0 --xmax 1000 --xlabel "Dijet Mass (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_j1j2_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_j1j2_pt --xmin 0 --xmax 1000 --xlabel "Dijet p_{T} (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_j1j2_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_j1j2_eta --xmin -5 --xmax 5 --xlabel "Dijet #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_j1j2_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Dijet #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_l1j1j2_mass" --ymin 1 --ymax 1e4 --output ResolveFLVEM_l1j1j2_mass --xmin 800 --xmax 8000 --xlabel "m(l1jj) (GeV)" --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_l1j1j2_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_l1j1j2_pt --xmin 0 --xmax 1000 --xlabel "p_{T}(l1jj) (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_l1j1j2_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_l1j1j2_eta --xmin -5 --xmax 5 --xlabel "#eta(l1jj)" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_l1j1j2_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_l1j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "#phi(l1jj)" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_l2j1j2_mass" --ymin 1 --ymax 1e4 --output ResolveFLVEM_l2j1j2_mass --xmin 800 --xmax 8000 --xlabel "m(l2jj) (GeV)" --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_l2j1j2_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_l2j1j2_pt --xmin 0 --xmax 1000 --xlabel "p_{T}(l2jj) (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_l2j1j2_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_l2j1j2_eta --xmin -5 --xmax 5 --xlabel "#eta(l2jj)" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_l2j1j2_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_l2j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "#phi(l2jj)" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_mlljj_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_mlljj_pt --xmin 0 --xmax 800 --xlabel "WR p_{T} (GeV)"  --rmin 0 --rmax 2.5 --rebin 10 
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_mlljj_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_mlljj_eta --xmin -5 --xmax 5 --xlabel "WR #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_mlljj_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_mlljj_phi --xmin -3.14 --xmax 3.14 --xlabel "WR #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_leading_lep_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Leading Lepton #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_leading_lep_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Leading Lepton #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_subleading_lep_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Subleading Lepton #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_subleading_lep_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Lepton #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_jetnum" --ymin 1 --ymax 1e6 --output ResolveFLVEM_jetnum --xmin 0 --xmax 5 --xlabel "Number of Jets" --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_pvgood" --ymin 1 --ymax 1e4 --output ResolveFLVEM_punum --xmin 0 --xmax 80 --xlabel "Number of Pileup Vertices" --rebin 2 --rmin 0 --rmax 2.5


## Same sign 
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_SS_ll_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Same sign Dilepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_SS_leading_jet_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_leading_jet_pt --xmin 0 --xmax 2000 --xlabel "Same sign Leading Jet p_{T} (GeV)"  --rmin 0 --rmax 2.0 --rebin 50
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_SS_subleading_jet_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_subleading_jet_pt --xmin 0 --xmax 500 --xlabel "Same sign Subleading Jet p_{T} (GeV)" --rmin 0 --rmax 2.0 --rebin 20
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_SS_mlljj" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_mlljj --xmin 800 --xmax 4000 --xlabel "Same sign m(lljj) (GeV)"  --rmin 0 --rmax 2.0 --rebin 100
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_SS_leading_lep_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Same sign Leading Lepton p_{T} (GeV)"  --rmin 0 --rmax 2.0 --rebin 50
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_SS_subleading_lep_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Same sign Subleading Lepton p_{T} (GeV)" --rmin 0 --rmax 2.0 --rebin 20 
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_SS_mass" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_dilepton_mass --xmin 300 --xmax 800 --xlabel "Same sign m(ll) (GeV)" --rebin 1 --rmin 0 --rmax 2.0 

python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Same sign Dilepton #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Dilepton #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_leading_jet_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_leading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Leading Jet #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_leading_jet_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_leading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Leading Jet #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_subleading_jet_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_subleading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Subleading Jet #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_subleading_jet_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_subleading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Subleading Jet #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_j1j2_mass" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_j1j2_mass --xmin 0 --xmax 1000 --xlabel "Same sign Dijet Mass (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_j1j2_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_j1j2_pt --xmin 0 --xmax 1000 --xlabel "Same sign Dijet p_{T} (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_j1j2_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_j1j2_eta --xmin -5 --xmax 5 --xlabel "Same sign Dijet #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_j1j2_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Dijet #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_l1j1j2_mass" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_l1j1j2_mass --xmin 800 --xmax 8000 --xlabel "Same sign m(l1jj) (GeV)" --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_l1j1j2_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_l1j1j2_pt --xmin 0 --xmax 1000 --xlabel "Same sign p_{T}(l1jj) (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_l1j1j2_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_l1j1j2_eta --xmin -5 --xmax 5 --xlabel "Same sign #eta(l1jj)" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_l1j1j2_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_l1j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign #phi(l1jj)" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_l2j1j2_mass" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_l2j1j2_mass --xmin 800 --xmax 8000 --xlabel "Same sign m(l2jj) (GeV)" --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_l2j1j2_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_l2j1j2_pt --xmin 0 --xmax 1000 --xlabel "Same sign p_{T}(l2jj) (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_l2j1j2_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_l2j1j2_eta --xmin -5 --xmax 5 --xlabel "Same sign #eta(l2jj)" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_l2j1j2_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_l2j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign #phi(l2jj)" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_mlljj_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_mlljj_pt --xmin 0 --xmax 800 --xlabel "Same sign WR p_{T} (GeV)"  --rmin 0 --rmax 2.5 --rebin 10 
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_mlljj_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_mlljj_eta --xmin -5 --xmax 5 --xlabel "Same sign WR #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_mlljj_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_mlljj_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign WR #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_leading_lep_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Leading Lepton #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_leading_lep_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Leading Lepton #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_subleading_lep_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Same sign Subleading Lepton #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_subleading_lep_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Same sign Subleading Lepton #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_jetnum" --ymin 1 --ymax 1e6 --output ResolveFLVEM_SS_jetnum --xmin 0 --xmax 5 --xlabel "Same sign Number of Jets" --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_SS_pvgood" --ymin 1 --ymax 1e4 --output ResolveFLVEM_SS_punum --xmin 0 --xmax 80 --xlabel "Same sign Number of Pileup Vertices" --rebin 2 --rmin 0 --rmax 2.5



## other sign 

python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_OS_ll_pt" --ymin 1 --ymax 1e5 --output ResolveFLVEM_OS_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Other sign Dilepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_OS_leading_jet_pt" --ymin 1 --ymax 1e5 --output ResolveFLVEM_OS_leading_jet_pt --xmin 0 --xmax 2000 --xlabel "Other sign Leading Jet p_{T} (GeV)"  --rmin 0 --rmax 2.0 --rebin 50
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_OS_subleading_jet_pt" --ymin 1 --ymax 1e5 --output ResolveFLVEM_OS_subleading_jet_pt --xmin 0 --xmax 500 --xlabel "Other sign Subleading Jet p_{T} (GeV)" --rmin 0 --rmax 2.0 --rebin 20
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_OS_mlljj" --ymin 1 --ymax 1e5 --output ResolveFLVEM_OS_mlljj --xmin 800 --xmax 4000 --xlabel "Other sign m(lljj) (GeV)"  --rmin 0 --rmax 2.0 --rebin 100
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_OS_leading_lep_pt" --ymin 1 --ymax 1e5 --output ResolveFLVEM_OS_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Other sign Leading Lepton p_{T} (GeV)"  --rmin 0 --rmax 2.0 --rebin 50
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_OS_subleading_lep_pt" --ymin 1 --ymax 1e5 --output ResolveFLVEM_OS_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Other sign Subleading Lepton p_{T} (GeV)" --rmin 0 --rmax 2.0 --rebin 20 
python "$DIR/MM.py" --ymin 1 --hist "FlavCR_Resolved_EM_OS_mass" --ymin 1 --ymax 1e5 --output ResolveFLVEM_OS_dilepton_mass --xmin 300 --xmax 800 --xlabel "Other sign m(ll) (GeV)" --rebin 1 --rmin 0 --rmax 2.0 

python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_dilepton_eta --xmin -5 --xmax 5 --xlabel "Other sign Dilepton #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_dilepton_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Dilepton #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_leading_jet_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_leading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Leading Jet #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_leading_jet_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_leading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Leading Jet #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_subleading_jet_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_subleading_jet_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Subleading Jet #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_subleading_jet_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_subleading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Subleading Jet #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_j1j2_mass" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_j1j2_mass --xmin 0 --xmax 1000 --xlabel "Other sign Dijet Mass (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_j1j2_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_j1j2_pt --xmin 0 --xmax 1000 --xlabel "Other sign Dijet p_{T} (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_j1j2_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_j1j2_eta --xmin -5 --xmax 5 --xlabel "Other sign Dijet #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_j1j2_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Dijet #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_l1j1j2_mass" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_l1j1j2_mass --xmin 800 --xmax 8000 --xlabel "Other sign m(l1jj) (GeV)" --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_l1j1j2_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_l1j1j2_pt --xmin 0 --xmax 1000 --xlabel "Other sign p_{T}(l1jj) (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_l1j1j2_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_l1j1j2_eta --xmin -5 --xmax 5 --xlabel "Other sign #eta(l1jj)" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_l1j1j2_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_l1j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign #phi(l1jj)" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_l2j1j2_mass" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_l2j1j2_mass --xmin 800 --xmax 8000 --xlabel "Other sign m(l2jj) (GeV)" --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_l2j1j2_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_l2j1j2_pt --xmin 0 --xmax 1000 --xlabel "Other sign p_{T}(l2jj) (GeV)" --rebin 5 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_l2j1j2_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_l2j1j2_eta --xmin -5 --xmax 5 --xlabel "Other sign #eta(l2jj)" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_l2j1j2_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_l2j1j2_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign #phi(l2jj)" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_mlljj_pt" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_mlljj_pt --xmin 0 --xmax 800 --xlabel "Other sign WR p_{T} (GeV)"  --rmin 0 --rmax 2.5 --rebin 10 
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_mlljj_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_mlljj_eta --xmin -5 --xmax 5 --xlabel "Other sign WR #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_mlljj_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_mlljj_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign WR #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_leading_lep_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_leading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Leading Lepton #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_leading_lep_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_leading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Leading Lepton #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_subleading_lep_eta" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_subleading_lep_eta --xmin -2.5 --xmax 2.5 --xlabel "Other sign Subleading Lepton #eta" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_subleading_lep_phi" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Other sign Subleading Lepton #phi" --rebin 2 --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_jetnum" --ymin 1 --ymax 1e6 --output ResolveFLVEM_OS_jetnum --xmin 0 --xmax 5 --xlabel "Other sign Number of Jets" --rmin 0 --rmax 2.5
python "$DIR/MM.py"  --hist "FlavCR_Resolved_EM_OS_pvgood" --ymin 1 --ymax 1e4 --output ResolveFLVEM_OS_punum --xmin 0 --xmax 80 --xlabel "Other sign Number of Pileup Vertices" --rebin 2 --rmin 0 --rmax 2.5

