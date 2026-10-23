#!/usr/bin/env python3
"""Raw numbers behind the fake-rate maps: (1) event counts TT/TL/LT/LL, (2) per-muon T/L counts of truth-F muons
per (pT, |eta|) bin and the rate f = T/(T+L), for TTLJ alone and for all MC background (noQCD).
Regions: DY CR mumu SS (FO baseline) and SR mumu SS (FO baseline, mll>400; Full and Low 800-1600).
  -> results/16_np_counts_tables.txt
"""
import sys

import numpy as np

import dycr_analysis as DA
import fo_analysis as FA
import folib as L

PT = FA.PT_EDGES
ETA = FA.ETA_EDGES


def ev_table(d, m, P):
    row = []
    for c in L.CATS:
        mk = m & (d["cat"] == c)
        row.append(f"{c} {d['weight'][mk].sum():8.2f} [{mk.sum():5d}]")
    P("   events: " + "   ".join(row))


def mu_table(d, m, P, title):
    rm = FA.build_map(d, m, "F")
    P(f"   {title}: truth-F muons, per bin  T sumw [raw] | L sumw [raw] | f = T/(T+L)")
    P("   pT \\ |eta|".ljust(14) + "".join(f"{ETA[j]}-{ETA[j + 1]}".center(52) for j in range(len(ETA) - 1)))
    for i in range(len(PT) - 1):
        cells = []
        for j in range(len(ETA) - 1):
            cells.append(f"T {rm.T[i, j]:7.2f} [{rm.nT[i, j]:4d}] | L {rm.L[i, j]:8.2f} [{rm.nL[i, j]:5d}] | {rm.r[i, j]:.3f}±{rm.err[i, j]:.3f}")
        P(f"   {PT[i]}-{PT[i + 1]}".ljust(14) + "  ".join(c.rjust(50) for c in cells))
    tT, tL = rm.T.sum(), rm.L.sum()
    P(f"   all bins: T {tT:.2f} [{rm.nT.sum()}]  L {tL:.2f} [{rm.nL.sum()}]  f {tT / (tT + tL):.3f}")


def main():
    txt = []
    P = lambda *x: (txt.append(" ".join(str(y) for y in x)), print(*x))  # noqa: E731
    P("# FO baseline (exactly 2 FO muons, no FO electron), SS, weighted MC (signed) [raw entries]. W+jets = HT set, noQCD.")
    P("# per-muon table: each truth-F muon of every event counted once (T if TkRelIso<0.1, else L).")
    dy, _ = DA.load_dy()
    sr, _ = L.load()
    regs = [
        ("DY CR mumu SS (60<=mll<150, mlljj>800)", dy, dy["base"] & dy["ss"] & ~dy["data"] & ~dy["qcd"]),
        ("SR mumu SS Full (mll>400, mlljj>800)", sr, L.sel(sr, "SS", "Full") & FA.bkg_mask(sr, False)),
        ("SR mumu SS Low (mll>400, 800<mlljj<1600)", sr, L.sel(sr, "SS", "Low") & FA.bkg_mask(sr, False)),
    ]
    for name, d, m in regs:
        P(f"\n######## {name}")
        for lab, mm in (("TTLJ", m & (d["proc"] == "TTLJ")), ("all MC bkg", m)):
            P(f"\n## {lab}")
            ev_table(d, mm, P)
            mu_table(d, mm, P, lab)
    out = L.RESULTS + "/16_np_counts_tables.txt"
    open(out, "w").write("\n".join(txt) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    sys.exit(main())
