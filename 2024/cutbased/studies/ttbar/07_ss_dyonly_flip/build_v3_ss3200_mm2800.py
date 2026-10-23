#!/usr/bin/env python3
"""Scenario cbv15_an2_ref_v3_ss3200_mm2800 = cbv15_an2_ref_v3_ss3200 with both mu-mu same-sign regions
(rMuMuSR_SS, rDYMuMuCR_SS) binned 800,1000,1200,1400,1600,2000,2400,2800,8000 (one last bin from 2800).
Both regions are ...,2800,3200,8000 in ss3200, a superset -> every object (backgrounds, systematics, signals,
data_obs) is merged in place. Every other region and every card line is ss3200 unchanged (new shapes path only).
"""
import array, glob, os, re, shutil, sys
import ROOT
ROOT.gROOT.SetBatch(True); ROOT.TH1.AddDirectory(False)

B = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/combine/scenarios/test"
SRC_TAG, NEW_TAG = "cbv15_an2_ref_v3_ss3200", "cbv15_an2_ref_v3_ss3200_mm2800"
SRC, NEW = f"{B}/{SRC_TAG}", f"{B}/{NEW_TAG}"
SHS, SHN = f"{SRC}/shapes_2024_{SRC_TAG}.root", f"{NEW}/shapes_2024_{NEW_TAG}.root"
EDGES = [800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 8000]
MERGE = ("rMuMuSR_SS", "rDYMuMuCR_SS")


def edges_of(h):
    return [round(h.GetBinLowEdge(i), 3) for i in range(1, h.GetNbinsX() + 2)]


def merge(h, n):
    old = edges_of(h)
    assert all(e in old for e in EDGES), (n, old)
    r = h.Rebin(len(EDGES) - 1, n, array.array("d", EDGES)); r.SetDirectory(0)
    assert abs(r.Integral() - h.Integral()) <= 1e-9 * max(1.0, abs(h.Integral())), n
    return r


src = ROOT.TFile.Open(SHS)
if not src: sys.exit("missing " + SHS)
os.makedirs(NEW, exist_ok=True)
out = ROOT.TFile.Open(SHN, "RECREATE")
for k in src.GetListOfKeys():
    reg = k.GetName(); d_in = src.Get(reg); d_out = out.mkdir(reg)
    names = [kk.GetName() for kk in d_in.GetListOfKeys()]
    for n in names:
        h = d_in.Get(n)
        d_out.WriteTObject(merge(h, n) if reg in MERGE else h, n)
    if reg in MERGE:
        print(f"  {reg} merged ({len(names)} objects)  bkg-free data_obs {d_in.Get('data_obs').Integral():.2f}")
out.Close()

if os.path.exists(NEW + "/datacards"): shutil.rmtree(NEW + "/datacards")
shutil.copytree(SRC + "/datacards", NEW + "/datacards",
                ignore=shutil.ignore_patterns("*.log", "*.root", "higgsCombine*", "*.res"))
n = 0
for c in sorted(glob.glob(NEW + "/datacards/2024/*/card_*.txt")):
    t = re.sub(r"\S*shapes_2024_" + re.escape(SRC_TAG) + r"\.root", SHN, open(c).read())
    assert SHN in t, c
    open(c, "w").write(t); n += 1
print("cards written:", n)
