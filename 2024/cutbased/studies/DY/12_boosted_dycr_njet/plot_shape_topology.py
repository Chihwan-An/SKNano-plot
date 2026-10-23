#!/usr/bin/env python3
"""FxFx / LO Z pT *shape* ratio: inclusive vs resolved vs boosted topology (2026-09-23).

Top row (reco, exact analysis topology; CF_Tree dumps, LO without DY correction = weight / w_dy, FxFx w_dy = 1):
  Incl      hasPair, 60 <= m_ll < 150, any jets
  Resolved  isDYCR (>= 2 AK4, all dR > 0.4, m_lljj > 800)
  Boosted   isBoostedDYCR && !passResolved (resolved topology fails, back-to-back fat jet, m_lN > 800)
  pT(ll) = l1 + l2 (Incl, Resolved), lead + DY-pair loose lepton l4 (Boosted). FxFx dumps have no gen information.
Bottom row (gen, from 11_fatjet_category json): Incl, GenJ2 (>= 2 AK4 GenJets), GenFJ1x (>= 1 AK8 and < 2 AK4) -- count-based
  approximation of the boosted topology, m_ll 60-150.
Shapes are unit-normalised inside NORM (the range where all three reco categories are populated), so the ratio compares the
pT dependence only; the absolute FxFx/LO of each category is printed in the legend.
    python3 plot_shape_topology.py"""
import glob, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
D0 = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test/data/chargeflip"
GEN_JSON = os.path.join(HERE, "..", "11_fatjet_category", "plots", "zpt_ratio_by_jetcat_2024.json")
OUT = os.path.join(HERE, "plots")
COLS = ["channel", "isBoostedDYCR", "passResolved", "isDYCR", "hasPair", "m_l1l2", "pt_l1l2", "weight", "w_dy",
        "l1_pt", "l1_phi", "l4_pt", "l4_phi"]
EDR = np.array([200, 250, 300, 350, 400, 500, 600, 800, 1000.])
NORM = (200., 1000.)
CATS = {"Incl": ("inclusive (60<m_ll<150)", "0.3"), "Resolved": ("resolved DY CR", "tab:red"), "Boosted": ("boosted DY CR (resolved fail)", "tab:blue")}


def load(pat):
    parts = {c: [] for c in COLS}
    for f in sorted(glob.glob(pat)):
        d = np.load(f)
        for c in COLS: parts[c].append(d[c].astype(np.float64))
    d = {c: np.concatenate(v) for c, v in parts.items()}
    B = (d["isBoostedDYCR"] > 0) & (d["passResolved"] < 0.5)
    zb = np.hypot(d["l1_pt"] * np.cos(d["l1_phi"]) + d["l4_pt"] * np.cos(d["l4_phi"]),
                  d["l1_pt"] * np.sin(d["l1_phi"]) + d["l4_pt"] * np.sin(d["l4_phi"]))
    d["zpt"] = np.where(B, zb, d["pt_l1l2"])
    d["cat"] = {"Incl": (d["hasPair"] > 0) & (d["m_l1l2"] >= 60) & (d["m_l1l2"] < 150), "Resolved": d["isDYCR"] > 0, "Boosted": B}
    return d


def h(x, w):
    return np.histogram(x, EDR, weights=w)[0], np.histogram(x, EDR, weights=w ** 2)[0]


lo = load(f"{D0}/dumps_dynew_dy/*.npz"); fx = load(f"{D0}/dumps_fxfx/*.npz")
wlo = lo["weight"] / lo["w_dy"]; wfx = fx["weight"]
G = json.load(open(GEN_JSON))["mll60to150"]
GCATS = {"Incl": ("all events", "0.3"), "GenJ2": (r"$\geq$2 AK4 GenJets", "tab:red"), "GenFJ1x": (r"$\geq$1 AK8 and <2 AK4 GenJets", "tab:blue")}

res = {"edges": EDR.tolist(), "norm": NORM, "reco": {}, "gen_source": GEN_JSON}
fig, axes = plt.subplots(2, 2, figsize=(12, 8.5), sharey=True)
c = np.sqrt(EDR[:-1] * EDR[1:])
for j, (ch, cid) in enumerate((("EE", 11), ("MM", 13))):
    ax = axes[0, j]
    for k, (lab, col) in CATS.items():
        ml = lo["cat"][k] & (lo["channel"] == cid) & (lo["zpt"] >= NORM[0]) & (lo["zpt"] < NORM[1])
        mf = fx["cat"][k] & (fx["channel"] == cid) & (fx["zpt"] >= NORM[0]) & (fx["zpt"] < NORM[1])
        hl, vl = h(lo["zpt"][ml], wlo[ml]); hf, vf = h(fx["zpt"][mf], wfx[mf])
        K = hf.sum() / hl.sum(); r = (hf / hf.sum()) / (hl / hl.sum())
        re = r * np.sqrt(vf / hf ** 2 + vl / hl ** 2)   # bin stat; normalisation correlation neglected
        res["reco"].setdefault(ch, {})[k] = {"shape_ratio": r.tolist(), "err": re.tolist(), "K_in_norm": K,
                                             "sumw_lo": hl.sum(), "sumw_fx": hf.sum()}
        off = {"Incl": 0.97, "Resolved": 1.0, "Boosted": 1.03}[k]
        ax.errorbar(c * off, r, re, fmt="o-", ms=4, lw=1, color=col, capsize=2, label=f"{lab}  (FxFx/LO abs {K:.2f})")
    ax.set_title(f"{ch}, reco (exact topology): FxFx / LO shape, norm. {NORM[0]:.0f}-{NORM[1]:.0f}", fontsize=10)
    ax.set_xlabel(r"reco $p_T(\ell\ell)$ [GeV]")
    # gen, count-based categories (lepton flavour not split in the gen study)
    gx = axes[1, j]
    e = np.array(G["Incl"]["edges"]); sel = (e[:-1] >= NORM[0]) & (e[1:] <= NORM[1]); gc = np.sqrt(np.maximum(e[:-1], 5) * e[1:])
    for k, (lab, col) in GCATS.items():
        g = G[k]; lo_ = np.array(g["lo"])[sel]; fx_ = np.array(g["fxfx"])[sel]
        r = (fx_ / fx_.sum()) / (lo_ / lo_.sum())
        rel = np.array(g["err"])[sel] / np.maximum(np.array(g["shape_ratio"])[sel], 1e-9)   # relative bin error from study 11
        gx.errorbar(gc[sel], r, r * rel, fmt="s--", ms=3, lw=1, color=col, capsize=2, label=f"{lab}  (K {g['K']:.2f})")
    gx.set_title(f"gen (study 11, ee+μμ), count-based categories, m_ll 60-150", fontsize=10)
    gx.set_xlabel(r"gen $p_T(Z)$ [GeV]")
for ax in axes.flat:
    ax.axhline(1, color="k", lw=0.8, ls=":"); ax.set_xscale("log"); ax.set_xlim(190, 1050); ax.set_ylim(0.5, 1.5)
    ax.set_xticks([200, 300, 400, 500, 700, 1000]); ax.set_xticklabels(["200", "300", "400", "500", "700", "1000"])
    ax.legend(fontsize=8, loc="lower left")
for ax in axes[:, 0]: ax.set_ylabel("FxFx / LO (shape, unit area in norm. range)")
fig.tight_layout(); fig.savefig(f"{OUT}/zpt_shape_ratio_topology.png", dpi=130); fig.savefig(f"{OUT}/zpt_shape_ratio_topology.pdf")
json.dump(res, open(f"{OUT}/zpt_shape_ratio_topology.json", "w"), indent=1)
print("reco shape ratio (norm %d-%d), bins %s" % (NORM[0], NORM[1], EDR.astype(int).tolist()))
for ch, d in res["reco"].items():
    for k, x in d.items():
        print(f"{ch} {k:9s} abs {x['K_in_norm']:.3f} " + " ".join(f"{v:.2f}±{s:.2f}" for v, s in zip(x["shape_ratio"], x["err"])))
