#!/usr/bin/env python3
"""Boosted DY CR: AK4 jet multiplicity, and whether its Z pT looks like the 1-jet region (2026-09-23).

Regions (HNWR_ChargeFlip CF_Tree dumps, 2024, DY MC):
  B   boosted DY CR that fails the resolved topology: isBoostedDYCR && !passResolved   (HNWR.cc:2499, !IsResolvedEvent)
  J1  1-jet region: hasPair, 60 <= m_ll < 150, reco nJet == 1 (AK4 pT>40 cleaned vs loose leptons, dR>0.4 between leptons)
  R2  resolved DY CR: isDYCR (passResolved, 60 <= m_ll < 150, m_lljj > 800)
Z pT: gen_zpt (LO, analyzer >= 09-22) and reco Z pT (B: lead lepton + DY-pair loose lepton l4; J1/R2: l1+l2).
LO weights: 'nom' = weight (new DY corr: jet-wise C x EW x R), 'raw' = weight / w_dy. FxFx dumps have w_dy = 1 and no gen
information, so FxFx/LO is compared on reco Z pT only.
    python3 boosted_njet_zpt.py [--lo DIR] [--fxfx DIR] [--out DIR]"""
import argparse, glob, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
D0 = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test/data/chargeflip"
ap = argparse.ArgumentParser()
ap.add_argument("--lo", default=f"{D0}/dumps_dynew_dy")
ap.add_argument("--fxfx", default=f"{D0}/dumps_fxfx")
ap.add_argument("--out", default=f"{HERE}/plots")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

COLS = ["channel", "isBoostedDYCR", "passResolved", "isDYCR", "hasPair", "m_l1l2", "nJet", "n_genjet", "gen_zpt",
        "pt_l1l2", "weight", "w_dy", "l1_pt", "l1_eta", "l1_phi", "l4_pt", "l4_eta", "l4_phi", "fj_pt"]


def load(files):
    parts = {c: [] for c in COLS}
    for f in files:
        d = np.load(f)
        for c in COLS: parts[c].append(d[c].astype(np.float64))
    return {c: np.concatenate(v) for c, v in parts.items()}


def ptsum(p1, e1, f1, p2, e2, f2):
    px = p1 * np.cos(f1) + p2 * np.cos(f2); py = p1 * np.sin(f1) + p2 * np.sin(f2)
    return np.hypot(px, py)


def regions(d):
    B = (d["isBoostedDYCR"] > 0) & (d["passResolved"] < 0.5)
    J1 = (d["hasPair"] > 0) & (d["m_l1l2"] >= 60) & (d["m_l1l2"] < 150) & (d["nJet"] == 1)
    R2 = d["isDYCR"] > 0
    zreco = np.where(B, ptsum(d["l1_pt"], d["l1_eta"], d["l1_phi"], d["l4_pt"], d["l4_eta"], d["l4_phi"]), d["pt_l1l2"])
    return {"B": B, "J1": J1, "R2": R2}, zreco


lo = load(sorted(glob.glob(f"{a.lo}/*.npz")))
fx = load(sorted(glob.glob(f"{a.fxfx}/*.npz")))
lo_reg, lo_zr = regions(lo); fx_reg, fx_zr = regions(fx)
w_nom = lo["weight"]; w_raw = lo["weight"] / lo["w_dy"]
CH = {"EE": 11, "MM": 13}
res = {"inputs": {"lo": a.lo, "fxfx": a.fxfx}, "njet": {}, "zpt": {}}
L = []

# ---- 1. jet multiplicity in the boosted DY CR ----
def frac_table(var, lab, maxn=4):
    rows = []
    for ch, cid in CH.items():
        m = lo_reg["B"] & (lo["channel"] == cid)
        tot = w_nom[m].sum(); v = lo[var][m]
        fr = [w_nom[m & (lo[var] == n)].sum() / tot for n in range(maxn)] + [w_nom[m & (lo[var] >= maxn)].sum() / tot]
        rows.append((ch, m.sum(), tot, fr))
        res["njet"][f"{var}_{ch}"] = {"n_events": int(m.sum()), "sumw": tot, "frac": fr}
    L.append(f"| {lab} | 이벤트 (MC) | Σw | " + " | ".join([str(n) for n in range(maxn)] + [f"≥{maxn}"]) + " |")
    L.append("|---" * (maxn + 4) + "|")
    for ch, n, tot, fr in rows:
        L.append(f"| {ch} | {n} | {tot:.1f} | " + " | ".join(f"{100 * x:.1f}%" for x in fr) + " |")
    L.append("")

L += ["## 1. boosted DY CR (resolved 실패) 의 jet 수 — LO DY MC, 새 DY 보정 weight", ""]
frac_table("nJet", "reco AK4 (pT>40, 렙톤 ΔR>0.4 cleaning; fat jet 안의 AK4 포함)")
frac_table("n_genjet", "GenJet (C 선택 기준, AK4 GenJet pT>40 |η|<2.5, hard 렙톤 ΔR>0.4)")

# ---- 2. Z pT shapes ----
EDG = np.array([0, 50, 100, 150, 200, 250, 300, 400, 500, 600, 800, 1000, 1500])

def hist(x, w, m):
    h, _ = np.histogram(np.clip(x[m], 0, EDG[-1] - 1e-3), EDG, weights=w[m]); e2, _ = np.histogram(np.clip(x[m], 0, EDG[-1] - 1e-3), EDG, weights=w[m] ** 2)
    return h, e2

def shape(h, e2):
    s = h.sum(); return h / s / np.diff(EDG), np.sqrt(e2) / s / np.diff(EDG)

cen = 0.5 * (EDG[1:] + EDG[:-1])
LAB = {"B": "boosted DY CR (resolved fail)", "J1": "1-jet (reco nJet=1, 60<m_ll<150)", "R2": "resolved DY CR",
       "G1": "gen: n_genjet=1 (60<m_ll<150 any reco)", "G2": "gen: n_genjet>=2"}
for ch, cid in CH.items():
    c = lo["channel"] == cid
    zw = (lo["hasPair"] > 0) & (lo["m_l1l2"] >= 60) & (lo["m_l1l2"] < 150)
    sel = {"B": lo_reg["B"] & c, "J1": lo_reg["J1"] & c, "R2": lo_reg["R2"] & c,
           "G1": zw & c & (lo["n_genjet"] == 1), "G2": zw & c & (lo["n_genjet"] >= 2)}
    fig, ax = plt.subplots(2, 1, figsize=(7, 7), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    ref = None
    for k, m in sel.items():
        y, e = shape(*hist(lo["gen_zpt"], w_nom, m))
        res["zpt"].setdefault(ch, {})[f"gen_{k}"] = {"edges": EDG.tolist(), "shape": y.tolist(), "err": e.tolist(), "sumw": float(w_nom[m].sum())}
        ax[0].errorbar(cen, y, e, xerr=np.diff(EDG) / 2, fmt="o", ms=3, label=LAB[k])
    ax[0].set_yscale("log"); ax[0].set_ylabel("unit area / GeV"); ax[0].legend(fontsize=8)
    ax[0].set_title(f"{ch}: gen Z pT, LO DY (new corr)")
    # ratio of the boosted-CR weight to the 1-jet one is meaningless (different phase space); show FxFx/LO instead below
    ax[1].axis("off")
    fig.tight_layout(); fig.savefig(f"{a.out}/genzpt_shapes_{ch}.png", dpi=120); plt.close(fig)

# ---- 3. FxFx / LO(raw) vs reco Z pT per region: is the generator ratio in B like J1 or like R2? ----
L += ["## 3. FxFx / LO (DY 보정 없음), reco Z pT — 영역별 비 (각 영역 안에서 절대 비)", ""]
EDR = np.array([0, 50, 100, 150, 200, 300, 400, 500, 700, 1000, 1500])
cr = 0.5 * (EDR[1:] + EDR[:-1])
for ch, cid in CH.items():
    fig, ax = plt.subplots(figsize=(7, 4.5))
    L.append(f"**{ch}** (pT(ll) bin: " + ", ".join(f"{int(EDR[i])}-{int(EDR[i + 1])}" for i in range(len(EDR) - 1)) + ")")
    L.append(""); L.append("| 영역 | FxFx Σw | LO Σw | 합 | " + " | ".join(f"{int(EDR[i])}" for i in range(len(EDR) - 1)) + " |")
    L.append("|---" * (len(EDR) + 3) + "|")
    for k in ("J1", "R2", "B"):
        ml = lo_reg[k] & (lo["channel"] == cid); mf = fx_reg[k] & (fx["channel"] == cid)
        hl, el = np.histogram(np.clip(lo_zr[ml], 0, EDR[-1] - 1e-3), EDR, weights=w_raw[ml])[0], np.histogram(np.clip(lo_zr[ml], 0, EDR[-1] - 1e-3), EDR, weights=w_raw[ml] ** 2)[0]
        hf, ef = np.histogram(np.clip(fx_zr[mf], 0, EDR[-1] - 1e-3), EDR, weights=fx["weight"][mf])[0], np.histogram(np.clip(fx_zr[mf], 0, EDR[-1] - 1e-3), EDR, weights=fx["weight"][mf] ** 2)[0]
        with np.errstate(divide="ignore", invalid="ignore"):
            r = hf / hl; re = r * np.sqrt(ef / hf ** 2 + el / hl ** 2)
        tot = hf.sum() / hl.sum()
        res["zpt"].setdefault(ch, {})[f"fxfx_over_lo_{k}"] = {"edges": EDR.tolist(), "ratio": np.nan_to_num(r).tolist(), "err": np.nan_to_num(re).tolist(), "total": tot}
        ok = (hl > 0) & (hf > 0) & (np.abs(re) < 0.5)
        ax.errorbar(cr[ok], r[ok], re[ok], xerr=(np.diff(EDR) / 2)[ok], fmt="o", ms=3, label=f"{LAB[k]} (total {tot:.2f})")
        cells = [f"{x:.2f}±{y:.2f}" if (hl[i] > 0 and hf[i] > 0 and abs(y) < 0.5) else "–" for i, (x, y) in enumerate(zip(r, re))]
        L.append(f"| {k} | {hf.sum():.0f} | {hl.sum():.0f} | {tot:.3f} | " + " | ".join(cells) + " |")
    L.append("")
    ax.axhline(1, color="gray", lw=0.8); ax.set_ylim(0.4, 1.8); ax.set_xlabel("reco pT(ll) [GeV]"); ax.set_ylabel("FxFx / LO (no DY corr)")
    ax.set_title(f"{ch}: generator ratio per region"); ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(f"{a.out}/fxfx_over_lo_recozpt_{ch}.png", dpi=120); plt.close(fig)

# ---- 2b. mean gen Z pT, n_genjet split inside B ----
L += ["## 2. boosted DY CR 안에서 gen Z pT (LO, 새 보정 weight) — n_genjet 별", ""]
L.append("| ch | n_genjet | Σw 비중 | ⟨gen Z pT⟩ | median |"); L.append("|---|---|---|---|---|")
for ch, cid in CH.items():
    m0 = lo_reg["B"] & (lo["channel"] == cid)
    for lab, cond in (("0", lo["n_genjet"] == 0), ("1", lo["n_genjet"] == 1), ("≥2", lo["n_genjet"] >= 2)):
        m = m0 & cond; w = w_nom[m]; x = lo["gen_zpt"][m]
        if w.sum() <= 0: continue
        o = np.argsort(x); cw = np.cumsum(w[o]); med = x[o][np.searchsorted(cw, 0.5 * cw[-1])]
        L.append(f"| {ch} | {lab} | {100 * w.sum() / w_nom[m0].sum():.1f}% | {np.average(x, weights=w):.0f} | {med:.0f} |")
L.append("")

json.dump(res, open(f"{a.out}/summary.json", "w"), indent=1)
open(f"{a.out}/tables.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
