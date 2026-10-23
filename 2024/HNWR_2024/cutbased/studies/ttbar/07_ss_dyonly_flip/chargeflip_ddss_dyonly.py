#!/usr/bin/env python3
"""Data-driven EE same-sign templates for the cbv15 cards (charge-flip method, docs/chargeflip_method_ee2024.md step 6
applied to the SR): SS flip prediction = OS DATA events x w, w = [P1(1-P2)+P2(1-P1)] / [(1-P1)(1-P2)+P1P2] with
P = P_final(pT, |eta_SC|, tc) = P_MC,gen x SF(|eta|, tc) from the chargeflip_method JSON. Non-flip SS (WZ/ZZ, nonprompt,
DY gen-SS/unmatched, TT without a flipped electron) from MC (HNWR_ChargeFlip RFlav tree: DY corrections + lepton SFs).

Output ROOT file with directories rEESR_SS (resolved EE SR: m_ee>400, m_lljj>800) and rDYEECR_SS (60<m_ee<150, m_lljj>800):
  Flip, Flip_FlipP_e<i>_tc<k>_2024Up/Down (SF fit error per (|eta|,tc) category, 12 independent nuisances),
  Flip_FlipPgenStat_2024Up/Down (P_MC,gen MC-stat, all bins coherent), DYJets / TT / Nonprompt / Others (non-flip SS MC),
  data_obs (DY CR: SS data; SR: sum of the prediction, i.e. blinded).
    chargeflip_ddss.py --dumps <dir with tree_*.npz (RFlav)> --json <chargeflip_method json> --out <root file> [--tc2-only] [--sr-edges 800,...,8000]
  --tc2-only (2026-09-14): both electrons tightCharge == 2 in every component (OS data for the flip prediction, non-flip SS MC,
             SS data in the DY CR); use with the tc=2-only method json (tc_order [2]). Without it a tc2-only json would give
             tc != 2 electrons the tc2 probability.
  --sr-edges : comma list replacing the rEESR_SS binning.
  --sf2      : AN-style json: 2-region barrel/endcap SF even if the json also carries SF3 (three regions).
  --pt-shift : (2026-09-30) AN step 1 energy shift in the template: every OS event gives two entries, entry i = "electron i
               flipped", weight SF_i P_i / (1 - P_i) (as chargeflip_ptshift.predict_ss), with only electron i's momentum scaled
               by f_i. m_lljj is filled at m_lljj x sqrt(f_i): exact for m_ll, an upper bound of the shift for m_lljj (the jet
               4-vectors needed for the exact value are not in the dumps; |1 - f| <= 0.009).
  --flip-groups DY,TT : (2026-09-30) with --dy-only, the groups whose flips are taken from the flip term (default DY):
               the OS MC of the other groups is subtracted, and these groups enter the SS MC with their non-flip events only.
  --os-mc    : (2026-09-30) treat the OS MC (all backgrounds, MC weight) as if it were the OS data of the region and apply the
               same method to it -- blinded SR without opening its OS data. With --dy-only the flip term becomes
               (OS MC - OS non-DY MC) x w = OS DY MC x w. SS data_obs of the DY CR stays the real data.
"""
import argparse, glob, json, os
import numpy as np
import ROOT

ETA = np.array([0.0, 0.8, 1.479, 2.0, 2.5]); PTB = np.array([53., 70., 100., 150., 250., 400., 1000.])
EDGES = {"rEESR_SS": [800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 3561, 4643, 5533, 8000],
         "rDYEECR_SS": [800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 8000]}
SEL = {"rEESR_SS": lambda d: (d["passResolved"] > 0) & (d["m_l1l2"] > 400) & (d["m_lljj"] > 800),
       "rDYEECR_SS": lambda d: d["isDYCR"] > 0}
GROUP = {"DY": "DYJets", "TT": "TT", "Others": "Others", "Nonprompt": "Nonprompt"}


def group_of(b):
    b = b.replace("tree_Skim_HNWR_", "")
    if b.startswith("DYto2L"): return "DY"
    if b.startswith(("EGamma", "Muon")): return "DATA"
    # Signal is NOT background. The final return is a catch-all, so without this the WR samples land in
    # Nonprompt: harmless in the DY CR (they do not reach it) but they own the SR m_lljj tail. "SIG" is
    # not a key of GROUP, so every GROUP.get(g, "x") consumer drops it (config.SIGNAL_GLOBS = WRtoN*).
    if b.startswith("WRtoN"): return "SIG"
    if b.startswith(("TTto2L2Nu", "TWminusto2L2Nu", "TbarWplusto2L2Nu")): return "TT"
    if b.startswith(("WWto", "WZto", "ZZto", "TTLL", "TTLNu")): return "Others"
    return "Nonprompt"


def load(dump_dir, keys=None):
    # Dumps from different productions can carry different branches (e.g. j1/j2 only exist from the RFlav v3 dump on).
    # A missing key must be filled per file, otherwise the concatenated arrays have different lengths and every
    # selection silently misaligns -- so collect the union of the keys first and pad with -999.
    # keys: optional subset of columns to load (memory; the 2026-09-17 boosted dumps are 6 GB with 91 columns).
    paths = sorted(glob.glob(os.path.join(dump_dir, "tree_*.npz")))
    allkeys = sorted(set().union(*[set(np.load(p).files) for p in paths])) if paths else []
    keys = allkeys if keys is None else sorted(set(keys) | {"channel", "weight", "isSS"})
    acc = {}
    for p in paths:
        g = group_of(os.path.basename(p)); z = np.load(p); m = z["channel"] == 11
        if m.sum() == 0: continue
        have = set(z.files)
        for k in keys:
            acc.setdefault(k, []).append(z[k][m] if k in have else np.full(int(m.sum()), -999.0, dtype="float32"))
        acc.setdefault("grp", []).append(np.full(m.sum(), g))
    d = {k: np.concatenate(v) for k, v in acc.items()}
    n = len(d["channel"])
    assert all(len(v) == n for v in d.values()), "ragged dump columns"
    d["weight"] = np.where(d["grp"] == "DATA", 1.0, d["weight"]).astype("float64")
    for i in (1, 2):
        if f"l{i}_genChargeIdx" in d:   # NanoAOD genPartIdx charge (photon match -> unmatched); see chargeflip_method.py
            g = d[f"l{i}_genChargeIdx"]; d[f"l{i}_genCharge"] = np.where(g == 0, -999.0, g)
        d[f"l{i}_ieta"] = np.clip(np.searchsorted(ETA, np.abs(d[f"l{i}_scEta"]), side="right") - 1, 0, 3)
        d[f"l{i}_ipt"] = np.clip(np.searchsorted(PTB, d[f"l{i}_pt"], side="right") - 1, 0, 5)
        d[f"l{i}_flip"] = (d[f"l{i}_genCharge"] > -900) & (d[f"l{i}_charge"] != d[f"l{i}_genCharge"])
    d["ss"] = d["isSS"] > 0
    return d


def flip_weight(P1, P2):
    return (P1 * (1 - P2) + P2 * (1 - P1)) / ((1 - P1) * (1 - P2) + P1 * P2)


# ---- AN-style json (chargeflip_ptshift.py, 2026-09-11): P[eta region][pT bin] x SF(barrel | endcap) ------------------
def new_format(J):
    return "rate_regions" in J


def new_weights(J, d, sf2=False):
    """Nominal flip weight per event and the systematic variations for the chargeflip_ptshift json.
    SF regions: J["sf"]["SF3"] (per-lepton LSQ regions, e.g. inner_barrel / outer_barrel / endcap) when present,
    else the barrel / endcap pair of J["sf"]["SF"]; sf2=True forces the 2-region pair (2026-09-17: the RooFit-fitted
    _sf3roofit.json carries both). Returns (w, [(name, w_up, w_down), ...]). Crack electrons: P = 0."""
    regs = list(J["rate_regions"].items()); P = np.nan_to_num(np.array(J["P"])); Pe = np.nan_to_num(np.array(J["P_err"]))
    pt_edges = np.array(J["pt_edges"]); npt = len(pt_edges) - 1
    if "SF3" in J["sf"] and not sf2:
        sfreg = {n: tuple(v) for n, v in J["sf"]["SF3"]["regions"].items()}; SFv = dict(J["sf"]["SF3"]["SF"]); SFe = dict(J["sf"]["SF3"]["SF_err"])
    else:
        sfreg = {"barrel": (0.0, 1.4442), "endcap": (1.566, 2.5)}
        SFv = {"barrel": J["sf"]["SF"]["barrel"], "endcap": J["sf"]["SF"]["endcap"]}
        SFe = {"barrel": J["sf"]["SF"]["barrel_err"] or 0.0, "endcap": J["sf"]["SF"]["endcap_err"] or 0.0}
    names = list(sfreg)
    # SF region of each rate region (by its centre)
    reg_sf = np.array([next((k for k, n in enumerate(names) if sfreg[n][0] <= 0.5 * (lo + hi) < sfreg[n][1]), -1) for _, (lo, hi) in regs])
    idx = {}
    for i in (1, 2):
        ae = np.abs(d[f"l{i}_scEta"]); ie = np.full(len(ae), -1)
        for k, (_, (lo, hi)) in enumerate(regs): ie[(ae >= lo) & (ae < hi)] = k
        ip = np.clip(np.searchsorted(pt_edges, d[f"l{i}_pt"], side="right") - 1, 0, npt - 1)
        idx[i] = (ie, ip)
    def wof(Pm, sfvec):
        out = []
        for i in (1, 2):
            ie, ip = idx[i]; ok = ie >= 0
            p = np.zeros(len(ie)); p[ok] = Pm[ie[ok], ip[ok]] * sfvec[reg_sf[ie[ok]]]
            out.append(p)
        return flip_weight(out[0], out[1])
    sf0 = np.array([SFv[n] for n in names])
    w = wof(P, sf0)
    var = []
    for k, n in enumerate(names):
        up = sf0.copy(); up[k] += SFe[n]; dn = sf0.copy(); dn[k] = max(dn[k] - SFe[n], 0.0)
        var.append((f"FlipSF_{n}", wof(P, up), wof(P, dn)))
    var.append(("FlipPstat", wof(np.clip(P + Pe, 0, None), sf0), wof(np.clip(P - Pe, 0, None), sf0)))
    return w, var


def new_entries(J, d, sf2=False):
    """--pt-shift: per-electron entries. Returns {name: [(w1, f1), (w2, f2)]} for the nominal ("") and every variation
    of new_weights (same names, Up/Down), with w_i = SF_i P_i / (1 - P_i) and f_i the energy-shift factor of electron i."""
    regs = list(J["rate_regions"].items()); P = np.nan_to_num(np.array(J["P"])); Pe = np.nan_to_num(np.array(J["P_err"]))
    pt_edges = np.array(J["pt_edges"]); npt = len(pt_edges) - 1
    if "SF3" in J["sf"] and not sf2:
        sfreg = {n: tuple(v) for n, v in J["sf"]["SF3"]["regions"].items()}; SFv = dict(J["sf"]["SF3"]["SF"]); SFe = dict(J["sf"]["SF3"]["SF_err"])
    else:
        sfreg = {"barrel": (0.0, 1.4442), "endcap": (1.566, 2.5)}
        SFv = {"barrel": J["sf"]["SF"]["barrel"], "endcap": J["sf"]["SF"]["endcap"]}
        SFe = {"barrel": J["sf"]["SF"]["barrel_err"] or 0.0, "endcap": J["sf"]["SF"]["endcap_err"] or 0.0}
    names = list(sfreg)
    reg_sf = np.array([next((k for k, n in enumerate(names) if sfreg[n][0] <= 0.5 * (lo + hi) < sfreg[n][1]), -1) for _, (lo, hi) in regs])
    shreg = J["shift_regions"]; shpt = [[float(x) for x in r["pt"].split("-")] for r in J["shift"][list(shreg)[0]]]
    sh_edges = np.array([lo for lo, _ in shpt] + [shpt[-1][1]])
    ftab = np.array([[r["f"] for r in J["shift"][n]] for n in shreg])
    idx, fl = {}, {}
    for i in (1, 2):
        ae = np.abs(d[f"l{i}_scEta"]); ie = np.full(len(ae), -1)
        for k, (_, (lo, hi)) in enumerate(regs): ie[(ae >= lo) & (ae < hi)] = k
        ip = np.clip(np.searchsorted(pt_edges, d[f"l{i}_pt"], side="right") - 1, 0, npt - 1)
        idx[i] = (ie, ip)
        ir = np.full(len(ae), -1)
        for k, (lo, hi) in enumerate(shreg.values()): ir[(ae >= lo) & (ae < hi)] = k
        jp = np.clip(np.searchsorted(sh_edges, d[f"l{i}_pt"], side="right") - 1, 0, len(sh_edges) - 2)
        f = np.ones(len(ae)); ok = ir >= 0; f[ok] = ftab[ir[ok], jp[ok]]; fl[i] = f
    def ent(Pm, sfvec):
        out = []
        for i in (1, 2):
            ie, ip = idx[i]; ok = ie >= 0; w = np.zeros(len(ie))
            p = Pm[ie[ok], ip[ok]]; w[ok] = sfvec[reg_sf[ie[ok]]] * p / np.clip(1 - p, 1e-9, None)
            out.append((w, fl[i]))
        return out
    sf0 = np.array([SFv[n] for n in names])
    res = {"": ent(P, sf0)}
    for k, n in enumerate(names):
        up = sf0.copy(); up[k] += SFe[n]; dn = sf0.copy(); dn[k] = max(dn[k] - SFe[n], 0.0)
        res[f"FlipSF_{n}"] = (ent(P, up), ent(P, dn))
    res["FlipPstat"] = (ent(np.clip(P + Pe, 0, None), sf0), ent(np.clip(P - Pe, 0, None), sf0))
    return res


def flip_sf_weight(J, d, sf2=False):
    """Per-event correction for MC events whose electron charge is gen-level flipped.

    The MC charge-flip rate is low: the method measures SF = data/MC flip rate ~1.43-1.45 per lepton
    region and folds it into the data-driven prediction. MC gen-flipped events carry no such factor, so
    taking TT/Others from raw SS MC (--dy-only) undercounts their flip component by exactly that SF.
    Returns 1.0 everywhere except gen-flipped MC events, which get SF(region of the flipped electron).
    """
    import numpy as np
    if "SF3" in J["sf"] and not sf2:
        sfreg = {n: tuple(v) for n, v in J["sf"]["SF3"]["regions"].items()}; SFv = dict(J["sf"]["SF3"]["SF"])
    else:
        sfreg = {"barrel": (0.0, 1.4442), "endcap": (1.566, 2.5)}
        SFv = {"barrel": J["sf"]["SF"]["barrel"], "endcap": J["sf"]["SF"]["endcap"]}
    names = list(sfreg)
    out = np.ones(len(d["channel"]))
    for i in (1, 2):
        ae = np.abs(d[f"l{i}_scEta"]); fl = d[f"l{i}_flip"].astype(bool)
        for n in names:
            lo, hi = sfreg[n]
            m = fl & (ae >= lo) & (ae < hi)
            out[m] *= SFv[n]
    return out


def th1(name, edges, vals, w2):
    h = ROOT.TH1D(name, name, len(edges) - 1, np.array(edges, dtype="float64")); h.Sumw2()
    for i, (v, e) in enumerate(zip(vals, w2)):
        h.SetBinContent(i + 1, float(v)); h.SetBinError(i + 1, float(np.sqrt(e)))
    return h


def fill(x, w, edges):
    v, _ = np.histogram(x, bins=edges, weights=w); e, _ = np.histogram(x, bins=edges, weights=w * w)
    return v, e


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dumps", required=True); ap.add_argument("--json", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--tc2-only", action="store_true", help="both electrons tightCharge == 2 in all components")
    ap.add_argument("--sr-edges", default=None, help="comma list of rEESR_SS bin edges")
    ap.add_argument("--sf2", action="store_true", help="AN json: use the 2-region (barrel/endcap) SF even when SF3 is present")
    ap.add_argument("--no-flip-sf", action="store_true",
                    help="--dy-only: do NOT apply the measured flip SF to gen-flipped MC (for comparison only)")
    ap.add_argument("--flip-groups", default="DY", help="--dy-only: comma list of groups predicted by the flip term (DY, TT)")
    ap.add_argument("--pt-shift", action="store_true", help="two entries per OS event with the energy shift of the flipped electron")
    ap.add_argument("--os-mc", action="store_true",
                    help="use the OS MC (all backgrounds, MC weights) in place of the OS data in the flip term")
    ap.add_argument("--dy-only", action="store_true",
                    help="charge-misID predicts the DY flip only. The OS-data flip prediction has the non-DY flip "
                         "component subtracted with MC (same per-event weight), and TT/Nonprompt/Others are taken "
                         "from the FULL SS MC (flip + non-flip) instead of non-flip only -- so the ttbar part of the "
                         "SS region is carried by the MC template that R_TT_Resolved_2024 scales, i.e. it is "
                         "normalised by the e-mu flavour CR rather than by the flip weight.")
    a = ap.parse_args()
    if a.sr_edges: EDGES["rEESR_SS"] = [float(x) for x in a.sr_edges.split(",")]
    FG = [g.strip() for g in a.flip_groups.split(",")]
    assert all(g in GROUP for g in FG), FG
    J = json.load(open(a.json)); NEW = new_format(J)
    d = load(a.dumps)
    if NEW:
        w_all, var_all = new_weights(J, d, sf2=a.sf2)
        if a.pt_shift:
            E = new_entries(J, d, sf2=a.sf2)
            var_all = [(n, E[n][0], E[n][1]) for n in E if n]; w_all = E[""]
    else:
        tcs = J["tc_order"]
        Pfin = np.nan_to_num(np.array(J["step5"]["P_final"]))                  # [ipt][ieta][itc]
        Pgen = np.nan_to_num(np.array(J["step1"]["P_gen"])); Egen = np.nan_to_num(np.array(J["step1"]["err"]))
        SF = np.array(J["step4"]["SF"]); eSF = np.array(J["step4"]["err"])      # [ieta][itc]
        itc = {i: np.array([tcs.index(int(t)) if int(t) in tcs else 0 for t in d[f"l{i}_tightCharge"]]) for i in (1, 2)}
        if a.tc2_only and tcs != [2]: raise SystemExit("--tc2-only needs the tc=2-only method json (tc_order [2])")
    sfw = flip_sf_weight(J, d, sf2=a.sf2) if (a.dy_only and NEW and not a.no_flip_sf) else np.ones(len(d["channel"]))
    isdata = d["grp"] == "DATA"
    tcmask = ((d["l1_tightCharge"] == 2) & (d["l2_tightCharge"] == 2)) if a.tc2_only else np.ones(len(isdata), bool)
    fo = ROOT.TFile.Open(a.out, "RECREATE")
    summary = {}
    for reg, edges in EDGES.items():
        sel = SEL[reg](d) & tcmask; od = fo.mkdir(reg); od.cd()
        if a.os_mc:     # OS MC as pseudo-data (signal excluded), carrying its MC weight
            os_ = sel & ~isdata & ~d["ss"] & (d["grp"] != "SIG"); osw = d["weight"][os_]
        else:
            os_ = sel & isdata & ~d["ss"]; osw = np.ones(int(os_.sum()))
        x = d["m_lljj"][os_]
        # --dy-only: OS MC of every non-DY background, to be subtracted from the OS-data flip prediction.
        submc = sel & ~isdata & ~d["ss"] & ~np.isin(d["grp"], FG + ["SIG"]) if a.dy_only else None
        xs = d["m_lljj"][submc] if a.dy_only else None
        wsub = d["weight"][submc] if a.dy_only else None
        if NEW:
            def fill_w(mask, base_w, warr):
                """weighted fill of m_lljj for the events in mask: one entry per event (w array) or, with --pt-shift,
                two entries per event (list of (w_i, f_i)), m_lljj x sqrt(f_i)."""
                if not a.pt_shift: return fill(d["m_lljj"][mask], warr[mask] * base_w, edges)
                vv = np.zeros(len(edges) - 1); ee = np.zeros(len(edges) - 1)
                for wi, fi in warr:
                    v1, e1 = fill(d["m_lljj"][mask] * np.sqrt(fi[mask]), wi[mask] * base_w, edges); vv += v1; ee += e1
                return vv, ee
            def flipfill(warr):
                v, e = fill_w(os_, osw, warr)
                if a.dy_only:
                    vs, es = fill_w(submc, wsub, warr)
                    v = np.clip(v - vs, 0.0, None); e = e + es      # subtraction: errors add in quadrature
                return v, e
            v, e = flipfill(w_all); od.WriteTObject(th1("Flip", edges, v, e), "Flip")
            summary[reg] = {"Flip": float(v.sum()), "Flip_raw_OS": int(os_.sum()), "OS_yield": float(osw.sum())}
            if a.dy_only:
                vs, _ = fill_w(submc, wsub, w_all)
                summary[reg]["Flip_nonDY_subtracted"] = float(vs.sum())
            for name, wu, wd in var_all:
                for tag, ww in (("Up", wu), ("Down", wd)):
                    v1, e1 = flipfill(ww); n = f"Flip_{name}_2024{tag}"; od.WriteTObject(th1(n, edges, v1, e1), n)
        else:
          def wvec(P):
            P1 = P[d["l1_ipt"][os_], d["l1_ieta"][os_], itc[1][os_]]; P2 = P[d["l2_ipt"][os_], d["l2_ieta"][os_], itc[2][os_]]
            return flip_weight(P1, P2)
          w0 = wvec(Pfin); v, e = fill(x, w0, edges); od.WriteTObject(th1("Flip", edges, v, e), "Flip")
          summary[reg] = {"Flip": float(v.sum()), "Flip_raw_OS": int(os_.sum())}
          # SF fit error per (|eta|, tc) category: scale P_final of that category by (1 +- eSF/SF)
          for j in range(4):
            for k, tc in enumerate(tcs):
                rel = eSF[j, k] / SF[j, k] if SF[j, k] > 0 else 0.0
                for tag, sgn in (("Up", 1), ("Down", -1)):
                    P = Pfin.copy(); P[:, j, k] *= max(1 + sgn * rel, 0.0)
                    v1, e1 = fill(x, wvec(P), edges); n = f"Flip_FlipP_e{j}_tc{tc}_2024{tag}"; od.WriteTObject(th1(n, edges, v1, e1), n)
          # P_MC,gen MC-stat, coherent over all bins
          for tag, sgn in (("Up", 1), ("Down", -1)):
            P = np.clip(Pgen + sgn * Egen, 0, None) * SF[None, :, :]
            v1, e1 = fill(x, wvec(P), edges); n = f"Flip_FlipPgenStat_2024{tag}"; od.WriteTObject(th1(n, edges, v1, e1), n)
        # SS from MC. Default: non-flip only (the flipped part lives in the data-driven Flip template).
        # --dy-only: only DY stays non-flip-only; every other background is taken in full (flip + non-flip),
        # because its flip component was just subtracted out of Flip above.
        nonflip = sel & ~isdata & d["ss"] & ~(d["l1_flip"] | d["l2_flip"])
        allss = sel & ~isdata & d["ss"]
        tot = v.copy(); tot_e = e.copy()
        for g, proc in GROUP.items():
            base = nonflip if (not a.dy_only or g in FG) else allss
            m = base & (d["grp"] == g); v1, e1 = fill(d["m_lljj"][m], d["weight"][m] * sfw[m], edges)
            od.WriteTObject(th1(proc, edges, v1, e1), proc); summary[reg][proc] = float(v1.sum()); tot += v1; tot_e += e1
        if reg == "rDYEECR_SS":
            m = sel & isdata & d["ss"]; v1, e1 = fill(d["m_lljj"][m], np.ones(m.sum()), edges)
            od.WriteTObject(th1("data_obs", edges, v1, e1), "data_obs"); summary[reg]["data_obs"] = float(v1.sum())
        else:   # blinded SR: data_obs = total prediction
            od.WriteTObject(th1("data_obs", edges, tot, tot_e), "data_obs"); summary[reg]["data_obs(pred)"] = float(tot.sum())
        summary[reg]["pred_total"] = float(tot.sum())
    fo.Close()
    print(json.dumps(summary, indent=1)); print("wrote", a.out)


if __name__ == "__main__":
    main()
