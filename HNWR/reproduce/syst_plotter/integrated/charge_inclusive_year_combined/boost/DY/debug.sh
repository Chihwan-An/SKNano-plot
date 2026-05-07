
### Same sign 
#python MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_MM_SS" --ymin 1 --ymax 1e3 --output BoostDYMM_SS_mlljj --xmin 800 --xmax 4000 --xlabel "m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0

#python EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_EE_SS" --ymin 1 --ymax 1e3 --output BoostDYEE_SS_mlljj --xmin 800 --xmax 4000 --xlabel "Same sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0


## other sign 

#python MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_MM_OS" --ymin 1 --ymax 1e3 --output BoostDYMM_OS_mlljj --xmin 800 --xmax 4000 --xlabel "Other sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0
#python EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_EE_OS" --ymin 1 --ymax 1e3 --output BoostDYEE_OS_mlljj --xmin 800 --xmax 4000 --xlabel "Other sign m(lJ) (GeV)" --rebin 100 --rmin 0 --rmax 2.0


python /data6/Users/achihwan/SKNanoAnalyzer-v13/plots/HNWR/reproduce/syst_plotter/integrated/plotter_file/year_sep/EE.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_EE" --ymin 1 --ymax 1e6 --output BoostDYEE_mlljj --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1500,1800,8000" --rmin 0.5 --rmax 1.5 --show-sb
#python /data6/Users/achihwan/SKNanoAnalyzer-v13/plots/HNWR/reproduce/syst_plotter/integrated/plotter_file/ht_binned/MM.py --signal-scale 1.0 --hist "Obj_PU_m(lljj)_boosted_DY_CR_MM" --ymin 1 --ymax 1e6 --output BoostDYMM_mlljj --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1500,1800,8000" --rmin 0.5 --rmax 1.5 --show-sb