#!/usr/bin/env python3
"""SR-sideband (data-usable) test of the SS mumu fake-factor method WITH DATA.
Sidebands (FO baseline, outside the SR mll>400 && mlljj>800):
  SB-A  mll>400, mlljj<800      SB-B  200<mll<400 (any mlljj)
MC  : the SR FOMode skims (skim/hnwr_fo; mll>200, no mlljj cut) restricted to the sidebands.
Data: FOMode,FOSB,RFlav production (skim/hnwr_fosb, Muon0/1). The data tree never holds the SR window;
      this script refuses to run if any data event is inside it.

  1. data vs MC per charge x iso category in SB-A / SB-B (noQCD, +QCD)
  2. calibration: pred = sum_data(fail) w_FF - sum_MC(fail, truth PP) w_FF,  obs = data(TT) - MC(TT, truth PP),
     k = obs/pred with the MC sideband map (SB-AB SS+OS truth F) -> the data/MC scale of the fake rate;
     the same estimator on MC (MC as pseudo-data) vs MC truth nonprompt TT.
  3. OS prompt isolation: per-muon T fraction by pT, data vs MC.
Writes results/12_sb_data.txt / .json.
"""
import glob
import os
import sys

import numpy as np

import fo_analysis as FA
import folib as L

SKIM_SB = os.path.join(L.STUDY, "skim", "hnwr_fosb")


def load_data():
    cols = {}
    for f in sorted(glob.glob(os.path.join(SKIM_SB, "*.npz"))):
        d = np.load(f)
        for k in [k for k in d.files if k.startswith("FO__")]:
            cols.setdefault(k[4:], []).append(d[k])
    ev = {k: np.concatenate(v) for k, v in cols.items()}
    if ((ev["mll"] > 400) & (ev["mlljj"] > 800)).any():
        raise RuntimeError("data event inside the SR window -- stop")
    ev["cat"] = L.iso_cat(ev)
    ev["ss"] = ev["mu1_charge"] * ev["mu2_charge"] > 0
    ev["base"] = (ev["nLooseMuon"] == 2) & (ev["nLooseElectron"] == 0)
    ev["weight"] = np.ones(len(ev["mll"]))
    return ev, len(glob.glob(os.path.join(SKIM_SB, "*.npz")))


def S(w):
    w = np.asarray(w, np.float64)
    return np.array([w.sum(), (w ** 2).sum(), len(w)])


def f(t, p=2):
    return f"{t[0]:.{p}f}±{np.sqrt(t[1]):.{p}f} [{int(t[2])}]"


def ratio(a, b):
    if b[0] == 0:
        return np.nan, np.nan
    r = a[0] / b[0]
    return r, abs(r) * np.sqrt((a[1] / a[0] ** 2 if a[0] else 0) + b[1] / b[0] ** 2)


def sbmask(d, k):
    a = (d["mll"] > 400) & (d["mlljj"] < 800)
    b = (d["mll"] > 200) & (d["mll"] < 400)
    return {"SB-A": a, "SB-B": b, "SB-AB": a | b}[k]


def main():
    txt, J = [], {}
    P = lambda *x: (txt.append(" ".join(str(y) for y in x)), print(*x))  # noqa: E731
    D, nfiles = load_data()
    M, _ = L.load()
    noQ = FA.bkg_mask(M, False)
    wQ = FA.bkg_mask(M, True)
    P(f"# SR sideband, FO baseline. Data files {nfiles} (Muon0/1 periods), data events {len(D['mll'])}. MC: W+jets HT.")
    P("# yields: signed sumw ± sqrt(sumw2) [raw]")

    fmap = FA.build_map(M, M["base"] & sbmask(M, "SB-AB") & noQ, "F")
    fmapSS = FA.build_map(M, M["base"] & M["ss"] & sbmask(M, "SB-AB") & noQ, "F")
    P(fmap.table("MC map SB-AB SS+OS, truth F, noQCD"))
    J["map|SB-AB SS+OS"] = [fmap.r, fmap.err]

    for sb in ("SB-A", "SB-B", "SB-AB"):
        for ch in ("SS", "OS"):
            cD = D["base"] & (D["ss"] if ch == "SS" else ~D["ss"]) & sbmask(D, sb)
            cM = M["base"] & (M["ss"] if ch == "SS" else ~M["ss"]) & sbmask(M, sb)
            P(f"\n## {sb} {ch}")
            P("".ljust(16) + "".join(k.rjust(26) for k in L.CATS))
            rows = {"MC noQCD": [S(M["weight"][cM & noQ & (M["cat"] == k)]) for k in L.CATS],
                    "MC +QCD": [S(M["weight"][cM & wQ & (M["cat"] == k)]) for k in L.CATS],
                    "data": [S(D["weight"][cD & (D["cat"] == k)]) for k in L.CATS]}
            for r, v in rows.items():
                P(r.ljust(16) + "".join(f(x).rjust(26) for x in v))
                for k, x in zip(L.CATS, v):
                    J[f"yield|{sb}|{ch}|{r}|{k}"] = x
            for ref in ("MC noQCD", "MC +QCD"):
                P(f"data/{ref}".ljust(16) + "".join((lambda q: f"{q[0]:.3f}±{q[1]:.3f}")(ratio(a, b)).rjust(26)
                                                     for a, b in zip(rows["data"], rows[ref])))
            if ch != "SS":
                continue
            fail_D, fail_M = D["cat"] != "TT", M["cat"] != "TT"
            for mname, fm in (("SB-AB SS+OS", fmap), ("SB-AB SS", fmapSS)):
                for qlab, mm in (("noQCD", noQ), ("+QCD", wQ)):
                    wD = L.ff_prediction(D, cD & fail_D, fm)
                    wPP = L.ff_prediction(M, cM & mm & fail_M & (M["pair"] == "PP"), fm)
                    pred = np.array([wD.sum() - wPP.sum(), (wD ** 2).sum() + (wPP ** 2).sum(), 0])
                    oD = S(D["weight"][cD & (D["cat"] == "TT")])
                    pr = S(M["weight"][cM & mm & (M["cat"] == "TT") & (M["pair"] == "PP")])
                    obs = np.array([oD[0] - pr[0], oD[1] + pr[1], 0])
                    wM = L.ff_prediction(M, cM & mm & fail_M, fm)
                    predMC = np.array([wM.sum() - wPP.sum(), (wM ** 2).sum() + (wPP ** 2).sum(), 0])
                    tF = S(M["weight"][cM & mm & (M["cat"] == "TT") & np.isin(M["pair"], ["PF", "FP", "FF"])])
                    k, ke = ratio(obs, pred)
                    rm, rme = ratio(predMC, tF)
                    P(f"  method map {mname:12s} {qlab:6s} data: pred {pred[0]:8.2f}±{np.sqrt(pred[1]):.2f}  "
                      f"obs(TT-prompt) {obs[0]:8.2f}±{np.sqrt(obs[1]):.2f}  obs/pred {k:.3f}±{ke:.3f} | "
                      f"MC: pred {predMC[0]:.2f} truth F {tF[0]:.2f} pred/F {rm:.3f}±{rme:.3f}")
                    J[f"method|{sb}|{mname}|{qlab}"] = dict(pred=pred, obs=obs, predMC=predMC, truthF=tF, k=[k, ke])

    P("\n## OS sideband per-muon T fraction by pT (both muons), data vs MC noQCD")
    edges = [53, 60, 80, 120, 200, 4000]
    for sb in ("SB-A", "SB-B"):
        for lab, d, m in (("data", D, D["base"] & ~D["ss"] & sbmask(D, sb)),
                          ("MC", M, M["base"] & ~M["ss"] & sbmask(M, sb) & noQ)):
            rm = L.RateMap(edges, [0, 2.4])
            for k in (1, 2):
                rm.fill(d[f"mu{k}_pt"][m], d[f"mu{k}_eta"][m], d[f"mu{k}_tkRelIso"][m] < L.TIGHT_ISO, d["weight"][m])
            P(f"  {sb} {lab:5s} " + "  ".join(f"{edges[i]}-{edges[i + 1]}: {rm.r[i, 0]:.4f}±{rm.err[i, 0]:.4f}"
                                             for i in range(len(edges) - 1)))
            J[f"osTeff|{sb}|{lab}"] = [rm.r[:, 0], rm.err[:, 0]]

    out_t, out_j = FA.out_paths("12_sb_data")
    open(out_t, "w").write("\n".join(txt) + "\n")
    FA.dumpj(J, out_j)
    print("wrote", out_t)


if __name__ == "__main__":
    sys.exit(main())
