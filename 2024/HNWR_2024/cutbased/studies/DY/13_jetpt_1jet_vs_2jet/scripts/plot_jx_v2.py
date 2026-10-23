#!/usr/bin/env python3
"""One-jet vs two-jet jet-pT correction, v2 (2026-09-25). OS, stat errors only, DY without R (`_noR`).

Normalisation: the quick local run used a few files per sample. Each MC sample is scaled by k_s = (full-production
Central/DYCR_Resolved_MM_OS_mlljj yield) / (local JX_MM_2j_mll60to150 yield with R) -- the same selection (resolved,
OS, 60<m_ll<150, m(lljj)>800) -- falling back to the ee channel and then to the file ratio when the MM yield is tiny.
Data (period G subset) is scaled per stream the same way. nonDY = ttbar/tW + VV/ttV (W+jets not run).

Selections: 2j (resolved, m(lljj)>800), 1j (one AK4, no AK8, m(llj)>800), 1jall (one AK4, no AK8, no mass cut).
Transfers, each with (i) R_src in the analysis R bins (40/100/200/400/600/800/2000) applied as is and (ii) R_src in fine
bins (= the jet-pT MC shape corrected bin by bin):
  2j, 1j, 1jall : m_ll 60-100 -> 100-150      (1j/1jall for comparison with the 2j closure)
  1j, 1jall     : m_ll 60-150 -> > 400        (the SR direction; two jets there is the blinded SR)
  2j            : m_ll 60-150 -> 150-400      (two-jet reference in the same direction, data allowed)
Plus R(jet pT) in m_ll 60-150 for 2j / 1j / 1jall overlaid.
"""
import glob, os
import numpy as np
import uproot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

IN = "/gv0/Users/achihwan/SKNanoOutput_jetxcheck"
FULLP = "/gv0/Users/achihwan/SKNanoOutput/HNWR/RFlav_DYCRCharge_SRChargeSplit_ZptNJet_FlipSF/2024"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plots_v2")
os.makedirs(OUT, exist_ok=True)
XB = np.array([40, 60, 80, 100, 125, 150, 200, 250, 300, 400, 500, 600, 800, 2000.])
RB = np.array([40, 100, 200, 400, 600, 800, 2000.])
CI = np.searchsorted(RB, XB[:-1], side="right") - 1


def group(s):
    b = s.replace("Skim_HNWR_", "")
    if b.startswith("DYto2L"): return "DY"
    if b.startswith(("Muon",)): return "dataMM"
    if b.startswith(("EGamma",)): return "dataEE"
    if b.startswith(("TTto2L2Nu", "TWminusto2L2Nu", "TbarWplusto2L2Nu")): return "TT"
    return "Others"


def local_sum(d, name):
    t = 0.0
    for f in glob.glob(f"{d}/hists_*.root"):
        try: t += uproot.open(f)[f"Central/{name}"].values().sum()
        except Exception: pass
    return t


def full_sum(sample, ch):
    t = 0.0
    for f in glob.glob(f"{FULLP}/{sample}.root") + glob.glob(f"{FULLP}/{sample}_p[0-9][0-9].root"):
        try: t += uproot.open(f)[f"Central/DYCR_Resolved_{ch}_OS_mlljj"].values().sum()
        except Exception: pass
    return t


SAMPLES = {}   # dir -> (group, scale)
LOG = []
data_local = {"dataMM": 0.0, "dataEE": 0.0}
for d in sorted(glob.glob(f"{IN}/Skim_HNWR_*")):
    s = os.path.basename(d); g = group(s)
    if not glob.glob(f"{d}/hists_*.root"): continue
    if g.startswith("data"):
        ch = g[-2:]; data_local[g] += local_sum(d, f"JX_{ch}_2j_mll60to150_M"); SAMPLES[d] = (g, None); continue
    k = None
    for ch in ("MM", "EE"):
        loc = local_sum(d, f"JX_{ch}_2j_mll60to150_M"); ful = full_sum(s, ch)
        if loc > 0 and ful > 0 and ful > 0.05 * max(1.0, loc):
            k = ful / loc; src = ch; break
    tot, used = map(int, open(f"{d}/scale.txt").read().split())
    if k is None: k, src = tot / used, "files"
    SAMPLES[d] = (g, k); LOG.append(f"{s:60s} {g:7s} k = {k:9.3f}  ({src}; file ratio {tot / used:.2f})")
DATA_FULL = {"dataMM": sum(full_sum(f"Skim_HNWR_Muon{i}_{p}", "MM") for i in (0, 1) for p in "C D E F G H I I_v2".split()),
             "dataEE": sum(full_sum(f"Skim_HNWR_EGamma{i}_{p}", "EE") for i in (0, 1) for p in "C D E F G H I I_v2".split())}
for d, (g, k) in list(SAMPLES.items()):
    if g.startswith("data"): SAMPLES[d] = (g, DATA_FULL[g] / data_local[g])
LOG += [f"data scale MM {DATA_FULL['dataMM'] / data_local['dataMM']:.3f}, EE {DATA_FULL['dataEE'] / data_local['dataEE']:.3f}"]

C = {}


def hist(g, name):
    if (g, name) in C: return C[(g, name)]
    v = np.zeros(len(XB) - 1); e2 = np.zeros(len(XB) - 1)
    for d, (gg, k) in SAMPLES.items():
        if gg != g: continue
        for f in glob.glob(f"{d}/hists_*.root"):
            try: h = uproot.open(f)[f"Central/{name}"]
            except Exception: continue
            x = h.axis().edges(); idx = np.digitize(0.5 * (x[:-1] + x[1:]), XB) - 1; ok = (idx >= 0) & (idx < len(v))
            np.add.at(v, idx[ok], h.values()[ok] * k); np.add.at(e2, idx[ok], h.variances()[ok] * k * k)
    C[(g, name)] = (v, e2); return v, e2


def parts(ch, sel, win):
    n = f"JX_{ch}_{sel}_{win}_j1pt_noR"
    d = hist(f"data{ch}", n); y = hist("DY", n); t = hist("TT", n); o = hist("Others", n)
    return d, y, (t[0] + o[0], t[1] + o[1])


def R_of(d, y, nd, coarse=False):
    (dv, de), (yv, ye), (nv, ne) = d, y, nd
    if coarse:
        cs = lambda v: np.array([v[CI == k].sum() for k in range(len(RB) - 1)])
        dv, de, yv, ye, nv, ne = cs(dv), cs(de), cs(yv), cs(ye), cs(nv), cs(ne)
    with np.errstate(divide="ignore", invalid="ignore"):
        R = (dv - nv) / yv; eR = np.sqrt(de + ne + R ** 2 * ye) / yv
    return (R[CI], eR[CI]) if coarse else (R, eR)


def transfer(ch, sel, src, dst):
    ds, ys, ns = parts(ch, sel, src); dd, yd, nd = parts(ch, sel, dst)
    out = {}
    for tag, coarse in (("i", True), ("ii", False)):
        R, eR = R_of(ds, ys, ns, coarse)
        with np.errstate(divide="ignore", invalid="ignore"):
            Rr = np.where(np.isfinite(R), R, np.nan)
            p = nd[0] + Rr * yd[0]; ep = np.sqrt(nd[1] + Rr ** 2 * yd[1] + (yd[0] * np.nan_to_num(eR)) ** 2)
            q = dd[0] / p; eq = np.abs(q) * np.sqrt(dd[1] / dd[0] ** 2 + (ep / p) ** 2)
        ok = np.isfinite(q) & (dd[0] > 5)
        out[tag] = (q, eq, ok, np.sum(((q - 1) / eq)[ok] ** 2), dd[0].sum() / np.nansum(np.where(ok | (dd[0] <= 5), p, 0)))
    with np.errstate(divide="ignore", invalid="ignore"):
        q0 = dd[0] / (nd[0] + yd[0])
    out["none"] = (q0, dd[0].sum() / (nd[0] + yd[0]).sum())
    return out, dd[0], yd[0].sum() / max((yd[0] + nd[0]).sum(), 1e-9)


x = 0.5 * (XB[:-1] + XB[1:]); xe = 0.5 * np.diff(XB)
L = ["# one-jet vs two-jet jet-pT correction, v2 (per-sample normalisation from the full production), OS, stat only", "", "```"] + LOG + ["```", ""]
CASES = [("2j", "mll60to100", "mll100to150", "2 jets: 60–100 → 100–150"),
         ("1j", "mll60to100", "mll100to150", "1 jet m(llj)>800: 60–100 → 100–150"),
         ("1jall", "mll60to100", "mll100to150", "1 jet no mass cut: 60–100 → 100–150"),
         ("2j", "mll60to150", "mll150to400", "2 jets: 60–150 → 150–400"),
         ("1j", "mll60to150", "mll400", "1 jet m(llj)>800: 60–150 → >400"),
         ("1jall", "mll60to150", "mll400", "1 jet no mass cut: 60–150 → >400")]
fig, axs = plt.subplots(len(CASES), 2, figsize=(13, 3.1 * len(CASES)), sharex=True)
for c, ch in enumerate(["EE", "MM"]):
    L += [f"## {ch}", "", "| case | dst data | DY frac | total: none / (i) / (ii) | chi2 (i) | chi2 (ii) |", "|---|---|---|---|---|---|"]
    rows = []
    for r, (sel, src, dst, lab) in enumerate(CASES):
        o, dd, fdy = transfer(ch, sel, src, dst); ax = axs[r, c]
        for tag, col, mk, off in (("i", "#1d4ed8", "s", -0.02), ("ii", "#c2410c", "o", 0.02)):
            q, eq, ok, chi2, tot = o[tag]
            ax.errorbar(x * (1 + off), np.where(ok, q, np.nan), np.where(ok, eq, np.nan), fmt=mk, color=col, ms=4, mfc="none" if tag == "i" else col,
                        label=("(i) coarse R as is" if tag == "i" else "(ii) + MC shape per fine bin") + f": total {tot:.3f}, χ² {chi2:.1f}/{ok.sum()}")
        ax.plot(x, np.where(dd > 5, o["none"][0], np.nan), "x", color="#9ca3af", alpha=0.6, label=f"no R: total {o['none'][1]:.3f}")
        ax.axhline(1, color="gray", lw=0.8); ax.set_xscale("log"); ax.set_xlim(40, 2000); ax.set_ylim(0.3, 2.3)
        ax.set_title(f"{'ee' if ch == 'EE' else 'μμ'} — {lab} (data {dd.sum():.0f}, DY {fdy:.0%})", loc="left", fontsize=9)
        ax.set_ylabel("data / pred"); ax.legend(fontsize=6.5, loc="upper right")
        L.append(f"| {lab} | {dd.sum():.0f} | {fdy:.0%} | {o['none'][1]:.3f} / {o['i'][4]:.3f} / {o['ii'][4]:.3f} | {o['i'][3]:.1f}/{o['i'][2].sum()} | {o['ii'][3]:.1f}/{o['ii'][2].sum()} |")
        rows.append((lab, o, dd))
    L.append("")
    for lab, o, dd in rows:
        L.append(f"{lab}, per bin (i) / (ii): " + ", ".join(f"{XB[i]:.0f}: {o['i'][0][i]:.2f}/{o['ii'][0][i]:.2f}±{o['ii'][1][i]:.2f}"
                                                           for i in range(len(x)) if o["ii"][2][i]))
    L.append("")
for ax in axs[-1]: ax.set_xlabel("leading jet pT (GeV)")
fig.tight_layout(); fig.savefig(f"{OUT}/transfers_i_vs_ii.png", dpi=120); plt.close(fig)

# R overlay in m_ll 60-150
figR, axR = plt.subplots(2, 2, figsize=(13, 8), gridspec_kw={"height_ratios": [1.3, 1]}, sharex=True)
for c, ch in enumerate(["EE", "MM"]):
    L += [f"## {ch}: R(jet pT) = (data - nonDY)/DY, m_ll 60-150", "", "| sel | " + " | ".join(f"{XB[i]:.0f}-{XB[i+1]:.0f}" for i in range(len(x))) + " |", "|---" * (len(x) + 1) + "|"]
    ref = None
    for k, (sel, lab, col, mk) in enumerate([("2j", "2 jets, m(lljj)>800", "#1d4ed8", "s"), ("1j", "1 jet, m(llj)>800", "#c2410c", "o"),
                                              ("1jall", "1 jet, no mass cut", "#7c3aed", "D")]):
        R, eR = R_of(*parts(ch, sel, "mll60to150"))
        if ref is None: ref = (R, eR)
        axR[0, c].errorbar(x * (1 + 0.02 * (k - 1)), R, np.abs(eR), fmt=mk, color=col, ms=4, label=lab)
        if k:
            with np.errstate(divide="ignore", invalid="ignore"):
                rr = R / ref[0]; err = np.abs(rr) * np.sqrt((eR / R) ** 2 + (ref[1] / ref[0]) ** 2)
            axR[1, c].errorbar(x * (1 + 0.02 * (k - 1)), rr, err, fmt=mk, color=col, ms=4, label=lab)
        L.append(f"| {sel} | " + " | ".join(f"{a:.2f}±{abs(b):.2f}" if np.isfinite(a) else "-" for a, b in zip(R, eR)) + " |")
    axR[0, c].set_xscale("log"); axR[0, c].set_xlim(40, 2000); axR[0, c].set_ylim(0.3, 3); axR[0, c].set_ylabel("(data − nonDY)/DY"); axR[0, c].legend(fontsize=8)
    axR[0, c].set_title(f"{'ee' if ch == 'EE' else 'μμ'} OS, m(ll) 60–150, DY without R", loc="left", fontsize=10)
    axR[1, c].axhline(1, color="gray", lw=0.8); axR[1, c].set_ylim(0.4, 1.8); axR[1, c].set_ylabel("R / R(2 jets)"); axR[1, c].set_xlabel("leading jet pT (GeV)")
    axR[1, c].legend(fontsize=8); L.append("")
figR.tight_layout(); figR.savefig(f"{OUT}/R_1jet_vs_2jet.png", dpi=130)
open(f"{OUT}/summary.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
