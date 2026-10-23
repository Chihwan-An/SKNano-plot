#!/usr/bin/env python3
"""card 의 TT 그룹에 실제로 무엇이 들어가는지 (ttbar 2L / tW / single-top s,t-channel) region 별 yield 로 확인.
입력: BDT/SR/test/cbv15dc/input2024 (RFlav_DYCRCharge/2024 로 가는 v13 식 이름의 symlink farm).
post_processor 의 SAMPLE_MAP 은 부분일치 + 첫 일치 우선이라 "ST" 가 ST_tch / ST_sch 보다 먼저 걸린다.
    python3 audit_tt_composition.py          (일반 python3 + ROOT 로 충분)"""
import ROOT, glob, collections
ROOT.gROOT.SetBatch(True); ROOT.gErrorIgnoreLevel = ROOT.kError
D = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test/cbv15dc/input2024/"


def integ(p, h):
    f = ROOT.TFile.Open(p); o = f.Get("Central/" + h); v = o.Integral(0, -1) if o else 0.0; f.Close(); return v


comp = collections.OrderedDict([("ttbar 2L", ["TTLL*"]), ("tW", ["ST_tW*"]), ("ST s-ch", ["ST_sch*"]), ("ST t-ch", ["ST_tch*"])])
for h in ["FlavCR_Resolved_EM_mlljj", "SR_Resolved_EE_mlljj", "SR_Resolved_MM_mlljj", "FlavCR_Boosted_EMJ_mlljj",
          "FlavCR_Boosted_MEJ_mlljj", "SR_Boosted_EE_mlljj", "SR_Boosted_MM_mlljj"]:          # MC only: SR 도 MC 는 읽어도 된다
    y = {k: sum(integ(p, h) for g in gl for p in glob.glob(D + g + ".root")) for k, gl in comp.items()}
    tot = sum(y.values())
    print("%-28s" % h, "  ".join("%s %.1f (%.1f%%)" % (k, v, 100 * v / tot if tot else 0) for k, v in y.items()))
