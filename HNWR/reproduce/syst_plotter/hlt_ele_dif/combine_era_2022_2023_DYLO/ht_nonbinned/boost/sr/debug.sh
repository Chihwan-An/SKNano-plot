

python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WRMass_ee" --ymin 1 --ymax 1e5 --output BoostSREE_WRMass --xmin 800 --xmax 4000 --xlabel "m(lljj) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_Dilepton_Pt_ee" --ymin 1 --ymax 1e5 --output BoostSREE_Dilepton_pt --xmin 0 --xmax 1000 --xlabel "p_{T}^{ll} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_LeadingLepPt_ee" --ymin 1 --ymax 1e5 --output BoostSREE_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)" --bins "0,50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000" --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_SubLeadingLepPt_ee" --ymin 1 --ymax 1e5 --output BoostSREE_subleading_lep_pt --xmin 0 --xmax 1000 --xlabel "Subleading Lepton p_{T} (GeV)" --bins "0,50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000" --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_mll_ee" --ymin 1 --ymax 1e5 --output BoostSREE_dilepton_mass --xmin 0 --xmax 2000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_leading_fatjet_pt_boosted_ee" --ymin 1 --ymax 1e5 --output BoostSREE_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "p_{T}^{J} (GeV)" --bins "0,200,400,600,800,1000,2000"--rmin 0 --rmax 2.0

python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_WRMass_mumu" --ymin 1 --ymax 1e5 --output BoostSRMM_WRMass --xmin 800 --xmax 4000 --xlabel "m(lljj) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_Dilepton_Pt_mumu" --ymin 1 --ymax 1e5 --output BoostSRMM_Dilepton_pt --xmin 0 --xmax 1000 --xlabel "m(lljj) (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_LeadingLepPt_mumu" --ymin 1 --ymax 1e5 --output BoostSRMM_LeadingLepPt --xmin 0 --xmax 1000 --xlabel "m(lljj) (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_SubLeadingLepPt_mumu" --ymin 1 --ymax 1e5 --output BoostSRMM_SubLeadingLepPt --xmin 0 --xmax 1000 --xlabel "m(lljj) (GeV)" --rebin 20 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_mll_mumu" --ymin 1 --ymax 1e5 --output BoostSRMM_dilepton_mass --xmin 0 --xmax 2000 --xlabel "m(lljj) (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_boosted_leading_fatjet_pt_boosted_mumu" --ymin 1 --ymax 1e5 --output BoostSRMM_leading_fatjet_pt --xmin 0 --xmax 2000 --xlabel "m(lljj) (GeV)" --rebin 50 --rmin 0 --rmax 2.0
