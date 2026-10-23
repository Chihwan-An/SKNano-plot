#!/usr/bin/env python3
"""CR1 (m_ll 60-100) -> CR2 (100-150) closure of the jet-pT correction on the jet-pT axis itself, bin by bin (2026-09-25).
Assumption under test: the data/MC difference in leading-jet pT does not depend on m_ll; the m_ll dependence of the
jet-pT shape is taken from MC. So
    R_CR1(x)   = (data - nonDY) / DY            in CR1, per jet-pT bin x (fine bins, per flavour)
    pred_CR2(x) = nonDY_CR2(x) + R_CR1(x) * DY_CR2(x)        (= CR1 corrected MC transported with the MC CR2/CR1 shape)
and data_CR2 / pred_CR2 should be 1. Also on m_lljj: DY_CR2^corr(m) = sum_x R_CR1(x) DY_CR2(x, m).
Input: 2D DYCR{1,2}_Resolved_<ch>_jetpt_mlljj (x = leading jet pT, y = m_lljj), DY from DYCR_ZptOnly (C x EW, no R),
production closure_ZptNJet_inputs (new per-jet C). Stat errors only (data + MC stat, R_CR1 stat propagated).
"""
import glob, os, re, sys
import numpy as np, uproot
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
PC = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased"; sys.path.insert(0, PC)
import config  # noqa: E402
PROD = "/gv0/Users/achihwan/SKNanoOutput_dy3gen/HNWR/closure_ZptNJet_inputs/2024"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "2024_ZptNJet_jetpt_binbybin")
XB = np.array([40, 60, 80, 100, 125, 150, 200, 250, 300, 400, 500, 600, 800, 1000, 2000.])
MB = np.array([800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 8000.])

def files():
    out = {}
    for p in sorted(glob.glob(os.path.join(PROD, "*.root"))):
        stem = config.sample_stem(os.path.basename(p)[:-5])
        if stem is None or config.is_signal(stem): continue
        out[stem] = p
    for s in [s for s in out if re.match(r".*_p\d\d$", s) and re.sub(r"_p\d\d$", "", s) in out]: del out[s]
    return out.items()

def group_of(stem, ch):
    if config.is_data(stem): return "data" if config.is_data(stem, config.CHANNELS[ch]["data"]) else None
    g = config.classify_sample(re.sub(r"_p\d\d$", "", stem))[0]
    return "DY" if g == "DYJets" else "nonDY"

H = {}
for stem, p in files():
    f = uproot.open(p)
    for cr in ("DYCR1", "DYCR2"):
        for ch in ("EE", "MM"):
            g = group_of(stem, ch)
            if g is None: continue
            name = f"DYCR_ZptOnly/Central/{cr}_Resolved_{ch}_jetpt_mlljj"
            if g != "DY" and name not in f: name = f"Central/{cr}_Resolved_{ch}_jetpt_mlljj"
            if name not in f: continue
            h = f[name]; k = (cr, ch, g)
            v, e2 = h.values(), h.variances()
            if k in H: H[k][0] += v; H[k][1] += e2
            else: H[k] = [v.copy(), e2.copy(), h.axis(0).edges(), h.axis(1).edges()]

def reb(k, xb=XB, mcut=800.):
    v, e2, xe, ye = H[k]
    ym = ye[:-1] >= mcut - 1e-6
    ix = np.searchsorted(xe, xb)
    vx = np.array([v[ix[i]:ix[i + 1], ym].sum() for i in range(len(xb) - 1)])
    ex = np.array([e2[ix[i]:ix[i + 1], ym].sum() for i in range(len(xb) - 1)])
    return vx, ex

def reb2(k, xb=XB):
    v, e2, xe, ye = H[k]; ix = np.searchsorted(xe, xb); iy = np.searchsorted(ye, MB)
    return (np.array([[v[ix[i]:ix[i + 1], iy[j]:iy[j + 1]].sum() for j in range(len(MB) - 1)] for i in range(len(xb) - 1)]),
            np.array([[e2[ix[i]:ix[i + 1], iy[j]:iy[j + 1]].sum() for j in range(len(MB) - 1)] for i in range(len(xb) - 1)]))

L = ["# CR1 (m_ll 60-100) -> CR2 (100-150): jet-pT correction bin by bin, resolved DY CR (m_lljj > 800), stat only", ""]
fig, axs = plt.subplots(3, 2, figsize=(13, 11), gridspec_kw={"height_ratios": [1.2, 1, 1]})
x = 0.5 * (XB[:-1] + XB[1:]); xe = 0.5 * np.diff(XB)
for c, ch in enumerate(("EE", "MM")):
    d1, ed1 = reb(("DYCR1", ch, "data")); y1, ey1 = reb(("DYCR1", ch, "DY")); n1, en1 = reb(("DYCR1", ch, "nonDY"))
    d2, ed2 = reb(("DYCR2", ch, "data")); y2, ey2 = reb(("DYCR2", ch, "DY")); n2, en2 = reb(("DYCR2", ch, "nonDY"))
    with np.errstate(divide="ignore", invalid="ignore"):
        R1 = (d1 - n1) / y1; eR1 = np.sqrt(ed1 + en1 + R1 ** 2 * ey1) / y1
        R2 = (d2 - n2) / y2; eR2 = np.sqrt(ed2 + en2 + R2 ** 2 * ey2) / y2
        pb = n2 + y2; pa = n2 + R1 * y2
        epa = np.sqrt(en2 + R1 ** 2 * ey2 + (y2 * eR1) ** 2)
        rb = d2 / pb; ra = d2 / pa; era = ra * np.sqrt(ed2 / d2 ** 2 + (epa / pa) ** 2); erb = rb * np.sqrt(ed2 / d2 ** 2 + (en2 + ey2) / pb ** 2)
        rr = R2 / R1; err = rr * np.sqrt((eR2 / R2) ** 2 + (eR1 / R1) ** 2)
    # (i) analysis-binning R_CR1 (40/100/200/400/600/800/2000) applied as is, vs (ii) = fine-bin R_CR1 above
    RB = np.array([40, 100, 200, 400, 600, 800, 2000.]); ci = np.searchsorted(RB, XB[:-1], side="right") - 1
    cs = lambda v: np.array([v[ci == k].sum() for k in range(len(RB) - 1)])
    with np.errstate(divide="ignore", invalid="ignore"):
        Rc = (cs(d1) - cs(n1)) / cs(y1); eRc = np.sqrt(cs(ed1) + cs(en1) + Rc ** 2 * cs(ey1)) / cs(y1)
        RA, eRA = Rc[ci], eRc[ci]
        pA = n2 + RA * y2; epA = np.sqrt(en2 + RA ** 2 * ey2 + (y2 * eRA) ** 2)
        rA = d2 / pA; erA = rA * np.sqrt(ed2 / d2 ** 2 + (epA / pA) ** 2)
    okA = np.isfinite(rA) & (d2 > 0); chiA = np.nansum(((rA - 1) / erA)[okA] ** 2)
    ok = np.isfinite(ra) & (d2 > 0)
    chi2 = np.nansum(((ra - 1) / era)[ok] ** 2); nb = ok.sum()
    L += [f"## {ch}", "", f"CR1 data {d1.sum():.0f}, CR2 data {d2.sum():.0f}; CR2 total data/pred: before {d2.sum()/pb.sum():.3f}, after {d2.sum()/pa.sum():.3f}; "
          f"jet-pT chi2(after) = {chi2:.1f} / {nb} bins", "",
          f"(i) coarse R_CR1 as is: total {d2.sum()/pA.sum():.3f}, jet-pT chi2 {chiA:.1f}/{okA.sum()};  (ii) + MC jet-pT shape per fine bin: total {d2.sum()/pa.sum():.3f}, chi2 {chi2:.1f}/{nb}", "",
          "| jet pT | R_CR1 | R_CR2 | R_CR2/R_CR1 | CR2 data/pred (no corr) | (i) coarse R_CR1 as is | (ii) + MC shape per fine bin |", "|---|---|---|---|---|---|---|"]
    for i in range(len(x)):
        L.append(f"| {XB[i]:.0f}-{XB[i+1]:.0f} | {R1[i]:.3f}±{eR1[i]:.3f} | {R2[i]:.3f}±{eR2[i]:.3f} | {rr[i]:.3f}±{err[i]:.3f} | {rb[i]:.3f}±{erb[i]:.3f} | {rA[i]:.3f}±{erA[i]:.3f} | **{ra[i]:.3f}±{era[i]:.3f}** |")
    # mass axis with the fine-bin R
    Y2, EY2 = reb2(("DYCR2", ch, "DY")); N2, EN2 = reb2(("DYCR2", ch, "nonDY")); D2, _ = reb2(("DYCR2", ch, "data"))
    Rr = np.nan_to_num(R1, nan=1.0)
    ym = (Rr[:, None] * Y2).sum(0); nm = N2.sum(0); dm = D2.sum(0); em = np.sqrt((Rr[:, None] ** 2 * EY2).sum(0) + EN2.sum(0))
    RAr = np.nan_to_num(RA, nan=1.0); ymA = (RAr[:, None] * Y2).sum(0); rmA = dm / (ymA + nm)
    rm = dm / (ym + nm); erm = rm * np.sqrt(1 / np.maximum(dm, 1) + (em / (ym + nm)) ** 2); rm0 = dm / (Y2.sum(0) + nm)
    L += ["", "m_lljj (CR2) data/pred  no corr → (i) → (ii): " + ", ".join(f"{MB[j]:.0f}: {rm0[j]:.3f}→{rmA[j]:.3f}→{rm[j]:.3f}±{erm[j]:.3f}" for j in range(len(MB) - 1)), ""]
    # plots
    ax = axs[0, c]
    ax.errorbar(x, R1, eR1, xerr=xe, fmt="o", color="#1d4ed8", ms=4, label="R from CR1 (60–100)")
    ax.errorbar(x, R2, eR2, xerr=xe, fmt="s", mfc="none", color="#c2410c", ms=4, label="R measured in CR2 (100–150)")
    ax.set_xscale("log"); ax.set_ylabel("(data − nonDY) / DY"); ax.set_ylim(0.3, 2.5); ax.legend(fontsize=8)
    ax.set_title(f"{'ee' if ch == 'EE' else 'μμ'} resolved DY CR, m(lljj) > 800 (no R in MC)", loc="left", fontsize=10)
    ax = axs[1, c]
    ax.errorbar(x, rb, erb, xerr=xe, fmt="x", color="#9ca3af", ms=4, alpha=0.5, label="no jet-pT corr. (reference)")
    ax.errorbar(x * 0.98, rA, erA, xerr=xe, fmt="s", mfc="none", color="#1d4ed8", ms=4, label=f"(i) R_CR1 analysis bins, as is  χ² {chiA:.1f}/{okA.sum()}")
    ax.errorbar(x, ra, era, xerr=xe, fmt="o", color="#0f766e", ms=4, label=f"(ii) + MC jet-pT shape per fine bin  χ² {chi2:.1f}/{nb}")
    ax.axhline(1, color="gray", lw=0.8); ax.set_xscale("log"); ax.set_ylim(0.5, 2.2); ax.set_ylabel("CR2 data / pred"); ax.set_xlabel("leading jet pT (GeV)"); ax.legend(fontsize=8)
    ax = axs[2, c]; xm = np.arange(len(MB) - 1)
    ax.errorbar(xm, rm0, fmt="x", color="#9ca3af", ms=4, alpha=0.5, label="no jet-pT corr.")
    ax.errorbar(xm - 0.1, rmA, fmt="s", mfc="none", color="#1d4ed8", ms=4, label="(i) R_CR1 analysis bins")
    ax.errorbar(xm + 0.1, rm, erm, fmt="o", color="#0f766e", ms=4, label="(ii) + MC shape per fine bin")
    ax.axhline(1, color="gray", lw=0.8); ax.set_ylim(0.5, 2.0); ax.set_xticks(xm); ax.set_xticklabels([f"{MB[j]:.0f}" for j in xm], fontsize=8)
    ax.set_xlabel("m(lljj) bin low edge (GeV), CR2"); ax.set_ylabel("CR2 data / pred"); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(f"{OUT}/cr1_to_cr2_jetpt_binbybin.png", dpi=130)
open(f"{OUT}/summary.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
