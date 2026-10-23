"""Common code for the HNWR FOMode (FO_MM_resolved) analysis. MC only.

Terminology (kept distinct everywhere):
  iso category  : iso-TT / iso-TL / iso-LT / iso-LL  (T: TkRelIso<0.1, L: >=0.1; lead/sub by pT)
  process       : TTLL, TTLJ, tW, ST s/t, ttV, DY, W+jets, VV, VVV, QCD, SIG_...  (sample based)
  truth         : P (prompt mu or prompt tau->mu), F (b, b->c, c, nonprompt tau, light), U (undetermined)
FO baseline     : exactly two FO leptons in the event, both muons (nLooseMuon==2, nLooseElectron==0).
"""
import glob
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
SKIM = os.path.join(STUDY, "skim", "hnwr_fo")
RESULTS = os.path.join(STUDY, "results")
PLOTS = os.environ.get("NP_PLOTS") or "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/out/nonprompt_ssmm"

TIGHT_ISO = 0.1
SIGNALS6 = ["MWR3000_N200", "MWR4000_N200", "MWR5000_N200",
            "MWR3000_N1500", "MWR4000_N2000", "MWR5000_N2500"]
CARD_EDGES = np.array([800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 8000], float)
SPLIT = 1600.0
ORIGIN_NAMES = {0: "no gen mu", 1: "prompt", 2: "prompt tau", 3: "b direct", 4: "b->c cascade",
                5: "c (no b)", 6: "nonprompt tau", 7: "light/other", 8: "chain inconclusive"}
CATS = ["TT", "TL", "LT", "LL"]
PROCS_ORDER = ["TTLJ", "TTLL", "tW", "ST s/t", "ttV", "DY", "W+jets(MLNu)", "W+jets(HT)", "VV", "VVV",
               "QCD_MuEnriched", "QCD_EMEnriched", "QCD_bcToE"]


def process_of(s):
    if "WRtoNMutoMuMuJJ_" in s:
        return "SIG_" + s.split("MuMuJJ_")[-1]
    if s.startswith("QCD_"):
        return "QCD_" + s.split("_")[-1]
    t = s.replace("Skim_HNWR_", "")
    if t.startswith("TTtoLNu2Q"):
        return "TTLJ"
    if t.startswith("TTto2L2Nu"):
        return "TTLL"
    if t.startswith(("TWminus", "TbarWplus")):
        return "tW"
    if t.startswith(("TBbar", "Tbar")):
        return "ST s/t"
    if t.startswith(("TTLL_Bin", "TTLNu")):
        return "ttV"
    if t.startswith("DYto2L"):
        return "DY"
    if t.startswith("WtoLNu-4Jets"):
        return "W+jets(MLNu)"
    if t.startswith("WtoLNu_MLNu"):
        return "W+jets(HT)"
    if t in ("WWW", "WWZ", "WZZ", "ZZZ"):
        return "VVV"
    if t.startswith(("WW", "WZ", "ZZ")):
        return "VV"
    return t


def load(skimdir=SKIM, wjets="HT"):
    """All FO events of every MC npz. wjets selects the W+jets set: 'HT' (MLNu0to120_HT +
    MLNu120toInf_HT, inclusive in MLNu), 'MLNu' (MLNu-binned >120 only) or 'both' (overlapping)."""
    cols, names = {}, []
    hists = {}
    for f in sorted(glob.glob(os.path.join(skimdir, "*.npz"))):
        s = os.path.basename(f)[:-4]
        if "EGamma" in s or s.startswith(("Muon", "Skim_HNWR_Muon")):
            raise RuntimeError(f"data in skim dir: {f}")
        p = process_of(s)
        if wjets == "HT" and p == "W+jets(MLNu)":
            continue
        if wjets == "MLNu" and p == "W+jets(HT)":
            continue
        d = np.load(f)
        hists[s] = {k[6:]: d[k] for k in d.files if k.startswith("hist__")}
        keys = [k for k in d.files if k.startswith("FO__")]
        if not keys:
            continue
        n = len(d[keys[0]])
        for k in keys:
            cols.setdefault(k[4:], []).append(d[k])
        names.append(np.full(n, s, dtype=object))
    ev = {k: np.concatenate(v) for k, v in cols.items()}
    ev["sample"] = np.concatenate(names)
    ev["proc"] = np.array([process_of(s) for s in ev["sample"]], dtype=object)
    ev["cat"] = iso_cat(ev)
    ev["ss"] = ev["mu1_charge"] * ev["mu2_charge"] > 0
    ev["t1"] = truth(ev["mu1_genOrigin"])
    ev["t2"] = truth(ev["mu2_genOrigin"])
    ev["pair"] = np.char.add(ev["t1"].astype(str), ev["t2"].astype(str))
    ev["isSig"] = np.array([p.startswith("SIG_") for p in ev["proc"]])
    ev["base"] = (ev["nLooseMuon"] == 2) & (ev["nLooseElectron"] == 0)
    return ev, hists


def iso_cat(d):
    t1 = d["mu1_tkRelIso"] < TIGHT_ISO
    t2 = d["mu2_tkRelIso"] < TIGHT_ISO
    return np.where(t1 & t2, "TT", np.where(t1 & ~t2, "TL", np.where(~t1 & t2, "LT", "LL")))


def truth(origin):
    return np.where(np.isin(origin, [1, 2]), "P", np.where(np.isin(origin, [3, 4, 5, 6, 7]), "F", "U"))


def window(d, win):
    m = d["mlljj"]
    return {"Full": m > 800, "Low": (m > 800) & (m < SPLIT), "High": m >= SPLIT}[win]


def sel(d, ch="SS", win="Full", mll=400.0):
    c = d["ss"] if ch == "SS" else ~d["ss"]
    return d["base"] & c & (d["mll"] > mll) & window(d, win)


def ws(w):
    w = np.asarray(w, np.float64)
    return w.sum(), (w ** 2).sum(), len(w)


def fmt(t, p=2):
    return f"{t[0]:.{p}f}±{np.sqrt(t[1]):.{p}f} [{t[2]}]"


# ---------------------------------------------------------------- fake / prompt rates
class RateMap:
    """Weighted rate r = N(T)/N(FO) on a (pT, |eta|) grid with the correlated error
    var(r) = (L^2 var(T) + T^2 var(L)) / (T+L)^4 (T and L = FO-T are independent sums).
    Bins with r outside [0,1) are kept and flagged, never clipped."""

    def __init__(self, pt_edges, eta_edges):
        self.pt = np.asarray(pt_edges, float)
        self.eta = np.asarray(eta_edges, float)
        shape = (len(self.pt) - 1, len(self.eta) - 1)
        self.T = np.zeros(shape); self.T2 = np.zeros(shape)
        self.L = np.zeros(shape); self.L2 = np.zeros(shape)
        self.nT = np.zeros(shape, int); self.nL = np.zeros(shape, int)

    def idx(self, pt, eta):
        i = np.clip(np.searchsorted(self.pt, pt, side="right") - 1, 0, len(self.pt) - 2)
        j = np.clip(np.searchsorted(self.eta, np.abs(eta), side="right") - 1, 0, len(self.eta) - 2)
        return i, j

    def fill(self, pt, eta, tight, w):
        i, j = self.idx(pt, eta)
        w = np.asarray(w, float)
        for mask, S, S2, N in ((tight, self.T, self.T2, self.nT), (~tight, self.L, self.L2, self.nL)):
            np.add.at(S, (i[mask], j[mask]), w[mask])
            np.add.at(S2, (i[mask], j[mask]), w[mask] ** 2)
            np.add.at(N, (i[mask], j[mask]), 1)
        return self

    @property
    def r(self):
        with np.errstate(divide="ignore", invalid="ignore"):
            return self.T / (self.T + self.L)

    @property
    def err(self):
        tot = self.T + self.L
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.sqrt(self.L ** 2 * self.T2 + self.T ** 2 * self.L2) / tot ** 2

    def valid(self):
        r = self.r
        return np.isfinite(r) & (r >= 0) & (r < 1) & (self.T + self.L > 0)

    def lookup(self, pt, eta, r=None):
        i, j = self.idx(pt, eta)
        return (self.r if r is None else r)[i, j]

    def toys(self, n, rng):
        """Gaussian toys of T and L per bin (independent), returning rate arrays."""
        out = []
        for _ in range(n):
            T = self.T + rng.normal(size=self.T.shape) * np.sqrt(self.T2)
            L = self.L + rng.normal(size=self.L.shape) * np.sqrt(self.L2)
            with np.errstate(divide="ignore", invalid="ignore"):
                out.append(T / (T + L))
        return out

    def table(self, name):
        lines = [f"# {name}: rate r = T/(T+L), weighted; [raw nT/nL]; flag '!' = invalid (not clipped)"]
        head = "pT \\ |eta| " + " ".join(f"{self.eta[j]:.1f}-{self.eta[j + 1]:.1f}".rjust(26)
                                        for j in range(len(self.eta) - 1))
        lines.append(head)
        v = self.valid()
        for i in range(len(self.pt) - 1):
            row = f"{self.pt[i]:.0f}-{self.pt[i + 1]:.0f}".ljust(11)
            for j in range(len(self.eta) - 1):
                row += (f"{self.r[i, j]:.3f}±{self.err[i, j]:.3f} [{self.nT[i, j]}/{self.nL[i, j]}]"
                        + ("" if v[i, j] else "!")).rjust(27)
            lines.append(row)
        return "\n".join(lines)


def fake_factor(r):
    with np.errstate(divide="ignore", invalid="ignore"):
        return r / (1 - r)


def ff_prediction(d, m, fmap, r=None, prompt_eff=None):
    """Per-event weight of the fake-factor prediction of nonprompt iso-TT for events m.
    Default (prompt eff = 1): TL/LT -> +F_fail, LL -> -F1 F2.
    With prompt_eff (a RateMap of prompt T efficiency) the full 2-lepton matrix inversion
    is used instead (see mm_weights)."""
    F1 = fake_factor(fmap.lookup(d["mu1_pt"][m], d["mu1_eta"][m], r))
    F2 = fake_factor(fmap.lookup(d["mu2_pt"][m], d["mu2_eta"][m], r))
    cat = d["cat"][m]
    w = d["weight"][m].astype(np.float64)
    if prompt_eff is None:
        f = np.where(cat == "TL", F2, np.where(cat == "LT", F1, np.where(cat == "LL", -F1 * F2, 0.0)))
        return w * f
    f1 = fmap.lookup(d["mu1_pt"][m], d["mu1_eta"][m], r)
    f2 = fmap.lookup(d["mu2_pt"][m], d["mu2_eta"][m], r)
    e1 = prompt_eff.lookup(d["mu1_pt"][m], d["mu1_eta"][m])
    e2 = prompt_eff.lookup(d["mu2_pt"][m], d["mu2_eta"][m])
    return w * mm_weights(cat, e1, f1, e2, f2)


def mm_weights(cat, e1, f1, e2, f2):
    """Full 2-muon matrix method: nonprompt contribution to iso-TT (PF+FP+FF in TT) per
    observed event, for per-muon prompt efficiency e and fake rate f.
    Observed (TT,TL,LT,LL) = M (PP,PF,FP,FF) with M = kron([[e1,f1],[1-e1,1-f1]], [[e2,f2],[1-e2,1-f2]]).
    TT_nonprompt = e1 f2 PF + f1 e2 FP + f1 f2 FF."""
    n = len(cat)
    out = np.zeros(n)
    idx = {"TT": 0, "TL": 1, "LT": 2, "LL": 3}
    for k in range(n):
        A = np.array([[e1[k], f1[k]], [1 - e1[k], 1 - f1[k]]])
        B = np.array([[e2[k], f2[k]], [1 - e2[k], 1 - f2[k]]])
        M = np.kron(A, B)
        try:
            Minv = np.linalg.inv(M)
        except np.linalg.LinAlgError:
            out[k] = np.nan
            continue
        col = Minv[:, idx[cat[k]]]  # (PP,PF,FP,FF) per unit observed event
        out[k] = e1[k] * f2[k] * col[1] + f1[k] * e2[k] * col[2] + f1[k] * f2[k] * col[3]
    return out
