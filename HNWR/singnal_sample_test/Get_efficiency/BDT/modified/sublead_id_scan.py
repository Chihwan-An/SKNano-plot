#!/usr/bin/env python3
"""m<2000: ID pass fractions for the GEN-MATCHED sublead lepton with reco
pT > 20 (fakes excluded by dR<0.2 gen matching), then the full resolved-chain
acceptance with sublead pT > 20 using the best-performing IDs."""

import glob
import numpy as np
import awkward as ak
import uproot

NANO = "/gv0/Users/achihwan/SKNano/Run3NanoAODv12/2023"

EL_BR = ["Electron_pt", "Electron_eta", "Electron_phi", "Electron_mass",
         "Electron_cutBased", "Electron_cutBased_HEEP",
         "Electron_mvaIso_WP80", "Electron_mvaIso_WP90",
         "Electron_mvaNoIso_WP80", "Electron_mvaNoIso_WP90",
         "Jet_pt", "Jet_eta", "Jet_phi",
         "HLT_Photon200", "HLT_Ele115_CaloIdVT_GsfTrkIdT"]
MU_BR = ["Muon_pt", "Muon_eta", "Muon_phi", "Muon_mass",
         "Muon_looseId", "Muon_mediumId", "Muon_mediumPromptId", "Muon_tightId",
         "Muon_softId", "Muon_softMvaId", "Muon_highPtId", "Muon_mvaMuID_WP",
         "Muon_miniIsoId", "Muon_pfIsoId", "Muon_tkIsoId", "Muon_puppiIsoId",
         "Muon_multiIsoId", "Muon_tkRelIso", "Muon_isGlobal", "Muon_isTracker",
         "Jet_pt", "Jet_eta", "Jet_phi",
         "HLT_Mu50", "HLT_CascadeMu100", "HLT_HighPtTkMu100"]
LHE_BR = ["LHEPart_pt", "LHEPart_eta", "LHEPart_phi", "LHEPart_mass",
          "LHEPart_status", "LHEPart_pdgId"]

EL_IDS = [
    ("HEEP (current tight)",  lambda a: a["Electron_cutBased_HEEP"]),
    ("cutBased Loose",        lambda a: a["Electron_cutBased"] >= 2),
    ("cutBased Medium",       lambda a: a["Electron_cutBased"] >= 3),
    ("cutBased Tight",        lambda a: a["Electron_cutBased"] >= 4),
    ("mvaIso WP80",           lambda a: a["Electron_mvaIso_WP80"]),
    ("mvaIso WP90",           lambda a: a["Electron_mvaIso_WP90"]),
    ("mvaNoIso WP80",         lambda a: a["Electron_mvaNoIso_WP80"]),
    ("mvaNoIso WP90",         lambda a: a["Electron_mvaNoIso_WP90"]),
]
MU_IDS = [
    ("highPtId==2 +tkIso<0.1 (current)", lambda a: (a["Muon_highPtId"] == 2) & (a["Muon_tkRelIso"] < 0.1)),
    ("highPtId==2 (global)",  lambda a: a["Muon_highPtId"] == 2),
    ("highPtId>=1 (tracker)", lambda a: a["Muon_highPtId"] >= 1),
    ("looseId",               lambda a: a["Muon_looseId"]),
    ("mediumId",              lambda a: a["Muon_mediumId"]),
    ("mediumPromptId",        lambda a: a["Muon_mediumPromptId"]),
    ("tightId",               lambda a: a["Muon_tightId"]),
    ("softId",                lambda a: a["Muon_softId"]),
    ("softMvaId",             lambda a: a["Muon_softMvaId"]),
    ("mvaMuID_WP>=1 (Medium)", lambda a: a["Muon_mvaMuID_WP"] >= 1),
    ("mvaMuID_WP>=2 (Tight)", lambda a: a["Muon_mvaMuID_WP"] >= 2),
    ("mediumId+miniIso>=1",   lambda a: a["Muon_mediumId"] & (a["Muon_miniIsoId"] >= 1)),
    ("mediumId+pfIso>=2",     lambda a: a["Muon_mediumId"] & (a["Muon_pfIsoId"] >= 2)),
    ("mediumId+tkIso<0.1",    lambda a: a["Muon_mediumId"] & (a["Muon_tkRelIso"] < 0.1)),
    ("tightId+tkIso<0.1",     lambda a: a["Muon_tightId"] & (a["Muon_tkRelIso"] < 0.1)),
]


def load(tag, br):
    fs = sorted(glob.glob(f"{NANO}/{tag}/**/*.root", recursive=True))
    return ak.concatenate([uproot.open(p)["Events"].arrays(br) for p in fs])


def lhem(a):
    s = a["LHEPart_status"] == 1
    pt, eta, phi, m = (a[f"LHEPart_{k}"][s] for k in ("pt", "eta", "phi", "mass"))
    px = ak.sum(pt * np.cos(phi), axis=1); py = ak.sum(pt * np.sin(phi), axis=1)
    pz = ak.sum(pt * np.sinh(eta), axis=1)
    e = ak.sum(np.sqrt((pt * np.cosh(eta))**2 + m**2), axis=1)
    return np.sqrt(np.maximum(e**2 - px**2 - py**2 - pz**2, 0.))


def dphif(a, b):
    d = np.abs(a - b); return ak.where(d > np.pi, 2 * np.pi - d, d)


def at(arr, i):
    ii = ak.fill_none(ak.firsts(i), -1); i0 = ak.where(ii < 0, 0, ii)
    return ak.fill_none(ak.firsts(ak.pad_none(arr, 1, axis=1)[ak.singletons(i0)]), 0.)


def gen_sublead(a, pdg):
    lep = (np.abs(a["LHEPart_pdgId"]) == pdg) & (a["LHEPart_status"] == 1)
    gpt = ak.where(lep, a["LHEPart_pt"], -1.)
    g1 = ak.fill_none(ak.firsts(ak.argmax(gpt, axis=1, keepdims=True)), -1)
    gidx = ak.local_index(a["LHEPart_pt"], axis=1)
    gpt2 = ak.where(lep & (gidx != g1), a["LHEPart_pt"], -1.)
    g2 = ak.argmax(gpt2, axis=1, keepdims=True)
    has = np.asarray(ak.max(gpt2, axis=1, initial=-1., mask_identity=False)) > 0
    return (np.asarray(at(a["LHEPart_eta"], g2)),
            np.asarray(at(a["LHEPart_phi"], g2)), has)


def id_scan(chn, obj, pdg, ids, etamax):
    agg = {nm: [0, 0] for nm, _ in ids}
    for wr in (4000, 6000):
        for n in (100, 300):
            tag = (f"WRtoNEltoElElJJ_MWR{wr}_N{n}_*" if chn == "EE"
                   else f"WRtoNMutoMuMuJJ_MWR{wr}_N{n}_*")
            a = load(tag, (EL_BR if chn == "EE" else MU_BR) + LHE_BR)
            a = a[np.asarray(lhem(a) < 2000.)]
            ge, gp, has = gen_sublead(a, pdg)
            dr = np.sqrt((a[f"{obj}_eta"] - ge)**2 + dphif(a[f"{obj}_phi"], gp)**2)
            match = (dr < 0.2) & (a[f"{obj}_pt"] > 20.) & (np.abs(a[f"{obj}_eta"]) < etamax)
            hasm = np.asarray(ak.any(match, axis=1)) & has
            for nm, fn in ids:
                np_ = int(ak.sum(ak.any(match & fn(a), axis=1)[hasm]))
                agg[nm][0] += np_; agg[nm][1] += int(hasm.sum())
    print(f"--- {chn}: gen-matched sublead, reco pT>20, m<2000 "
          f"(N cand = {agg[ids[0][0]][1]}) ---")
    for nm, _ in sorted(ids, key=lambda x: -agg[x[0]][0]):
        p, t = agg[nm]
        print(f"  {nm:34s} {p/max(t,1):6.1%}")


id_scan("EE", "Electron", 11, EL_IDS, 2.5)
id_scan("MM", "Muon", 13, MU_IDS, 2.4)
