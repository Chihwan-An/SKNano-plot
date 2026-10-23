#!/usr/bin/env python3
"""Which samples fill the card 'Nonprompt' group in each card region (Central, MC yield in the card mlljj range).
Uses the card post_processor's REGION_CONFIG / classify_file on the cbv15dc_ht linkfarm (W+jets = HT set, VVV added).
Nonprompt split: TTLJ (TTtoLNu2Q), W+jets (HT), single top t-/s-channel. Other groups printed for context.

  np_composition_regions.py [--input BDT/SR/test/cbv15dc_ht/input2024]  -> results/13_np_composition_regions.txt
"""
import argparse
import collections
import glob
import os
import sys

import ROOT

T = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test"
sys.path.insert(0, os.path.join(T, "cbv15"))
import post_processor_chsplit as PP  # noqa: E402

import folib as L  # noqa: E402

# card regions of cbv15_an2 (EE SS categories are merged in the cards)
REGIONS = [("bEESR", ["bEESR"]), ("bMuMuSR", ["bMuMuSR"]),
           ("rEESR_OS", ["rEESR_OS"]), ("rEESR_SS", ["rEESR_SS_2e", "rEESR_SS_lt2"]),
           ("rMuMuSR_OS", ["rMuMuSR_OS"]), ("rMuMuSR_SS", ["rMuMuSR_SS"]),
           ("bDYEECR", ["bDYEECR"]), ("rDYEECR_OS", ["rDYEECR_OS"]), ("rDYEECR_SS", ["rDYEECR_SS_2e", "rDYEECR_SS_lt2"]),
           ("bDYMuMuCR", ["bDYMuMuCR"]), ("rDYMuMuCR_OS", ["rDYMuMuCR_OS"]), ("rDYMuMuCR_SS", ["rDYMuMuCR_SS"]),
           ("bFlvEMuCR", ["bFlvEMuCR"]), ("bFlvMuECR", ["bFlvMuECR"]), ("rFlvCR", ["rFlvCR"])]


def np_sub(base):
    if "TTLJ" in base or "TTtoLNu2Q" in base:
        return "TTLJ"
    if "WtoLNu" in base or "WJet" in base:
        return "W+jets"
    if "ST_tch" in base or "t-channel" in base:
        return "ST t-ch"
    if "ST_sch" in base and "powheg" in base:
        return "ST s-ch powheg"
    if "ST_sch" in base or "s-channel" in base:
        return "ST s-ch"
    return "other:" + base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=os.path.join(T, "cbv15dc_ht", "input2024"))
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(a.input, "*.root")))
    Y = collections.defaultdict(float)          # (region, key) -> yield
    for fn in files:
        base = os.path.basename(fn)[:-5]
        opened = None
        for reg, subs in REGIONS:
            for r in subs:
                cfg = PP.REGION_CONFIG.get(r)
                if cfg is None:
                    continue
                kind, label = PP.classify_file(base, cfg["data"], cfg.get("sig_channel"))
                if kind != "mc":
                    continue
                # the card map sends ST_tch/ST_sch to TT ("ST" matches first); here they count as Nonprompt
                if base.startswith(("ST_tch", "ST_sch")):
                    label = "Nonprompt"
                if opened is None:
                    opened = ROOT.TFile.Open(fn)
                hns = cfg["hist"] if isinstance(cfg["hist"], (list, tuple)) else [cfg["hist"]]
                lo, hi = cfg["bins"][0], cfg["bins"][-1]
                v, found = 0.0, False
                for hn in hns:   # rEESR_SS_lt2 / rDYEECR_SS_lt2 sum two histograms (1e + 0e tightCharge)
                    h = opened.Get(f"Central/{hn}")
                    if h:
                        found = True
                        v += h.Integral(h.FindBin(lo + 1e-6), h.FindBin(hi - 1e-6))
                if not found:
                    continue
                Y[(reg, label)] += v
                if label == "Nonprompt":
                    Y[(reg, "NP:" + np_sub(base))] += v
        if opened:
            opened.Close()
    txt = []
    P = lambda *x: (txt.append(" ".join(str(y) for y in x)), print(*x))  # noqa: E731
    P(f"# Nonprompt composition per card region, Central MC, card mlljj range. input {a.input}")
    P("# columns: Nonprompt total | TTLJ  W+jets(HT)  ST t-ch  ST s-ch  ST s-ch powheg (fraction of Nonprompt) | other groups")
    P("# ST t/s moved from the card's TT group to Nonprompt here. ST s-ch has two overlapping sets (default + powheg) in the")
    P("# card linkfarm -> both are summed in the card (double counting); both are counted here too and shown separately.")
    head = f"{'region':14s} {'Nonprompt':>9s} | {'TTLJ':>14s} {'W+jets':>14s} {'ST t':>13s} {'ST s':>13s} {'ST s pw':>13s} | {'DYJets':>9s} {'TT':>9s} {'Others':>8s}  NP/bkg"
    P(head)
    for reg, _ in REGIONS:
        npt = Y[(reg, "Nonprompt")]
        parts = [Y[(reg, "NP:" + k)] for k in ("TTLJ", "W+jets", "ST t-ch", "ST s-ch", "ST s-ch powheg")]
        others = {g: Y[(reg, g)] for g in ("DYJets", "TT", "Others")}
        tot = npt + sum(others.values())
        P(f"{reg:14s} {npt:9.2f} | " + " ".join(f"{p:7.2f} ({p / npt if npt else 0:4.0%})" for p in parts[:2])
          + " " + " ".join(f"{p:6.2f} ({p / npt if npt else 0:3.0%})" for p in parts[2:])
          + f" | {others['DYJets']:9.1f} {others['TT']:9.1f} {others['Others']:8.1f}  {npt / tot if tot else 0:5.1%}")
        extra = {k: v for (r, k), v in Y.items() if r == reg and k.startswith("NP:other")}
        if extra:
            P("      unclassified NP:", extra)
    out = os.path.join(L.RESULTS, "13_np_composition_regions.txt")
    open(out, "w").write("\n".join(txt) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
