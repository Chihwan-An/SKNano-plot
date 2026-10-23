#!/usr/bin/env python3
"""2026-10-02: background N_eff of the four resolved SRs (EE SS, EE OS, MM SS, MM OS) with the inputs of the nominal
cards cbv15_an2_ref_v3_ss3200, as a check of the binning rule (tail N_eff >= 10).

N_eff = (sum w)^2 / sum w^2 of the total background (variances of all processes added).
  tail N_eff(E) : events with m_lljj in [E, 8000]  (the "last bin" if the last edge were E)
  bin N_eff     : per bin of the current v3_ss3200 binning

Inputs (1 GeV, 800-8000):
  EE OS, MM OS, MM SS : BDT/SR/test/cbv15dc/shapes_2024_dc{,_mm}.root  (DYJets, TT, Nonprompt, Others MC)
  EE SS               : nominal data-driven template rebuilt event by event as chargeflip_ddss_dyonly.py
                        --sf2 --dy-only --json chargeflip_ptshift_ee2024_sf3roofit.json (= v3_ss3200):
                        Flip = OS data x w - OS non-DY MC x w (variance of both added), DY non-flip SS MC,
                        TT/Nonprompt/Others full SS MC x flip SF on gen-flipped electrons.
                        Reference: MC-only SS (rEESR_SS_2e + rEESR_SS_lt2 of shapes_2024_dc.root).
Runs without ROOT (uproot + numpy; ROOT is stubbed for the import of chargeflip_ddss_dyonly).
  --total-only : total background only (output *_total.{png,pdf,json}).
"""
import json, os, sys, types
import numpy as np
import uproot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers"
SRT = f"{REPO}/BDT/SR/test"
SCEN = f"{REPO}/BDT/combine/scenarios/test/cbv15_an2_ref_v3_ss3200/shapes_2024_cbv15_an2_ref_v3_ss3200.root"
sys.modules.setdefault("ROOT", types.ModuleType("ROOT"))
sys.path.insert(0, f"{REPO}/plot/cutbased/studies/ttbar/07_ss_dyonly_flip")
import chargeflip_ddss_dyonly as M  # noqa: E402

E1 = np.arange(800, 8001, 1.0)
MCG = ["DYJets", "TT", "Nonprompt", "Others"]
COL = {"Flip": "#AA3377", "DYJets": "#DDAA33", "TT": "#CC3311", "Nonprompt": "#228833", "Others": "#888888"}


def from_shapes(path, reg, groups=MCG):
    f = uproot.open(path); out = {}
    for g in groups:
        h = f[f"{reg}/{g}"]
        assert np.allclose(h.axis().edges(), E1), (path, reg, g)
        out[g] = (h.values().astype(float), h.variances().astype(float))
    return out


def ee_ss_datadriven():
    J = json.load(open(f"{SRT}/data/chargeflip/chargeflip_ptshift_ee2024_sf3roofit.json"))
    d = M.load(f"{SRT}/data/chargeflip/dumps_v4/all")
    w_all, _ = M.new_weights(J, d, sf2=True); sfw = M.flip_sf_weight(J, d, sf2=True)
    isdata = d["grp"] == "DATA"; sel = M.SEL["rEESR_SS"](d); x = d["m_lljj"]
    os_ = sel & isdata & ~d["ss"]
    sub = sel & ~isdata & ~d["ss"] & ~np.isin(d["grp"], ["DY", "SIG"])
    v, e = M.fill(x[os_], w_all[os_], E1)
    vs, es = M.fill(x[sub], w_all[sub] * d["weight"][sub], E1)
    out = {"Flip": (v - vs, e + es)}          # unclipped: the clip of the cards acts on the coarse bins only
    nonflip = sel & ~isdata & d["ss"] & ~(d["l1_flip"] | d["l2_flip"]); allss = sel & ~isdata & d["ss"]
    for g, proc in M.GROUP.items():
        m = (nonflip if g == "DY" else allss) & (d["grp"] == g)
        out[proc] = M.fill(x[m], d["weight"][m] * sfw[m], E1)
    return out


def tail(a):  # sum over [E_i, 8000] for every lower edge E_i (i = 0..7199)
    return np.cumsum(a[::-1])[::-1]


def neff(s, v):
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(v > 0, s * s / v, 0.0)


def rebin(a, edges):
    idx = np.searchsorted(E1, edges); return np.add.reduceat(a, idx[:-1])[: len(edges) - 1]


REGS = [("rEESR_SS", "EE SS (data-driven flip, nominal)"), ("rEESR_OS", "EE OS"),
        ("rMuMuSR_SS", "MuMu SS"), ("rMuMuSR_OS", "MuMu OS")]

if __name__ == "__main__":
    TOTAL_ONLY = "--total-only" in sys.argv   # no per-process / MC-only reference curves
    SUF = "_total" if TOTAL_ONLY else ""
    P = {"rEESR_SS": ee_ss_datadriven(),
         "rEESR_OS": from_shapes(f"{SRT}/cbv15dc/shapes_2024_dc.root", "rEESR_OS"),
         "rMuMuSR_SS": from_shapes(f"{SRT}/cbv15dc/shapes_2024_dc_mm.root", "rMuMuSR_SS"),
         "rMuMuSR_OS": from_shapes(f"{SRT}/cbv15dc/shapes_2024_dc_mm.root", "rMuMuSR_OS")}
    a = from_shapes(f"{SRT}/cbv15dc/shapes_2024_dc.root", "rEESR_SS_2e"); b = from_shapes(f"{SRT}/cbv15dc/shapes_2024_dc.root", "rEESR_SS_lt2")
    ref_ee_ss_mc = {g: (a[g][0] + b[g][0], a[g][1] + b[g][1]) for g in MCG}
    card = uproot.open(SCEN)

    res = {}; fig, axs = plt.subplots(2, 2, figsize=(13, 9.5), sharex=True)
    for ax, (reg, lab) in zip(axs.flat, REGS):
        pr = P[reg]; S = sum(v for v, _ in pr.values()); V = sum(e for _, e in pr.values())
        ts, tv = tail(S), tail(V); nt = neff(ts, tv)
        edges = [float(e) for e in card[f"{reg}/data_obs"].axis().edges()]
        # check against the card templates (yield per card bin)
        cb = sum(card[f"{reg}/{p}"].values() for p in pr if f"{p}" in [k.split(";")[0] for k in card[reg].keys()])
        mine = rebin(S, edges)
        ax.plot(E1[:-1], nt, color="k", lw=2, label="total background")
        for p, (v, e) in ([] if TOTAL_ONLY else pr.items()):
            if abs(v.sum()) > 0: ax.plot(E1[:-1], neff(tail(v), tail(e)), color=COL[p], lw=1, ls="--", label=p)
        if reg == "rEESR_SS" and not TOTAL_ONLY:
            Sm = sum(v for v, _ in ref_ee_ss_mc.values()); Vm = sum(e for _, e in ref_ee_ss_mc.values())
            ax.plot(E1[:-1], neff(tail(Sm), tail(Vm)), color="tab:blue", lw=1.5, ls=":", label="MC-only SS (reference)")
        ax.axhline(10, color="tab:red", lw=1); ax.text(7900, 11, r"$N_\mathrm{eff}=10$", color="tab:red", ha="right", fontsize=9)
        for x0 in edges[1:-1]: ax.axvline(x0, color="0.75", lw=0.8, zorder=0)
        # per-bin N_eff of the current binning, drawn as horizontal segments
        bs, bv = rebin(S, edges), rebin(V, edges); bn = neff(bs, bv)
        for lo, hi, n in zip(edges[:-1], edges[1:], bn):
            ax.hlines(max(n, 0.11), lo, hi, color="tab:orange", lw=3, zorder=3)
        ax.plot([], [], color="tab:orange", lw=3, label="per bin (v3_ss3200 binning)")
        ok = np.where(nt >= 10)[0]; e10 = float(E1[ok.max()]) if len(ok) else float("nan")
        drop = np.where(nt < 10)[0]; first = float(E1[drop.min() - 1]) if len(drop) else float("nan")
        ax.axvline(first, color="tab:red", ls=":", lw=1.4)
        # tail sum of weights (background events above E) on the right axis; mark sum w = 1
        ax2 = ax.twinx(); ax2.plot(E1[:-1], ts, color="tab:blue", lw=1.6, alpha=0.8)
        ax2.set_yscale("log"); ax2.set_ylim(1e-3, 1e4); ax2.tick_params(axis="y", colors="tab:blue")
        ax2.set_ylabel(r"tail $\sum w$ (bkg events in $[E, 8\,\mathrm{TeV}]$)", color="tab:blue", fontsize=9)
        ax2.axhline(1, color="tab:blue", lw=0.8, ls="--")
        b1 = np.where(ts < 1)[0]; e_w1 = float(E1[b1.min()]) if len(b1) else float("nan")
        ax.axvline(e_w1, color="tab:blue", ls="-.", lw=1.4)
        ax.set_yscale("log"); ax.set_ylim(0.1, 1e5); ax.set_xlim(800, 8000)
        ax.set_title(f"{lab}\nNeff<10 from E = {first:.0f} (red)    tail $\\sum w$<1 from E = {e_w1:.0f} GeV (blue)", fontsize=10.5)
        ax.set_ylabel(r"$N_\mathrm{eff}$ of $[E, 8\,\mathrm{TeV}]$"); ax.grid(alpha=0.3, which="both", lw=0.4)
        res[reg] = {"edges": edges, "bin_yield": [round(float(x), 4) for x in bs], "bin_neff": [round(float(x), 2) for x in bn],
                    "card_bin_yield": [round(float(x), 4) for x in cb], "highest_E_tail_neff_ge10": e10,
                    "first_drop_E": first, "tail_sumw_lt1_E": e_w1, "tail_neff_at": {str(E): round(float(nt[int(E - 800)]), 2) for E in
                                                            (2000, 2400, 2800, 3200, 3500, 4000, 4500, 5000, 5500)},
                    "tail_yield_at": {str(E): round(float(ts[int(E - 800)]), 3) for E in (2400, 2800, 3200, 4000, 5000)}}
    for ax in axs[1]: ax.set_xlabel(r"lower edge $E$ = $m_{\ell\ell jj}$ [GeV]")
    axs[0, 0].plot([], [], color="tab:blue", lw=1.6, label=r"tail $\sum w$ (right axis)")
    axs[0, 0].legend(fontsize=8, loc="upper right")
    fig.suptitle("Resolved SR background $N_\\mathrm{eff} = (\\sum w)^2/\\sum w^2$, 2024, inputs of cbv15_an2_ref_v3_ss3200", fontsize=12)
    fig.tight_layout()
    for ext in ("png", "pdf"): fig.savefig(f"{HERE}/sr_neff_resolved_2024{SUF}.{ext}", dpi=130)
    json.dump(res, open(f"{HERE}/sr_neff_resolved_2024{SUF}.json", "w"), indent=1)
    for r, v in res.items():
        print(f"== {r}: tail Neff>=10 up to {v['highest_E_tail_neff_ge10']:.0f} (first drop {v['first_drop_E']:.0f}); tail sum w < 1 from {v['tail_sumw_lt1_E']:.0f}")
        print("   edges     ", [int(e) for e in v["edges"]])
        print("   bin yield ", v["bin_yield"]); print("   card yield", v["card_bin_yield"]); print("   bin Neff  ", v["bin_neff"])
        print("   tail Neff ", v["tail_neff_at"]); print("   tail B    ", v["tail_yield_at"])
