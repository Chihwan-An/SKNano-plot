#!/usr/bin/env python3
"""The JMAR discriminant in the boosted SR, over the FULL background, as yields / raw entries / shapes.

    P_top = TopbWqq + TopbWq + TopbWev + TopbWmv + TopbWtauhv
    D     = P_S / (P_S + a_top P_top + a_QCD P_QCD)     P_S = XWWqqev (SR EE) / XWWqqmv (SR MM)
Defaults follow the JMAR recommendation, a_top = a_QCD = 1: the alpha scan (boosted_sr_qcd_term.py) puts the
optimum at a_QCD of a few with an AUC gain of 0.002 over 1:1, which is not worth tuning for.

Background: every chunk under --bkg, each sample scaled by xsec / (sum of genEventSumw over its own chunks) and
then summed into the four analysis groups of plot/cutbased/config.py, so the stack matches the main analysis.
Signal: xsec / sumsign from the per-point registry json.
  <out>/Dyield_<region>.png   stacked background + signal overlay, events at the 2024 lumi
  <out>/Draw_<region>.png     the same as raw tree entries -- the MC statistics behind the yields
  <out>/Dnorm_<region>.png    every group to unit area: shape only, normalised from the WEIGHTED histogram
  <out>/Dcut_<region>.png     where to actually cut: signal / background efficiency and S/sqrt(B) against the cut
                              on D.  AUC and the ROC say how well D separates but say nothing about the cut,
                              and the cut that corresponds to a given selection moves when a_top / a_QCD change.
  boosted_sr_D_yield.py [--alpha-top 1] [--alpha-qcd 1]"""
import argparse, glob, json, os, re, sys
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import mplhep as hep
import ROOT

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(S)))      # plot/cutbased, for config.py
import config

ap = argparse.ArgumentParser()
ap.add_argument("--sig", default=f"{S}/trees_boosted_sig")
ap.add_argument("--bkg", default=f"{S}/trees_boosted_bkg_full")
ap.add_argument("--xsec", default=f"{S}/condor/bkg_xsec_all.json")
ap.add_argument("--sig-json", default=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(S)))), "HNWR/data/Sample/2024"))
ap.add_argument("--out", default=f"{S}/fatjet_taggers/globalpart3_D/02_discriminant")
ap.add_argument("--alpha-top", type=float, default=1.0)
ap.add_argument("--alpha-qcd", type=float, default=1.0)
ap.add_argument("--alpha-map", default=None,
                help="per-region override, e.g. 'SR_EE:1:2.37,SR_MM:1:75'; only the ratio matters, so these are "
                     "the alpha=1 form of the (alpha, beta) that maximises AUC in the 2D scan")
ap.add_argument("--masses", default="1000,3000,5000,7000")
ap.add_argument("--eff-lines", default="0.9,0.8,0.7", help="signal efficiencies to mark with a vertical line")
ap.add_argument("--eff-mass", type=int, default=3000, help="mass point those efficiencies refer to")
a = ap.parse_args()
ROOT.gROOT.SetBatch(True)
hep.style.use("CMS")
os.makedirs(a.out, exist_ok=True)

AMAP = {}
if a.alpha_map:
    for e in a.alpha_map.split(","):
        r, at, ab = e.split(":"); AMAP[r] = (float(at), float(ab))

LUMI = 109.8
TOP = ["TopbWev", "TopbWmv", "TopbWq", "TopbWqq", "TopbWtauhv"]
MASSES = [int(m) for m in a.masses.split(",")]
SIGTAG = {"EE": "WRtoNEltoElElJJ", "MM": "WRtoNMutoMuMuJJ"}
REG = {"SR_EE": ("isEE==1", "XWWqqev", "$W_R \\to eN \\to eejj$, boosted SR"),
       "SR_MM": ("isEE==0", "XWWqqmv", "$W_R \\to \\mu N \\to \\mu\\mu jj$, boosted SR")}
# same groups and colours as the main analysis plots (config keeps them as ROOT constants)
ROOTCOL = {"kYellow": "gold", "kRed": "tab:red", "kGreen+2": "tab:green", "kBlue": "tab:blue"}
GLAB = {"DYJets": "Drell-Yan", "TT": "$t\\bar{t}$ + tW", "Nonprompt": "Nonprompt", "Others": "Others"}
GROUPS = [(g, GLAB.get(g, g), ROOTCOL.get(c, "gray")) for g, (c, _) in config.BACKGROUND_GROUPS.items()]
COL = plt.cm.viridis(np.linspace(0, 0.92, len(MASSES)))
EB = np.linspace(0, 1, 26)
X = json.load(open(a.xsec))
CHUNK = re.compile(r"_c\d{3}$")


def disc(path, sel, sig_name, at, ab):
    """D and the event weight of every selected event of one tree."""
    d = ROOT.RDataFrame("tagger", path).Filter(f"region==1 && {sel}")
    A = d.AsNumpy([f"p_{sig_name}", "p_QCD", "w"] + [f"p_{t}" for t in TOP])
    if len(A["w"]) == 0:
        return None
    Ps = A[f"p_{sig_name}"]; Pt = sum(A[f"p_{t}"] for t in TOP); Pq = A["p_QCD"]
    den = Ps + at * Pt + ab * Pq
    return np.where(den > 0, Ps / np.maximum(den, 1e-30), 0.0), A["w"]


# genEventSumw per sample, summed over that sample's chunks
sumw = {}
for p in sorted(glob.glob(f"{a.bkg}/*.norm.json")):
    nm = json.load(open(p)); sumw[nm["sample"]] = sumw.get(nm["sample"], 0.0) + nm["sumw"]

for region, (sel, sig_name, chlab) in REG.items():
    ch = region.split("_")[1]
    AT, AB = AMAP.get(region, (a.alpha_top, a.alpha_qcd))
    sig = []
    for m, col in zip(MASSES, COL):
        f = f"{a.sig}/{ch}_MWR{m}_N200.root"
        r = disc(f, sel, sig_name, AT, AB) if os.path.exists(f) else None
        if r is None:
            continue
        j = json.load(open(f"{a.sig_json}/{SIGTAG[ch]}_MWR{m}_N200.json"))
        sig.append((f"$m_{{W_R}}$ = {m / 1000:g} TeV", col, r[0], r[1] * (LUMI * 1000.0 * j["xsec"] / j["sumsign"])))

    grp = {g: {"D": [], "w": [], "n": 0} for g, _, _ in GROUPS}
    missing = set()
    for p in sorted(glob.glob(f"{a.bkg}/*.root")):
        s = CHUNK.sub("", os.path.basename(p)[:-5])
        if s not in X or s not in sumw:
            missing.add(s); continue
        r = disc(p, sel, sig_name, AT, AB)
        if r is None:
            continue
        g = X[s]["group"]
        grp[g]["D"].append(r[0]); grp[g]["w"].append(r[1] * (LUMI * 1000.0 * X[s]["xsec"] / sumw[s])); grp[g]["n"] += 1
    if missing:
        print(f"!! {region}: no xsec/sumw for {sorted(missing)}")
    bkg = [(lab, col, np.concatenate(grp[g]["D"]), np.concatenate(grp[g]["w"]))
           for g, lab, col in GROUPS if grp[g]["D"]]
    if not sig or not bkg:
        continue

    print(f"\n== {region}  (a_top = {AT:g}, a_QCD = {AB:g})")
    tot = totcut = 0.0
    for lab, _, D, w in bkg:
        y, yc = w.sum(), w[D > 0.5].sum(); tot += y; totcut += yc
        print(f"   {lab:16s} raw {len(D):7d}  yield {y:9.2f}  D>0.5 {yc:8.2f}  ({yc / y * 100:5.1f}%)")
    print(f"   {'배경 합':16s}             yield {tot:9.2f}  D>0.5 {totcut:8.2f}  ({totcut / tot * 100:5.1f}%)")
    for lab, _, D, w in sig:
        y, yc = w.sum(), w[D > 0.5].sum()
        print(f"   {lab.replace('$m_{W_R}$ = ', 'W_R '):16s} raw {len(D):7d}  yield {y:9.2f}  D>0.5 {yc:8.2f}  "
              f"({yc / y * 100:5.1f}%)   S/sqrt(B): {y / np.sqrt(tot):7.2f} -> {yc / np.sqrt(totcut):7.2f}")

    for kind in ("yield", "raw", "norm"):
        fig, ax = plt.subplots(figsize=(12, 9))

        def hist(D, w):
            h = np.histogram(D, bins=EB, weights=(np.ones_like(w) if kind == "raw" else w))[0]
            return h / h.sum() if kind == "norm" and h.sum() > 0 else h

        ymax = 0.0
        if kind == "norm":        # shapes: a stack would hide them
            for lab, col, D, w in bkg:
                h = hist(D, w); ax.stairs(h, EB, color=col, lw=4, ls="--", label=lab); ymax = max(ymax, h.max())
        else:
            # smallest first: histplot stacks the first entry at the bottom, so this puts the biggest on top
            st = sorted([(lab, col, hist(D, w)) for lab, col, D, w in bkg], key=lambda s: s[2].sum())
            hep.histplot([s[2] for s in st], EB, stack=True, histtype="fill", color=[s[1] for s in st],
                         label=[s[0] for s in st], ax=ax, alpha=0.85)
            ymax = sum(s[2] for s in st).max()
        for lab, col, D, w in sig:
            h = hist(D, w); ax.stairs(h, EB, color=col, lw=2.5, label=lab); ymax = max(ymax, h.max())
        if kind == "yield" and a.eff_lines:
            # where the cut keeps a given fraction of ONE mass point: signal efficiency is mass dependent,
            # so the lines are tied to --eff-mass and mean nothing for the other curves
            ref = [(l, D, w) for l, _, D, w in sig if f"{a.eff_mass / 1000:g} TeV" in l]
            if ref:
                _, Dr, wr = ref[0]
                o = np.argsort(-Dr); c = np.cumsum(wr[o]) / wr.sum()
                for e in [float(x) for x in a.eff_lines.split(",")]:
                    dcut = Dr[o][min(np.searchsorted(c, e), len(c) - 1)]
                    ax.axvline(dcut, color="0.35", ls="--", lw=1.6, alpha=0.9)
                    ax.text(dcut, ymax * 8, f"{e * 100:.0f}%", rotation=90, ha="right", va="top",
                            fontsize=12, color="0.35")
                ax.plot([], [], color="0.35", ls="--", lw=1.6,
                        label=f"signal eff. ({a.eff_mass / 1000:g} TeV)")
        ax.set_yscale("log")
        ax.set_ylim({"raw": 0.5, "yield": 1e-3, "norm": 1e-4}[kind], ymax * (30 if kind == "norm" else 3e2))
        ax.set_xlim(0, 1)
        ax.set_xlabel(f"$D = P_S\\,/\\,(P_S + {AT:g}P_{{top}} + {AB:g}P_{{QCD}})$")
        ax.set_ylabel({"raw": "raw tree entries / 0.04", "yield": "events / 0.04",
                       "norm": "fraction of events / 0.04"}[kind])
        ax.grid(alpha=0.3, which="both")
        if kind == "yield":
            hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=16)
        else:
            hep.cms.label("Work in progress", data=False, com=13.6, ax=ax, fontsize=16, rlabel="(13.6 TeV)")
        note = {"yield": "", "raw": "\nMC statistics, not a yield", "norm": "\nshapes, each to unit area"}[kind]
        ax.legend(fontsize=12, loc="upper center", ncol=2, framealpha=0.93,
                  title=f"{chlab}\n$m_N$ = 200 GeV{note}", title_fontsize=12)
        name = {"yield": "Dyield", "raw": "Draw", "norm": "Dnorm"}[kind]
        fig.tight_layout(); fig.savefig(f"{a.out}/{name}_{region}.png", dpi=110); plt.close(fig)
        print(f"   wrote {a.out}/{name}_{region}.png")

    # ---- where to cut ---------------------------------------------------------------------------------------------
    cuts = np.linspace(0, 0.995, 200)
    Db = np.concatenate([D for _, _, D, _ in bkg]); Wb = np.concatenate([w for _, _, _, w in bkg])
    Bof = np.array([Wb[Db > c].sum() for c in cuts])
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(12, 11), sharex=True,
                                  gridspec_kw={"height_ratios": [1, 1.3], "hspace": 0.07})
    ax.plot(cuts, Bof / Bof[0], color="black", lw=3, ls="--", label="background (all)")
    for lab, col, D, w in sig:
        Sof = np.array([w[D > c].sum() for c in cuts])
        ax.plot(cuts, Sof / Sof[0], color=col, lw=2.5, label=lab)
        ok = Bof >= 1.0                       # below one background event S/sqrt(B) diverges on MC that ran out
        z = np.full(len(cuts), np.nan); z[ok] = Sof[ok] / np.sqrt(Bof[ok])
        ax2.plot(cuts, z / z[0], color=col, lw=2.5, label=lab)
    ax.set_yscale("log"); ax.set_ylim(1e-3, 2); ax.set_ylabel("efficiency of the cut")
    ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=11, loc="lower left", ncol=2,
                                                title=f"{chlab}\n$m_N$ = 200 GeV", title_fontsize=11)
    hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=15)
    ax2.axhline(1.0, color="0.6", ls=":", lw=2)
    ax2.set_ylabel("$S/\\sqrt{B}$  (relative to no cut)")
    ax2.set_xlabel(f"cut on $D = P_S/(P_S + {AT:g}P_{{top}} + {AB:g}P_{{QCD}})$")
    ax2.set_xlim(0, 1); ax2.grid(alpha=0.3, which="both")
    ax2.text(0.02, 0.95, f"drawn only where at least one background event survives (D < {cuts[Bof >= 1][-1]:.3f})",
             transform=ax2.transAxes, va="top", fontsize=12, color="0.35")
    fig.savefig(f"{a.out}/Dcut_{region}.png", dpi=110, bbox_inches="tight"); plt.close(fig)
    print(f"   wrote {a.out}/Dcut_{region}.png")
    print(f"   {'cut':>6s} {'bkg':>9s} {'bkg eff':>8s}" + "".join(f"{l.replace('$m_{W_R}$ = ','')[:7]:>9s}" for l, _, _, _ in sig))
    for c in (0.0, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95):
        b = Wb[Db > c].sum()
        row = f"   {c:6.2f} {b:9.2f} {b / Bof[0] * 100:7.1f}%"
        for lab, _, D, w in sig:
            ss = w[D > c].sum()
            row += f"{(ss / np.sqrt(b) if b > 0 else float('nan')):9.2f}"
        print(row + "   <- S/sqrt(B)")
print("BOOSTED_SR_D_YIELD_DONE")
