#!/usr/bin/env python3
"""시나리오 shapes 파일에서 e-mu CR 의 data_obs / 그룹별 yield 를 읽어 data/MC 와 (data-nonTT)/TT 를 출력.
    python3 audit_scenario_cr_yields.py [tag ...]      기본: cbv15_an2_ref cbv15_an2_ref_fixstream"""
import ROOT, glob, os, sys
ROOT.gROOT.SetBatch(True); ROOT.gErrorIgnoreLevel = ROOT.kError
B = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/combine/scenarios/test/"
for tag in (sys.argv[1:] or ["cbv15_an2_ref", "cbv15_an2_ref_fixstream"]):
    p = glob.glob(B + tag + "/shapes_2024_*.root")
    if not p: print(tag, "no shapes"); continue
    f = ROOT.TFile.Open(p[0]); print(tag)
    for ch in ["rFlvCR", "bFlvEMuCR", "bFlvMuECR"]:
        d = f.Get(ch); y = {n: d.Get(n).Integral() for n in ["data_obs", "TT", "DYJets", "Nonprompt", "Others"]}
        mc = sum(v for k, v in y.items() if k != "data_obs")
        print("   %-10s" % ch, {k: round(v, 1) for k, v in y.items()}, " data/MC %.3f  (data-nonTT)/TT %.3f" % (y["data_obs"] / mc, (y["data_obs"] - (mc - y["TT"])) / y["TT"]))
    f.Close()
