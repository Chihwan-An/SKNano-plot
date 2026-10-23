#!/usr/bin/env python3
"""Study 24c: does the 1-jet DATA tell the native 1-jet MC from [2-jet DY MC x f(m_ll, Z pT) + 1-jet non-DY MC] in the electron |eta_SC| shape?  EE, OS, m_ll >= 400.
    python3 studies/chargeflip/scripts/mll_zpt_2d_eta_datacheck.py"""
import json
from pathlib import Path
import numpy as np
BASE = Path(__file__).resolve().parents[1]; OUT = BASE / "AN_rawcharge/24_mll_zpt_2d_factor_drll"
z = np.load(BASE / "data/zpt_zeta_transfer_events.npz"); ee = (z["channel"] == 11) & (z["m_l1l2"] >= 400); d = {k: (z[k][ee].astype("float64") if z[k].dtype == np.float32 else z[k][ee]) for k in z.files}
isdata = d["grp"] == "DATA"; d["weight"] = np.where(isdata, 1.0, d["weight"]); two = d["topo2j"].astype(bool)
dphi = np.abs(d["l1_phi"] - d["l2_phi"]); dphi = np.where(dphi > np.pi, 2 * np.pi - dphi, dphi); keep = two | (np.hypot(d["l1_eta"] - d["l2_eta"], dphi) > 0.4)
d = {k: v[keep] for k, v in d.items()}; two = d["topo2j"].astype(bool); one = ~two; isdata = d["grp"] == "DATA"; dy = d["grp"] == "DY"
F = json.load(open(OUT / "summary.json"))["EE"]["factor"]; f = np.array(F["f"]); XE = np.array([np.inf if x is None else x for x in F["zpt_edges"]]); YE = np.array([np.inf if x is None else x for x in F["zeta_edges"]])
fev = f[np.clip(np.searchsorted(XE, d["m_l1l2"], side="right") - 1, 0, len(XE) - 2), np.clip(np.searchsorted(YE, d["pt_l1l2"], side="right") - 1, 0, len(YE) - 2)]
E = np.array([0, 0.5, 1.0, 1.4442, 1.566, 2.0, 2.5]); R = {}
for lep in ("l1", "l2"):
    x = np.abs(d[f"{lep}_scEta"]); h = lambda m, w: np.histogram(x[m], E, weights=w)[0]
    D = h(one & isdata, None); nat = h(one & ~isdata, d["weight"][one & ~isdata]); nd = h(one & ~isdata & ~dy, d["weight"][one & ~isdata & ~dy]); tr = h(two & dy, (d["weight"] * fev)[two & dy]) + nd
    dy1 = h(one & dy, d["weight"][one & dy]); dy2 = h(two & dy, (d["weight"] * fev)[two & dy]); okb = D > 0; out = {}
    print(f"\n{lep} |eta_SC| bins {E.tolist()}  (bin 1.44-1.57 = gap)\n  data            " + " ".join(f"{v:8.0f}" for v in D))
    for name, m in (("native 1j MC", nat), ("transferred", tr)):
        sc = D[okb].sum() / m[okb].sum(); chi = float((((D - sc * m)[okb]) ** 2 / D[okb]).sum()); out[name] = dict(chi2_shape=chi, ndf=int(okb.sum() - 1), data_over_mc=(D / np.where(m > 0, m, 1)).tolist())
        print(f"  {name:15s} " + " ".join(f"{v:8.1f}" for v in m) + f"   data/MC: " + " ".join(f"{a / b:5.2f}" if b > 0 else "    -" for a, b in zip(D, m)) + f"   shape chi2/ndf (data stat only) = {chi:.1f}/{okb.sum() - 1}")
    print("  DY only: 2jxf / native 1j  " + " ".join(f"{a / b:5.2f}" if b > 0 else "    -" for a, b in zip(dy2, dy1)) + f"    endcap (|eta|>1.566) fraction: data {D[4:].sum() / D.sum():.3f}, native MC {nat[4:].sum() / nat.sum():.3f}, transferred {tr[4:].sum() / tr.sum():.3f}")
    out["endcap_fraction"] = dict(data=float(D[4:].sum() / D.sum()), data_err=float(np.sqrt(D[4:].sum()) / D.sum()), native=float(nat[4:].sum() / nat.sum()), transferred=float(tr[4:].sum() / tr.sum())); R[lep] = out
(OUT / "eta_datacheck.json").write_text(json.dumps(R, indent=1) + "\n")
