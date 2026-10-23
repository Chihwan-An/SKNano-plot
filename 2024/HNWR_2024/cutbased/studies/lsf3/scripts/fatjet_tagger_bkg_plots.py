#!/usr/bin/env python3
"""N = 200 signal pass rate of the per-event max GlobalParT3 XWW score over LSF3 > 0.75 fatjets, with the DY and TTLL + tW backgrounds.
Denominator (signal and background) = events with at least one LSF3 > 0.75 fatjet, so every curve starts at 1.
Signal: fatjet_tagger_hists.py outputs (HNWR3SR skims); background: fatjet_tagger_bkg_hists.py outputs (HNWR skims), each sample
weighted by xsec / sumW (condor/bkg_xsec.json) and summed per group: DY = DYto2L-4Jets HT-binned (MLM), TTLL + tW = TTto2L2Nu +
TWminusto2L2Nu + TbarWplusto2L2Nu. XWWqqev is drawn with the EE signal, XWWqqmv with the MM signal.
  <out>/<tagger>/N200_all_masspoints/<tagger>_<CH>_N200_LSF075_passrate_withbkg.png
  fatjet_tagger_bkg_plots.py [--sig-hists ...] [--bkg-hists ...] [--out studies/lsf3/fatjet_taggers]"""
import argparse, glob, json, os
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import mplhep as hep

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NANO15 = os.path.join(os.environ.get("SKNANO_HOME", "/data9/Users/achihwan/nano15/SKNanoAnalyzer"), "Nano15_Analyzers")
ap = argparse.ArgumentParser()
ap.add_argument("--sig-hists", default=f"{S}/hists_fatjet_taggers")
ap.add_argument("--bkg-hists", default=f"{S}/hists_fatjet_taggers_bkg")
ap.add_argument("--xsec", default=f"{S}/condor/bkg_xsec.json")
ap.add_argument("--out", default=f"{S}/fatjet_taggers")
ap.add_argument("--sig-json", default=os.path.join(NANO15, "HNWR/data/Sample/2024"),
                help="per-sample W_R registry jsons with xsec [pb] and sumsign")
a = ap.parse_args()
LUMI = 109.8   # fb^-1, 2024
REB = 4        # 200 -> 50 bins for the stacked template
SIGTAG = {"EE": "WRtoNEltoElElJJ", "MM": "WRtoNMutoMuMuJJ"}
hep.style.use("CMS")

TAGS = {"XWWqqev": ("EE", "GlobalParT3 XWW(qq e$\\nu$)", "$W_R \\to eN \\to eejj$"),
        "XWWqqmv": ("MM", "GlobalParT3 XWW(qq $\\mu\\nu$)", "$W_R \\to \\mu N \\to \\mu\\mu jj$")}
GROUPS = {"DY": ("Drell-Yan", "tab:red"), "TT": ("TTLL + tW", "tab:orange")}
X = json.load(open(a.xsec))

# background: sum chunks per sample, normalise each sample by xsec / sumW, sum per group
bkg = {g: {"n": 0.0, "h": {t: np.zeros(200) for t in TAGS}} for g in GROUPS}
seen = {}
for p in sorted(glob.glob(f"{a.bkg_hists}/*.npz")):
    r = np.load(p); s = str(r["sample"]); x = X[s]; f = x["xsec"] / x["sumW"]; g = x["group"]
    bkg[g]["n"] += f * float(r["n_anylsf"])
    for t in TAGS: bkg[g]["h"][t] += f * r[f"h_lsf_{t}"]
    seen[s] = seen.get(s, 0) + 1
print("background chunks per sample:", seen)
missing = sorted(set(X) - set(seen))
if missing: print("!! no chunks for", missing)

def pr(h, n): return np.cumsum(h[::-1])[::-1] / n
n = 0
for tag, (ch, tlab, chlab) in TAGS.items():
    sig = {}
    for p in glob.glob(f"{a.sig_hists}/{ch}_MWR*_N200.npz"):
        m = int(os.path.basename(p).split("_")[1][3:]); sig[m] = dict(np.load(p))
    masses = sorted(sig); cmap = plt.get_cmap("viridis")(np.linspace(0, 0.95, len(masses)))
    fig, ax = plt.subplots(figsize=(12, 9)); e = np.linspace(0, 1, 201)
    for k, m in enumerate(masses):
        ax.plot(e[:-1], pr(sig[m][f"h_lsf_{tag}"], sig[m]["n_anylsf"]), color=cmap[k], lw=2.5, label=f"$m_{{W_R}}$ = {m / 1000:g} TeV")
    rows = []
    for g, (glab, col) in GROUPS.items():
        y = pr(bkg[g]["h"][tag], bkg[g]["n"])
        ax.plot(e[:-1], y, color=col, lw=4, ls="--", label=glab)
        rows.append(f"{glab}: >0.3 {y[60] * 100:.2f}%, >0.5 {y[100] * 100:.3f}%, >0.7 {y[140] * 100:.4f}%")
    ax.set_xlim(0, 0.8); ax.set_ylim(0, 1.05); ax.set_xlabel(f"cut on max {tlab} score"); ax.set_ylabel("pass rate (score > cut)")
    ax.grid(alpha=0.3)
    hep.cms.label("Work in progress", data=False, com=13.6, ax=ax, fontsize=16, rlabel="(13.6 TeV)")
    ax.text(0.04, 0.96, chlab, transform=ax.transAxes, va="top", fontsize=17)
    ax.legend(fontsize=15, loc="lower left", title="$m_N$ = 200 GeV, fatjets with LSF$_3$ > 0.75", title_fontsize=14)
    d = f"{a.out}/{tag}/N200_all_masspoints"; os.makedirs(d, exist_ok=True)
    fig.tight_layout(); fig.savefig(f"{d}/{tag}_{ch}_N200_LSF075_passrate_withbkg.png", dpi=110); plt.close(fig); n += 1

    # stacked score template: events with >= 1 LSF3 > 0.75 fatjet, max score over those fatjets, normalised to LUMI
    eb = e[::REB]; fig, ax = plt.subplots(figsize=(12, 9))
    stack = [(GROUPS[g][0], GROUPS[g][1], LUMI * 1000.0 * bkg[g]["h"][tag].reshape(-1, REB).sum(axis=1)) for g in ("TT", "DY")]
    hep.histplot([s[2] for s in stack], eb, stack=True, histtype="fill", color=[s[1] for s in stack], label=[s[0] for s in stack], ax=ax, alpha=0.85)
    sig_tot = []
    for k, m in enumerate(masses):
        sj = json.load(open(f"{a.sig_json}/{SIGTAG[ch]}_MWR{m}_N200.json"))
        ys = LUMI * 1000.0 * sj["xsec"] / sj["sumsign"] * sig[m][f"h_lsf_{tag}"].reshape(-1, REB).sum(axis=1); sig_tot.append(ys.sum())
        ax.stairs(ys, eb, color=cmap[k], lw=2.5, label=f"$m_{{W_R}}$ = {m / 1000:g} TeV, $m_N$ = 200 GeV")
    btot = sum(s[2] for s in stack)
    ax.set_yscale("log"); ax.set_ylim(max(1e-2, min(min(sig_tot) * 1e-3, 1e-1)), btot.max() * 1e4); ax.set_xlim(0, 0.8)
    ax.set_xlabel(f"max {tlab} score (fatjets with LSF$_3$ > 0.75)"); ax.set_ylabel("events / 0.02")
    hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=16)
    ax.text(0.04, 0.96, chlab, transform=ax.transAxes, va="top", fontsize=17)
    ax.legend(fontsize=13, loc="upper right", ncol=2)
    fig.tight_layout(); fig.savefig(f"{d}/{tag}_{ch}_N200_LSF075_score_stack.png", dpi=110); plt.close(fig); n += 1
    print(tag, "stack yields (>=1 LSF fatjet):", ", ".join(f"{s[0]} {s[2].sum():.3g}" for s in stack), "| signal", ", ".join(f"{m // 1000}TeV {y:.3g}" for m, y in zip(masses, sig_tot)))
    print(tag, "|", " ; ".join(rows), "| signal >0.5: " + ", ".join(f"{m // 1000}TeV {pr(sig[m][f'h_lsf_{tag}'], sig[m]['n_anylsf'])[100] * 100:.1f}%" for m in masses))
# LSF3 itself in the same pass-rate format: max LSF3 over all fatjets, denominator = events with >= 1 fatjet
bl = {g: {"n": 0.0, "h": np.zeros(200)} for g in GROUPS}
for p in sorted(glob.glob(f"{a.bkg_hists}/*.npz")):
    r = np.load(p)
    if "h_all_lsf3" not in r.files: continue
    x = X[str(r["sample"])]; f = x["xsec"] / x["sumW"]; bl[x["group"]]["n"] += f * float(r["n_anyfj"]); bl[x["group"]]["h"] += f * r["h_all_lsf3"]
for ch, chlab in (("EE", TAGS["XWWqqev"][2]), ("MM", TAGS["XWWqqmv"][2])):
    sig = {}
    for p in glob.glob(f"{a.sig_hists}/{ch}_MWR*_N200.npz"):
        r = dict(np.load(p))
        if "h_all_lsf3" in r: sig[int(os.path.basename(p).split("_")[1][3:])] = r
    if not sig or any(bl[g]["n"] <= 0 for g in GROUPS): print(f"!! LSF3 histograms missing for {ch}"); continue
    masses = sorted(sig); cmap = plt.get_cmap("viridis")(np.linspace(0, 0.95, len(masses))); e = np.linspace(0, 1, 201)
    fig, ax = plt.subplots(figsize=(12, 9))
    for k, m in enumerate(masses):
        ax.plot(e[:-1], pr(sig[m]["h_all_lsf3"], sig[m]["n_anyfj"]), color=cmap[k], lw=2.5, label=f"$m_{{W_R}}$ = {m / 1000:g} TeV")
    rows = []
    for g, (glab, col) in GROUPS.items():
        y = pr(bl[g]["h"], bl[g]["n"]); ax.plot(e[:-1], y, color=col, lw=4, ls="--", label=glab); rows.append(f"{glab} >0.75 {y[150] * 100:.2f}%")
    ax.axvline(0.75, color="gray", ls=":", lw=2)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.05); ax.set_xlabel("cut on max LSF$_3$ of the fatjets"); ax.set_ylabel("pass rate (LSF$_3$ > cut)"); ax.grid(alpha=0.3)
    hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=16)
    ax.text(0.04, 0.66, chlab, transform=ax.transAxes, va="top", fontsize=17)
    ax.legend(fontsize=15, loc="lower left", title="$m_N$ = 200 GeV, events with $\\geq$ 1 fatjet", title_fontsize=14)
    d = f"{a.out}/LSF3/N200_all_masspoints"; os.makedirs(d, exist_ok=True)
    fig.tight_layout(); fig.savefig(f"{d}/LSF3_{ch}_N200_passrate_withbkg.png", dpi=110); plt.close(fig); n += 1

    # same scan as event counts: the background groups stacked, the signal drawn on top as lines. The pass-rate
    # version above hides that DY and TT sit four orders of magnitude above the signal at every LSF3 cut.
    # The scan starts at 0.5: below that every curve is flat, so the low end only wastes axis width.
    ycum = {g: LUMI * 1000.0 * np.cumsum(bl[g]["h"][::-1])[::-1] for g in ("TT", "DY")}
    ysig = {}
    for m in masses:
        sj = json.load(open(f"{a.sig_json}/{SIGTAG[ch]}_MWR{m}_N200.json"))
        ysig[m] = LUMI * 1000.0 * sj["xsec"] / sj["sumsign"] * np.cumsum(sig[m]["h_all_lsf3"][::-1])[::-1]
    for fname in ("yieldstack_withbkg",):
        x = e[:-1]
        fig, ax = plt.subplots(figsize=(12, 9))
        cumb = np.zeros(200)
        for g in ("TT", "DY"):
            ax.fill_between(x, cumb, cumb + ycum[g], step="post", color=GROUPS[g][1], alpha=0.75,
                            linewidth=0, label=GROUPS[g][0], zorder=1)
            cumb = cumb + ycum[g]
        ax.step(x, cumb, where="post", color="black", lw=1.5, zorder=2)
        for k, m in enumerate(masses):
            ax.plot(x, ysig[m], color=cmap[k], lw=2.5, zorder=3, label=f"$m_{{W_R}}$ = {m / 1000:g} TeV")
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlim(0.5, 1); ax.set_xlabel("cut on max LSF$_3$ of the fatjets")
        ticks = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        ax.set_xticks(ticks, [f"{t:g}" for t in ticks], minor=False)
        ax.set_xticks([], [], minor=True)
        ax.axvline(0.75, color="gray", ls=":", lw=2, zorder=4)
        # the stack fills everything below it, so the only free space is above: leave three decades of headroom
        # for the legend rather than letting it sit on top of the signal lines.
        ax.set_ylim(1.0, cumb.max() * 3e3)
        ax.set_ylabel("events above the cut")
        ax.grid(alpha=0.3, which="both")
        hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=16)
        ax.text(0.04, 0.80, chlab, transform=ax.transAxes, va="top", fontsize=17)
        h, l = ax.get_legend_handles_labels()      # signal first, then the stacked background
        order = list(range(2, len(l))) + [0, 1]
        ax.legend([h[i] for i in order], [l[i] for i in order], fontsize=14, ncol=3,
                  loc="upper right", title="$m_N$ = 200 GeV, events with $\\geq$ 1 fatjet", title_fontsize=13)
        fig.tight_layout(); fig.savefig(f"{d}/LSF3_{ch}_N200_{fname}.png", dpi=110); plt.close(fig); n += 1
    print(f"LSF3 {ch} |", " ; ".join(rows), "| signal >0.75: " + ", ".join(f"{m // 1000}TeV {pr(sig[m]['h_all_lsf3'], sig[m]['n_anyfj'])[150] * 100:.1f}%" for m in masses))
print(f"{n} plots"); print("FATJET_TAGGER_BKG_PLOTS_DONE")
