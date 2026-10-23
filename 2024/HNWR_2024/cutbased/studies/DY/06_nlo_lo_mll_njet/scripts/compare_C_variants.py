#!/usr/bin/env python
"""C(pT) derived three ways, to separate three effects that get confused.

All curves are shape-only normalised exactly as the delivered correction is
(K = sum NLO / sum LO over pT >= 50, divided out), so only the *shape* is being
compared -- the normalisation difference between them is printed separately.

  inclusive      what ships: every LHE multiplicity summed, HT > 40 on both sides
  Njets == 1     the only multiplicity where both generators have a matrix
                 element. Answers "does the correction change if we compare
                 like with like in parton multiplicity?"
  m(ll) slices   inclusive in multiplicity, but derived separately in
                 50-120 / 120-200 / >200. Each slice carries its own K, so the
                 mass-dependent normalisation is taken out and what remains is
                 the mass dependence of the *pT shape*.

The HT > 40 question is answered by printing Njets == 1 with and without it: if
the 40 GeV threshold were what makes the one-jet ratio large, removing it would
move the curve.

Run (tamsa2, Nano15 env):
    python3 compare_C_variants.py [--out DIR]
"""
import argparse
import importlib.util
import json
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRIPTS = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/HNWR/scripts"
_spec = importlib.util.spec_from_file_location(
    "_zpt", os.path.join(SCRIPTS, "make_dy_zpt_nlo_lo.py"))
Z = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(Z)

# Coarse enough to read, and the three tail bins are the ones the correction
# actually delivers (250-350, 350-500, 500-1000).
GRID = np.array([50, 60, 70, 80, 90, 100, 120, 150, 200, 250, 350, 500, 1000], float)
NORM_MIN_PT = 50.0

VARIANTS = [
    ("Zpt_genZ_HT40", "inclusive (delivered)"),
    ("Zpt_genZ_HT40_Njet1", "LHE $N_{jets}=1$"),
    ("Zpt_genZ_Njet1", "LHE $N_{jets}=1$, no $H_T$ cut"),
    ("Zpt_genZ_HT40_M50to120", r"$m(\ell\ell)$ 50-120"),
    ("Zpt_genZ_HT40_M120to200", r"$m(\ell\ell)$ 120-200"),
    ("Zpt_genZ_HT40_M200toInf", r"$m(\ell\ell) > 200$"),
]


def summed(base, era, aliases, variant, lumi_pb):
    acc, edges = None, None
    for a in aliases:
        got = Z.read_one(f"{base}/{era}/{a}.root", "Central", variant)
        if got is None:
            continue
        v, var, e = got
        edges = e
        v, var = v * lumi_pb, var * lumi_pb ** 2
        acc = [v.copy(), var.copy()] if acc is None else [acc[0] + v, acc[1] + var]
    return acc, edges


def rebin(v, var, src, dst):
    c = 0.5 * (src[:-1] + src[1:])
    idx = np.searchsorted(dst, c, side="right") - 1
    ok = (idx >= 0) & (idx < len(dst) - 1)
    ov, oe = np.zeros(len(dst) - 1), np.zeros(len(dst) - 1)
    np.add.at(ov, idx[ok], v[ok])
    np.add.at(oe, idx[ok], var[ok])
    return ov, oe


def curve(base, era, variant, lumi_pb):
    """(C on GRID, stat error, K) with the shipped shape-only normalisation."""
    nlo_s, lo_s = Z.samples_for(era)
    nlo, e1 = summed(base, era, nlo_s, variant, lumi_pb)
    lo, e2 = summed(base, era, lo_s, variant, lumi_pb)
    if nlo is None or lo is None:
        return None
    src = np.asarray(e1, float)
    m = src[:-1] >= NORM_MIN_PT
    K = nlo[0][m].sum() / lo[0][m].sum()
    n, nv = rebin(nlo[0], nlo[1], src, GRID)
    d, dv = rebin(lo[0], lo[1], src, GRID)
    with np.errstate(divide="ignore", invalid="ignore"):
        raw = np.where(d > 0, n / d, np.nan)
        err = np.where(d > 0, np.sqrt(nv / d**2 + n**2 * dv / d**4), np.nan)
    return raw / K, err / K, K


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.path.join(
        os.environ.get("SKNANO_OUTPUT", "/gv0/Users/achihwan/SKNanoOutput"), "DYGenZpT"))
    ap.add_argument("--era", default="2024")
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)) + "/../plots")
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    lumi_pb = Z.LUMI[args.era] * 1000.0

    res = {}
    for name, _ in VARIANTS:
        c = curve(args.base, args.era, name, lumi_pb)
        if c is None:
            print(f"[skip] {name}: no input")
            continue
        res[name] = c

    lab = [f"{int(GRID[i])}-{int(GRID[i+1])}" for i in range(len(GRID) - 1)]
    print("\n=== C(pT), shape-only normalised (each curve by its own K) ===")
    print(f"{'pT bin':<12}" + "".join(f"{n.replace('Zpt_genZ_','').replace('HT40_',''):>16}"
                                      for n in res))
    for i, l in enumerate(lab):
        print(f"{l:<12}" + "".join(
            f"{res[n][0][i]:>16.4f}" if np.isfinite(res[n][0][i]) else f"{'---':>16}"
            for n in res))
    print(f"{'K (divided)':<12}" + "".join(f"{res[n][2]:>16.4f}" for n in res))

    base_name = "Zpt_genZ_HT40"
    if base_name in res:
        print("\n=== shape difference: C_variant / C_inclusive ===")
        print(f"{'pT bin':<12}" + "".join(
            f"{n.replace('Zpt_genZ_','').replace('HT40_',''):>16}"
            for n in res if n != base_name))
        for i, l in enumerate(lab):
            cells = []
            for n in res:
                if n == base_name:
                    continue
                a, b = res[n][0][i], res[base_name][0][i]
                cells.append(f"{a/b:>16.4f}" if np.isfinite(a) and np.isfinite(b) and b != 0
                             else f"{'---':>16}")
            print(f"{l:<12}" + "".join(cells))

    # --- figure: two panels, each C curves + ratio to the delivered one
    groups = [("multiplicity", ["Zpt_genZ_HT40", "Zpt_genZ_HT40_Njet1", "Zpt_genZ_Njet1"]),
              ("mass", ["Zpt_genZ_HT40", "Zpt_genZ_HT40_M50to120",
                        "Zpt_genZ_HT40_M120to200", "Zpt_genZ_HT40_M200toInf"])]
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 6.8), sharex=True,
                             gridspec_kw={"height_ratios": [2.2, 1.0], "hspace": 0.07,
                                          "wspace": 0.22})
    ctr = 0.5 * (GRID[:-1] + GRID[1:])
    colors = ["k", "tab:red", "tab:orange", "tab:blue", "tab:green", "tab:purple"]
    titles = {"multiplicity": "parton multiplicity", "mass": r"$m(\ell\ell)$ slice"}
    for icol, (gname, names) in enumerate(groups):
        ax, rax = axes[0][icol], axes[1][icol]
        for j, n in enumerate([x for x in names if x in res]):
            lbl = dict(VARIANTS)[n]
            ax.errorbar(ctr, res[n][0], yerr=res[n][1], fmt="o-", ms=3.2, lw=1.2,
                        color=colors[j], label=lbl)
            if n != base_name and base_name in res:
                rax.plot(ctr, res[n][0] / res[base_name][0], "o-", ms=3.2, lw=1.2,
                         color=colors[j])
        ax.set_xscale("log")
        ax.set_xlim(GRID[0], GRID[-1])
        ax.axhline(1.0, color="gray", lw=0.8, ls=":")
        ax.set_title(titles[gname], fontsize=11)
        ax.legend(fontsize=8.5, loc="lower left")
        ax.grid(alpha=0.25, which="both")
        if icol == 0:
            ax.set_ylabel(r"$C(p_T)$, shape-only")
        rax.axhline(1.0, color="gray", lw=0.8, ls=":")
        rax.set_xscale("log")
        rax.set_xlim(GRID[0], GRID[-1])
        rax.set_xlabel(r"gen $p_T(Z)$ [GeV]")
        rax.grid(alpha=0.25, which="both")
        if icol == 0:
            rax.set_ylabel("/ delivered")
    fig.suptitle(f"DY Z-$p_T$ correction, {args.era}: how C changes with what it is "
                 f"derived from", fontsize=12)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.9, bottom=0.11)
    stem = os.path.join(out, f"C_variants_{args.era}")
    for ext in ("pdf", "png"):
        fig.savefig(f"{stem}.{ext}", dpi=140)
    print(f"\nwrote {stem}.pdf/.png")
    with open(f"{stem}.json", "w") as f:
        json.dump({"grid": GRID.tolist(),
                   **{n: {"C": np.nan_to_num(v[0], nan=0).tolist(),
                          "err": np.nan_to_num(v[1], nan=0).tolist(), "K": v[2]}
                      for n, v in res.items()}}, f)


if __name__ == "__main__":
    main()
