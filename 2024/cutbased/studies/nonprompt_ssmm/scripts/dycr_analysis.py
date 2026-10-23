#!/usr/bin/env python3
"""Resolved DY CR mumu (60 <= mll < 150, mlljj > 800) test of the SS nonprompt method with DATA.
Input: HNWR FOMode,FODYCR,RFlav production, skimmed to skim/hnwr_fodycr/*.npz (MC + Muon0/1 data).

  dycr_analysis.py            # tables -> results/10_dycr.txt / .json

Steps
  1. validation   FO iso-TT (two tight muons, no tight electron) vs HNWR DYCR_Resolved_MM_mlljj, data and MC
  2. yields       data vs MC per charge x iso category; MC by process and by truth pair
  3. method       fake-factor prediction of the nonprompt iso-TT from the fail categories:
                    pred = sum_data(fail) w_FF - sum_MC(fail, truth PP) w_FF      (prompt leakage subtracted)
                    obs  = data(TT) - MC(TT, truth PP)                            (prompt MC subtracted)
                  with the SR MC map (SS Low window, truth F; the map the SR study used) and a DY CR MC map.
                  The same estimator on MC (MC as pseudo-data) is compared to the MC truth nonprompt TT.
  4. prompt iso   OS (prompt dominated): data/MC of the fail fraction (TL+LT+LL)/all, i.e. the prompt
                  isolation efficiency modelling that the fail categories depend on.
W+jets = HT-binned set only. QCD reported with and without.
"""
import collections
import glob
import json
import os
import sys

import numpy as np

import folib as L
import fo_analysis as FA

SKIM_DY = os.path.join(L.STUDY, "skim", "hnwr_fodycr")
MLLJJ_EDGES = np.array([800, 1000, 1200, 1500, 2000, 8000], float)


def is_data(s):
    return s.startswith(("Skim_HNWR_Muon", "Muon"))


def load_dy():
    cols, names, hists = {}, [], {}
    for f in sorted(glob.glob(os.path.join(SKIM_DY, "*.npz"))):
        s = os.path.basename(f)[:-4]
        if "EGamma" in s:
            raise RuntimeError(f"EGamma in the DY CR mumu skim: {f}")
        if L.process_of(s) == "W+jets(MLNu)":
            continue
        d = np.load(f)
        hists[s] = {k[6:]: d[k] for k in d.files if k.startswith("hist__")}
        keys = [k for k in d.files if k.startswith("FO__")]
        if not keys or len(d[keys[0]]) == 0:
            continue
        for k in keys:
            cols.setdefault(k[4:], []).append(d[k])
        names.append(np.full(len(d[keys[0]]), s, dtype=object))
    ev = {k: np.concatenate(v) for k, v in cols.items()}
    ev["sample"] = np.concatenate(names)
    ev["data"] = np.array([is_data(s) for s in ev["sample"]])
    ev["proc"] = np.array(["data" if is_data(s) else L.process_of(s) for s in ev["sample"]], dtype=object)
    ev["cat"] = L.iso_cat(ev)
    ev["ss"] = ev["mu1_charge"] * ev["mu2_charge"] > 0
    ev["t1"] = np.where(ev["data"], "D", L.truth(ev["mu1_genOrigin"]))
    ev["t2"] = np.where(ev["data"], "D", L.truth(ev["mu2_genOrigin"]))
    ev["pair"] = np.char.add(ev["t1"].astype(str), ev["t2"].astype(str))
    ev["qcd"] = np.array([p.startswith("QCD") for p in ev["proc"]])
    ev["base"] = (ev["nLooseMuon"] == 2) & (ev["nLooseElectron"] == 0)
    ev["weight"] = ev["weight"].astype(np.float64)
    return ev, hists


def S(w):
    w = np.asarray(w, np.float64)
    return np.array([w.sum(), (w ** 2).sum(), len(w)])


def f(t, p=2):
    return f"{t[0]:.{p}f}±{np.sqrt(t[1]):.{p}f} [{int(t[2])}]"


def ratio(a, b):
    """a/b with uncorrelated errors; a, b = (sum, sumw2, n)."""
    if b[0] == 0:
        return np.nan, np.nan
    r = a[0] / b[0]
    return r, abs(r) * np.sqrt((a[1] / a[0] ** 2 if a[0] else 0) + b[1] / b[0] ** 2)


def main():
    txt, J = [], {}
    P = lambda *x: (txt.append(" ".join(str(y) for y in x)), print(*x))  # noqa: E731
    d, hists = load_dy()
    D, M = d["data"], ~d["data"]
    noQ = M & ~d["qcd"]
    P("# resolved DY CR mumu: 60<=mll<150, mlljj>800, FO baseline (exactly 2 FO muons, no FO electron).")
    P("# yields: signed sumw ± sqrt(sumw2) [raw]. Data weight 1. W+jets = HT set. 'noQCD' / '+QCD'.")
    P(f"# events in skim: data {D.sum()}, MC {M.sum()}")

    # ---------------------------------------------------------------- 1. validation
    P("\n## 1. validation: FO iso-TT (nTightMuon==2, nTightElectron==0) vs DYCR_Resolved_MM_mlljj")
    tt2 = (d["cat"] == "TT") & (d["nTightMuon"] == 2) & (d["nTightElectron"] == 0)
    groups = {"data": lambda s: is_data(s),
              "MC noQCD": lambda s: not is_data(s) and not s.startswith("QCD"),
              "MC QCD": lambda s: s.startswith("QCD")}
    for lab, m in (("data", D), ("MC noQCD", noQ), ("MC QCD", M & d["qcd"])):
        h = sum(hists[s].get("DYCR_Resolved_MM_mlljj", np.zeros(1)).sum() for s in hists if groups[lab](s))
        fo = d["weight"][tt2 & m].sum()
        P(f"  {lab:9s} FO-TT {fo:12.3f}   hist {h:12.3f}   ratio {fo / h if h else np.nan:.4f}")
        J[f"valid|{lab}"] = [fo, h]

    # ---------------------------------------------------------------- 2. yields
    P("\n## 2. data vs MC per charge x iso category (FO baseline)")
    procs = [p for p in L.PROCS_ORDER if (d["proc"] == p).any()]
    for ch in ("SS", "OS"):
        c = d["base"] & (d["ss"] if ch == "SS" else ~d["ss"])
        P(f"\n### {ch}")
        P("category".ljust(22) + "".join(k.rjust(26) for k in L.CATS))
        rows = collections.OrderedDict()
        for p in procs:
            rows[p] = [S(d["weight"][c & (d["proc"] == p) & (d["cat"] == k)]) for k in L.CATS]
        rows["MC noQCD"] = [S(d["weight"][c & noQ & (d["cat"] == k)]) for k in L.CATS]
        rows["MC +QCD"] = [S(d["weight"][c & M & (d["cat"] == k)]) for k in L.CATS]
        rows["data"] = [S(d["weight"][c & D & (d["cat"] == k)]) for k in L.CATS]
        for r, v in rows.items():
            P(r.ljust(22) + "".join(f(x).rjust(26) for x in v))
            for k, x in zip(L.CATS, v):
                J[f"yield|{ch}|{r}|{k}"] = x
        for ref in ("MC noQCD", "MC +QCD"):
            P(f"data/{ref}".ljust(22) + "".join(
                (lambda q: f"{q[0]:.3f}±{q[1]:.3f}")(ratio(a, b)).rjust(26) for a, b in zip(rows["data"], rows[ref])))
        P("truth pair (MC noQCD, fraction of sumw):")
        for k in L.CATS:
            mk = c & noQ & (d["cat"] == k)
            tot = d["weight"][mk].sum()
            fr = {pp: d["weight"][mk & (d["pair"] == pp)].sum() / tot for pp in sorted(set(d["pair"][mk]))} if tot else {}
            P(f"  iso-{k}: " + ", ".join(f"{pp} {v:.2f}" for pp, v in sorted(fr.items(), key=lambda x: -x[1]) if abs(v) >= 0.01))
            J[f"pair|{ch}|{k}"] = fr

    # ---------------------------------------------------------------- 3. method
    P("\n## 3. fake-factor method in the SS DY CR")
    sr, _ = L.load()                       # SR FO skim (MC only), for the map the SR study used
    srmaps = FA.maps(sr)
    del sr
    dySS = d["base"] & d["ss"]
    dyAll = d["base"]
    fmaps = {
        "SR_MC_lowSS": srmaps["F_lowSS"],
        "DYCR_MC_SS": FA.build_map(d, dySS & noQ, "F"),
        "DYCR_MC_SSOS": FA.build_map(d, dyAll & noQ, "F"),
    }
    P(fmaps["DYCR_MC_SSOS"].table("F map, DY CR MC noQCD, SS+OS, truth F"))
    J["map|DYCR_MC_SSOS"] = [fmaps["DYCR_MC_SSOS"].r, fmaps["DYCR_MC_SSOS"].err]
    J["map|SR_MC_lowSS"] = [fmaps["SR_MC_lowSS"].r, fmaps["SR_MC_lowSS"].err]
    fail = d["cat"] != "TT"
    TT = d["cat"] == "TT"
    for ch in ("SS", "OS"):
        c = d["base"] & (d["ss"] if ch == "SS" else ~d["ss"])
        for mname, fm in fmaps.items():
            for qlab, mcm in (("noQCD", noQ), ("+QCD", M)):
                wD = L.ff_prediction(d, c & D & fail, fm)
                wPP = L.ff_prediction(d, c & mcm & fail & (d["pair"] == "PP"), fm)
                pred = np.array([wD.sum() - wPP.sum(), (wD ** 2).sum() + (wPP ** 2).sum(), 0])
                obsD = S(d["weight"][c & D & TT])
                promptTT = S(d["weight"][c & mcm & TT & (d["pair"] == "PP")])
                obs = np.array([obsD[0] - promptTT[0], obsD[1] + promptTT[1], 0])
                # MC as pseudo-data
                wM = L.ff_prediction(d, c & mcm & fail, fm)
                predMC = np.array([wM.sum() - wPP.sum(), (wM ** 2).sum() + (wPP ** 2).sum(), 0])
                truthMC = S(d["weight"][c & mcm & TT & np.isin(d["pair"], ["PF", "FP", "FF"])])
                truthMCU = S(d["weight"][c & mcm & TT & (d["pair"] != "PP")])
                r_d = ratio(pred, obs)
                r_m = ratio(predMC, truthMC)
                r_mu = ratio(predMC, truthMCU)
                key = f"{ch}|{mname}|{qlab}"
                P(f"  {key:30s} data: pred {pred[0]:8.2f}±{np.sqrt(pred[1]):.2f}  obs(data TT - prompt MC) "
                  f"{obs[0]:8.2f}±{np.sqrt(obs[1]):.2f}  pred/obs {r_d[0]:.3f}±{r_d[1]:.3f} | "
                  f"MC: pred {predMC[0]:.2f}  truth F {truthMC[0]:.2f} (F+U {truthMCU[0]:.2f})  "
                  f"ratio {r_m[0]:.3f}±{r_m[1]:.3f} (F+U {r_mu[0]:.3f})")
                J[f"method|{key}"] = dict(pred=pred, obs=obs, obsData=obsD, promptTT=promptTT, predMC=predMC,
                                          truthMC=truthMC, truthMCU=truthMCU)
                # mlljj shape
                if qlab == "noQCD":
                    hD = np.histogram(d["mlljj"][c & D & fail], MLLJJ_EDGES, weights=wD)[0]
                    hPP = np.histogram(d["mlljj"][c & mcm & fail & (d["pair"] == "PP")], MLLJJ_EDGES, weights=wPP)[0]
                    hO = np.histogram(d["mlljj"][c & D & TT], MLLJJ_EDGES)[0].astype(float)
                    hPr = np.histogram(d["mlljj"][c & mcm & TT & (d["pair"] == "PP")], MLLJJ_EDGES,
                                       weights=d["weight"][c & mcm & TT & (d["pair"] == "PP")])[0]
                    hOther = np.histogram(d["mlljj"][c & mcm & TT & (d["pair"] != "PP")], MLLJJ_EDGES,
                                          weights=d["weight"][c & mcm & TT & (d["pair"] != "PP")])[0]
                    J[f"shape|{key}"] = dict(edges=MLLJJ_EDGES, pred=hD - hPP, data=hO, prompt=hPr, mcnp=hOther)

    # ---------------------------------------------------------------- 4. prompt isolation
    P("\n## 4. OS (prompt dominated): fail fraction (TL+LT+LL)/all, data vs MC")
    for ch in ("OS", "SS"):
        c = d["base"] & (d["ss"] if ch == "SS" else ~d["ss"])
        for lab, m in (("data", D), ("MC noQCD", noQ), ("MC +QCD", M)):
            a = d["weight"][c & m & fail].sum()
            t = d["weight"][c & m].sum()
            n = (c & m).sum()
            P(f"  {ch} {lab:9s} fail {a:10.2f} / all {t:10.2f} = {a / t if t else np.nan:.4f}  (raw {n})")
            J[f"failfrac|{ch}|{lab}"] = [a, t]
        # per muon: pT-binned prompt T efficiency in OS MC vs data (data treated as all prompt in OS)
    edges = [53, 60, 80, 120, 200, 4000]
    P("  OS per-muon T fraction by pT (data vs MC noQCD), both muons:")
    c = d["base"] & ~d["ss"]
    for lab, m in (("data", D), ("MC", noQ)):
        rm = L.RateMap(edges, [0, 2.4])
        for k in (1, 2):
            mk = c & m
            rm.fill(d[f"mu{k}_pt"][mk], d[f"mu{k}_eta"][mk], d[f"mu{k}_tkRelIso"][mk] < L.TIGHT_ISO, d["weight"][mk])
        P(f"    {lab:5s} " + "  ".join(f"{edges[i]}-{edges[i + 1]}: {rm.r[i, 0]:.4f}±{rm.err[i, 0]:.4f}"
                                        for i in range(len(edges) - 1)))
        J[f"osTeff|{lab}"] = [rm.r[:, 0], rm.err[:, 0]]

    out_t, out_j = FA.out_paths("10_dycr")
    open(out_t, "w").write("\n".join(txt) + "\n")
    FA.dumpj(J, out_j)
    print("wrote", out_t)


if __name__ == "__main__":
    sys.exit(main())
