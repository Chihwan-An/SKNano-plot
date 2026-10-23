#!/usr/bin/env python3
"""Data-measured muon fake rate with prompt-MC subtraction, and the matching fake-factor application.

Fake rate (per muon, FOLOW production, SS, 60<mll<300, FO baseline):
    loose = TkRelIso < LMAX (tight included), tight = TkRelIso < 0.1
    f = (data tight - prompt MC tight) / (data loose - prompt MC loose)
    prompt MC = MC muons with truth P (origin 1, 2); noQCD (FOLOW has no QCD).
    OS is not used: FOLOW stores no OS data TT event.
Application (per event of the AR = TL / LT / LL, the LNT muon(s) with iso < LMAX):
    Fake = sum_data(AR) F - sum_MC(AR, LNT muon prompt) w F,  F = f/(1-f)
    TL -> F2, LT -> F1, LL -> -F1 F2;  'LNT muon prompt': TL sub P, LT lead P, LL either P.

  ffdata.py [--lmax 0.4] [--pt 53,4000]  -> results/24_fr_data_promptsub.txt
"""
import argparse
import os
import sys

import numpy as np

import fo_analysis as FA  # noqa: E402
import folib as L  # noqa: E402
import fr_mll60300 as FR  # noqa: E402

ETA = [0, 0.8, 1.5, 2.0, 2.4]


def _fill(rm, d, m, lmax, w):
    for k in (1, 2):
        iso = d[f"mu{k}_tkRelIso"]
        sel = m & (iso < lmax)
        rm.fill(d[f"mu{k}_pt"][sel], d[f"mu{k}_eta"][sel], iso[sel] < L.TIGHT_ISO, w[sel])
    return rm


def _promptmuon_fill(rm, d, m, lmax):
    """fill only the truth-P muons of MC events m."""
    for k in (1, 2):
        iso = d[f"mu{k}_tkRelIso"]
        sel = m & (iso < lmax) & (d[f"t{k}"] == "P")
        rm.fill(d[f"mu{k}_pt"][sel], d[f"mu{k}_eta"][sel], iso[sel] < L.TIGHT_ISO, d["weight"][sel])
    return rm


def subtract(a, b):
    """RateMap a - b (sums subtract, variances add)."""
    r = L.RateMap(a.pt, a.eta)
    r.T, r.L = a.T - b.T, a.L - b.L
    r.T2, r.L2 = a.T2 + b.T2, a.L2 + b.L2
    r.nT, r.nL = a.nT, a.nL
    return r


def region(lo):
    return lo["base"] & lo["ss"] & (lo["mll"] > 60) & (lo["mll"] < 300)


def maps(lo, lmax, pt):
    """(data map, data, prompt MC, MC-as-pseudo-data map) for the FOLOW SS 60<mll<300 region."""
    reg = region(lo)
    D, M = reg & lo["data"], reg & ~lo["data"]
    rD = _fill(L.RateMap(pt, ETA), lo, D, lmax, np.ones(len(lo["mll"])))
    rP = _promptmuon_fill(L.RateMap(pt, ETA), lo, M, lmax)
    rM = _fill(L.RateMap(pt, ETA), lo, M, lmax, lo["weight"])
    return subtract(rD, rP), rD, rP, subtract(rM, rP)


def data_map(lmax=0.4, pt=(53.0, 4000.0)):
    FR.PT = list(pt)
    lo, _ = FR.load()
    return maps(lo, lmax, list(pt))[0]


def lnt_prompt(d):
    """MC events whose LNT muon(s) are truth prompt (TL: sub, LT: lead, LL: either)."""
    c = d["cat"]
    p1, p2 = d["t1"] == "P", d["t2"] == "P"
    return np.where(c == "TL", p2, np.where(c == "LT", p1, np.where(c == "LL", p1 | p2, False)))


def ff_weights(d, m, rm, lmax):
    """per-event fake-factor weight w F (TL: F2, LT: F1, LL: -F1 F2), AR = fail muon(s) with iso < lmax."""
    ok = m & (d["cat"] != "TT")
    ok &= ~np.isin(d["cat"], ["LT", "LL"]) | (d["mu1_tkRelIso"] < lmax)
    ok &= ~np.isin(d["cat"], ["TL", "LL"]) | (d["mu2_tkRelIso"] < lmax)
    F1 = L.fake_factor(rm.lookup(d["mu1_pt"], d["mu1_eta"]))
    F2 = L.fake_factor(rm.lookup(d["mu2_pt"], d["mu2_eta"]))
    c = d["cat"]
    fac = np.where(c == "TL", F2, np.where(c == "LT", F1, np.where(c == "LL", -F1 * F2, 0.0)))
    return np.where(ok, d["weight"] * fac, 0.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lmax", type=float, default=0.4)
    ap.add_argument("--pt", default="53,4000")
    a = ap.parse_args()
    txt = []
    P = lambda *x: (txt.append(" ".join(str(y) for y in x)), print(*x))  # noqa: E731
    lo, missing = FR.load()
    P(f"# data fake rate, FOLOW SS 60<mll<300, FO baseline. loose iso<{a.lmax:g}, tight iso<{L.TIGHT_ISO}.")
    P("# f = (data T - prompt MC T) / (data loose - prompt MC loose); prompt MC = truth-P muons, noQCD.")
    P(f"# samples not complete / missing: {missing}")
    for pts in ([float(x) for x in a.pt.split(",")], [53, 60, 80, 120, 200, 4000]):
        rm, rD, rP, rMC = maps(lo, a.lmax, pts)
        P("\n" + rm.table(f"DATA, prompt-subtracted, pT {pts}"))
        P("\n" + rD.table("data (no subtraction)"))
        P("\n" + rP.table("prompt MC (truth-P muons) to subtract"))
        with np.errstate(divide="ignore", invalid="ignore"):
            P(f"# prompt MC fraction of data: tight {np.array2string(rP.T / rD.T, precision=3)}"
              f"  loose {np.array2string((rP.T + rP.L) / (rD.T + rD.L), precision=3)}")
        P("\n" + rMC.table("MC as pseudo-data, same method (= truth non-P map)"))
        with np.errstate(divide="ignore", invalid="ignore"):
            P(f"# data / MC: {np.array2string(rm.r / rMC.r, precision=3)}")

    # MC closure of the same method in the SR (noQCD): MC map -> SR SS AR with LNT-prompt subtraction
    rm, _, _, rMC = maps(lo, a.lmax, [float(x) for x in a.pt.split(",")])
    del lo
    sr, _ = L.load()
    reg = L.sel(sr, "SS", "Full") & FA.bkg_mask(sr, False)
    tgt = sr["weight"][reg & (sr["cat"] == "TT") & (sr["pair"] != "PP")].sum()
    P("\n## MC closure, SR SS (mll>400, mlljj>800), noQCD: target = MC iso-TT not PP (F or U)")
    for lab, m_ in (("MC map", rMC), ("data map", rm)):
        pa = ff_weights(sr, reg, m_, a.lmax).sum()
        pp = ff_weights(sr, reg & lnt_prompt(sr), m_, a.lmax).sum()
        pold = ff_weights(sr, reg & (sr["pair"] == "PP"), m_, a.lmax).sum()
        P(f"  {lab:9s} AR {pa:7.2f}  - LNT-prompt {pp:6.2f} = {pa - pp:7.2f}  target {tgt:6.2f}  ratio {(pa - pp) / tgt:.3f}"
          f"   | old (-PP only {pold:6.2f}) = {pa - pold:7.2f}")
    out = os.path.join(L.RESULTS, "24_fr_data_promptsub.txt")
    open(out, "w").write("\n".join(txt) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    sys.exit(main())
