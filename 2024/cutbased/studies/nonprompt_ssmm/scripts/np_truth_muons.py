#!/usr/bin/env python3
"""Which muon is the nonprompt one in TTLJ / W+jets events of the card SS mumu regions, and where it comes from.
Regions (card definition: iso-TT, exactly two tight muons, no tight electron, SS):
  rMuMuSR_SS    : SR FO skims (skim/hnwr_fo), mll>400, mlljj>800
  rDYMuMuCR_SS  : DY CR FO skims (skim/hnwr_fodycr), 60<=mll<150, mlljj>800
Per process: yield, truth pair (lead/sub: P prompt, F nonprompt, U no gen muon), which muon is F,
origin of the F muon (b direct / b->c / c / nonprompt tau / light / none), its pT and dR to the nearest jet
is not stored -> pT and |eta| only.   -> results/14_np_truth_muons.txt
"""
import collections
import sys

import numpy as np

import dycr_analysis as DA
import folib as L

PROCS = ["TTLJ", "W+jets(HT)", "TTLL", "tW", "ST s/t", "DY", "VV", "ttV", "VVV"]
PT_EDGES = [53, 80, 120, 200, 300, 500, 4000]


def block(d, m, P, J, key):
    tot = d["weight"][m].sum()
    P(f"  total {tot:.2f} [{m.sum()} raw]")
    J[key + "|total"] = tot
    pairs = collections.Counter()
    for pp in np.unique(d["pair"][m]):
        pairs[pp] = d["weight"][m & (d["pair"] == pp)].sum()
    P("  truth pair (lead,sub): " + ", ".join(f"{k} {v / tot:.2f}" for k, v in pairs.most_common() if abs(v / tot) >= 0.01))
    J[key + "|pairs"] = {k: v / tot for k, v in pairs.items()}
    # the nonprompt muon(s): F; if none is F, U (no gen muon) is reported separately
    orig = collections.Counter()
    which = collections.Counter()
    pts = {"lead": [], "sub": []}
    wts = {"lead": [], "sub": []}
    for k, lab in ((1, "lead"), (2, "sub")):
        mk = m & (d[f"t{k}"] != "P")
        for o in np.unique(d[f"mu{k}_genOrigin"][mk]):
            orig[L.ORIGIN_NAMES.get(int(o), str(o))] += d["weight"][mk & (d[f"mu{k}_genOrigin"] == o)].sum()
        which[lab] = d["weight"][mk].sum()
        pts[lab] = d[f"mu{k}_pt"][mk]
        wts[lab] = d["weight"][mk]
    nt = sum(orig.values())
    P(f"  non-prompt muon is: lead {which['lead'] / nt:.2f}, sub {which['sub'] / nt:.2f} (of {nt:.2f} non-prompt muons)")
    P("  its origin: " + ", ".join(f"{k} {v / nt:.2f}" for k, v in orig.most_common() if abs(v / nt) >= 0.005))
    J[key + "|origin"] = {k: v / nt for k, v in orig.items()}
    J[key + "|which"] = {k: v / nt for k, v in which.items()}
    allpt = np.concatenate([pts["lead"], pts["sub"]])
    allw = np.concatenate([wts["lead"], wts["sub"]])
    h = np.histogram(allpt, PT_EDGES, weights=allw)[0]
    P("  its pT: " + "  ".join(f"{PT_EDGES[i]}-{PT_EDGES[i + 1]} {h[i] / nt:.2f}" for i in range(len(h))))


def main():
    txt, J = [], {}
    P = lambda *x: (txt.append(" ".join(str(y) for y in x)), print(*x))  # noqa: E731
    P("# card SS mumu regions: iso-TT, nTightMuon==2, nTightElectron==0. Weighted MC (signed). W+jets = HT set.")
    P("# origin: 'no gen mu' = no gen muon (genPartIdx and dR<0.3 fallback both fail); 'prompt tau' counts as prompt.")
    sr, _ = L.load()
    dy, _ = DA.load_dy()
    regions = [
        ("rMuMuSR_SS", sr, lambda d: (d["mll"] > 400) & (d["mlljj"] > 800)),
        ("rDYMuMuCR_SS", dy, lambda d: np.ones(len(d["mll"]), bool)),
    ]
    for rname, d, win in regions:
        base = d["ss"] & (d["cat"] == "TT") & (d["nTightMuon"] == 2) & (d["nTightElectron"] == 0) & win(d)
        if "isSig" in d:
            base &= ~d["isSig"]
        if "data" in d:
            base &= ~d["data"]
        P(f"\n######## {rname}")
        procs = [p for p in PROCS if (base & (d["proc"] == p)).any()]
        tot_all = d["weight"][base & ~np.array([p.startswith("QCD") for p in d["proc"]])].sum()
        P("  process yields (noQCD): " + ", ".join(f"{p} {d['weight'][base & (d['proc'] == p)].sum():.2f}" for p in procs)
          + f"  | total {tot_all:.2f}")
        for p in ("TTLJ", "W+jets(HT)"):
            m = base & (d["proc"] == p)
            P(f"\n## {rname} / {p}")
            block(d, m, P, J, f"{rname}|{p}")
    out_t = L.RESULTS + "/14_np_truth_muons.txt"
    open(out_t, "w").write("\n".join(txt) + "\n")
    import fo_analysis as FA
    FA.dumpj(J, L.RESULTS + "/14_np_truth_muons.json")
    print("wrote", out_t)


if __name__ == "__main__":
    sys.exit(main())
