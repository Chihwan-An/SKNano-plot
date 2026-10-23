#!/usr/bin/env python3
"""post_processor_chsplit.py 의 데이터 stream 처리 점검 (수정 전 로직 기준으로 '무엇이 새고 있었나' 를 센다).
region 의 cfg["data"] 패턴에 맞는 데이터 파일 = data_obs. 맞지 않는 데이터 파일은 (수정 전) classify_file 에서
MC 로 떨어져 SAMPLE_MAP 에 안 걸리므로 "Others" 에 raw count 로 더해졌다.
** CR 만 센다. blind 인 SR 은 건너뛴다 (SR 데이터 수치를 출력하지 않기 위함). **
    python3 audit_datastream_leak.py"""
import sys, glob, os, ROOT, importlib.util
ROOT.gROOT.SetBatch(True); ROOT.gErrorIgnoreLevel = ROOT.kError
T = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test/"
sys.argv = ["x"]
spec = importlib.util.spec_from_file_location("pp", T + "cbv15/post_processor_chsplit.py.bak_20260919_datastream")   # 수정 전 REGION_CONFIG
pp = importlib.util.module_from_spec(spec); spec.loader.exec_module(pp)
D = T + "cbv15dc/input2024/"
datafiles = [p for p in sorted(glob.glob(D + "*.root")) if os.path.basename(p).startswith(("EGamma", "Muon", "SingleMuon"))]


def integ(p, hs):
    f = ROOT.TFile.Open(p); v = 0.0
    for h in (hs if isinstance(hs, list) else [hs]):
        o = f.Get("Central/" + h); v += o.Integral(0, -1) if o else 0.0
    f.Close(); return v


for reg, cfg in pp.REGION_CONFIG.items():
    if reg.startswith("n") or cfg.get("blind"):
        continue
    pats = cfg["data"]
    sel = sum(integ(p, cfg["hist"]) for p in datafiles if any(x in os.path.basename(p) for x in pats))
    leak = sum(integ(p, cfg["hist"]) for p in datafiles if not any(x in os.path.basename(p) for x in pats))
    print("%-16s data(sel) %8.0f   leak->Others %6.0f   streams=%s" % (reg, sel, leak, pats))
