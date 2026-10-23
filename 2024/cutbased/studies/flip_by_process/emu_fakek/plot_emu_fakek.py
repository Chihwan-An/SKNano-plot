#!/usr/bin/env python3
"""Resolved e-mu flavour CR, OS/SS m_lljj: how far does the data/MC muon fake-rate factor k move the MC? (stat errors only)
Input: plotter TSV of the FlipSF production (no flip SF on e-mu yet) -> out/flipsf_flv/before/E_Mu/jet_lepton/{OS,SS}/ResolveFLVEM_{OS,SS}_mlljj.tsv
The e-mu MC carries no truth, so k is applied to two envelopes:
  (1) Nonprompt group x k            (W+jets, semileptonic top, single top: the fake-muon-rich samples)
  (2) Nonprompt and TT x k           (TT SS in e-mu = b-hadron leptons, also nonprompt; upper edge: every fake treated as a muon)
k = 1.3 (studies/nonprompt_ssmm MEMO §17: data/MC fake-muon rate 1.27-1.33). Stat error = MC stat per group (TSV *_Stat_pct) in quadrature.
"""
import csv, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

K = 1.3
B = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/out/flipsf_flv/before/E_Mu/jet_lepton"
OUT = os.path.dirname(os.path.abspath(__file__))
G = ["DYJets", "Others", "TT", "Nonprompt"]
COL = {"Nonprompt": "#3f9c5a", "TT": "#d0463c", "Others": "#3f63c7", "DYJets": "#e9c43b"}
LAB = {"Nonprompt": "Nonprompt", "TT": "tt̄+tW", "Others": "Others", "DYJets": "Drell-Yan"}


def load(cs):
    R = list(csv.DictReader(open(f"{B}/{cs}/ResolveFLVEM_{cs}_mlljj.tsv"), delimiter="\t"))
    R = [r for r in R if r["Bin"] != "Total"]
    lo = np.array([float(r["BinLow"]) for r in R]); hi = np.array([float(r["BinHigh"]) for r in R])
    d = np.array([float(r["Data"]) for r in R])
    n = {g: np.array([float(r[g]) for r in R]) for g in G}
    e = {g: n[g] * np.array([float(r[f"{g}_Stat_pct"]) for r in R]) / 100 for g in G}
    return lo, hi, d, n, e


def variant(n, e, scaled):
    tot = sum(n[g] * (K if g in scaled else 1) for g in G)
    err = np.sqrt(sum((e[g] * (K if g in scaled else 1)) ** 2 for g in G))
    return tot, err


lines = ["# resolved e-mu flavour CR: MC with the muon fake-rate factor k = 1.3 (stat errors only)", "",
         "| selection | data | MC nominal | Nonprompt x k | Nonprompt + TT x k |", "|---|---|---|---|---|"]
fig, axs = plt.subplots(2, 2, figsize=(13, 7.2), gridspec_kw={"height_ratios": [2.2, 1]}, sharex="col")
V0 = [("MC (nominal)", [], "#222222", "-"), ("Nonprompt × 1.3", ["Nonprompt"], "#3f9c5a", "--"),
     ("Nonprompt + tt̄ × 1.3", ["Nonprompt", "TT"], "#8a4fbf", ":")]
comp = []
for col, cs in enumerate(["OS", "SS"]):
    lo, hi, d, n, e = load(cs)
    # TT in OS is prompt ttbar: only the SS TT (b-hadron leptons) is a fake candidate
    V = V0 if cs == "SS" else [v if "tt̄" not in v[0] else (v[0] + " (SS only)", ["Nonprompt"], v[2], v[3]) for v in V0]
    x = np.arange(len(lo)); ax, rx = axs[0, col], axs[1, col]
    base = np.zeros(len(x))
    for g in G:
        ax.bar(x, n[g], bottom=base, width=0.96, color=COL[g], label=LAB[g], linewidth=0); base += n[g]
    tot0, err0 = variant(n, e, [])
    for lab, sc, c, ls in V[1:]:
        if "SS only" in lab: continue
        t, _ = variant(n, e, sc)
        ax.step(np.r_[x - 0.5, x[-1] + 0.5], np.r_[t, t[-1]], where="post", color=c, lw=2, ls=ls, label=lab)
    ax.errorbar(x, d, np.sqrt(d), fmt="o", color="k", ms=4, label="Data", zorder=5)
    ax.set_yscale("log"); ax.set_ylabel("Events / bin"); ax.set_title(f"Resolved eμ flavour CR, {cs}", loc="left", fontsize=11)
    ax.legend(fontsize=8, ncol=2, frameon=False)
    ax.set_ylim(0.1 if cs == "SS" else 1, max(d.max(), base.max()) * 30)
    for lab, sc, c, ls in V:
        t, er = variant(n, e, sc)
        with np.errstate(divide="ignore", invalid="ignore"):
            r = np.where(t > 0, d / t, np.nan); re = np.where(t > 0, np.sqrt(d) / t, np.nan)
            band = np.where(t > 0, er / t, np.nan)
        off = {"MC (nominal)": -0.2, "Nonprompt × 1.3": 0.0}.get(lab, 0.2)
        if cs == "OS" and "SS only" in lab: continue
        rx.errorbar(x + off, r, re, fmt="o", ms=3.5, color=c, label=lab)
        if not sc:
            rx.fill_between(np.r_[x - 0.5, x[-1] + 0.5], np.r_[1 - band, 1 - band[-1]], np.r_[1 + band, 1 + band[-1]],
                            step="post", color="#999999", alpha=0.35, lw=0, label="MC stat (nominal)")
        D, T, E = d.sum(), t.sum(), np.sqrt((er ** 2).sum())
        if col == 0 and lab == "MC (nominal)": pass
    rx.axhline(1, color="#666666", lw=0.8); rx.set_ylabel("Data / MC"); rx.set_ylim(0.5, 3.5 if cs == "SS" else 1.6)
    rx.set_xticks(x); rx.set_xticklabels([f"{a:.0f}–{b:.0f}" if b < 8000 else f"{a:.0f}+" for a, b in zip(lo, hi)], rotation=40, fontsize=8)
    rx.set_xlabel("m(lljj) bin (GeV)"); rx.legend(fontsize=7, ncol=2, frameon=False, loc="upper left")
    row = [cs, f"{d.sum():.0f}"]
    for lab, sc, c, ls in V:
        t, er = variant(n, e, sc); T = t.sum(); E = np.sqrt((er ** 2).sum())
        row.append(f"{T:.1f} ± {E:.1f} (data/MC {d.sum() / T:.3f} ± {np.sqrt(d.sum()) / T:.3f})")
    lines.append("| " + " | ".join(row) + " |")
    comp.append(f"{cs} composition: " + ", ".join(f"{g} {n[g].sum():.1f}" for g in G))
lines += ["", "OS: TT is prompt ttbar, so the last column applies k to Nonprompt only (same as the middle column).", ""] + comp
fig.tight_layout(); fig.savefig(f"{OUT}/emu_fakek_mlljj.png", dpi=140)
md = "\n".join(lines) + "\n"; open(f"{OUT}/emu_fakek.md", "w").write(md); print(md)
