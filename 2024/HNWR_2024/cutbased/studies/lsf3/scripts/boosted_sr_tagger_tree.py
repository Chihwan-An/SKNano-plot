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

Writes a FLAT TREE, one entry per selected event, carrying ALL 17 GlobalParT-3 class scores of the chosen fatjet so
that any target-specific discriminant can be built downstream per event, e.g. the JMAR recommendation
    P_S   = XWW4q + XWW3q + XWWqqev + XWWqqmv
    P_top = TopbWqq + TopbWq + TopbWev + TopbWmv + TopbWtauhv
    D_WW  = P_S / (P_S + a_top * P_top + a_QCD * QCD)
The individual scores are mass-decorrelated outputs, NOT a normalised probability set: over one 2024 file they sum to
0.92 (median) per fatjet and Xqq alone exceeds 1 for 0.6 % of jets, so only ratios of them are meaningful.
  boosted_sr_tagger_tree.py --points EE:4000:200,... --out <dir>
  boosted_sr_tagger_tree.py --sample TTto2L2Nu_TuneCP5 --file-list <txt> --out <dir>"""
import argparse, glob, json, os
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
ap.add_argument("--name", default=None, help="output stem; defaults to --sample (used to keep condor chunks apart)")
ap.add_argument("--nfiles", type=int, default=1, help="background: how many skim files to read (0 = all)")
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
struct FJ  { P4 p4; float ev, mv, lsf3; int idx; };

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

// {code, isEE, XWWqqev, XWWqqmv, lsf3, fatjet index, m(lJ), lead pt}
// code 0 = no region, 1 = boosted SR, 2 = boosted Flavor CR
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
    RVec<float> out = {0, 0, -1, -1, -1, -1, -1, -1};

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
        fjs.push_back({P4(fpt[i], feta[i], fphi[i], fmass[i]), fev[i], fmv[i], flsf[i], int(i)});
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
    out = {code, isEE ? 1.f : 0.f, J->ev, J->mv, J->lsf3,
           float(J->idx), float((lead->p4 + J->p4).M()), float(lead->p4.Pt())};
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
CLASSES = ["QCD", "TopbWev", "TopbWmv", "TopbWq", "TopbWqq", "TopbWtauhv",
           "XWW3q", "XWW4q", "XWWqqev", "XWWqqmv",
           "Xbb", "Xcc", "Xcs", "Xqq", "Xtauhtaue", "Xtauhtauh", "Xtauhtaum"]
# region code x lead-lepton flavour -> the four regions
REGIONS = {"SR_EE": (1, 1), "SR_MM": (1, 0), "FLV_EMJ": (2, 1), "FLV_MEJ": (2, 0)}


def book(df, ch, mwr, mn):
    """Columns of the output tree: the region, the chosen fatjet and its full class-score vector."""
    df = (df.Define("bsr", f"bsr::region({TRIGE}, {TRIGM}, {ARGS})")
            .Filter("bsr[0] > 0", "in a boosted region")
            .Define("fj", "int(bsr[5])")
            .Define("region", "int(bsr[0])")          # 1 = boosted SR, 2 = boosted flavour CR
            .Define("isEE", "int(bsr[1])")            # flavour of the LEADING lepton
            .Define("lsf3", "bsr[4]")
            .Define("m_lJ", "bsr[6]")
            .Define("lead_pt", "bsr[7]")
            .Define("fj_pt", "FatJet_pt[fj]")
            .Define("fj_eta", "FatJet_eta[fj]")
            .Define("fj_msoftdrop", "FatJet_msoftdrop[fj]")
            .Define("fj_mass", "FatJet_mass[fj]")
            .Define("mwr", f"{mwr}").Define("mn", f"{mn}")
            .Define("ch_is_EE", f"{1 if ch == 'EE' else 0}"))
    for c in CLASSES:
        df = df.Define(f"p_{c}", f"FatJet_globalParT3_{c}[fj]")
    cols = ["region", "isEE", "ch_is_EE", "mwr", "mn", "w", "lead_pt", "m_lJ",
            "fj_pt", "fj_eta", "fj_msoftdrop", "fj_mass", "lsf3"] + [f"p_{c}" for c in CLASSES]
    return df, cols


if not a.points and not a.sample:
    raise SystemExit("pass --points CH:MWR:MN[,...] for signal, or --sample NAME for a background")

if a.sample:
    # background: mwr / mn are 0 so a signal and a background tree can be chained together
    allfiles = sorted(glob.glob(f"{a.skim_dir}/Skim_{a.skim_tag}_{a.sample}/tree_*.root"))
    if a.file_list:                      # condor: one chunk of the sample's files
        files = [l.strip() for l in open(a.file_list) if l.strip()]
    else:
        files = allfiles[:a.nfiles] if a.nfiles > 0 else allfiles
    if not files:
        raise SystemExit(f"no skim files for {a.sample} under {a.skim_dir}")
    tag = a.name or a.sample
    # genEventSumw of exactly the files being read, so a partial run still normalises correctly:
    # the skim has already thrown events away, so the sum cannot be recovered from the Events tree.
    runs = ROOT.RDataFrame("Runs", files)
    sumw = runs.Sum("genEventSumw").GetValue()
    nev = runs.Sum("genEventCount").GetValue()
    df = ROOT.RDataFrame("Events", files)
    if a.test: df = df.Range(50000)
    df = df.Define("w", "double(genWeight)")
    d, cols = book(df, "EE", 0, 0)
    if a.test:
        print(f"{a.sample}: {d.Count().GetValue()} entries from {len(files)} file(s) (test)", flush=True)
    else:
        d.Snapshot("tagger", f"{a.out}/{tag}.root", cols)
        json.dump({"sample": a.sample, "nfiles": len(files), "nfiles_total": len(allfiles),
                   "sumw": sumw, "genEventCount": nev},
                  open(f"{a.out}/{tag}.norm.json", "w"), indent=1)
        print(f"{tag}: wrote {a.out}/{tag}.root from {len(files)} file(s), sumw={sumw:.6g}", flush=True)
    print("BOOSTED_SR_TAGGER_TREE_DONE"); raise SystemExit(0)

TAG = {"EE": "WRtoNEltoElElJJ", "MM": "WRtoNMutoMuMuJJ"}
for p in a.points.split(","):
    ch, mwr, mn = p.split(":")
    files = sorted(glob.glob(f"{a.skim_dir}/Skim_{a.skim_tag}_{TAG[ch]}_MWR{mwr}_N{mn}/tree_*.root"))
    if not files:
        print(f"!! no skim for {p}", flush=True); continue
    df = ROOT.RDataFrame("Events", files)
    if a.test: df = df.Range(20000)
    df = df.Define("w", "genWeight > 0 ? 1.0 : -1.0")
    d, cols = book(df, ch, mwr, mn)
    name = f"{ch}_MWR{mwr}_N{mn}"
    if a.test:
        print(f"{name}: {d.Count().GetValue()} entries (test)", flush=True); continue
    d.Snapshot("tagger", f"{a.out}/{name}.root", cols)
    print(f"{name}: wrote {a.out}/{name}.root", flush=True)
print("BOOSTED_SR_TAGGER_TREE_DONE")
