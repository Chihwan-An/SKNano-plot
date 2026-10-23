#!/usr/bin/env bash
# Resolved DY CR - both tight charge
# MM: OS/SS × tight/not_tight  (both muons tight)
# EE: OS/SS × 2e_tight/1e_tight/0e_tight  (electron tight count)

# ─── MM ───────────────────────────────────────────────────────────────────────
for SIGN in OS SS; do
for TC in tight not_tight; do
TAG="${SIGN}_${TC}"
PRE="Obj_PU_Corr_DYCR_Resolved_MM_${TAG}"
OUT="ResolveDYMM_${TAG}"

python MM.py --hist "${PRE}_pt"                    --ymin 1 --ymax 1e6 --output ${OUT}_dilepton_pt          --xmin 0     --xmax 1000  --xlabel "Dilepton p_{T} (GeV)"        --rebin 5  --rmin 0 --rmax 2.0
python MM.py --hist "${PRE}_leading_jet_pt"        --ymin 1 --ymax 1e6 --output ${OUT}_leading_jet_pt       --xmin 0     --xmax 2000  --xlabel "Leading Jet p_{T} (GeV)"      --rebin 10 --rmin 0 --rmax 2.0
python MM.py --hist "${PRE}_subleading_jet_pt"     --ymin 1 --ymax 1e6 --output ${OUT}_subleading_jet_pt    --xmin 0     --xmax 500   --xlabel "Subleading Jet p_{T} (GeV)"   --rebin 2  --rmin 0 --rmax 2.0
python MM.py --hist "${PRE}_mlljj"                 --ymin 1 --ymax 1e6 --output ${OUT}_mlljj                --xmin 800   --xmax 4000  --xlabel "m(lljj) (GeV)"                --rebin 20 --rmin 0 --rmax 2.0
python MM.py --hist "${PRE}_leading_lep_pt"        --ymin 1 --ymax 1e6 --output ${OUT}_leading_lep_pt       --xmin 0     --xmax 1000  --xlabel "Leading Lepton p_{T} (GeV)"   --rebin 50 --rmin 0 --rmax 2.0
python MM.py --hist "${PRE}_subleading_lep_pt"     --ymin 1 --ymax 1e6 --output ${OUT}_subleading_lep_pt    --xmin 0     --xmax 1000  --xlabel "Subleading Lepton p_{T} (GeV)"--rebin 10 --rmin 0 --rmax 2.0
python MM.py --hist "${PRE}_mass"                  --ymin 1 --ymax 1e6 --output ${OUT}_dilepton_mass        --xmin 0     --xmax 200   --xlabel "m(ll) (GeV)"                  --rebin 10 --rmin 0 --rmax 2.0
python MM.py --hist "${PRE}_eta"                   --ymin 1 --ymax 1e6 --output ${OUT}_dilepton_eta         --xmin -5    --xmax 5     --xlabel "Dilepton #eta"                 --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_phi"                   --ymin 1 --ymax 1e6 --output ${OUT}_dilepton_phi         --xmin -3.14 --xmax 3.14  --xlabel "Dilepton #phi"                 --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_leading_jet_eta"       --ymin 1 --ymax 1e6 --output ${OUT}_leading_jet_eta      --xmin -2.5  --xmax 2.5   --xlabel "Leading Jet #eta"              --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_leading_jet_phi"       --ymin 1 --ymax 1e6 --output ${OUT}_leading_jet_phi      --xmin -3.14 --xmax 3.14  --xlabel "Leading Jet #phi"              --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_subleading_jet_eta"    --ymin 1 --ymax 1e6 --output ${OUT}_subleading_jet_eta   --xmin -2.5  --xmax 2.5   --xlabel "Subleading Jet #eta"           --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_subleading_jet_phi"    --ymin 1 --ymax 1e6 --output ${OUT}_subleading_jet_phi   --xmin -3.14 --xmax 3.14  --xlabel "Subleading Jet #phi"           --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_j1j2_mass"             --ymin 1 --ymax 1e6 --output ${OUT}_j1j2_mass            --xmin 0     --xmax 1000  --xlabel "Dijet Mass (GeV)"              --rebin 5  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_j1j2_pt"               --ymin 1 --ymax 1e6 --output ${OUT}_j1j2_pt              --xmin 0     --xmax 1000  --xlabel "Dijet p_{T} (GeV)"             --rebin 5  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_j1j2_eta"              --ymin 1 --ymax 1e6 --output ${OUT}_j1j2_eta             --xmin -5    --xmax 5     --xlabel "Dijet #eta"                    --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_j1j2_phi"              --ymin 1 --ymax 1e6 --output ${OUT}_j1j2_phi             --xmin -3.14 --xmax 3.14  --xlabel "Dijet #phi"                    --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_l1j1j2_mass"           --ymin 1 --ymax 1e6 --output ${OUT}_l1j1j2_mass          --xmin 0     --xmax 2000  --xlabel "m(l1jj) (GeV)"                --rebin 5  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_l1j1j2_pt"             --ymin 1 --ymax 1e6 --output ${OUT}_l1j1j2_pt            --xmin 0     --xmax 1000  --xlabel "p_{T}(l1jj) (GeV)"            --rebin 5  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_l1j1j2_eta"            --ymin 1 --ymax 1e6 --output ${OUT}_l1j1j2_eta           --xmin -5    --xmax 5     --xlabel "#eta(l1jj)"                    --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_l1j1j2_phi"            --ymin 1 --ymax 1e6 --output ${OUT}_l1j1j2_phi           --xmin -3.14 --xmax 3.14  --xlabel "#phi(l1jj)"                    --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_l2j1j2_mass"           --ymin 1 --ymax 1e6 --output ${OUT}_l2j1j2_mass          --xmin 0     --xmax 2000  --xlabel "m(l2jj) (GeV)"                --rebin 5  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_l2j1j2_pt"             --ymin 1 --ymax 1e6 --output ${OUT}_l2j1j2_pt            --xmin 0     --xmax 1000  --xlabel "p_{T}(l2jj) (GeV)"            --rebin 5  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_l2j1j2_eta"            --ymin 1 --ymax 1e6 --output ${OUT}_l2j1j2_eta           --xmin -5    --xmax 5     --xlabel "#eta(l2jj)"                    --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_l2j1j2_phi"            --ymin 1 --ymax 1e6 --output ${OUT}_l2j1j2_phi           --xmin -3.14 --xmax 3.14  --xlabel "#phi(l2jj)"                    --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_mlljj_pt"              --ymin 1 --ymax 1e6 --output ${OUT}_mlljj_pt             --xmin 0     --xmax 1000  --xlabel "WR p_{T} (GeV)"               --rebin 5  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_mlljj_eta"             --ymin 1 --ymax 1e6 --output ${OUT}_mlljj_eta            --xmin -5    --xmax 5     --xlabel "WR #eta"                       --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_mlljj_phi"             --ymin 1 --ymax 1e6 --output ${OUT}_mlljj_phi            --xmin -3.14 --xmax 3.14  --xlabel "WR #phi"                       --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_leading_lep_eta"       --ymin 1 --ymax 1e6 --output ${OUT}_leading_lep_eta      --xmin -2.5  --xmax 2.5   --xlabel "Leading Lepton #eta"           --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_leading_lep_phi"       --ymin 1 --ymax 1e6 --output ${OUT}_leading_lep_phi      --xmin -3.14 --xmax 3.14  --xlabel "Leading Lepton #phi"           --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_subleading_lep_eta"    --ymin 1 --ymax 1e6 --output ${OUT}_subleading_lep_eta   --xmin -2.5  --xmax 2.5   --xlabel "Subleading Lepton #eta"        --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_subleading_lep_phi"    --ymin 1 --ymax 1e6 --output ${OUT}_subleading_lep_phi   --xmin -3.14 --xmax 3.14  --xlabel "Subleading Lepton #phi"        --rebin 2  --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_jetnum"                --ymin 1 --ymax 1e6 --output ${OUT}_jetnum               --xmin 0     --xmax 5     --xlabel "Number of Jets"                           --rmin 0.7 --rmax 1.3
python MM.py --hist "${PRE}_pvgood"                --ymin 1 --ymax 1e6 --output ${OUT}_punum                --xmin 0     --xmax 80    --xlabel "Number of Pileup Vertices"     --rebin 2  --rmin 0.7 --rmax 1.3

done
done

# ─── EE ───────────────────────────────────────────────────────────────────────
for SIGN in OS SS; do
for NE in 2e_tight 1e_tight 0e_tight; do
TAG="${SIGN}_${NE}"
PRE="Obj_PU_Corr_DYCR_Resolved_EE_${TAG}"
OUT="ResolveDYEE_${TAG}"

python EE.py --hist "${PRE}_pt"                    --ymin 1 --ymax 1e6 --output ${OUT}_dilepton_pt          --xmin 0     --xmax 1000  --xlabel "Dilepton p_{T} (GeV)"        --rebin 5  --rmin 0 --rmax 2.0
python EE.py --hist "${PRE}_leading_jet_pt"        --ymin 1 --ymax 1e6 --output ${OUT}_leading_jet_pt       --xmin 0     --xmax 2000  --xlabel "Leading Jet p_{T} (GeV)"      --rebin 10 --rmin 0 --rmax 2.0
python EE.py --hist "${PRE}_subleading_jet_pt"     --ymin 1 --ymax 1e6 --output ${OUT}_subleading_jet_pt    --xmin 0     --xmax 500   --xlabel "Subleading Jet p_{T} (GeV)"   --rebin 2  --rmin 0 --rmax 2.0
python EE.py --hist "${PRE}_mlljj"                 --ymin 1 --ymax 1e6 --output ${OUT}_mlljj                --xmin 800   --xmax 4000  --xlabel "m(lljj) (GeV)"                --rebin 20 --rmin 0 --rmax 2.0
python EE.py --hist "${PRE}_leading_lep_pt"        --ymin 1 --ymax 1e6 --output ${OUT}_leading_lep_pt       --xmin 0     --xmax 1000  --xlabel "Leading Lepton p_{T} (GeV)"   --rebin 50 --rmin 0 --rmax 2.0
python EE.py --hist "${PRE}_subleading_lep_pt"     --ymin 1 --ymax 1e6 --output ${OUT}_subleading_lep_pt    --xmin 0     --xmax 1000  --xlabel "Subleading Lepton p_{T} (GeV)"--rebin 10 --rmin 0 --rmax 2.0
python EE.py --hist "${PRE}_mass"                  --ymin 1 --ymax 1e6 --output ${OUT}_dilepton_mass        --xmin 0     --xmax 200   --xlabel "m(ll) (GeV)"                  --rebin 1  --rmin 0 --rmax 2.0
python EE.py --hist "${PRE}_eta"                   --ymin 1 --ymax 1e6 --output ${OUT}_dilepton_eta         --xmin -5    --xmax 5     --xlabel "Dilepton #eta"                 --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_phi"                   --ymin 1 --ymax 1e6 --output ${OUT}_dilepton_phi         --xmin -3.14 --xmax 3.14  --xlabel "Dilepton #phi"                 --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_leading_jet_eta"       --ymin 1 --ymax 1e6 --output ${OUT}_leading_jet_eta      --xmin -2.5  --xmax 2.5   --xlabel "Leading Jet #eta"              --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_leading_jet_phi"       --ymin 1 --ymax 1e6 --output ${OUT}_leading_jet_phi      --xmin -3.14 --xmax 3.14  --xlabel "Leading Jet #phi"              --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_subleading_jet_eta"    --ymin 1 --ymax 1e6 --output ${OUT}_subleading_jet_eta   --xmin -2.5  --xmax 2.5   --xlabel "Subleading Jet #eta"           --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_subleading_jet_phi"    --ymin 1 --ymax 1e6 --output ${OUT}_subleading_jet_phi   --xmin -3.14 --xmax 3.14  --xlabel "Subleading Jet #phi"           --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_j1j2_mass"             --ymin 1 --ymax 1e6 --output ${OUT}_j1j2_mass            --xmin 0     --xmax 1000  --xlabel "Dijet Mass (GeV)"              --rebin 5  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_j1j2_pt"               --ymin 1 --ymax 1e6 --output ${OUT}_j1j2_pt              --xmin 0     --xmax 1000  --xlabel "Dijet p_{T} (GeV)"             --rebin 5  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_j1j2_eta"              --ymin 1 --ymax 1e6 --output ${OUT}_j1j2_eta             --xmin -5    --xmax 5     --xlabel "Dijet #eta"                    --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_j1j2_phi"              --ymin 1 --ymax 1e6 --output ${OUT}_j1j2_phi             --xmin -3.14 --xmax 3.14  --xlabel "Dijet #phi"                    --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_l1j1j2_mass"           --ymin 1 --ymax 1e6 --output ${OUT}_l1j1j2_mass          --xmin 0     --xmax 2000  --xlabel "m(l1jj) (GeV)"                --rebin 5  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_l1j1j2_pt"             --ymin 1 --ymax 1e6 --output ${OUT}_l1j1j2_pt            --xmin 0     --xmax 1000  --xlabel "p_{T}(l1jj) (GeV)"            --rebin 5  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_l1j1j2_eta"            --ymin 1 --ymax 1e6 --output ${OUT}_l1j1j2_eta           --xmin -5    --xmax 5     --xlabel "#eta(l1jj)"                    --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_l1j1j2_phi"            --ymin 1 --ymax 1e6 --output ${OUT}_l1j1j2_phi           --xmin -3.14 --xmax 3.14  --xlabel "#phi(l1jj)"                    --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_l2j1j2_mass"           --ymin 1 --ymax 1e6 --output ${OUT}_l2j1j2_mass          --xmin 0     --xmax 2000  --xlabel "m(l2jj) (GeV)"                --rebin 5  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_l2j1j2_pt"             --ymin 1 --ymax 1e6 --output ${OUT}_l2j1j2_pt            --xmin 0     --xmax 1000  --xlabel "p_{T}(l2jj) (GeV)"            --rebin 5  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_l2j1j2_eta"            --ymin 1 --ymax 1e6 --output ${OUT}_l2j1j2_eta           --xmin -5    --xmax 5     --xlabel "#eta(l2jj)"                    --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_l2j1j2_phi"            --ymin 1 --ymax 1e6 --output ${OUT}_l2j1j2_phi           --xmin -3.14 --xmax 3.14  --xlabel "#phi(l2jj)"                    --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_mlljj_pt"              --ymin 1 --ymax 1e6 --output ${OUT}_mlljj_pt             --xmin 0     --xmax 1000  --xlabel "WR p_{T} (GeV)"               --rebin 5  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_mlljj_eta"             --ymin 1 --ymax 1e6 --output ${OUT}_mlljj_eta            --xmin -5    --xmax 5     --xlabel "WR #eta"                       --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_mlljj_phi"             --ymin 1 --ymax 1e6 --output ${OUT}_mlljj_phi            --xmin -3.14 --xmax 3.14  --xlabel "WR #phi"                       --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_leading_lep_eta"       --ymin 1 --ymax 1e6 --output ${OUT}_leading_lep_eta      --xmin -2.5  --xmax 2.5   --xlabel "Leading Lepton #eta"           --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_leading_lep_phi"       --ymin 1 --ymax 1e6 --output ${OUT}_leading_lep_phi      --xmin -3.14 --xmax 3.14  --xlabel "Leading Lepton #phi"           --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_subleading_lep_eta"    --ymin 1 --ymax 1e6 --output ${OUT}_subleading_lep_eta   --xmin -2.5  --xmax 2.5   --xlabel "Subleading Lepton #eta"        --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_subleading_lep_phi"    --ymin 1 --ymax 1e6 --output ${OUT}_subleading_lep_phi   --xmin -3.14 --xmax 3.14  --xlabel "Subleading Lepton #phi"        --rebin 2  --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_jetnum"                --ymin 1 --ymax 1e6 --output ${OUT}_jetnum               --xmin 0     --xmax 5     --xlabel "Number of Jets"                           --rmin 0.7 --rmax 1.3
python EE.py --hist "${PRE}_pvgood"                --ymin 1 --ymax 1e6 --output ${OUT}_punum                --xmin 0     --xmax 80    --xlabel "Number of Pileup Vertices"     --rebin 2  --rmin 0.7 --rmax 1.3

done
done
