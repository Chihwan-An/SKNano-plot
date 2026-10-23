#!/usr/bin/env python3
"""Rebin the regenerated boosted-SR block (1 GeV) onto the card's binning and splice it
into the scenario shapes file.

The post_processor writes SR templates with 1-GeV bins; cbv15_dc_cards.py rebins them to
the card edges (BOOST_EDGE). Splicing the raw file in directly leaves combine fitting 7200
mostly-empty bins, which does not converge. The card edges are a subset of the 1-GeV edges,
so TH1::Rebin reproduces the card binning exactly -- verified below on the processes the
stream fix does not touch (TT/DYJets/Nonprompt must match the old file bin by bin).
"""
import array, os, sys
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.TH1.AddDirectory(False)

B = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/combine/scenarios/test"
H = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased/studies/ttbar/03_combine_validation/sr_fixstream"
SRC = B + "/cbv15_an2_ref_flvos/shapes_2024_cbv15_an2_ref_flvos.root"   # OS-only rFlvCR already in
DST = B + "/cbv15_an2_ref_v2"
REPL = {"bEESR", "bMuMuSR"}
UNCHANGED = ("TT", "DYJets", "Nonprompt")     # the stream fix only touches Others

old = ROOT.TFile.Open(SRC)
new = ROOT.TFile.Open(H + "/shapes_2024_bSR_fixstream.root")
os.makedirs(DST, exist_ok=True)
out = ROOT.TFile.Open(DST + "/shapes_2024_cbv15_an2_ref_v2.root", "RECREATE")

bad = []
for k in old.GetListOfKeys():
    reg = k.GetName()
    d_out = out.mkdir(reg)
    if reg not in REPL:
        d_in = old.Get(reg)
        for kk in d_in.GetListOfKeys():
            h = kk.ReadObj(); d_out.cd(); h.Write(kk.GetName())
        continue

    ref = old.Get(reg + "/TT")
    edges = array.array("d", [ref.GetBinLowEdge(i) for i in range(1, ref.GetNbinsX() + 2)])
    nb = len(edges) - 1
    d_in = new.Get(reg)
    for kk in d_in.GetListOfKeys():
        name = kk.GetName()
        h = kk.ReadObj()
        r = h.Rebin(nb, name + "_rb", edges)
        # sanity: the rebin must preserve the integral
        if abs(r.Integral() - h.Integral()) > 1e-6 * max(1.0, abs(h.Integral())):
            bad.append((reg, name, "integral"))
        if name.split("_")[0] in UNCHANGED or name in UNCHANGED:
            ref_h = old.Get("%s/%s" % (reg, name))
            if ref_h:
                for i in range(1, nb + 1):
                    if abs(r.GetBinContent(i) - ref_h.GetBinContent(i)) > 1e-4:
                        bad.append((reg, name, "bin%d %.4f vs %.4f" % (i, r.GetBinContent(i), ref_h.GetBinContent(i))))
                        break
        d_out.cd(); r.Write(name)
    print("  %-10s rebinned %d hists -> %d bins %s" % (reg, d_in.GetNkeys(), nb, list(edges)))

out.Close()
print("\n검증: 변경되지 않아야 할 process(TT/DYJets/Nonprompt)의 불일치 =", len(bad))
for b in bad[:10]:
    print("   !!", b)
sys.exit(1 if bad else 0)
