#!/usr/bin/env python3
"""Code-drift check for the DY-only re-production: the same DY sample run today with the OLD correction
(userflags RFlav,DYCRCharge,SRChargeSplit) against the files of the existing productions. If the analyzer
did not change what these histograms hold, every common histogram agrees."""
import sys, numpy as np, uproot
S = "Skim_HNWR_DYto2L-4Jets_Bin-HT-2500-MLL-50to120.root"
NEW = "/gv0/Users/achihwan/SKNanoOutput_dynew/HNWR/RFlav_DYCRCharge_SRChargeSplit/2024/" + S
OLD = {"RFlav": "/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/RFlav/2024/" + S,
       "RFlav_DYCRCharge": "/gv0/Users/achihwan/SKNanoOutput/HNWR/RFlav_DYCRCharge/2024/" + S}
fn = uproot.open(NEW)
for tag, path in OLD.items():
    fo = uproot.open(path)
    for d in ("Central", "JES_Up", "ZPtRwQCDScale_Up", "ResolvedDYReshapeBin3_Down"):
        if d not in fo or d not in fn:
            print(f"{tag:18s} {d:28s} missing (old {d in fo}, new {d in fn})"); continue
        ko = {k.split(";")[0] for k, c in fo[d].classnames().items() if c.startswith("TH1")}
        kn = {k.split(";")[0] for k, c in fn[d].classnames().items() if c.startswith("TH1")}
        worst, wname, nbad = 0., "", 0
        for k in sorted(ko & kn):
            a, b = fo[d][k].values(), fn[d][k].values()
            if a.shape != b.shape: nbad += 1; continue
            den = np.abs(a).sum()
            r = np.abs(a - b).sum() / den if den > 0 else (0. if np.abs(b).sum() == 0 else 1.)
            if r > worst: worst, wname = r, k
            if r > 1e-4: nbad += 1
        print(f"{tag:18s} {d:28s} common {len(ko & kn):4d}  only-old {len(ko - kn):3d}  only-new {len(kn - ko):3d}  "
              f"differing(>1e-4) {nbad:3d}  worst {worst:.2e} {wname}")
        if ko - kn: print("     only in old:", sorted(ko - kn)[:8])
