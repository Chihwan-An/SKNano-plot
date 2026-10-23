#!/usr/bin/env bash
# CR1 -> CR2 closure with the per-GenJet FxFx/LO C (2026-09-22): DY = DYCRStudy_DYCRSplit_ZptOnly_ZptNJet (C x EW, no R),
# data / non-DY = DYCRSplit_NoDYCorr; both symlinked into closure_ZptNJet_inputs.
cd /data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased
PLOT_EXTRA_BINDS="/tmp:/tmp" ./condor/in_container.sh python3 /data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/studies/DY/03_cr1_to_cr2_closure/scripts/make_dycr12_closure_cutbased_style.py --prod /gv0/Users/achihwan/SKNanoOutput_dy3gen/HNWR/closure_ZptNJet_inputs/2024 --out /data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/studies/DY/03_cr1_to_cr2_closure/2024_ZptNJet 2>&1 | grep -v "^Info in" | tee /data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/studies/DY/03_cr1_to_cr2_closure/2024_ZptNJet/closure.log
echo CLOSURE_DONE
