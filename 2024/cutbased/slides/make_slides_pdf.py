#!/usr/bin/env python3
"""Collect cutbased plots from ../out into a single PDF slide deck.

Usage: python3 make_slides_pdf.py

One page = (region, variable), flavours placed side by side.
Main variables first, then a "Backup" divider, then everything else.
Output: slides/pdf/<YYYYMMDD>/<YYYYMMDD_HHMMSS>.pdf
"""

import glob
import os
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

SLIDES_DIR = Path(__file__).resolve().parent
OUT_DIR = SLIDES_DIR.parent / "out"

PAGE_W, PAGE_H = 13.333, 7.5  # inches, 16:9 (same as the old pptx decks)

# (title, out subpath, [(flavor_dir, file prefix, cell label), ...])
REGIONS = [
    ("Resolved DY CR", "Resolve/DY",
     [("EE", "ResolveDYEE", "ee"), ("MM", "ResolveDYMM", "μμ")]),
    ("Resolved DY CR1 (60-100)", "Resolve/DYCR1",
     [("EE", "ResolveDYCR1EE", "ee"), ("MM", "ResolveDYCR1MM", "μμ")]),
    ("Resolved DY CR2 (100-150)", "Resolve/DYCR2",
     [("EE", "ResolveDYCR2EE", "ee"), ("MM", "ResolveDYCR2MM", "μμ")]),
    ("Resolved Flavour CR", "Resolve/FLV",
     [("E_Mu", "ResolveFLVEM", "eμ")]),
    ("Boosted DY CR", "Boost/DY",
     [("EE", "BoostDYEE", "ee"), ("MM", "BoostDYMM", "μμ")]),
    ("Boosted DY CR1 (60-100)", "Boost/DYCR1",
     [("EE", "BoostDYCR1EE", "ee"), ("MM", "BoostDYCR1MM", "μμ")]),
    ("Boosted DY CR2 (100-150)", "Boost/DYCR2",
     [("EE", "BoostDYCR2EE", "ee"), ("MM", "BoostDYCR2MM", "μμ")]),
    ("Boosted Flavour CR", "Boost/FLV",
     [("Mu_E", "BoostFLVMEJ", "μ + e-jet"), ("E_Mu", "BoostFLVEMJ", "e + μ-jet")]),
]

# A tuple entry means "first candidate that exists" (SDM vs SDMass differs by region).
MAIN_VARS = {
    "Resolve": ["dilepton_pt", "dilepton_mass",
                "leading_jet_pt", "subleading_jet_pt", "mlljj",
                "jetnum", "leading_lep_eta", "subleading_lep_eta",
                "leading_jet_eta", "subleading_jet_eta"],
    "Boost":   ["dilepton_pt", "dilepton_mass", "leading_fatjet_pt",
                ("fatjet_SDM", "fatjet_SDMass"), "mlljj",
                "jetnum", "leading_lep_eta", "subleading_lep_eta",
                "fatjet_eta"],
}

BACKUP_VARS = {
    "Resolve": ["leading_lep_pt", "leading_lep_eta", "leading_lep_phi",
                "subleading_lep_pt", "subleading_lep_eta", "subleading_lep_phi",
                "dilepton_eta", "dilepton_phi",
                "leading_jet_eta", "leading_jet_phi",
                "subleading_jet_eta", "subleading_jet_phi",
                "j1j2_pt", "j1j2_eta", "j1j2_phi", "j1j2_mass",
                "l1j1j2_pt", "l1j1j2_eta", "l1j1j2_phi", "l1j1j2_mass",
                "l2j1j2_pt", "l2j1j2_eta", "l2j1j2_phi", "l2j1j2_mass",
                "mlljj_fine", "mlljj_pt", "mlljj_eta", "mlljj_phi",
                "jetnum", "punum"],
    "Boost":   ["leading_lep_pt", "leading_lep_eta", "leading_lep_phi",
                "subleading_lep_pt", "subleading_lep_eta", "subleading_lep_phi",
                "dilepton_eta", "dilepton_phi",
                "fatjet_eta", "fatjet_phi", "fatjet_lsf3",
                "deltaR_leadlep_fatjet", "dphi_leadlep_fatjet",
                "mlljj_fine", "WR_pt", "WR_eta", "WR_phi",
                "jetnum", "punum"],
}

# First page: corrections applied in the HNWR analyzer (src/HNWR.cc).
# (section, [(name, applied, note), ...]); applied True -> green check, False -> red x.
CORRECTIONS = [
    ("Event weights", [
        ("MC weight x trigger lumi (HLT_Mu50)", True, ""),
        ("Pileup reweighting", True, ""),
    ]),
    ("Lepton scale factors", [
        ("Electron HEEP ID / RECO / Trigger SF", True, ""),
        ("Muon HighPt ID / RECO / Trigger / Iso SF", True, ""),
        ("LSF3 cut efficiency SF", True, "boosted SR / flavour CR only"),
    ]),
    ("Object corrections", [
        ("JEC + nominal JER smearing (AK4 / AK8 / m_SD)", True, ""),
        ("Muon momentum scale", True, "Rochester < 200 GeV, Generalized Endpoint > 200 GeV"),
        ("High-pT muon extra resolution smearing", True, "MC only"),
        ("Electron energy scale & smearing", True, "MC only"),
    ]),
    ("DY MC only", [
        ("Z-pT reweight C(gen Z pT), NLO/LO", True, ""),
        ("NLO EW correction EW(gen Z pT)", True, "arXiv:1705.04664"),
        ("Data-driven R(reco jet pT) from DY CR", True, "2022 / 2022EE"),
    ]),
    ("Not applied", [
        ("b-tagging SF", False, ""),
        ("Top pT reweighting", False, ""),
        ("L1 prefire", False, "N/A in Run 3"),
    ]),
]

MISSING = []


def topology_of(subpath):
    return subpath.split("/")[0]


def find_plot(subpath, flavor_dir, prefix, var):
    base = OUT_DIR / subpath / flavor_dir
    for pattern in (f"*/Inclusive/{prefix}_{var}_plot.png",
                    f"*/{prefix}_{var}_plot.png",
                    f"{prefix}_{var}_plot.png"):
        hits = sorted(glob.glob(str(base / pattern)))
        if hits:
            return hits[0]
    return None


def resolve_var(subpath, flavors, var):
    """Return (name, per-flavour path list) for a var or candidate tuple."""
    candidates = var if isinstance(var, tuple) else (var,)
    for cand in candidates:
        paths = [find_plot(subpath, fdir, pfx, cand) for fdir, pfx, _ in flavors]
        if any(paths):
            return cand, paths
    name = candidates[0]
    for fdir, pfx, _ in flavors:
        MISSING.append(f"{subpath}/{fdir}: {pfx}_{name}")
    return name, [None] * len(flavors)


def leftover_vars(subpath, flavors, used):
    """Variables present on disk but not in the explicit lists, sorted."""
    found = set()
    for fdir, pfx, _ in flavors:
        for f in glob.glob(str(OUT_DIR / subpath / fdir / "**" / f"{pfx}_*_plot.png"),
                           recursive=True):
            found.add(os.path.basename(f)[len(pfx) + 1:-len("_plot.png")])
    return sorted(found - used)


def add_plot_page(pdf, title, labels, paths):
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))
    fig.text(0.02, 0.975, title, fontsize=18, fontweight="bold", ha="left", va="top")
    n = len(paths)
    for i, (label, path) in enumerate(zip(labels, paths)):
        left, width = 0.02 + i * (0.96 / n), 0.96 / n - 0.01
        ax = fig.add_axes([left, 0.03, width, 0.85], anchor="C")
        ax.axis("off")
        ax.set_title(label, fontsize=13, fontweight="bold")
        if path is None:
            ax.text(0.5, 0.5, "MISSING", ha="center", va="center",
                    fontsize=20, color="red", transform=ax.transAxes)
        else:
            # interpolation="none": PDF에 원본 픽셀을 그대로 내장 (리샘플링 방지)
            ax.imshow(mpimg.imread(path), interpolation="none")
    pdf.savefig(fig)
    plt.close(fig)


def add_corrections_page(pdf):
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))
    fig.text(0.02, 0.975, "Applied corrections", fontsize=20, fontweight="bold",
             ha="left", va="top")

    x_name, x_mark, x_note = 0.05, 0.55, 0.60
    y, dy_section, dy_row = 0.88, 0.045, 0.038
    for section, rows in CORRECTIONS:
        fig.text(0.03, y, section, fontsize=14, fontweight="bold")
        y -= dy_section
        for name, applied, note in rows:
            mark, color = ("✓", "green") if applied else ("✗", "red")
            fig.text(x_name, y, name, fontsize=11)
            fig.text(x_mark, y, mark, fontsize=12, fontweight="bold", color=color,
                     ha="center")
            if note:
                fig.text(x_note, y, note, fontsize=10, color="gray")
            y -= dy_row
        y -= 0.01

    pdf.savefig(fig)
    plt.close(fig)


def add_divider(pdf, text):
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))
    fig.text(0.5, 0.5, text, fontsize=40, fontweight="bold", ha="center", va="center")
    pdf.savefig(fig)
    plt.close(fig)


def output_path():
    now = datetime.now()
    outdir = SLIDES_DIR / "pdf" / now.strftime("%Y%m%d")
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir / f"{now.strftime('%Y%m%d_%H%M%S')}.pdf"


def main():
    out = output_path()
    npages = 0
    with PdfPages(out) as pdf:
        add_corrections_page(pdf)
        npages += 1

        used = {}  # subpath -> set of vars already shown
        for title, subpath, flavors in REGIONS:
            labels = [lab for _, _, lab in flavors]
            used[subpath] = set()
            for var in MAIN_VARS[topology_of(subpath)]:
                name, paths = resolve_var(subpath, flavors, var)
                used[subpath].add(name)
                add_plot_page(pdf, f"{title} — {name}", labels, paths)
                npages += 1

        add_divider(pdf, "Backup")
        npages += 1

        for title, subpath, flavors in REGIONS:
            labels = [lab for _, _, lab in flavors]
            explicit = BACKUP_VARS[topology_of(subpath)]
            extras = leftover_vars(subpath, flavors,
                                   used[subpath] | {v for v in explicit
                                                    if not isinstance(v, tuple)})
            for var in list(explicit) + extras:
                if var in used[subpath]:  # MAIN에서 이미 보여준 변수는 건너뜀
                    continue
                name, paths = resolve_var(subpath, flavors, var)
                used[subpath].add(name)
                add_plot_page(pdf, f"{title} — {name}", labels, paths)
                npages += 1

    print(f"Wrote {out} ({npages} pages)")
    if MISSING:
        print(f"\nWARNING: {len(MISSING)} plots not found:")
        for m in MISSING:
            print(f"  {m}")


if __name__ == "__main__":
    main()
