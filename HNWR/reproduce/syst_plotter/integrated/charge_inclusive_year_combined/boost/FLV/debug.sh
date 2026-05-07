
#python EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_e_mujet_SS_Flavor_CR" --ymin 1 --ymax 2e3 --output BoostFLVEMJ_SS_mlljj --xmin 800 --xmax 4000 --xlabel "Same sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0

#python MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_mu_ejets_SS_Flavor_CR" --ymin 1 --ymax 2e3 --output BoostFLVMEJ_SS_mlljj --xmin 800 --xmax 4000 --xlabel "Same sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0

## OS

#python EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_e_mujet_OS_Flavor_CR" --ymin 1 --ymax 2e3 --output BoostFLVEMJ_OS_mlljj --xmin 800 --xmax 4000 --xlabel "Other sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0

#python MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_mu_ejets_OS_Flavor_CR" --ymin 1 --ymax 2e3 --output BoostFLVMEJ_OS_mlljj --xmin 800 --xmax 4000 --xlabel "Other sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
#python EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_e_mujet_Flavor_CR" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_mlljj --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1500,1800,8000" --rmin 0.5 --rmax 1.5
#python MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_mu_ejets_Flavor_CR" --ymin 1 --ymax 1e6 --output BoostFLVMEJ_mlljj --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1500,1800,8000" --rmin 0.5 --rmax 1.5


python /data6/Users/achihwan/SKNanoAnalyzer-v13/plots/HNWR/reproduce/syst_plotter/integrated/plotter_file/year_sep/EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_e_mujet_Flavor_CR" --ymin 1e-1 --ymax 1e3 --output BoostFLVEMJ_mlljj --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1500,1800,8000" --rmin 0.5 --rmax 1.5 --show-sb
python /data6/Users/achihwan/SKNanoAnalyzer-v13/plots/HNWR/reproduce/syst_plotter/integrated/plotter_file/year_sep/MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_mu_ejets_Flavor_CR" --ymin 1 --ymax 1e6 --output BoostFLVMEJ_mlljj --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1500,1800,8000" --rmin 0.5 --rmax 1.5 --show-sb



