#!/usr/bin/env python3
"""Pre-BDT significance comparison from HNWR_BDT_presel NoSyst ntuples (2023).

Scenarios (resolved selection is identical in all three; ntuple-level split):
  (i)   old       : resolved + boosted[passMllSR]  (sublead present & mll>200)
  (ii)  merged    : resolved + boosted[all]        (no-loose, single category)
  (iii) split     : resolved + boosted-withlep[passMllSR] + boosted-nolep[mll=-999]
                    (proposed 3-category architecture; withlep == old boosted)

Observable: resolved -> mlljj, boosted -> ml1fatjet.
Window: [10%, 90%] quantiles of the SIGNAL observable per category.
Z = S/sqrt(B) in window; combined = quadrature sum over categories.
Weights: ntuple 'weight' (gen x lumi, no SF).

NOTE: resolved-loose expansion (sublead pT>20 + ID/iso) is NOT reproducible
from these ntuples (sublead stored at >53 tight); needs its own production.
"""

import numpy as np
import uproot

OUT_DIR = "/gv0/Users/achihwan/SKNanoOutput/HNWR_BDT_presel/NoSyst/2023"
HERE = __file__.rsplit("/", 1)[0]

DY = [f"DYMLL120HT{h}" for h in ["40to70","70to100","100to400","400to800","800to1500","1500to2500","2500"]] \
   + [f"DYMLL50to120HT{h}" for h in ["40to70","70to100","100to400","400to800","800to1500","1500to2500","2500"]]
GROUPS = {
    "DY": DY,
    "TT": ["TTLJ_powheg", "TTLL_powheg"],
    "WJets": ["WJets"],
    "ST": ["ST_sch_antitop_Lep","ST_sch_top_Lep","ST_tch_antitop","ST_tch_top",
           "ST_tW_antitop_Fullyhad","ST_tW_antitop_Lep","ST_tW_antitop_Semilep",
           "ST_tW_top_Fullyhad","ST_tW_top_Lep","ST_tW_top_Semilep"],
    "VV": ["WWto2L2Nu","WWto4Q","WWtoLNu2Q","WZto2L2Q","WZto3LNu","WZtoLNu2Q",
           "ZZto2L2Nu","ZZto2L2Q","ZZto2Nu2Q","ZZto4L"],
}
SIGNALS = ["WR2000N100EE", "WR2000N100MM"]

CATS = [  # (name, tree, observable)
    ("res_EE", "SR_EE_BDTTree_resolved", "mlljj"),
    ("res_MM", "SR_MM_BDTTree_resolved", "mlljj"),
    ("boo_EE", "SR_EE_BDTTree_boosted", "ml1fatjet"),
    ("boo_MM", "SR_MM_BDTTree_boosted", "ml1fatjet"),
]


def read(sample, tree, branches):
    """Read a tree whose name contains a literal '/' inside the Central dir."""
    try:
        f = uproot.open(f"{OUT_DIR}/Skim_20002_{sample}.root")
    except Exception:
        return None
    items = dict(f["Central"].items(recursive=False, filter_classname="TTree"))
    key = f"Central/{tree};1"
    if key not in items:
        return None
    t = items[key]
    if t.num_entries == 0:
        return {b: np.array([]) for b in branches}
    return t.arrays(branches, library="np")


def load_all():
    """data[proc][cat] = dict(obs, w, mll, passMll)"""
    data = {}
    procs = {**{g: GROUPS[g] for g in GROUPS}, **{s: [s] for s in SIGNALS}}
    for proc, samples in procs.items():
        data[proc] = {}
        for cat, tree, obs in CATS:
            os_, ws, mls, pms = [], [], [], []
            for s in samples:
                a = read(s, tree, [obs, "weight", "mll", "passMllSR"])
                if a is None:
                    print(f"  [warn] {s}/{tree} missing")
                    continue
                os_.append(a[obs]); ws.append(a["weight"])
                mls.append(a["mll"]); pms.append(a["passMllSR"].astype(bool))
            data[proc][cat] = dict(
                obs=np.concatenate(os_) if os_ else np.array([]),
                w=np.concatenate(ws) if ws else np.array([]),
                mll=np.concatenate(mls) if mls else np.array([]),
                pm=np.concatenate(pms) if pms else np.array([], dtype=bool))
    return data


def subsel(d, mode):
    if mode == "all":
        m = np.ones(len(d["obs"]), dtype=bool)
    elif mode == "withlep":
        m = d["pm"]                      # sublead present & mll>200 (== old boosted)
    elif mode == "nolep":
        m = d["mll"] < -900.
    return d["obs"][m], d["w"][m]


def window(sig_obs, sig_w):
    if len(sig_obs) == 0 or sig_w.sum() <= 0:
        return None
    order = np.argsort(sig_obs)
    cw = np.cumsum(sig_w[order]) / sig_w.sum()
    lo = sig_obs[order][np.searchsorted(cw, 0.10)]
    hi = sig_obs[order][min(np.searchsorted(cw, 0.90), len(order) - 1)]
    return lo, hi


def zval(S, B):
    """Asimov significance; B floored at 1 event to keep ultra-clean windows finite."""
    B = max(B, 1.0)
    if S <= 0:
        return 0.
    return float(np.sqrt(2. * ((S + B) * np.log(1. + S / B) - S)))


def main():
    data = load_all()
    lines = []
    for sig in SIGNALS:
        ch = sig[-2:]
        lines.append(f"\n===== signal {sig} (channel {ch}) =====")
        scen_z = {"old": [], "merged": [], "split": []}
        for cat, tree, obsname in CATS:
            if not cat.endswith(ch):
                continue
            sd = data[sig][cat]
            pieces = ([("res", "all")] if cat.startswith("res") else
                      [("boo_old/withlep", "withlep"), ("boo_all", "all"), ("boo_nolep", "nolep")])
            for pname, mode in pieces:
                so, sw = subsel(sd, mode)
                wdw = window(so, sw)
                if wdw is None:
                    lines.append(f"  {cat}/{pname}: no signal")
                    continue
                lo, hi = wdw
                S = sw[(so >= lo) & (so <= hi)].sum()
                comps, B = {}, 0.
                for g in GROUPS:
                    bo, bw = subsel(data[g][cat], mode)
                    y = bw[(bo >= lo) & (bo <= hi)].sum()
                    comps[g] = y; B += y
                z = zval(S, B)
                comp_s = " ".join(f"{g}:{comps[g]:.1f}" for g in GROUPS)
                lines.append(f"  {cat:7s} {pname:15s} win[{lo:5.0f},{hi:5.0f}] "
                             f"S={S:8.1f} B={B:9.1f} ({comp_s})  Z={z:6.2f}")
                if pname == "res":
                    for k in scen_z:
                        scen_z[k].append(z)
                elif pname == "boo_old/withlep":
                    scen_z["old"].append(z); scen_z["split"].append(z)
                elif pname == "boo_all":
                    scen_z["merged"].append(z)
                elif pname == "boo_nolep":
                    scen_z["split"].append(z)
        for k, zs in scen_z.items():
            lines.append(f"  >> scenario {k:7s}: combined Z = "
                         f"{np.sqrt(sum(z * z for z in zs if np.isfinite(z))):.2f}")
    text = "\n".join(lines)
    print(text)
    with open(f"{HERE}/significance_study.txt", "w") as fh:
        fh.write(text + "\n")


if __name__ == "__main__":
    main()
