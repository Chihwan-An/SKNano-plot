#!/usr/bin/env python3
"""2026-09-30: closure of the flip weight on the simulation in the resolved EE SR and SS DY CR (no data needed).

  pred  = sum over OS DY MC of weight x w(P1, P2)   with SF = 1 (the MC flip probability only)
  truth = sum over SS DY MC with a gen-level flipped electron of weight
Also the same for all backgrounds (OS MC x w vs flipped SS MC), per m_lljj bin of the card binning.
    osmc_sr_closure.py --dumps <dir> --json <ptshift json> --out <json> [--sr-edges ...]
"""
import argparse, copy, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chargeflip_ddss_dyonly as dd

ap = argparse.ArgumentParser()
ap.add_argument("--dumps", required=True); ap.add_argument("--json", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--sr-edges", default="800,1000,1200,1400,1600,2000,2400,2800,3200,8000")
a = ap.parse_args()
J = copy.deepcopy(json.load(open(a.json)))
J["sf"]["SF"].update(barrel=1.0, endcap=1.0, barrel_err=0.0, endcap_err=0.0)
J["sf"].pop("SF3", None)
keys = ["passResolved", "isDYCR", "m_l1l2", "m_lljj"] + [f"l{i}_{k}" for i in (1, 2) for k in ("pt", "scEta", "charge", "genChargeIdx")]
d = dd.load(a.dumps, keys=keys)
w, _ = dd.new_weights(J, d, sf2=True)
mc = (d["grp"] != "DATA") & (d["grp"] != "SIG")
flipped = d["l1_flip"] | d["l2_flip"]
edges = {"rEESR_SS": [float(x) for x in a.sr_edges.split(",")], "rDYEECR_SS": dd.EDGES["rDYEECR_SS"]}
out = {}
for reg, ed in edges.items():
    sel = dd.SEL[reg](d) & mc; R = {}
    for lab, gm in (("DY", d["grp"] == "DY"), ("DYTT", np.isin(d["grp"], ["DY", "TT"])), ("all", np.ones(len(mc), bool))):
        os_ = sel & gm & ~d["ss"]; ss_ = sel & gm & d["ss"] & flipped
        pv, pe = dd.fill(d["m_lljj"][os_], (d["weight"] * w)[os_], ed)
        tv, te = dd.fill(d["m_lljj"][ss_], d["weight"][ss_], ed)
        R[lab] = dict(pred=float(pv.sum()), pred_err=float(np.sqrt(pe.sum())), truth=float(tv.sum()), truth_err=float(np.sqrt(te.sum())),
                      ratio=float(pv.sum() / tv.sum()) if tv.sum() > 0 else None, edges=ed, pred_bins=pv.tolist(), truth_bins=tv.tolist(),
                      truth_bins_err=np.sqrt(te).tolist())
        print(f"{reg:11s} {lab:3s}  OS MC x w(SF=1) {pv.sum():8.2f} +- {np.sqrt(pe.sum()):.2f}   flipped SS MC {tv.sum():8.2f} +- {np.sqrt(te.sum()):.2f}"
              f"   pred/truth {pv.sum() / tv.sum():.3f}")
        print("    per bin pred/truth: " + " ".join(f"{p / t:.2f}" if t > 0 else "-" for p, t in zip(pv, tv)))
    out[reg] = R
json.dump(out, open(a.out, "w"), indent=1); print("wrote", a.out)
