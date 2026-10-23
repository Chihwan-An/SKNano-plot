#!/usr/bin/env python3
"""Pass rate and cumulative yield of the boosted-candidate fatjet (no LSF3 requirement) for XWWqqev (EE), XWWqqmv (MM) and
LSF3 (EE and MM), scanning the cut. Denominator = events passing the boosted fatjet selection of the channel
(boosted_fatjet_tagger_hists.py). Signal: N = 200, every W_R mass; background: DY (HT-binned MLM) and TTLL + tW, each sample
weighted by xsec / sumW (condor/bkg_xsec.json); yields are normalised to LUMI.
The tagger plots use the log10-binned histograms (`h_<ch>_<tag>_log`, 1e-8 to 1) when they are in the npz, so the region below
one linear bin (score < 0.005), where the background piles up, is resolved; otherwise they fall back to the 200 linear bins.
Every curve carries a dotted crosshair at its "LSF3 > 0.75 equivalent" point: the horizontal line is what that sample keeps
with LSF3 > 0.75, the vertical line is the tagger cut that keeps the same amount.
  <out>/<tagger>_<CH>_N200_passrate_withbkg.png   pass rate vs cut (log x for the taggers)
  <out>/<tagger>_<CH>_N200_cumulative_withbkg.png cumulative events above the cut (log x, log y)
  <out>/<tagger>_<CH>_N200_score_stack.png        stacked score template
  <out>/passrate_boosted_fatjet.md
  boosted_fatjet_tagger_plots.py [--sig-hists ...] [--bkg-hists ...] [--out studies/lsf3/fatjet_taggers/boosted_fatjet]"""
import argparse, glob, json, os
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import mplhep as hep

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NANO15 = os.path.join(os.environ.get("SKNANO_HOME", "/data9/Users/achihwan/nano15/SKNanoAnalyzer"), "Nano15_Analyzers")
ap = argparse.ArgumentParser()
ap.add_argument("--sig-hists", default=f"{S}/hists_boosted_sig")
ap.add_argument("--bkg-hists", default=f"{S}/hists_boosted_bkg")
ap.add_argument("--xsec", default=f"{S}/condor/bkg_xsec.json")
ap.add_argument("--out", default=f"{S}/fatjet_taggers/boosted_fatjet")
ap.add_argument("--sig-json", default=os.path.join(NANO15, "HNWR/data/Sample/2024"),
                help="per-sample W_R registry jsons with xsec [pb] and sumsign")
a = ap.parse_args()
LUMI = 109.8   # fb^-1, 2024
REB = 4        # 200 -> 50 bins for the stacked template
NB = 200
XMIN = 1.0 / NB       # left end of the log x axis when only the linear bins are available
XMINLOG = 1e-6        # left end of the log x axis with the log10-binned histograms
LSFCUT = 0.75
SIGTAG = {"EE": "WRtoNEltoElElJJ", "MM": "WRtoNMutoMuMuJJ"}
hep.style.use("CMS")
os.makedirs(a.out, exist_ok=True)

CHLAB = {"EE": "$W_R \\to eN \\to eejj$", "MM": "$W_R \\to \\mu N \\to \\mu\\mu jj$"}
PLOTS = [("XWWqqev", "EE", "GlobalParT3 XWW(qq e$\\nu$) score", [0.3, 0.5, 0.7]),
         ("XWWqqmv", "MM", "GlobalParT3 XWW(qq $\\mu\\nu$) score", [0.3, 0.5, 0.7]),
         ("lsf3", "EE", "LSF$_3$", [0.5, 0.75, 0.9, 0.95]),
         ("lsf3", "MM", "LSF$_3$", [0.5, 0.75, 0.9, 0.95])]
GROUPS = {"DY": ("Drell-Yan", "tab:red"), "TT": ("TTLL + tW", "tab:orange")}
X = json.load(open(a.xsec))

TAGS = ("XWWqqev", "XWWqqmv", "lsf3")
bkg = {g: {ch: {"n": 0.0, "h": {t: np.zeros(NB) for t in TAGS}, "hl": {}} for ch in ("EE", "MM")} for g in GROUPS}
seen = {}; LOGE = None
for p in sorted(glob.glob(f"{a.bkg_hists}/*.npz")):
    r = np.load(p); s = str(r["sample"]); x = X[s]; f = x["xsec"] / x["sumW"]; seen[s] = seen.get(s, 0) + 1
    if "log_edges" in r.files: LOGE = r["log_edges"]
    for ch in ("EE", "MM"):
        bkg[x["group"]][ch]["n"] += f * float(r[f"n_{ch}"])
        for t in TAGS:
            bkg[x["group"]][ch]["h"][t] += f * r[f"h_{ch}_{t}"]
            if f"h_{ch}_{t}_log" in r.files:
                bkg[x["group"]][ch]["hl"][t] = bkg[x["group"]][ch]["hl"].get(t, 0) + f * r[f"h_{ch}_{t}_log"]
missing = sorted(set(X) - set(seen))
print(f"background: {sum(seen.values())} chunks, {len(seen)} samples" + (f"; !! missing {missing}" if missing else ""))
sig = {}
for p in glob.glob(f"{a.sig_hists}/*_N200.npz"):
    ch, m = os.path.basename(p).split("_")[:2]; sig[(ch, int(m[3:]))] = dict(np.load(p))
    if "log_edges" in sig[(ch, int(m[3:]))]: LOGE = sig[(ch, int(m[3:]))]["log_edges"]
sigscale = {}   # (ch, mass) -> xsec / sumsign, for the LUMI-normalised yields
for (ch, m) in sig:
    sj = json.load(open(f"{a.sig_json}/{SIGTAG[ch]}_MWR{m}_N200.json")); sigscale[(ch, m)] = sj["xsec"] / sj["sumsign"]
print("log-binned histograms:", "yes" if LOGE is not None else "no (falling back to the 200 linear bins)")

def cum(h): return np.cumsum(h[::-1])[::-1]              # events above each bin low edge
def pr(h, n): return cum(h) / n if n > 0 else np.zeros_like(h)
def at(y, c): return y[int(round(c * NB))]
def cross(y, ref, edges):
    """Cut where the (decreasing) curve y falls to ref; linear interpolation between bin edges. 0 = never reaches ref."""
    below = np.flatnonzero(y <= ref)
    if not len(below): return 0.0
    i = below[0]
    if i == 0 or y[i - 1] == y[i]: return edges[i]
    return edges[i - 1] + (edges[i] - edges[i - 1]) * (y[i - 1] - ref) / (y[i - 1] - y[i])
e = np.linspace(0, 1, NB + 1)
md = ["# Pass rate of the boosted-candidate fatjet (no LSF3 requirement), 2024", "",
      "Denominator = events passing the boosted fatjet selection of the channel: leading tight lepton (pT > 60) of the channel flavour, "
      "AK8 pT > 200, |eta| < 2.5, msoftdrop > 40, TIGHT ID, first fatjet with |dPhi(l, J)| > 2.0, m(lJ) > 800. Signal N = 200; "
      f"background weighted by xsec / sumW, yields normalised to {LUMI} fb^-1. 'same-rate tagger cut' = the tagger cut that keeps "
      "the same fraction as LSF3 > 0.75 (from the log10-binned histograms when available).", ""]
for tag, ch, xl, cuts in PLOTS:
    masses = sorted(m for (c, m) in sig if c == ch); cmap = plt.get_cmap("viridis")(np.linspace(0, 0.95, len(masses)))
    istag = tag != "lsf3"
    uselog = istag and LOGE is not None
    ex = LOGE if uselog else e     # bin edges of the curves that get plotted
    xlo = XMINLOG if uselog else XMIN
    # curves: (label, colour, style, pass rate, cumulative yield, LSF3 pass rate, LSF3 cumulative yield)
    curves = []
    for k, m in enumerate(masses):
        r = sig[(ch, m)]; sc = LUMI * 1000.0 * sigscale[(ch, m)]; n = r[f"n_{ch}"]
        h = r[f"h_{ch}_{tag}_log"] if uselog else r[f"h_{ch}_{tag}"]
        curves.append((f"$m_{{W_R}}$ = {m / 1000:g} TeV", cmap[k], dict(lw=2.5),
                       pr(h, n), sc * cum(h), pr(r[f"h_{ch}_lsf3"], n), sc * cum(r[f"h_{ch}_lsf3"])))
    for g, (glab, col) in GROUPS.items():
        B = bkg[g][ch]; sc = LUMI * 1000.0
        h = B["hl"][tag] if uselog else B["h"][tag]
        curves.append((glab, col, dict(lw=4, ls="--"),
                       pr(h, B["n"]), sc * cum(h), pr(B["h"]["lsf3"], B["n"]), sc * cum(B["h"]["lsf3"])))

    md += [f"## {tag}, {ch}", "", "| sample | selected (fraction of skim) | " + " | ".join(f"> {c}" for c in cuts)
           + (" | LSF3 > 0.75 | same-rate tagger cut |" if istag else " |"), "|---|---|" + "---|" * (len(cuts) + (2 if istag else 0))]
    for k, m in enumerate(masses):
        r = sig[(ch, m)]; ylin = pr(r[f"h_{ch}_{tag}"], r[f"n_{ch}"]); ylsf = curves[k][5]
        row = f"| W_R {m / 1000:g} TeV, N 200 | {r[f'n_{ch}'] / r['total'] * 100:.1f}% | " + " | ".join(f"{at(ylin, c) * 100:.2f}%" for c in cuts)
        md.append(row + (f" | {at(ylsf, LSFCUT) * 100:.2f}% | {cross(curves[k][3], at(ylsf, LSFCUT), ex):.2e} |" if istag else " |"))
    for j, (g, (glab, _)) in enumerate(GROUPS.items()):
        B = bkg[g][ch]; c = curves[len(masses) + j]; ylin = pr(B["h"][tag], B["n"])
        row = f"| {glab} | - | " + " | ".join(f"{at(ylin, cc) * 100:.3f}%" for cc in cuts)
        md.append(row + (f" | {at(c[5], LSFCUT) * 100:.2f}% | {cross(c[3], at(c[5], LSFCUT), ex):.2e} |" if istag else " |"))
    md.append("")

    # ---- pass rate ----------------------------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 9))
    for lab, col, st, y, _, ylsf, _ in curves:
        ax.plot(ex[:-1], y, color=col, **st, label=lab)
        if istag:   # dotted crosshair at the LSF3 > 0.75 working point of this sample
            ref = at(ylsf, LSFCUT); xc = cross(y, ref, ex)
            if xc > xlo:
                ax.plot([xlo, xc], [ref, ref], color=col, ls=":", lw=1.2, alpha=0.8)
                ax.plot([xc, xc], [0, ref], color=col, ls=":", lw=1.2, alpha=0.8)
                ax.plot([xc], [ref], marker="o", ms=6, color=col)
            else:   # crossing below the plotted range: show the LSF3 level alone
                ax.plot([xlo, 1], [ref, ref], color=col, ls=":", lw=1.2, alpha=0.8)
    if istag:
        ax.plot([], [], color="gray", ls=":", lw=1.5, marker="o", ms=6, label="same as LSF$_3$ > 0.75")
        ax.set_xscale("log"); ax.set_xlim(xlo, 1)
    else:
        ax.axvline(LSFCUT, color="gray", ls=":", lw=2); ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05); ax.set_xlabel(f"cut on {xl} of the boosted fatjet"); ax.set_ylabel("pass rate (> cut)")
    ax.grid(alpha=0.3, which="both")
    hep.cms.label("Work in progress", data=False, com=13.6, ax=ax, fontsize=16, rlabel="(13.6 TeV)")
    ax.text(0.04, 0.96 if istag else 0.66, CHLAB[ch], transform=ax.transAxes, va="top", fontsize=17)
    ax.legend(fontsize=13, loc="lower left", ncol=2 if istag else 1,
              title="$m_N$ = 200 GeV, boosted fatjet selection", title_fontsize=13)
    name = "LSF3" if tag == "lsf3" else tag
    fig.tight_layout(); fig.savefig(f"{a.out}/{name}_{ch}_N200_passrate_withbkg.png", dpi=110); plt.close(fig)

    # ---- cumulative yield ---------------------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 9))
    for lab, col, st, _, Y, _, Ylsf in curves:
        ax.plot(ex[:-1], np.where(Y > 0, Y, np.nan), color=col, **st, label=lab)
        if istag:
            ref = Ylsf[int(round(LSFCUT * NB))]; xc = cross(Y, ref, ex)
            if xc > xlo:
                ax.plot([xlo, xc], [ref, ref], color=col, ls=":", lw=1.2, alpha=0.8)
                ax.plot([xc, xc], [1e-3, ref], color=col, ls=":", lw=1.2, alpha=0.8)
                ax.plot([xc], [ref], marker="o", ms=6, color=col)
            else:
                ax.plot([xlo, 1], [ref, ref], color=col, ls=":", lw=1.2, alpha=0.8)
    if istag:
        ax.plot([], [], color="gray", ls=":", lw=1.5, marker="o", ms=6, label="same as LSF$_3$ > 0.75")
        ax.set_xscale("log"); ax.set_xlim(xlo, 1)
    else:
        ax.axvline(LSFCUT, color="gray", ls=":", lw=2); ax.set_xlim(0, 1)
    ax.set_yscale("log"); ax.set_ylim(1e-2, 1e8)
    ax.set_xlabel(f"cut on {xl} of the boosted fatjet"); ax.set_ylabel("events above the cut")
    ax.grid(alpha=0.3, which="both")
    hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=16)
    ax.text(0.04, 0.96, CHLAB[ch], transform=ax.transAxes, va="top", fontsize=17)
    ax.legend(fontsize=13, loc="upper right", ncol=2, title="$m_N$ = 200 GeV, boosted fatjet selection", title_fontsize=13)
    fig.tight_layout(); fig.savefig(f"{a.out}/{name}_{ch}_N200_cumulative_withbkg.png", dpi=110); plt.close(fig)

    # ---- stacked template ---------------------------------------------------------------------------------------
    eb = e[::REB]; fig, ax = plt.subplots(figsize=(12, 9))
    stack = [(GROUPS[g][0], GROUPS[g][1], LUMI * 1000.0 * bkg[g][ch]["h"][tag].reshape(-1, REB).sum(axis=1)) for g in ("TT", "DY")]
    hep.histplot([s[2] for s in stack], eb, stack=True, histtype="fill", color=[s[1] for s in stack], label=[s[0] for s in stack], ax=ax, alpha=0.85)
    ytot = []
    for k, m in enumerate(masses):
        ys = LUMI * 1000.0 * sigscale[(ch, m)] * sig[(ch, m)][f"h_{ch}_{tag}"].reshape(-1, REB).sum(axis=1); ytot.append(ys.sum())
        ax.stairs(ys, eb, color=cmap[k], lw=2.5, label=f"$m_{{W_R}}$ = {m / 1000:g} TeV, $m_N$ = 200 GeV")
    btot = sum(s[2] for s in stack)
    ax.set_yscale("log"); ax.set_ylim(1e-2, max(btot.max(), max(ytot)) * 1e4); ax.set_xlim(0, 1 if tag == "lsf3" else 0.8)
    ax.set_xlabel(f"{xl} of the boosted fatjet"); ax.set_ylabel("events / 0.02")
    hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=16)
    ax.text(0.04, 0.96, CHLAB[ch], transform=ax.transAxes, va="top", fontsize=17)
    ax.legend(fontsize=13, loc="upper right", ncol=2, title="boosted fatjet selection", title_fontsize=13)
    fig.tight_layout(); fig.savefig(f"{a.out}/{name}_{ch}_N200_score_stack.png", dpi=110); plt.close(fig)
    if istag:
        print(f"{name} {ch} LSF3>0.75 equivalent tagger cut: "
              + ", ".join(f"{c[0].split('=')[-1].strip() if 'm_' in c[0] else c[0]} {cross(c[3], at(c[5], LSFCUT), ex):.2e}" for c in curves))
open(f"{a.out}/passrate_boosted_fatjet.md", "w").write("\n".join(md) + "\n")
print("\n".join(md)); print("BOOSTED_FATJET_TAGGER_PLOTS_DONE")
