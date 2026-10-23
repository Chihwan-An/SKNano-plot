#!/usr/bin/env python3
"""DY CR1 -> CR2 closure of the jet-pT correction R (AN2019_083 Fig. 27-30), 2024.

Input: $SKNANO_OUTPUT/HNWR/DYCRStudy_RFlav_DYCRSplit_WeightSystOnly/2024 (userflags DYCRStudy,RFlav,DYCRSplit,
WeightSystOnly; submitted 2026-09-17). The DYCR_ZptOnly variant carries C x kappa_EW but no R:
    DYCR_ZptOnly/Central/DYCR{1,2}_<Resolved|Boosted>_<EE|MM>_jetpt_mlljj   TH2: leading (fat)jet pT (10 GeV) x m(lljj)/m(lJ) (50 GeV)
    DYCR_ZptOnly/Central/DYCR{1,2}_<cat>_<ch>_mlljj                        TH1 (cross-check of the y-projection)
Method: R_CR1(jet pT bin) = (data - non-DY)/DY from the x-projection of the CR1 2D histogram in the delivered R
binning; DY_CR2^corr(mass) = sum_x R_CR1(x) DY_CR2(x, mass). CR2 m(lljj)/m(lJ): data vs stack before/after.
Output: ../validation/dycr12_closure_<cat>_<ch>.{pdf,png}, ../validation/dycr12_R_CR1.json
    python3 make_dycr12_closure.py [--prod DIR] [--variant DYCR_ZptOnly] [--flav]   (--flav: per-flavour R, as in RFlav)
"""
import argparse, glob, json, os, re, sys
import numpy as np, uproot
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
sys.path.insert(0, "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased")
import config  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--prod", default="/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/DYCRStudy_RFlav_DYCRSplit_WeightSystOnly/2024")
ap.add_argument("--variant", default="DYCR_ZptOnly")
ap.add_argument("--flav", action="store_true", help="derive R in CR1 per flavour (default: ee+mumu combined, AN2019_083 style)")
ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "validation"))
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

RBINS = {"Resolved": [40, 100, 200, 400, 600, 800, 2000], "Boosted": [200, 400, 600, 2000]}
MBINS = {"Resolved": [800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 8000], "Boosted": [800, 1000, 1200, 1500, 1800, 8000]}
GROUPS = ["DYJets", "TT", "Nonprompt", "Others"]
COL = {"DYJets": "#ffff00", "TT": "#ff0000", "Nonprompt": "#00a000", "Others": "#0000ff"}
LAB = {"DYJets": "Drell-Yan", "TT": r"t$\bar{\rm t}$+tW", "Nonprompt": "Nonprompt", "Others": "Others"}
CH = {"EE": "ee", "MM": r"$\mu\mu$"}


def files():
    out = {}
    for p in sorted(glob.glob(os.path.join(a.prod, "*.root"))):
        stem = config.sample_stem(os.path.basename(p)[:-5])
        if stem is None or config.is_signal(stem):
            continue
        out[stem] = p
    for s in [s for s in out if re.match(r".*_p\d\d$", s) and re.sub(r"_p\d\d$", "", s) in out]:
        del out[s]
    return list(out.items())


def group_of(stem, ch):
    if config.is_data(stem):
        return "data" if config.is_data(stem, config.CHANNELS[ch]["data"]) else None
    g, _ = config.classify_sample(re.sub(r"_p\d\d$", "", stem))
    return g


# --- read the 2D histograms: H[(cr, cat, ch, group)] = (values[x, y], xedges, yedges)
H = {}
FL = files()
for stem, p in FL:
    f = uproot.open(p)
    for cr in ("DYCR1", "DYCR2"):
        for cat in ("Resolved", "Boosted"):
            for ch in ("EE", "MM"):
                g = group_of(stem, ch)
                if g is None:
                    continue
                name = f"{a.variant}/Central/{cr}_{cat}_{ch}_jetpt_mlljj"
                if name not in f:
                    continue
                h = f[name]
                v = h.values(flow=False); xe = h.axis(0).edges(); ye = h.axis(1).edges()
                key = (cr, cat, ch, g)
                if key in H:
                    H[key][0][...] += v
                else:
                    H[key] = [v.copy(), xe, ye]
    f.close()
print(f"{len(FL)} files, {len(H)} histograms")


def rebin_x(v, xe, edges):
    """sum the fine x bins into the coarse `edges`; returns (nbins_coarse, ny)"""
    idx = np.searchsorted(xe, edges)
    return np.stack([v[idx[i]:idx[i + 1]].sum(0) for i in range(len(edges) - 1)])


def rebin_y(v, ye, edges):
    idx = np.searchsorted(ye, edges)
    return np.array([v[idx[i]:idx[i + 1]].sum() for i in range(len(edges) - 1)])


R_out = {}
for cat in ("Resolved", "Boosted"):
    rb = np.array(RBINS[cat], float); mb = np.array(MBINS[cat], float)
    # --- R from CR1 (per flavour or combined)
    Rmap = {}
    for ch in ("EE", "MM"):
        chans = [ch] if a.flav else ["EE", "MM"]
        num = np.zeros(len(rb) - 1); den = np.zeros(len(rb) - 1)
        for c in chans:
            d = H.get(("DYCR1", cat, c, "data")); dy = H.get(("DYCR1", cat, c, "DYJets"))
            if d is None or dy is None:
                continue
            nd = sum(rebin_x(H[("DYCR1", cat, c, g)][0], H[("DYCR1", cat, c, g)][1], rb).sum(1)
                     for g in ("TT", "Nonprompt", "Others") if ("DYCR1", cat, c, g) in H)
            num += rebin_x(d[0], d[1], rb).sum(1) - nd
            den += rebin_x(dy[0], dy[1], rb).sum(1)
        Rmap[ch] = np.where(den > 0, num / np.where(den > 0, den, 1), 1.0)
        R_out[f"{cat}_{ch}"] = {"edges": rb.tolist(), "R_CR1": Rmap[ch].tolist(), "flavour_split": a.flav}
        print(cat, ch, "R_CR1 =", np.round(Rmap[ch], 3))
    # --- apply to CR2 and plot
    for ch in ("EE", "MM"):
        if ("DYCR2", cat, ch, "data") not in H or ("DYCR2", cat, ch, "DYJets") not in H:
            print("missing CR2", cat, ch); continue
        dy2 = H[("DYCR2", cat, ch, "DYJets")]
        dy_x_m = rebin_x(dy2[0], dy2[1], rb)                      # (nR, ny fine)
        dy_before = rebin_y(dy_x_m.sum(0), dy2[2], mb)
        dy_after = rebin_y((Rmap[ch][:, None] * dy_x_m).sum(0), dy2[2], mb)
        data = rebin_y(H[("DYCR2", cat, ch, "data")][0].sum(0), dy2[2], mb)
        stacks = {g: rebin_y(H[("DYCR2", cat, ch, g)][0].sum(0), dy2[2], mb) if ("DYCR2", cat, ch, g) in H else np.zeros(len(mb) - 1)
                  for g in ("TT", "Nonprompt", "Others")}
        fig = plt.figure(figsize=(11, 5.6), dpi=150)
        gs = GridSpec(2, 2, height_ratios=[3, 1], hspace=0.05, wspace=0.25)
        for j, (dyv, title) in enumerate(((dy_before, r"before $R$ (C $\times \kappa_{\rm EW}$ only)"), (dy_after, r"after $R$ derived in DY CR1"))):
            ax = fig.add_subplot(gs[0, j]); axr = fig.add_subplot(gs[1, j], sharex=ax)
            bottom = np.zeros(len(mb) - 1); tot = np.zeros(len(mb) - 1)
            for g, vals in (("Others", stacks["Others"]), ("Nonprompt", stacks["Nonprompt"]), ("TT", stacks["TT"]), ("DYJets", dyv)):
                ax.bar(mb[:-1], vals, width=np.diff(mb), bottom=bottom, align="edge", color=COL[g], label=LAB[g], edgecolor="k", lw=0.3)
                bottom += vals; tot += vals
            xc = 0.5 * (mb[1:] + mb[:-1])
            ax.errorbar(xc, data, yerr=np.sqrt(data), fmt="ko", ms=4, label="Data")
            ax.set_yscale("log"); ax.set_ylim(0.5, max(tot.max(), data.max()) * 30)
            ax.set_ylabel("Events / bin"); ax.legend(fontsize=8, loc="upper right")
            ax.set_title(f"{cat} DY CR2 (100 < $m_{{\\ell\\ell}}$ < 150 GeV), {CH[ch]}, {title}", fontsize=9)
            chi2 = np.sum((data - tot) ** 2 / np.where(tot > 0, tot, 1))
            ax.text(0.03, 0.93, f"data/MC = {data.sum()/tot.sum():.3f}   $\\chi^2$/bins = {chi2:.1f}/{len(mb)-1}", transform=ax.transAxes, fontsize=8)
            r = np.where(tot > 0, data / np.where(tot > 0, tot, 1), np.nan)
            axr.errorbar(xc, r, yerr=np.sqrt(data) / np.where(tot > 0, tot, 1), fmt="ko", ms=4)
            axr.axhline(1, color="gray", ls="--"); axr.set_ylim(0.5, 1.5); axr.set_ylabel("Data / MC")
            axr.set_xlabel(r"$m_{\ell\ell jj}$ [GeV]" if cat == "Resolved" else r"$m_{\ell J}$ [GeV]")
            axr.set_xlim(mb[0], min(mb[-1], 4000)); plt.setp(ax.get_xticklabels(), visible=False)
        fig.suptitle("CMS Work in progress   —   2024, 109.8 fb$^{-1}$ (13.6 TeV)", fontsize=10)
        tag = "flav" if a.flav else "comb"
        for ext in ("pdf", "png"):
            fig.savefig(os.path.join(a.out, f"dycr12_closure_{cat.lower()}_{ch}_{tag}.{ext}"), bbox_inches="tight")
        plt.close(fig)
        print(cat, ch, "CR2 data/MC before %.3f after %.3f" % (data.sum() / (dy_before + sum(stacks.values())).sum(), data.sum() / (dy_after + sum(stacks.values())).sum()))
json.dump(R_out, open(os.path.join(a.out, f"dycr12_R_CR1_{'flav' if a.flav else 'comb'}.json"), "w"), indent=1)
print("done ->", a.out)
