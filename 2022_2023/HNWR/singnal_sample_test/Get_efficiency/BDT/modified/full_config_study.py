#!/usr/bin/env python3
"""Final-configuration study (NanoAOD emulation, 2023 signal):

resolved_old : lead tight(+trig,safe pT) + sublead TIGHT pT>53 + mll>200
               + 2 cleaned jets + 4-object dR
resolved_new : same but sublead = (EE: cutBased-Loose||HEEP / MM:
               mediumId+miniIsoLoose || current tight), pT>20
boosted      : NO-LOOSE definition (applied in code): !resolved && trig
               && lead tight pT>60(+safe) && >=1 AK8 (pT>200,|eta|<2.5,
               dR(lead)>0.4)  [fatjet ID / jet-veto / noise filter omitted]

Outputs per (sample, region):
  A) category migration: resolved/boosted/total for old vs new resolved
  B) boosted sublead CAPTURE (not a requirement): fraction of boosted events
     whose gen-matched sublead is stored under each ID at pT>53 / pT>20
"""

import glob
import numpy as np
import awkward as ak
import uproot

NANO = "/gv0/Users/achihwan/SKNano/Run3NanoAODv12/2023"
OUT = __file__.rsplit("/", 1)[0]
THR = {4000: 2000., 6000: 4000.}
SAMPLES = [(wr, n) for wr in (4000, 6000) for n in (100, 300)]

LHE = ["LHEPart_pt", "LHEPart_eta", "LHEPart_phi", "LHEPart_mass",
       "LHEPart_status", "LHEPart_pdgId"]
EL_BR = ["Electron_pt", "Electron_eta", "Electron_phi", "Electron_mass",
         "Electron_cutBased", "Electron_cutBased_HEEP",
         "Electron_mvaIso_WP80", "Electron_mvaIso_WP90",
         "Electron_mvaNoIso_WP80", "Electron_mvaNoIso_WP90",
         "Jet_pt", "Jet_eta", "Jet_phi", "FatJet_pt", "FatJet_eta", "FatJet_phi",
         "HLT_Photon200", "HLT_Ele115_CaloIdVT_GsfTrkIdT"] + LHE
MU_BR = ["Muon_pt", "Muon_eta", "Muon_phi", "Muon_mass",
         "Muon_looseId", "Muon_mediumId", "Muon_tightId", "Muon_highPtId",
         "Muon_miniIsoId", "Muon_tkRelIso", "Muon_mvaMuID_WP",
         "Jet_pt", "Jet_eta", "Jet_phi", "FatJet_pt", "FatJet_eta", "FatJet_phi",
         "HLT_Mu50", "HLT_CascadeMu100", "HLT_HighPtTkMu100"] + LHE


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


def resolved(a, pre, leadmask, leadcut, trig, submask, subpt):
    lpt_ = ak.where(leadmask, a[pre + "_pt"], -1.)
    lpt = np.asarray(ak.max(lpt_, axis=1, initial=-1., mask_identity=False))
    li = ak.argmax(lpt_, axis=1, keepdims=True); lii = ak.fill_none(ak.firsts(li), -1)
    idx = ak.local_index(a[pre + "_pt"], axis=1)
    cand = (idx != lii) & submask & (a[pre + "_pt"] > subpt)
    spt_ = ak.where(cand, a[pre + "_pt"], -1.)
    si = ak.argmax(spt_, axis=1, keepdims=True)
    has2 = np.asarray(ak.max(spt_, axis=1, initial=-1., mask_identity=False)) > 0.
    le, lp = np.asarray(at(a[pre + "_eta"], li)), np.asarray(at(a[pre + "_phi"], li))
    se, sp = np.asarray(at(a[pre + "_eta"], si)), np.asarray(at(a[pre + "_phi"], si))
    lm, sm = np.asarray(at(a[pre + "_mass"], li)), np.asarray(at(a[pre + "_mass"], si))
    l1, s1 = np.asarray(at(a[pre + "_pt"], li)), np.asarray(at(a[pre + "_pt"], si))
    E = lambda pt, eta, m: np.sqrt((pt * np.cosh(eta))**2 + m**2)
    mll = np.sqrt(np.maximum(
        (E(l1, le, lm) + E(s1, se, sm))**2 - (l1 * np.cos(lp) + s1 * np.cos(sp))**2
        - (l1 * np.sin(lp) + s1 * np.sin(sp))**2 - (l1 * np.sinh(le) + s1 * np.sinh(se))**2, 0.))
    drll = np.sqrt((le - se)**2 + np.asarray(dphif(ak.Array(lp), ak.Array(sp)))**2)
    jok = (a["Jet_pt"] > 40.) & (np.abs(a["Jet_eta"]) < 2.5)
    dr1 = np.sqrt((a["Jet_eta"] - le)**2 + dphif(a["Jet_phi"], lp)**2)
    dr2 = np.sqrt((a["Jet_eta"] - se)**2 + dphif(a["Jet_phi"], sp)**2)
    jc = jok & (dr1 > 0.4) & (dr2 > 0.4)
    jidx = ak.local_index(a["Jet_pt"], axis=1)
    jpt = ak.where(jc, a["Jet_pt"], -1.)
    j1 = ak.argmax(jpt, axis=1, keepdims=True); j1i = ak.fill_none(ak.firsts(j1), -1)
    jpt2 = ak.where(jc & (jidx != j1i), a["Jet_pt"], -1.)
    j2 = ak.argmax(jpt2, axis=1, keepdims=True)
    n2 = np.asarray(ak.sum(jc, axis=1)) >= 2
    j1e, j1p = np.asarray(at(a["Jet_eta"], j1)), np.asarray(at(a["Jet_phi"], j1))
    j2e, j2p = np.asarray(at(a["Jet_eta"], j2)), np.asarray(at(a["Jet_phi"], j2))
    drjj = np.sqrt((j1e - j2e)**2 + np.asarray(dphif(ak.Array(j1p), ak.Array(j2p)))**2)
    passed = trig & (lpt > leadcut) & has2 & (mll > 200.) & n2 & (drll > 0.4) & (drjj > 0.4)
    return passed, lpt, li


def boosted_base(a, pre, trig, lpt, li, leadcut):
    """no-loose boosted lepton+fatjet part: trig + lead tight + AK8 away from lead."""
    le, lp = np.asarray(at(a[pre + "_eta"], li)), np.asarray(at(a[pre + "_phi"], li))
    fok = (a["FatJet_pt"] > 200.) & (np.abs(a["FatJet_eta"]) < 2.5)
    drf = np.sqrt((a["FatJet_eta"] - le)**2 + dphif(a["FatJet_phi"], lp)**2)
    ak8 = np.asarray(ak.sum(fok & (drf > 0.4), axis=1)) >= 1
    return trig & (lpt > leadcut) & ak8


def gen_sub(a, pdg):
    lep = (np.abs(a["LHEPart_pdgId"]) == pdg) & (a["LHEPart_status"] == 1)
    gpt = ak.where(lep, a["LHEPart_pt"], -1.)
    g1 = ak.fill_none(ak.firsts(ak.argmax(gpt, axis=1, keepdims=True)), -1)
    gidx = ak.local_index(a["LHEPart_pt"], axis=1)
    gpt2 = ak.where(lep & (gidx != g1), a["LHEPart_pt"], -1.)
    g2 = ak.argmax(gpt2, axis=1, keepdims=True)
    return np.asarray(at(a["LHEPart_eta"], g2)), np.asarray(at(a["LHEPart_phi"], g2))


def main():
    lines = []
    cap_ids_el = [
        ("current loose (cbL||HEEP)", lambda a: (a["Electron_cutBased"] >= 2) | a["Electron_cutBased_HEEP"]),
        ("cutBased Loose", lambda a: a["Electron_cutBased"] >= 2),
        ("mvaNoIso WP90", lambda a: a["Electron_mvaNoIso_WP90"]),
        ("mvaNoIso WP80", lambda a: a["Electron_mvaNoIso_WP80"]),
        ("mvaIso WP90", lambda a: a["Electron_mvaIso_WP90"]),
        ("cbL||HEEP||mvaNoIso90", lambda a: (a["Electron_cutBased"] >= 2) | a["Electron_cutBased_HEEP"] | a["Electron_mvaNoIso_WP90"]),
    ]
    cap_ids_mu = [
        ("current loose (highPtId2)", lambda a: a["Muon_highPtId"] == 2),
        ("looseId", lambda a: a["Muon_looseId"]),
        ("mediumId", lambda a: a["Muon_mediumId"]),
        ("medium+miniIsoL", lambda a: a["Muon_mediumId"] & (a["Muon_miniIsoId"] >= 1)),
        ("highPtId>=1", lambda a: a["Muon_highPtId"] >= 1),
    ]
    for wr, n in SAMPLES:
        for ch in ("EE", "MM"):
            if ch == "EE":
                a = load(f"WRtoNEltoElElJJ_MWR{wr}_N{n}_*", EL_BR)
                trig = np.asarray(a["HLT_Photon200"] | a["HLT_Ele115_CaloIdVT_GsfTrkIdT"])
                acc = np.abs(a["Electron_eta"]) < 2.5
                tight = a["Electron_cutBased_HEEP"] & acc
                subnew = ((a["Electron_cutBased"] >= 2) | a["Electron_cutBased_HEEP"]) & acc
                pre, leadcut, etam, pdg, capids = "Electron", 118., 2.5, 11, cap_ids_el
                leadmask = tight & (a["Electron_pt"] > 60.)
            else:
                a = load(f"WRtoNMutoMuMuJJ_MWR{wr}_N{n}_*", MU_BR)
                trig = np.asarray(a["HLT_Mu50"] | a["HLT_CascadeMu100"] | a["HLT_HighPtTkMu100"])
                acc = np.abs(a["Muon_eta"]) < 2.4
                tight = acc & (a["Muon_highPtId"] == 2) & (a["Muon_tkRelIso"] < 0.1)
                subnew = acc & ((a["Muon_mediumId"] & (a["Muon_miniIsoId"] >= 1))
                                | ((a["Muon_highPtId"] == 2) & (a["Muon_tkRelIso"] < 0.1)))
                pre, leadcut, etam, pdg, capids = "Muon", 60., 2.4, 13, cap_ids_mu
                leadmask = tight & (a["Muon_pt"] > 60.)
            m = lhem(a)
            res_old, lpt, li = resolved(a, pre, leadmask, leadcut, trig, tight, 53.)
            res_new, _, _ = resolved(a, pre, leadmask, leadcut, trig, subnew, 20.)
            bb = boosted_base(a, pre, trig, lpt, li, leadcut)
            boo_old = bb & ~res_old
            boo_new = bb & ~res_new
            ge, gp = gen_sub(a, pdg)
            dr = np.sqrt((a[f"{pre}_eta"] - ge)**2 + dphif(a[f"{pre}_phi"], gp)**2)
            match20 = (dr < 0.2) & (a[f"{pre}_pt"] > 20.) & (np.abs(a[f"{pre}_eta"]) < etam)
            match53 = match20 & (a[f"{pre}_pt"] > 53.)
            for reg, lo, hi in (("off", 0., THR[wr]), ("on", THR[wr], 1e9)):
                s = np.asarray((m >= lo) & (m < hi))
                ro, rn = res_old[s].mean(), res_new[s].mean()
                bo, bn = boo_old[s].mean(), boo_new[s].mean()
                lines.append(f"[A] WR{wr}N{n}{ch} {reg}: res {ro:6.1%}->{rn:6.1%} ({rn-ro:+.1%})  "
                             f"boo {bo:6.1%}->{bn:6.1%} ({bn-bo:+.1%})  "
                             f"TOT {ro+bo:6.1%}->{rn+bn:6.1%} ({rn+bn-ro-bo:+.1%})")
                bsel = np.asarray(boo_new) & s
                nb = max(bsel.sum(), 1)
                caps = []
                for nm, fn in capids:
                    c53 = float(np.asarray(ak.any(match53 & fn(a), axis=1))[bsel].mean())
                    c20 = float(np.asarray(ak.any(match20 & fn(a), axis=1))[bsel].mean())
                    caps.append(f"{nm}: {c53:.0%}/{c20:.0%}")
                lines.append(f"[B] WR{wr}N{n}{ch} {reg} boosted sublead capture (pT>53 / pT>20): "
                             + " | ".join(caps))
    text = "\n".join(lines)
    print(text)
    with open(f"{OUT}/full_config_study.txt", "w") as fh:
        fh.write(text + "\n")


if __name__ == "__main__":
    main()
