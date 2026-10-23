#!/usr/bin/env python3
"""Tagger and LSF3 working points in one plot, on the boosted fatjet selection (boosted_fatjet_tagger_hists.py output).
One figure per channel: x = what the cut keeps, left y axis = 1 - tagger cut (XWWqqev for EE, XWWqqmv for MM),
right y axis = LSF3 cut. Solid curves are read on the left axis, dashed curves on the right axis; one colour per sample,
signal (N = 200, xsec x LUMI) and background (DY, TTLL + tW; xsec / sumW x LUMI) together.
  <out>/<CH>_N200_cutvs_passrate.png  x = pass rate of that sample
  <out>/<CH>_N200_cutvs_yield.png     x = events above the cut (log x)
  boosted_fatjet_roc_plots.py [--sig-hists ...] [--bkg-hists ...] [--out .../fatjet_taggers/boosted_fatjet]"""
import argparse, glob, json, os
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import mplhep as hep

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--sig-hists", default=f"{S}/hists_boosted_sig")
ap.add_argument("--bkg-hists", default=f"{S}/hists_boosted_bkg")
ap.add_argument("--xsec", default=f"{S}/condor/bkg_xsec.json")
ap.add_argument("--out", default=f"{S}/fatjet_taggers/boosted_fatjet")
ap.add_argument("--sig-json", default=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(S)))), "HNWR/data/Sample/2024"))
a = ap.parse_args()
LUMI = 109.8
NB = 200
LSFCUT = 0.75
SIGTAG = {"EE": "WRtoNEltoElElJJ", "MM": "WRtoNMutoMuMuJJ"}
TAGOF = {"EE": ("XWWqqev", "GlobalParT3 XWW(qq e$\\nu$)"), "MM": ("XWWqqmv", "GlobalParT3 XWW(qq $\\mu\\nu$)")}
CHLAB = {"EE": "$W_R \\to eN \\to eejj$", "MM": "$W_R \\to \\mu N \\to \\mu\\mu jj$"}
hep.style.use("CMS")
os.makedirs(a.out, exist_ok=True)

X = json.load(open(a.xsec))
bkg = {g: {ch: {"n": 0.0, "h": {}, "hl": {}} for ch in ("EE", "MM")} for g in ("DY", "TT")}
for p in sorted(glob.glob(f"{a.bkg_hists}/*.npz")):
    r = np.load(p); x = X[str(r["sample"])]; f = x["xsec"] / x["sumW"]; g = x["group"]
    for ch in ("EE", "MM"):
        bkg[g][ch]["n"] += f * float(r[f"n_{ch}"])
        for t in ("XWWqqev", "XWWqqmv", "lsf3"):
            bkg[g][ch]["h"][t] = bkg[g][ch]["h"].get(t, 0) + f * r[f"h_{ch}_{t}"]
            if f"h_{ch}_{t}_log" in r.files: bkg[g][ch]["hl"][t] = bkg[g][ch]["hl"].get(t, 0) + f * r[f"h_{ch}_{t}_log"]
sig, LOGE = {}, None
for p in glob.glob(f"{a.sig_hists}/*_N200.npz"):
    ch, m = os.path.basename(p).split("_")[:2]; d = dict(np.load(p)); sig[(ch, int(m[3:]))] = d
    if "log_edges" in d: LOGE = d["log_edges"]
scale = {}
for (ch, m) in sig:
    sj = json.load(open(f"{a.sig_json}/{SIGTAG[ch]}_MWR{m}_N200.json")); scale[(ch, m)] = LUMI * 1000.0 * sj["xsec"] / sj["sumsign"]

def cum(h): return np.cumsum(h[::-1])[::-1]
e = np.linspace(0, 1, NB + 1)
n = 0
for ch in ("EE", "MM"):
    tag, tlab = TAGOF[ch]
    masses = sorted(m for (c, m) in sig if c == ch); cmap = plt.get_cmap("viridis")(np.linspace(0, 0.95, len(masses)))
    uselog = LOGE is not None and tag in bkg["DY"][ch]["hl"]
    etag = LOGE if uselog else e          # cut values of the tagger curves
    # samples: (label, colour, tagger hist, lsf3 hist, denominator, yield scale)
    samples = [(f"$m_{{W_R}}$ = {m / 1000:g} TeV", cmap[k],
                sig[(ch, m)][f"h_{ch}_{tag}_log"] if uselog else sig[(ch, m)][f"h_{ch}_{tag}"],
                sig[(ch, m)][f"h_{ch}_lsf3"], sig[(ch, m)][f"n_{ch}"], scale[(ch, m)]) for k, m in enumerate(masses)]
    # one background: DY + TTLL + tW summed (already xsec / sumW weighted)
    bt = sum(bkg[g][ch]["hl"][tag] if uselog else bkg[g][ch]["h"][tag] for g in ("DY", "TT"))
    bl = sum(bkg[g][ch]["h"]["lsf3"] for g in ("DY", "TT"))
    bn = sum(bkg[g][ch]["n"] for g in ("DY", "TT"))
    samples += [("Background (DY + TTLL + tW)", "tab:red", bt, bl, bn, LUMI * 1000.0)]
    for kind in ("passrate", "yield"):
        fig, axl = plt.subplots(figsize=(13, 9)); axr = axl.twinx()
        for lab, col, ht, hl, nsel, sc in samples:
            xt = cum(ht) / nsel if kind == "passrate" else sc * cum(ht)      # what the tagger cut keeps
            xl_ = cum(hl) / nsel if kind == "passrate" else sc * cum(hl)     # what the LSF3 cut keeps
            lw = 4 if lab.startswith("Background") else 2.3
            axl.plot(xt, 1 - etag[:-1], color=col, ls="-", lw=lw, label=lab)
            axr.plot(xl_, e[:-1], color=col, ls="--", lw=lw)
            i = int(round(LSFCUT * NB))
            axr.plot([xl_[i]], [LSFCUT], marker="o", ms=7, color=col)
        axl.plot([], [], color="gray", ls="-", lw=2.5, label="tagger (left axis)")
        axl.plot([], [], color="gray", ls="--", lw=2.5, label="LSF$_3$ (right axis)")
        axl.plot([], [], color="gray", ls="none", marker="o", ms=7, label="LSF$_3$ > 0.75")
        axl.set_xlabel("pass rate of the cut" if kind == "passrate" else "events above the cut")
        axl.set_ylabel(f"1 - {tlab} cut")
        axr.set_ylabel("LSF$_3$ cut")
        axl.set_ylim(0, 1.02); axr.set_ylim(0, 1.02)
        if kind == "passrate":
            axl.set_xlim(0, 1)
        else:
            axl.set_xscale("log"); axl.set_xlim(1e-2, 3e5)
        axl.grid(alpha=0.3, which="both")
        hep.cms.label("Work in progress", data=False, com=13.6, ax=axl, fontsize=15,
                      rlabel="(13.6 TeV)" if kind == "passrate" else f"{LUMI} fb$^{{-1}}$ (13.6 TeV)")
        axl.text(0.03, 0.97, CHLAB[ch], transform=axl.transAxes, va="top", fontsize=16)
        axl.legend(fontsize=12, loc="lower left", ncol=2, title="$m_N$ = 200 GeV, boosted fatjet selection", title_fontsize=12)
        fig.tight_layout(); fig.savefig(f"{a.out}/{ch}_N200_cutvs_{kind}.png", dpi=110); plt.close(fig); n += 1
        print(f"drew {a.out}/{ch}_N200_cutvs_{kind}.png", flush=True)
print(f"{n} plots"); print("BOOSTED_FATJET_ROC_PLOTS_DONE")
