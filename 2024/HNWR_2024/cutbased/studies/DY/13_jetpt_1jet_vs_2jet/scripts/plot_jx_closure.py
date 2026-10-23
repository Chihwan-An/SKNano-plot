#!/usr/bin/env python3
"""(a) jet-pT correction R(jet pT) = (data - nonDY)/DY measured with one jet vs two jets, and (b) the CR1 (m_ll 60-100) ->
CR2 (100-150) bin-by-bin closure for each selection. OS, stat errors only, DY without R (`_noR`).

Selections (HNWR userflag JetXcheck, quick local run):
  2j     resolved two-jet, m(lljj) > 800            (= the DY CR the analysis R comes from)
  1j     exactly one AK4 jet, no AK8, m(llj) > 800
  1jall  exactly one AK4 jet, no AK8, no mass cut
  2jall  resolved two-jet, no mass cut
Data = period G subset; it is scaled per channel by one global factor so that the two-jet OS DY CR (m_ll 60-150, m(lljj) > 800)
matches the full production (EE 35120, MM 52218 events). The closure ratios hardly depend on that factor (nonDY ~1-6 %).
nonDY = ttbar + tW only (VV, W+jets not in the quick run).
"""
import glob, os
import numpy as np
import uproot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

IN = "/gv0/Users/achihwan/SKNanoOutput_jetxcheck"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plots")
FULL = {"EE": 35120.0, "MM": 52218.0}
XB = np.array([40, 60, 80, 100, 125, 150, 200, 250, 300, 400, 500, 600, 800, 2000.])
SELS = [("2j", "2 jets, m(lljj)>800", "#1d4ed8", "s"), ("1j", "1 jet, m(llj)>800", "#c2410c", "o"),
        ("1jall", "1 jet, no mass cut", "#7c3aed", "D"), ("2jall", "2 jets, no mass cut", "#0f766e", "^")]
RFILE = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/HNWR/data/corrections/jetpt/zptnjet/dy_jetpt_ratio.root"


def groups(g):
    if g == "DY": return sorted(glob.glob(f"{IN}/Skim_HNWR_DYto2L-4Jets_*"))
    if g == "TT": return [f"{IN}/{s}" for s in ["Skim_HNWR_TTto2L2Nu_TuneCP5", "Skim_HNWR_TWminusto2L2Nu", "Skim_HNWR_TbarWplusto2L2Nu"]]
    if g == "dataMM": return [f"{IN}/Skim_HNWR_Muon0_G", f"{IN}/Skim_HNWR_Muon1_G"]
    if g == "dataEE": return [f"{IN}/Skim_HNWR_EGamma0_G", f"{IN}/Skim_HNWR_EGamma1_G"]


C = {}


def hist(g, name):
    if (g, name) in C: return C[(g, name)]
    v = np.zeros(len(XB) - 1); e2 = np.zeros(len(XB) - 1)
    for d in groups(g):
        sc = 1.0
        if not g.startswith("data"):
            tot, used = map(int, open(f"{d}/scale.txt").read().split()); sc = tot / used
        for f in glob.glob(f"{d}/hists_*.root"):
            try: h = uproot.open(f)[f"Central/{name}"]
            except Exception: continue
            x = h.axis().edges(); idx = np.digitize(0.5 * (x[:-1] + x[1:]), XB) - 1; ok = (idx >= 0) & (idx < len(v))
            np.add.at(v, idx[ok], h.values()[ok] * sc); np.add.at(e2, idx[ok], h.variances()[ok] * sc * sc)
    C[(g, name)] = (v, e2); return v, e2


def comp(ch, sel, win, fdata):
    n = f"JX_{ch}_{sel}_{win}_j1pt_noR"
    d, ed = hist(f"data{ch}", n); y, ey = hist("DY", n); t, et = hist("TT", n)
    return d * fdata, ed * fdata ** 2, y, ey, t, et


def Rof(d, ed, y, ey, t, et):
    with np.errstate(divide="ignore", invalid="ignore"):
        R = (d - t) / y; eR = np.sqrt(ed + et + R ** 2 * ey) / y
    return R, eR


def read_R(ch):
    try:
        h = uproot.open(RFILE)[f"resolved_{ch}/2024/rebinned/R_nominal"]; return h.axis().edges(), h.values(), h.errors()
    except Exception:
        return None


x = 0.5 * (XB[:-1] + XB[1:]); xe = 0.5 * np.diff(XB)
L = ["# jet-pT correction with one vs two jets, and CR1 -> CR2 closure per selection (OS, stat only, quick local run)", ""]
figR, axR = plt.subplots(2, 2, figsize=(13, 8.5), gridspec_kw={"height_ratios": [1.3, 1]}, sharex=True)
figC, axC = plt.subplots(1, 2, figsize=(13, 4.8))
for c, ch in enumerate(["EE", "MM"]):
    dG = hist(f"data{ch}", f"JX_{ch}_2j_mll60to150_j1pt_noR")[0].sum()
    f = FULL[ch] / dG
    L += [f"## {ch}  (data scale {f:.3f} = {FULL[ch]:.0f} / {dG:.0f})", ""]
    ref = None
    L += ["### R(jet pT) = (data - ttbar/tW) / DY, m_ll 60-150", "",
          "| selection | data | " + " | ".join(f"{XB[i]:.0f}-{XB[i+1]:.0f}" for i in range(len(x))) + " |", "|---" * (len(x) + 2) + "|"]
    for sel, lab, col, mk in SELS:
        d, ed, y, ey, t, et = comp(ch, sel, "mll60to150", f)
        R, eR = Rof(d, ed, y, ey, t, et)
        if sel == "2j": ref = (R, eR)
        axR[0, c].errorbar(x * (1 + 0.02 * (SELS.index((sel, lab, col, mk)) - 1.5)), R, np.abs(eR), fmt=mk, color=col, ms=4, label=lab)
        with np.errstate(divide="ignore", invalid="ignore"):
            rr = R / ref[0]; err = rr * np.sqrt((eR / R) ** 2 + (ref[1] / ref[0]) ** 2)
        if sel != "2j":
            axR[1, c].errorbar(x * (1 + 0.02 * (SELS.index((sel, lab, col, mk)) - 1.5)), rr, np.abs(err), fmt=mk, color=col, ms=4, label=lab)
        L.append(f"| {sel} | {d.sum():.0f} | " + " | ".join(f"{a:.2f}±{b:.2f}" if np.isfinite(a) else "-" for a, b in zip(R, eR)) + " |")
    rf = read_R(ch)
    if rf:
        e, v, s = rf; m = np.isfinite(v) & (v > 0)
        axR[0, c].step(np.r_[e[:-1][m], e[1:][m][-1]], np.r_[v[m], v[m][-1]], where="post", color="k", lw=1, ls="--", label="analysis R (full prod.)")
    axR[0, c].set_xscale("log"); axR[0, c].set_ylim(0.3, 3.0); axR[0, c].set_ylabel("(data − tt̄/tW) / DY")
    axR[0, c].set_title(f"{'ee' if ch == 'EE' else 'μμ'} OS, m(ll) 60–150, DY without R", loc="left", fontsize=10); axR[0, c].legend(fontsize=7)
    axR[1, c].axhline(1, color="gray", lw=0.8); axR[1, c].set_ylim(0.4, 1.8); axR[1, c].set_ylabel("R / R(2 jets, m(lljj)>800)")
    axR[1, c].set_xlabel("leading jet pT (GeV)"); axR[1, c].legend(fontsize=7)
    L.append("")
    # closure CR1 -> CR2
    L += ["### CR1 (60-100) -> CR2 (100-150): CR2 data / (ttbar/tW + R_CR1 x DY)", "",
          "| selection | CR2 data | total before -> after | chi2/bins | " + " | ".join(f"{XB[i]:.0f}-{XB[i+1]:.0f}" for i in range(len(x))) + " |",
          "|---" * (len(x) + 4) + "|"]
    for k, (sel, lab, col, mk) in enumerate(SELS):
        d1, ed1, y1, ey1, t1, et1 = comp(ch, sel, "mll60to100", f)
        d2, ed2, y2, ey2, t2, et2 = comp(ch, sel, "mll100to150", f)
        R1, eR1 = Rof(d1, ed1, y1, ey1, t1, et1)
        with np.errstate(divide="ignore", invalid="ignore"):
            Rr = np.where(np.isfinite(R1), R1, 1.0)
            pa = t2 + Rr * y2; epa = np.sqrt(et2 + Rr ** 2 * ey2 + (y2 * np.nan_to_num(eR1)) ** 2)
            ra = d2 / pa; era = ra * np.sqrt(ed2 / d2 ** 2 + (epa / pa) ** 2)
        ok = np.isfinite(ra) & (d2 > 5)
        chi2 = np.sum(((ra - 1) / era)[ok] ** 2)
        axC[c].errorbar(x * (1 + 0.02 * (k - 1.5)), np.where(ok, ra, np.nan), np.where(ok, np.abs(era), np.nan), fmt=mk, color=col, ms=4,
                        label=f"{lab}  χ² {chi2:.1f}/{ok.sum()}")
        L.append(f"| {sel} | {d2.sum():.0f} | {d2.sum() / (t2 + y2).sum():.3f} -> {d2.sum() / pa.sum():.3f} | {chi2:.1f}/{ok.sum()} | "
                 + " | ".join(f"{a:.2f}±{b:.2f}" if o else "-" for a, b, o in zip(ra, era, ok)) + " |")
    axC[c].axhline(1, color="gray", lw=0.8); axC[c].set_xscale("log"); axC[c].set_ylim(0.4, 1.8)
    axC[c].set_xlabel("leading jet pT (GeV)"); axC[c].set_ylabel("CR2 data / (MC with R from CR1)")
    axC[c].set_title(f"{'ee' if ch == 'EE' else 'μμ'} OS: R from m(ll) 60–100 applied to 100–150", loc="left", fontsize=10); axC[c].legend(fontsize=7)
    L.append("")
# ---------------- 1j -> 2j transfer, 2-jet DY CR (m_ll 60-150, m(lljj) > 800) data
RB = np.array([40, 100, 200, 400, 600, 800, 2000.])
cidx = np.searchsorted(RB, XB[:-1], side="right") - 1
figT, axT = plt.subplots(2, 2, figsize=(13, 8))
L += ["## 1-jet R transported to the 2-jet DY CR (m_ll 60-150, m(lljj)>800)", "",
      "A = R_1j in the analysis R bins (40/100/200/400/600/800/2000) applied as is; "
      "B = R_1j in fine bins (= 1-jet data carried to two jets with the MC 2j/1j jet-pT shape bin by bin). Stat only.", ""]
for c, ch in enumerate(["EE", "MM"]):
    f = FULL[ch] / hist(f"data{ch}", f"JX_{ch}_2j_mll60to150_j1pt_noR")[0].sum()
    d2, ed2, y2, ey2, t2, et2 = comp(ch, "2j", "mll60to150", f)
    for r, src in enumerate(["1j", "1jall"]):
        d1, ed1, y1, ey1, t1, et1 = comp(ch, src, "mll60to150", f)
        Rf, eRf = Rof(d1, ed1, y1, ey1, t1, et1)
        # coarse: sum the fine bins inside each analysis bin
        def csum(v): return np.array([v[cidx == k].sum() for k in range(len(RB) - 1)])
        Rc, eRc = Rof(csum(d1), csum(ed1), csum(y1), csum(ey1), csum(t1), csum(et1))
        RA, eRA = Rc[cidx], eRc[cidx]
        ax = axT[r, c]
        L += [f"### {ch}: source {src}", "", "| jet pT | 2j data | data/(A) | data/(B) | data/(no R) |", "|---|---|---|---|---|"]
        for lab, RR, eRR, col, mk in [("A: coarse R_" + src + " as is", RA, eRA, "#1d4ed8", "s"), ("B: fine-bin R_" + src + " (MC shape per bin)", Rf, eRf, "#c2410c", "o"),
                                      ("no R", np.ones_like(Rf), np.zeros_like(Rf), "#9ca3af", "x")]:
            with np.errstate(divide="ignore", invalid="ignore"):
                RRn = np.where(np.isfinite(RR), RR, np.nan)
                pr = t2 + RRn * y2; epr = np.sqrt(et2 + RRn ** 2 * ey2 + (y2 * np.nan_to_num(eRR)) ** 2)
                q = d2 / pr; eq = np.abs(q) * np.sqrt(ed2 / d2 ** 2 + (epr / pr) ** 2)
            ok = np.isfinite(q) & (d2 > 5)
            chi2 = np.sum(((q - 1) / eq)[ok] ** 2)
            ax.errorbar(x * (1 + {"s": -0.02, "o": 0.0, "x": 0.02}[mk]), np.where(ok, q, np.nan), np.where(ok, eq, np.nan), fmt=mk, color=col, ms=4,
                        label=f"{lab}: total {d2.sum() / np.nansum(pr):.3f}, χ² {chi2:.1f}/{ok.sum()}", alpha=0.5 if mk == "x" else 1)
            if mk == "s": qA, eqA = q, eq
            if mk == "o": qB, eqB = q, eq
            if mk == "x": q0 = q
        for i in range(len(x)):
            if d2[i] > 5: L.append(f"| {XB[i]:.0f}-{XB[i+1]:.0f} | {d2[i]:.0f} | {qA[i]:.3f}±{eqA[i]:.3f} | {qB[i]:.3f}±{eqB[i]:.3f} | {q0[i]:.3f} |")
        L.append("")
        ax.axhline(1, color="gray", lw=0.8); ax.set_xscale("log"); ax.set_ylim(0.4, 2.2)
        ax.set_xlabel("leading jet pT (GeV)"); ax.set_ylabel("2-jet DY CR data / pred")
        ax.set_title(f"{'ee' if ch == 'EE' else 'μμ'}: R from {'1 jet, m(llj)>800' if src == '1j' else '1 jet, no mass cut'} → 2 jets", loc="left", fontsize=10)
        ax.legend(fontsize=7)
figT.tight_layout(); figT.savefig(f"{OUT}/transfer_1j_to_2j_AB.png", dpi=130)
figR.tight_layout(); figR.savefig(f"{OUT}/R_1jet_vs_2jet.png", dpi=130)
figC.tight_layout(); figC.savefig(f"{OUT}/closure_cr1_cr2_by_selection.png", dpi=130)
open(f"{OUT}/summary_closure.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
