#!/usr/bin/env python
"""[Claude-generated 2026-07-24] AN2019_083 Ch.5 + App.J correction values.

Derives, from the Reproduce20_002 histogram outputs, the Run-3 analogues of
  Fig. 24  : DY jet-pT reweighting  (data - nonDY)/DY  vs leading jet pT
  Fig. 31  : NLO/LO vs Data/LO of m(WR) in the DY CR
  Fig. 32  : NLO/LO ratio compared between DY CR and SR
  Table 19 : DY normalization scale factor (CR-only approximation)
  Table 20 : tt+tW normalization scale factor (flavor-CR-only approximation)
  Table 55 : (bonus, App. J) SR / e-mu-sideband ratios from tt MC, constant fit

Corrections are saved to background_corrections.root (TH1D with errors) and
background_corrections.json.  See corrections/README.md for method notes.

Run: /data6/Users/achihwan/micromamba/envs/Nano/bin/python make_ch5_appJ_corrections.py
"""
import glob
import json
import os

import numpy as np
import uproot
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = "/gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy"
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "corrections"))
ERAS = ["2022", "2022EE", "2023", "2023BPix"]
ALL_ERAS = ERAS + ["combined"]
LUMI = {"2022": 7.99, "2022EE": 26.68, "2023": 17.96, "2023BPix": 9.68,
        "combined": 62.31}

# region prefix per (cat, flavor); analysis regions: OS, EE with 2e_tight
DYCR = {("resolved", "EE"): "DYCR_Resolved_EE_OS_2e_tight",
        ("resolved", "MM"): "DYCR_Resolved_MM_OS",
        ("boosted", "EE"): "DYCR_Boosted_EE_OS_2e_tight",
        ("boosted", "MM"): "DYCR_Boosted_MM_OS"}
SR = {("resolved", "EE"): "SR_Resolved_EE_OS_2e_tight",
      ("resolved", "MM"): "SR_Resolved_MM_OS",
      ("boosted", "EE"): "SR_Boosted_EE_OS_2e_tight",
      ("boosted", "MM"): "SR_Boosted_MM_OS"}
FLAVCR = {"resolved": "FlavCR_Resolved_EM_OS",
          "boosted_ejet": "FlavCR_Boosted_MEJ_OS",   # isolated mu + e-in-jet
          "boosted_mujet": "FlavCR_Boosted_EMJ_OS"}  # isolated e + mu-in-jet
JETVAR = {"resolved": "leading_jet_pt", "boosted": "leading_fatjet_pt"}

EDGES_JETPT = {
    "resolved": np.array([40, 80, 120, 160, 200, 250, 300, 400, 500, 700,
                          1000, 1500, 2000], float),
    "boosted": np.array([200, 250, 300, 350, 400, 500, 600, 800, 1000,
                         1500, 2000], float),
}
EDGES_MWR_CR = {
    "resolved": np.array([400, 600, 800, 1000, 1200, 1400, 1600, 2000, 2400,
                          2800, 3200, 4000, 8000], float),
    "boosted": np.array([400, 600, 800, 1000, 1200, 1600, 2000, 2800, 4000,
                         8000], float),
}
EDGES_MWR_SR = {c: e[e >= 800] for c, e in EDGES_MWR_CR.items()}

GROUPS = ["data_e", "data_m", "dy_lo", "dy_nlo", "tt", "nonprompt", "others"]
LOG = []


def log(msg):
    LOG.append(msg)
    print("[log]", msg)


def group_of(stem):
    if stem.startswith("WR"):
        return None
    if stem in ("DYJets_MG", "WJets", "WJets_MG") or stem.startswith("DYJets10to50"):
        return None
    if stem.startswith("EGamma"):
        return "data_e"
    if stem.startswith(("Muon", "SingleMuon")):
        return "data_m"
    if stem == "DYJets":
        return "dy_nlo"
    if stem.startswith("DYMLL"):
        return "dy_lo"
    if stem == "TTLL_powheg" or stem.startswith("ST_tW"):
        return "tt"
    if stem.startswith(("TTLJ", "WJetM", "ST_tch", "ST_sch", "WtoLNu")):
        return "nonprompt"
    return "others"


# ----------------------------------------------------------------------------
# 1. read every needed histogram once per era, keep raw (1 GeV) binning
# ----------------------------------------------------------------------------
NEEDED = set()
for (cat, fl), pre in DYCR.items():
    NEEDED.add(f"{pre}_{JETVAR[cat]}")
    NEEDED.add(f"{pre}_mlljj")
for pre in SR.values():
    NEEDED.add(f"{pre}_mlljj")
for pre in FLAVCR.values():
    NEEDED.add(f"{pre}_mlljj")

# store[era][hname][group] = [values, variances]; edges kept in RAW_EDGES
store = {era: {h: {} for h in NEEDED} for era in ALL_ERAS}
RAW_EDGES = {}

for era in ERAS:
    for path in sorted(glob.glob(f"{BASE}/{era}/*.root")):
        stem = os.path.basename(path)[:-5]
        grp = group_of(stem)
        if grp is None:
            continue
        try:
            f = uproot.open(path)
        except Exception as e:
            log(f"OPEN FAIL {era}/{stem}: {type(e).__name__}")
            continue
        for hname in NEEDED:
            try:
                h = f[f"Central/{hname}"]
            except Exception:
                continue  # never filled for this sample -> zero
            v, e2 = h.values(), h.variances()
            RAW_EDGES.setdefault(hname, h.axis().edges())
            slot = store[era][hname]
            if grp in slot:
                slot[grp][0] += v
                slot[grp][1] += e2
            else:
                slot[grp] = [v.copy(), e2.copy()]
        f.close()

for hname in NEEDED:
    for grp in GROUPS:
        eras_with = [e for e in ERAS if grp in store[e][hname]]
        if not eras_with:
            log(f"MISSING everywhere: {hname} [{grp}]")
            continue
        v = sum(store[e][hname][grp][0] for e in eras_with)
        e2 = sum(store[e][hname][grp][1] for e in eras_with)
        store["combined"][hname][grp] = [v, e2]

# cross-check era-sum vs pre-merged directory for one histogram
try:
    f = uproot.open(f"{BASE}/combined_22_23/merged/TTLL_powheg.root")
    v_merged = f["Central/DYCR_Resolved_EE_OS_2e_tight_mlljj"].values().sum()
    # era-sum of the same sample only
    v_sum = 0.0
    for era in ERAS:
        v_sum += uproot.open(f"{BASE}/{era}/TTLL_powheg.root")[
            "Central/DYCR_Resolved_EE_OS_2e_tight_mlljj"].values().sum()
    log(f"cross-check TTLL DYCR mlljj: era-sum={v_sum:.3f} merged={v_merged:.3f}")
except Exception as e:
    log(f"cross-check failed: {type(e).__name__}: {e}")


def rebin(v, e2, src_edges, dst_edges):
    out_v = np.zeros(len(dst_edges) - 1)
    out_e2 = np.zeros(len(dst_edges) - 1)
    centers = 0.5 * (src_edges[:-1] + src_edges[1:])
    idx = np.searchsorted(dst_edges, centers, side="right") - 1
    ok = (idx >= 0) & (idx < len(out_v))
    np.add.at(out_v, idx[ok], v[ok])
    np.add.at(out_e2, idx[ok], e2[ok])
    return out_v, out_e2


def get(era, hname, grp, dst_edges):
    """(values, variances) rebinned; zeros if absent."""
    slot = store[era][hname]
    if grp not in slot:
        return np.zeros(len(dst_edges) - 1), np.zeros(len(dst_edges) - 1)
    return rebin(slot[grp][0], slot[grp][1], RAW_EDGES[hname], dst_edges)


def ratio(num, num_e2, den, den_e2):
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(den > 0, num / den, np.nan)
        re = np.where(den > 0,
                      np.sqrt(num_e2 / den**2 + num**2 * den_e2 / den**4), np.nan)
    return r, re


RESULTS = {"meta": {
    "source": BASE,
    "note": "AN2019_083 Fig24/31/32, Table19/20(/55) Run-3 analogues; "
            "errors are statistical (data+MC) only; see README.md",
    "lumi_fb": LUMI,
}}

# ----------------------------------------------------------------------------
# 2. Fig 24: (data - nonDY)/DY vs leading jet pT in the DY CR
# ----------------------------------------------------------------------------
fig24 = {}
for era in ALL_ERAS:
    fig24[era] = {}
    for cat in ["resolved", "boosted"]:
        dst = EDGES_JETPT[cat]
        comp = {}
        for fl in ["EE", "MM"]:
            hname = f"{DYCR[(cat, fl)]}_{JETVAR[cat]}"
            dkey = "data_e" if fl == "EE" else "data_m"
            d, d_e2 = get(era, hname, dkey, dst)
            dy, dy_e2 = get(era, hname, "dy_lo", dst)
            nv = ne2 = 0
            for g in ["tt", "nonprompt", "others"]:
                v, e2 = get(era, hname, g, dst)
                nv, ne2 = nv + v, ne2 + e2
            comp[fl] = (d - nv, d_e2 + ne2, dy, dy_e2)
        comp["comb"] = tuple(comp["EE"][i] + comp["MM"][i] for i in range(4))
        fig24[era][cat] = {}
        for fl, (num, num_e2, den, den_e2) in comp.items():
            r, re = ratio(num, num_e2, den, den_e2)
            fig24[era][cat][fl] = {"edges": dst.tolist(),
                                   "value": np.round(r, 5).tolist(),
                                   "error": np.round(re, 5).tolist()}
RESULTS["fig24_dy_jetpt_reweight"] = fig24

# ----------------------------------------------------------------------------
# 3. Fig 31 (NLO/LO vs Data/LO in DY CR) and Fig 32 (NLO/LO in CR vs SR)
#    flavors combined (ee + mumu), m(WR) = mlljj (resolved) / m(lJ) (boosted)
# ----------------------------------------------------------------------------
fig31, fig32 = {}, {}
for era in ALL_ERAS:
    fig31[era], fig32[era] = {}, {}
    for cat in ["resolved", "boosted"]:
        for reg, edges, out in [("cr", EDGES_MWR_CR[cat], fig31),
                                ("sr", EDGES_MWR_SR[cat], fig32)]:
            pre = DYCR if reg == "cr" else SR
            lo = lo_e2 = nlo = nlo_e2 = 0
            dat = dat_e2 = sub = sub_e2 = 0
            for fl in ["EE", "MM"]:
                hname = f"{pre[(cat, fl)]}_mlljj"
                v, e2 = get(era, hname, "dy_lo", edges)
                lo, lo_e2 = lo + v, lo_e2 + e2
                v, e2 = get(era, hname, "dy_nlo", edges)
                nlo, nlo_e2 = nlo + v, nlo_e2 + e2
                if reg == "cr":
                    dkey = "data_e" if fl == "EE" else "data_m"
                    v, e2 = get(era, hname, dkey, edges)
                    dat, dat_e2 = dat + v, dat_e2 + e2
                    for g in ["tt", "nonprompt", "others"]:
                        v, e2 = get(era, hname, g, edges)
                        sub, sub_e2 = sub + v, sub_e2 + e2
            r_nlo, re_nlo = ratio(nlo, nlo_e2, lo, lo_e2)
            entry = {"edges": edges.tolist(),
                     "nlo_over_lo": np.round(r_nlo, 5).tolist(),
                     "nlo_over_lo_err": np.round(re_nlo, 5).tolist()}
            if reg == "cr":
                r_dat, re_dat = ratio(dat - sub, dat_e2 + sub_e2, lo, lo_e2)
                entry["data_over_lo"] = np.round(r_dat, 5).tolist()
                entry["data_over_lo_err"] = np.round(re_dat, 5).tolist()
            out[era][cat] = entry
# fig32: pair CR (restricted to >=800) with SR
for era in ALL_ERAS:
    for cat in ["resolved", "boosted"]:
        edges = EDGES_MWR_SR[cat]
        cr_edges = np.array(fig31[era][cat]["edges"])
        keep = cr_edges[:-1] >= 800
        fig32[era][cat] = {
            "edges": edges.tolist(),
            "dycr": np.array(fig31[era][cat]["nlo_over_lo"])[keep].tolist(),
            "dycr_err": np.array(fig31[era][cat]["nlo_over_lo_err"])[keep].tolist(),
            "sr": fig32[era][cat]["nlo_over_lo"],
            "sr_err": fig32[era][cat]["nlo_over_lo_err"],
        }
RESULTS["fig31_dy_nlo_lo_data_lo_cr"] = fig31
RESULTS["fig32_dy_nlo_lo_cr_vs_sr"] = fig32

# ----------------------------------------------------------------------------
# 4. Table 19: DY normalization SF in the DY CR (CR-only approximation)
# ----------------------------------------------------------------------------
WIDE = np.array([0.0, 8000.0])


def one_bin_sf(era, hname, dkey, sig_grp, bkg_grps):
    d, d_e2 = get(era, hname, dkey, WIDE)
    s, s_e2 = get(era, hname, sig_grp, WIDE)
    b = b_e2 = 0
    for g in bkg_grps:
        v, e2 = get(era, hname, g, WIDE)
        b, b_e2 = b + v, b_e2 + e2
    D, S, B = d[0], s[0], b[0]
    if S <= 0:
        return None
    sf = (D - B) / S
    var = (d_e2[0] + b_e2[0]) / S**2 + (D - B) ** 2 * s_e2[0] / S**4
    return {"value": round(float(sf), 4), "error": round(float(np.sqrt(var)), 4),
            "n_data": float(D), "n_subtracted": round(float(B), 2),
            "n_target_mc": round(float(S), 2)}


table19 = {}
for era in ALL_ERAS:
    table19[era] = {}
    for cat in ["resolved", "boosted"]:
        for fl in ["EE", "MM"]:
            r = one_bin_sf(era, f"{DYCR[(cat, fl)]}_mlljj",
                           "data_e" if fl == "EE" else "data_m",
                           "dy_lo", ["tt", "nonprompt", "others"])
            table19[era][f"{cat}_{fl.lower()}"] = r
RESULTS["table19_dy_rate_param"] = table19

# ----------------------------------------------------------------------------
# 5. Table 20: tt+tW SF in the flavor sideband (CR-only approximation)
# ----------------------------------------------------------------------------
table20 = {}
for era in ALL_ERAS:
    table20[era] = {}
    for key, pre in FLAVCR.items():
        r = one_bin_sf(era, f"{pre}_mlljj", "data_m",
                       "tt", ["dy_lo", "nonprompt", "others"])
        table20[era][key] = r
RESULTS["table20_tt_rate_param"] = table20

# ----------------------------------------------------------------------------
# 6. Table 55 (bonus): SR / e-mu sideband ratios from tt MC, constant fit
# ----------------------------------------------------------------------------
def const_fit(r, re):
    ok = np.isfinite(r) & np.isfinite(re) & (re > 0)
    if ok.sum() < 2:
        return None
    w = 1.0 / re[ok] ** 2
    p0 = float(np.sum(w * r[ok]) / np.sum(w))
    err = float(1.0 / np.sqrt(np.sum(w)))
    chi2 = float(np.sum(w * (r[ok] - p0) ** 2))
    return {"p0": round(p0, 4), "err": round(err, 4),
            "chi2": round(chi2, 2), "nbins": int(ok.sum())}


table55 = {}
for era in ALL_ERAS:
    table55[era] = {}
    for cat, sb_key in [("resolved", "resolved"),
                        ("boosted_ee", "boosted_ejet"),
                        ("boosted_mm", "boosted_mujet")]:
        edges = EDGES_MWR_SR["resolved" if cat == "resolved" else "boosted"]
        sb, sb_e2 = get(era, f"{FLAVCR[sb_key]}_mlljj", "tt", edges)
        flavs = ["EE", "MM"] if cat == "resolved" else (
            ["EE"] if cat == "boosted_ee" else ["MM"])
        srcat = "resolved" if cat == "resolved" else "boosted"
        for fl in flavs:
            sr, sr_e2 = get(era, f"{SR[(srcat, fl)]}_mlljj", "tt", edges)
            r, re = ratio(sr, sr_e2, sb, sb_e2)
            fit = const_fit(r, re)
            table55[era][f"{srcat}_{fl.lower()}_over_emu"] = {
                "edges": edges.tolist(),
                "ratio": np.round(r, 4).tolist(),
                "ratio_err": np.round(re, 4).tolist(),
                "fit": fit}
RESULTS["table55_emu_ratios"] = table55

# check whether SR histograms contain events below 800 (low-mass fit possible?)
for cat in ["resolved", "boosted"]:
    hname = f"{SR[(cat, 'MM')]}_mlljj"
    v, _ = get("combined", hname, "tt", np.array([0.0, 800.0, 8000.0]))
    log(f"SR {cat} MM tt below/above 800 GeV: {v[0]:.2f} / {v[1]:.2f}")

# ----------------------------------------------------------------------------
# 7. outputs: JSON, ROOT, plots, tables
# ----------------------------------------------------------------------------
os.makedirs(OUT, exist_ok=True)
with open(f"{OUT}/background_corrections.json", "w") as jf:
    json.dump(RESULTS, jf, indent=1)
log("wrote background_corrections.json")

import ROOT  # noqa: E402

ROOT.gROOT.SetBatch(True)
rf = ROOT.TFile(f"{OUT}/background_corrections.root", "RECREATE")


def write_th1(dirpath, name, edges, vals, errs, title=""):
    d = rf
    for part in dirpath.split("/"):
        nxt = d.GetDirectory(part)
        d = nxt if nxt else d.mkdir(part)
    d.cd()
    h = ROOT.TH1D(name, title, len(edges) - 1, np.asarray(edges, float))
    for i, (v, e) in enumerate(zip(vals, errs), start=1):
        if np.isfinite(v):
            h.SetBinContent(i, v)
            h.SetBinError(i, e if np.isfinite(e) else 0.0)
    h.Write()


for era in ALL_ERAS:
    for cat in ["resolved", "boosted"]:
        e24 = fig24[era][cat]
        for fl in ["EE", "MM", "comb"]:
            d = e24[fl]
            write_th1(f"fig24_jetpt_ratio/{era}", f"{cat}_{fl}",
                      d["edges"], d["value"], d["error"],
                      "(data-nonDY)/DY vs leading jet pT")
        d = fig31[era][cat]
        write_th1(f"fig31_nlo_lo/{era}", f"{cat}_nlo_over_lo", d["edges"],
                  d["nlo_over_lo"], d["nlo_over_lo_err"])
        write_th1(f"fig31_nlo_lo/{era}", f"{cat}_data_over_lo", d["edges"],
                  d["data_over_lo"], d["data_over_lo_err"])
        d = fig32[era][cat]
        write_th1(f"fig32_cr_vs_sr/{era}", f"{cat}_dycr", d["edges"],
                  d["dycr"], d["dycr_err"])
        write_th1(f"fig32_cr_vs_sr/{era}", f"{cat}_sr", d["edges"],
                  d["sr"], d["sr_err"])

for tname, tdict in [("table19_dy_rate", table19), ("table20_tt_rate", table20)]:
    for era in ALL_ERAS:
        keys = [k for k, v in tdict[era].items() if v]
        d = rf.GetDirectory(tname) or rf.mkdir(tname)
        d.cd()
        h = ROOT.TH1D(era, "rate parameter (CR-only)", len(keys), 0, len(keys))
        for i, k in enumerate(keys, start=1):
            h.GetXaxis().SetBinLabel(i, k)
            h.SetBinContent(i, tdict[era][k]["value"])
            h.SetBinError(i, tdict[era][k]["error"])
        h.Write()
for era in ALL_ERAS:
    keys = [k for k, v in table55[era].items() if v.get("fit")]
    d = rf.GetDirectory("table55_emu_ratio") or rf.mkdir("table55_emu_ratio")
    d.cd()
    h = ROOT.TH1D(era, "SR/e#mu-sideband constant fit", len(keys), 0, len(keys))
    for i, k in enumerate(keys, start=1):
        h.GetXaxis().SetBinLabel(i, k)
        h.SetBinContent(i, table55[era][k]["fit"]["p0"])
        h.SetBinError(i, table55[era][k]["fit"]["err"])
    h.Write()
rf.Close()
log("wrote background_corrections.root")

# ------------------------------- plots --------------------------------------
def steps(ax, edges, v, e, color, label, fmt="o", ms=3.5):
    c = 0.5 * (edges[:-1] + edges[1:])
    xe = 0.5 * (edges[1:] - edges[:-1])
    ax.errorbar(c, v, yerr=e, xerr=xe, fmt=fmt, ms=ms, lw=1.1,
                color=color, label=label)


for cat in ["resolved", "boosted"]:
    fig, axes = plt.subplots(2, 3, figsize=(14.5, 8.2), dpi=150, sharey=True)
    for ax, era in zip(axes.ravel(), ALL_ERAS):
        for fl, col, lab, fmt in [("EE", "#4477aa", "ee only", "o"),
                                  ("MM", "#66ccee", r"$\mu\mu$ only", "o"),
                                  ("comb", "#222222", r"ee+$\mu\mu$ (nominal)", "s")]:
            d = fig24[era][cat][fl]
            steps(ax, np.array(d["edges"]), np.array(d["value"], float),
                  np.array(d["error"], float), col, lab, fmt)
        ax.axhline(1, color="#999999", lw=0.8, ls=":")
        ax.set_ylim(0.2, 1.8)
        ax.set_xlim(d["edges"][0], 1500)
        ax.set_xlabel("Leading %s $p_T$ [GeV]"
                      % ("AK4 jet" if cat == "resolved" else "AK8 jet"))
        ax.set_ylabel(r"(data $-$ non-DY) / DY MC")
        ax.text(0.04, 0.93, f"{era}  ({LUMI[era]:.4g} fb$^{{-1}}$), {cat} DY CR",
                transform=ax.transAxes, fontsize=10)
        ax.legend(fontsize=8, loc="lower left", frameon=False)
        ax.tick_params(direction="in", top=True, right=True)
    axes.ravel()[-1].axis("off")
    fig.suptitle("DY jet-$p_T$ correction, AN2019_083 Fig. 24 analogue (13.6 TeV)",
                 fontsize=11)
    fig.tight_layout()
    for ext in ["pdf", "png"]:
        fig.savefig(f"{OUT}/fig24_jetpt_ratio_{cat}.{ext}")
    plt.close(fig)
    log(f"wrote fig24_jetpt_ratio_{cat}")

for cat in ["resolved", "boosted"]:
    fig, axes = plt.subplots(2, 3, figsize=(14.5, 8.2), dpi=150, sharey=True)
    for ax, era in zip(axes.ravel(), ALL_ERAS):
        d = fig31[era][cat]
        E = np.array(d["edges"])
        steps(ax, E, np.array(d["nlo_over_lo"], float),
              np.array(d["nlo_over_lo_err"], float), "#222222", "NLO/LO", "o")
        steps(ax, E, np.array(d["data_over_lo"], float),
              np.array(d["data_over_lo_err"], float), "#4477aa",
              r"(Data$-$non-DY)/LO", "s")
        ax.axhline(1, color="#999999", lw=0.8, ls=":")
        ax.set_ylim(0, 2)
        ax.set_xscale("log")
        ax.set_xlim(E[0], E[-1])
        ax.set_xlabel(r"$m(W_R)^{RECO}$ [GeV]")
        ax.set_ylabel("ratio to LO DY")
        ax.text(0.04, 0.93, f"{era}, {cat} DY CR", transform=ax.transAxes,
                fontsize=10)
        ax.legend(fontsize=8, loc="lower left", frameon=False)
        ax.tick_params(direction="in", top=True, right=True)
    axes.ravel()[-1].axis("off")
    fig.suptitle("NLO/LO vs Data/LO in DY CR, AN2019_083 Fig. 31 analogue",
                 fontsize=11)
    fig.tight_layout()
    for ext in ["pdf", "png"]:
        fig.savefig(f"{OUT}/fig31_nlo_lo_data_lo_{cat}.{ext}")
    plt.close(fig)
    log(f"wrote fig31_nlo_lo_data_lo_{cat}")

for cat in ["resolved", "boosted"]:
    fig, axes = plt.subplots(2, 3, figsize=(14.5, 8.2), dpi=150, sharey=True)
    for ax, era in zip(axes.ravel(), ALL_ERAS):
        d = fig32[era][cat]
        E = np.array(d["edges"])
        steps(ax, E, np.array(d["dycr"], float), np.array(d["dycr_err"], float),
              "#222222", "NLO/LO in DY CR", "o")
        steps(ax, E, np.array(d["sr"], float), np.array(d["sr_err"], float),
              "#cc3311", "NLO/LO in SR", "s")
        ax.axhline(1, color="#999999", lw=0.8, ls=":")
        ax.set_ylim(0, 2)
        ax.set_xscale("log")
        ax.set_xlim(E[0], E[-1])
        ax.set_xlabel(r"$m(W_R)^{RECO}$ [GeV]")
        ax.set_ylabel("NLO/LO ratio")
        ax.text(0.04, 0.93, f"{era}, {cat}", transform=ax.transAxes, fontsize=10)
        ax.legend(fontsize=8, loc="lower left", frameon=False)
        ax.tick_params(direction="in", top=True, right=True)
    axes.ravel()[-1].axis("off")
    fig.suptitle("DY NLO/LO ratio in CR and SR, AN2019_083 Fig. 32 analogue",
                 fontsize=11)
    fig.tight_layout()
    for ext in ["pdf", "png"]:
        fig.savefig(f"{OUT}/fig32_nlo_lo_cr_sr_{cat}.{ext}")
    plt.close(fig)
    log(f"wrote fig32_nlo_lo_cr_sr_{cat}")

# ------------------------------- tables -------------------------------------
def dump_table(fname, tdict, cols, header, caption, label):
    with open(f"{OUT}/{fname}.csv", "w") as cf:
        cf.write("era," + ",".join(f"{c},{c}_err" for c in cols) + "\n")
        for era in ALL_ERAS:
            row = [era]
            for c in cols:
                v = tdict[era].get(c)
                row += ([f'{v["value"]:.3f}', f'{v["error"]:.3f}'] if v
                        else ["-", "-"])
            cf.write(",".join(row) + "\n")
    with open(f"{OUT}/{fname}.tex", "w") as tf:
        tf.write("\\begin{table}[htbp]\n\\centering\n")
        tf.write(f"\\caption{{{caption}}}\n\\label{{{label}}}\n")
        tf.write("\\begin{tabular}{l" + "c" * len(cols) + "}\n\\hline\n")
        tf.write("Era & " + " & ".join(header) + " \\\\\n\\hline\n")
        for era in ALL_ERAS:
            cells = []
            for c in cols:
                v = tdict[era].get(c)
                cells.append(f'${v["value"]:.2f} \\pm {v["error"]:.2f}$'
                             if v else "--")
            tf.write(era.replace("_", "\\_") + " & " + " & ".join(cells)
                     + " \\\\\n")
        tf.write("\\hline\n\\end{tabular}\n\\end{table}\n")


dump_table("table19_dy_rate", table19,
           ["resolved_ee", "resolved_mm", "boosted_ee", "boosted_mm"],
           ["Resolved $ee$", "Resolved $\\mu\\mu$",
            "Boosted $ee$", "Boosted $\\mu\\mu$"],
           "DY normalization scale factors from the DY CR "
           "(counting estimate, statistical uncertainties only). "
           "Run-3 analogue of AN2019\\_083 Table~19.",
           "tab:dy_rate_param")
dump_table("table20_tt_rate", table20,
           ["resolved", "boosted_ejet", "boosted_mujet"],
           ["Resolved", "Boosted with $e$-jet", "Boosted with $\\mu$-jet"],
           "$t\\bar{t}$+tW normalization scale factors from the flavor "
           "sideband (counting estimate, statistical uncertainties only). "
           "Run-3 analogue of AN2019\\_083 Table~20.",
           "tab:tt_rate_param")
log("wrote table19/table20 csv+tex")

# table 55 summary csv
with open(f"{OUT}/table55_emu_ratio_fits.csv", "w") as cf:
    cf.write("era,category,p0,err,chi2,nbins\n")
    for era in ALL_ERAS:
        for k, v in table55[era].items():
            if v.get("fit"):
                f5 = v["fit"]
                cf.write(f"{era},{k},{f5['p0']},{f5['err']},{f5['chi2']},"
                         f"{f5['nbins']}\n")
log("wrote table55_emu_ratio_fits.csv")

with open(f"{OUT}/run_log.txt", "w") as lf:
    lf.write("\n".join(LOG) + "\n")
print("DONE")
