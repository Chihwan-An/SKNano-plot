#!/usr/bin/env python3
"""Tagger scores of the boosted-candidate fatjet (no LSF3 requirement), 2024 skims: signal points or one background file chunk.
Candidate, as the boosted branch of HNWR.cc without the LSF3 cut (re-implemented on NanoAOD):
  tight e = HEEP, pT > 53; tight mu = highPtId == 2, tkRelIso < 0.1, TuneP pT > 53; the leading tight lepton has pT > 60 and the
  channel flavour (EE: electron, MM: muon)
  AK8: pT > 200, |eta| < 2.5, msoftdrop > 40, TIGHT jet ID from the energy fractions (neHEF < 0.99, neEmEF < 0.9, nConst > 1,
  chHEF > 0.01, chMult > 0; no lepton-fraction cuts); the first fatjet in pT order with |dPhi(leading lepton, J)| > 2.0;
  m(leading lepton + J) > 800
  (raw NanoAOD pT / msoftdrop, no JEC/JER lanes; no loose-lepton / low-m_ll requirements)
Stored for the candidate: FatJet_globalParT3_XWWqqev, _XWWqqmv and FatJet_lsf3 (lsf3 < 0 -> first bin), 200 bins in [0,1].
Signal (--points CH:MWR:MN,...): only the channel of the sample, weights = genWeight sign. Background (--sample, --file-list): both
channels, weights = genWeight (xsec / sumW applied when plotting).
  boosted_fatjet_tagger_hists.py --points EE:4000:200,... --out <dir>
  boosted_fatjet_tagger_hists.py --sample TTto2L2Nu_TuneCP5 --file-list <txt> --out <dir>"""
import argparse, glob, os
import numpy as np
import ROOT

ap = argparse.ArgumentParser()
ap.add_argument("--points", default=None, help="signal: comma list CH:MWR:MN")
ap.add_argument("--sample", default=None, help="background sample name")
ap.add_argument("--file-list", default=None)
ap.add_argument("--skim-dir", default="/gv0/Users/achihwan/SkimNano15/2024")
ap.add_argument("--out", required=True)
ap.add_argument("--mt", type=int, default=4)
ap.add_argument("--test", action="store_true", help="20000 events (signal) / first file 50000 events (background), no MT, no output")
a = ap.parse_args()
ROOT.gROOT.SetBatch(True)
if a.mt > 1 and not a.test: ROOT.EnableImplicitMT(a.mt)
os.makedirs(a.out, exist_ok=True)

ROOT.gInterpreter.Declare(r'''
#include "ROOT/RVec.hxx"
#include "Math/Vector4D.h"
#include "Math/VectorUtil.h"
using ROOT::VecOps::RVec;
using P4 = ROOT::Math::PtEtaPhiMVector;
// {pass, XWWqqev, XWWqqmv, lsf3} of the boosted-candidate fatjet
RVec<float> boostCand(bool isEE,
                      const RVec<float>& ept, const RVec<float>& eeta, const RVec<float>& ephi, const RVec<bool>& eheep,
                      const RVec<float>& mpt, const RVec<float>& meta, const RVec<float>& mphi, const RVec<UChar_t>& mhpt, const RVec<float>& mtk,
                      const RVec<float>& mtunep,
                      const RVec<float>& fpt, const RVec<float>& feta, const RVec<float>& fphi, const RVec<float>& fmass, const RVec<float>& fsd,
                      const RVec<float>& flsf, const RVec<float>& fev, const RVec<float>& fmv,
                      const RVec<float>& fneHEF, const RVec<float>& fneEmEF, const RVec<float>& fchHEF, const RVec<UChar_t>& fchMult, const RVec<UChar_t>& fneMult) {
    RVec<float> out = {0, -1, -1, -1};
    float lpt = 0, leta = 0, lphi = 0; bool lIsE = false;
    for (size_t i = 0; i < ept.size(); ++i) if (eheep[i] && ept[i] > 53. && ept[i] > lpt) { lpt = ept[i]; leta = eeta[i]; lphi = ephi[i]; lIsE = true; }
    for (size_t i = 0; i < mpt.size(); ++i) {
        float pt = mpt[i] * mtunep[i];
        if (mhpt[i] == 2 && mtk[i] < 0.1 && pt > 53. && pt > lpt) { lpt = pt; leta = meta[i]; lphi = mphi[i]; lIsE = false; }
    }
    if (lpt <= 60. || lIsE != isEE) return out;
    P4 l(lpt, leta, lphi, isEE ? 0.000511 : 0.1057);
    std::vector<size_t> idx(fpt.size()); for (size_t i = 0; i < idx.size(); ++i) idx[i] = i;
    std::sort(idx.begin(), idx.end(), [&](size_t x, size_t y) { return fpt[x] > fpt[y]; });
    for (size_t k : idx) {
        if (fpt[k] <= 200. || std::fabs(feta[k]) >= 2.5 || fsd[k] <= 40.) continue;
        if (!(fneHEF[k] < 0.99 && fneEmEF[k] < 0.9 && (int(fchMult[k]) + int(fneMult[k])) > 1 && fchHEF[k] > 0.01 && fchMult[k] > 0)) continue;
        P4 j(fpt[k], feta[k], fphi[k], fmass[k]);
        if (std::fabs(ROOT::Math::VectorUtil::DeltaPhi(l, j)) <= 2.0) continue;
        if ((l + j).M() <= 800.) return out;      // the analyzer takes the first away fatjet and then cuts on m(lJ)
        out = {1, fev[k], fmv[k], flsf[k]};
        return out;
    }
    return out;
}
''')
ARGS = ("Electron_pt, Electron_eta, Electron_phi, Electron_cutBased_HEEP, Muon_pt, Muon_eta, Muon_phi, Muon_highPtId, Muon_tkRelIso, "
        "Muon_tunepRelPt, FatJet_pt, FatJet_eta, FatJet_phi, FatJet_mass, FatJet_msoftdrop, FatJet_lsf3, FatJet_globalParT3_XWWqqev, "
        "FatJet_globalParT3_XWWqqmv, FatJet_neHEF, FatJet_neEmEF, FatJet_chHEF, FatJet_chMultiplicity, FatJet_neMultiplicity")
NB = 200
NBL, LMIN = 240, -8.0    # log10(score) histogram: 30 bins per decade from 1e-8 to 1, to resolve the pile-up near 0
TAGCOL = {"XWWqqev": 1, "XWWqqmv": 2, "lsf3": 3}

def book(df, chans, name):
    b = {"total": df.Sum("w"), "total_raw": df.Count()}
    for ch in chans:
        d = df.Define(f"bc_{ch}", f"boostCand({'true' if ch == 'EE' else 'false'}, {ARGS})").Filter(f"bc_{ch}[0] > 0.5")
        b[f"n_{ch}"] = d.Sum("w"); b[f"nraw_{ch}"] = d.Count()
        for tag, k in TAGCOL.items():
            d = d.Define(f"s_{ch}_{tag}", f"std::min(std::max(bc_{ch}[{k}], 0.0f), 0.99999f)")
            b[f"h_{ch}_{tag}"] = d.Histo1D((f"h_{name}_{ch}_{tag}", "", NB, 0., 1.), f"s_{ch}_{tag}", "w")
            # same score in log10 bins; score == 0 goes into the first bin
            b[f"h_{ch}_{tag}_log"] = d.Define(f"l_{ch}_{tag}", f"s_{ch}_{tag} > 0 ? std::max(float(std::log10(s_{ch}_{tag})), float({LMIN})) : float({LMIN})") \
                                      .Histo1D((f"hl_{name}_{ch}_{tag}", "", NBL, LMIN, 0.), f"l_{ch}_{tag}", "w")
    return b

def finish(b):
    res = {"log_edges": np.logspace(LMIN, 0, NBL + 1)}
    for k, v in b.items():
        if k.startswith("h_"):
            h = v.GetValue(); n = NBL if k.endswith("_log") else NB
            res[k] = np.array([h.GetBinContent(i) for i in range(1, n + 1)])
        else:
            res[k] = float(v.GetValue())
    return res

jobs = []
if a.points:
    TAG = {"EE": "WRtoNEltoElElJJ", "MM": "WRtoNMutoMuMuJJ"}
    for p in a.points.split(","):
        ch, mwr, mn = p.split(":")
        files = sorted(glob.glob(f"{a.skim_dir}/Skim_HNWR3SR_{TAG[ch]}_MWR{mwr}_N{mn}/tree_*.root"))
        df = ROOT.RDataFrame("Events", files)
        if a.test: df = df.Range(20000)
        df = df.Define("w", "genWeight > 0 ? 1.0 : -1.0")
        jobs.append((f"{ch}_MWR{mwr}_N{mn}", [ch], book(df, [ch], p.replace(":", "_"))))
else:
    files = [l.strip() for l in open(a.file_list) if l.strip()]
    if a.test: files = files[:1]
    df = ROOT.RDataFrame("Events", files)
    if a.test: df = df.Range(50000)
    df = df.Define("w", "double(genWeight)")
    jobs.append((os.path.basename(a.file_list), ["EE", "MM"], book(df, ["EE", "MM"], a.sample)))

ROOT.RDF.RunGraphs([v for *_, b in jobs for v in b.values()])
for name, chans, b in jobs:
    res = finish(b)
    if a.sample: res["sample"] = a.sample
    if not a.test: np.savez(f"{a.out}/{name}.npz", **res)
    msg = []
    for ch in chans:
        n = res[f"n_{ch}"]
        if n <= 0: msg.append(f"{ch}: 0 selected"); continue
        ev, mv, ls = res[f"h_{ch}_XWWqqev"], res[f"h_{ch}_XWWqqmv"], res[f"h_{ch}_lsf3"]
        msg.append(f"{ch}: selected {res[f'nraw_{ch}']:.0f} ({n / res['total'] * 100:.2f}%), of those XWWqqev>0.5 {ev[100:].sum() / n * 100:.2f}%, "
                   f"XWWqqmv>0.5 {mv[100:].sum() / n * 100:.2f}%, LSF3>0.75 {ls[150:].sum() / n * 100:.1f}%")
    print(f"{name}: " + " | ".join(msg), flush=True)
print("BOOSTED_FATJET_TAGGER_HISTS_DONE")
