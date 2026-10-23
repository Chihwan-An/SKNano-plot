#!/usr/bin/env python3
"""MC closure of fake-rate maps measured in data-usable sidebands of the SR selection (outside the SR),
applied to the SS SR (mll>400, mlljj>800). MC only (SR FOMode skims), noQCD unless noted.

Sidebands (FO baseline, SS; OS+SS variant too):
  SB-A  mll>400, mlljj<800                  (same mll as the SR, below the SR mass cut)
  SB-B  200<mll<400, any mlljj              (below the SR mll cut)
  SB-AB union of the two
Targets: SS SR Full / Low / High window, truth-nonprompt iso-TT (F; F+U also printed).
Also: signal yield / S/B in each sideband, fake-muon origin fractions sideband vs SR.

  sideband_closure.py   -> results/11_sideband_closure.txt / .json
"""
import sys

import numpy as np

import fo_analysis as FA
import folib as L

RNG = np.random.default_rng(7)


def main():
    txt, J = [], {}
    P = lambda *x: (txt.append(" ".join(str(y) for y in x)), print(*x))  # noqa: E731
    d, _ = L.load()
    b = FA.bkg_mask(d, False)
    bq = FA.bkg_mask(d, True)
    ss, os_ = d["base"] & d["ss"], d["base"] & ~d["ss"]
    sbA = (d["mll"] > 400) & (d["mlljj"] < 800)
    sbB = (d["mll"] > 200) & (d["mll"] < 400)
    SB = {"SB-A": sbA, "SB-B": sbB, "SB-AB": sbA | sbB}
    P("# fake-rate maps from data-usable sidebands -> SS SR. MC only, truth-F map, W+jets HT, noQCD (QCD rows marked).")

    # ---- sideband content and signal contamination
    P("\n## sideband yields (SS, noQCD) and signal S/B per iso category")
    for k, m in SB.items():
        row = {c: d["weight"][ss & m & b & (d["cat"] == c)].sum() for c in L.CATS}
        P(f"  {k:6s} bkg " + "  ".join(f"{c} {v:8.2f}" for c, v in row.items()))
        for s in L.SIGNALS6:
            sm = ss & m & (d["proc"] == "SIG_" + s)
            sv = {c: d["weight"][sm & (d["cat"] == c)].sum() for c in L.CATS}
            P(f"         {s:14s} " + "  ".join(f"{c} {sv[c]:7.3f} (S/B {sv[c] / row[c] if row[c] else np.nan:.3f})" for c in L.CATS))
            J[f"sig|{k}|{s}"] = sv
        J[f"bkg|{k}"] = row

    # ---- fake-muon origin, sideband vs SR (fail muon of TL/LT, truth F)
    P("\n## origin of the failing truth-F muon (TL: sub, LT: lead), SS noQCD, fraction of sumw")
    SRm = (d["mll"] > 400) & (d["mlljj"] > 800)
    for k, m in list(SB.items()) + [("SR", SRm)]:
        fr = {}
        tot = 0.0
        for cat, mu in (("TL", 2), ("LT", 1)):
            mk = ss & m & b & (d["cat"] == cat) & (d[f"t{mu}"] == "F")
            for o in np.unique(d[f"mu{mu}_genOrigin"][mk]):
                w = d["weight"][mk & (d[f"mu{mu}_genOrigin"] == o)].sum()
                fr[L.ORIGIN_NAMES.get(int(o), str(o))] = fr.get(L.ORIGIN_NAMES.get(int(o), str(o)), 0) + w
                tot += w
        P(f"  {k:6s} " + ", ".join(f"{o} {v / tot:.2f}" for o, v in sorted(fr.items(), key=lambda x: -x[1]) if v / tot >= 0.01))
        # pT of that muon
        J[f"origin|{k}"] = {o: v / tot for o, v in fr.items()}

    # ---- maps
    maps = {}
    for k, m in SB.items():
        maps[f"{k} SS"] = FA.build_map(d, ss & m & b, "F")
        maps[f"{k} SS+OS"] = FA.build_map(d, (ss | os_) & m & b, "F")
    maps["SR low (in-SR ref)"] = FA.build_map(d, ss & (d["mll"] > 400) & L.window(d, "Low") & b, "F")
    maps["SB-AB SS+OS +QCD"] = FA.build_map(d, (ss | os_) & (sbA | sbB) & bq, "F")
    P("\n## maps (truth F, weighted r = T/FO)")
    for k in ("SB-A SS", "SB-B SS", "SB-AB SS+OS", "SR low (in-SR ref)"):
        P(maps[k].table(k))
        J[f"map|{k}"] = [maps[k].r, maps[k].err]

    # ---- closure in the SR
    P("\n## closure: map -> SS SR, truth-F AR only (pred) vs truth nonprompt iso-TT (target), noQCD")
    P("   map                     window   pred ± MC ± map          target F        pred/F     pred/(F+U)")
    for mk_name, fm in maps.items():
        for win in ("Full", "Low", "High"):
            reg = ss & (d["mll"] > 400) & L.window(d, win) & (bq if "+QCD" in mk_name else b)
            ar = reg & (d["cat"] != "TT") & ((d["t1"] == "F") | (d["t2"] == "F"))
            # truth-F application region: the failing muon(s) must be F (as in the SR study closure)
            fail_F = np.where(d["cat"] == "TL", d["t2"] == "F", np.where(d["cat"] == "LT", d["t1"] == "F",
                              (d["t1"] == "F") & (d["t2"] == "F")))
            ar = reg & (d["cat"] != "TT") & fail_F
            w = L.ff_prediction(d, ar, fm)
            toys = [L.ff_prediction(d, ar, fm, r=r).sum() for r in fm.toys(100, RNG)]
            tgtF = L.ws(d["weight"][reg & (d["cat"] == "TT") & np.isin(d["pair"], ["PF", "FP", "FF"])])
            tgtFU = d["weight"][reg & (d["cat"] == "TT") & (d["pair"] != "PP")].sum()
            p = w.sum()
            P(f"   {mk_name:22s} {win:5s} {p:8.3f} ± {np.sqrt((w ** 2).sum()):.3f} ± {FA.spread(np.array(toys)):.3f}"
              f"   {tgtF[0]:8.3f}±{np.sqrt(tgtF[1]):.3f}   {p / tgtF[0]:.3f}      {p / tgtFU:.3f}")
            J[f"closure|{mk_name}|{win}"] = dict(pred=p, pred_mc=np.sqrt((w ** 2).sum()), pred_map=FA.spread(np.array(toys)),
                                                  tgtF=tgtF[0], tgtF_err=np.sqrt(tgtF[1]), tgtFU=tgtFU)

    out_t, out_j = FA.out_paths("11_sideband_closure")
    open(out_t, "w").write("\n".join(txt) + "\n")
    FA.dumpj(J, out_j)
    print("wrote", out_t)


if __name__ == "__main__":
    sys.exit(main())
