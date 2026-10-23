#!/usr/bin/env python3
"""Study 19 (step 0): event cache for the (Z pT, Z eta) 2-jet -> 1-jet transfer study.
Keeps OS events with hasPair, m_ll >= 60 and either nJet == 1 or the SR topology (nJet >= 2, passResolved, m_lljj > 800), EE and MM.
DATA: 1-jet events at any m_ll, and 2-jet events ONLY inside the DY CR (60 <= m_ll < 150). 2-jet data above 150 GeV (sideband / SR)
are never read. EE data = EGamma stream, MM data = Muon stream. float32 columns.
    python3 zpt_zeta_transfer_build.py [--dumps DIR] [--cache FILE]"""
import argparse, glob, json, os
from pathlib import Path
import numpy as np
BASE = Path(__file__).resolve().parents[1]; T_ = Path(__file__).resolve().parents[5] / "BDT/SR/test"
ap = argparse.ArgumentParser()
ap.add_argument("--dumps", default=str(T_ / "data/chargeflip/dumps_boost")); ap.add_argument("--cache", default=str(BASE / "data/zpt_zeta_transfer_events.npz"))
a = ap.parse_args()
KEYS = ["channel", "nJet", "m_l1l2", "pt_l1l2", "m_lljj", "weight", "w_dy", "l1_pt", "l2_pt", "l1_scEta", "l2_scEta", "l1_eta", "l2_eta", "l1_phi", "l2_phi"]


def group_of(b):
    b = b.replace("tree_Skim_HNWR_", "").replace("tree_", "")
    if b.startswith("DYto2L"): return "DY"
    if b.startswith("EGamma"): return "DATA_EG"
    if b.startswith("Muon"): return "DATA_MU"
    if b.startswith("WRtoN"): return None
    if b.startswith(("TTto2L2Nu", "TWminusto2L2Nu", "TbarWplusto2L2Nu")): return "TT"
    if b.startswith(("WWto", "WZto", "ZZto", "TTLL", "TTLNu")): return "Others"
    return "Nonprompt"


acc = {k: [] for k in KEYS + ["grp", "topo2j"]}
for p in sorted(glob.glob(os.path.join(a.dumps, "tree_*.npz"))):
    g = group_of(os.path.basename(p))
    if g is None: continue
    z = np.load(p); ch = z["channel"]; mll = z["m_l1l2"]
    topo = (z["nJet"] >= 2) & (z["passResolved"] > 0) & (z["m_lljj"] > 800)
    m = (z["hasPair"] > 0) & (z["isSS"] == 0) & (mll >= 60) & ((z["nJet"] == 1) | topo) & ((ch == 11) | (ch == 13))
    if g.startswith("DATA"):
        m &= (ch == 11) if g == "DATA_EG" else (ch == 13)           # stream <-> channel
        m &= ~(topo & (mll >= 150))                                  # blinding: 2-jet data only inside the DY CR window
    if not m.any(): continue
    for k in KEYS: acc[k].append(np.asarray(z[k][m], dtype="float32"))
    acc["grp"].append(np.full(int(m.sum()), "DATA" if g.startswith("DATA") else g)); acc["topo2j"].append(topo[m])
    print(f"  {os.path.basename(p)[5:60]:56s} {g:9s} {int(m.sum()):9d}", flush=True)
d = {k: np.concatenate(v) for k, v in acc.items()}
np.savez_compressed(a.cache, **d)
Path(a.cache).with_suffix(".json").write_text(json.dumps(dict(source_directory=str(Path(a.dumps).resolve()), keys=KEYS, n=int(len(d["channel"])),
    selection="hasPair & OS & m_ll>=60 & (nJet==1 | (nJet>=2 & passResolved & m_lljj>800)); data: stream-matched, 2-jet data only for m_ll<150"), indent=1) + "\n")
print("cached", len(d["channel"]), "events ->", a.cache)
