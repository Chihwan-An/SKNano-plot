#!/usr/bin/env python3
"""OS SR 에서 비DY MC 를 빼고 남은 DY 를 flip 했을 때, 그 결과가 'OS DY MC 를 직접 flip 한 것' 과 맞는가.

--dy-only 는  Flip_DY = Flip(OS 데이터) - Flip(비DY OS MC)  로 데이터 기반 DY 를 만든다.
그것이 정말 DY 라면  Flip(OS DY MC)  와 같아야 한다. 둘의 비 = OS SR 의 DY data/MC.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util, json
import numpy as np

spec = importlib.util.spec_from_file_location("dd", os.path.join(os.path.dirname(os.path.abspath(__file__)), "chargeflip_ddss_dyonly.py"))
dd = importlib.util.module_from_spec(spec); spec.loader.exec_module(dd)

T = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test"
J = json.load(open(T + "/data/chargeflip/chargeflip_ptshift_ee2024_sf3roofit.json"))
d = dd.load(T + "/data/chargeflip/dumps_v4/all")
w_all, _ = dd.new_weights(J, d, sf2=True)
isdata = d["grp"] == "DATA"

EDG = {"rEESR_SS":  [800,1000,1200,1400,1600,2000,2400,2800,3132,8000],
       "rDYEECR_SS":[800,1000,1200,1400,1600,2000,2400,2800,3200,8000]}
for reg, edges in EDG.items():
    sel = dd.SEL[reg](d)
    osd  = sel & isdata & ~d["ss"]
    osmc = sel & ~isdata & ~d["ss"] & (d["grp"] != "SIG")
    def F(mask, extra=None):
        w = w_all[mask] if extra is None else w_all[mask] * extra
        v, _ = dd.fill(d["m_lljj"][mask], w, edges); return float(v.sum())
    def N(mask, extra=None):
        w = np.ones(int(mask.sum())) if extra is None else extra
        v, _ = dd.fill(d["m_lljj"][mask], w, edges); return float(v.sum())

    f_data = F(osd)
    nonDY  = osmc & (d["grp"] != "DY")
    onlyDY = osmc & (d["grp"] == "DY")
    f_nonDY = F(nonDY, d["weight"][nonDY])
    f_DYmc  = F(onlyDY, d["weight"][onlyDY])
    f_dd    = f_data - f_nonDY

    print("\n=== %s ===" % reg)
    print("  OS 쪽 원 yield        데이터 %9.1f   MC 합 %9.1f   (DY %8.1f / 비DY %8.1f)"
          % (N(osd), N(osmc, d["weight"][osmc]), N(onlyDY, d["weight"][onlyDY]), N(nonDY, d["weight"][nonDY])))
    print("  flip weight 적용 후")
    print("    Flip(OS 데이터)                 %8.2f   <- 현행 baseline 의 Flip" % f_data)
    print("    Flip(비DY OS MC)   빼는 값      %8.2f" % f_nonDY)
    print("    = 데이터 기반 DY flip            %8.2f   <- --dy-only 의 Flip" % f_dd)
    print("    Flip(OS DY MC)     직접 계산     %8.2f" % f_DYmc)
    print("    비  (데이터기반 DY) / (DY MC)    %8.3f   <- OS SR 의 DY data/MC" % (f_dd / f_DYmc if f_DYmc else float("nan")))
