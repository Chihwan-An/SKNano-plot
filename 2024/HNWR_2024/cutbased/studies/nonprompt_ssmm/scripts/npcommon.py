"""Shared helpers for the resolved SS mumu nonprompt study (MC only).

Naming used everywhere in this study, to keep two different "TT"s apart:
  * isolation category : "iso-TT", "iso-TL", "iso-LT", "iso-LL"  (lead/sub pass T = TkRelIso<0.1)
  * process group      : "ttbar(2l)" = plotter group "TT" (TTLL + ST_tW), "TTLJ", "W+jets", ...
  * truth               : prompt (P) / nonprompt (F) per muon from the gen origin, see truth_class()
The plotter group "Nonprompt" (TTLJ + W+jets + ST s/t) is a *sample* label, not truth.
"""
import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
CUTBASED = os.path.abspath(os.path.join(STUDY, "..", ".."))
sys.path.insert(0, CUTBASED)
from config import classify_sample  # noqa: E402

TIGHT_ISO = 0.1
SIGNALS6 = ["MWR3000_N200", "MWR4000_N200", "MWR5000_N200",
            "MWR3000_N1500", "MWR4000_N2000", "MWR5000_N2500"]
CARD_EDGES = np.array([800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 8000], float)
LOW_HIGH_SPLIT = 1600.0

# gen origin codes written by the FOMode analyzer (HNWR_BDT_presel_3SR::MuonGenOrigin)
ORIGIN_NAMES = {0: "no gen mu", 1: "prompt", 2: "prompt tau", 3: "b direct", 4: "b->c cascade",
                5: "c (no b)", 6: "nonprompt tau", 7: "light/other", 8: "HF-less chain"}


def process_of(sample):
    """Fine process label used in the tables (sample-level, not truth)."""
    if sample.startswith("Skim_HNWR3SR_"):
        return "SIG_" + sample.split("MuMuJJ_")[-1]
    if sample.startswith("QCD_"):
        return "QCD_" + sample.split("_")[-1]
    if sample.startswith("TTLJ"):
        return "TTLJ"
    if sample.startswith("TTLL"):
        return "TTLL"
    if sample.startswith("ST_tW"):
        return "ST_tW"
    if sample.startswith("ST_"):
        return "ST_s/t"
    if sample.startswith("WtoLNu"):
        return "W+jets"
    if sample.startswith("DYto2L"):
        return "DY"
    if sample.startswith(("WW", "WZ", "ZZ")):
        return "VV"
    if sample.startswith("tt"):
        return "ttV"
    return sample


def group_of(sample):
    """Plotter / card group (config.classify_sample), QCD and signal added."""
    if sample.startswith("Skim_HNWR3SR_"):
        return "SIG_" + sample.split("MuMuJJ_")[-1]
    if sample.startswith("QCD_"):
        return "QCD"
    g = classify_sample(sample)
    return g[0] if isinstance(g, tuple) else g


def load(skimdir, tree, samples=None):
    """Concatenate one tree of every npz in skimdir. Returns dict of arrays + 'sample'."""
    files = sorted(glob.glob(os.path.join(skimdir, "*.npz")))
    cols = {}
    names = []
    for f in files:
        s = os.path.basename(f)[:-4]
        if samples is not None and s not in samples:
            continue
        if s.startswith(("EGamma", "Muon")):
            raise RuntimeError(f"data file in skim dir: {f}")
        d = np.load(f)
        keys = [k for k in d.files if k.startswith(tree + "__")]
        if not keys:
            continue
        n = len(d[keys[0]])
        for k in keys:
            cols.setdefault(k.split("__", 1)[1], []).append(d[k])
        names.append(np.full(n, s, dtype=object))
    out = {k: np.concatenate(v) for k, v in cols.items()}
    out["sample"] = np.concatenate(names) if names else np.zeros(0, dtype=object)
    return out


def iso_cat(d):
    t1 = d["mu1_tkRelIso"] < TIGHT_ISO
    t2 = d["mu2_tkRelIso"] < TIGHT_ISO
    return np.where(t1 & t2, "TT", np.where(t1 & ~t2, "TL", np.where(~t1 & t2, "LT", "LL")))


def base_mask(d, mll=400.0, mlljj=800.0):
    return (d["mll"] > mll) & (d["mlljj"] > mlljj)


def charge_mask(d, ch):
    return d["lepChargeProduct"] > 0 if ch == "SS" else d["lepChargeProduct"] < 0


def mass_window(d, win):
    m = d["mlljj"]
    if win == "Full":
        return m > 800
    if win == "Low":
        return (m > 800) & (m < LOW_HIGH_SPLIT)
    if win == "High":
        return m >= LOW_HIGH_SPLIT
    raise ValueError(win)


def truth_prompt(origin, flav):
    """Per-muon truth: 'P' prompt (prompt mu or prompt tau->mu), 'F' nonprompt
    (b, b->c, c, nonprompt tau, light/other), 'U' undetermined (no gen muon found, or a
    matched gen muon whose ancestry is inconclusive). Uses the FOMode gen origin when
    available, else the NanoAOD genPartFlav (1,15 -> P; 3,4,5 -> F; 0 -> U)."""
    if origin is not None:
        return np.where(np.isin(origin, [1, 2]), "P",
                        np.where(np.isin(origin, [3, 4, 5, 6, 7]), "F", "U"))
    return np.where(np.isin(flav, [1, 15]), "P", np.where(np.isin(flav, [3, 4, 5]), "F", "U"))


def pair_truth(d):
    o1 = d.get("mu1_genOrigin")
    o2 = d.get("mu2_genOrigin")
    t1 = truth_prompt(o1, d["mu1_genPartFlav_truth"])
    t2 = truth_prompt(o2, d["mu2_genPartFlav_truth"])
    return np.char.add(t1.astype(str), t2.astype(str))


def wsum(w, m=None):
    if m is not None:
        w = w[m]
    return float(np.sum(w, dtype=np.float64)), float(np.sum(np.asarray(w, np.float64) ** 2)), int(len(w))


def fmt(sw, sw2, n, prec=2):
    return f"{sw:.{prec}f} ± {np.sqrt(sw2):.{prec}f} [{n}]"
