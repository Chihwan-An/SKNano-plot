#!/usr/bin/env python3
"""Inputs for the AN2019_083 App. J study (data-driven ttbar from the e-mu sideband), 2024.

The cut-based analyzer output (HNWR/RFlav/2024) has no low-mass (m_WR < 800 GeV) regions -- the low-mass CR block
of HNWR.cc is an empty stub -- so the regions are rebuilt from the BDT preselection RNTuples, which carry no mass cut:
    $SKNANO_OUTPUT/HNWR_BDT_presel_3SR/2024/<sample>.root : Central_<region>_BDTTree_<resolved|boosted>
    resolved: m = mlljj,     high = mll > 400 && m > 800,  low = mll > 200 && m < 800
    boosted : m = ml1fatjet, high = mll > 200 && m > 800,  low = mll > 200 && m < 800
Same-flavour data are read in the LOW-mass region only; the high-mass SR data are never touched (blinded).
Data streams follow plot/cutbased/config.py: ee / e+mu-jet (EMJ) -> EGamma, mumu / e-mu / mu+e-jet (MEJ) -> Muon.
Output: <out>/emu_method_hists_2024.root  (<region>/<low|high>/<group>[_<syst>Up|Down], data_obs, sig_<point>)
    ./condor/in_container.sh python3 make_emu_method_hists_2024.py --out DIR        (from plot/cutbased)
"""
import argparse, fnmatch, glob, os, re, sys
import numpy as np, ROOT
sys.path.insert(0, "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased")
import config  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--prod", default="/gv0/Users/achihwan/SKNanoOutput/HNWR_BDT_presel_3SR/2024")
ap.add_argument("--out", required=True)
ap.add_argument("--threads", type=int, default=8)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
ROOT.gROOT.SetBatch(True); ROOT.gErrorIgnoreLevel = ROOT.kError; ROOT.TH1.AddDirectory(False)
ROOT.EnableImplicitMT(a.threads)

# region -> (tree, mass variable, mll cut of the high-mass selection, data stream globs, same-flavour?)
REG = {
    "Res_EE":    ("Central_SR_EE_BDTTree_resolved",     "mlljj",     400, ["EGamma*"], True),
    "Res_MM":    ("Central_SR_MM_BDTTree_resolved",     "mlljj",     400, ["Muon*"],   True),
    "Res_EM":    ("Central_CR_FLV_EM_BDTTree_resolved", "mlljj",     400, ["Muon*"],   False),
    "Boost_EE":  ("Central_SR_EE_BDTTree_boosted",      "ml1fatjet", 200, ["EGamma*"], True),
    "Boost_MM":  ("Central_SR_MM_BDTTree_boosted",      "ml1fatjet", 200, ["Muon*"],   True),
    "Boost_EMJ": ("Central_CR_FLV_EM_BDTTree_boosted",  "ml1fatjet", 200, ["EGamma*"], False),   # e (tight) + mu-jet
    "Boost_MEJ": ("Central_CR_FLV_ME_BDTTree_boosted",  "ml1fatjet", 200, ["Muon*"],   False),   # mu (tight) + e-jet
}
LOW = np.array([200, 300, 400, 500, 600, 700, 800], float)
HIGH = {"Res": np.array([800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 8000], float),
        "Boost": np.array([800, 1000, 1200, 1500, 1800, 8000], float)}


def classify(stem):
    if stem.startswith(("EGamma", "Muon")):
        return "data"
    if "WRtoN" in stem:
        return "sig_" + re.sub(r"^.*?(WRtoN\w+?)_MWR(\d+)_N(\d+).*$", r"\1_WR\2_N\3", stem)
    if stem.startswith("QCD"):
        return None                                   # QCD MC is not part of the cut-based background model
    g, _ = config.classify_sample(stem)
    return g


H = {}


def add(key, h):
    if key in H:
        H[key].Add(h)
    else:
        H[key] = h.Clone("_".join(key)); H[key].SetDirectory(0)


files = sorted(p for p in glob.glob(os.path.join(a.prod, "*.root")))
for ip, p in enumerate(files):
    stem = os.path.basename(p)[:-5]; grp = classify(stem)
    if grp is None:
        continue
    f = ROOT.TFile.Open(p); keys = set(k.GetName() for k in f.GetListOfKeys()); f.Close()
    for reg, (tree, mvar, mllhi, streams, sf) in REG.items():
        if tree not in keys:
            continue
        isdata = grp == "data"
        if isdata and not any(fnmatch.fnmatch(stem, s) for s in streams):
            continue
        if grp.startswith("sig_") and sf:
            continue                                   # signal is only needed in the flavour sidebands (Table 54)
        df = ROOT.RDataFrame(tree, p)
        cols = [str(c) for c in df.GetColumnNames()]
        # nominal = weight_Central (all scale factors; reproduces the HNWR/RFlav histograms). The bare "weight" column is
        # 7% higher. The object-variation columns (JES, JER, lepton scale/resolution) are 0 in the Central tree -- they
        # only live in their own <syst>_<Up|Down>_* trees -- so only the weight-type systematics are taken here.
        SHAPE_ONLY = ("JES", "JER", "ElectronScale", "ElectronRes", "MuonScale", "MuonRes")
        systs = [] if (isdata or grp.startswith("sig_")) else sorted(c[len("weight_"):] for c in cols
                                                                   if re.match(r"^weight_.*_(Up|Down)$", c) and not c[len("weight_"):].startswith(SHAPE_ONLY))
        wnom = "weight_Central" if not isdata else None
        booked = []
        for rng, sel, edges in (("low", f"mll > 200 && {mvar} < 800 && {mvar} >= 200", LOW),
                                ("high", f"mll > {mllhi} && {mvar} >= 800", HIGH[reg.split('_')[0]])):
            if isdata and sf and rng == "high":
                continue                               # blinded: never read same-flavour high-mass data
            d = df.Filter(sel).Define("mfit", f"({mvar} >= {edges[-1]}) ? {edges[-1] - 1.0} : (double){mvar}")   # overflow into the last bin
            model = ROOT.RDF.TH1DModel(f"h_{reg}_{rng}", "", len(edges) - 1, edges)
            if isdata:
                booked.append(((reg, rng, "data_obs"), d.Histo1D(model, "mfit")))
            else:
                booked.append(((reg, rng, grp), d.Histo1D(model, "mfit", wnom)))
                for s in systs:
                    booked.append(((reg, rng, f"{grp}_{s}"), d.Histo1D(model, "mfit", f"weight_{s}")))
        for key, hp in booked:
            h = hp.GetValue(); h.Sumw2(); add(key, h)
    print(f"[{ip + 1}/{len(files)}] {stem} -> {grp}", flush=True)

out = ROOT.TFile.Open(os.path.join(a.out, "emu_method_hists_2024.root"), "RECREATE")
for (reg, rng, name), h in sorted(H.items()):
    d = out.Get(f"{reg}/{rng}") or out.mkdir(f"{reg}/{rng}")
    d.cd(); h.Write(name)
out.Close()
print("wrote", os.path.join(a.out, "emu_method_hists_2024.root"), len(H), "histograms")
