#!/usr/bin/env bash
# Boosted SR - MM tight charge

for SIGN in OS SS; do
for TC in tight not_tight; do
TAG="${SIGN}_${TC}"
OUT="BoostSRMM_${TAG}"

python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_eta_mumu_${TAG}"                       --ymin 1e-1 --ymax 1e6 --output ${OUT}_dilepton_eta           --xmin -5    --xmax 5     --xlabel "Dilepton #eta"                      --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_phi_mumu_${TAG}"                       --ymin 1e-1 --ymax 1e6 --output ${OUT}_dilepton_phi           --xmin -3.14 --xmax 3.14  --xlabel "Dilepton #phi"                      --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_eta_mumu_${TAG}"                --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_eta             --xmin -2.4  --xmax 2.4   --xlabel "Fat Jet #eta"                       --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_phi_mumu_${TAG}"                --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_phi             --xmin -3.14 --xmax 3.14  --xlabel "Fat Jet #phi"                       --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_SDM_mumu_${TAG}"                --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_SDM             --xmin 0     --xmax 200   --xlabel "Fat Jet Soft Drop Mass (GeV)"       --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_pt_mumu_${TAG}"                     --ymin 1e-1 --ymax 1e6 --output ${OUT}_WR_pt                 --xmin 0     --xmax 8000  --xlabel "WR p_{T} (GeV)"                    --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_eta_mumu_${TAG}"                    --ymin 1e-1 --ymax 1e6 --output ${OUT}_WR_eta                --xmin -5    --xmax 5     --xlabel "WR #eta"                            --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_WR_phi_mumu_${TAG}"                    --ymin 1e-1 --ymax 1e6 --output ${OUT}_WR_phi                --xmin -3.14 --xmax 3.14  --xlabel "WR #phi"                            --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_lep_eta_mumu_${TAG}"           --ymin 1e-1 --ymax 1e6 --output ${OUT}_leading_lep_eta        --xmin -2.5  --xmax 2.5   --xlabel "Leading Lepton #eta"                --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_lep_phi_mumu_${TAG}"           --ymin 1e-1 --ymax 1e6 --output ${OUT}_leading_lep_phi        --xmin -3.14 --xmax 3.14  --xlabel "Leading Lepton #phi"                --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_subleading_lep_eta_mumu_${TAG}"        --ymin 1e-1 --ymax 1e6 --output ${OUT}_subleading_lep_eta     --xmin -2.5  --xmax 2.5   --xlabel "Subleading Lepton #eta"             --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_subleading_lep_phi_mumu_${TAG}"        --ymin 1e-1 --ymax 1e6 --output ${OUT}_subleading_lep_phi     --xmin -3.14 --xmax 3.14  --xlabel "Subleading Lepton #phi"             --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_fatjet_lsf3_mumu_${TAG}"               --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_lsf3            --xmin 0     --xmax 1     --xlabel "Fat Jet LSF3"                       --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_deltaR_leadlep_fatjet_mumu_${TAG}"     --ymin 1e-1 --ymax 1e6 --output ${OUT}_deltaR_leadlep_fatjet  --xmin 0     --xmax 5     --xlabel "#DeltaR(lead lep, fat jet)"         --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_dphi_leadlep_fatjet_mumu_${TAG}"       --ymin 1e-1 --ymax 1e6 --output ${OUT}_dphi_leadlep_fatjet    --xmin 0     --xmax 3.14  --xlabel "#Delta#phi(lead lep, fat jet)"      --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_pvgood_mumu_${TAG}"                    --ymin 1e-1 --ymax 1e6 --output ${OUT}_punum                 --xmin 0     --xmax 80    --xlabel "Number of Pileup Vertices"          --rebin 2   --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_jetnum_mumu_${TAG}"                    --ymin 1e-1 --ymax 1e6 --output ${OUT}_jetnum                --xmin 0     --xmax 20    --xlabel "Number of Jets"                                 --rmin 0.7 --rmax 1.3
python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_WRMass_mumu_${TAG}"                 --ymin 1    --ymax 1e6 --output ${OUT}_WRMass               --xmin 800   --xmax 4000  --xlabel "m(lljj) (GeV)"                     --rebin 100 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_Dilepton_Pt_mumu_${TAG}"            --ymin 1    --ymax 1e6 --output ${OUT}_Dilepton_pt           --xmin 0     --xmax 1000  --xlabel "p_{T}^{ll} (GeV)"                  --rebin 50  --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_LeadingLepPt_mumu_${TAG}"              --ymin 1    --ymax 1e6 --output ${OUT}_LeadingLepPt          --xmin 0     --xmax 1000  --xlabel "Leading Lepton p_{T} (GeV)"        --rebin 50  --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_SubLeadingLepPt_mumu_${TAG}"           --ymin 1    --ymax 1e6 --output ${OUT}_SubLeadingLepPt       --xmin 0     --xmax 1000  --xlabel "Subleading Lepton p_{T} (GeV)"     --rebin 20  --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_mll_mumu_${TAG}"                       --ymin 1    --ymax 1e6 --output ${OUT}_dilepton_mass         --xmin 0     --xmax 2000  --xlabel "m(ll) (GeV)"                      --rebin 50  --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_fatjet_pt_boosted_mumu_${TAG}" --ymin 1    --ymax 1e6 --output ${OUT}_leading_fatjet_pt     --xmin 0     --xmax 2000  --xlabel "p_{T}^{J} (GeV)"                   --rebin 50  --rmin 0 --rmax 2.0

done
done
