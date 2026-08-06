#!/usr/bin/env python3
"""Per-WR summary figure: LHE-vs-SR stacked panels (N=100/300/500, EE+MM) on top,
offshell/onshell efficiencies and first-fail flow diagrams below.

Offshell/onshell boundary is the analyzer's SetSignalFlags definition:
WR4000 -> 2000 GeV, WR6000 -> 4000 GeV (LHE sumall mass).

One figure per (selection, WR):
  cutbased/WR{wr}_summary.png   cut-based SR chain
  BDT/WR{wr}_summary.png        BDT preselection chain

All fractions use the unweighted LHE denominator of the mass region
(LHE_mass_sumall_all_noweight), matching the GenReco_test stack convention.

The 2D fail histograms (*Fail_cutflow_vs_lhe_mass_noweight, x = LHE mass in
100 GeV bins, y = first-fail bin) are filled only for events in NEITHER SR:
 - resolved 2D covers everything (its bins 0-1 / 0-3 hold the preselection
   kills that never reach the boosted decision), so the boosted breakdown is
   completed with a "preselection" row taken from those resolved bins;
 - for the ONSHELL boosted diagram, events captured by the resolved side are
   absent from the 2D: cut-based adds SR_Resolved to bin 0 ("resolved-like",
   exact since resolved SR implies IsResolvedEvent); BDT shows them as their
   own "resolved candidate" row (exact: isBoostedCandidate requires
   !isResolvedCandidate).

Samples whose outputs predate the fail-cutflow show their stacked panel but a
"pending rerun" note in the diagram cells; re-running this script after the
analyzer rerun fills them in.
"""

import math, os
import numpy as np
import uproot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import mplhep as hep

hep.style.use("CMS")

IN_DIR   = "/gv0/Users/achihwan/SKNanoOutput/WRGenRecoMass/2023"
OUT_BASE = os.path.dirname(os.path.abspath(__file__))

WR_POINTS  = {4000: 2000., 6000: 4000.}   # WR -> offshell/onshell boundary [GeV]
N_LIST     = [100, 300, 500]
CHANNELS   = ["EE", "MM"]
REBIN      = 200                          # stack-panel display binning [GeV]
TOP_K      = 5                            # reasons shown per fail list

COLOR_LHE, COLOR_RES, COLOR_BOO = "dimgray", "tomato", "steelblue"

# ---------------------------------------------------------------------------
# Fail-bin labels — keep in sync with the comment blocks in WRGenRecoMass.cc
# (FillResolvedFailCutflow / FillBoostedFailCutflow and their BDT twins) and
# with GenReco_test/offshell_cutflow/plot_cutflow.py.
CUTBASED_RES_LABELS = [
    "MET noise filter", "Jet veto map", r"N(tight lep) $\neq$ 2",
    r"Lead lep $p_T$ (130 e / 60 $\mu$)", r"Sublead lep $p_T$ < 53",
    r"e-$\mu$ mixed pair", "Trigger", "< 2 jet cand. (any $p_T$)",
    r"Jet $p_T$ < 40", r"$\Delta R$(j1, lep)", r"$\Delta R$(j2, lep)",
    r"$\Delta R$(l1, l2)", r"$\Delta R$(j1, j2)", r"$m_{ll}$ < 400",
    r"$m_{lljj}$ < 800", "passed all (sanity)",
]
BDT_RES_LABELS = [
    "No HLT fired", "MET noise filter", "N(tight lep) = 0", "Jet veto map",
    r"N(tight lep) $\neq$ 2", r"e-$\mu$ mixed pair", r"Lead lep $p_T$ < 60",
    r"Sublead lep $p_T$ < 53", r"Lead trig / safe $p_T$", r"$m_{ll}$ < 200",
    "< 2 jet cand. (any $p_T$)", r"Jet $p_T$ < 40", r"$\Delta R$(j1, lep)",
    r"$\Delta R$(j2, lep)", r"$\Delta R$(l1, l2)", r"$\Delta R$(j1, j2)",
    "passed all (sanity)",
]
CUTBASED_BOO_LABELS = [
    "resolved-like (boosted skipped)", "No tight lepton",
    r"Lead lep $p_T$ (130 e / 60 $\mu$)", "Trigger",
    r"low-$m_{ll}$ SF pair (DY CR)", "No AK8 (pT/$\\eta$/ID/SDM)",
    "No LSF3 > 0.75 fatjet", r"No away fatjet ($|\Delta\phi|$>2)",
    "Extra tight lepton", "No SF loose lep in fatjet",
    "OF loose lep in fatjet", r"$m_{ll}$(lead, SF loose) < 200",
    r"$m$(lep + fatjet) < 800", "passed all (sanity)",
]
BDT_BOO_LABELS = [
    r"Lead lep $p_T$ < 60", "No extra loose lepton", r"Lead trig / safe $p_T$",
    r"No SF loose pair $m_{ll}$ > 200", "resolved-like topology (veto)",
    "No AK8 fatjet", "passed all (sanity)",
]

# Single-line medium-length labels for the summary tables (same bin order).
CUTBASED_RES_SHORT = [
    "MET filter", "Jet veto", r"N(tight) $\neq$ 2", r"Lead lep $p_T$",
    r"Sublead lep $p_T$", r"e-$\mu$ pair", "Trigger", "< 2 jet cand.",
    r"Jet $p_T$ < 40", r"$\Delta$R(j1, l)", r"$\Delta$R(j2, l)",
    r"$\Delta$R(l, l)", r"$\Delta$R(j, j)", r"$m_{ll}$ < 400",
    r"$m_{lljj}$ < 800", "sanity",
]
BDT_RES_SHORT = [
    "No HLT", "MET filter", "N(tight) = 0", "Jet veto", r"N(tight) $\neq$ 2",
    r"e-$\mu$ pair", r"Lead $p_T$ < 60", r"Sublead $p_T$ < 53", r"Trig/safe $p_T$",
    r"$m_{ll}$ < 200", "< 2 jet cand.", r"Jet $p_T$ < 40", r"$\Delta$R(j1, l)",
    r"$\Delta$R(j2, l)", r"$\Delta$R(l, l)", r"$\Delta$R(j, j)", "sanity",
]
CUTBASED_BOO_SHORT = [
    "resolved-like", "No tight lep", r"Lead lep $p_T$", "Trigger",
    r"low-$m_{ll}$ (DY CR)", "No AK8", "No LSF3 > 0.75", r"No $|\Delta\phi|$>2 FJ",
    "Extra tight lep", "No SF lep in FJ", "OF lep in FJ", r"$m_{ll}$ < 200",
    "m(l+FJ) < 800", "sanity",
]
BDT_BOO_SHORT = [
    r"Lead $p_T$ < 60", "No extra loose", r"Trig/safe $p_T$",
    r"No SF pair $m_{ll}$>200", "resolved-like veto", "No AK8", "sanity",
]

SELECTIONS = {
    "cutbased": {
        "sr_res": "Central/SR_Resolved_{ch}_lhe_mass_noweight",
        "sr_boo": "Central/SR_Boosted_{ch}_lhe_mass_noweight",
        "res2d":  "Central/ResolvedFail_cutflow_vs_lhe_mass_noweight",
        "boo2d":  "Central/BoostedFail_cutflow_vs_lhe_mass_noweight",
        "lep2d":  "Central/LostNtightLoose_vs_lhe_mass_noweight",
        "lepres2d": "Central/LostLepCatResFail_vs_lhe_mass_noweight",
        "lepboo2d": "Central/LostLepCatBooFail_vs_lhe_mass_noweight",
        "nfail_res": 16, "nfail_boo": 14,
        "res_labels": CUTBASED_RES_LABELS,
        "boo_labels": CUTBASED_BOO_LABELS,
        "res_short": CUTBASED_RES_SHORT,
        "boo_short": CUTBASED_BOO_SHORT,
        "presel_bins": [0, 1],     # resolved-2D bins that never reach boosted
        "resolved_sr_to_boo_bin0": True,   # onshell: add SR_Resolved into bin 0
        "title": "cut-based",
    },
    "BDT": {
        "sr_res": "Central/BDTSR_Resolved_{ch}_lhe_mass_noweight",
        "sr_boo": "Central/BDTSR_Boosted_{ch}_lhe_mass_noweight",
        "res2d":  "Central/BDTResolvedFail_cutflow_vs_lhe_mass_noweight",
        "boo2d":  "Central/BDTBoostedFail_cutflow_vs_lhe_mass_noweight",
        "lep2d":  "Central/BDTLostNtightLoose_vs_lhe_mass_noweight",
        "lepres2d": "Central/BDTLostLepCatResFail_vs_lhe_mass_noweight",
        "lepboo2d": "Central/BDTLostLepCatBooFail_vs_lhe_mass_noweight",
        "nfail_res": 17, "nfail_boo": 7,
        "res_labels": BDT_RES_LABELS,
        "boo_labels": BDT_BOO_LABELS,
        "res_short": BDT_RES_SHORT,
        "boo_short": BDT_BOO_SHORT,
        "presel_bins": [0, 1, 2, 3],
        "resolved_sr_to_boo_bin0": False,  # shown as its own "resolved candidate" row
        "title": "BDT presel",
    },
}


# ---------------------------------------------------------------------------
def integral_region(f, name, lo, hi):
    """Integral of a 1 GeV-binned 1D histogram on [lo, hi); None if absent."""
    if name not in f:
        return None
    vals  = f[name].values(flow=False)
    edges = f[name].axis().edges()
    sel = (edges[:-1] >= lo) & (edges[:-1] < hi)
    return float(vals[sel].sum())


def slice2d(f, name, lo, hi):
    """y-projection of a fail 2D histogram over x in [lo, hi); None if absent."""
    if name not in f:
        return None
    h = f[name]
    vals = h.values(flow=False)            # (nx, ny)
    xedges = h.axis(0).edges()
    sel = (xedges[:-1] >= lo) & (xedges[:-1] < hi)
    return vals[sel].sum(axis=0)


def load_sample(wr, n, ch, sel):
    """All numbers for one (sample, selection): per-region totals, SR counts,
    resolved/boosted fail vectors. Returns None if the file is missing."""
    path = f"{IN_DIR}/WR{wr}N{n}{ch}.root"
    if not os.path.exists(path):
        return None
    thr = WR_POINTS[wr]
    out = {"thr": thr}
    with uproot.open(path) as f:
        # full-range stack inputs (1 GeV binning)
        for key, hname in (("all", "LHE_mass_sumall_all_noweight"),
                           ("res", sel["sr_res"].format(ch=ch)),
                           ("boo", sel["sr_boo"].format(ch=ch))):
            out[key] = f[hname].values(flow=False) if hname in f else None
        out["edges"] = (f["LHE_mass_sumall_all_noweight"].axis().edges()
                        if out["all"] is not None else None)
        for reg, lo, hi in (("off", 0., thr), ("on", thr, 1e9)):
            out[f"n_{reg}"]   = integral_region(f, "LHE_mass_sumall_all_noweight", lo, hi)
            out[f"res_{reg}"] = integral_region(f, sel["sr_res"].format(ch=ch), lo, hi) or 0.
            out[f"boo_{reg}"] = integral_region(f, sel["sr_boo"].format(ch=ch), lo, hi) or 0.
            out[f"resfail_{reg}"] = slice2d(f, sel["res2d"], lo, hi)
            out[f"boofail_{reg}"] = slice2d(f, sel["boo2d"], lo, hi)
            out[f"lepfail_{reg}"] = slice2d(f, sel["lep2d"], lo, hi)
            out[f"lepresfail_{reg}"] = slice2d(f, sel["lepres2d"], lo, hi)
            out[f"lepboofail_{reg}"] = slice2d(f, sel["lepboo2d"], lo, hi)
    return out


# ---------------------------------------------------------------------------
def draw_stack(ax, data, wr, n, ch, sel_title):
    if data is None or data["all"] is None:
        ax.text(0.5, 0.5, f"WR{wr} N{n} {ch}\n(no file)", ha="center",
                va="center", transform=ax.transAxes, fontsize=11)
        ax.set_xticks([]); ax.set_yticks([])
        return
    nbin = len(data["all"]) // REBIN * REBIN
    reb = lambda v: v[:nbin].reshape(-1, REBIN).sum(axis=1)
    allv = reb(data["all"])
    edges = data["edges"][:nbin + 1:REBIN]
    ntot = allv.sum()
    if ntot <= 0:
        ax.axis("off"); return
    centers = 0.5 * (edges[:-1] + edges[1:])
    width = edges[1] - edges[0]
    gray = allv / ntot
    res = reb(data["res"]) / ntot if data["res"] is not None else np.zeros_like(gray)
    boo = reb(data["boo"]) / ntot if data["boo"] is not None else np.zeros_like(gray)
    ax.bar(centers, gray, width=width, color="lightgray", label="LHE all")
    ax.bar(centers, boo, width=width, color=COLOR_BOO,
           label=f"Boosted $\\epsilon$={data['boo'].sum()/ntot:.1%}" if data["boo"] is not None else "Boosted")
    ax.bar(centers, res, width=width, bottom=boo, color=COLOR_RES,
           label=f"Resolved $\\epsilon$={data['res'].sum()/ntot:.1%}" if data["res"] is not None else "Resolved")
    thr = data["thr"]
    ax.axvline(thr, color="black", ls=":", lw=1.2)
    off_frac = (data["n_off"] or 0.) / ntot
    # per-region efficiencies written directly on the panel: left = offshell,
    # right = onshell (denominator = that region's LHE count)
    n_off, n_on = data["n_off"] or 0., data["n_on"] or 0.
    left = f"offshell (< {thr:.0f}): {off_frac:.1%}"
    if n_off > 0:
        left += (f"\nres {data['res_off']/n_off:.1%}"
                 f"\nboo {data['boo_off']/n_off:.1%}")
    ax.text(0.03, 0.96, left, transform=ax.transAxes, fontsize=9, va="top",
            color="#444444", linespacing=1.4)
    if n_on > 0:
        right = (f"onshell ($\\geq$ {thr:.0f})"
                 f"\nres {data['res_on']/n_on:.1%}"
                 f"\nboo {data['boo_on']/n_on:.1%}")
        ax.text(0.97, 0.96, right, transform=ax.transAxes, fontsize=9, va="top",
                ha="right", color="#444444", linespacing=1.4)
    ax.set_xlim(0., wr * 1.2)
    ax.set_title(f"WR{wr} N{n} {ch}  ({sel_title})", fontsize=12, loc="left")
    ax.set_xlabel("LHE m [GeV]", fontsize=10)
    ax.set_ylabel("fraction / bin", fontsize=10)
    ax.tick_params(labelsize=9)
    ax.legend(fontsize=8, frameon=False)


# ---------------------------------------------------------------------------
def top_reasons(fail_by_ch, labels, k=TOP_K):
    """fail_by_ch: {ch: vector or None}. Rank bins by summed fraction, return
    [(label, {ch: frac})] of top-k plus an 'other' row."""
    chs = [c for c in CHANNELS if fail_by_ch.get(c) is not None]
    if not chs:
        return []
    nb = len(labels)
    tot = np.zeros(nb)
    for c in chs:
        v = fail_by_ch[c]
        tot[:len(v)] += v[:nb]
    order = np.argsort(tot)[::-1]
    rows, used = [], []
    for i in order[:k]:
        if tot[i] <= 0:
            continue
        rows.append((labels[i], {c: fail_by_ch[c][i] for c in chs}))
        used.append(i)
    other = {c: float(sum(fail_by_ch[c][i] for i in range(nb)
                          if i not in used and i < len(fail_by_ch[c]))) for c in chs}
    if any(v > 0 for v in other.values()):
        rows.append(("other", other))
    return rows


def render_table(ax, bbox, title, rows, denom, summary=None, note=None):
    """Reasons as rows (full-length labels), EE/MM as value columns.
    rows: [(label, {ch: count})]; summary: optional (label, {ch: count}) first
    row (Lost / not boosted). All values are fractions of `denom`."""
    chs = [c for c in CHANNELS if c in denom and denom[c]]
    entries = ([summary] if summary else []) + rows
    cell = [[lab] + [f"{d.get(c, 0.)/denom[c]:.1%}" for c in chs]
            for lab, d in entries]
    tab = ax.table(cellText=cell, colLabels=[""] + chs, bbox=bbox,
                   cellLoc="center", colWidths=[0.62, 0.19, 0.19])
    tab.auto_set_font_size(False)
    tab.set_fontsize(8.5)
    nsum = 1 if summary else 0
    for (r, c), cellobj in tab.get_celld().items():
        cellobj.set_edgecolor("#bbbbbb")
        if r == 0:
            cellobj.set_facecolor("#eef2f6")
        elif c > 0:
            cellobj.set_text_props(fontsize=7.8)
        if r > 0 and c == 0:
            cellobj.set_text_props(fontsize=7.5, ha="left")
            cellobj.PAD = 0.03
        if summary and r == 1:
            cellobj.set_facecolor("#f3f3f3")
    ax.text(bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] + 0.03, title,
            transform=ax.transAxes, ha="center", va="bottom", fontsize=9)
    if note:
        ax.text(bbox[0] + bbox[2] / 2, bbox[1] - 0.04, note,
                transform=ax.transAxes, ha="center", va="top",
                fontsize=7.5, color="#777777")


def draw_tables(ax, per_ch, sel, n_label):
    """Left table: offshell lost decomposed by resolved first-fail (a complete
    partition of the lost fraction). Right table: onshell 'not in boosted SR'
    decomposed by boosted first-fail (resolved capture + presel kills included
    as their own columns). Rows = EE / MM; all numbers are fractions of that
    mass region's LHE count."""
    ax.axis("off")
    chs = [c for c in CHANNELS if per_ch.get(c)]
    if not chs:
        ax.text(0.5, 0.5, "no data", ha="center", va="center", transform=ax.transAxes)
        return
    if all(per_ch[c]["resfail_off"] is None for c in chs):
        ax.text(0.5, 0.5, f"{n_label}: fail cutflow pending rerun", ha="center",
                va="center", transform=ax.transAxes, fontsize=11, color="#888888")
        return
    # ---- offshell (left+middle): resolved- and boosted-chain first-fail ----
    denom_off = {c: per_ch[c]["n_off"] or 0. for c in chs}
    lost_off = {c: denom_off[c] - per_ch[c]["res_off"] - per_ch[c]["boo_off"] for c in chs}
    rf = {c: per_ch[c]["resfail_off"] for c in chs}
    off_rows = top_reasons(rf, sel["res_short"], k=5)
    render_table(ax, [0.01, 0.80, 0.30, 0.17],
                 "Offshell · resolved fail", off_rows, denom_off,
                 summary=("Lost", lost_off))
    bf_off = {c: per_ch[c]["boofail_off"] for c in chs}
    off_boo_rows = top_reasons(bf_off, sel["boo_short"], k=5)
    render_table(ax, [0.355, 0.80, 0.30, 0.17],
                 "Offshell · boosted fail", off_boo_rows, denom_off,
                 note="(presel kills only in the resolved table)")
    # ---- onshell (right): boosted-chain first-fail among everything not boosted ----
    denom_on = {c: per_ch[c]["n_on"] or 0. for c in chs}
    notboo = {c: denom_on[c] - per_ch[c]["boo_on"] for c in chs}
    bf, labels_ext = {}, list(sel["boo_short"])
    if not sel["resolved_sr_to_boo_bin0"]:
        labels_ext.append("resolved cand. (excl.)")
    labels_ext.append("presel (filters/veto)")
    for c in chs:
        v = per_ch[c]["boofail_on"]
        if v is None:
            bf[c] = None; continue
        v = list(v)
        if sel["resolved_sr_to_boo_bin0"]:
            v[0] += per_ch[c]["res_on"]   # resolved SR implies bin 0 (resolved-like)
        else:
            v.append(per_ch[c]["res_on"]) # excluded by definition of the candidate
        presel = (float(sum(per_ch[c]["resfail_on"][i] for i in sel["presel_bins"]))
                  if per_ch[c]["resfail_on"] is not None else 0.)
        v.append(presel)
        bf[c] = np.array(v)
    on_rows = top_reasons(bf, labels_ext, k=5)
    render_table(ax, [0.70, 0.80, 0.30, 0.17],
                 "Onshell · boosted fail", on_rows, denom_on,
                 summary=("not boosted", notboo))

    # ---- lepton-multiplicity of the LOST events (9 categories) ----
    LEP_GROUPS = [
        (r"Tight $\geq$ 2",                 [0]),
        ("Tight = 1  (total)",              [1, 2, 3, 4, 5]),
        ("   fail = sublead (loose)",       [1]),
        ("   fail = lead (loose)",          [2]),
        (r"   2nd: $p_T$>53, ID fail",      [3]),
        (r"   2nd: reco, $p_T$<53",         [4]),
        ("   2nd: not reconstructed",       [5]),
        ("Tight = 0  (total)",              [6, 7, 8]),
        (r"   $\geq$ 2 loose",              [6]),
        ("   1 loose",                      [7]),
        ("   0 loose",                      [8]),
    ]
    def lep_rows(key):
        vecs = {c: per_ch[c][key] for c in chs}
        # old outputs carry the pre-split 7-bin version -> treat as pending
        if all(v is None or len(v) < 9 for v in vecs.values()):
            return None
        vecs = {c: v for c, v in vecs.items() if v is not None and len(v) >= 9}
        return [(lab, {c: float(sum(vecs[c][i] for i in idx)) for c in chs
                       if vecs[c] is not None})
                for lab, idx in LEP_GROUPS]
    for key, denom, x0, ttl in (("lepfail_off", denom_off, 0.10, "Offshell lost · lepton mult."),
                                ("lepfail_on",  denom_on,  0.62, "Onshell lost · lepton mult.")):
        rows = lep_rows(key)
        if rows is None:
            ax.text(x0 + 0.14, 0.55, "lepton mult.\npending rerun", ha="center",
                    va="center", transform=ax.transAxes, fontsize=9, color="#888888")
            continue
        render_table(ax, [x0, 0.47, 0.28, 0.24], ttl, rows, denom,
                     note="(excl. presel/no-HLT kills)")

    # ---- lepton category x first-fail cross (reason split per chain) ----
    CROSS_GROUPS = [(r"Tight $\geq$ 2", [0]), ("T=1 +loose", [1, 2]),
                    ("T=1 no loose", [3, 4, 5]), ("Tight = 0", [6, 7, 8])]
    def cross_rows(key, nfail, labels):
        vecs = {c: per_ch[c][key] for c in chs}
        if all(v is None for v in vecs.values()):
            return None
        rows = []
        for glab, cats in CROSS_GROUPS:
            mat = {c: np.array([sum(vecs[c][cat * nfail + f] for cat in cats)
                                for f in range(nfail)])
                   for c in chs if vecs[c] is not None}
            rows.append((glab, {c: float(m.sum()) for c, m in mat.items()}))
            order = np.argsort(sum(mat.values()))[::-1]
            for f in order[:2]:
                val = {c: float(mat[c][f]) for c in mat}
                if sum(val.values()) <= 0:
                    continue
                rows.append((u"   \u2192 " + labels[f], val))
        return rows
    for key, nfail, labels, denom, x0, ttl, note in (
            ("lepresfail_off", sel["nfail_res"], sel["res_short"], denom_off, 0.01,
             "Offshell lost · lep $\\times$ resolved fail", None),
            ("lepboofail_off", sel["nfail_boo"], sel["boo_short"], denom_off, 0.355,
             "Offshell lost · lep $\\times$ boosted fail", "(events reaching the boosted decision)"),
            ("lepboofail_on", sel["nfail_boo"], sel["boo_short"], denom_on, 0.70,
             "Onshell lost · lep $\\times$ boosted fail", "(events reaching the boosted decision)")):
        rows = cross_rows(key, nfail, labels)
        if rows is None:
            ax.text(x0 + 0.15, 0.20, "cross table\npending rerun", ha="center",
                    va="center", transform=ax.transAxes, fontsize=9, color="#888888")
            continue
        render_table(ax, [x0, 0.03, 0.30, 0.36], ttl, rows, denom, note=note)
    ax.text(-0.01, 0.45, n_label, transform=ax.transAxes, ha="right", va="center",
            fontsize=12, rotation=90)


# ---------------------------------------------------------------------------
def sanity_check(tag, per_ch):
    for c, d in per_ch.items():
        if not d or d["resfail_off"] is None:
            continue
        for reg in ("off", "on"):
            n = d[f"n_{reg}"] or 0.
            if n <= 0:
                continue
            lost = n - d[f"res_{reg}"] - d[f"boo_{reg}"]
            rsum = d[f"resfail_{reg}"].sum() if d[f"resfail_{reg}"] is not None else float("nan")
            if abs(lost - rsum) > max(1., 0.001 * n):
                print(f"  [check] {tag} {c} {reg}: lost={lost:.0f} vs resolved-fail sum={rsum:.0f}")


def make_figure(sel_key, wr):
    sel = SELECTIONS[sel_key]
    ncol = len(N_LIST)
    fig = plt.figure(figsize=(7.2 * ncol, 26))
    gs = gridspec.GridSpec(3, ncol, height_ratios=[1.0, 1.0, 2.0],
                           hspace=0.4, wspace=0.28)
    drew = False
    for j, n in enumerate(N_LIST):
        per_ch = {ch: load_sample(wr, n, ch, sel) for ch in CHANNELS}
        for i, ch in enumerate(CHANNELS):
            draw_stack(fig.add_subplot(gs[i, j]), per_ch[ch], wr, n, ch, sel["title"])
        draw_tables(fig.add_subplot(gs[2, j]), per_ch, sel, f"N{n}")
        sanity_check(f"WR{wr}N{n}", per_ch)
        drew = drew or any(per_ch[c] for c in CHANNELS)
    if not drew:
        plt.close(fig)
        return None
    fig.suptitle(f"WR{wr}  —  {sel['title']}: offshell/onshell efficiency and "
                 "first-fail breakdown (EE · MM)", fontsize=16, y=0.995)
    outdir = f"{OUT_BASE}/{sel_key}"
    os.makedirs(outdir, exist_ok=True)
    out = f"{outdir}/WR{wr}_summary.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return out


def main():
    for sel_key in SELECTIONS:
        for wr in WR_POINTS:
            out = make_figure(sel_key, wr)
            print(f"wrote {out}" if out else f"no data for {sel_key} WR{wr}")


if __name__ == "__main__":
    main()
