#!/usr/bin/env python3
"""Study 24d: the (m_ll, Z pT) transfer in m_ll slices, and its dependence on the binning of f.  EE, OS, 1-jet target, dR(ll) > 0.4.
For every m_ll slice: yields and flip-weighted sums (w from chargeflip_ptshift_ee2024_sf3.json) of 1-jet DATA, native 1-jet MC and
[2-jet SR-topology DY MC x f + 1-jet non-DY MC], with MC statistical errors, and the leading-electron |eta_SC| shape chi2 of data against both.
f = N_DY(1j)/N_DY(2j) is derived here (DY MC, m_ll >= 60) for three binnings: nominal (as study 24), fine, coarse. N_eff < 30 cells -> m_ll-only factor.
    python3 studies/chargeflip/scripts/mll_zpt_2d_slices.py"""
import json
from pathlib import Path
import numpy as np
BASE = Path(__file__).resolve().parents[1]; T_ = Path(__file__).resolve().parents[5] / "BDT/SR/test"; OUT = BASE / "AN_rawcharge/24_mll_zpt_2d_factor_drll"
z = np.load(BASE / "data/zpt_zeta_transfer_events.npz"); ee = z["channel"] == 11; d = {k: (z[k][ee].astype("float64") if z[k].dtype == np.float32 else z[k][ee]) for k in z.files}
isdata = d["grp"] == "DATA"; d["weight"] = np.where(isdata, 1.0, d["weight"]); two = d["topo2j"].astype(bool)
dphi = np.abs(d["l1_phi"] - d["l2_phi"]); dphi = np.where(dphi > np.pi, 2 * np.pi - dphi, dphi); keep = two | (np.hypot(d["l1_eta"] - d["l2_eta"], dphi) > 0.4)
d = {k: v[keep] for k, v in d.items()}; two = d["topo2j"].astype(bool); one = ~two; isdata = d["grp"] == "DATA"; dy = d["grp"] == "DY"; W = d["weight"]
J = json.load(open(T_ / "data/chargeflip/chargeflip_ptshift_ee2024_sf3.json")); regs = list(J["rate_regions"].items()); P = np.nan_to_num(np.array(J["P"])); pt_edges = np.array(J["pt_edges"])
sfreg = {n: tuple(v) for n, v in J["sf"]["SF3"]["regions"].items()}; SFv = dict(J["sf"]["SF3"]["SF"]); names = list(sfreg)
reg_sf = np.array([next((k for k, n in enumerate(names) if sfreg[n][0] <= 0.5 * (lo + hi) < sfreg[n][1]), -1) for _, (lo, hi) in regs]); sf0 = np.array([SFv[n] for n in names]); pl = []
for i in (1, 2):
    ae = np.abs(d[f"l{i}_scEta"]); ie = np.full(len(ae), -1)
    for k, (_, (lo, hi)) in enumerate(regs): ie[(ae >= lo) & (ae < hi)] = k
    ip = np.clip(np.searchsorted(pt_edges, d[f"l{i}_pt"], side="right") - 1, 0, len(pt_edges) - 2); p = np.zeros(len(ie)); ok = ie >= 0; p[ok] = P[ie[ok], ip[ok]] * sf0[reg_sf[ie[ok]]]; pl.append(p)
w = (pl[0] * (1 - pl[1]) + pl[1] * (1 - pl[0])) / ((1 - pl[0]) * (1 - pl[1]) + pl[0] * pl[1]); inf = np.inf
BINS = {"nominal": ([60, 70, 80, 85, 90, 95, 100, 110, 130, 150, 200, 250, 300, 400, 450, 500, 600, 700, 800, 1000, 1300, inf], [0, 25, 50, 75, 100, 125, 150, 175, 200, 250, 300, 400, 500, 600, 800, 1000, inf]),
        "fine": (list(range(60, 150, 5)) + list(range(150, 400, 25)) + list(range(400, 1000, 50)) + [1000, 1150, 1300, 1600, 2000, inf], list(range(0, 300, 10)) + list(range(300, 500, 25)) + [500, 550, 600, 700, 800, 1000, inf]),
        "coarse": ([60, 150, 200, 300, 400, 500, 700, 1000, inf], [0, 50, 100, 150, 200, 300, 400, 600, inf])}


def derive(xe, ye):
    xe, ye = np.array(xe, float), np.array(ye, float); h = lambda m: (np.histogram2d(d["m_l1l2"][m], d["pt_l1l2"][m], [xe, ye], weights=W[m])[0], np.histogram2d(d["m_l1l2"][m], d["pt_l1l2"][m], [xe, ye], weights=W[m] ** 2)[0])
    (n1, v1), (n2, v2) = h(dy & one), h(dy & two); neff = lambda n, v: np.where(v > 0, n * n / np.where(v > 0, v, 1), 0.0); ok = (neff(n1, v1) >= 30) & (neff(n2, v2) >= 30)
    fx = n1.sum(1) / np.where(n2.sum(1) > 0, n2.sum(1), 1); f = np.where(ok, n1 / np.where(n2 > 0, n2, 1), fx[:, None])
    return f[np.clip(np.searchsorted(xe, d["m_l1l2"], side="right") - 1, 0, len(xe) - 2), np.clip(np.searchsorted(ye, d["pt_l1l2"], side="right") - 1, 0, len(ye) - 2)], int(ok.sum()), ok.size


ETA = np.array([0, 0.5, 1.0, 1.4442, 1.566, 2.0, 2.5]); SL = [(150, 200), (200, 300), (300, 400), (200, 400), (400, 500), (500, 700), (400, 700), (700, 1000), (1000, 1e9), (700, 1e9), (400, 1e9)]; R = {}
for bname, (xe, ye) in BINS.items():
    fev, nok, ntot = derive(xe, ye); R[bname] = {}
    print(f"\n=== f binning: {bname}  ({len(xe) - 1} m_ll x {len(ye) - 1} Z pT bins, 2D cells used {nok}/{ntot}) ===")
    print("  m_ll slice |  N data   N native     N transf |  Sum w data      Sum w native (data/MC)        Sum w transferred (data/MC)   | <w> DY nat / 2jxf | l1 |eta| shape chi2/4: native, transf | endcap frac data / nat / transf")
    for lo, hi in SL:
        s = (d["m_l1l2"] >= lo) & (d["m_l1l2"] < hi); D = s & one & isdata; M = s & one & ~isdata; ND = M & ~dy; D1 = s & one & dy; D2 = s & two & dy
        sw_d, e_d = w[D].sum(), np.sqrt((w[D] ** 2).sum()); sw_n, e_n = (W * w)[M].sum(), np.sqrt(((W * w)[M] ** 2).sum()); t = W * w * fev; sw_t, e_t = t[D2].sum() + (W * w)[ND].sum(), np.sqrt((t[D2] ** 2).sum() + ((W * w)[ND] ** 2).sum())
        x = np.abs(d["l1_scEta"]); hd = np.histogram(x[D], ETA)[0].astype(float); hn = np.histogram(x[M], ETA, weights=W[M])[0]; ht = np.histogram(x[D2], ETA, weights=(W * fev)[D2])[0] + np.histogram(x[ND], ETA, weights=W[ND])[0]; okb = hd > 0
        chi = lambda m: float((((hd - hd[okb].sum() / m[okb].sum() * m)[okb]) ** 2 / hd[okb]).sum()); rd = lambda a, ea, b, eb: (a / b, a / b * np.hypot(ea / a, eb / b))
        r1, r2 = rd(sw_d, e_d, sw_n, e_n), rd(sw_d, e_d, sw_t, e_t); lab = f"{lo}-{hi:.0f}" if hi < 1e8 else f">={lo}"
        R[bname][lab] = dict(n_data=int(D.sum()), n_native=float(W[M].sum()), n_transferred=float((W * fev)[D2].sum() + W[ND].sum()), sumw_data=float(sw_d), sumw_data_err=float(e_d), sumw_native=float(sw_n), sumw_native_err=float(e_n), sumw_transferred=float(sw_t), sumw_transferred_err=float(e_t),
                             data_over_native=r1, data_over_transferred=r2, meanw_dy_native=float((W * w)[D1].sum() / W[D1].sum()), meanw_dy_2jxf=float(t[D2].sum() / (W * fev)[D2].sum()), chi2_eta_native=chi(hn), chi2_eta_transferred=chi(ht),
                             endcap=dict(data=float(hd[4:].sum() / hd.sum()), native=float(hn[4:].sum() / hn.sum()), transferred=float(ht[4:].sum() / ht.sum())))
        q = R[bname][lab]
        print(f"  {lab:10s} | {q['n_data']:7d} {q['n_native']:10.1f} {q['n_transferred']:12.1f} | {sw_d:8.2f}+-{e_d:5.2f}  {sw_n:8.2f}+-{e_n:5.2f} ({r1[0]:.3f}+-{r1[1]:.3f})  {sw_t:8.2f}+-{e_t:5.2f} ({r2[0]:.3f}+-{r2[1]:.3f}) | {q['meanw_dy_native']:.5f} / {q['meanw_dy_2jxf']:.5f} |"
              f" {q['chi2_eta_native']:7.1f} {q['chi2_eta_transferred']:7.1f} | {q['endcap']['data']:.3f} / {q['endcap']['native']:.3f} / {q['endcap']['transferred']:.3f}")
(OUT / "slices.json").write_text(json.dumps(R, indent=1) + "\n")
