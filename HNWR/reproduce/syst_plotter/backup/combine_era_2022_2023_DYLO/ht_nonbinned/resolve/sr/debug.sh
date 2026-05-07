#python EE.py --signal-scale 1.0 --hist "Obj_PU_Corr_SR_Resolved_EE_mlljj" --ymin 1 --ymax 5e3 --output ResolveSREE_mlljj --xmin 800 --xmax 4000 --xlabel "m(lljj) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
#python MM.py --signal-scale 1.0 --hist "Obj_PU_Corr_SR_Resolved_MM_mlljj" --ymin 1 --ymax 5e3 --output ResolveSRMM_mlljj --xmin 800 --xmax 4000 --xlabel "m(lljj) (GeV)" --rebin 100 --rmin 0 --rmax 2.0


python EE.py --signal-scale 1.0 --hist "Obj_PU_Corr_SR_Resolved_EE_ll_pt" --ymin 1 --ymax 1e5 --output ResolveSREE_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Dilepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python EE.py --signal-scale 1.0 --hist "Obj_PU_Corr_SR_Resolved_EE_leading_jet_pt" --ymin 1 --ymax 1e5 --output ResolveSREE_leading_jet_pt --xmin 0 --xmax 2000 --xlabel "Leading Jet p_{T} (GeV)"  --rmin 0 --rmax 2.0 --rebin 50
python EE.py --signal-scale 1.0 --hist "Obj_PU_Corr_SR_Resolved_EE_subleading_jet_pt" --ymin 1 --ymax 1e5 --output ResolveSREE_subleading_jet_pt --xmin 0 --xmax 2000 --xlabel "Subleading Jet p_{T} (GeV)"  --rmin 0 --rmax 2.0 --rebin 50
python EE.py --signal-scale 1.0 --hist "Obj_PU_Corr_SR_Resolved_EE_mlljj" --ymin 1 --ymax 1e5 --output ResolveSREE_mlljj --xmin 800 --xmax 4000 --xlabel "m(lljj) (GeV)"  --rmin 0 --rmax 2.0 --rebin 100
python EE.py --signal-scale 1.0 --hist "Obj_PU_Corr_SR_Resolved_EE_leading_lep_pt" --ymin 1 --ymax 1e5 --output ResolveSREE_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)"  --rmin 0 --rmax 2.0 --rebin 50
python EE.py --signal-scale 1.0 --hist "Obj_PU_Corr_SR_Resolved_EE_subleading_lep_pt" --ymin 1 --ymax 1e5 --output ResolveSREE_subleading_lep_pt --xmin 0 --xmax 1000 --xlabel "Subleading Lepton p_{T} (GeV)"  --rmin 0 --rmax 2.0 --rebin 50 
python EE.py --signal-scale 1.0 --hist "Obj_PU_Corr_SR_Resolved_EE_mass" --ymin 1 --ymax 1e5 --output ResolveSREE_dilepton_mass --xmin 0 --xmax 2000 --xlabel "m(ll) (GeV)"  --rmin 0 --rmax 2.0 --rebin 5


python MM.py --signal-scale 1.0 --hist "Obj_PU_Corr_SR_Resolved_MM_ll_pt" --ymin 1 --ymax 1e5 --output ResolveSRMM_dilepton_pt --xmin 0 --xmax 1000 --xlabel "Dilepton p_{T} (GeV)" --rebin 50 --rmin 0 --rmax 2.0
python MM.py --signal-scale 1.0 --hist "Obj_PU_Corr_SR_Resolved_MM_leading_jet_pt" --ymin 1 --ymax 1e5 --output ResolveSRMM_leading_jet_pt --xmin 0 --xmax 2000 --xlabel "Leading Jet p_{T} (GeV)"  --rmin 0 --rmax 2.0 --rebin 50
python MM.py --signal-scale 1.0 --hist "Obj_PU_Corr_SR_Resolved_MM_subleading_jet_pt" --ymin 1 --ymax 1e5 --output ResolveSRMM_subleading_jet_pt --xmin 0 --xmax 2000 --xlabel "Subleading Jet p_{T} (GeV)"  --rmin 0 --rmax 2.0  --rebin 50
python MM.py --signal-scale 1.0 --hist "Obj_PU_Corr_SR_Resolved_MM_mlljj" --ymin 1 --ymax 1e5 --output ResolveSRMM_mlljj --xmin 800 --xmax 4000 --xlabel "m(lljj) (GeV)"  --rmin 0 --rmax 2.0 --rebin 100
python MM.py --signal-scale 1.0 --hist "Obj_PU_Corr_SR_Resolved_MM_leading_lep_pt" --ymin 1 --ymax 1e5 --output ResolveSRMM_leading_lep_pt --xmin 0 --xmax 1000 --xlabel "Leading Lepton p_{T} (GeV)"  --rmin 0 --rmax 2.0 --rebin 50
python MM.py --signal-scale 1.0 --hist "Obj_PU_Corr_SR_Resolved_MM_subleading_lep_pt" --ymin 1 --ymax 1e5 --output ResolveSRMM_subleading_lep_pt --xmin 0 --xmax 1000 --xlabel "Subleading Lepton p_{T} (GeV)" --rmin 0 --rmax 2.0 --rebin 50
python MM.py --signal-scale 1.0 --hist "Obj_PU_Corr_SR_Resolved_MM_mass" --ymin 1 --ymax 1e5 --output ResolveSRMM_dilepton_mass --xmin 0 --xmax 2000 --xlabel "m(ll) (GeV)" --rebin 5 --rmin 0 --rmax 2.0 