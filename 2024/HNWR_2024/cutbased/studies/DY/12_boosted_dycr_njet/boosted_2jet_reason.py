#!/usr/bin/env python3
"""Boosted DY CR events with >= 2 AK4 jets: why do they fail the resolved topology, and does their FxFx/LO Z pT shape
match the resolved DY CR? (2026-09-23)
Resolved topology (HNWR_ChargeFlip.cc:302, HNWR.cc:1996): exactly two tight SF leptons (hasPair) and >= 2 AK4 jets with
dR(j,l) > 0.4 for both leading jets, dR(l1,l2) > 0.4, dR(j1,j2) > 0.4. The dump has no jet phi, so the last class
("hasPair, dR(ll) > 0.4") is the jet-lepton / jet-jet overlap remainder.
    python3 boosted_2jet_reason.py"""
import glob, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "plots")
D0 = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test/data/chargeflip"
COLS = ["channel", "isBoostedDYCR", "passResolved", "isDYCR", "hasPair", "nJet", "n_genjet", "weight", "w_dy",
        "l1_pt", "l1_eta", "l1_phi", "l2_eta", "l2_phi", "l4_pt", "l4_eta", "l4_phi", "pt_l1l2", "l4_inFatJet"]
EDR = np.array([200, 250, 300, 350, 400, 500, 600, 800, 1000.])


def load(pat):
    parts = {c: [] for c in COLS}
    for f in sorted(glob.glob(pat)):
        d = np.load(f)
        for c in COLS: parts[c].append(d[c].astype(np.float64))
    d = {c: np.concatenate(v) for c, v in parts.items()}
    d["B"] = (d["isBoostedDYCR"] > 0) & (d["passResolved"] < 0.5)
    dphi = np.abs((d["l1_phi"] - d["l2_phi"] + np.pi) % (2 * np.pi) - np.pi)
    d["dRll"] = np.where(d["hasPair"] > 0, np.hypot(d["l1_eta"] - d["l2_eta"], dphi), -1)
    zb = np.hypot(d["l1_pt"] * np.cos(d["l1_phi"]) + d["l4_pt"] * np.cos(d["l4_phi"]),
                  d["l1_pt"] * np.sin(d["l1_phi"]) + d["l4_pt"] * np.sin(d["l4_phi"]))
    d["zpt"] = np.where(d["B"], zb, d["pt_l1l2"])
    return d


lo = load(f"{D0}/dumps_dynew_dy/*.npz"); fx = load(f"{D0}/dumps_fxfx/*.npz")
wn = lo["weight"]; wr = lo["weight"] / lo["w_dy"]
L = ["## boosted DY CR, reco nJet >= 2: resolved 실패 이유 (LO DY, 새 보정 weight)", "",
     "| ch | Σw 비중 (B 안) | tight 쌍 없음 (둘째 렙톤 loose/없음) | tight 쌍, ΔR(ll)<0.4 | tight 쌍, ΔR(ll)>0.4 (jet–렙톤/jet–jet 겹침) | l4 가 fat jet 안 | GenJet ≥2 |",
     "|---|---|---|---|---|---|---|"]
res = {}
for ch, cid in (("EE", 11), ("MM", 13)):
    mB = lo["B"] & (lo["channel"] == cid); m = mB & (lo["nJet"] >= 2); W = wn[m].sum()
    f = lambda x: 100 * wn[m & x].sum() / W
    r = {"frac_in_B": 100 * W / wn[mB].sum(), "noPair": f(lo["hasPair"] < 0.5), "pair_dRll_lt04": f((lo["hasPair"] > 0) & (lo["dRll"] < 0.4)),
         "pair_dRll_gt04": f((lo["hasPair"] > 0) & (lo["dRll"] >= 0.4)), "l4_inFatJet": f(lo["l4_inFatJet"] > 0), "genjet_ge2": f(lo["n_genjet"] >= 2)}
    res[ch] = r
    L.append(f"| {ch} | {r['frac_in_B']:.1f}% | {r['noPair']:.1f}% | {r['pair_dRll_lt04']:.1f}% | {r['pair_dRll_gt04']:.1f}% | {r['l4_inFatJet']:.1f}% | {r['genjet_ge2']:.1f}% |")
L.append("")

# FxFx/LO shape (norm 200-1000) : resolved DY CR vs boosted nJet=1 vs boosted nJet>=2
CATS = {"Resolved DY CR": (lambda d: d["isDYCR"] > 0, "tab:red"),
        "Boosted, nJet=1": (lambda d: d["B"] & (d["nJet"] == 1), "tab:green"),
        "Boosted, nJet>=2": (lambda d: d["B"] & (d["nJet"] >= 2), "tab:blue")}
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True); c = np.sqrt(EDR[:-1] * EDR[1:])
L += ["## FxFx / LO (보정 없음) reco pT(ll) 모양 비, 200–1000 에서 단위 면적", "",
      "| ch | 영역 | 절대 비 | " + " | ".join(f"{int(EDR[i])}-{int(EDR[i+1])}" for i in range(len(EDR) - 1)) + " |", "|---" * (len(EDR) + 2) + "|"]
for j, (ch, cid) in enumerate((("EE", 11), ("MM", 13))):
    ax = axes[j]
    for i, (lab, (sel, col)) in enumerate(CATS.items()):
        ml = sel(lo) & (lo["channel"] == cid) & (lo["zpt"] >= 200) & (lo["zpt"] < 1000)
        mf = sel(fx) & (fx["channel"] == cid) & (fx["zpt"] >= 200) & (fx["zpt"] < 1000)
        hl = np.histogram(lo["zpt"][ml], EDR, weights=wr[ml])[0]; vl = np.histogram(lo["zpt"][ml], EDR, weights=wr[ml] ** 2)[0]
        hf = np.histogram(fx["zpt"][mf], EDR, weights=fx["weight"][mf])[0]; vf = np.histogram(fx["zpt"][mf], EDR, weights=fx["weight"][mf] ** 2)[0]
        K = hf.sum() / hl.sum(); r = (hf / hf.sum()) / (hl / hl.sum()); re = r * np.sqrt(vf / hf ** 2 + vl / hl ** 2)
        res.setdefault("shape", {}).setdefault(ch, {})[lab] = {"K": K, "ratio": r.tolist(), "err": re.tolist()}
        ax.errorbar(c * (0.97 + 0.03 * i), r, re, fmt="o-", ms=4, lw=1, capsize=2, color=col, label=f"{lab} (FxFx/LO abs {K:.2f})")
        L.append(f"| {ch} | {lab} | {K:.2f} | " + " | ".join(f"{x:.2f}±{y:.2f}" for x, y in zip(r, re)) + " |")
    ax.axhline(1, color="k", lw=0.8, ls=":"); ax.set_xscale("log"); ax.set_xlim(190, 1050); ax.set_ylim(0.4, 1.6)
    ax.set_xticks([200, 300, 400, 500, 700, 1000]); ax.set_xticklabels(["200", "300", "400", "500", "700", "1000"])
    ax.set_xlabel(r"reco $p_T(\ell\ell)$ [GeV]"); ax.set_title(f"{ch}: FxFx / LO shape (unit area 200-1000), no DY corr", fontsize=10); ax.legend(fontsize=8, loc="lower left")
axes[0].set_ylabel("FxFx / LO (shape)")
fig.tight_layout(); fig.savefig(f"{OUT}/zpt_shape_ratio_boosted_njet.png", dpi=130); fig.savefig(f"{OUT}/zpt_shape_ratio_boosted_njet.pdf")
json.dump(res, open(f"{OUT}/boosted_2jet_reason.json", "w"), indent=1)
open(f"{OUT}/boosted_2jet_reason.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
