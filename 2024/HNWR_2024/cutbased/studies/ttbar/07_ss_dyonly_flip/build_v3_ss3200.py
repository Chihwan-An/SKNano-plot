#!/usr/bin/env python3
"""Scenario cbv15_an2_ref_v3_ss3200 = v3 with both resolved same-sign SRs binned like the original
cut-based SR: 800,1000,1200,1400,1600,2000,2400,2800,3200,8000 (single last bin, no tail split).

rMuMuSR_SS : v3 edges (...,3200,3496,4685,5231,8000) are a superset -> merge bins in place.
rEESR_SS   : v3 edges (...,2800,3132,8000) are not -> rebuilt from the 1 GeV sources:
             background = ddss_dyonly_sf_ss3200.root (run_dyonly_sf.sh with --sr-edges ...,3200,8000),
             signal     = cbv15_dc_cards.py output at the same edges (SIG_SRC below),
             data_obs   = Asimov (new background sum), as in v3.
Every other region and every card line is v3 unchanged (cards only get the new shapes path).
"""
import array, glob, os, re, shutil, sys
import ROOT
ROOT.gROOT.SetBatch(True); ROOT.TH1.AddDirectory(False)

B = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/combine/scenarios/test"
V3, NEW = B + "/cbv15_an2_ref_v3", B + "/cbv15_an2_ref_v3_ss3200"
SH3, SHN = V3 + "/shapes_2024_cbv15_an2_ref_v3.root", NEW + "/shapes_2024_cbv15_an2_ref_v3_ss3200.root"
H = os.path.dirname(os.path.abspath(__file__))
DD = H + "/ddss_dyonly_sf_ss3200.root"
SIG_SRC = B + "/cbv15_tmp_ss3200sig/shapes_2024_cbv15_tmp_ss3200sig.root"
EDGES = [800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 8000]
BKG = ["Flip", "TT", "DYJets", "Nonprompt", "Others"]


def edges_of(h):
    return [round(h.GetBinLowEdge(i), 3) for i in range(1, h.GetNbinsX() + 2)]


def merge(h, n):
    old = edges_of(h)
    assert all(e in old for e in EDGES), (n, old)
    r = h.Rebin(len(EDGES) - 1, n, array.array("d", EDGES)); r.SetDirectory(0)
    assert abs(r.Integral() - h.Integral()) <= 1e-9 * max(1.0, abs(h.Integral())), n
    return r


old, dd, sg = ROOT.TFile.Open(SH3), ROOT.TFile.Open(DD), ROOT.TFile.Open(SIG_SRC)
if not (old and dd and sg): sys.exit("missing input")
os.makedirs(NEW, exist_ok=True)
out = ROOT.TFile.Open(SHN, "RECREATE")
for k in old.GetListOfKeys():
    reg = k.GetName(); d_in = old.Get(reg); d_out = out.mkdir(reg)
    names = [kk.GetName() for kk in d_in.GetListOfKeys()]
    if reg == "rMuMuSR_SS":
        for n in names:
            d_out.WriteTObject(merge(d_in.Get(n), n), n)
        print("  rMuMuSR_SS merged  (%d objects)" % len(names))
        continue
    if reg != "rEESR_SS":
        for n in names:
            d_out.WriteTObject(d_in.Get(n), n)
        continue
    # rEESR_SS: same object names as v3, new content
    new, tot = {}, None
    for kk in dd.Get(reg).GetListOfKeys():
        n = kk.GetName()
        if n == "data_obs": continue
        new[n] = kk.ReadObj()
    s = sg.Get(reg)
    for n in names:
        if n.startswith("WR"): new[n] = s.Get(n)
    for n in BKG:
        if tot is None: tot = new[n].Clone("data_obs"); tot.SetDirectory(0)
        else: tot.Add(new[n])
    new["data_obs"] = tot
    miss, extra = set(names) - set(new), set(new) - set(names)
    assert not miss, ("missing in rebuilt rEESR_SS", sorted(miss)[:10])
    for n in names:
        h = new[n]
        assert edges_of(h) == [float(e) for e in EDGES], (n, edges_of(h))
        d_out.WriteTObject(h, n)
    print("  rEESR_SS rebuilt   bkg %.2f  (v3 %.2f)  dropped extra %d" % (tot.Integral(), d_in.Get("data_obs").Integral(), len(extra)))
out.Close()

if os.path.exists(NEW + "/datacards"): shutil.rmtree(NEW + "/datacards")
shutil.copytree(V3 + "/datacards", NEW + "/datacards",
                ignore=shutil.ignore_patterns("*.log", "*.root", "higgsCombine*", "*.res"))
n = 0
for c in sorted(glob.glob(NEW + "/datacards/2024/*/card_*.txt")):
    t = re.sub(r"\S*shapes_2024_cbv15_an2_ref_v3\.root", SHN, open(c).read())
    open(c, "w").write(t); n += 1
print("cards written:", n)
