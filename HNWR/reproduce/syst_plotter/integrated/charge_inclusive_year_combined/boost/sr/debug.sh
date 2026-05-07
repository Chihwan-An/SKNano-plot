

#python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WRMass_ee_SS" --ymin 3 --ymax 1e5 --output BoostSREE_SS_WRMass --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0.7 --rmax 1.3

#python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_WRMass_mumu_SS" --ymin 3 --ymax 1e5 --output BoostSRMM_SS_WRMass --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1400,1600,2000,2400,2800,3200,8000" --rmin 0.7 --rmax 1.3

#python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WRMass_ee" --ymin 1 --ymax 1e6 --output BoostSREE_WRMass --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1500,1800,8000" --rmin 0.7 --rmax 1.3
#python MM.py --signal-scale 1.0 --hist "Obj_PU_SR_boosted_WRMass_mumu" --ymin 1 --ymax 1e6 --output BoostSRMM_WRMass --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1500,1800,8000" --rmin 0.7 --rmax 1.3

python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WRMass_ee_SS_2e_tight" --ymin 1e-2 --ymax 1e5 --output BoostSREE_SS_2e_tight_WRMass --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1500,1800,8000" --rmin 0.7 --rmax 1.3
python EE.py --signal-scale 1.0 --hist "Obj_PU_boosted_WRMass_ee_OS_2e_tight" --ymin 1e-2 --ymax 1e5 --output BoostSREE_OS_2e_tight_WRMass --xmin 800 --xmax 8000 --xlabel "m(lJ) (GeV)" --bins "800,1000,1200,1500,1800,8000" --rmin 0.7 --rmax 1.3