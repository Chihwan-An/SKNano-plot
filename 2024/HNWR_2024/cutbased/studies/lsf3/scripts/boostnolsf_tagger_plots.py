#!/usr/bin/env python3
"""Tagger pass rate and surviving yield in the boosted SR / Flavor CR of the BoostNoLSF production.

Reads the HNWR output written with userflag BoostNoLSF, where the away fatjet is taken from the FULL fatjet
collection (no LSF3 > 0.75) and the GlobalParT3 XWW scores of that fatjet are stored alongside LSF3:
    <region>_fatjet_{XWWqqev,XWWqqmv,lsf3}        200 (100 for lsf3) linear bins in [0, 1]
    <region>_fatjet_{XWWqqev,XWWqqmv,lsf3}_log10  240 log10 bins from 1e-8 to 1
The log10 histograms are the ones plotted: the background piles up below one linear bin (0.005), which is exactly
where the separation has to be read off. Under/overflow are folded back into the first/last bin -- LSF3 is exactly
1.0 for ~5 % of the SR fatjets and would otherwise be lost to the overflow.
Per region the tagger matching the flavour of the lepton INSIDE the fatjet is the relevant one:
    SR_Boosted_EE     electron in the fatjet -> XWWqqev
    SR_Boosted_MM     muon in the fatjet     -> XWWqqmv
    FlavCR_Boosted_EMJ  lead e, muon in jet  -> XWWqqmv
    FlavCR_Boosted_MEJ  lead mu, electron in jet -> XWWqqev

With --bkg every non-signal sample of the same production is read too, grouped with the analysis-wide rules of
plot/HNWR_2024/cutbased/config.py (DYJets / TT / Nonprompt / Others). The analyzer histograms are already normalised to the
2024 lumi, so a group is the plain sum of its samples -- no per-sample xsec bookkeeping here, unlike the npz
pipeline of boosted_fatjet_tagger_plots.py which starts from the skims.
  <out>/<region>_<tagger>_passrate.png    pass rate vs cut, one curve per W_R mass (+ background groups)
  <out>/<region>_<tagger>_yield.png       surviving yield vs cut (2024 lumi, absolute)
  <out>/<region>_<tagger>_stack.png       stacked background score template with the signal overlaid   [--bkg]
  <out>/<region>_<tagger>_signif.png      S/sqrt(B) vs cut, against the LSF3 > 0.75 working point      [--bkg]
  <out>/boostnolsf_passrate.md
  boostnolsf_tagger_plots.py [--in <dir>] [--out ...] [--bkg]"""
import argparse, fnmatch, glob, os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import mplhep as hep
import uproot

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(S)))    # plot/HNWR_2024/cutbased, for config.py
import config

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="inp", default="/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/BoostNoLSF/2024")
ap.add_argument("--out", default=f"{S}/fatjet_taggers/boostnolsf")
ap.add_argument("--masses", default="1000,2000,3000,4000,5000,6000,7000")
ap.add_argument("--bkg", action="store_true", help="read the background samples of the same production too")
ap.add_argument("--bmin", type=float, default=1.0,
                help="stop the S/sqrt(B) curve once fewer than this many background events survive the cut; "
                     "above it the MC is exhausted (B = 0 beyond ~0.7) and S/sqrt(B) diverges on nothing")
a = ap.parse_args()
hep.style.use("CMS")
os.makedirs(a.out, exist_ok=True)

LUMI = 109.8
MASSES = [int(m) for m in a.masses.split(",")]
SIGTAG = {"EE": "WRtoNEltoElElJJ", "MM": "WRtoNMutoMuMuJJ"}
# (region, signal channel that populates it, discriminant, axis label, log x)
# LSF3 is scanned on the same fatjet in the same region, and the analyzer already writes its histograms
# next to the tagger ones in the same files, so it is just another entry here -- nothing to re-run.
# It gets a linear axis: unlike the tagger scores it is spread over [0, 1] rather than piled up at 0.
PLOTS = [
    ("SR_Boosted_EE", "EE", "XWWqqev", "GlobalParT3 XWW(qq e$\\nu$) score", True),
    ("SR_Boosted_EE", "EE", "lsf3",    "LSF$_3$", False),
    ("SR_Boosted_MM", "MM", "XWWqqmv", "GlobalParT3 XWW(qq $\\mu\\nu$) score", True),
    ("SR_Boosted_MM", "MM", "lsf3",    "LSF$_3$", False),
]
CHLAB = {"EE": "$W_R \\to eN \\to eejj$, boosted SR", "MM": "$W_R \\to \\mu N \\to \\mu\\mu jj$, boosted SR"}
# config keeps the group colours as ROOT constants so it never has to import ROOT; map them to the matplotlib
# equivalents so these plots stack in the same colours as the main analysis plots.
ROOTCOL = {"kYellow": "gold", "kRed": "tab:red", "kGreen+2": "tab:green", "kBlue": "tab:blue"}
GLAB = {"DYJets": "Drell-Yan", "TT": "$t\\bar{t}$ + tW", "Nonprompt": "Nonprompt", "Others": "Others"}
GROUPS = [(g, GLAB.get(g, g), ROOTCOL.get(col, "gray")) for g, (col, _) in config.BACKGROUND_GROUPS.items()]
LSFCUT = 0.75
XLO = 1e-6          # left end of the plotted log range; the axis itself goes down to 1e-8
NSTACK = 50         # target bins of the stacked template (the linear histograms have 200, LSF3 100)


def read(src, name):
    """Histogram contents with the flow bins folded into the first / last bin."""
    v = src[name].values(flow=True)
    body = v[1:-1].copy()
    body[0] += v[0]         # underflow: score <= 0 never passes any cut
    body[-1] += v[-1]       # overflow: score == 1 passes every cut
    return body


def survivors(h):
    """Yield above each bin's LOWER edge: reverse-cumulative, so entry i = sum of bins >= i."""
    return np.cumsum(h[::-1])[::-1]


def crossing(y, level, x):
    """The cut at which curve y drops through `level`, or 0 if it never does.

    Interpolates in log x for the tagger axes, which span eight decades; falls back to linear where the
    bin edge is 0, i.e. on the linear LSF3 axis.
    """
    below = np.nonzero(y < level)[0]
    if len(below) == 0 or below[0] == 0:
        return 0.0
    i = below[0]
    y0, y1 = y[i - 1], y[i]
    if y0 == y1:
        return x[i]
    f = (y0 - level) / (y0 - y1)
    if x[i - 1] <= 0:
        return float(x[i - 1] + f * (x[i] - x[i - 1]))
    return float(np.exp(np.log(x[i - 1]) + f * (np.log(x[i]) - np.log(x[i - 1]))))


def load_background(region, tag, suffix):
    """Per-group discriminant / LSF3 / linear histograms, summed over the samples of the group.

    The analyzer output is already lumi-normalised, so a group is the plain sum of its samples.  "tag" is
    the scanned discriminant on its own axis (log10 or linear), "lsf" is always the log10 LSF3 histogram --
    the LSF3 > 0.75 reference has to be read off the same fine axis whatever is being scanned -- and "lin"
    is the linear histogram used for the stacked template.
    """
    out = {g: None for g, _, _ in GROUPS}
    used, unclassified = [], []
    for path in sorted(glob.glob(f"{a.inp}/Skim_HNWR_*.root")):
        stem = os.path.basename(path)[len("Skim_HNWR_"):-len(".root")]
        if any(fnmatch.fnmatch(stem, g) for g in config.SIGNAL_GLOBS):
            continue
        group, _ = config.classify_sample(stem)
        if group is None:
            unclassified.append(stem); continue
        src = uproot.open(path)["Central"]
        if f"{region}_fatjet_{tag}{suffix}" not in {k.split(";")[0] for k in src.keys(recursive=False)}:
            continue     # region empty for this sample, so the analyzer never booked the histogram
        piece = {"tag": read(src, f"{region}_fatjet_{tag}{suffix}"),
                 "lsf": read(src, f"{region}_fatjet_lsf3_log10"),
                 "lin": read(src, f"{region}_fatjet_{tag}")}
        out[group] = piece if out[group] is None else {k: out[group][k] + v for k, v in piece.items()}
        used.append(stem)
    if unclassified:
        print(f"!! {region}: unclassified samples {unclassified}")
    print(f"{region} {tag}: background from {len(used)} samples")
    return {g: v for g, v in out.items() if v is not None}


edges = np.logspace(-8, 0, 241)
ex = edges[:-1]              # a cut placed at each bin's lower edge
ilsf = np.searchsorted(ex, LSFCUT) - 1
md = ["# BoostNoLSF: tagger pass rate in the boosted SR", "",
      ("Signal and background, 2024." if a.bkg else "Signal only, 2024.")
      + " The away fatjet is the first with |dPhi(lead lepton, J)| > 2.0 taken from the FULL",
      "fatjet collection -- no LSF3 cut -- so the tagger scan replaces LSF3 rather than sitting on top of it.", ""]
if a.bkg:
    md += [f"Background groups follow plot/HNWR_2024/cutbased/config.py. The analyzer histograms are already normalised to "
           f"{LUMI} fb^-1, so each group is the plain sum of its samples.", ""]
COL = plt.cm.viridis(np.linspace(0, 0.92, len(MASSES)))

for region, ch, tag, xl, logx in PLOTS:
    suffix = "_log10" if logx else ""
    curves, ext = [], None
    for m, col in zip(MASSES, COL):
        path = f"{a.inp}/Skim_HNWR_{SIGTAG[ch]}_MWR{m}_N200.root"
        if not os.path.exists(path):
            print(f"missing {path}"); continue
        src = uproot.open(path)["Central"]
        htag, hlsf = read(src, f"{region}_fatjet_{tag}{suffix}"), read(src, f"{region}_fatjet_lsf3_log10")
        hlin = read(src, f"{region}_fatjet_{tag}")
        n = htag.sum()
        if n <= 0:
            print(f"{region} MWR{m}: empty"); continue
        # the scanned axis: the log10 edges for the taggers, the histogram's own linear edges for LSF3
        ext = ex if logx else np.linspace(0, 1, len(htag) + 1)[:-1]
        curves.append((f"$m_{{W_R}}$ = {m / 1000:g} TeV", col, n, survivors(htag), survivors(hlsf), hlin))

    if not curves:
        continue
    xlot = XLO if logx else 0.0

    bkg = load_background(region, tag, suffix) if a.bkg else {}
    # background groups carry the same (label, colour, total, cumulative tagger, cumulative LSF3, linear) shape
    bcurves = [(lab, colr, bkg[g]["tag"].sum(), survivors(bkg[g]["tag"]), survivors(bkg[g]["lsf"]), bkg[g]["lin"])
               for g, lab, colr in GROUPS if g in bkg]
    if bkg:
        btot = {k: sum(b[k] for b in bkg.values()) for k in ("tag", "lsf", "lin")}
        Btag, Blsf = survivors(btot["tag"]), survivors(btot["lsf"])
        Blsf75 = Blsf[ilsf]
        # The background MC runs out long before the score does (B < 1 event above ~0.54, exactly 0 above ~0.7).
        # S/sqrt(B) past that is a divergence on an empty denominator, not a working point, so every statement
        # about a "best" cut is restricted to the range where the background estimate still means something.
        ok = Btag >= a.bmin
        xend = ext[ok][-1] if ok.any() else xlot

    md += [f"## {region} ({tag})", "",
           "| sample | SR yield (no cut) | LSF3 > 0.75 | same-rate cut | > 0.01 | > 0.1 | > 0.5 |",
           "|---|---|---|---|---|---|---|"]
    for lab, _, n, ytag, ylsf, _ in curves + bcurves:
        ref = ylsf[ilsf] / n
        at = lambda c: ytag[np.searchsorted(ext, c) - 1] / n
        md.append(f"| {lab.replace('$m_{W_R}$ = ', 'W_R ')} | {n:.2f} | {ref * 100:.1f}% | "
                  f"{crossing(ytag / n, ref, ext):.2e} | {at(0.01) * 100:.1f}% | {at(0.1) * 100:.1f}% | {at(0.5) * 100:.1f}% |")
    md.append("")

    # ---- what the LSF3-equivalent tagger cut costs in background -------------------------------------------------
    if bkg:
        md += ["At each signal's LSF3-equivalent tagger cut (the cut keeping the same signal fraction as LSF3 > 0.75), "
               f"against LSF3 > 0.75 itself, which keeps {Blsf75:.2f} background events. The last two columns scan "
               f"for the best cut instead, over the range where at least {a.bmin:g} background event survives "
               f"(score < {xend:.2f}); past that the background MC is exhausted and S/sqrt(B) diverges on nothing. "
               "That maximum is shallow -- 'best cut' is the range staying within 1 % of it, not a single "
               "recommended value.", "",
               "| sample | tagger cut | background kept | vs LSF3 > 0.75 | S/sqrt(B) tagger | S/sqrt(B) LSF3 | best cut | S/sqrt(B) best |",
               "|---|---|---|---|---|---|---|---|"]
        for lab, _, n, ytag, ylsf, _ in curves:
            slsf = ylsf[ilsf]
            xc = crossing(ytag, slsf, ext)
            i = max(np.searchsorted(ext, xc) - 1, 0) if xc > 0 else 0
            b, s = Btag[i], ytag[i]
            z = np.full(len(ytag), np.nan); z[ok] = ytag[ok] / np.sqrt(Btag[ok])
            j = np.nanargmax(z)
            # the maximum is shallow -- quote the range that stays within 1 % of it rather than the single
            # argmax, which sits inside the line width of the others and is not a recommendation
            good = np.nan_to_num(z, nan=-np.inf) >= z[j] * 0.99
            lo, hi = j, j
            while lo > 0 and good[lo - 1]: lo -= 1
            while hi < len(good) - 1 and good[hi + 1]: hi += 1
            md.append(f"| {lab.replace('$m_{W_R}$ = ', 'W_R ')} | {xc:.2e} | {b:.2f} | {b / Blsf75:.2f}x | "
                      f"{s / np.sqrt(b):.2f} | {slsf / np.sqrt(Blsf75):.2f} | {ext[lo]:.2f}-{ext[hi]:.2f} | {z[j]:.2f} |")
        md.append("")

    # ---- pass rate / surviving yield ----------------------------------------------------------------------------
    for kind in ("passrate", "yield"):
        fig, ax = plt.subplots(figsize=(12, 9))
        for lab, col, n, ytag, ylsf, _ in curves:
            norm = n if kind == "passrate" else 1.0
            ax.plot(ext, ytag / norm, color=col, lw=3, label=lab)
            if not logx:
                continue     # scanning LSF3 itself: the "equivalent cut" is 0.75, drawn once as a vline below
            # dotted crosshair: what this sample keeps with LSF3 > 0.75, and the tagger cut that keeps as much
            ref = ylsf[ilsf]
            xc = crossing(ytag, ref, ext)
            if xc > xlot:
                ax.plot([xlot, xc], [ref / norm] * 2, color=col, ls=":", lw=1.2, alpha=0.8)
                ax.plot([xc, xc], [ax.get_ylim()[0] if kind == "yield" else 0, ref / norm], color=col, ls=":", lw=1.2, alpha=0.8)
                ax.plot([xc], [ref / norm], marker="o", ms=7, color=col)
        for lab, colr, n, ytag, _, _ in bcurves:
            ax.plot(ext, ytag / (n if kind == "passrate" else 1.0), color=colr, lw=4, ls="--", label=lab)
        if logx:
            ax.plot([], [], color="gray", ls=":", lw=1.5, marker="o", ms=7, label="same as LSF$_3$ > 0.75")
            ax.set_xscale("log"); ax.set_xlim(XLO, 1)
        else:
            ax.axvline(LSFCUT, color="gray", ls=":", lw=2, label="LSF$_3$ > 0.75"); ax.set_xlim(0, 1)
        if kind == "passrate":
            ax.set_ylim(0, 1.05); ax.set_ylabel("pass rate (> cut)")
        else:
            # the crosshair verticals drag the autoscale down to ~1e-5 and leave half the axis empty;
            # a hundredth of an event is already below anything worth reading off
            ax.set_yscale("log"); ax.set_ylim(1e-2, None)
            ax.set_ylabel("events above the cut")      # the lumi is in the header, not the axis
        ax.set_xlabel(f"cut on {xl} of the boosted fatjet")
        ax.grid(alpha=0.3, which="both")
        hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=16)
        # the channel goes in the legend title: as a free-floating text it lands on top of the signal
        # curves, which sit at a pass rate of ~1 across the whole left half of the axis
        ax.legend(fontsize=13, loc="lower left", ncol=2, framealpha=0.93,
                  title=f"{CHLAB[ch]}\n$m_N$ = 200 GeV, no LSF$_3$ cut", title_fontsize=13)
        fig.tight_layout(); fig.savefig(f"{a.out}/{region}_{tag}_{kind}.png", dpi=110); plt.close(fig)
        print(f"wrote {a.out}/{region}_{tag}_{kind}.png")

    if not bkg:
        continue

    # ---- stacked score template ---------------------------------------------------------------------------------
    nlin = len(bcurves[0][5])          # 200 for the taggers, 100 for LSF3
    reb = max(nlin // NSTACK, 1)
    eb = np.linspace(0, 1, nlin + 1)[::reb]
    # largest group at the bottom of the stack
    stack = sorted([(lab, colr, hlin.reshape(-1, reb).sum(axis=1)) for lab, colr, _, _, _, hlin in bcurves],
                   key=lambda s: s[2].sum(), reverse=True)
    fig, ax = plt.subplots(figsize=(12, 9))
    hep.histplot([s[2] for s in stack], eb, stack=True, histtype="fill", color=[s[1] for s in stack],
                 label=[s[0] for s in stack], ax=ax, alpha=0.85)
    ymax = sum(s[2] for s in stack).max()
    for lab, col, n, _, _, hlin in curves:
        ys = hlin.reshape(-1, reb).sum(axis=1)
        ax.stairs(ys, eb, color=col, lw=2.5, label=lab)
        ymax = max(ymax, ys.max())
    ax.set_yscale("log"); ax.set_ylim(1e-3, ymax * 3e2)
    ax.set_xlim(0, 1 if not logx else 0.8)     # the tagger scores stop at ~0.75, LSF3 runs to 1
    if not logx:
        ax.axvline(LSFCUT, color="gray", ls=":", lw=2)
    ax.set_xlabel(f"{xl} of the boosted fatjet"); ax.set_ylabel(f"events / {reb / nlin:g}")
    ax.grid(alpha=0.3, which="both")
    hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=16)
    ax.text(0.04, 0.96, CHLAB[ch], transform=ax.transAxes, va="top", fontsize=17)
    ax.legend(fontsize=13, loc="upper right", ncol=2, title="$m_N$ = 200 GeV, no LSF$_3$ cut", title_fontsize=13)
    fig.tight_layout(); fig.savefig(f"{a.out}/{region}_{tag}_stack.png", dpi=110); plt.close(fig)
    print(f"wrote {a.out}/{region}_{tag}_stack.png")

    # ---- S/sqrt(B) vs the cut -----------------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 9))
    # No marker on the maximum: it is shallow (within 1 % over roughly half a decade of cut), so a star
    # sits inside the line width of everything around it and reads as a precision the scan does not have.
    for lab, col, n, ytag, ylsf, _ in curves:
        z = np.full(len(ytag), np.nan)
        z[ok] = ytag[ok] / np.sqrt(Btag[ok])
        ax.plot(ext, z, color=col, lw=3, label=lab)
        ax.plot([xlot, 1], [ylsf[ilsf] / np.sqrt(Blsf75)] * 2, color=col, ls=":", lw=1.2, alpha=0.8)
    ax.axvline(xend, color="gray", lw=1.5, alpha=0.7)
    ax.plot([], [], color="gray", ls=":", lw=1.5, label="LSF$_3$ > 0.75 working point")
    ax.plot([], [], color="gray", lw=1.5, alpha=0.7, label=f"B < {a.bmin:g} event beyond")
    if logx:
        ax.set_xscale("log"); ax.set_xlim(XLO, 1)
    else:
        ax.set_xlim(0, 1)
    ax.set_yscale("log")
    ax.set_xlabel(f"cut on {xl} of the boosted fatjet"); ax.set_ylabel("$S/\\sqrt{B}$")
    ax.grid(alpha=0.3, which="both")
    hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=16)
    ax.legend(fontsize=13, loc="lower left", ncol=2, framealpha=0.93,
              title=f"{CHLAB[ch]}\n$m_N$ = 200 GeV, no LSF$_3$ cut", title_fontsize=13)
    fig.tight_layout(); fig.savefig(f"{a.out}/{region}_{tag}_signif.png", dpi=110); plt.close(fig)
    print(f"wrote {a.out}/{region}_{tag}_signif.png")

open(f"{a.out}/boostnolsf_passrate.md", "w").write("\n".join(md) + "\n")
print("\n".join(md)); print("BOOSTNOLSF_TAGGER_PLOTS_DONE")
