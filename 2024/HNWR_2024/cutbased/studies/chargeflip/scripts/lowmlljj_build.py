#!/usr/bin/env python3
"""Study 25 (step 0): event cache of the resolved low-m_lljj validation region.
Selection: channel == <--channel>, hasPair, nJet >= 2, passResolved, m_ll >= 200, m_lljj < 800  (OS and SS; data of that channel and all MC).
This is the open 'low-mass CR' of the analysis (m_ll > 200, m_lljj < 800). Events with m_lljj >= 800 are never read here.
    python3 studies/chargeflip/scripts/lowmlljj_build.py                 # EE -> data/lowmlljj_events.npz
    python3 studies/chargeflip/scripts/lowmlljj_build.py --channel 13    # MM -> data/lowmlljj_events_mm.npz"""
import argparse, glob, json, os
from pathlib import Path
import numpy as np
BASE = Path(__file__).resolve().parents[1]; DUMPS = Path(__file__).resolve().parents[5] / "BDT/SR/test/data/chargeflip/dumps_boost"
ap = argparse.ArgumentParser(); ap.add_argument("--channel", type=int, default=11, choices=[11, 13], help="11 = EE (EGamma data), 13 = MM (Muon data)")
ap.add_argument("--cache", default=None); ap.add_argument("--dumps", default=None, help="npz dump dir (default: BDT/SR/test/data/chargeflip/dumps_boost)")
ap.add_argument("--mll-min", type=float, default=200.0, help="lower m_ll edge of the cache (default 200 = the open low-mass CR; 60 to include the Z window)")
a = ap.parse_args()
if a.dumps: DUMPS = Path(a.dumps)
CH = "EE" if a.channel == 11 else "MM"; DATA_PREFIX = "EGamma" if a.channel == 11 else "Muon"; OTHER_PREFIX = "Muon" if a.channel == 11 else "EGamma"
CACHE = Path(a.cache) if a.cache else BASE / ("data/lowmlljj_events.npz" if a.channel == 11 else "data/lowmlljj_events_mm.npz")
KEYS = ["channel", "hasPair", "isSS", "nJet", "m_l1l2", "pt_l1l2", "m_lljj", "weight", "j1_pt", "j2_pt", "j1_eta", "j2_eta",
        "l1_pt", "l2_pt", "l1_scEta", "l2_scEta", "l1_eta", "l2_eta", "l1_phi", "l2_phi", "l1_charge", "l2_charge", "l1_genChargeIdx", "l2_genChargeIdx"]


def group_of(b):
    b = b.replace("tree_Skim_HNWR_", "").replace("tree_", "")
    if b.startswith("DYto2L"): return "DY"
    if b.startswith(DATA_PREFIX): return "DATA"
    if b.startswith((OTHER_PREFIX, "WRtoN")): return None
    if b.startswith(("TTto2L2Nu", "TWminusto2L2Nu", "TbarWplusto2L2Nu")): return "TT"
    if b.startswith(("WWto", "WZto", "ZZto", "TTLL", "TTLNu")): return "Others"
    return "Nonprompt"


acc = {k: [] for k in KEYS + ["grp"]}
for p in sorted(glob.glob(str(DUMPS / "tree_*.npz"))):
    g = group_of(os.path.basename(p))
    if g is None: continue
    z = np.load(p); m = (z["channel"] == a.channel) & (z["hasPair"] > 0) & (z["nJet"] >= 2) & (z["passResolved"] > 0) & (z["m_l1l2"] >= a.mll_min) & (z["m_lljj"] < 800)
    if not m.any(): continue
    for k in KEYS: acc[k].append(np.asarray(z[k][m], dtype="float64"))
    acc["grp"].append(np.full(int(m.sum()), g)); print(f"  {os.path.basename(p)[15:75]:60s} {g:9s} {int(m.sum()):8d}", flush=True)
d = {k: np.concatenate(v) for k, v in acc.items()}
tmp = CACHE.with_name(CACHE.name + ".tmp.npz"); np.savez_compressed(tmp, **d); os.replace(tmp, CACHE)
CACHE.with_suffix(".json").write_text(json.dumps(dict(source=str(DUMPS), selection=f"{CH}, hasPair, nJet>=2, passResolved, m_ll>={a.mll_min:.0f}, m_lljj<800", keys=KEYS, n=int(len(d["grp"]))), indent=1) + "\n"); print("wrote", CACHE, len(d["grp"]))
