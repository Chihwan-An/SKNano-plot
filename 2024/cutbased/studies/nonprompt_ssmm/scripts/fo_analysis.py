#!/usr/bin/env python3
"""Resolved SS mumu nonprompt study on the HNWR FOMode tree (MC only, no data).

  fo_analysis.py composition   # step 3: category x process x truth tables, signal S/B
  fo_analysis.py coverage      # pT/|eta| of truth-nonprompt muons, low vs high window
  fo_analysis.py fakerate      # step 4: MC fake-rate / prompt-efficiency maps
  fo_analysis.py closure       # step 4: low-window map -> high-window SS closure
  fo_analysis.py signal        # step 5: weighted signal leakage WS per SS bin
  fo_analysis.py all

Every table goes to results/<step>.txt and the numbers the plots need to results/<step>.json.
Defaults: FO baseline (exactly two FO muons, no FO electron), mll>400, W+jets = HT-binned set,
QCD excluded from the "B" sums and reported separately.
"""
import argparse
import collections
import json
import os
import sys

import numpy as np

import folib as L

PT_EDGES = [53, 60, 80, 120, 200, 4000]
ETA_EDGES = [0, 1.2, 2.4]
HIGH_EDGES = np.array([1600, 2000, 2400, 2800, 3200, 8000], float)
LOW_EDGES = np.array([800, 1000, 1200, 1400, 1600], float)
HIGH_MERGED = np.array([1600, 2000, 2400, 8000], float)  # enough target MC per bin for a shape test
RNG = np.random.default_rng(12345)
NTOY = 300


def _np(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer, np.bool_)):
        return o.item()
    raise TypeError(type(o))


def spread(toys, axis=0):
    """Robust toy spread: half the central 68% interval (toys near r->1 give heavy tails)."""
    q = np.nanpercentile(toys, [16, 84], axis=axis)
    return 0.5 * (q[1] - q[0])


def dumpj(J, path):
    json.dump(J, open(path, "w"), indent=1, default=_np)


def out_paths(name):
    os.makedirs(L.RESULTS, exist_ok=True)
    return os.path.join(L.RESULTS, name + ".txt"), os.path.join(L.RESULTS, name + ".json")


def bkg_mask(d, qcd=False):
    m = ~d["isSig"]
    if not qcd:
        m &= ~np.array([p.startswith("QCD") for p in d["proc"]])
    return m


def fail_muon_truth(d):
    """Truth of the failing muon(s): TL -> sub, LT -> lead, LL -> both (joined)."""
    return np.where(d["cat"] == "TL", d["t2"], np.where(d["cat"] == "LT", d["t1"],
                    np.where(d["cat"] == "LL", np.char.add(d["t1"].astype(str), d["t2"].astype(str)), "")))


# ------------------------------------------------------------------ step 3
def composition(d, store):
    txt, js = out_paths("03_composition")
    lines, J = [], {}
    P = lines.append
    procs = [p for p in L.PROCS_ORDER if p in set(d["proc"])]
    P("# FO baseline, mll>400. Yields: signed sumw ± sqrt(sumw2) [raw entries]. MC only.")
    P("# 'truth' is per muon: P prompt(+prompt tau), F nonprompt (b, b->c, c, nonprompt tau, light), U undetermined.")
    for ch in ("SS", "OS"):
        for win in ("Full", "Low", "High"):
            base = L.sel(d, ch, win)
            P(f"\n## {ch} {win}  ({'mlljj>800' if win == 'Full' else ('800<mlljj<1600' if win == 'Low' else 'mlljj>=1600')})")
            P("process".ljust(16) + "".join(f"iso-{c}".rjust(30) for c in L.CATS))
            for p in procs + ["sum noQCD", "sum +QCD"]:
                if p == "sum noQCD":
                    pm = bkg_mask(d, False)
                elif p == "sum +QCD":
                    pm = bkg_mask(d, True)
                else:
                    pm = d["proc"] == p
                row = p.ljust(16)
                for c in L.CATS:
                    t = L.ws(d["weight"][base & pm & (d["cat"] == c)])
                    row += L.fmt(t).rjust(30)
                    J[f"{ch}|{win}|{p}|{c}"] = t
                P(row)
            # truth pair composition, background noQCD and +QCD
            for qcd in (False, True):
                bm = base & bkg_mask(d, qcd)
                P(f"-- truth pair (lead,sub) fractions of {'bkg+QCD' if qcd else 'bkg noQCD'} per iso category:")
                pairs = sorted(set(d["pair"][bm].tolist()))
                P("pair".ljust(8) + "".join(f"iso-{c}".rjust(22) for c in L.CATS))
                for pr in pairs:
                    row = pr.ljust(8)
                    for c in L.CATS:
                        mc = bm & (d["cat"] == c)
                        tot = d["weight"][mc].sum()
                        t = L.ws(d["weight"][mc & (d["pair"] == pr)])
                        row += (f"{t[0]:.2f} ({100 * t[0] / tot if tot else 0:.1f}%)").rjust(22)
                        J[f"{ch}|{win}|pair{'Q' if qcd else ''}|{pr}|{c}"] = t
                    P(row)
            # origin of every F / U muon, split by whether that muon is T or L
            bm = base & bkg_mask(d, False)
            P("-- origin of nonprompt/undetermined muons (bkg noQCD), sumw by origin, muon T vs L:")
            for c in L.CATS:
                mc = bm & (d["cat"] == c)
                acc = collections.defaultdict(float)
                for k in (1, 2):
                    o = d[f"mu{k}_genOrigin"][mc]
                    t = d[f"mu{k}_tkRelIso"][mc] < L.TIGHT_ISO
                    w = d["weight"][mc]
                    for code in (0, 3, 4, 5, 6, 7, 8):
                        for tt in (True, False):
                            s = w[(o == code) & (t == tt)].sum()
                            if s != 0:
                                acc[(code, "T" if tt else "L")] += s
                J[f"{ch}|{win}|origin|{c}"] = {f"{L.ORIGIN_NAMES[k[0]]}|{k[1]}": v for k, v in acc.items()}
                P(f"   iso-{c}: " + ", ".join(f"{L.ORIGIN_NAMES[k[0]]}({k[1]})={v:.2f}"
                                          for k, v in sorted(acc.items(), key=lambda x: -abs(x[1]))))
            # unmatched: how many NanoAOD-unmatched muons get recovered by dR
            for k in (1, 2):
                m0 = bm & (d[f"mu{k}_genPartFlav"] == 0)
                if m0.any():
                    rec = collections.Counter(zip(d[f"mu{k}_genMatchType"][m0].tolist(), d[f"mu{k}_genOrigin"][m0].tolist()))
                    P(f"   mu{k} genPartFlav==0: {m0.sum()} raw; (matchType, origin) counts: {dict(rec.most_common(8))}")
            # signals
            P("-- signal yields and raw S/B (B = bkg noQCD; B+Q with QCD):")
            for s in L.SIGNALS6:
                sm = base & (d["proc"] == "SIG_" + s)
                row = s.ljust(16)
                for c in L.CATS:
                    S = L.ws(d["weight"][sm & (d["cat"] == c)])
                    B = d["weight"][base & bkg_mask(d, False) & (d["cat"] == c)].sum()
                    BQ = d["weight"][base & bkg_mask(d, True) & (d["cat"] == c)].sum()
                    row += f"  {c}: {S[0]:.3f}±{np.sqrt(S[1]):.3f} S/B {S[0] / B if B else np.nan:.3f} S/(B+Q) {S[0] / BQ if BQ else np.nan:.3f};"
                    J[f"{ch}|{win}|SIG_{s}|{c}"] = S
                P(row)
    open(txt, "w").write("\n".join(lines) + "\n")
    dumpj(J, js)
    print("\n".join(lines))


# ------------------------------------------------------------------ coverage
def coverage(d, store):
    txt, js = out_paths("04a_coverage")
    lines, J = [], {}
    P = lines.append
    fine = np.array([53, 60, 70, 80, 100, 120, 150, 200, 300, 500, 1000, 4000], float)
    P("# pT and |eta| of FO muons in SS baseline, bkg noQCD, by truth; fractions of sumw per pT bin")
    P("pT bins: " + " ".join(f"{fine[i]:.0f}-{fine[i + 1]:.0f}" for i in range(len(fine) - 1)))
    for win in ("Low", "High"):
        base = L.sel(d, "SS", win) & bkg_mask(d, False)
        for tr in ("F", "P", "U"):
            for tl in ("T", "L"):
                pts, etas, ws = [], [], []
                for k in (1, 2):
                    m = base & (d[f"t{k}"] == tr) & ((d[f"mu{k}_tkRelIso"] < L.TIGHT_ISO) == (tl == "T"))
                    pts.append(d[f"mu{k}_pt"][m]); etas.append(np.abs(d[f"mu{k}_eta"][m])); ws.append(d["weight"][m])
                pt, eta, w = np.concatenate(pts), np.concatenate(etas), np.concatenate(ws)
                h, _ = np.histogram(pt, fine, weights=w)
                n, _ = np.histogram(pt, fine)
                he, _ = np.histogram(eta, [0, 0.9, 1.2, 2.1, 2.4], weights=w)
                tot = w.sum()
                J[f"{win}|{tr}|{tl}"] = {"pt_sumw": h.tolist(), "pt_raw": n.tolist(), "eta_sumw": he.tolist(), "tot": tot}
                q = np.quantile(pt, [0.5, 0.9, 0.99]) if len(pt) else [np.nan] * 3
                P(f"{win:4s} {tr}{tl}: sumw {tot:8.2f} raw {len(pt):6d} | pT median/90%/99% {q[0]:.0f}/{q[1]:.0f}/{q[2]:.0f} | "
                  + " ".join(f"{x / tot if tot else 0:.3f}" for x in h) + f" | raw per bin {n.tolist()}"
                  + f" | |eta| [0,.9,1.2,2.1,2.4] {' '.join(f'{x / tot if tot else 0:.2f}' for x in he)}")
    J["fine_edges"] = fine.tolist()
    open(txt, "w").write("\n".join(lines) + "\n")
    dumpj(J, js)
    print("\n".join(lines))


# ------------------------------------------------------------------ step 4 maps
def build_map(d, m, truth_code, origin_filter=None, pt_edges=PT_EDGES, eta_edges=ETA_EDGES):
    rm = L.RateMap(pt_edges, eta_edges)
    for k in (1, 2):
        mk = m & (d[f"t{k}"] == truth_code)
        if origin_filter is not None:
            mk &= np.isin(d[f"mu{k}_genOrigin"], origin_filter)
        rm.fill(d[f"mu{k}_pt"][mk], d[f"mu{k}_eta"][mk], d[f"mu{k}_tkRelIso"][mk] < L.TIGHT_ISO, d["weight"][mk])
    return rm


def maps(d):
    b = bkg_mask(d, False)
    bq = bkg_mask(d, True)
    lowSS = L.sel(d, "SS", "Low")
    highSS = L.sel(d, "SS", "High")
    lowAll = L.sel(d, "SS", "Low") | L.sel(d, "OS", "Low")
    return {
        "F_lowSS": build_map(d, lowSS & b, "F"),
        "F_lowSS_QCD": build_map(d, lowSS & bq, "F"),
        "F_lowSSOS": build_map(d, lowAll & b, "F"),
        "F_highSS": build_map(d, highSS & b, "F"),
        "F_lowSS_bOrigin": build_map(d, lowSS & b, "F", origin_filter=[3, 4]),
        "F_lowSS_TTLJ": build_map(d, lowSS & (d["proc"] == "TTLJ"), "F"),
        "F_lowSS_ptsplit": build_map(d, lowSS & b, "F", pt_edges=[53, 60, 80, 120, 200, 300, 4000]),
        "F_highSS_ptsplit": build_map(d, highSS & b, "F", pt_edges=[53, 60, 80, 120, 200, 300, 4000]),
        "P_lowSS": build_map(d, lowSS & b, "P"),
        "P_highSS": build_map(d, highSS & b, "P"),
    }


def fakerate(d, store):
    txt, js = out_paths("04b_fakerate")
    M = maps(d)
    store["maps"] = M
    lines, J = [], {}
    for k, m in M.items():
        lines.append(m.table(k))
        lines.append("")
        J[k] = {"r": np.nan_to_num(m.r, nan=-1).tolist(), "err": np.nan_to_num(m.err, nan=-1).tolist(),
                "nT": m.nT.tolist(), "nL": m.nL.tolist(), "valid": m.valid().tolist(),
                "pt": m.pt.tolist(), "eta": m.eta.tolist()}
    open(txt, "w").write("\n".join(lines) + "\n")
    dumpj(J, js)
    print("\n".join(lines))


# ------------------------------------------------------------------ closure
def hist(x, w, edges):
    x = np.minimum(x, edges[-1] - 1e-3)
    h, _ = np.histogram(x, edges, weights=w)
    h2, _ = np.histogram(x, edges, weights=np.asarray(w, float) ** 2)
    return h, h2


def closure(d, store):
    txt, js = out_paths("04c_closure")
    M = store.get("maps") or maps(d)
    fmap, pmap = M["F_lowSS"], M["P_lowSS"]
    lines, J = [], {}
    P = lines.append
    P("# closure: F map from SS Low (bkg noQCD, truth-nonprompt muons) applied to SS High.")
    P("# target = iso-TT with >=1 truth-F muon. U-only iso-TT (no F, >=1 U) reported separately.")
    for app_key, app_win, edges in (("High", "High", HIGH_EDGES), ("HighMerged", "High", HIGH_MERGED),
                                    ("Low", "Low", LOW_EDGES)):
        for qcd in (False, True):
            reg = L.sel(d, "SS", app_win) & bkg_mask(d, qcd)
            hasF = (d["t1"] == "F") | (d["t2"] == "F")
            hasU = ((d["t1"] == "U") | (d["t2"] == "U")) & ~hasF
            pp = (d["t1"] == "P") & (d["t2"] == "P")
            tgt = reg & (d["cat"] == "TT") & hasF
            tgtU = reg & (d["cat"] == "TT") & hasU
            ar = reg & np.isin(d["cat"], ["TL", "LT", "LL"])
            T_h, T_h2 = hist(d["mlljj"][tgt], d["weight"][tgt], edges)
            res = {"edges": edges.tolist(), "target": T_h.tolist(), "target_err2": T_h2.tolist(),
                   "targetU": hist(d["mlljj"][tgtU], d["weight"][tgtU], edges)[0].tolist()}
            variants = {
                "FF, AR truth-F only": ar & hasF,
                "FF, AR all - PP (prompt-subtracted)": ar,
                "FF, one-fake only (no LL)": ar & (d["cat"] != "LL"),
            }
            for name, m in variants.items():
                w = L.ff_prediction(d, m, fmap)
                if name.startswith("FF, AR all"):
                    mpp = m & pp
                    w_pp = L.ff_prediction(d, mpp, fmap)
                    h_all, h2_all = hist(d["mlljj"][m], w, edges)
                    h_pp, h2_pp = hist(d["mlljj"][mpp], w_pp, edges)
                    h, h2 = h_all - h_pp, h2_all + h2_pp  # conservative (not independent)
                    res["pp_subtracted"] = h_pp.tolist()
                else:
                    h, h2 = hist(d["mlljj"][m], w, edges)
                # map stat via toys
                toys = []
                for r in fmap.toys(NTOY, RNG):
                    wt = L.ff_prediction(d, m, fmap, r=r)
                    ht, _ = hist(d["mlljj"][m], np.nan_to_num(wt), edges)
                    if name.startswith("FF, AR all"):
                        wpt = L.ff_prediction(d, m & pp, fmap, r=r)
                        ht = ht - hist(d["mlljj"][m & pp], np.nan_to_num(wpt), edges)[0]
                    toys.append(ht)
                toys = np.array(toys)
                res[name] = {"pred": h.tolist(), "pred_err2_mc": h2.tolist(), "pred_err_map": spread(toys).tolist(),
                             "tot": float(h.sum()), "tot_err_mc": float(np.sqrt(h2.sum())),
                             "tot_err_map": float(spread(toys.sum(1))), "nan_events": int(np.isnan(w).sum())}
            # full matrix method (prompt efficiency from SS Low prompt muons)
            m = reg & np.isin(d["cat"], ["TT", "TL", "LT", "LL"])
            wmm = L.ff_prediction(d, m, fmap, prompt_eff=pmap)
            h, h2 = hist(d["mlljj"][m], np.nan_to_num(wmm), edges)
            res["full matrix (eps from P_lowSS), all SS events"] = {
                "pred": h.tolist(), "pred_err2_mc": h2.tolist(), "tot": float(h.sum()),
                "tot_err_mc": float(np.sqrt(h2.sum())), "nan_events": int(np.isnan(wmm).sum())}
            key = f"{app_key}|{'QCD' if qcd else 'noQCD'}"
            J[key] = res
            P(f"\n## apply to SS {app_win} [{app_key}] ({'bkg+QCD' if qcd else 'bkg noQCD'}); bins {edges.tolist()}")
            P(f"target nonprompt iso-TT: {T_h.sum():.3f} ± {np.sqrt(T_h2.sum()):.3f}   per bin {np.round(T_h, 3).tolist()}")
            tFU = T_h.sum() + np.sum(res['targetU'])
            P(f"U-only iso-TT (not in target): {np.sum(res['targetU']):.3f}   -> F+U target {tFU:.3f}"
              " (the prompt-subtracted estimator predicts F+U: U fail muons are in its AR)")
            for name in list(variants) + ["full matrix (eps from P_lowSS), all SS events"]:
                r = res[name]
                emap = r.get("tot_err_map", float("nan"))
                P(f"{name:48s}: {r['tot']:.3f} ± {r['tot_err_mc']:.3f}(MC) ± {emap:.3f}(map)  "
                  f"pred/target(F) {r['tot'] / T_h.sum() if T_h.sum() else np.nan:.3f}  pred/target(F+U) {r['tot'] / tFU if tFU else np.nan:.3f}"
                  f"   per bin {np.round(r['pred'], 3).tolist()}")
                if T_h.sum():
                    err = np.sqrt(np.array(r["pred_err2_mc"]) + T_h2 + np.array(r.get("pred_err_map", np.zeros(len(T_h)))) ** 2)
                    with np.errstate(divide="ignore", invalid="ignore"):
                        pull = (np.array(r["pred"]) - T_h) / err
                    P(f"{'':48s}  per-bin pull {np.round(pull, 2).tolist()}  chi2/ndf {np.nansum(pull ** 2):.2f}/{np.isfinite(pull).sum()}")
    open(txt, "w").write("\n".join(lines) + "\n")
    dumpj(J, js)
    print("\n".join(lines))


# ------------------------------------------------------------------ step 5 signal leakage
def signal(d, store):
    txt, js = out_paths("05_signal_leakage")
    M = store.get("maps") or maps(d)
    fmap = M["F_lowSS"]
    lines, J = [], {}
    P = lines.append
    edges = L.CARD_EDGES
    P("# SS Full, card mlljj bins. WS = sum(signal TL+LT) w F_fail - sum(signal LL) w F1 F2 with the SS-Low MC map.")
    P("# B_TT = bkg noQCD iso-TT; B_np_TT = truth-nonprompt part of it. Errors: signal MC stat, map stat (toys).")
    reg = L.sel(d, "SS", "Full")
    bm = reg & bkg_mask(d, False)
    hasF = (d["t1"] == "F") | (d["t2"] == "F")
    B_TT, _ = hist(d["mlljj"][bm & (d["cat"] == "TT")], d["weight"][bm & (d["cat"] == "TT")], edges)
    B_np, _ = hist(d["mlljj"][bm & (d["cat"] == "TT") & hasF], d["weight"][bm & (d["cat"] == "TT") & hasF], edges)
    wb = L.ff_prediction(d, bm & np.isin(d["cat"], ["TL", "LT", "LL"]), fmap)
    B_pred, _ = hist(d["mlljj"][bm & np.isin(d["cat"], ["TL", "LT", "LL"])], wb, edges)
    J["edges"] = edges.tolist(); J["B_TT"] = B_TT.tolist(); J["B_np_TT"] = B_np.tolist(); J["B_pred_FF"] = B_pred.tolist()
    toysR = fmap.toys(NTOY, RNG)
    for s in L.SIGNALS6:
        sm = reg & (d["proc"] == "SIG_" + s)
        H = {c: hist(d["mlljj"][sm & (d["cat"] == c)], d["weight"][sm & (d["cat"] == c)], edges) for c in L.CATS}
        ma = sm & np.isin(d["cat"], ["TL", "LT", "LL"])
        w = L.ff_prediction(d, ma, fmap)
        WS, WS2 = hist(d["mlljj"][ma], w, edges)
        toys = np.array([hist(d["mlljj"][ma], np.nan_to_num(L.ff_prediction(d, ma, fmap, r=r)), edges)[0] for r in toysR])
        eWS_map = spread(toys)
        J[s] = {c: [H[c][0].tolist(), H[c][1].tolist()] for c in L.CATS}
        J[s]["WS"] = WS.tolist(); J[s]["WS_err_mc"] = np.sqrt(WS2).tolist(); J[s]["WS_err_map"] = eWS_map.tolist()
        P(f"\n## {s}   total: S_TT {H['TT'][0].sum():.3f} S_TL {H['TL'][0].sum():.3f} S_LT {H['LT'][0].sum():.3f} "
          f"S_LL {H['LL'][0].sum():.4f}   WS {WS.sum():.4f} ± {np.sqrt(WS2.sum()):.4f}(MC) ± {spread(toys.sum(1)):.4f}(map)")
        P("bin".ljust(12) + "S_TT".rjust(10) + "S_TL".rjust(9) + "S_LT".rjust(9) + "S_LL".rjust(9) + "B_TT".rjust(9)
          + "S/B".rjust(9) + "fail/TT".rjust(9) + "WS".rjust(10) + "±MC".rjust(8) + "±map".rjust(8)
          + "WS/S_TT".rjust(9) + "WS/Bnp".rjust(9))
        for i in range(len(edges) - 1):
            stt, stl, slt, sll = (H[c][0][i] for c in L.CATS)
            fail = stl + slt + sll
            with np.errstate(divide="ignore", invalid="ignore"):
                P(f"{edges[i]:.0f}-{edges[i + 1]:.0f}".ljust(12) + f"{stt:10.3f}{stl:9.3f}{slt:9.3f}{sll:9.4f}{B_TT[i]:9.3f}"
                  f"{stt / B_TT[i]:9.2f}{fail / stt:9.3f}{WS[i]:10.4f}{np.sqrt(WS2[i]):8.4f}{eWS_map[i]:8.4f}"
                  f"{WS[i] / stt:9.4f}{WS[i] / B_np[i]:9.3f}")
    open(txt, "w").write("\n".join(lines) + "\n")
    dumpj(J, js)
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["composition", "coverage", "fakerate", "closure", "signal", "all"])
    ap.add_argument("--skim", default=L.SKIM)
    ap.add_argument("--wjets", default="HT", choices=["HT", "MLNu", "both"])
    a = ap.parse_args()
    d, _ = L.load(a.skim, wjets=a.wjets)
    print(f"[fo_analysis] {len(d['weight'])} FO events, W+jets set = {a.wjets}", file=sys.stderr)
    store = {}
    steps = ["composition", "coverage", "fakerate", "closure", "signal"] if a.step == "all" else [a.step]
    for s in steps:
        globals()[s](d, store)


if __name__ == "__main__":
    main()
