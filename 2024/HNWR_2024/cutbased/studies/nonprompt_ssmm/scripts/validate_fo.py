#!/usr/bin/env python3
"""Validate the FO tree against the standard HNWR SR histograms.

For every FOMode output sample:
  (a) same job: FO events with the HNWR SR lepton condition (exactly two T muons, no T
      electron, iso-TT, mll>400, mlljj>800) vs the SR_Resolved_MM_{OS,SS}_mlljj integral
      above 800 GeV written by the same job -> must agree (the FO pair can differ from the
      T pair only when a harder L muon exists; counted separately).
  (b) production: the same histograms vs the card-input production
      (HNWR/RFlav_DYCRCharge/2024) -> reproducibility of the weights.
MC only.
"""
import argparse
import glob
import os

import numpy as np
import ROOT

import folib as L

CARD_INPUT = "/gv0/Users/achihwan/SKNanoOutput/HNWR/RFlav_DYCRCharge/2024"


def hist_int(f, name, lo=800.0):
    h = f.Get(name)
    if not h:
        return None
    b = h.GetXaxis().FindBin(lo + 1e-3)
    return h.Integral(b, h.GetNbinsX() + 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skim", default=L.SKIM)
    ap.add_argument("--fo-out", default="/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/FOMode_RFlav/2024")
    ap.add_argument("--out", default=os.path.join(L.RESULTS, "01_validate_fo.txt"))
    a = ap.parse_args()
    lines = ["# sample  ch  FO(TTcond)  FO(TTcond, nLooseMuon==2)  hist(same job)  ratio  | card-input hist  ratio(job/card)"]
    for f in sorted(glob.glob(os.path.join(a.skim, "*.npz"))):
        s = os.path.basename(f)[:-4]
        d = np.load(f)
        if "FO__weight" not in d.files:
            continue
        ev = {k[4:]: d[k] for k in d.files if k.startswith("FO__")}
        tt = (ev["mu1_tkRelIso"] < 0.1) & (ev["mu2_tkRelIso"] < 0.1)
        cond = tt & (ev["nTightMuon"] == 2) & (ev["nTightElectron"] == 0) & (ev["mll"] > 400) & (ev["mlljj"] > 800)
        ss = ev["mu1_charge"] * ev["mu2_charge"] > 0
        def npz_int(ch, lo=800.0):
            k = f"hist__SR_Resolved_MM_{ch}_mlljj"
            if k not in d.files:
                return None
            c, e = d[k], d[k + "__edges"]  # c has under/overflow at 0 and -1; e = low edges of bins 1..n+1
            first = int(np.searchsorted(e, lo + 1e-3, side="right"))  # bin index (1-based) containing lo
            return float(c[first:].sum())
        cin = os.path.join(CARD_INPUT, s + ".root")
        cards = [ROOT.TFile.Open(cin)] if os.path.exists(cin) else \
            [ROOT.TFile.Open(x) for x in sorted(glob.glob(os.path.join(CARD_INPUT, s + "_p[0-9][0-9].root")))]
        for ch, m in (("OS", ~ss), ("SS", ss)):
            fo = ev["weight"][cond & m].sum()
            fo2 = ev["weight"][cond & m & (ev["nLooseMuon"] == 2)].sum()
            hj = npz_int(ch)
            parts = [hist_int(c, f"Central/SR_Resolved_MM_{ch}_mlljj") for c in cards]
            hc = sum(x for x in parts if x is not None) if any(x is not None for x in parts) else None
            r1 = f"{fo / hj:.5f}" if hj else "-"
            r2 = f"{hj / hc:.5f}" if (hj and hc) else "-"
            lines.append(f"{s:60s} {ch} {fo:12.4f} {fo2:12.4f} {hj if hj is None else round(hj, 4)!s:>12} {r1:>9} | "
                         f"{hc if hc is None else round(hc, 4)!s:>12} {r2:>9}")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
