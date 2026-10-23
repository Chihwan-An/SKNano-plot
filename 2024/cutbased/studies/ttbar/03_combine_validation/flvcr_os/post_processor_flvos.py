#!/usr/bin/env python3
"""
ROOT file post-processor for combine datacard shape inputs.

Reads per-sample ROOT files from an era directory, groups backgrounds
according to SAMPLE_MAP, applies per-region rebinning, and writes a
single shape ROOT file with one TDirectory per region suitable for
CMS Combine.

Output structure:
  {region}/data_obs                 -- observed data (summed per region)
  {region}/{process}                -- nominal MC / signal
  {region}/{process}_{syst}_{era}Up   -- systematic up variation
  {region}/{process}_{syst}_{era}Down -- systematic down variation

Usage:
  python post_processor.py tsv_and_root/2022/link_to_root/2022/
  python post_processor.py tsv_and_root/2022/link_to_root/2022/ --era 2022 --output shapes_2022.root
  python post_processor.py tsv_and_root/2022/link_to_root/2022/ --regions bEESR bMuMuSR
  python post_processor.py tsv_and_root/2022/link_to_root/2022/ --no-signal
"""

import ROOT
import math
import numpy as np
import os
import re
import sys
import argparse

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

# ── Sample grouping ──────────────────────────────────────────────────────────
BACKGROUND_GROUPS = ["DYJets", "TT", "Nonprompt", "Others"]

# First-match wins; "ST" intentionally precedes "ST_tch"/"ST_sch" (kept from EE.py)
SAMPLE_MAP = {
    "DY":     "DYJets",
    "TTLL":   "TT",
    "TTLJ":   "Nonprompt",
    "ST":     "TT",
    "WJet":   "Nonprompt",
    "WtoLNu": "Nonprompt",
    "ST_tch": "Nonprompt",
    "ST_sch": "Nonprompt",
}

# ── Systematics ───────────────────────────────────────────────────────────────
# Applied to both backgrounds and signal
SYST_LIST_COMMON = [
    "Pileup",
    "ElectronID", "ElectronReco", "ElectronTrig",
    "MuonID",     "MuonReco",     "MuonTrig",    "MuonIso",
    # Object-level lepton energy/momentum scale & resolution (kinematic, MC only).
    "MuonScale",  "ElectronScale", "ElectronRes",
    "JER", "JES",
    # AK8 JES/JER and LSF3-cut-efficiency SF: affect boosted regions only, but the
    # analyzer produces <syst>_Up/Down dirs for every region (LSF weight stays 1
    # outside the boosted SR / flavor CR), so collect here.
    # Per-bin activation is gated in make_datacards{EE,MM}.py (BIN_SYSTS).
    "FatJetJES", "FatJetJER",
    "LSF",
]

# Theory systematics: signal (WR) samples only.
#
# All four are acceptance-only: the analyzer divides every LHE weight by the inclusive
# normalisation K_var of its own index, so the inclusive cross-section change cancels and
# the nuisance carries just the selection-efficiency change. The inclusive part is drawn
# as the theory band of the exclusion plot instead of being fitted.
#
# PDF is special: it has NO PDF_Up / PDF_Down directory in the analyzer output. A Hessian
# envelope is a quadrature sum over members OF THE OBSERVABLE and cannot be carried by a
# per-event weight -- the old target that tried overestimated it by 38-157x in the signal
# regions. Instead the analyzer writes PDFmem000..102/<region>_mlljj under the
# RunXsecSyst userflag and the envelope is formed here, in pdf_envelope(), at the FINAL
# template binning. The nuisance name is unchanged, so make_datacards{EE,MM}.py needs no
# edit.
SYST_LIST_SIGNAL_ONLY = ["AlphaS", "ScaleWeight_muF", "ScaleWeight_muR", "PDF"]

# Hessian members of LHEPdfWeight: 0 = central, 1..100 = eigenvector directions.
# 101/102 are the alpha_S members and belong to the separate AlphaS nuisance, which the
# analyzer computes correctly as a single weight -- they must NOT enter the envelope.
PDF_N_HESSIAN = 100
PDF_MEM_DIRS = [f"PDFmem{i:03d}" for i in range(PDF_N_HESSIAN + 1)]

# DY-only: the uncertainties of the DY corrections the analyzer applies,
#   w_DY *= C(gen Z pT) * EW(gen Z pT) * R(reco leading jet pT).
# Written for the DYJets group alone -- no other process carries these
# directories, and the analyzer leaves the weights at 1 outside DYMLL* samples.
#
# ZPtRw_MC_stat is the MC statistical error of C, read from the bin errors of
# the nominal ZPTReweight histogram; the three ZPtRwQCD* are the theory
# variations of its NLO numerator (docs/MCLRSM.yaml). The four are disjoint --
# the correction file's own ZPTReweight_Up/Down is the quadrature sum of the
# three theory groups and is used by nothing here, since taking it alongside
# them would count theory twice and leave the statistical error out. The per-bin
# reshape nuisances each move one pT bin of R by its sigma_R and leave the rest
# nominal (Reproduce20_002_copy.cc:2956,2966). Bin counts follow the delivered
# curves: 6 resolved, 3 boosted.
# ZPtRwEW1/2/3 are the three independent EW uncertainty sources of the NLO EW
# correction EW(gen Z pT), arXiv:1705.04664 (ZPtEWCorr.root, hist_e1/e2/e3).
# Pure theory, era-independent -- correlated across eras like the rest.
SYST_LIST_DY_ONLY = (
    ["ZPtRw_MC_stat", "ZPtRwQCDScale", "ZPtRwQCDPDFError", "ZPtRwQCDPDFAlphaS"]
    + ["ZPtRwEW1", "ZPtRwEW2", "ZPtRwEW3"]
    + [f"ResolvedDYReshapeBin{i}" for i in range(1, 7)]
    + [f"BoostedDYReshapeBin{i}"  for i in range(1, 4)]
)

# These stay correlated across eras, so they are written WITHOUT the era suffix
# that output_syst_name() adds to everything else.
SYST_ERA_CORRELATED = frozenset(SYST_LIST_DY_ONLY)

# The group the DY-only systematics belong to.
DY_GROUP = "DYJets"

SYST_LIST = SYST_LIST_COMMON + SYST_LIST_SIGNAL_ONLY + SYST_LIST_DY_ONLY

# ── Region config (hist name + rebin + data/signal patterns) ─────────────────
# rebin: int  → TH1.Rebin(n)
# bins:  list → TH1.Rebin(n_bins-1, name, edge_array)
REGION_CONFIG = {
    "bEESR": {
        "hist": "SR_Boosted_EE_mlljj",
        "bins": list(range(800, 8001, 1)),
        "data": ["EGamma"],
        "sig_channel": "EE",
        "blind": True,
    },
    "bMuMuSR": {
        "hist": "SR_Boosted_MM_mlljj",
        "bins": list(range(800, 8001, 1)),
        "data": ["Muon", "SingleMuon"],
        "sig_channel": "MM",
        "blind": True,
    },
    "bFlvMuECR": {
        "hist": "FlavCR_Boosted_MEJ_mlljj",
        "bins": [800, 1000, 1200, 1500, 1800, 4000],
        "data": ["Muon", "SingleMuon"],
        "sig_channel": None,
    },
    "bFlvEMuCR": {
        "hist": "FlavCR_Boosted_EMJ_mlljj",
        "bins": [800, 1000, 1200, 1500, 1800, 4000],
        "data": ["EGamma"],
        "sig_channel": None,
    },
    "bDYEECR": {
        "hist": "DYCR_Boosted_EE_mlljj",
        "bins": [800, 1000, 1200, 1500, 1800, 4000],
        "data": ["EGamma"],
        "sig_channel": None,
    },
    "bDYMuMuCR": {
        "hist": "DYCR_Boosted_MM_mlljj",
        "bins": [800, 1000, 1200, 1500, 1800, 4000],
        "data": ["Muon", "SingleMuon"],
        "sig_channel": None,
    },
    # charge-split boosted SR / DY CR (2026-09-17, same RFlav+DYCRCharge production: SR_Boosted_*_{OS,SS}_mlljj are
    # written without a userflag, DYCR_Boosted_*_{OS,SS}_mlljj behind DYCRCharge). Raw charge of the lead lepton x the
    # same-flavour loose lepton inside the fatjet; no tightCharge split.
    "bEESR_OS":    {"hist": "SR_Boosted_EE_OS_mlljj", "bins": list(range(800, 8001, 1)), "data": ["EGamma"], "sig_channel": "EE", "blind": True},
    "bEESR_SS":    {"hist": "SR_Boosted_EE_SS_mlljj", "bins": list(range(800, 8001, 1)), "data": ["EGamma"], "sig_channel": "EE", "blind": True},
    "bMuMuSR_OS":  {"hist": "SR_Boosted_MM_OS_mlljj", "bins": list(range(800, 8001, 1)), "data": ["Muon", "SingleMuon"], "sig_channel": "MM", "blind": True},
    "bMuMuSR_SS":  {"hist": "SR_Boosted_MM_SS_mlljj", "bins": list(range(800, 8001, 1)), "data": ["Muon", "SingleMuon"], "sig_channel": "MM", "blind": True},
    "bDYEECR_OS":  {"hist": "DYCR_Boosted_EE_OS_mlljj", "bins": [800, 1000, 1200, 1500, 1800, 4000], "data": ["EGamma"], "sig_channel": None},
    "bDYEECR_SS":  {"hist": "DYCR_Boosted_EE_SS_mlljj", "bins": [800, 1000, 1200, 1500, 1800, 4000], "data": ["EGamma"], "sig_channel": None},
    "bDYMuMuCR_OS": {"hist": "DYCR_Boosted_MM_OS_mlljj", "bins": [800, 1000, 1200, 1500, 1800, 4000], "data": ["Muon", "SingleMuon"], "sig_channel": None},
    "bDYMuMuCR_SS": {"hist": "DYCR_Boosted_MM_SS_mlljj", "bins": [800, 1000, 1200, 1500, 1800, 4000], "data": ["Muon", "SingleMuon"], "sig_channel": None},
    "rEESR": {
        "hist": "SR_Resolved_EE_mlljj",
        "bins": list(range(800, 8001, 1)),
        "data": ["EGamma"],
        "sig_channel": "EE",
        "blind": True,
    },
    # charge-split resolved EE SR (2026-09-09, HNWR userflag DYCRCharge production): OS, SS with both
    # electrons tightCharge==2, SS with at least one electron tightCharge<2. "hist" may be a list (summed).
    "rEESR_OS": {
        "hist": "SR_Resolved_EE_OS_mlljj",
        "bins": list(range(800, 8001, 1)),
        "data": ["EGamma"],
        "sig_channel": "EE",
        "blind": True,
    },
    "rEESR_SS_2e": {
        "hist": "SR_Resolved_EE_SS_2e_tight_mlljj",
        "bins": list(range(800, 8001, 1)),
        "data": ["EGamma"],
        "sig_channel": "EE",
        "blind": True,
    },
    "rEESR_SS_lt2": {
        "hist": ["SR_Resolved_EE_SS_1e_tight_mlljj", "SR_Resolved_EE_SS_0e_tight_mlljj"],
        "bins": list(range(800, 8001, 1)),
        "data": ["EGamma"],
        "sig_channel": "EE",
        "blind": True,
    },
    # charge-split resolved MM SR (all tightCharge; muon flips are negligible, MM SS = nonprompt/WZ)
    "rMuMuSR_OS": {
        "hist": "SR_Resolved_MM_OS_mlljj",
        "bins": list(range(800, 8001, 1)),
        "data": ["Muon", "SingleMuon"],
        "sig_channel": "MM",
        "blind": True,
    },
    "rMuMuSR_SS": {
        "hist": "SR_Resolved_MM_SS_mlljj",
        "bins": list(range(800, 8001, 1)),
        "data": ["Muon", "SingleMuon"],
        "sig_channel": "MM",
        "blind": True,
    },
    "rMuMuSR": {
        "hist": "SR_Resolved_MM_mlljj",
        "bins": list(range(800, 8001, 1)),
        "data": ["Muon", "SingleMuon"],
        "sig_channel": "MM",
        "blind": True,
    },
    # charge-split resolved DY CRs (2026-09-09): OS / SS; the EE SS is kept per tightCharge category so the
    # card builder can apply the per-category flip SF before summing.
    "rDYEECR_OS": {"hist": "DYCR_Resolved_EE_OS_mlljj", "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000], "data": ["EGamma"], "sig_channel": None},
    "rDYEECR_SS_2e": {"hist": "DYCR_Resolved_EE_SS_2e_tight_mlljj", "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000], "data": ["EGamma"], "sig_channel": None},
    "rDYEECR_SS_lt2": {"hist": ["DYCR_Resolved_EE_SS_1e_tight_mlljj", "DYCR_Resolved_EE_SS_0e_tight_mlljj"], "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000], "data": ["EGamma"], "sig_channel": None},
    "rDYMuMuCR_OS": {"hist": "DYCR_Resolved_MM_OS_mlljj", "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000], "data": ["Muon", "SingleMuon"], "sig_channel": None},
    "rDYMuMuCR_SS": {"hist": "DYCR_Resolved_MM_SS_mlljj", "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000], "data": ["Muon", "SingleMuon"], "sig_channel": None},
    "rDYEECR": {
        "hist": "DYCR_Resolved_EE_mlljj",
        "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000],
        "data": ["EGamma"],
        "sig_channel": None,
    },
    "rDYMuMuCR": {
        "hist": "DYCR_Resolved_MM_mlljj",
        "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000],
        "data": ["Muon", "SingleMuon"],
        "sig_channel": None,
    },
    "rFlvCR": {
        # 2026-09-22 (studies/ttbar 06 §12): opposite-sign only. The charge-inclusive
        # FlavCR_Resolved_EM_mlljj is 7.4% same-sign, where MC undershoots data 2.3x
        # (269 vs 115), which pushes the naive beta from 1.000 to 1.048. The SR this CR
        # normalises (rEESR_OS) is opposite-sign, so the CR must be too.
        "hist": "FlavCR_Resolved_EM_OS_mlljj",
        "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000],
        # 2026-09-19: Muon stream only. The resolved e-mu CR requires the muon trigger (HNWR.cc), so the
        # EGamma stream holds the SAME events again (3559 of the 3623 Muon-stream events): summing both
        # doubled data_obs (7182 vs MC 3469). Same choice as plot/cutbased/config.py and make_cr_template.py.
        "data": ["Muon", "SingleMuon"],
        "sig_channel": None,
    },
}

EXCLUDE_KEYWORDS = ["Skim", "skim"]
# every data-stream pattern used by any region (see classify_file)
ALL_DATA_PATTERNS = sorted({pat for cfg in REGION_CONFIG.values() for pat in cfg["data"]})


# ── Helpers ───────────────────────────────────────────────────────────────────

def classify_file(fname_base, data_patterns, sig_channel):
    """
    Returns (kind, label) where kind is 'data' / 'signal' / 'mc' / None (skip).
    For 'mc', label is the BACKGROUND_GROUPS key.
    For 'signal', label is fname_base.
    """
    if any(kw in fname_base for kw in EXCLUDE_KEYWORDS):
        return None, None

    # The DY background template is the HT-binned LO DYMLL* set -- the set the
    # C/EW corrections are applied to. The inclusive NLO DYJets (amcatnloFXFX)
    # was the NUMERATOR when C was derived, so the analyzer deliberately gives
    # it no correction; summing it here would both double-count the DY yield
    # and dilute every ZPtRw* variation with an uncorrected component.
    if fname_base.startswith("DYJets"):
        return None, None

    if fname_base.startswith("WR"):
        if sig_channel is None:
            return None, None
        if fname_base.endswith(sig_channel):
            return "signal", fname_base
        return None, None

    if any(pat in fname_base for pat in data_patterns):
        return "data", "data_obs"
    # 2026-09-19: a data file of a stream this region does not use (e.g. Muon* in an EGamma-only region) is
    # not MC. Without this guard it fell through to the "Others" default below and its raw event counts were
    # added to the Others template (bFlvEMuCR: Others 22 -> 458; rDYMuMuCR_OS: +2663; boosted SRs too).
    if any(pat in fname_base for pat in ALL_DATA_PATTERNS):
        return None, None

    group = "Others"
    for key, grp in SAMPLE_MAP.items():
        if key in fname_base:
            group = grp
            break
    return "mc", group


def _add_overflow(h):
    """Fold the ROOT overflow bin into the last content bin in-place."""
    n   = h.GetNbinsX()
    ov_c = h.GetBinContent(n + 1)
    ov_e = h.GetBinError(n + 1)
    if ov_c == 0 and ov_e == 0:
        return
    h.SetBinContent(n, h.GetBinContent(n) + ov_c)
    h.SetBinError(n, math.sqrt(h.GetBinError(n)**2 + ov_e**2))
    h.SetBinContent(n + 1, 0)
    h.SetBinError(n + 1, 0)


def _trim_range(h, x_low, x_high):
    """Return a new histogram restricted to [x_low, x_high] with overflow folded into last bin."""
    ax    = h.GetXaxis()
    i_lo  = ax.FindBin(x_low  + 1e-9)
    i_hi  = ax.FindBin(x_high - 1e-9)
    edges = np.array([ax.GetBinLowEdge(i) for i in range(i_lo, i_hi + 2)], dtype=float)
    h_new = h.Rebin(i_hi - i_lo + 1, ROOT.TUUID().AsString(), edges)
    h_new.SetDirectory(0)
    _add_overflow(h_new)
    return h_new


def _reshape_hist(h, rebin=None, bins=None, x_range=None):
    """Apply rebin/trim + overflow fold to an already-detached histogram."""
    if bins is not None:
        arr = np.array(bins, dtype=float)
        h_new = h.Rebin(len(arr) - 1, ROOT.TUUID().AsString(), arr)
        h_new.SetDirectory(0)
        _add_overflow(h_new)
        return h_new

    if rebin and rebin > 1:
        h.Rebin(rebin)

    if x_range is not None:
        return _trim_range(h, x_range[0], x_range[1])

    _add_overflow(h)
    return h


def load_hists(fpath, syst_dirs, hist_name, rebin=None, bins=None, x_range=None):
    """Open fpath ONCE and return {syst_dir: reshaped hist or None} for each dir.

    Opening each sample file a single time (rather than re-opening it for every
    systematic Up/Down) cuts the number of TFile::Open calls by ~50x. Over a
    network filesystem those redundant opens are the main source of transient
    TFile::Init read faults, so batching them here is both faster and far more
    robust.
    """
    out = {d: None for d in syst_dirs}
    f = ROOT.TFile.Open(fpath)
    if not f or f.IsZombie():
        return out
    names = hist_name if isinstance(hist_name, (list, tuple)) else [hist_name]
    for d in syst_dirs:
        h = None
        for hn in names:
            h_raw = f.Get(f"{d}/{hn}")
            if not h_raw:
                continue
            if h is None:
                h = h_raw.Clone(ROOT.TUUID().AsString()); h.SetDirectory(0)
            else:
                h.Add(h_raw)
        if h is None:
            continue
        out[d] = h
    f.Close()

    # Reshape after the file is closed: every hist is already detached.
    for d in syst_dirs:
        if out[d] is not None:
            out[d] = _reshape_hist(out[d], rebin, bins, x_range)
    return out


def load_hist(fpath, syst_dir, hist_name, rebin=None, bins=None, x_range=None):
    """Load, optionally rebin/trim, and detach a single histogram from a ROOT file."""
    return load_hists(fpath, [syst_dir], hist_name, rebin, bins, x_range)[syst_dir]


def accumulate(base, h):
    """Add h into base (clone if base is None), return result."""
    if base is None:
        c = h.Clone(ROOT.TUUID().AsString())
        c.SetDirectory(0)
        return c
    base.Add(h)
    return base


def write_hist(h, name, tdir):
    if h is None:
        return
    out = h.Clone(name)
    out.SetDirectory(tdir)
    out.Write()


def xsec_syst_path(fpath):
    """Path of the RunXsecSyst twin of a normal analyzer output file.

    SKNano.py appends the userflag to the output path, so
        <base>/<era>/<sample>.root   ->   <base>/RunXsecSyst/<era>/<sample>.root
    HNWR_XSECSYST_DIR overrides the directory outright when the two productions do not
    sit side by side.
    """
    sample_dir, fname = os.path.split(fpath)
    override = os.environ.get("HNWR_XSECSYST_DIR")
    if override:
        return os.path.join(override, fname)
    base, era = os.path.split(sample_dir.rstrip("/"))
    return os.path.join(base, "RunXsecSyst", era, fname)


_pdf_missing = set()


def pdf_envelope(fpath, hist_name, h_cen, rebin=None, bins=None, x_range=None):
    """(up, down) for the PDF nuisance, or (None, None) if the members are unavailable.

    The envelope is
        dN(bin) = sqrt( sum_i ( N_i(bin) - N_0(bin) )^2 ),  i = 1..100
    evaluated AFTER the histograms are rebinned to the template binning -- the quantity is
    per template bin, so forming it on the analyzer's raw 8000 bins and rebinning
    afterwards would give a different (and wrong) answer.

    The result is returned as a RELATIVE variation applied to h_cen, the Central shape of
    the ordinary production, rather than as the absolute member-0 histogram. Member 0
    reproduces Central by construction (K_0 = 1), but the two come from separate jobs and
    tying the templates to h_cen keeps them consistent with the nominal the datacard uses
    even if the RunXsecSyst production is regenerated on its own.
    """
    xpath = xsec_syst_path(fpath)
    if not os.path.exists(xpath):
        if xpath not in _pdf_missing:
            _pdf_missing.add(xpath)
            print(f"  WARNING: no RunXsecSyst file at {xpath} -- PDF will be a null "
                  f"variation for this sample. Run the analyzer with "
                  f"--userflags RunXsecSyst.")
        return None, None

    hs = load_hists(xpath, PDF_MEM_DIRS, hist_name, rebin, bins, x_range)
    h0 = hs["PDFmem000"]
    if h0 is None:
        if xpath not in _pdf_missing:
            _pdf_missing.add(xpath)
            print(f"  WARNING: {xpath} has no PDFmem000/{hist_name} -- PDF null for this "
                  f"sample.")
        return None, None

    n_found = sum(1 for i in range(1, PDF_N_HESSIAN + 1)
                  if hs[f"PDFmem{i:03d}"] is not None)
    if n_found != PDF_N_HESSIAN and xpath not in _pdf_missing:
        _pdf_missing.add(xpath)
        print(f"  WARNING: {xpath} has {n_found}/{PDF_N_HESSIAN} PDF members for "
              f"{hist_name}; the envelope is built from what is there.")

    up = h_cen.Clone(ROOT.TUUID().AsString())
    dn = h_cen.Clone(ROOT.TUUID().AsString())
    up.SetDirectory(0)
    dn.SetDirectory(0)

    for b in range(0, h0.GetNbinsX() + 2):
        n0 = h0.GetBinContent(b)
        if n0 == 0.0:
            continue
        s = 0.0
        for i in range(1, PDF_N_HESSIAN + 1):
            hi = hs[f"PDFmem{i:03d}"]
            if hi is None:
                continue
            d = hi.GetBinContent(b) - n0
            s += d * d
        rel = (s ** 0.5) / abs(n0)
        c = h_cen.GetBinContent(b)
        up.SetBinContent(b, c * (1.0 + rel))
        # combine cannot take a negative template; rel > 1 would only happen in a bin with
        # almost no MC left, where the down side is meaningless anyway.
        dn.SetBinContent(b, c * max(1.0 - rel, 0.0))

    return up, dn


def output_syst_name(syst, era_label):
    """Return the output systematic label with era suffix.

    Systematics in SYST_ERA_CORRELATED keep their bare name: combineCards.py
    correlates nuisances across eras by matching the name, so the suffix is
    exactly what would decorrelate them. The DY correction uncertainties are
    meant to be shared, so they must not get one.
    """
    if syst in SYST_ERA_CORRELATED:
        return syst
    return f"{syst}_{era_label}" if era_label else syst


# ── Main processor ────────────────────────────────────────────────────────────

def process_era(input_dir, output_path, era_label, regions=None, include_signal=True, verbose=True):
    all_files = sorted(f for f in os.listdir(input_dir) if f.endswith(".root"))
    if not all_files:
        print(f"ERROR: no .root files found in {input_dir}")
        sys.exit(1)

    active_regions = regions or list(REGION_CONFIG.keys())

    out_f = ROOT.TFile(output_path, "RECREATE")
    if not out_f or out_f.IsZombie():
        print(f"ERROR: cannot create {output_path}")
        sys.exit(1)

    for region in active_regions:
        cfg = REGION_CONFIG[region]
        hist_name   = cfg["hist"]
        rebin       = cfg.get("rebin")
        bins        = cfg.get("bins")
        x_range     = cfg.get("range")
        data_pats   = cfg["data"]
        sig_channel = cfg["sig_channel"] if include_signal else None

        if verbose:
            print(f"\n{'='*70}")
            print(f"Region: {region}  hist: {hist_name}")
            print(f"{'='*70}")

        # Accumulators keyed by label
        central: dict[str, ROOT.TH1]  = {}
        up     : dict[str, dict[str, ROOT.TH1]] = {s: {} for s in SYST_LIST}
        dn     : dict[str, dict[str, ROOT.TH1]] = {s: {} for s in SYST_LIST}

        for fname in all_files:
            fbase = fname.replace(".root", "")
            fpath = os.path.join(input_dir, fname)

            kind, label = classify_file(fbase, data_pats, sig_channel)
            if kind is None:
                continue

            # Which systematics apply to this file.
            if kind == "signal":
                systs = SYST_LIST_COMMON + SYST_LIST_SIGNAL_ONLY
            elif kind == "mc" and label == DY_GROUP:
                systs = SYST_LIST_COMMON + SYST_LIST_DY_ONLY
            elif kind == "mc":
                systs = SYST_LIST_COMMON
            else:  # data: no systematics
                systs = []

            # Read Central plus every needed systematic dir in ONE file open.
            syst_dirs = ["Central"]
            for syst in systs:
                syst_dirs += [f"{syst}_Up", f"{syst}_Down"]
            hists = load_hists(fpath, syst_dirs, hist_name, rebin, bins, x_range)

            h_cen = hists["Central"]
            if h_cen is None:
                if verbose:
                    print(f"  SKIP (no Central/{hist_name}) : {fname}")
                continue

            if verbose:
                print(f"  [{kind.upper():<6}] {fname:<48} yield={h_cen.Integral():.1f}")

            central[label] = accumulate(central.get(label), h_cen)

            # PDF is not in the analyzer's syst directories; build it here from the
            # per-member histograms of the matching RunXsecSyst job. Done per file, which
            # is exact because a signal label maps to exactly one file (classify_file
            # returns fname_base as the label) -- envelopes do not add linearly, so this
            # would have to accumulate members instead if that ever changed.
            if kind == "signal" and "PDF" in systs:
                hu_pdf, hd_pdf = pdf_envelope(fpath, hist_name, h_cen,
                                              rebin, bins, x_range)
                hists["PDF_Up"], hists["PDF_Down"] = hu_pdf, hd_pdf

            for syst in systs:
                hu = hists[f"{syst}_Up"]
                hd = hists[f"{syst}_Down"]
                # A sample can lack a systematic tree (e.g. fully-hadronic /
                # low-HT samples carry only JER/JES, no lepton-SF or pileup
                # variations). That systematic simply does not vary this
                # sample, so fall back to its Central shape. Without this the
                # sample stays in the group's nominal but drops out of every
                # variation, shifting the whole group's up/down uniformly
                # below nominal (looks like all systematics are identical).
                # accumulate() only reads its second arg, so reusing the shared
                # Central object as the fallback is safe.
                if hu is None:
                    hu = h_cen
                if hd is None:
                    hd = h_cen
                if hu:
                    up[syst][label] = accumulate(up[syst].get(label), hu)
                if hd:
                    dn[syst][label] = accumulate(dn[syst].get(label), hd)

        # ── Write this region to output file ─────────────────────────────────
        out_dir = out_f.mkdir(region)
        out_dir.cd()

        # data_obs: real data for unblinded regions, sum of backgrounds for blinded
        if cfg.get("blind", False):
            asimov = None
            for grp in BACKGROUND_GROUPS:
                if grp in central:
                    asimov = accumulate(asimov, central[grp])
            if asimov and verbose:
                print(f"  [BLIND] data_obs = Asimov (sum of bkg, yield={asimov.Integral():.1f})")
            write_hist(asimov, "data_obs", out_dir)
        elif "data_obs" in central:
            write_hist(central["data_obs"], "data_obs", out_dir)

        # backgrounds
        for grp in BACKGROUND_GROUPS:
            if grp not in central:
                continue
            write_hist(central[grp], grp, out_dir)
            grp_systs = SYST_LIST_COMMON + (SYST_LIST_DY_ONLY if grp == DY_GROUP else [])
            for syst in grp_systs:
                syst_out = output_syst_name(syst, era_label)
                write_hist(up[syst].get(grp), f"{grp}_{syst_out}Up",   out_dir)
                write_hist(dn[syst].get(grp), f"{grp}_{syst_out}Down", out_dir)

        # signals (sorted for reproducibility)
        for sig_label in sorted(k for k in central if k not in BACKGROUND_GROUPS and k != "data_obs"):
            write_hist(central[sig_label], sig_label, out_dir)
            for syst in SYST_LIST_COMMON + SYST_LIST_SIGNAL_ONLY:
                syst_out = output_syst_name(syst, era_label)
                write_hist(up[syst].get(sig_label), f"{sig_label}_{syst_out}Up",   out_dir)
                write_hist(dn[syst].get(sig_label), f"{sig_label}_{syst_out}Down", out_dir)

        if verbose:
            print(f"  >> Written TDirectory '{region}'")

    out_f.Close()
    print(f"\n>> Shape file written: {output_path}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="ROOT post-processor: groups backgrounds, rebins, writes combine shape file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "input_dir",
        help="Directory containing per-sample .root files "
             "(e.g. tsv_and_root/2022/link_to_root/2022/)",
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output ROOT file path. Default: {era}_shapes.root",
    )
    parser.add_argument(
        "--era", default=None,
        help="Era label used in the default output name (e.g. 2022, 2022EE). "
             "Inferred from the input directory name if omitted.",
    )
    parser.add_argument(
        "--regions", nargs="*", choices=list(REGION_CONFIG.keys()),
        metavar="REGION",
        help=f"Regions to process. Default: all. Choices: {list(REGION_CONFIG.keys())}",
    )
    parser.add_argument(
        "--no-signal", action="store_true",
        help="Skip signal (WR) histograms entirely.",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="Suppress per-file output.",
    )
    args = parser.parse_args()

    input_dir = os.path.realpath(args.input_dir)
    if not os.path.isdir(input_dir):
        print(f"ERROR: {input_dir} is not a directory")
        sys.exit(1)

    era_label = args.era or os.path.basename(input_dir)
    out_path  = args.output or f"{era_label}_shapes.root"

    print(f"Input  : {input_dir}")
    print(f"Era    : {era_label}")
    print(f"Output : {out_path}")
    print(f"Regions: {args.regions or 'all'}")

    process_era(
        input_dir      = input_dir,
        output_path    = out_path,
        era_label      = era_label,
        regions        = args.regions,
        include_signal = not args.no_signal,
        verbose        = not args.quiet,
    )


if __name__ == "__main__":
    main()
