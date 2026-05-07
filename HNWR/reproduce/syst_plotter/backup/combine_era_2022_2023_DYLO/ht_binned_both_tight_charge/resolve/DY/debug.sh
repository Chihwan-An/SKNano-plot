#!/usr/bin/env bash


python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_2e_tight_mlljj"                 --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_2e_tight_mlljj                --xmin 800   --xmax 4000  --xlabel "m(lljj) (GeV)"                --rebin 20 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_1e_tight_mlljj"                 --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_1e_tight_mlljj                --xmin 800   --xmax 4000  --xlabel "m(lljj) (GeV)"                --rebin 20 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_OS_0e_tight_mlljj"                 --ymin 1 --ymax 1e6 --output ResolveDYEE_OS_0e_tight_mlljj                --xmin 800   --xmax 4000  --xlabel "m(lljj) (GeV)"                --rebin 20 --rmin 0 --rmax 2.0


python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_2e_tight_mlljj"                 --ymin 1 --ymax 1e6 --output ResolveDYEE_SS_2e_tight_mlljj                --xmin 800   --xmax 4000  --xlabel "m(lljj) (GeV)"                --rebin 20 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_1e_tight_mlljj"                 --ymin 1 --ymax 1e6 --output ResolveDYEE_SS_1e_tight_mlljj                --xmin 800   --xmax 4000  --xlabel "m(lljj) (GeV)"                --rebin 20 --rmin 0 --rmax 2.0
python EE.py --hist "Obj_PU_Corr_DYCR_Resolved_EE_SS_0e_tight_mlljj"                 --ymin 1 --ymax 1e6 --output ResolveDYEE_SS_0e_tight_mlljj                --xmin 800   --xmax 4000  --xlabel "m(lljj) (GeV)"                --rebin 20 --rmin 0 --rmax 2.0