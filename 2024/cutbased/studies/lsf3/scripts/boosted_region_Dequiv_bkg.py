#!/usr/bin/env python3
"""Background in the boosted SR / Flavor CR when LSF3 > 0.75 is swapped for a D cut of the same strength.

    D = P_S / (P_S + a_top P_top + a_QCD P_QCD),  JMAR 1:1 by default
    P_S = XWWqqev for an electron inside the fatjet (SR EE, Flavor CR MEJ), XWWqqmv for a muon (SR MM, EMJ)
"Same strength": in each SR the D cut is chosen so that the lumi-weighted total background efficiency equals the
one of LSF3 > 0.75 on the same events (--match bkg), or so that the signal efficiency of --mass does (--match sig).
The Flavor CR takes the cut of the SR whose fatjet carries the same lepton flavour (EMJ <- SR MM, MEJ <- SR EE):
a cut is a cut, the CR is not re-tuned.  Errors are MC statistics only, sqrt(sum w^2).
  <out>/mlJ_<region>.png   m(lJ) stack with LSF3 > 0.75 | the same with D > c | D / LSF3 per group
  boosted_region_Dequiv_bkg.py [--match bkg|sig] [--mass 3000]"""
import argparse, glob, json, os, re
import numpy as np
import uproot
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import mplhep as hep

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--sig", default=f"{S}/trees_boosted_sig")
ap.add_argument("--bkg", default=f"{S}/trees_boosted_bkg_full")
ap.add_argument("--xsec", default=f"{S}/condor/bkg_xsec_all.json")
ap.add_argument("--sig-json", default=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(S)))), "HNWR/data/Sample/2024"))
ap.add_argument("--out", default=f"{S}/fatjet_taggers/globalpart3_D/06_lsf3_equiv")
ap.add_argument("--match", default="bkg", choices=["bkg", "sig"])
ap.add_argument("--mass", type=int, default=3000, help="signal point quoted (and matched with --match sig)")
ap.add_argument("--alpha-top", type=float, default=1.0)
ap.add_argument("--alpha-qcd", type=float, default=1.0)
a = ap.parse_args()
hep.style.use("CMS")
out = f"{a.out}_{a.match}"
os.makedirs(out, exist_ok=True)

LUMI = 109.8
LSFCUT = 0.75
TOP = ["TopbWev", "TopbWmv", "TopbWq", "TopbWqq", "TopbWtauhv"]
GROUPS = [("DYJets", "Drell-Yan", "gold"), ("TT", "$t\\bar{t}$ + tW", "tab:red"),
          ("Nonprompt", "Nonprompt", "tab:green"), ("Others", "Others", "tab:blue")]
# region: (code, isEE, P_S class, SR whose cut it takes, label)
REG = {"SR_EE":   (1, 1, "XWWqqev", "SR_EE", "boosted SR, ee"),
       "SR_MM":   (1, 0, "XWWqqmv", "SR_MM", "boosted SR, $\\mu\\mu$"),
       "FLV_EMJ": (2, 1, "XWWqqmv", "SR_MM", "boosted Flavor CR, e + $\\mu$-jet"),
       "FLV_MEJ": (2, 0, "XWWqqev", "SR_EE", "boosted Flavor CR, $\\mu$ + e-jet")}
SIGTAG = {"EE": "WRtoNEltoElElJJ", "MM": "WRtoNMutoMuMuJJ"}
EB = np.array([800, 1000, 1200, 1400, 1700, 2000, 2400, 3000, 4000, 6000], float)
BR = ["region", "isEE", "w", "lsf3", "m_lJ", "p_QCD", "p_XWWqqev", "p_XWWqqmv"] + [f"p_{t}" for t in TOP]
X = json.load(open(a.xsec))
CHUNK = re.compile(r"_c\d{3}$")


def D(A, ps):
    P = A[f"p_{ps}"]; den = P + a.alpha_top * sum(A[f"p_{t}"] for t in TOP) + a.alpha_qcd * A["p_QCD"]
    return np.where(den > 0, P / np.maximum(den, 1e-30), 0.0)


# ---- background, all regions at once ---------------------------------------------------------------------------
sumw = {}
for p in glob.glob(f"{a.bkg}/*.norm.json"):
    nm = json.load(open(p)); sumw[nm["sample"]] = sumw.get(nm["sample"], 0.0) + nm["sumw"]
cat = {k: [] for k in BR + ["grp", "scale"]}
for p in sorted(glob.glob(f"{a.bkg}/*.root")):
    s = CHUNK.sub("", os.path.basename(p)[:-5])
    if s not in X or s not in sumw:
        print(f"!! no xsec/sumw for {s}"); continue
    with uproot.open(p) as f:
        if "tagger" not in f or f["tagger"].num_entries == 0:
            continue
        A = f["tagger"].arrays(BR, library="np")
    for k in BR: cat[k].append(A[k])
    n = len(A["w"])
    cat["grp"].append(np.full(n, X[s]["group"])); cat["scale"].append(np.full(n, LUMI * 1000.0 * X[s]["xsec"] / sumw[s]))
B = {k: np.concatenate(v) for k, v in cat.items()}
B["w"] = B["w"] * B["scale"]


def sig(ch, code, isEE):
    j = json.load(open(f"{a.sig_json}/{SIGTAG[ch]}_MWR{a.mass}_N200.json"))
    with uproot.open(f"{a.sig}/{ch}_MWR{a.mass}_N200.root") as f:
        A = f["tagger"].arrays(BR, library="np")
    m = (A["region"] == code) & (A["isEE"] == isEE)
    A = {k: v[m] for k, v in A.items()}
    A["w"] = A["w"] * LUMI * 1000.0 * j["xsec"] / j["sumsign"]
    return A


def cut_at(d, w, eff):
    """Smallest D threshold whose weighted efficiency (D > c) does not exceed eff."""
    o = np.argsort(-d); c = np.cumsum(w[o]) / w.sum()
    i = min(np.searchsorted(c, eff), len(c) - 1)
    return d[o][i]


# ---- D cuts from the SRs ---------------------------------------------------------------------------------------
CUT = {}
print(f"D = P_S/(P_S + {a.alpha_top:g} P_top + {a.alpha_qcd:g} P_QCD), matched on {a.match} efficiency")
for r in ("SR_EE", "SR_MM"):
    code, isEE, ps, _, _ = REG[r]
    m = (B["region"] == code) & (B["isEE"] == isEE)
    db, wb, lb = D(B, ps)[m], B["w"][m], B["lsf3"][m]
    Sg = sig(r[-2:], code, isEE); ds = D(Sg, ps)
    eb_l = wb[lb > LSFCUT].sum() / wb.sum(); es_l = Sg["w"][Sg["lsf3"] > LSFCUT].sum() / Sg["w"].sum()
    c = cut_at(db, wb, eb_l) if a.match == "bkg" else cut_at(ds, Sg["w"], es_l)
    eb_d = wb[db > c].sum() / wb.sum(); es_d = Sg["w"][ds > c].sum() / Sg["w"].sum()
    CUT[r] = (c, es_l, es_d)
    print(f"  {r}: LSF3>{LSFCUT}: bkg {eb_l*100:5.1f}%  sig{a.mass//1000} {es_l*100:5.1f}%   |   "
          f"D>{c:.4f}: bkg {eb_d*100:5.1f}%  sig{a.mass//1000} {es_d*100:5.1f}%")


def hist(x, w):
    h = np.histogram(np.clip(x, EB[0], EB[-1] - 1e-3), EB, weights=w)[0]
    e2 = np.histogram(np.clip(x, EB[0], EB[-1] - 1e-3), EB, weights=w * w)[0]
    return h, np.sqrt(e2)


for r, (code, isEE, ps, src, lab) in REG.items():
    c, es_l, es_d = CUT[src]
    m = (B["region"] == code) & (B["isEE"] == isEE)
    d = D(B, ps)
    sel = {"L": m & (B["lsf3"] > LSFCUT), "D": m & (d > c)}
    H = {k: {g: hist(B["m_lJ"][s & (B["grp"] == g)], B["w"][s & (B["grp"] == g)]) for g, _, _ in GROUPS}
         for k, s in sel.items()}
    T = {k: (sum(H[k][g][0] for g, _, _ in GROUPS), np.sqrt(sum(H[k][g][1] ** 2 for g, _, _ in GROUPS)))
         for k in H}

    print(f"\n== {r}  (D > {c:.4f}, from {src})")
    print(f"   {'':12s} {'no cut':>16s} {'LSF3>0.75':>18s} {'D cut':>18s} {'D/LSF3':>7s}")
    for g, gl, _ in GROUPS + [("tot", "total", None)]:
        gm = m if g == "tot" else m & (B["grp"] == g)
        y = [(B["w"][gm & s].sum(), np.sqrt((B["w"][gm & s] ** 2).sum())) for s in (m, sel["L"], sel["D"])]
        print(f"   {g:12s} " + " ".join(f"{v:9.2f}±{e:6.2f}" for v, e in y)
              + f" {y[2][0] / y[1][0] if y[1][0] else float('nan'):7.2f}")

    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(2, 2, height_ratios=[2.2, 1], hspace=0.08, wspace=0.06)
    axL, axD = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    axR = fig.add_subplot(gs[1, :])
    order = sorted(GROUPS, key=lambda g: H["L"][g[0]][0].sum())
    ymax = max(T["L"][0].max(), T["D"][0].max())
    ymin = max(1e-2, min(v[v > 0].min() for v in (T["L"][0], T["D"][0]) if (v > 0).any()) * 0.3)
    for ax, k, ttl in ((axL, "L", f"LSF$_3$ > {LSFCUT:g}"),
                       (axD, "D", f"D > {c:.3f}  ({'bkg' if a.match == 'bkg' else 'sig'}-eff. matched)")):
        hep.histplot([H[k][g][0] for g, _, _ in order], EB, stack=True, histtype="fill",
                     color=[col for _, _, col in order], label=[gl for _, gl, _ in order], ax=ax, alpha=0.85)
        t, e = T[k]
        ax.stairs(t + e, EB, baseline=np.maximum(t - e, 1e-9), fill=False, hatch="///", color="0.25", lw=0,
                  label="stat. unc.")
        ax.set_yscale("log"); ax.set_ylim(ymin, ymax * 200); ax.set_xlim(EB[0], EB[-1])
        ax.set_xticklabels([]); ax.grid(alpha=0.3, which="both")
        es = es_l if k == "L" else es_d
        ax.legend(fontsize=12, ncol=2, loc="upper right",
                  title=f"{lab}\n{ttl}\ntotal bkg {t.sum():.1f} ± {np.sqrt((e**2).sum()):.1f};  "
                        f"$W_R$ {a.mass/1000:g} TeV eff. {es*100:.0f}%", title_fontsize=12)
        hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=15)
    axL.set_ylabel("events / bin"); axD.set_yticklabels([])
    for g, gl, col in GROUPS + [("tot", "total", "black")]:
        (hl, el), (hd, ed) = (T["L"], T["D"]) if g == "tot" else (H["L"][g], H["D"][g])
        ok = hl > 0
        rr = np.full(len(hl), np.nan); er = np.full(len(hl), np.nan)
        rr[ok] = hd[ok] / hl[ok]
        er[ok] = rr[ok] * np.sqrt((ed[ok] / np.maximum(hd[ok], 1e-12)) ** 2 + (el[ok] / hl[ok]) ** 2)
        xc = 0.5 * (EB[1:] + EB[:-1])
        off = {"DYJets": -0.15, "TT": -0.05, "Nonprompt": 0.05, "Others": 0.15, "tot": 0}[g] * np.diff(EB)
        axR.errorbar(xc + off, rr, yerr=er, fmt="o" if g == "tot" else "s", color=col, ms=8 if g == "tot" else 5,
                     lw=2 if g == "tot" else 1.2, capsize=3, label=gl, zorder=5 if g == "tot" else 3)
    axR.axhline(1, color="0.5", ls=":")
    axR.set_xlim(EB[0], EB[-1]); axR.set_ylim(0, 3)
    axR.set_xlabel("$m(\\ell J)$ [GeV]"); axR.set_ylabel("D cut / LSF$_3$ cut")
    axR.grid(alpha=0.3); axR.legend(fontsize=11, ncol=5, loc="upper left")
    fig.savefig(f"{out}/mlJ_{r}.png", dpi=100, bbox_inches="tight"); plt.close(fig)
    print(f"   wrote {out}/mlJ_{r}.png")
print("DONE")
