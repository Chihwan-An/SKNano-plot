#!/bin/bash

python CR_2022EE.py --hist-name DileptonMass_CR --output-name DileptonMass_CR_2022_EE --x-range 0,400  --logy --ymax 1e1 --ymin 1e-3 --x-title "m_{ll} [GeV]" --custom-bins "0,10,30,50,70,90,140,200,300,2000"  --normalize-by-bin-size 
python CR_2022EE.py --hist-name LeadingBJetPt_CR --output-name LeadingJetpt_CR_2022_EE --x-range 30,200  --logy --ymax 1e1 --ymin 1e-2 --x-title "Jet p_{T} [GeV]" --custom-bins "30,40,50,70,90,120,150,5000"  --normalize-by-bin-size --apply-scale-factors --sf-file SF.csv
python CR_2022EE.py --hist-name LeadingMuonPt_CR --output-name LeadingMuonpt_CR_2022_EE --x-range 50,300  --logy --ymax 1e1 --ymin 1e-3 --x-title "Leading Muon p_{T} [GeV]" --custom-bins "50,75,100,125,150,175,200,5000"  --normalize-by-bin-size --apply-scale-factors --sf-file SF.csv
python CR_2022EE.py --hist-name LeadingTopJetPt_CR --output-name LeadingTopJetpt_CR_2022_EE --x-range 350,1000  --logy --ymax 1e1 --ymin 1e-3 --x-title "Top Jet p_{T} [GeV]" --custom-bins "350,400,480,600,5000"  --normalize-by-bin-size --apply-scale-factors --sf-file SF.csv
python CR_2022EE.py --hist-name SubleadingMuonPt_CR --output-name SubleadingMuonpt_CR_2022_EE --x-range 30,60  --logy --ymax 1e1 --ymin 1e-3 --x-title "Subleading Muon p_{T} [GeV]" --custom-bins "30,35,40,45,50,60,5000"  --normalize-by-bin-size --apply-scale-factors --sf-file SF.csv

python CR_2022EE.py --hist-name TopjetnumCR --output-name TopJetnum_CR_2022_EE --x-range 0,5  --logy --ymax 1e4 --ymin 1e-6 --x-title "Topjetnum"  #--normalize-by-bin-size
python CR_2022EE.py --hist-name BjetnumCR --output-name Jetnum_CR_2022_EE --x-range 0,5  --logy --ymax 1e4 --ymin 1e-6 --x-title "Jetnum"

python CR_2022EE.py --hist-name WRMass_CR --output-name WRMass_CR_2022_EE --x-range 350,800 --logy --ymax 1e0 --ymin 1e-5 --x-title "m_{WR} [GeV]" --custom-bins "350,400,450,500,550,600,650,700,800"  --normalize-by-bin-size
python CR_2022EE.py --hist-name "b_met_transverse_massCR" --output-name bmettransversemass_CR_2022_EE --x-range 0,250 --logy --ymax 1e0 --ymin 1e-5 --x-title "b met transverse mass [GeV]" --custom-bins "0,20,40,60,80,100,120,140,160,180,200,220,240,250"  --normalize-by-bin-size

# 데이터 범위 제한 예시 (각 Muon 데이터셋의 범위를 제한)
# python CR_2022EE.py --hist-name WRMass_CR --output-name WRMass_CR_2022_EE --x-range 400,5000 --logy --ymax 1e0 --ymin 1e-5 --x-title "m_{WR} [GeV]" --custom-bins "400,600,800,1000,1200,1500,2000,3000,4000,5000" #--normalize-by-bin-size --muon-e-range "0,2000" --muon-f-range "0,3000" --muon-g-range "0,1000"