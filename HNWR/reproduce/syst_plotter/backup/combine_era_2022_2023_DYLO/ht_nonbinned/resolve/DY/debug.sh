python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Dilepton p_{T} (GeV)" --rmin 0 --rmax 2.0 --rebin 5
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_leading_jet_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_leading_jet_pt --xmin 0 --xmax 2000 --xlabel "Leading Jet p_{T} (GeV)" --rebin 10 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_subleading_jet_pt" --ymin 1 --ymax 1e4 --output ResolveDYEE_subleading_jet_pt --xmin 0 --xmax 500 --xlabel "Subleading Jet p_{T} (GeV)" --rebin 2 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_mlljj" --ymin 1 --ymax 1e6 --output ResolveDYEE_mlljj --xmin 800 --xmax 4000 --xlabel "m(lljj) (GeV)" --rebin 20 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_leading_lep_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_subleading_lep_pt" --ymin 1 --ymax 1e6 --output ResolveDYEE_subleading_lep_pt --xmin 0 --xmax 400 --xlabel "Subleading Lepton p_{T} (GeV)"   --rebin 10 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_mass" --ymin 1 --ymax 1e6 --output ResolveDYEE_dilepton_mass --xmin 0 --xmax 200 --xlabel "m(ll) (GeV)" --rebin 1 --rmin 0 --rmax 2.0   


python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Dilepton p_{T} (GeV)" --rmin 0 --rmax 2.0 --rebin 5
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_leading_jet_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_leading_jet_pt --xmin 0 --xmax 2000 --xlabel "Leading Jet p_{T} (GeV)" --rebin 10 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_subleading_jet_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_subleading_jet_pt --xmin 0 --xmax 500 --xlabel "Subleading Jet p_{T} (GeV)" --rebin 2 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_mlljj" --ymin 1 --ymax 1e6 --output ResolveDYMM_mlljj --xmin 800 --xmax 4000 --xlabel "m(lljj) (GeV)" --rebin 20 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_leading_lep_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_subleading_lep_pt" --ymin 1 --ymax 1e6 --output ResolveDYMM_subleading_lep_pt --xmin 0 --xmax 1000 --xlabel "Subleading Lepton p_{T} (GeV)" --rebin 10 --rmin 0 --rmax 2.0
python MM.py --hist "Obj_PU_Corr_DYCR_Resolved_MM_mass" --ymin 1 --ymax 1e6 --output ResolveDYMM_dilepton_mass --xmin 0 --xmax 200 --xlabel "m(ll) (GeV)" --rebin 10 --rmin 0 --rmax 2.0
