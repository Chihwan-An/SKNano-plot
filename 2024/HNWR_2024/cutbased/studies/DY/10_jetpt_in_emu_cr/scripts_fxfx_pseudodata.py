#!/usr/bin/env python3
"""FxFx pseudo-data test of the DY correction in the (blinded) SR, MC only.
FxFx (NLO, no correction) plays the role of data; LO x C x EW x R must reproduce it in the DY CR (where R was
derived) AND in the SR (m_ll > 400, m_lljj > 800). The quantity is FxFx / LO on the jet-pT and m_lljj axes,
for the uncorrected LO, LO with the shipped correction, and LO with the per-jet C + its R.
If R extrapolates in m_ll, the corrected ratio is the same flat line in the CR and the SR."""
import glob, json, os, sys
import numpy as np, uproot
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)) + "/plots"; os.makedirs(OUT, exist_ok=True)
FXFX = "/gv0/Users/achihwan/SKNanoOutput_dy3gen/HNWR/DYCRSplit_NoDYCorr_WeightSystOnly/2024"
LO = {"LO no corr.": FXFX, "LO x C(shipped) x EW x R(shipped)": "/gv0/Users/achihwan/SKNanoOutput/HNWR/RFlav_DYCRCharge/2024",
      "LO x C(per-jet) x EW x R(new)": "/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/RFlav_DYCRCharge_ZptNJet/2024"}
COL = {"LO no corr.": "0.4", "LO x C(shipped) x EW x R(shipped)": "tab:orange", "LO x C(per-jet) x EW x R(new)": "tab:red"}
# region -> (histogram prefix per channel, channels)
REG = {"Resolved DY CR (60<m_ll<150)": ("DYCR_Resolved_{ch}", ["EE", "MM"]), "Resolved SR (m_ll>400, m_lljj>800)": ("SR_Resolved_{ch}", ["EE", "MM"]),
       "e-mu CR (m_ll>400, m_lljj>800)": ("FlavCR_Resolved_EM", ["EM"]),
       "Boosted DY CR": ("DYCR_Boosted_{ch}", ["EE", "MM"]), "Boosted SR": ("SR_Boosted_{ch}", ["EE", "MM"])}
VARS = {"leading_jet_pt": np.array([40, 100, 200, 400, 600, 800, 2000.]), "mlljj": np.array([800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 4000, 8000.]),
        "leading_fatjet_pt": np.array([200, 400, 600, 2000.]), "mlljj_boosted": np.array([800, 1000, 1200, 1500, 1800, 2400, 8000.])}
def hvar(reg, var):
    b = reg.startswith("Boosted")
    if var == "leading_jet_pt": return None if b else var
    if var == "leading_fatjet_pt": return var if b else None
    if var == "mlljj": return None if b else var
    if var == "mlljj_boosted": return "mlljj" if b else None
def rebin(v, src, dst):
    c = 0.5 * (src[:-1] + src[1:]); i = np.searchsorted(dst, c, side="right") - 1; ok = (i >= 0) & (i < len(dst) - 1)
    o = np.zeros(len(dst) - 1); np.add.at(o, i[ok], v[ok]); return o
def collect(base, pattern):
    acc = {}
    for p in sorted(glob.glob(os.path.join(base, pattern))):
        f = uproot.open(p)
        for reg, (pref, chs) in REG.items():
            for ch in chs:
                for var, dst in VARS.items():
                    hv = hvar(reg, var)
                    if hv is None: continue
                    name = f"Central/{pref.format(ch=ch)}_{hv}"
                    if name not in f: continue
                    h = f[name]; a = acc.setdefault((reg, var), [np.zeros(len(dst) - 1), np.zeros(len(dst) - 1)])
                    a[0] += rebin(h.values(), h.axis().edges(), dst); a[1] += rebin(h.variances(), h.axis().edges(), dst)
    return acc
FX = collect(FXFX, "DYto2*_FxFx.root"); L = {k: collect(v, "Skim_HNWR_DYto2L*.root") for k, v in LO.items()}
report = {}
for var in VARS:
    regs = [r for r in REG if hvar(r, var)]
    fig, ax = plt.subplots(2, len(regs), figsize=(4.2 * len(regs), 7), sharex="col", gridspec_kw=dict(height_ratios=[2, 1.6]))
    for j, reg in enumerate(regs):
        dst = VARS[var]; c = 0.5 * (dst[:-1] + dst[1:]); w = np.diff(dst); fx, fxv = FX[(reg, var)]
        ax[0, j].errorbar(c, fx / w, np.sqrt(fxv) / w, fmt="ko", ms=4, label="FxFx (NLO), no corr. = pseudo-data")
        for lab, S in L.items():
            lo, lov = S[(reg, var)]; ax[0, j].step(dst, np.r_[lo / w, (lo / w)[-1]], where="post", color=COL[lab], lw=1.5, label=lab)
            r = np.where(lo > 0, fx / np.where(lo > 0, lo, 1), np.nan); e = np.where(lo > 0, np.sqrt(fxv + r ** 2 * lov) / np.where(lo > 0, lo, 1), np.nan)
            ax[1, j].errorbar(c, r, e, fmt="o-" if "new" in lab else "s--", ms=4, color=COL[lab], label=lab)
            report.setdefault(var, {}).setdefault(reg, {})[lab] = dict(edges=dst.tolist(), ratio=r.tolist(), err=e.tolist(), fxfx=fx.tolist(), lo=lo.tolist(), sum_ratio=float(fx.sum() / lo.sum()))
        ax[0, j].set_yscale("log"); ax[0, j].set_title(reg, fontsize=9); ax[1, j].axhline(1, color="k", lw=0.8); ax[1, j].set_ylim(0.3, 2.0)
        ax[1, j].set_xlabel(var.replace("_", " ") + " [GeV]"); ax[1, j].set_xscale("log")
        if j == 0: ax[0, j].set_ylabel("events / GeV"); ax[1, j].set_ylabel("FxFx / LO"); ax[0, j].legend(fontsize=6); ax[1, j].legend(fontsize=6)
    fig.suptitle(f"FxFx pseudo-data: FxFx / LO on the {var.replace('_', ' ')} axis, DY CR vs SR (MC only), 2024", fontsize=11)
    fig.tight_layout(); fig.savefig(f"{OUT}/fxfx_pseudodata_{var}_2024.png", dpi=120); fig.savefig(f"{OUT}/fxfx_pseudodata_{var}_2024.pdf"); plt.close(fig)
    for reg in regs:
        print(f"\n== {var} :: {reg}   FxFx / LO"); dst = VARS[var]
        print("%-36s %7s" % ("LO variant", "sum") + "".join("%12s" % f"{dst[k]:.0f}-{dst[k+1]:.0f}" for k in range(len(dst) - 1)))
        for lab, x in report[var][reg].items(): print("%-36s %7.3f" % (lab, x["sum_ratio"]) + "".join("%12s" % (f"{r:.2f}±{e:.2f}" if np.isfinite(r) else "-") for r, e in zip(x["ratio"], x["err"])))
        print("%-36s %7.0f" % ("  FxFx events (weighted)", sum(report[var][reg]["LO no corr."]["fxfx"])))
json.dump(report, open(f"{OUT}/fxfx_pseudodata_2024.json", "w"), indent=1); print("wrote", OUT)
