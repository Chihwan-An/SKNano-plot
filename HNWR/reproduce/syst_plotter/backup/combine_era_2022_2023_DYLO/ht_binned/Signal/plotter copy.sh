#!/usr/bin/env bash

python cutflow.py --signal-scale 1.0 --input /gv0/Users/achihwan/SKNanoRunlog/2026_03_16_114427_Reproduce20_002_copy/2023/WR4000N100MM/output/hists_0.root --output cutflow_mumu_Boosted_SR
python cutflow.py --signal-scale 1.0 --input /gv0/Users/achihwan/SKNanoRunlog/2026_03_16_114427_Reproduce20_002_copy/2023/WR4000N2100MM/output/hists_0.root --output cutflow_mumu_resolved_SR
python cutflow.py --signal-scale 1.0 --input /gv0/Users/achihwan/SKNanoRunlog/2026_03_16_114427_Reproduce20_002_copy/2023/WR4000N100EE/output/hists_0.root --output cutflow_ee_Boosted_SR
python cutflow.py --signal-scale 1.0 --input /gv0/Users/achihwan/SKNanoRunlog/2026_03_16_114427_Reproduce20_002_copy/2023/WR4000N2100EE/output/hists_0.root --output cutflow_ee_resolved_SR
