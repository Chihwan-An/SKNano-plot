#!/usr/bin/env python3
"""Study 24b: flip-weighted check of the 2D transfer. EE, OS. Compares Sum w (w = flip weight with the data SF, chargeflip_ptshift_ee2024_sf3.json) of
1-jet DATA, the native 1-jet MC, and [2-jet SR-topology DY MC x f(m_ll, Z pT) + 1-jet non-DY MC], and the mean w of the DY components.
f is read from AN_rawcharge/24_mll_zpt_2d_factor_drll/summary.json (zpt_zeta_transfer_study.py --factor mll_zpt --drll). numpy only.
    python3 studies/chargeflip/scripts/mll_zpt_2d_sigma_w.py"""
import json
from pathlib import Path
import numpy as np
BASE = Path(__file__).resolve().parents[1]; T_ = Path(__file__).resolve().parents[5] / "BDT/SR/test"; OUT = BASE / "AN_rawcharge/24_mll_zpt_2d_factor_drll"
z = np.load(BASE / "data/zpt_zeta_transfer_events.npz"); ee = z["channel"] == 11; d = {k: (z[k][ee].astype("float64") if z[k].dtype == np.float32 else z[k][ee]) for k in z.files}
isdata = d["grp"] == "DATA"; d["weight"] = np.where(isdata, 1.0, d["weight"]); two = d["topo2j"].astype(bool)
dphi = np.abs(d["l1_phi"] - d["l2_phi"]); dphi = np.where(dphi > np.pi, 2 * np.pi - dphi, dphi); keep = two | (np.hypot(d["l1_eta"] - d["l2_eta"], dphi) > 0.4)
d = {k: v[keep] for k, v in d.items()}; two = d["topo2j"].astype(bool); one = ~two; isdata = d["grp"] == "DATA"
J = json.load(open(T_ / "data/chargeflip/chargeflip_ptshift_ee2024_sf3.json")); regs = list(J["rate_regions"].items()); P = np.nan_to_num(np.array(J["P"])); pt_edges = np.array(J["pt_edges"])
sfreg = {n: tuple(v) for n, v in J["sf"]["SF3"]["regions"].items()}; SFv = dict(J["sf"]["SF3"]["SF"]); names = list(sfreg)
reg_sf = np.array([next((k for k, n in enumerate(names) if sfreg[n][0] <= 0.5 * (lo + hi) < sfreg[n][1]), -1) for _, (lo, hi) in regs]); sf0 = np.array([SFv[n] for n in names])
pl = []
for i in (1, 2):
    ae = np.abs(d[f"l{i}_scEta"]); ie = np.full(len(ae), -1)
    for k, (_, (lo, hi)) in enumerate(regs): ie[(ae >= lo) & (ae < hi)] = k
    ip = np.clip(np.searchsorted(pt_edges, d[f"l{i}_pt"], side="right") - 1, 0, len(pt_edges) - 2); p = np.zeros(len(ie)); ok = ie >= 0; p[ok] = P[ie[ok], ip[ok]] * sf0[reg_sf[ie[ok]]]; pl.append(p)
w = (pl[0] * (1 - pl[1]) + pl[1] * (1 - pl[0])) / ((1 - pl[0]) * (1 - pl[1]) + pl[0] * pl[1])
F = json.load(open(OUT / "summary.json"))["EE"]["factor"]; f = np.array(F["f"]); XE = np.array([np.inf if x is None else x for x in F["zpt_edges"]]); YE = np.array([np.inf if x is None else x for x in F["zeta_edges"]])   # x = m_ll, y = Z pT in mll_zpt mode
fev = f[np.clip(np.searchsorted(XE, d["m_l1l2"], side="right") - 1, 0, len(XE) - 2), np.clip(np.searchsorted(YE, d["pt_l1l2"], side="right") - 1, 0, len(YE) - 2)]
R = {}; print("EE, OS, dR(ll)>0.4.  Sum w: 1-jet data | native 1-jet MC | 2j DY x f + 1j non-DY          <w> of DY: native 1j | 2j x f | 2j (no f)")
for name, lo, hi in (("60-150", 60, 150), ("150-400", 150, 400), (">=400", 400, 1e9), (">=700", 700, 1e9)):
    s = (d["m_l1l2"] >= lo) & (d["m_l1l2"] < hi); dy = d["grp"] == "DY"; D = s & one & isdata; M1 = s & one & ~isdata; DY1 = s & one & dy; DY2 = s & two & dy; ND = s & one & ~isdata & ~dy
    sw = lambda m, x=1.0: float((d["weight"][m] * w[m] * (x if np.isscalar(x) else x[m])).sum()); n = lambda m, x=1.0: float((d["weight"][m] * (x if np.isscalar(x) else x[m])).sum())
    r = dict(sumw_data=sw(D), sumw_native=sw(M1), sumw_transferred=sw(DY2, fev) + sw(ND), n_data=n(D), n_native=n(M1), n_transferred=n(DY2, fev) + n(ND),
             meanw_dy_native=sw(DY1) / n(DY1), meanw_dy_2jxf=sw(DY2, fev) / n(DY2, fev), meanw_dy_2j=sw(DY2) / n(DY2), meanw_data=sw(D) / n(D), err_data=float(np.sqrt((w[D] ** 2).sum())))
    r["data_over_native"] = r["sumw_data"] / r["sumw_native"]; r["data_over_transferred"] = r["sumw_data"] / r["sumw_transferred"]; R[name] = r
    print(f"  m_ll {name:8s} {r['sumw_data']:9.2f} +- {r['err_data']:5.2f} | {r['sumw_native']:9.2f} (data/MC {r['data_over_native']:.3f}) | {r['sumw_transferred']:9.2f} (data/MC {r['data_over_transferred']:.3f})"
          f"      {r['meanw_dy_native']:.5f} | {r['meanw_dy_2jxf']:.5f} | {r['meanw_dy_2j']:.5f}   (data, all comps: {r['meanw_data']:.5f})")
(OUT / "sigma_w.json").write_text(json.dumps(R, indent=1) + "\n")
