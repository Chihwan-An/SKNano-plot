#!/usr/bin/env bash
# Boosted Flavor CR - both tight charge
#
# EMJ (e_mujet):
#   OS → 4 combos: M_tight_E_tight / M_tight_E_not_tight / M_not_tight_E_tight / M_not_tight_E_not_tight
#   SS → SS_tight only (analyzer accumulates all M_tight combos into single SS_tight histogram)
#
# MEJ (mu_ejets):
#   OS/SS → 4 combos each: M_tight_E_tight / M_tight_E_not_tight / M_not_tight_E_tight / M_not_tight_E_not_tight

# ─── EMJ OS: 4 tight combos ───────────────────────────────────────────────────
for MTC in M_tight M_not_tight; do
for ETC in E_tight E_not_tight; do
TAG="OS_${MTC}_${ETC}"
OUT="BoostFLVEMJ_${TAG}"
# mixed hist names: first 3 use "Obj_PU_{var}_boosted_e_mujet_*" prefix; rest use "Obj_PU_Boosted_Flavor_CR_e_mujet_*" prefix

python EE.py --hist "Obj_PU_m(lljj)_boosted_e_mujet_${TAG}_Flavor_CR"                              --ymin 1e-1 --ymax 1e6 --output ${OUT}_mlljj                   --xmin 800   --xmax 4000  --xlabel "m(lljj) (GeV)"                      --rebin 100 --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_pt(ll)_boosted_e_mujet_${TAG}_Flavor_CR"                               --ymin 1e-1 --ymax 1e6 --output ${OUT}_dilepton_pt             --xmin 0     --xmax 1000  --xlabel "Dilepton p_{T} (GeV)"                --rebin 50  --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_leading_fatjet_pt_boosted_e_mujet_${TAG}_Flavor_CR"                    --ymin 1e-1 --ymax 1e6 --output ${OUT}_leading_fatjet_pt       --xmin 0     --xmax 2000  --xlabel "Leading Fat Jet p_{T} (GeV)"         --bins "200,400,600,800,1000,2000" --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_LeadingLepPt"                        --ymin 1e-1 --ymax 1e6 --output ${OUT}_leading_lep_pt          --xmin 0     --xmax 1000  --xlabel "Leading Lepton p_{T} (GeV)"          --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_SubLeadingLepPt"                     --ymin 1e-1 --ymax 1e6 --output ${OUT}_subleading_lep_pt       --xmin 0     --xmax 500   --xlabel "Subleading Lepton p_{T} (GeV)"       --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_Fatjet_SDMass"                       --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_SDMass           --xmin 0     --xmax 200   --xlabel "Fat Jet Soft Drop Mass (GeV)"        --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_Fatjet_pt"                           --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_pt               --xmin 0     --xmax 2000  --xlabel "Leading Fat Jet p_{T} (GeV)"         --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_LeadingLepEta"                       --ymin 1e-1 --ymax 1e6 --output ${OUT}_leading_lep_eta         --xmin -2.5  --xmax 2.5   --xlabel "Leading Lepton #eta"                 --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_SubLeadingLepEta"                    --ymin 1e-1 --ymax 1e6 --output ${OUT}_subleading_lep_eta      --xmin -2.5  --xmax 2.5   --xlabel "Subleading Lepton #eta"              --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_Fatjet_Eta"                          --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_eta              --xmin -2.5  --xmax 2.5   --xlabel "Fat Jet #eta"                        --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_Fatjet_Phi"                          --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_phi              --xmin -3.14 --xmax 3.14  --xlabel "Fat Jet #phi"                        --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_DeltaR_LeadLep_Fatjet"              --ymin 1e-1 --ymax 1e6 --output ${OUT}_deltaR_leadlep_fatjet   --xmin 0     --xmax 5     --xlabel "#DeltaR(lead lep, fat jet)"          --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_LeadLep_LSF"                        --ymin 1e-1 --ymax 1e6 --output ${OUT}_leadlep_lsf             --xmin 0     --xmax 1     --xlabel "Lead Lep LSF"                        --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_mll"                                --ymin 1e-1 --ymax 1e6 --output ${OUT}_mll                     --xmin 0     --xmax 1000  --xlabel "m(ll) (GeV)"                         --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_mass"                               --ymin 1e-1 --ymax 1e6 --output ${OUT}_dilepton_mass            --xmin 0     --xmax 2000  --xlabel "m(ll) (GeV)"                         --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_eta"                                --ymin 1e-1 --ymax 1e6 --output ${OUT}_dilepton_eta             --xmin -5    --xmax 5     --xlabel "Dilepton #eta"                       --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_phi"                                --ymin 1e-1 --ymax 1e6 --output ${OUT}_dilepton_phi             --xmin -3.14 --xmax 3.14  --xlabel "Dilepton #phi"                       --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_WRpt"                               --ymin 1e-1 --ymax 1e6 --output ${OUT}_WR_pt                   --xmin 0     --xmax 1000  --xlabel "WR p_{T} (GeV)"                      --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_WR_eta"                             --ymin 1e-1 --ymax 1e6 --output ${OUT}_WR_eta                  --xmin -5    --xmax 5     --xlabel "WR #eta"                             --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_WR_phi"                             --ymin 1e-1 --ymax 1e6 --output ${OUT}_WR_phi                  --xmin -3.14 --xmax 3.14  --xlabel "WR #phi"                             --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_LeadingLepPhi"                      --ymin 1e-1 --ymax 1e6 --output ${OUT}_leading_lep_phi         --xmin -3.14 --xmax 3.14  --xlabel "Leading Lepton #phi"                 --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_SubLeadingLepPhi"                   --ymin 1e-1 --ymax 1e6 --output ${OUT}_subleading_lep_phi      --xmin -3.14 --xmax 3.14  --xlabel "Subleading Lepton #phi"              --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_Fatjet_lsf3"                        --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_lsf3             --xmin 0     --xmax 1     --xlabel "Fat Jet LSF3"                        --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_dphi_leadlep_fatjet"                --ymin 1e-1 --ymax 1e6 --output ${OUT}_dphi_leadlep_fatjet     --xmin 0     --xmax 3.14  --xlabel "#Delta#phi(lead lep, fat jet)"       --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_punum"                              --ymin 1e-1 --ymax 1e6 --output ${OUT}_punum                   --xmin 0     --xmax 80    --xlabel "Number of Pileup Vertices"           --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_jetnum"                             --ymin 1e-1 --ymax 1e6 --output ${OUT}_jetnum                  --xmin 0     --xmax 5     --xlabel "Number of Jets"                                  --rmin 0 --rmax 2.5

done
done

# ─── EMJ SS: tight only (M_tight_E_tight + M_tight_E_not_tight both → SS_tight) ─
TAG="SS_tight"
OUT="BoostFLVEMJ_${TAG}"

python EE.py --hist "Obj_PU_m(lljj)_boosted_e_mujet_${TAG}_Flavor_CR"                              --ymin 1e-1 --ymax 1e6 --output ${OUT}_mlljj                   --xmin 800   --xmax 4000  --xlabel "m(lljj) (GeV)"                      --rebin 100 --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_pt(ll)_boosted_e_mujet_${TAG}_Flavor_CR"                               --ymin 1e-1 --ymax 1e6 --output ${OUT}_dilepton_pt             --xmin 0     --xmax 1000  --xlabel "Dilepton p_{T} (GeV)"                --rebin 50  --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_leading_fatjet_pt_boosted_e_mujet_${TAG}_Flavor_CR"                    --ymin 1e-1 --ymax 1e6 --output ${OUT}_leading_fatjet_pt       --xmin 0     --xmax 2000  --xlabel "Leading Fat Jet p_{T} (GeV)"         --bins "200,400,600,800,1000,2000" --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_LeadingLepPt"                        --ymin 1e-1 --ymax 1e6 --output ${OUT}_leading_lep_pt          --xmin 0     --xmax 1000  --xlabel "Leading Lepton p_{T} (GeV)"          --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_SubLeadingLepPt"                     --ymin 1e-1 --ymax 1e6 --output ${OUT}_subleading_lep_pt       --xmin 0     --xmax 500   --xlabel "Subleading Lepton p_{T} (GeV)"       --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_Fatjet_SDMass"                       --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_SDMass           --xmin 0     --xmax 200   --xlabel "Fat Jet Soft Drop Mass (GeV)"        --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_Fatjet_pt"                           --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_pt               --xmin 0     --xmax 2000  --xlabel "Leading Fat Jet p_{T} (GeV)"         --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_LeadingLepEta"                       --ymin 1e-1 --ymax 1e6 --output ${OUT}_leading_lep_eta         --xmin -2.5  --xmax 2.5   --xlabel "Leading Lepton #eta"                 --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_SubLeadingLepEta"                    --ymin 1e-1 --ymax 1e6 --output ${OUT}_subleading_lep_eta      --xmin -2.5  --xmax 2.5   --xlabel "Subleading Lepton #eta"              --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_Fatjet_Eta"                          --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_eta              --xmin -2.5  --xmax 2.5   --xlabel "Fat Jet #eta"                        --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_Fatjet_Phi"                          --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_phi              --xmin -3.14 --xmax 3.14  --xlabel "Fat Jet #phi"                        --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_DeltaR_LeadLep_Fatjet"              --ymin 1e-1 --ymax 1e6 --output ${OUT}_deltaR_leadlep_fatjet   --xmin 0     --xmax 5     --xlabel "#DeltaR(lead lep, fat jet)"          --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_LeadLep_LSF"                        --ymin 1e-1 --ymax 1e6 --output ${OUT}_leadlep_lsf             --xmin 0     --xmax 1     --xlabel "Lead Lep LSF"                        --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_mll"                                --ymin 1e-1 --ymax 1e6 --output ${OUT}_mll                     --xmin 0     --xmax 1000  --xlabel "m(ll) (GeV)"                         --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_mass"                               --ymin 1e-1 --ymax 1e6 --output ${OUT}_dilepton_mass            --xmin 0     --xmax 2000  --xlabel "m(ll) (GeV)"                         --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_eta"                                --ymin 1e-1 --ymax 1e6 --output ${OUT}_dilepton_eta             --xmin -5    --xmax 5     --xlabel "Dilepton #eta"                       --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_phi"                                --ymin 1e-1 --ymax 1e6 --output ${OUT}_dilepton_phi             --xmin -3.14 --xmax 3.14  --xlabel "Dilepton #phi"                       --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_WRpt"                               --ymin 1e-1 --ymax 1e6 --output ${OUT}_WR_pt                   --xmin 0     --xmax 1000  --xlabel "WR p_{T} (GeV)"                      --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_WR_eta"                             --ymin 1e-1 --ymax 1e6 --output ${OUT}_WR_eta                  --xmin -5    --xmax 5     --xlabel "WR #eta"                             --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_WR_phi"                             --ymin 1e-1 --ymax 1e6 --output ${OUT}_WR_phi                  --xmin -3.14 --xmax 3.14  --xlabel "WR #phi"                             --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_LeadingLepPhi"                      --ymin 1e-1 --ymax 1e6 --output ${OUT}_leading_lep_phi         --xmin -3.14 --xmax 3.14  --xlabel "Leading Lepton #phi"                 --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_SubLeadingLepPhi"                   --ymin 1e-1 --ymax 1e6 --output ${OUT}_subleading_lep_phi      --xmin -3.14 --xmax 3.14  --xlabel "Subleading Lepton #phi"              --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_Fatjet_lsf3"                        --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_lsf3             --xmin 0     --xmax 1     --xlabel "Fat Jet LSF3"                        --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_dphi_leadlep_fatjet"                --ymin 1e-1 --ymax 1e6 --output ${OUT}_dphi_leadlep_fatjet     --xmin 0     --xmax 3.14  --xlabel "#Delta#phi(lead lep, fat jet)"       --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_punum"                              --ymin 1e-1 --ymax 1e6 --output ${OUT}_punum                   --xmin 0     --xmax 80    --xlabel "Number of Pileup Vertices"           --rebin 5   --rmin 0 --rmax 2.5
python EE.py --hist "Obj_PU_Boosted_Flavor_CR_e_mujet_${TAG}_jetnum"                             --ymin 1e-1 --ymax 1e6 --output ${OUT}_jetnum                  --xmin 0     --xmax 5     --xlabel "Number of Jets"                                  --rmin 0 --rmax 2.5

# ─── MEJ OS/SS: 4 tight combos each ──────────────────────────────────────────
for SIGN in OS SS; do
for MTC in M_tight M_not_tight; do
for ETC in E_tight E_not_tight; do
TAG="${SIGN}_${MTC}_${ETC}"
OUT="BoostFLVMEJ_${TAG}"

python MM.py --hist "Obj_PU_m(lljj)_boosted_mu_ejets_${TAG}_Flavor_CR"                             --ymin 1e-1 --ymax 1e6 --output ${OUT}_mlljj                   --xmin 800   --xmax 4000  --xlabel "m(lljj) (GeV)"                      --rebin 100 --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_pt(ll)_boosted_mu_ejets_${TAG}_Flavor_CR"                              --ymin 1e-1 --ymax 1e6 --output ${OUT}_dilepton_pt             --xmin 0     --xmax 1000  --xlabel "Dilepton p_{T} (GeV)"                --rebin 50  --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_leading_fatjet_pt_boosted_mu_ejets_${TAG}_Flavor_CR"                   --ymin 1e-1 --ymax 1e6 --output ${OUT}_leading_fatjet_pt       --xmin 0     --xmax 2000  --xlabel "Leading Fat Jet p_{T} (GeV)"         --bins "200,400,600,800,1000,2000" --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_LeadingLepPt"                       --ymin 1e-1 --ymax 1e6 --output ${OUT}_leading_lep_pt          --xmin 0     --xmax 1000  --xlabel "Leading Lepton p_{T} (GeV)"          --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_SubLeadingLepPt"                    --ymin 1e-1 --ymax 1e6 --output ${OUT}_subleading_lep_pt       --xmin 0     --xmax 500   --xlabel "Subleading Lepton p_{T} (GeV)"       --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_Fatjet_SDMass"                      --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_SDMass           --xmin 0     --xmax 200   --xlabel "Fat Jet Soft Drop Mass (GeV)"        --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_Fatjet_pt"                          --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_pt               --xmin 0     --xmax 2000  --xlabel "Leading Fat Jet p_{T} (GeV)"         --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_LeadingLepEta"                      --ymin 1e-1 --ymax 1e6 --output ${OUT}_leading_lep_eta         --xmin -2.5  --xmax 2.5   --xlabel "Leading Lepton #eta"                 --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_SubLeadingLepEta"                   --ymin 1e-1 --ymax 1e6 --output ${OUT}_subleading_lep_eta      --xmin -2.5  --xmax 2.5   --xlabel "Subleading Lepton #eta"              --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_Fatjet_Eta"                         --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_eta              --xmin -2.5  --xmax 2.5   --xlabel "Fat Jet #eta"                        --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_Fatjet_Phi"                         --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_phi              --xmin -3.14 --xmax 3.14  --xlabel "Fat Jet #phi"                        --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_DeltaR_LeadLep_Fatjet"             --ymin 1e-1 --ymax 1e6 --output ${OUT}_deltaR_leadlep_fatjet   --xmin 0     --xmax 5     --xlabel "#DeltaR(lead lep, fat jet)"          --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_LeadLep_LSF"                       --ymin 1e-1 --ymax 1e6 --output ${OUT}_leadlep_lsf             --xmin 0     --xmax 1     --xlabel "Lead Lep LSF"                        --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_mll"                               --ymin 1e-1 --ymax 1e6 --output ${OUT}_mll                     --xmin 0     --xmax 1000  --xlabel "m(ll) (GeV)"                         --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_mass"                              --ymin 1e-1 --ymax 1e6 --output ${OUT}_dilepton_mass            --xmin 0     --xmax 2000  --xlabel "m(ll) (GeV)"                         --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_eta"                               --ymin 1e-1 --ymax 1e6 --output ${OUT}_dilepton_eta             --xmin -5    --xmax 5     --xlabel "Dilepton #eta"                       --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_phi"                               --ymin 1e-1 --ymax 1e6 --output ${OUT}_dilepton_phi             --xmin -3.14 --xmax 3.14  --xlabel "Dilepton #phi"                       --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_WRpt"                              --ymin 1e-1 --ymax 1e6 --output ${OUT}_WR_pt                   --xmin 0     --xmax 1000  --xlabel "WR p_{T} (GeV)"                      --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_WR_eta"                            --ymin 1e-1 --ymax 1e6 --output ${OUT}_WR_eta                  --xmin -5    --xmax 5     --xlabel "WR #eta"                             --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_WR_phi"                            --ymin 1e-1 --ymax 1e6 --output ${OUT}_WR_phi                  --xmin -3.14 --xmax 3.14  --xlabel "WR #phi"                             --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_LeadingLepPhi"                     --ymin 1e-1 --ymax 1e6 --output ${OUT}_leading_lep_phi         --xmin -3.14 --xmax 3.14  --xlabel "Leading Lepton #phi"                 --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_SubLeadingLepPhi"                  --ymin 1e-1 --ymax 1e6 --output ${OUT}_subleading_lep_phi      --xmin -3.14 --xmax 3.14  --xlabel "Subleading Lepton #phi"              --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_Fatjet_lsf3"                       --ymin 1e-1 --ymax 1e6 --output ${OUT}_fatjet_lsf3             --xmin 0     --xmax 1     --xlabel "Fat Jet LSF3"                        --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_dphi_leadlep_fatjet"               --ymin 1e-1 --ymax 1e6 --output ${OUT}_dphi_leadlep_fatjet     --xmin 0     --xmax 3.14  --xlabel "#Delta#phi(lead lep, fat jet)"       --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_punum"                             --ymin 1e-1 --ymax 1e6 --output ${OUT}_punum                   --xmin 0     --xmax 80    --xlabel "Number of Pileup Vertices"           --rebin 5   --rmin 0 --rmax 2.5
python MM.py --hist "Obj_PU_Boosted_Flavor_CR_mu_ejets_${TAG}_jetnum"                            --ymin 1e-1 --ymax 1e6 --output ${OUT}_jetnum                  --xmin 0     --xmax 5     --xlabel "Number of Jets"                                  --rmin 0 --rmax 2.5

done
done
done
