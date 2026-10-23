#!/usr/bin/env python3
"""Muon fake rate in the low-mll sideband 60 < mll < 300 (any mlljj), HNWR FOMode,FOLOW,RFlav production.
Stored: SS always; OS only MC with a non-prompt muon / data not both tight (so OS TT prompt is absent by design).

  fr_mll60300.py [--lmax 0.4]
    1. MC truth-F fake rate vs pT in |eta| 0-0.8 / 0.8-1.5 / 1.5-2.0 / 2.0-2.4 for mll 60-120, 120-200, 200-300,
       60-300 (SS+OS), overlaid with the SR (mll>400, mlljj>800) and SR-sideband maps from the SR FO skims
       -> out/nonprompt_ssmm/dycr/fakerate_mll60300[_lmaxX].png
    2. MC closure of each map -> SR SS (truth-F AR vs truth nonprompt iso-TT)
    3. data SS calibration k = (data TT - MC PP TT) / (data fail x MC map - MC PP fail x map) / (MC truth / MC pred)
  -> results/18_fr_mll60300[_lmaxX].txt
"""
import argparse
import glob
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import mplhep as hep  # noqa: E402
import numpy as np  # noqa: E402
import ROOT  # noqa: E402

import fo_analysis as FA  # noqa: E402
import folib as L  # noqa: E402

hep.style.use("CMS")
RL = "/gv0/Users/achihwan/SKNanoRunlog/2026_09_24_170440_HNWR_FOMode_FOLOW_RFlav/2024"
OUT = "/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/FOMode_FOLOW_RFlav/2024"
TREE = "Central_FO_MM_resolved"
ETA = [0, 0.8, 1.5, 2.0, 2.4]
PT = list(FA.PT_EDGES)   # overridden by --pt
COLS = ["mu1_pt", "mu1_eta", "mu1_charge", "mu1_tkRelIso", "mu1_genOrigin", "mu2_pt", "mu2_eta", "mu2_charge",
        "mu2_tkRelIso", "mu2_genOrigin", "mll", "mlljj", "nLooseMuon", "nLooseElectron", "weight"]


def files_of(s):
    m = os.path.join(OUT, s + ".root")
    if os.path.exists(m) and os.path.exists(os.path.join(RL, s, "hadd.out")):
        return [m]
    nj = len(glob.glob(os.path.join(RL, s, "job_*.cc")))
    fs = sorted(glob.glob(os.path.join(RL, s, "output", "hists_*.root")))
    return fs if nj and len(fs) == nj else []


def load():
    parts, names, missing = [], [], []
    for s in sorted(os.listdir(RL)):
        fs = files_of(s)
        if not fs:
            missing.append(s)
            continue
        v = ROOT.std.vector("std::string")()
        for f in fs:
            tf = ROOT.TFile.Open(f)
            ok = tf and TREE in {k.GetName() for k in tf.GetListOfKeys()}
            tf.Close()
            if ok:
                v.push_back(f)
        if v.size() == 0:
            continue
        a = ROOT.RDataFrame(TREE, v).AsNumpy(COLS)
        parts.append({k: np.asarray(x) for k, x in a.items()})
        names.append(np.full(len(a["mll"]), s, dtype=object))
    ev = {k: np.concatenate([p[k] for p in parts]) for k in COLS}
    ev["sample"] = np.concatenate(names)
    ev["data"] = np.array([s.startswith("Skim_HNWR_Muon") for s in ev["sample"]])
    ev["proc"] = np.array(["data" if x else L.process_of(s) for s, x in zip(ev["sample"], ev["data"])], dtype=object)
    ev["cat"] = L.iso_cat(ev)
    ev["ss"] = ev["mu1_charge"] * ev["mu2_charge"] > 0
    ev["t1"] = np.where(ev["data"], "D", L.truth(ev["mu1_genOrigin"]))
    ev["t2"] = np.where(ev["data"], "D", L.truth(ev["mu2_genOrigin"]))
    ev["pair"] = np.char.add(ev["t1"].astype(str), ev["t2"].astype(str))
    ev["base"] = (ev["nLooseMuon"] == 2) & (ev["nLooseElectron"] == 0)
    ev["weight"] = ev["weight"].astype(np.float64)
    return ev, missing


def fmap(d, m, lmax):
    rm = L.RateMap(PT, ETA)
    for k in (1, 2):
        iso = d[f"mu{k}_tkRelIso"]
        sel = m & (d[f"t{k}"] == "F")
        if lmax > 0:
            sel &= iso < lmax
        rm.fill(d[f"mu{k}_pt"][sel], d[f"mu{k}_eta"][sel], iso[sel] < L.TIGHT_ISO, d["weight"][sel])
    return rm


def pred(d, m, rm, lmax):
    """fake-factor weights; with lmax the fail muon(s) must have iso < lmax (else the event is not in the AR)."""
    if lmax > 0:
        ok = np.ones(len(d["mll"]), bool)
        ok &= ~((d["cat"] == "LT") | (d["cat"] == "LL")) | (d["mu1_tkRelIso"] < lmax)
        ok &= ~((d["cat"] == "TL") | (d["cat"] == "LL")) | (d["mu2_tkRelIso"] < lmax)
        m = m & ok
    return L.ff_prediction(d, m, rm)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lmax", type=float, default=0.0)
    ap.add_argument("--pt", default="", help="comma-separated pT edges, e.g. 53,60,80,120,160,4000")
    a = ap.parse_args()
    global PT
    if a.pt:
        PT = [float(x) for x in a.pt.split(",")]
    tag = (f"_lmax{a.lmax:g}" if a.lmax > 0 else "") + (f"_pt{int(PT[-2])}" if a.pt else "")
    txt = []
    P = lambda *x: (txt.append(" ".join(str(y) for y in x)), print(*x))  # noqa: E731
    lo, missing = load()
    sr, _ = L.load()
    b = FA.bkg_mask(sr, False)
    P(f"# FOLOW 60<mll<300 any mlljj. L: {'0.1<=TkRelIso<%g' % a.lmax if a.lmax > 0 else 'TkRelIso>=0.1'}. MC noQCD, W+jets HT.")
    P(f"# samples not complete / missing: {missing}")
    mcl = lo["base"] & ~lo["data"]
    wins = [("mll 60-120", (lo["mll"] > 60) & (lo["mll"] < 120), "#5790fc", "o"),
            ("mll 120-200", (lo["mll"] > 120) & (lo["mll"] < 200), "#7a21dd", "D"),
            ("mll 200-300", (lo["mll"] > 200) & (lo["mll"] < 300), "#e42536", "^"),
            ("mll 60-300", (lo["mll"] > 60) & (lo["mll"] < 300), "#f89c20", "v")]
    maps = [(lab, fmap(lo, mcl & w, a.lmax), col, mk) for lab, w, col, mk in wins]
    sbSR = sr["base"] & (((sr["mll"] > 400) & (sr["mlljj"] < 800)) | ((sr["mll"] > 200) & (sr["mll"] < 400))) & b
    maps.append(("SR sideband (mll>200, not SR)", fmap(sr, sbSR, a.lmax), "#9c9ca1", "s"))
    srm = L.sel(sr, "SS", "Full") & b
    maps.append(("SR SS (mll>400, mlljj>800)", fmap(sr, srm, a.lmax), "black", "s"))

    # plot
    pt = np.asarray(PT, float); pt_draw = pt.copy(); pt_draw[-1] = max(300.0, pt[-2] + 100.0)
    ctr = 0.5 * (pt_draw[:-1] + pt_draw[1:])
    fig, axes = plt.subplots(1, len(ETA) - 1, figsize=(10 * (len(ETA) - 1), 9), sharey=True)
    for i, (lab, rm, col, mk) in enumerate(maps):
        neffT = np.where(rm.T2 > 0, rm.T ** 2 / np.where(rm.T2 > 0, rm.T2, 1), 0)
        for j, ax in enumerate(axes):
            ok = (rm.T[:, j] + rm.L[:, j] > 0) & (neffT[:, j] >= 3)
            ax.errorbar(ctr[ok] + (i - 2.5) * 3.0, rm.r[ok, j], yerr=rm.err[ok, j], fmt=mk, color=col, ms=9,
                        capsize=3, mew=2, label=lab, mfc="none" if col == "black" else col)
    for j, ax in enumerate(axes):
        ax.set_xlim(45, pt_draw[-1]); ax.set_ylim(0, 0.6 if a.lmax > 0 else 0.45)
        for e in pt_draw:
            ax.axvline(e, color="grey", lw=0.3, ls=":")
        ax.text(0.04, 0.93, rf"$|\eta|$ {ETA[j]:g}-{ETA[j + 1]:g}", transform=ax.transAxes, fontsize=20)
        ax.set_xlabel(rf"muon $p_T$ (GeV)  [last bin {PT[-2]:g}+]")
        hep.cms.label(ax=ax, label="Preliminary", data=False, lumi=None, com=13.6, year="2024", fontsize=15)
    axes[0].set_ylabel(r"fake rate $f$, truth-F $\mu$, MC noQCD")
    axes[-1].legend(loc="upper right", fontsize=12, title=("L: 0.1<=TkRelIso<%g" % a.lmax if a.lmax > 0 else "L: TkRelIso>=0.1")
                    + r"; $N_{eff}(T)<3$ hidden", title_fontsize=11)
    od = os.path.join(L.PLOTS, "dycr"); os.makedirs(od, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(od, f"fakerate_mll60300{tag}.{ext}"), bbox_inches="tight")

    # tables + closure to SR + data calibration
    for lab, rm, _, _ in maps:
        P("\n" + rm.table(lab))
    P("\n## MC closure: map -> SR SS (truth-F AR, same L definition)  pred / target(truth nonprompt iso-TT)")
    reg = L.sel(sr, "SS", "Full") & b
    failF = np.where(sr["cat"] == "TL", sr["t2"] == "F", np.where(sr["cat"] == "LT", sr["t1"] == "F",
                     (sr["t1"] == "F") & (sr["t2"] == "F")))
    tgt = sr["weight"][reg & (sr["cat"] == "TT") & np.isin(sr["pair"], ["PF", "FP", "FF"])].sum()
    for lab, rm, _, _ in maps:
        p = pred(sr, reg & (sr["cat"] != "TT") & failF, rm, a.lmax).sum()
        P(f"  {lab:32s} pred {p:7.2f}  target {tgt:7.2f}  ratio {p / tgt:.3f}")
    P("\n## data calibration in the low-mll SS sideband (map = same window MC map)")
    D = lo["data"] & lo["base"] & lo["ss"]
    M = mcl & lo["ss"]
    for lab, w, _, _ in wins:
        rm = fmap(lo, mcl & w, a.lmax)
        dfail = D & w & (lo["cat"] != "TT")
        wD = pred(lo, dfail, rm, a.lmax)
        wPP = pred(lo, M & w & (lo["cat"] != "TT") & (lo["pair"] == "PP"), rm, a.lmax)
        prd = wD.sum() - wPP.sum()
        obs = (D & w & (lo["cat"] == "TT")).sum() - lo["weight"][M & w & (lo["cat"] == "TT") & (lo["pair"] == "PP")].sum()
        wM = pred(lo, M & w & (lo["cat"] != "TT"), rm, a.lmax)
        prdMC = wM.sum() - wPP.sum()
        tMC = lo["weight"][M & w & (lo["cat"] == "TT") & np.isin(lo["pair"], ["PF", "FP", "FF"])].sum()
        nTT = (D & w & (lo["cat"] == "TT")).sum()
        k = (obs / prd) / (tMC / prdMC) if prd and prdMC and tMC else np.nan
        ke = k * np.sqrt(nTT) / obs if obs > 0 else np.nan
        ppTT = lo["weight"][M & w & (lo["cat"] == "TT") & (lo["pair"] == "PP")].sum()
        P(f"  {lab:12s} data: TT {nTT}  prompt MC {ppTT:.1f}"
          f"  obs {obs:.1f}  pred {prd:.1f}  obs/pred {obs / prd:.3f} | MC closure pred/truth {prdMC / tMC:.3f} -> k = {k:.3f} ± {ke:.3f}(stat)")
    out = os.path.join(L.RESULTS, f"18_fr_mll60300{tag}.txt")
    open(out, "w").write("\n".join(txt) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    sys.exit(main())
