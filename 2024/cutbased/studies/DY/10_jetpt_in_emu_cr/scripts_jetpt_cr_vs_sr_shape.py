#!/usr/bin/env python3
"""Leading / subleading jet pT shapes: DY MC in the DY CR vs DY MC in the SR vs one signal point (resolved, ee+mumu),
unit-area normalised, ratio to the DY-CR DY. Also data - non-DY of the DY CR. Boosted: leading AK8 jet pT."""
import glob, os, re, sys
import numpy as np, uproot
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
PC = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased"; sys.path.insert(0, PC); import config
OUT = os.path.join(PC, "studies/DY/10_jetpt_in_emu_cr/plots"); SET = "/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/RFlav_DYCRCharge_ZptNJet/2024"
SIG = {"MWR4000_N2000": "m_WR = 4 TeV, m_N = 2 TeV", "MWR4000_N200": "m_WR = 4 TeV, m_N = 0.2 TeV"}
VARS = {"Resolved": [("leading_jet_pt", np.array([40, 60, 80, 100, 130, 160, 200, 250, 300, 400, 500, 600, 800, 1000, 1300, 2000.])),
                     ("subleading_jet_pt", np.array([40, 50, 60, 80, 100, 130, 160, 200, 250, 300, 400, 500, 700, 1000.]))],
        "Boosted": [("leading_fatjet_pt", np.array([200, 250, 300, 350, 400, 500, 600, 800, 1000, 1300, 2000.]))]}
def rebin(v, src, dst):
    c = 0.5 * (src[:-1] + src[1:]); i = np.searchsorted(dst, c, side="right") - 1; ok = (i >= 0) & (i < len(dst) - 1)
    o = np.zeros(len(dst) - 1); np.add.at(o, i[ok], v[ok]); return o
def group(fn, ch):
    stem = config.sample_stem(fn)
    if stem is None: return "Nonprompt" if fn.startswith("WtoLNu_") else None
    if config.is_signal(stem):
        m = re.search(r"(MWR\d+_N\d+)", stem); lep = "EE" if "toElEl" in stem else "MM"
        return f"sig:{m.group(1)}" if m and m.group(1) in SIG and lep == ch else None
    if config.is_data(stem): return "data" if config.is_data(stem, config.CHANNELS[ch]["data"]) else None
    return config.classify_sample(re.sub(r"_p\d\d$", "", stem))[0]
H = {}
for p in sorted(glob.glob(os.path.join(SET, "*.root"))):
    fn = os.path.basename(p)[:-5]; f = None
    for ch in ("EE", "MM"):
        g = group(fn, ch)
        if g is None: continue
        if f is None: f = uproot.open(p)
        for cat, vs in VARS.items():
            for var, dst in vs:
                for reg in ("DYCR", "SR"):
                    name = f"Central/{reg}_{cat}_{ch}_{var}"
                    if name not in f: continue
                    h = f[name]; a = H.setdefault((cat, var, reg, g), [np.zeros(len(dst) - 1), np.zeros(len(dst) - 1)])
                    a[0] += rebin(h.values(), h.axis().edges(), dst); a[1] += rebin(h.variances(), h.axis().edges(), dst)
def get(cat, var, reg, g):
    return H.get((cat, var, reg, g), [np.zeros(1), np.zeros(1)])
for cat, vs in VARS.items():
    for var, dst in vs:
        w = np.diff(dst); c = 0.5 * (dst[:-1] + dst[1:])
        cr_dy, cr_dyv = get(cat, var, "DYCR", "DYJets"); sr_dy, sr_dyv = get(cat, var, "SR", "DYJets")
        cr_d = get(cat, var, "DYCR", "data")[0] - sum(get(cat, var, "DYCR", g)[0] for g in ("TT", "Nonprompt", "Others"))
        curves = [("DY MC, DY CR (60<m_ll<150)", cr_dy, cr_dyv, "tab:red", "-"), ("data - non-DY, DY CR", cr_d, get(cat, var, "DYCR", "data")[1], "k", "o"),
                  (f"DY MC, SR (m_ll>400)", sr_dy, sr_dyv, "tab:blue", "-")]
        for s, lab in SIG.items():
            v, vv = get(cat, var, "SR", f"sig:{s}"); curves.append((f"signal {lab}, SR", v, vv, "tab:green" if "N2000" in s else "tab:purple", "--"))
        fig, ax = plt.subplots(2, 1, figsize=(7.5, 7.5), sharex=True, gridspec_kw=dict(height_ratios=[2.4, 1.2]))
        ref = cr_dy / cr_dy.sum() / w
        for lab, v, vv, col, ls in curves:
            n = v.sum(); y = v / n / w; ye = np.sqrt(vv) / n / w
            if ls == "o": ax[0].errorbar(c, y, ye, fmt="ko", ms=4, label=f"{lab}  [{n:.0f}]")
            else: ax[0].step(dst, np.r_[y, y[-1]], where="post", color=col, ls=ls, lw=1.6, label=f"{lab}  [{n:.0f}]")
            r = np.where(ref > 0, y / np.where(ref > 0, ref, 1), np.nan); re_ = np.where(ref > 0, ye / np.where(ref > 0, ref, 1), np.nan)
            if ls == "o": ax[1].errorbar(c, r, re_, fmt="ko", ms=4)
            else: ax[1].errorbar(c, r, re_, fmt="o" + ls, ms=3, color=col, lw=1.2)
        ax[0].set_yscale("log"); ax[0].set_ylabel("fraction / GeV (unit area)"); ax[0].legend(fontsize=8)
        ax[0].set_title(f"{cat}: {var.replace('_', ' ')} shape — DY CR vs SR vs signal (2024, ee+#mu#mu, DY = C(per-jet) x EW x R)".replace("#mu#mu", "μμ"), fontsize=10)
        ax[1].axhline(1, color="k", lw=0.8); ax[1].set_ylabel("shape / DY MC in DY CR"); ax[1].set_xlabel(var.replace("_", " ") + " [GeV]"); ax[1].set_xscale("log"); ax[1].set_ylim(0, 4)
        fig.tight_layout(); fig.savefig(f"{OUT}/jetpt_shape_DYCR_vs_SR_vs_signal_{cat}_{var}_2024.png", dpi=120); fig.savefig(f"{OUT}/jetpt_shape_DYCR_vs_SR_vs_signal_{cat}_{var}_2024.pdf"); plt.close(fig)
        print(f"\n== {cat} {var}: shape fraction per bin (%)"); print("%-38s" % "" + "".join("%9s" % f"{dst[k]:.0f}-{dst[k+1]:.0f}" for k in range(len(dst) - 1)))
        for lab, v, vv, col, ls in curves: print("%-38s" % lab[:38] + "".join("%9.1f" % (100 * x / v.sum()) for x in v))
print("wrote", OUT)
