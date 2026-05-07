python EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_EE" --ymin 3 --ymax 1e6 --output BoostDYEE_mlljj --xmin 800 --xmax 4000 --xlabel "m(lJ) (GeV)" --rebin 100 --rmin 0.5 --rmax 2.0
python EE.py --signal-scale 1000 --hist "Obj_PU_leading_lep_pt_boosted_DY_CR_EE" --ymin 3 --ymax 3e5 --output BoostDYEE_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)" --bins "0,100,200,300,400,500,1000,2000" --rmin 0.5 --rmax 1.5
python EE.py --signal-scale 1000 --hist "Obj_PU_subleading_lep_pt_boosted_DY_CR_EE" --ymin 3 --ymax 3e5 --output BoostDYEE_subleading_lep_pt --xmin 0 --xmax 500 --xlabel "Subleading Lepton p_{T} (GeV)" --bins "0,50,100,150,200,250,300,500,1000" --rmin 0.5 --rmax 1.5
python EE.py --signal-scale 1000 --hist "Obj_PU_mll_boosted_DY_CR_EE" --ymin 3 --ymax 1e6 --output BoostDYEE_dilepton_mass --xmin 0 --xmax 200 --xlabel "m(ll) (GeV)" --rebin 2 --rmin 0.5 --rmax 1.5
python EE.py --signal-scale 1000 --hist "Obj_PU_pt(ll)_boosted_DY_CR_EE" --ymin 10 --ymax 1e6 --output BoostDYEE_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Dilepton p_{T} (GeV)" --rebin 50 --rmin 0.5 --rmax 1.5



python MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_MM" --ymin 3 --ymax 1e6 --output BoostDYMM_mlljj --xmin 800 --xmax 4000 --xlabel "m(lJ) (GeV)" --rebin 100 --rmin 0.5 --rmax 2.0