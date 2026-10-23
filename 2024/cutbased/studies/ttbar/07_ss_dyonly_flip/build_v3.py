#!/usr/bin/env python3
"""Scenario cbv15_an2_ref_v3 = v2 with the EE same-sign templates replaced by the DY-only flip.

shapes : rEESR_SS / rDYEECR_SS background templates (Flip + its 6 variations, TT, DYJets,
         Nonprompt, Others) <- ddss_dyonly_sf.root. Signal templates and the DY CR data are
         kept from v2; the SR data_obs (Asimov) is rebuilt as the new background sum.
cards  : EE same-sign TT now carries R_TT_Resolved_2024 -- after the DY-only switch it is
         mostly prompt ttbar with a flipped electron, i.e. the thing the e-mu CR normalises.
         The muon same-sign TT (rMuMuSR_SS, rDYMuMuCR_SS) keeps NO rateParam: muon flips are
         negligible, so that TT is nonprompt (06 §11). So the fit runs WITHOUT DROP_SS_TT.
"""
import glob, os, re, shutil
import ROOT
ROOT.gROOT.SetBatch(True); ROOT.TH1.AddDirectory(False)

B = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/combine/scenarios/test"
V2, V3 = B + "/cbv15_an2_ref_v2", B + "/cbv15_an2_ref_v3"
SH2, SH3 = V2 + "/shapes_2024_cbv15_an2_ref_v2.root", V3 + "/shapes_2024_cbv15_an2_ref_v3.root"
DD = os.path.dirname(os.path.abspath(__file__)) + "/ddss_dyonly_sf.root"
REPL = {"rEESR_SS", "rDYEECR_SS"}
BKG = ["Flip", "TT", "DYJets", "Nonprompt", "Others"]

os.makedirs(V3, exist_ok=True)
old, dd = ROOT.TFile.Open(SH2), ROOT.TFile.Open(DD)
out = ROOT.TFile.Open(SH3, "RECREATE")
for k in old.GetListOfKeys():
    reg = k.GetName(); d_in = old.Get(reg); d_out = out.mkdir(reg)
    names = [kk.GetName() for kk in d_in.GetListOfKeys()]
    for n in names:
        if reg in REPL and (n.split("_")[0] in BKG or n == "data_obs"):
            continue                                   # replaced below
        h = d_in.Get(n); d_out.cd(); h.Write(n)
    if reg not in REPL:
        continue
    ref = d_in.Get("TT")
    edges_v2 = [round(ref.GetBinLowEdge(i), 3) for i in range(1, ref.GetNbinsX() + 2)]
    tot = None
    for kk in dd.Get(reg).GetListOfKeys():
        n = kk.GetName()
        if n == "data_obs":
            continue
        h = kk.ReadObj()
        edges = [round(h.GetBinLowEdge(i), 3) for i in range(1, h.GetNbinsX() + 2)]
        assert edges == edges_v2, (reg, n, edges, edges_v2)
        d_out.cd(); h.Write(n)
        if n in BKG:
            if tot is None:
                tot = h.Clone("tot")
            else:
                tot.Add(h)
    if reg == "rDYEECR_SS":
        data = d_in.Get("data_obs")                    # real SS data, unchanged
    else:
        data = tot.Clone("data_obs")                   # blinded SR: Asimov = new background sum
    d_out.cd(); data.Write("data_obs")
    print("  %-11s bkg %8.2f  data_obs %8.2f  (%s)" % (reg, tot.Integral(), data.Integral(),
          "real SS data" if reg == "rDYEECR_SS" else "Asimov"))
out.Close()

# ---- datacards
if os.path.exists(V3 + "/datacards"):
    shutil.rmtree(V3 + "/datacards")
shutil.copytree(V2 + "/datacards", V3 + "/datacards")
n = 0
for c in sorted(glob.glob(V3 + "/datacards/2024/*/*.txt")):
    L = open(c).read().split("\n")
    L = [re.sub(r"\S*shapes_2024_cbv15_an2_ref_v2\.root", SH3, l) for l in L]
    bins = next(l.split()[1:] for l in L if l.startswith("bin ") and len(l.split()) > 5)
    # muon SS TT: no beta (nonprompt). EE SS TT: beta (flipped prompt ttbar).
    L = [l for l in L if not re.match(r"^R_TT_\S+\s+rateParam\s+r(MuMuSR|DYMuMuCR)_SS\s+TT\s", l)]
    add = ["R_TT_Resolved_2024     rateParam %s TT 1 [0.5,1.5]" % b for b in ("rEESR_SS", "rDYEECR_SS") if b in bins]
    i = max(j for j, l in enumerate(L) if " rateParam " in l)
    L[i + 1:i + 1] = [a for a in add if a not in L]
    open(c, "w").write("\n".join(L)); n += 1
print("cards written:", n)
