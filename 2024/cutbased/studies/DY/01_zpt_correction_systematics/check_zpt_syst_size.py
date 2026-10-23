#!/usr/bin/env python3
"""Z-pT 보정 C(gen Z pT) 의 theory variation 이 shape-only 정규화 뒤에 얼마나 남는지 JSON 에서 직접 계산.
입력: HNWR/data/corrections/zpt/dy_zpt_nlo_lo.json (make_dy_zpt_nlo_lo.py 산출물), variant Zpt_genZ_HT40, era 2024.
    python3 check_zpt_syst_size.py"""
import json, numpy as np
J = json.load(open("/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/HNWR/data/corrections/zpt/dy_zpt_nlo_lo.json"))
print("normalization:", J["meta"]["normalization"], "| norm_min_pt:", J["meta"]["low_pt_handling"]["norm_min_pt_gev"])
d = J["Zpt_genZ_HT40"]["2024"]; e = np.array(d["edges"]); c = np.array(d["ZPTReweight"])
sel = (e[:-1] >= 50) & (c > 0)
for g in ["QCDScale", "QCDPDFError", "QCDPDFAlphaS", ""]:
    up = np.array(d["ZPTReweight_%sUp" % g]); dn = np.array(d["ZPTReweight_%sDown" % g])
    ru = (up / c - 1)[sel] * 100; rd = (dn / c - 1)[sel] * 100
    print("%-14s max|up| %.2f%%  max|down| %.2f%%   tail bins (250-350, 350-500, 500-1000): up %s  down %s"
          % (g or "TOTAL", np.nanmax(abs(ru)), np.nanmax(abs(rd)), np.round(ru[-3:], 2), np.round(rd[-3:], 2)))
print("MC stat rel. error in the tail bins [%]:", np.round(np.array(d["ZPTReweight_stat"])[-3:] / c[-3:] * 100, 2))
print("C in the tail bins:", np.round(c[-3:], 3))
