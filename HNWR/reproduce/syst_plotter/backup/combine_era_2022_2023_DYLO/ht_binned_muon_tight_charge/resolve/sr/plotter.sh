#!/usr/bin/env bash
# Resolved SR - MM tight charge
# Pattern 1: Obj_PU_Corr_SR_Resolved_MM_SS_{tight/not_tight}_*  (filled by SS_tight flag)
# Pattern 2: Obj_PU_Corr_SR_ResolvedMM_SS_{tight/not_tight}_*   (filled by OS_tight flag, named SS by mistake)

for TC in tight not_tight; do
TAG="SS_${TC}"

# --- Pattern 1: Resolved_MM ---
PRE1="Obj_PU_Corr_SR_Resolved_MM_${TAG}"
OUT1="ResolveSRMM_${TAG}"

python MM.py --signal-scale 1.0 --hist "${PRE1}_ll_pt"              --ymin 1 --ymax 1e6 --output ${OUT1}_dilepton_pt         --xmin 0     --xmax 1000  --xlabel "Dilepton p_{T} (GeV)"        --rebin 50  --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "${PRE1}_leading_jet_pt"     --ymin 1 --ymax 1e6 --output ${OUT1}_leading_jet_pt      --xmin 0     --xmax 2000  --xlabel "Leading Jet p_{T} (GeV)"      --rebin 50  --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "${PRE1}_subleading_jet_pt"  --ymin 1 --ymax 1e6 --output ${OUT1}_subleading_jet_pt   --xmin 0     --xmax 2000  --xlabel "Subleading Jet p_{T} (GeV)"   --rebin 50  --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "${PRE1}_mlljj"              --ymin 1 --ymax 1e6 --output ${OUT1}_mlljj               --xmin 800   --xmax 4000  --xlabel "m(lljj) (GeV)"                --rebin 100 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "${PRE1}_leading_lep_pt"     --ymin 1 --ymax 1e6 --output ${OUT1}_leading_lep_pt      --xmin 0     --xmax 1000  --xlabel "Leading Lepton p_{T} (GeV)"   --rebin 50  --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "${PRE1}_subleading_lep_pt"  --ymin 1 --ymax 1e6 --output ${OUT1}_subleading_lep_pt   --xmin 0     --xmax 1000  --xlabel "Subleading Lepton p_{T} (GeV)"--rebin 50  --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "${PRE1}_mass"               --ymin 1 --ymax 1e6 --output ${OUT1}_dilepton_mass       --xmin 0     --xmax 2000  --xlabel "m(ll) (GeV)"                  --rebin 5   --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "${PRE1}_eta"                --ymin 1e-1 --ymax 1e6 --output ${OUT1}_dilepton_eta     --xmin -5    --xmax 5     --xlabel "Dilepton #eta"                 --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_phi"                --ymin 1e-1 --ymax 1e6 --output ${OUT1}_dilepton_phi     --xmin -3.14 --xmax 3.14  --xlabel "Dilepton #phi"                 --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_leading_jet_eta"    --ymin 1e-1 --ymax 1e6 --output ${OUT1}_leading_jet_eta  --xmin -2.5  --xmax 2.5   --xlabel "Leading Jet #eta"              --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_leading_jet_phi"    --ymin 1e-1 --ymax 1e6 --output ${OUT1}_leading_jet_phi  --xmin -3.14 --xmax 3.14  --xlabel "Leading Jet #phi"              --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_subleading_jet_eta" --ymin 1e-1 --ymax 1e6 --output ${OUT1}_subleading_jet_eta --xmin -2.5 --xmax 2.5  --xlabel "Subleading Jet #eta"           --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_subleading_jet_phi" --ymin 1e-1 --ymax 1e6 --output ${OUT1}_subleading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Jet #phi"          --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_j1j2_mass"          --ymin 1e-1 --ymax 1e6 --output ${OUT1}_j1j2_mass        --xmin 0     --xmax 1000  --xlabel "Dijet Mass (GeV)"              --rebin 5   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_j1j2_pt"            --ymin 1e-1 --ymax 1e6 --output ${OUT1}_j1j2_pt          --xmin 0     --xmax 1000  --xlabel "Dijet p_{T} (GeV)"             --rebin 5   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_j1j2_eta"           --ymin 1e-1 --ymax 1e6 --output ${OUT1}_j1j2_eta         --xmin -5    --xmax 5     --xlabel "Dijet #eta"                    --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_j1j2_phi"           --ymin 1e-1 --ymax 1e6 --output ${OUT1}_j1j2_phi         --xmin -3.14 --xmax 3.14  --xlabel "Dijet #phi"                    --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_l1j1j2_mass"        --ymin 1e-1 --ymax 1e6 --output ${OUT1}_l1j1j2_mass      --xmin 800   --xmax 8000  --xlabel "m(l1jj) (GeV)"  --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_l1j1j2_pt"          --ymin 1e-1 --ymax 1e6 --output ${OUT1}_l1j1j2_pt        --xmin 0     --xmax 2000  --xlabel "p_{T}(l1jj) (GeV)"            --rebin 5   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_l1j1j2_eta"         --ymin 1e-1 --ymax 1e6 --output ${OUT1}_l1j1j2_eta       --xmin -5    --xmax 5     --xlabel "#eta(l1jj)"                    --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_l1j1j2_phi"         --ymin 1e-1 --ymax 1e6 --output ${OUT1}_l1j1j2_phi       --xmin -3.14 --xmax 3.14  --xlabel "#phi(l1jj)"                    --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_l2j1j2_mass"        --ymin 1e-1 --ymax 1e6 --output ${OUT1}_l2j1j2_mass      --xmin 800   --xmax 8000  --xlabel "m(l2jj) (GeV)"  --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_l2j1j2_pt"          --ymin 1e-1 --ymax 1e6 --output ${OUT1}_l2j1j2_pt        --xmin 0     --xmax 2000  --xlabel "p_{T}(l2jj) (GeV)"            --rebin 5   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_l2j1j2_eta"         --ymin 1e-1 --ymax 1e6 --output ${OUT1}_l2j1j2_eta       --xmin -5    --xmax 5     --xlabel "#eta(l2jj)"                    --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_l2j1j2_phi"         --ymin 1e-1 --ymax 1e6 --output ${OUT1}_l2j1j2_phi       --xmin -3.14 --xmax 3.14  --xlabel "#phi(l2jj)"                    --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_mlljj_pt"           --ymin 1e-1 --ymax 1e6 --output ${OUT1}_mlljj_pt         --xmin 0     --xmax 8000  --xlabel "WR p_{T} (GeV)"               --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_mlljj_eta"          --ymin 1e-1 --ymax 1e6 --output ${OUT1}_mlljj_eta        --xmin -5    --xmax 5     --xlabel "WR #eta"                       --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_mlljj_phi"          --ymin 1e-1 --ymax 1e6 --output ${OUT1}_mlljj_phi        --xmin -3.14 --xmax 3.14  --xlabel "WR #phi"                       --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_leading_lep_eta"    --ymin 1e-1 --ymax 1e6 --output ${OUT1}_leading_lep_eta  --xmin -2.5  --xmax 2.5   --xlabel "Leading Lepton #eta"           --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_leading_lep_phi"    --ymin 1e-1 --ymax 1e6 --output ${OUT1}_leading_lep_phi  --xmin -3.14 --xmax 3.14  --xlabel "Leading Lepton #phi"           --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_subleading_lep_eta" --ymin 1e-1 --ymax 1e6 --output ${OUT1}_subleading_lep_eta --xmin -2.5 --xmax 2.5  --xlabel "Subleading Lepton #eta"        --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_subleading_lep_phi" --ymin 1e-1 --ymax 1e6 --output ${OUT1}_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Lepton #phi"       --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_jetnum"             --ymin 1e-1 --ymax 1e5 --output ${OUT1}_jetnum           --xmin 0     --xmax 5     --xlabel "Number of Jets"                            --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE1}_pvgood"             --ymin 1e-1 --ymax 1e6 --output ${OUT1}_punum            --xmin 0     --xmax 80    --xlabel "Number of Pileup Vertices"     --rebin 2   --rmin 0.7 --rmax 1.3

# --- Pattern 2: ResolvedMM (OS_tight flag, named SS in histogram by mistake) ---
PRE2="Obj_PU_Corr_SR_ResolvedMM_${TAG}"
OUT2="ResolveSRMMv2_${TAG}"

python MM.py --signal-scale 1.0 --hist "${PRE2}_ll_pt"              --ymin 1 --ymax 1e6 --output ${OUT2}_dilepton_pt         --xmin 0     --xmax 1000  --xlabel "Dilepton p_{T} (GeV)"        --rebin 50  --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "${PRE2}_leading_jet_pt"     --ymin 1 --ymax 1e6 --output ${OUT2}_leading_jet_pt      --xmin 0     --xmax 2000  --xlabel "Leading Jet p_{T} (GeV)"      --rebin 50  --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "${PRE2}_subleading_jet_pt"  --ymin 1 --ymax 1e6 --output ${OUT2}_subleading_jet_pt   --xmin 0     --xmax 2000  --xlabel "Subleading Jet p_{T} (GeV)"   --rebin 50  --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "${PRE2}_mlljj"              --ymin 1 --ymax 1e6 --output ${OUT2}_mlljj               --xmin 800   --xmax 4000  --xlabel "m(lljj) (GeV)"                --rebin 100 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "${PRE2}_leading_lep_pt"     --ymin 1 --ymax 1e6 --output ${OUT2}_leading_lep_pt      --xmin 0     --xmax 1000  --xlabel "Leading Lepton p_{T} (GeV)"   --rebin 50  --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "${PRE2}_subleading_lep_pt"  --ymin 1 --ymax 1e6 --output ${OUT2}_subleading_lep_pt   --xmin 0     --xmax 1000  --xlabel "Subleading Lepton p_{T} (GeV)"--rebin 50  --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "${PRE2}_mass"               --ymin 1 --ymax 1e6 --output ${OUT2}_dilepton_mass       --xmin 0     --xmax 2000  --xlabel "m(ll) (GeV)"                  --rebin 5   --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "${PRE2}_eta"                --ymin 1e-1 --ymax 1e6 --output ${OUT2}_dilepton_eta     --xmin -5    --xmax 5     --xlabel "Dilepton #eta"                 --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_phi"                --ymin 1e-1 --ymax 1e6 --output ${OUT2}_dilepton_phi     --xmin -3.14 --xmax 3.14  --xlabel "Dilepton #phi"                 --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_leading_jet_eta"    --ymin 1e-1 --ymax 1e6 --output ${OUT2}_leading_jet_eta  --xmin -2.5  --xmax 2.5   --xlabel "Leading Jet #eta"              --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_leading_jet_phi"    --ymin 1e-1 --ymax 1e6 --output ${OUT2}_leading_jet_phi  --xmin -3.14 --xmax 3.14  --xlabel "Leading Jet #phi"              --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_subleading_jet_eta" --ymin 1e-1 --ymax 1e6 --output ${OUT2}_subleading_jet_eta --xmin -2.5 --xmax 2.5  --xlabel "Subleading Jet #eta"           --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_subleading_jet_phi" --ymin 1e-1 --ymax 1e6 --output ${OUT2}_subleading_jet_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Jet #phi"          --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_j1j2_mass"          --ymin 1e-1 --ymax 1e6 --output ${OUT2}_j1j2_mass        --xmin 0     --xmax 1000  --xlabel "Dijet Mass (GeV)"              --rebin 5   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_j1j2_pt"            --ymin 1e-1 --ymax 1e6 --output ${OUT2}_j1j2_pt          --xmin 0     --xmax 1000  --xlabel "Dijet p_{T} (GeV)"             --rebin 5   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_j1j2_eta"           --ymin 1e-1 --ymax 1e6 --output ${OUT2}_j1j2_eta         --xmin -5    --xmax 5     --xlabel "Dijet #eta"                    --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_j1j2_phi"           --ymin 1e-1 --ymax 1e6 --output ${OUT2}_j1j2_phi         --xmin -3.14 --xmax 3.14  --xlabel "Dijet #phi"                    --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_l1j1j2_mass"        --ymin 1e-1 --ymax 1e6 --output ${OUT2}_l1j1j2_mass      --xmin 800   --xmax 8000  --xlabel "m(l1jj) (GeV)"  --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_l1j1j2_pt"          --ymin 1e-1 --ymax 1e6 --output ${OUT2}_l1j1j2_pt        --xmin 0     --xmax 2000  --xlabel "p_{T}(l1jj) (GeV)"            --rebin 5   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_l1j1j2_eta"         --ymin 1e-1 --ymax 1e6 --output ${OUT2}_l1j1j2_eta       --xmin -5    --xmax 5     --xlabel "#eta(l1jj)"                    --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_l1j1j2_phi"         --ymin 1e-1 --ymax 1e6 --output ${OUT2}_l1j1j2_phi       --xmin -3.14 --xmax 3.14  --xlabel "#phi(l1jj)"                    --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_l2j1j2_mass"        --ymin 1e-1 --ymax 1e6 --output ${OUT2}_l2j1j2_mass      --xmin 800   --xmax 8000  --xlabel "m(l2jj) (GeV)"  --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_l2j1j2_pt"          --ymin 1e-1 --ymax 1e6 --output ${OUT2}_l2j1j2_pt        --xmin 0     --xmax 2000  --xlabel "p_{T}(l2jj) (GeV)"            --rebin 5   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_l2j1j2_eta"         --ymin 1e-1 --ymax 1e6 --output ${OUT2}_l2j1j2_eta       --xmin -5    --xmax 5     --xlabel "#eta(l2jj)"                    --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_l2j1j2_phi"         --ymin 1e-1 --ymax 1e6 --output ${OUT2}_l2j1j2_phi       --xmin -3.14 --xmax 3.14  --xlabel "#phi(l2jj)"                    --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_mlljj_pt"           --ymin 1e-1 --ymax 1e6 --output ${OUT2}_mlljj_pt         --xmin 0     --xmax 8000  --xlabel "WR p_{T} (GeV)"               --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_mlljj_eta"          --ymin 1e-1 --ymax 1e6 --output ${OUT2}_mlljj_eta        --xmin -5    --xmax 5     --xlabel "WR #eta"                       --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_mlljj_phi"          --ymin 1e-1 --ymax 1e6 --output ${OUT2}_mlljj_phi        --xmin -3.14 --xmax 3.14  --xlabel "WR #phi"                       --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_leading_lep_eta"    --ymin 1e-1 --ymax 1e6 --output ${OUT2}_leading_lep_eta  --xmin -2.5  --xmax 2.5   --xlabel "Leading Lepton #eta"           --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_leading_lep_phi"    --ymin 1e-1 --ymax 1e6 --output ${OUT2}_leading_lep_phi  --xmin -3.14 --xmax 3.14  --xlabel "Leading Lepton #phi"           --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_subleading_lep_eta" --ymin 1e-1 --ymax 1e6 --output ${OUT2}_subleading_lep_eta --xmin -2.5 --xmax 2.5  --xlabel "Subleading Lepton #eta"        --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_subleading_lep_phi" --ymin 1e-1 --ymax 1e6 --output ${OUT2}_subleading_lep_phi --xmin -3.14 --xmax 3.14 --xlabel "Subleading Lepton #phi"       --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_jetnum"             --ymin 1e-1 --ymax 1e5 --output ${OUT2}_jetnum           --xmin 0     --xmax 5     --xlabel "Number of Jets"                            --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "${PRE2}_pvgood"             --ymin 1e-1 --ymax 1e6 --output ${OUT2}_punum            --xmin 0     --xmax 80    --xlabel "Number of Pileup Vertices"     --rebin 2   --rmin 0.7 --rmax 1.3

done
