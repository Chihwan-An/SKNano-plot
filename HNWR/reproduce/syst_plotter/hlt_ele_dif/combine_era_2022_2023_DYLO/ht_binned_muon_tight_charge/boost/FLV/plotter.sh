#!/usr/bin/env bash
# Boosted Flavor CR tight charge
# EMJ (e_mujet): uses EE.py   / MEJ (mu_ejets): uses MM.py

for SIGN in OS SS; do
for TC in tight not_tight; do
TAG="${SIGN}_${TC}"

# --- EMJ: Obj_PU_Boosted_Flavor_CR_e_mujet_{TAG}_{var} ---
PEMJ="Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}"
OEMJ="BoostFLVEMJ_${TAG}"

python EE.py --hist "${PEMJ}_Fatjet_pt"               --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_fatjet_pt             --xmin 0     --xmax 2000  --xlabel "Leading Fat Jet p_{T} (GeV)"    --bins "200,400,600,800,1000,2000" --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_Fatjet_SDMass"            --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_fatjet_SDMass         --xmin 0     --xmax 200   --xlabel "Fat Jet Soft Drop Mass (GeV)"   --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_LeadingLepEta"            --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_leading_lep_eta       --xmin -2.5  --xmax 2.5   --xlabel "Leading Lepton #eta"            --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_SubLeadingLepEta"         --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_subleading_lep_eta    --xmin -2.5  --xmax 2.5   --xlabel "Subleading Lepton #eta"         --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_Fatjet_Eta"               --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_fatjet_eta            --xmin -2.5  --xmax 2.5   --xlabel "Fat Jet #eta"                   --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_Fatjet_Phi"               --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_fatjet_phi            --xmin -3.14 --xmax 3.14  --xlabel "Fat Jet #phi"                   --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_DeltaR_LeadLep_Fatjet"   --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_deltaR_leadlep_fatjet --xmin 0     --xmax 5     --xlabel "#DeltaR(lead lep, fat jet)"    --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_LeadLep_LSF"              --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_leadlep_lsf           --xmin 0     --xmax 1     --xlabel "Lead Lep LSF"                   --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_WRpt"                     --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_WR_pt                --xmin 0     --xmax 1000  --xlabel "WR p_{T} (GeV)"                --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_mass"                     --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_dilepton_mass         --xmin 0     --xmax 2000  --xlabel "m(ll) (GeV)"                   --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_mll"                      --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_mll                  --xmin 0     --xmax 1000  --xlabel "m(ll) (GeV)"                   --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_eta"                      --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_dilepton_eta          --xmin -5    --xmax 5     --xlabel "Dilepton #eta"                  --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_phi"                      --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_dilepton_phi          --xmin -3.14 --xmax 3.14  --xlabel "Dilepton #phi"                  --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_WR_eta"                   --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_WR_eta              --xmin -5    --xmax 5     --xlabel "WR #eta"                        --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_WR_phi"                   --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_WR_phi              --xmin -3.14 --xmax 3.14  --xlabel "WR #phi"                        --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_LeadingLepPhi"            --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_leading_lep_phi       --xmin -3.14 --xmax 3.14  --xlabel "Leading Lepton #phi"            --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_SubLeadingLepPhi"         --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_subleading_lep_phi    --xmin -3.14 --xmax 3.14  --xlabel "Subleading Lepton #phi"         --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_Fatjet_lsf3"              --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_fatjet_lsf3          --xmin 0     --xmax 1     --xlabel "Fat Jet LSF3"                   --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_dphi_leadlep_fatjet"      --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_dphi_leadlep_fatjet  --xmin 0     --xmax 3.14  --xlabel "#Delta#phi(lead lep, fat jet)" --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_LeadingLepPt"             --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_leading_lep_pt        --xmin 0     --xmax 1000  --xlabel "Leading Lepton p_{T} (GeV)"    --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_SubLeadingLepPt"          --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_subleading_lep_pt     --xmin 0     --xmax 500   --xlabel "Subleading Lepton p_{T} (GeV)" --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_jetnum"                   --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_jetnum               --xmin 0     --xmax 5     --xlabel "Number of Jets"                           --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_punum"                    --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_punum                --xmin 0     --xmax 80    --xlabel "Number of Pileup Vertices"     --rebin 5  --rmin 0 --rmax 2.5
python EE.py --hist "${PEMJ}_pv"                       --ymin 1e-1 --ymax 1e6 --output ${OEMJ}_pv                   --xmin 0     --xmax 80    --xlabel "Number of Primary Vertices"     --rebin 5  --rmin 0 --rmax 2.5

# --- MEJ: Obj_PU_Boosted_Flavor_CR_mu_ejets_{TAG}_{var} ---
PMEJ="Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}"
OMEJ="BoostFLVMEJ_${TAG}"

python MM.py --hist "${PMEJ}_Fatjet_pt"               --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_fatjet_pt             --xmin 0     --xmax 2000  --xlabel "Leading Fat Jet p_{T} (GeV)"    --bins "200,400,600,800,1000,2000" --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_Fatjet_SDMass"            --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_fatjet_SDMass         --xmin 0     --xmax 200   --xlabel "Fat Jet Soft Drop Mass (GeV)"   --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_LeadingLepEta"            --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_leading_lep_eta       --xmin -2.5  --xmax 2.5   --xlabel "Leading Lepton #eta"            --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_SubLeadingLepEta"         --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_subleading_lep_eta    --xmin -2.5  --xmax 2.5   --xlabel "Subleading Lepton #eta"         --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_Fatjet_Eta"               --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_fatjet_eta            --xmin -2.5  --xmax 2.5   --xlabel "Fat Jet #eta"                   --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_Fatjet_Phi"               --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_fatjet_phi            --xmin -3.14 --xmax 3.14  --xlabel "Fat Jet #phi"                   --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_DeltaR_LeadLep_Fatjet"   --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_deltaR_leadlep_fatjet --xmin 0     --xmax 5     --xlabel "#DeltaR(lead lep, fat jet)"    --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_LeadLep_LSF"              --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_leadlep_lsf           --xmin 0     --xmax 1     --xlabel "Lead Lep LSF"                   --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_WRpt"                     --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_WR_pt                --xmin 0     --xmax 1000  --xlabel "WR p_{T} (GeV)"                --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_mass"                     --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_dilepton_mass         --xmin 0     --xmax 2000  --xlabel "m(ll) (GeV)"                   --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_mll"                      --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_mll                  --xmin 0     --xmax 1000  --xlabel "m(ll) (GeV)"                   --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_eta"                      --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_dilepton_eta          --xmin -5    --xmax 5     --xlabel "Dilepton #eta"                  --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_phi"                      --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_dilepton_phi          --xmin -3.14 --xmax 3.14  --xlabel "Dilepton #phi"                  --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_WR_eta"                   --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_WR_eta              --xmin -5    --xmax 5     --xlabel "WR #eta"                        --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_WR_phi"                   --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_WR_phi              --xmin -3.14 --xmax 3.14  --xlabel "WR #phi"                        --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_LeadingLepPhi"            --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_leading_lep_phi       --xmin -3.14 --xmax 3.14  --xlabel "Leading Lepton #phi"            --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_SubLeadingLepPhi"         --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_subleading_lep_phi    --xmin -3.14 --xmax 3.14  --xlabel "Subleading Lepton #phi"         --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_Fatjet_lsf3"              --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_fatjet_lsf3          --xmin 0     --xmax 1     --xlabel "Fat Jet LSF3"                   --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_dphi_leadlep_fatjet"      --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_dphi_leadlep_fatjet  --xmin 0     --xmax 3.14  --xlabel "#Delta#phi(lead lep, fat jet)" --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_LeadingLepPt"             --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_leading_lep_pt        --xmin 0     --xmax 1000  --xlabel "Leading Lepton p_{T} (GeV)"    --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_SubLeadingLepPt"          --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_subleading_lep_pt     --xmin 0     --xmax 500   --xlabel "Subleading Lepton p_{T} (GeV)" --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_jetnum"                   --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_jetnum               --xmin 0     --xmax 5     --xlabel "Number of Jets"                           --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_punum"                    --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_punum                --xmin 0     --xmax 80    --xlabel "Number of Pileup Vertices"     --rebin 5  --rmin 0 --rmax 2.5
python MM.py --hist "${PMEJ}_pv"                       --ymin 1e-1 --ymax 1e6 --output ${OMEJ}_pv                   --xmin 0     --xmax 80    --xlabel "Number of Primary Vertices"     --rebin 5  --rmin 0 --rmax 2.5

done
done
python MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_mlljj --xmin 800 --xmax 4000 --xlabel "m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0

python EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_mlljj --xmin 800 --xmax 4000 --xlabel "Same sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
## other sign 
python MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e3 --output BoostDYMM_OS_mlljj --xmin 800 --xmax 4000 --xlabel "Other sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e3 --output BoostDYEE_OS_mlljj --xmin 800 --xmax 4000 --xlabel "Other sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
