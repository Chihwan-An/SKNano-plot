#!/usr/bin/env python3
"""Does the jet-pT correction R hold at m_ll > 400?  The resolved e-mu flavour CR (m_ll > 400, m_lljj > 800 = the SR
selection with an e-mu pair) is the only unblinded region with the SR m_ll. There, (data - non-DY MC) is compared with
the DY MC (DY -> tautau -> e mu) on the leading-jet-pT axis, exactly as R is derived in the DY CR (60 < m_ll < 150),
for the uncorrected DY and for the corrected one (C x EW x R).  Reference: the same in the DY CR (ee+mumu)."""
import glob, json, os, re, sys
import numpy as np, uproot
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
PC = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased"; sys.path.insert(0, PC); import config
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PC, "studies/DY/10_jetpt_in_emu_cr/plots"); os.makedirs(OUT, exist_ok=True)
SET = "/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/RFlav_DYCRCharge_ZptNJet/2024"           # data, non-DY, DY x C(per-jet) x EW x R
SET_OLD = "/gv0/Users/achihwan/SKNanoOutput/HNWR/RFlav_DYCRCharge/2024"                # DY x C(shipped) x EW x R(shipped)
SET_NOCORR = "/gv0/Users/achihwan/SKNanoOutput_dy3gen/HNWR/DYCRSplit_NoDYCorr_WeightSystOnly/2024"   # DY, no correction
REG = {"emu": ("FlavCR_Resolved_EM", ["EM"]), "dycr": ("DYCR_Resolved", ["EE", "MM"])}
VARS = {"leading_jet_pt": np.array([40, 100, 200, 400, 600, 800, 2000.]), "leading_jet_pt_fine": np.array([40, 60, 80, 100, 130, 160, 200, 250, 300, 400, 500, 600, 800, 1200, 2000.]),
        "subleading_jet_pt": np.array([40, 60, 80, 100, 150, 200, 300, 400, 600, 1000, 2000.]), "mlljj": np.array([800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 4000, 8000.])}
HN = {"leading_jet_pt_fine": "leading_jet_pt"}
def stem_group(fname, ch):
    stem = config.sample_stem(fname)
    if stem is None: return "Nonprompt" if fname.startswith("WtoLNu_") else None
    if config.is_signal(stem): return None
    if config.is_data(stem):
        # e-mu CR: the plotter reads it as the MM job (config.REGIONS Resolve_FLV: channels [("MM", "EM")]) -> Muon stream only
        return "data" if config.is_data(stem, config.CHANNELS["MM" if ch == "EM" else ch]["data"]) else None
    return config.classify_sample(re.sub(r"_p\d\d$", "", stem))[0]
def rebin(v, src, dst):
    c = 0.5 * (src[:-1] + src[1:]); i = np.searchsorted(dst, c, side="right") - 1; ok = (i >= 0) & (i < len(dst) - 1)
    o = np.zeros(len(dst) - 1); np.add.at(o, i[ok], v[ok]); return o
def collect(base, want_groups, dy_only=False):
    acc = {}
    for p in sorted(glob.glob(os.path.join(base, "*.root"))):
        fn = os.path.basename(p)[:-5]
        if dy_only and not fn.startswith("Skim_HNWR_DYto2L"): continue
        f = None
        for reg, (pref, chs) in REG.items():
            for ch in chs:
                g = stem_group(fn, ch)
                if g is None or g not in want_groups: continue
                if f is None: f = uproot.open(p)
                for var, dst in VARS.items():
                    name = f"Central/{pref}_{ch}_{HN.get(var, var)}" if reg == "dycr" else f"Central/{pref}_{HN.get(var, var)}"
                    if name not in f: continue
                    h = f[name]; k = (reg, g, var)
                    a = acc.setdefault(k, [np.zeros(len(dst) - 1), np.zeros(len(dst) - 1)])
                    a[0] += rebin(h.values(), h.axis().edges(), dst); a[1] += rebin(h.variances(), h.axis().edges(), dst)
    return acc
A = collect(SET, {"data", "TT", "Nonprompt", "Others", "DYJets"})
B = collect(SET_OLD, {"DYJets"}, dy_only=True); C = collect(SET_NOCORR, {"DYJets"}, dy_only=True)
DY = {"no corr.": C, "C(shipped) x EW x R(shipped)": B, "C(per-jet) x EW x R(new)": A}
COL = {"no corr.": "0.4", "C(shipped) x EW x R(shipped)": "tab:orange", "C(per-jet) x EW x R(new)": "tab:red"}
report = {}
for var, dst in VARS.items():
    fig, ax = plt.subplots(2, 2, figsize=(12, 7.5), sharex="col", gridspec_kw=dict(height_ratios=[2.2, 1.4]))
    for j, (reg, title) in enumerate((("dycr", "Resolved DY CR (60 < m_ll < 150), ee+mumu"), ("emu", "Resolved e-mu CR (m_ll > 400, m_lljj > 800)"))):
        d, dv = A[(reg, "data", var)]; nd = sum(A[(reg, g, var)][0] for g in ("TT", "Nonprompt", "Others") if (reg, g, var) in A)
        ndv = sum(A[(reg, g, var)][1] for g in ("TT", "Nonprompt", "Others") if (reg, g, var) in A)
        res, resv = d - nd, dv + ndv; w = np.diff(dst); c = 0.5 * (dst[:-1] + dst[1:])
        ax[0, j].errorbar(c, res / w, np.sqrt(resv) / w, fmt="ko", ms=4, label="data - non-DY MC")
        ax[0, j].step(dst, np.r_[nd / w, (nd / w)[-1]], where="post", color="tab:blue", lw=1, ls=":", label="non-DY MC (TT+others)")
        for lab, S in DY.items():
            dy, dyv = S[(reg, "DYJets", var)]
            ax[0, j].step(dst, np.r_[dy / w, (dy / w)[-1]], where="post", color=COL[lab], lw=1.5, label=f"DY {lab}")
            r = np.where(dy > 0, res / np.where(dy > 0, dy, 1), np.nan); re_ = np.where(dy > 0, np.sqrt(resv + np.where(dy > 0, r ** 2 * dyv, 0)) / np.where(dy > 0, dy, 1), np.nan)
            ax[1, j].errorbar(c, r, re_, fmt="o-" if "new" in lab else "s--", ms=4, color=COL[lab], label=lab)
            report.setdefault(var, {}).setdefault(reg, {})[lab] = dict(edges=dst.tolist(), ratio=r.tolist(), err=re_.tolist(), dy=dy.tolist(), data_minus_nondy=res.tolist(), data=d.tolist(), nondy=nd.tolist())
        ax[0, j].set_yscale("log"); ax[0, j].set_title(title, fontsize=10); ax[0, j].set_ylabel("events / GeV"); ax[0, j].legend(fontsize=7)
        ax[1, j].axhline(1, color="k", lw=0.8); ax[1, j].set_ylabel("(data - non-DY) / DY"); ax[1, j].set_xlabel(var.replace("_", " ") + " [GeV]")
        ax[1, j].set_ylim(-0.5, 3.5) if reg == "emu" else ax[1, j].set_ylim(0.4, 2.2)
        if "jet" in var or var == "mlljj": ax[1, j].set_xscale("log")
        ax[1, j].legend(fontsize=7)
    fig.suptitle("Is R(jet pT) valid at m_ll > 400?  (data - non-DY) vs DY MC on the " + var.replace("_", " ") + " axis, 2024", fontsize=11)
    fig.tight_layout(); fig.savefig(f"{OUT}/jetpt_dataMinusNonDY_vs_DY_{var}_2024.png", dpi=120); fig.savefig(f"{OUT}/jetpt_dataMinusNonDY_vs_DY_{var}_2024.pdf"); plt.close(fig)
# e-mu CR: plain data / MC of the jet pT (TT modelling) and the DY fraction
var = "leading_jet_pt_fine"; dst = VARS[var]; c = 0.5 * (dst[:-1] + dst[1:])
d = A[("emu", "data", var)][0]; mc = {g: A[("emu", g, var)][0] for g in ("TT", "Nonprompt", "Others", "DYJets") if ("emu", g, var) in A}; tot = sum(mc.values())
print("\n== e-mu CR leading jet pT: data / MC (DY = C(per-jet) x EW x R)"); print("%-10s %8s %9s %7s %7s" % ("bin", "data", "MC", "d/MC", "DYfrac"))
for k in range(len(c)): print("%-10s %8.0f %9.1f %7.3f %7.3f" % (f"{dst[k]:.0f}-{dst[k+1]:.0f}", d[k], tot[k], d[k] / tot[k] if tot[k] > 0 else float("nan"), mc["DYJets"][k] / tot[k] if tot[k] > 0 else 0))
print("TOTAL data %.0f MC %.1f d/MC %.3f  DY %.1f (%.1f%%)" % (d.sum(), tot.sum(), d.sum() / tot.sum(), mc["DYJets"].sum(), 100 * mc["DYJets"].sum() / tot.sum()))
for var in ("leading_jet_pt", "mlljj"):
    for reg in ("dycr", "emu"):
        print(f"\n== {reg} {var}: (data - non-DY) / DY"); dst = VARS[var]
        print("%-32s" % "DY variant" + "".join("%12s" % f"{dst[k]:.0f}-{dst[k+1]:.0f}" for k in range(len(dst) - 1)))
        for lab, x in report[var][reg].items(): print("%-32s" % lab + "".join("%12s" % (f"{r:.2f}±{e:.2f}" if np.isfinite(r) else "-") for r, e in zip(x["ratio"], x["err"])))
        x = report[var][reg]["no corr."]; print("%-32s" % "  data - non-DY" + "".join("%12.0f" % v for v in x["data_minus_nondy"]) + "\n%-32s" % "  DY no corr." + "".join("%12.1f" % v for v in x["dy"]))
json.dump(report, open(f"{OUT}/jetpt_emu_cr_2024.json", "w"), indent=1); print("wrote", OUT)
