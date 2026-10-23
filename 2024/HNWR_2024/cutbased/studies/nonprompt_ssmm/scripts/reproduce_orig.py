#!/usr/bin/env python3
"""Step 2: reproduce the earlier MC numbers from the ORIGINAL presel ntuple skims.

iso-TT from Central_SR_MM (the production SR tree), iso-TL/LT from Central_SR_LL_MM.
Same cuts as before: mll>400, mlljj>800, OS/SS by lepChargeProduct, weight_Central.
Then: effect of the FO baseline (nLooseLepton==2) on iso-TT, QCD split, and the
comparison with the v3 card shapes.
"""
import argparse
import collections
import os

import numpy as np

import npcommon as C

CARD_SHAPES = ("/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/combine/scenarios/test/"
               "cbv15_an2_ref_v3/shapes_2024_cbv15_an2_ref_v3.root")


def card_yields():
    import ROOT
    f = ROOT.TFile.Open(CARD_SHAPES)
    out = {}
    for ch in ("rMuMuSR_OS", "rMuMuSR_SS"):
        d = f.Get(ch)
        for k in d.GetListOfKeys():
            n = k.GetName()
            if n.endswith("Up") or n.endswith("Down"):
                continue
            out[(ch, n)] = d.Get(n).Integral()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skim", default=os.path.join(C.STUDY, "skim", "orig"))
    ap.add_argument("--out", default=os.path.join(C.STUDY, "results", "02_reproduce.txt"))
    a = ap.parse_args()
    lines = []
    P = lines.append

    sr = C.load(a.skim, "SR_MM")
    ll = C.load(a.skim, "SR_LL_MM")
    for d in (sr, ll):
        d["group"] = np.array([C.group_of(s) for s in d["sample"]], dtype=object)
        d["proc"] = np.array([C.process_of(s) for s in d["sample"]], dtype=object)
    sr_cat = C.iso_cat(sr)
    ll_cat = C.iso_cat(ll)
    P(f"# sanity: SR_MM iso categories (must be all TT): {collections.Counter(sr_cat.tolist())}")
    P(f"# sanity: SR_LL_MM iso categories (no TT, no LL expected): {collections.Counter(ll_cat.tolist())}")
    P(f"# sanity: SR_LL_MM nLooseLepton values: {sorted(set(ll['nLooseLepton'].tolist()))}")
    P(f"# sanity: SR_MM nLooseLepton values: {collections.Counter(sr['nLooseLepton'].tolist())}")
    P(f"# sanity: ele1_isFilled any (SR_MM, SR_LL_MM): {sr['ele1_isFilled'].any()}, {ll['ele1_isFilled'].any()}")
    P(f"# sanity: pT ordering mu1>=mu2: {np.all(sr['mu1_pt'] >= sr['mu2_pt'])}, {np.all(ll['mu1_pt'] >= ll['mu2_pt'])}")

    bkg_groups = ["DYJets", "Nonprompt", "Others", "TT"]
    for ch in ("OS", "SS"):
        ms = C.base_mask(sr) & C.charge_mask(sr, ch)
        ml = C.base_mask(ll) & C.charge_mask(ll, ch)
        P(f"\n## {ch}  mll>400 mlljj>800  weighted sum ± sqrt(sumw2) [raw]")
        P(f"{'group':12s} {'iso-TT (SR_MM)':>26s} {'iso-TL':>24s} {'iso-LT':>24s} {'TL+LT':>24s}")
        tot = collections.defaultdict(lambda: [0., 0., 0])
        for g in bkg_groups + ["QCD"]:
            r = [C.wsum(sr["weight_Central"], ms & (sr["group"] == g)),
                 C.wsum(ll["weight_Central"], ml & (ll["group"] == g) & (ll_cat == "TL")),
                 C.wsum(ll["weight_Central"], ml & (ll["group"] == g) & (ll_cat == "LT")),
                 C.wsum(ll["weight_Central"], ml & (ll["group"] == g) & np.isin(ll_cat, ["TL", "LT"]))]
            P(f"{g:12s} " + " ".join(f"{C.fmt(*x):>24s}" for x in r))
            if g != "QCD":
                for i, x in enumerate(r):
                    tot[i][0] += x[0]; tot[i][1] += x[1]; tot[i][2] += x[2]
        P(f"{'sum noQCD':12s} " + " ".join(f"{C.fmt(*tot[i]):>24s}" for i in range(4)))
        q = [C.wsum(sr["weight_Central"], ms & (sr["group"] == "QCD")),
             C.wsum(ll["weight_Central"], ml & (ll["group"] == "QCD") & np.isin(ll_cat, ["TL", "LT"]))]
        P(f"{'sum +QCD':12s} TT {tot[0][0] + q[0][0]:.2f}   TL+LT {tot[3][0] + q[1][0]:.2f}"
          f"   TL:LT = {tot[1][0] / tot[2][0]:.2f}:1 (noQCD)")
        # FO baseline effect on iso-TT: exactly two loose leptons
        m2 = ms & (sr["nLooseLepton"] == 2) & np.isin(sr["group"], bkg_groups)
        P(f"iso-TT noQCD with nLooseLepton==2 (FO baseline): {C.fmt(*C.wsum(sr['weight_Central'], m2))}"
          f"  (all: {tot[0][0]:.2f}; removed {100 * (1 - C.wsum(sr['weight_Central'], m2)[0] / tot[0][0]):.2f}%)")
        # QCD by enrichment
        for sub in ("MuEnriched", "EMEnriched", "bcToE"):
            mq = ml & np.array([s.endswith(sub) for s in ll["sample"]]) & np.isin(ll_cat, ["TL", "LT"])
            mq2 = ms & np.array([s.endswith(sub) for s in sr["sample"]])
            P(f"  QCD {sub:10s}: iso-TT {C.fmt(*C.wsum(sr['weight_Central'], mq2))}   TL+LT {C.fmt(*C.wsum(ll['weight_Central'], mq))}")
        # duplicated s-channel single top (two generators both in the directory)
        for s in ("ST_sch_top_Lep", "ST_sch_top_Lep_powheg", "ST_sch_antitop_Lep", "ST_sch_antitop_Lep_powheg"):
            P(f"  {s:26s}: iso-TT {C.wsum(sr['weight_Central'], ms & (sr['sample'] == s))[0]:.3f}"
              f"  TL+LT {C.wsum(ll['weight_Central'], ml & (ll['sample'] == s) & np.isin(ll_cat, ['TL', 'LT']))[0]:.3f}")

    # card comparison (card = cut-based HNWR histograms, v3 scenario)
    try:
        cy = card_yields()
    except Exception as e:  # noqa: BLE001
        cy = {}
        P(f"card read failed: {e}")
    if cy:
        P("\n## v3 card rMuMuSR_{OS,SS} vs ntuple iso-TT (SR_MM tree, all nLoose)")
        for ch in ("OS", "SS"):
            ms = C.base_mask(sr) & C.charge_mask(sr, ch)
            for g in bkg_groups:
                nt = C.wsum(sr["weight_Central"], ms & (sr["group"] == g))[0]
                cv = cy.get((f"rMuMuSR_{ch}", g))
                P(f"  {ch} {g:10s} ntuple {nt:10.3f}  card {cv if cv is None else round(cv, 3)}"
                  + (f"  ratio {nt / cv:.4f}" if cv else ""))
            for s in C.SIGNALS6 + ["MWR2000_N200", "MWR1000_N200"]:
                nt = C.wsum(sr["weight_Central"], ms & (sr["group"] == "SIG_" + s))[0]
                key = "WR" + s.replace("MWR", "").replace("_N", "N") + "MM"
                cv = cy.get((f"rMuMuSR_{ch}", key))
                P(f"  {ch} {s:14s} ntuple {nt:10.3f}  card {cv if cv is None else round(cv, 3)}"
                  + (f"  ratio {nt / cv:.4f}" if cv else ""))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
