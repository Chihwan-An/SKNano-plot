#!/usr/bin/env python3
"""FxFx/LO(raw) on reco Z pT inside the boosted DY CR, split by reco AK4 nJet (1 vs >=2), next to the 1-jet region J1 (2026-09-23).
Same inputs/definitions as boosted_njet_zpt.py (imported)."""
import sys, os, numpy as np
sys.argv = [sys.argv[0], "--out", os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")]
import importlib.util
EDR = np.array([0, 150, 200, 300, 400, 500, 700, 1500])
spec = importlib.util.spec_from_file_location("b", os.path.join(os.path.dirname(os.path.abspath(__file__)), "boosted_njet_zpt.py"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
L = ["## 4. boosted DY CR 을 reco nJet 로 나눈 FxFx / LO (DY 보정 없음), reco Z pT", "",
     "| ch | 영역 | LO Σw | 합 | " + " | ".join(f"{EDR[i]}-{EDR[i+1]}" for i in range(len(EDR) - 1)) + " |", "|---" * (len(EDR) + 3) + "|"]
for ch, cid in b.CH.items():
    for lab, cl, cf in (("J1 (1-jet 영역)", b.lo_reg["J1"], b.fx_reg["J1"]),
                        ("B, nJet=1", b.lo_reg["B"] & (b.lo["nJet"] == 1), b.fx_reg["B"] & (b.fx["nJet"] == 1)),
                        ("B, nJet≥2", b.lo_reg["B"] & (b.lo["nJet"] >= 2), b.fx_reg["B"] & (b.fx["nJet"] >= 2))):
        ml = cl & (b.lo["channel"] == cid); mf = cf & (b.fx["channel"] == cid)
        xl = np.clip(b.lo_zr[ml], 0, 1499); xf = np.clip(b.fx_zr[mf], 0, 1499); wl = b.w_raw[ml]; wf = b.fx["weight"][mf]
        hl = np.histogram(xl, EDR, weights=wl)[0]; el = np.histogram(xl, EDR, weights=wl ** 2)[0]
        hf = np.histogram(xf, EDR, weights=wf)[0]; ef = np.histogram(xf, EDR, weights=wf ** 2)[0]
        with np.errstate(divide="ignore", invalid="ignore"):
            r = hf / hl; re = np.abs(r) * np.sqrt(ef / hf ** 2 + el / hl ** 2)
        cells = [f"{x:.2f}±{y:.2f}" if hl[i] > 0 and hf[i] > 0 and y < 0.5 else "–" for i, (x, y) in enumerate(zip(r, re))]
        L.append(f"| {ch} | {lab} | {hl.sum():.0f} | {hf.sum() / hl.sum():.3f} | " + " | ".join(cells) + " |")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots", "tables_split.md"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
