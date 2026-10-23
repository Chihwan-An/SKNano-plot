#!/usr/bin/env python3
"""Tagger scores of the boosted SR / boosted Flavor CR fatjet, 2024 skims: signal points or one background file chunk.

Unlike boosted_fatjet_tagger_hists.py, which stopped at the "boosted candidate fatjet" (lead lepton + away fatjet +
m(lJ) > 800), this reproduces the full boosted branch of HNWR.cc -- everything except the LSF3 cut itself, which is what
the tagger is meant to replace. Re-implemented on NanoAOD:
  leptons   pt > 53; electrons |eta| < 2.5 without the ECAL gap, tight = HEEP, loose = HEEP or the Loose WP of
            vidNestedWPBitmap with the isolation cut ignored; muons |eta| < 2.4 on TuneP pt, loose = highPtId == 2,
            tight = loose and tkRelIso < 0.1
  resolved  veto: exactly 2 tight leptons (60 / 53), the flavour's trigger, >= 2 selected jets (pt > 40, |eta| < 2.5,
            AK4PUPPI TightLeptonVeto, dR > 0.4 from every loose lepton) with all the dR > 0.4 pairings
  boosted   leading tight lepton pt > 60 sets the channel, its trigger fires, pt above the trigger plateau
  DY veto   no same-flavour loose lepton with 60 < m(l,l) < 150 (that event is the boosted DY CR)
  fatjet    AK8 pt > 200, |eta| < 2.5, msoftdrop > 40, AK8PUPPI Tight; first in pt order with |dPhi(lead, J)| > 2.0
            (taken from ALL fatjets, not from the LSF3 > 0.75 subset -- that cut is the one being scanned)
  leptons in the fatjet: SF / OF loose lepton with pt > 53, dR(lead, l) > 0.01 and dR(J, l) < 0.8
  no extra tight lepton beyond the lead / SF / OF ones; m(lJ) > 800
  SR        SF loose inside, no OF loose inside, m(lead + SF) > 200     -> SR EE (lead e) / SR MM (lead mu)
  Flavor CR no SF loose inside, OF loose inside, m(lead + OF) > 200     -> EMJ (lead e, mu-jet) / MEJ (lead mu, e-jet)
Not reproduced: JEC/JER lanes (raw NanoAOD pt / msoftdrop), the MET noise filter and the jet veto map.
Stored per region and channel: FatJet_globalParT3_XWWqqev, _XWWqqmv, FatJet_lsf3, in 200 linear and 240 log10 bins.
  boosted_sr_tagger_hists.py --points EE:4000:200,... --out <dir>
  boosted_sr_tagger_hists.py --sample TTto2L2Nu_TuneCP5 --file-list <txt> --out <dir>"""
import argparse, glob, os
import numpy as np
import ROOT

ap = argparse.ArgumentParser()
ap.add_argument("--points", default=None, help="signal: comma list CH:MWR:MN")
ap.add_argument("--sample", default=None, help="background sample name")
ap.add_argument("--file-list", default=None)
ap.add_argument("--skim-dir", default="/gv0/Users/achihwan/SkimNano15/2024")
ap.add_argument("--skim-tag", default="HNWR3SR", help="skim prefix; HNWR (the 2-lepton skim) reproduces the analyzer output for validation")
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
namespace bsr {

struct Lep { P4 p4; bool isMu; bool tight; };
struct FJ  { P4 p4; float ev, mv, lsf3; };

inline float dR(const P4& a, const P4& b)   { return ROOT::Math::VectorUtil::DeltaR(a, b); }
inline float dPhi(const P4& a, const P4& b) { return std::fabs(ROOT::Math::VectorUtil::DeltaPhi(a, b)); }

// HNWR::isPassLooseNoIso -- Loose WP of vidNestedWPBitmap, isolation (cut 7) ignored
inline bool looseNoIso(int bitmap) {
    for (int c = 0; c < 10; ++c) {
        if (c == 7) continue;
        if (((bitmap >> (c * 3)) & 7) < 2) return false;
    }
    return true;
}

// jetid.json AK4PUPPI_TightLeptonVeto / AK8PUPPI_Tight, |eta| < 2.6 branch (both collections are cut at 2.5)
inline bool ak4TightLepVeto(float chHEF, float neHEF, float chEmEF, float neEmEF, float muEF, int chM, int neM) {
    return chHEF > 0.01f && neHEF < 0.99f && chEmEF < 0.8f && neEmEF < 0.9f && muEF < 0.8f
        && chM >= 1 && (chM + neM) >= 2;
}
inline bool ak8Tight(float chHEF, float neHEF, float neEmEF, int chM, int neM) {
    return chHEF > 0.01f && neHEF < 0.99f && neEmEF < 0.9f && chM >= 1 && (chM + neM) >= 2;
}

// {code, isEE, XWWqqev, XWWqqmv, lsf3}; code 0 = no region, 1 = boosted SR, 2 = boosted Flavor CR
RVec<float> region(bool trigE, bool trigM,
                   const RVec<float>& ept, const RVec<float>& eeta, const RVec<float>& ephi, const RVec<float>& esc,
                   const RVec<bool>& eheep, const RVec<int>& ebit,
                   const RVec<float>& mpt, const RVec<float>& meta, const RVec<float>& mphi,
                   const RVec<unsigned char>& mhpt, const RVec<float>& mtk, const RVec<float>& mtunep,
                   const RVec<float>& jpt, const RVec<float>& jeta, const RVec<float>& jphi, const RVec<float>& jmass,
                   const RVec<float>& jchHEF, const RVec<float>& jneHEF, const RVec<float>& jchEmEF,
                   const RVec<float>& jneEmEF, const RVec<float>& jmuEF,
                   const RVec<unsigned char>& jchM, const RVec<unsigned char>& jneM,
                   const RVec<float>& fpt, const RVec<float>& feta, const RVec<float>& fphi, const RVec<float>& fmass,
                   const RVec<float>& fsd, const RVec<float>& flsf, const RVec<float>& fev, const RVec<float>& fmv,
                   const RVec<float>& fchHEF, const RVec<float>& fneHEF, const RVec<float>& fneEmEF,
                   const RVec<short>& fchM, const RVec<short>& fneM) {
    RVec<float> out = {0, 0, -1, -1, -1};

    // ---- leptons ----------------------------------------------------------------------------------------------
    std::vector<Lep> leps;
    for (size_t i = 0; i < ept.size(); ++i) {
        const float asc = std::fabs(esc[i]);
        if (asc >= 1.444f && asc < 1.566f) continue;       // GetAllElectrons dropped the ECAL gap
        if (std::fabs(eeta[i]) >= 2.5f || ept[i] <= 53.f) continue;
        const bool heep = eheep[i];
        if (!heep && !looseNoIso(ebit[i])) continue;       // neither tight nor loose
        leps.push_back({P4(ept[i], eeta[i], ephi[i], 0.000511f), false, heep});
    }
    for (size_t i = 0; i < mpt.size(); ++i) {
        const float pt = mpt[i] * mtunep[i];
        if (std::fabs(meta[i]) >= 2.4f || pt <= 53.f || mhpt[i] != 2) continue;   // loose == POG global high-pT
        leps.push_back({P4(pt, meta[i], mphi[i], 0.1057f), true, mtk[i] < 0.1f});
    }
    std::sort(leps.begin(), leps.end(), [](const Lep& x, const Lep& y) { return x.p4.Pt() > y.p4.Pt(); });
    std::vector<const Lep*> tight;
    for (const auto& l : leps) if (l.tight) tight.push_back(&l);

    // ---- selected jets, cleaned against every loose lepton -----------------------------------------------------
    std::vector<P4> jets;
    for (size_t i = 0; i < jpt.size(); ++i) {
        if (jpt[i] <= 40.f || std::fabs(jeta[i]) >= 2.5f) continue;
        if (!ak4TightLepVeto(jchHEF[i], jneHEF[i], jchEmEF[i], jneEmEF[i], jmuEF[i], int(jchM[i]), int(jneM[i]))) continue;
        const P4 j(jpt[i], jeta[i], jphi[i], jmass[i]);
        bool near = false;
        for (const auto& l : leps) if (dR(j, l.p4) < 0.4f) { near = true; break; }
        if (!near) jets.push_back(j);
    }
    std::sort(jets.begin(), jets.end(), [](const P4& x, const P4& y) { return x.Pt() > y.Pt(); });

    // ---- resolved veto -----------------------------------------------------------------------------------------
    if (tight.size() == 2 && tight[0]->p4.Pt() > 60.f && tight[1]->p4.Pt() > 53.f) {
        const bool eepair = !tight[0]->isMu && !tight[1]->isMu;
        if ((eepair ? trigE : trigM) && jets.size() >= 2
            && dR(jets[0], tight[0]->p4) > 0.4f && dR(jets[0], tight[1]->p4) > 0.4f
            && dR(jets[1], tight[0]->p4) > 0.4f && dR(jets[1], tight[1]->p4) > 0.4f
            && dR(tight[0]->p4, tight[1]->p4) > 0.4f && dR(jets[0], jets[1]) > 0.4f) return out;   // resolved event
    }

    // ---- boosted: leading tight lepton -------------------------------------------------------------------------
    if (tight.empty() || tight[0]->p4.Pt() <= 60.f) return out;
    const Lep* lead = tight[0];
    const bool isEE = !lead->isMu;
    if (!(isEE ? trigE : trigM)) return out;
    if (lead->p4.Pt() < (isEE ? 35.f : 52.f)) return out;          // trigger plateau

    // ---- low-mll same-flavour loose lepton -> boosted DY CR, not SR / Flavor CR --------------------------------
    for (const auto& l : leps) {
        if (&l == lead || l.isMu != lead->isMu) continue;
        const double m = (lead->p4 + l.p4).M();
        if (m > 60. && m < 150.) return out;
    }

    // ---- away fatjet (every fatjet: the LSF3 > 0.75 subset is what the tagger replaces) ------------------------
    std::vector<FJ> fjs;
    for (size_t i = 0; i < fpt.size(); ++i) {
        if (fpt[i] <= 200.f || std::fabs(feta[i]) >= 2.5f || fsd[i] <= 40.f) continue;
        if (!ak8Tight(fchHEF[i], fneHEF[i], fneEmEF[i], int(fchM[i]), int(fneM[i]))) continue;
        fjs.push_back({P4(fpt[i], feta[i], fphi[i], fmass[i]), fev[i], fmv[i], flsf[i]});
    }
    std::sort(fjs.begin(), fjs.end(), [](const FJ& x, const FJ& y) { return x.p4.Pt() > y.p4.Pt(); });
    const FJ* J = nullptr;
    for (const auto& f : fjs) if (dPhi(lead->p4, f.p4) > 2.0f) { J = &f; break; }
    if (J == nullptr) return out;

    // ---- loose lepton inside the fatjet ------------------------------------------------------------------------
    const Lep *sf = nullptr, *of = nullptr;
    for (const auto& l : leps) {
        if (l.isMu != lead->isMu || dR(lead->p4, l.p4) < 0.01f || l.p4.Pt() < 53.) continue;
        if (dR(J->p4, l.p4) < 0.8f) { sf = &l; break; }
    }
    for (const auto& l : leps) {
        if (l.isMu == lead->isMu || dR(lead->p4, l.p4) < 0.01f || l.p4.Pt() < 53.) continue;
        if (dR(J->p4, l.p4) < 0.8f) { of = &l; break; }
    }
    int nExtraTight = 0;
    for (const auto* t : tight) if (t != lead && t != sf && t != of) nExtraTight++;
    if (nExtraTight != 0) return out;
    if ((lead->p4 + J->p4).M() <= 800.) return out;

    float code = 0;
    if (sf && !of && (lead->p4 + sf->p4).M() > 200.)      code = 1;   // boosted SR
    else if (!sf && of && (lead->p4 + of->p4).M() > 200.) code = 2;   // boosted Flavor CR
    if (code == 0) return out;
    out = {code, isEE ? 1.f : 0.f, J->ev, J->mv, J->lsf3};
    return out;
}
}  // namespace bsr
''')

ARGS = ("Electron_pt, Electron_eta, Electron_phi, Electron_superclusterEta, Electron_cutBased_HEEP, "
        "Electron_vidNestedWPBitmap, Muon_pt, Muon_eta, Muon_phi, Muon_highPtId, Muon_tkRelIso, Muon_tunepRelPt, "
        "Jet_pt, Jet_eta, Jet_phi, Jet_mass, Jet_chHEF, Jet_neHEF, Jet_chEmEF, Jet_neEmEF, Jet_muEF, "
        "Jet_chMultiplicity, Jet_neMultiplicity, "
        "FatJet_pt, FatJet_eta, FatJet_phi, FatJet_mass, FatJet_msoftdrop, FatJet_lsf3, "
        "FatJet_globalParT3_XWWqqev, FatJet_globalParT3_XWWqqmv, "
        "FatJet_chHEF, FatJet_neHEF, FatJet_neEmEF, FatJet_chMultiplicity, FatJet_neMultiplicity")
TRIGE = "(HLT_Ele30_WPTight_Gsf || HLT_Photon200 || HLT_Ele115_CaloIdVT_GsfTrkIdT)"
TRIGM = "(HLT_Mu50 || HLT_CascadeMu100 || HLT_HighPtTkMu100)"
NB = 200
NBL, LMIN = 240, -8.0
TAGCOL = {"XWWqqev": 2, "XWWqqmv": 3, "lsf3": 4}
# region code x lead-lepton flavour -> the four regions
REGIONS = {"SR_EE": (1, 1), "SR_MM": (1, 0), "FLV_EMJ": (2, 1), "FLV_MEJ": (2, 0)}

def book(df, name):
    df = df.Define("bsr", f"bsr::region({TRIGE}, {TRIGM}, {ARGS})")
    b = {"total": df.Sum("w"), "total_raw": df.Count()}
    for reg, (code, isEE) in REGIONS.items():
        d = df.Filter(f"bsr[0] == {code} && bsr[1] == {isEE}")
        b[f"n_{reg}"] = d.Sum("w"); b[f"nraw_{reg}"] = d.Count()
        for tag, k in TAGCOL.items():
            d2 = d.Define(f"s_{reg}_{tag}", f"std::min(std::max(bsr[{k}], 0.0f), 0.99999f)")
            b[f"h_{reg}_{tag}"] = d2.Histo1D((f"h_{name}_{reg}_{tag}", "", NB, 0., 1.), f"s_{reg}_{tag}", "w")
            b[f"h_{reg}_{tag}_log"] = d2.Define(f"l_{reg}_{tag}",
                    f"s_{reg}_{tag} > 0 ? std::max(float(std::log10(s_{reg}_{tag})), float({LMIN})) : float({LMIN})") \
                .Histo1D((f"hl_{name}_{reg}_{tag}", "", NBL, LMIN, 0.), f"l_{reg}_{tag}", "w")
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
        files = sorted(glob.glob(f"{a.skim_dir}/Skim_{a.skim_tag}_{TAG[ch]}_MWR{mwr}_N{mn}/tree_*.root"))
        df = ROOT.RDataFrame("Events", files)
        if a.test: df = df.Range(20000)
        df = df.Define("w", "genWeight > 0 ? 1.0 : -1.0")
        jobs.append((f"{ch}_MWR{mwr}_N{mn}", book(df, p.replace(":", "_"))))
else:
    files = [l.strip() for l in open(a.file_list) if l.strip()]
    if a.test: files = files[:1]
    df = ROOT.RDataFrame("Events", files)
    if a.test: df = df.Range(50000)
    df = df.Define("w", "double(genWeight)")
    jobs.append((os.path.basename(a.file_list), book(df, a.sample)))

ROOT.RDF.RunGraphs([v for _, b in jobs for v in b.values()])
for name, b in jobs:
    res = finish(b)
    if a.sample: res["sample"] = a.sample
    if not a.test: np.savez(f"{a.out}/{name}.npz", **res)
    msg = []
    for reg in REGIONS:
        n = res[f"n_{reg}"]
        if n <= 0: msg.append(f"{reg}: 0"); continue
        ls = res[f"h_{reg}_lsf3"]
        msg.append(f"{reg}: {res[f'nraw_{reg}']:.0f} ({n / res['total'] * 100:.2f}%), LSF3>0.75 {ls[150:].sum() / n * 100:.1f}%")
    print(f"{name}: " + " | ".join(msg), flush=True)
print("BOOSTED_SR_TAGGER_HISTS_DONE")
