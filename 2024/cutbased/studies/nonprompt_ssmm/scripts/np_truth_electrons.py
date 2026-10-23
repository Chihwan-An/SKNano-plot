#!/usr/bin/env python3
"""Which electron is non-prompt / charge-flipped in the SS ee SR (card rEESR_SS), per MC process.
Input: HNWR FOMode,FOEE,RFlav production, RNTuple Central/FO_EE_resolved (merged file or per-job outputs).
Region: SS, both leading loose electrons tight (isTight), nTightElectron==2, nTightMuon==0, mll>400, mlljj>800.
Per electron truth:
  P    prompt e (origin 1/2) with the right charge
  FLIP prompt e (origin 1/2) with reco charge != gen charge
  CONV conversion of a prompt photon (origin 10)
  F    from a hadron: b / b->c / c / np tau / light (origin 3-7; genConv flag = via a photon, e.g. pi0 Dalitz)
  U    no gen match (origin 0/8): nearest gen particle printed
Weights: MC weight x DY R (no lepton SFs; composition study).

  np_truth_electrons.py [--samples TTtoLNu2Q,WtoLNu]   -> results/15_np_truth_electrons.txt
"""
import argparse
import collections
import glob
import os
import sys

import numpy as np
import ROOT

import folib as L

RL = "/gv0/Users/achihwan/SKNanoRunlog/2026_09_24_150956_HNWR_FOMode_FOEE_RFlav/2024"
OUT = "/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/FOMode_FOEE_RFlav/2024"
TREE = "Central_FO_EE_resolved"
ORIG = {0: "none", 1: "prompt", 2: "prompt tau", 3: "b", 4: "b->c", 5: "c", 6: "np tau", 7: "light", 8: "inconcl.",
        10: "prompt-γ conv"}
FLAV = {0: "0 unmatched", 1: "1 prompt", 15: "15 tau", 22: "22 photon", 5: "5 b", 4: "4 c", 3: "3 light"}
PT_EDGES = [53, 80, 120, 200, 300, 500, 4000]


def files_of(sample):
    m = os.path.join(OUT, sample + ".root")
    if os.path.exists(m) and os.path.exists(os.path.join(RL, sample, "hadd.out")):
        return [m]
    nj = len(glob.glob(os.path.join(RL, sample, "job_*.cc")))
    fs = sorted(glob.glob(os.path.join(RL, sample, "output", "hists_*.root")))
    return fs if nj and len(fs) == nj else []


def load(samples):
    out = {}
    for s in samples:
        fs = files_of(s)
        if not fs:
            print(f"[skip] {s} not complete")
            continue
        v = ROOT.std.vector("std::string")()
        ok = 0
        for f in fs:
            tf = ROOT.TFile.Open(f)
            if tf and TREE in {k.GetName() for k in tf.GetListOfKeys()}:
                v.push_back(f); ok += 1
            tf.Close()
        if not ok:
            continue
        out[s] = {k: np.asarray(x) for k, x in ROOT.RDataFrame(TREE, v).AsNumpy().items()}
    return out


def truth(o, flip):
    return np.where(np.isin(o, [1, 2]), np.where(flip, "FLIP", "P"),
                    np.where(o == 10, "CONV", np.where(np.isin(o, [3, 4, 5, 6, 7]), "F", "U")))


def analyse(name, d, P):
    ss = d["el1_charge"] * d["el2_charge"] > 0
    m = (ss & (d["el1_isTight"] == 1) & (d["el2_isTight"] == 1) & (d["nTightElectron"] == 2) & (d["nTightMuon"] == 0)
         & (d["mll"] > 400) & (d["mlljj"] > 800))
    w = d["weight"]
    tot = w[m].sum()
    P(f"\n## {name}: rEESR_SS yield {tot:.3f} [{m.sum()} raw]")
    if m.sum() == 0:
        return
    t = {}
    for k in (1, 2):
        pdg = d[f"el{k}_genPdgId"]
        gch = np.where(np.abs(pdg) == 11, -np.sign(pdg), 0)
        flip = (gch != 0) & (gch != d[f"el{k}_charge"])
        t[k] = truth(d[f"el{k}_genOrigin"], flip)
    pair = np.char.add(np.char.add(t[1].astype(str), "-"), t[2].astype(str))
    c = collections.Counter()
    for p in np.unique(pair[m]):
        c[p] = w[m & (pair == p)].sum()
    P("  truth pair (lead-sub): " + ", ".join(f"{k} {v / tot:.2f}" for k, v in c.most_common() if abs(v / tot) >= 0.01))
    # the "bad" electron(s): anything not P
    orig, flav, which, near = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    conv_had = 0.0
    pts, wts = [], []
    for k, lab in ((1, "lead"), (2, "sub")):
        mk = m & (t[k] != "P")
        which[lab] = w[mk].sum()
        for tv in np.unique(t[k][mk]):
            orig["[" + tv + "] "] += 0  # keep order
        for o in np.unique(d[f"el{k}_genOrigin"][mk]):
            mo = mk & (d[f"el{k}_genOrigin"] == o)
            key = ORIG.get(int(o), str(o))
            if int(o) in (1, 2):
                key = "prompt e, charge flipped" if (t[k][mo] == "FLIP").all() else key
            orig[key] += w[mo].sum()
        for tv in ("FLIP",):
            pass
        for f in np.unique(d[f"el{k}_genPartFlav"][mk]):
            flav[FLAV.get(int(f), str(f))] += w[mk & (d[f"el{k}_genPartFlav"] == f)].sum()
        conv_had += w[mk & (d[f"el{k}_genConv"] == 1) & np.isin(d[f"el{k}_genOrigin"], [3, 4, 5, 6, 7])].sum()
        mu = mk & (d[f"el{k}_genOrigin"] == 0)
        for p in np.unique(d[f"el{k}_nearPdgId"][mu]):
            near[int(p)] += w[mu & (d[f"el{k}_nearPdgId"] == p)].sum()
        pts.append(d[f"el{k}_pt"][mk]); wts.append(w[mk])
    nb = sum(which.values())
    orig = collections.Counter({k: v for k, v in orig.items() if not k.startswith("[")})
    P(f"  non-prompt/flipped electron is: lead {which['lead'] / nb:.2f}, sub {which['sub'] / nb:.2f} (of {nb:.3f})")
    P("  its truth: " + ", ".join(f"{k} {v / nb:.2f}" for k, v in orig.most_common() if abs(v / nb) >= 0.005))
    P("  NanoAOD genPartFlav: " + ", ".join(f"{k} {v / nb:.2f}" for k, v in flav.most_common() if abs(v / nb) >= 0.005))
    P(f"  hadron-origin via a photon (pi0/eta Dalitz, conversions in jets): {conv_had / nb:.2f}")
    if near:
        P("  unmatched -> nearest gen particle pdgId (dR<0.3, pT>5): "
          + ", ".join(f"{k} {v / nb:.2f}" for k, v in sorted(near.items(), key=lambda x: -x[1])[:6]))
    h = np.histogram(np.concatenate(pts), PT_EDGES, weights=np.concatenate(wts))[0]
    P("  its pT: " + "  ".join(f"{PT_EDGES[i]}-{PT_EDGES[i + 1]} {h[i] / nb:.2f}" for i in range(len(h))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", default="")
    a = ap.parse_args()
    allS = sorted(os.listdir(RL))
    keys = [k for k in a.samples.split(",") if k]
    samples = [s for s in allS if not keys or any(k in s for k in keys)]
    data = load(samples)
    groups = collections.defaultdict(list)
    for s in data:
        groups[L.process_of(s)].append(s)
    txt = []
    P = lambda *x: (txt.append(" ".join(str(y) for y in x)), print(*x))  # noqa: E731
    P("# rEESR_SS (SS, 2 tight e, 0 tight mu, mll>400, mlljj>800), FOEE truth tree. Weights: MC x DY R, no lepton SF.")
    P("# P prompt right charge / FLIP prompt wrong charge / CONV prompt-photon conversion / F hadron origin / U unmatched")
    for g in sorted(groups):
        d = {k: np.concatenate([data[s][k] for s in groups[g]]) for k in data[groups[g][0]]}
        analyse(g, d, P)
    out = os.path.join(L.RESULTS, "15_np_truth_electrons.txt")
    open(out, "w").write("\n".join(txt) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    sys.exit(main())
