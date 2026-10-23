#!/usr/bin/env python3
"""NanoAOD-level recovery study for the BDT preselection (2023 signal MC).

1) MM offshell: pT spectrum of the SUBLEAD muon (highest-pT highPtId==2 muon
   besides the tight lead) in events with a tight lead muon — how much sits
   below the 53 GeV threshold, and the cumulative recovery vs a lower cut.
2) EE trigger: event-level gain from adding HLT_Ele35_WPTight_Gsf to the
   electron OR (Photon200 || Ele115), with the lead-electron pT cut relaxed
   to 60 (same as the muon channel; Ele35 makes ~38 GeV trigger-safe).
3) EE loose-ID candidates: for 2nd electrons with pT > 53 that FAIL the
   current loose (approx: cutBased>=2 || HEEP — the analyzer LooseNoIso is
   cutBased-loose without the iso bits, so this is a slightly tight proxy),
   the pass fraction of every alternative ID -> which one recovers most.

Offshell/onshell split: invariant mass of all status==1 LHE particles,
boundary 2000 (WR4000) / 4000 (WR6000), matching the analyzer definition.
"""

import glob, os
import numpy as np
import awkward as ak
import uproot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep

hep.style.use("CMS")

NANO = "/gv0/Users/achihwan/SKNano/Run3NanoAODv12/2023"
OUT  = os.path.dirname(os.path.abspath(__file__))
THR  = {4000: 2000., 6000: 4000.}
SAMPLES = [(wr, n) for wr in (4000, 6000) for n in (100, 300)]

MU_BR = ["Muon_pt", "Muon_eta", "Muon_highPtId", "Muon_tkRelIso",
         "LHEPart_pt", "LHEPart_eta", "LHEPart_phi", "LHEPart_mass", "LHEPart_status"]
EL_BR = ["Electron_pt", "Electron_eta", "Electron_cutBased", "Electron_cutBased_HEEP",
         "Electron_mvaIso_WP80", "Electron_mvaIso_WP90",
         "Electron_mvaNoIso_WP80", "Electron_mvaNoIso_WP90",
         "Electron_mvaIso", "Electron_mvaNoIso",
         "HLT_Photon200", "HLT_Ele115_CaloIdVT_GsfTrkIdT", "HLT_Ele35_WPTight_Gsf",
         "LHEPart_pt", "LHEPart_eta", "LHEPart_phi", "LHEPart_mass", "LHEPart_status"]

EL_IDS = [
    ("cutBased Loose",   lambda a: a["Electron_cutBased"] >= 2),
    ("cutBased Medium",  lambda a: a["Electron_cutBased"] >= 3),
    ("cutBased Tight",   lambda a: a["Electron_cutBased"] >= 4),
    ("mvaIso WP80",      lambda a: a["Electron_mvaIso_WP80"]),
    ("mvaIso WP90",      lambda a: a["Electron_mvaIso_WP90"]),
    ("mvaNoIso WP80",    lambda a: a["Electron_mvaNoIso_WP80"]),
    ("mvaNoIso WP90",    lambda a: a["Electron_mvaNoIso_WP90"]),
]


def load(dataset_tag, branches):
    files = sorted(glob.glob(f"{NANO}/{dataset_tag}/**/*.root", recursive=True))
    return ak.concatenate([uproot.open(p)["Events"].arrays(branches) for p in files])


def lhe_mass(a):
    st1 = a["LHEPart_status"] == 1
    pt, eta, phi, m = (a[f"LHEPart_{k}"][st1] for k in ("pt", "eta", "phi", "mass"))
    px = ak.sum(pt * np.cos(phi), axis=1)
    py = ak.sum(pt * np.sin(phi), axis=1)
    pz = ak.sum(pt * np.sinh(eta), axis=1)
    e  = ak.sum(np.sqrt((pt * np.cosh(eta))**2 + m**2), axis=1)
    return np.sqrt(np.maximum(e**2 - px**2 - py**2 - pz**2, 0.))


# ---------------------------------------------------------------- 1) MM sublead pT
def muon_part():
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    lines = ["=== MM offshell: sublead (highPtId==2) muon pT, events with tight lead ==="]
    for ax, (wr, n) in zip(axes.flatten(), SAMPLES):
        a = load(f"WRtoNMutoMuMuJJ_MWR{wr}_N{n}_*", MU_BR)
        off = lhe_mass(a) < THR[wr]
        a = a[off]
        n_off = len(a)
        good = (np.abs(a["Muon_eta"]) < 2.4) & (a["Muon_highPtId"] == 2)
        tight = good & (a["Muon_tkRelIso"] < 0.1) & (a["Muon_pt"] > 60.)
        has_lead = ak.any(tight, axis=1)
        b = a[has_lead]
        # lead = highest-pT tight muon; sublead = highest-pT other highPtId muon
        pt_t = ak.where(tight[has_lead], b["Muon_pt"], -1.)
        lead_idx = ak.argmax(pt_t, axis=1, keepdims=True)
        loose_b = (np.abs(b["Muon_eta"]) < 2.4) & (b["Muon_highPtId"] == 2) & (b["Muon_pt"] > 10.)
        notlead = ak.local_index(b["Muon_pt"], axis=1) != ak.flatten(lead_idx)
        pt_s = ak.where(loose_b & notlead, b["Muon_pt"], -1.)
        sub = ak.max(pt_s, axis=1, initial=-1., mask_identity=False)
        sub = np.asarray(sub[sub > 0.])
        w = np.ones_like(sub) / max(n_off, 1)
        ax.hist(sub, bins=50, range=(0., 100.), weights=w, color="steelblue")
        ax.axvline(53., color="black", ls=":", lw=1.5)
        ax.set_xlabel(r"sublead $\mu$ (highPtId) $p_T$ [GeV]", fontsize=12)
        ax.set_ylabel("fraction of offshell events / 2 GeV", fontsize=12)
        ax.set_title(f"WR{wr} N{n} MM (offshell)", fontsize=13, loc="left")
        cums = {thr: (sub >= thr).sum() / n_off - (sub >= 53.).sum() / n_off
                for thr in (20., 30., 40.)}
        txt = "\n".join([f"recover vs cut:"] +
                        [f"  >{t:.0f}: +{v:.1%}" for t, v in cums.items()])
        ax.text(0.97, 0.95, txt, transform=ax.transAxes, ha="right", va="top",
                fontsize=10, color="#444444")
        lines.append(f"WR{wr}N{n}MM: offshell N={n_off}, tight-lead {len(b)/n_off:.1%}, "
                     "sublead-in-[cut,53) gain: " +
                     ", ".join(f">{t:.0f}GeV +{v:.1%}" for t, v in cums.items()))
    fig.tight_layout()
    fig.savefig(f"{OUT}/sublead_muon_pt_offshell.png", dpi=110)
    plt.close(fig)
    return lines


# ---------------------------------------------------------------- 2+3) EE studies
def electron_part():
    lines = ["", "=== EE trigger: OR + HLT_Ele35_WPTight_Gsf, lead pT > 60 ==="]
    agg = {}   # (region) -> dict(name -> [pass, tot]) aggregated over samples
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    for wr, n in SAMPLES:
        a = load(f"WRtoNEltoElElJJ_MWR{wr}_N{n}_*", EL_BR)
        m = lhe_mass(a)
        heep = a["Electron_cutBased_HEEP"] & (np.abs(a["Electron_eta"]) < 2.5)
        lead_pt = ak.max(ak.where(heep, a["Electron_pt"], -1.), axis=1, initial=-1., mask_identity=False)
        for reg, sel in (("off", m < THR[wr]), ("on", m >= THR[wr])):
            b = a[sel]
            n_reg = len(b)
            if reg == "off":
                old = np.asarray(b["HLT_Photon200"] | b["HLT_Ele115_CaloIdVT_GsfTrkIdT"])
                new = np.asarray(old | b["HLT_Ele35_WPTight_Gsf"])
                lp = np.asarray(lead_pt[sel])
                usable_old = old & (lp > 118.)   # current effective safe cut
                usable_new = new & (lp > 60.)    # Ele35 makes 60 trigger-safe
                lines.append(f"WR{wr}N{n}EE off: HLT-fired {old.sum()/n_reg:.1%} -> "
                             f"{new.sum()/n_reg:.1%} (+{(new.sum()-old.sum())/n_reg:.1%}); "
                             f"fired & lead>cut: {usable_old.sum()/n_reg:.1%} -> "
                             f"{usable_new.sum()/n_reg:.1%} (+{(usable_new.sum()-usable_old.sum())/n_reg:.1%})")
            # ---- 2nd-electron ID candidates: pT>53, fails current loose ----
            has_lead = np.asarray(lead_pt[sel]) > 60.
            c = b[has_lead]
            heep_c = c["Electron_cutBased_HEEP"] & (np.abs(c["Electron_eta"]) < 2.5)
            pt_l = ak.where(heep_c, c["Electron_pt"], -1.)
            lidx = ak.argmax(pt_l, axis=1, keepdims=True)
            notlead = ak.local_index(c["Electron_pt"], axis=1) != ak.flatten(lidx)
            cur_loose = (c["Electron_cutBased"] >= 2) | c["Electron_cutBased_HEEP"]
            cand = (notlead & (c["Electron_pt"] > 53.) & (np.abs(c["Electron_eta"]) < 2.5)
                    & ~cur_loose)
            n_cand = int(ak.sum(ak.any(cand, axis=1)))
            key = reg
            agg.setdefault(key, {nm: [0, 0] for nm, _ in EL_IDS})
            for nm, fn in EL_IDS:
                npass = int(ak.sum(ak.any(cand & fn(c), axis=1)))
                agg[key][nm][0] += npass
                agg[key][nm][1] += n_cand
    lines.append("")
    lines.append("=== EE 2nd-electron (pT>53, fails current loose) — alternative-ID pass fraction ===")
    for i, (reg, ax) in enumerate(zip(("off", "on"), axes)):
        names = [nm for nm, _ in EL_IDS]
        fr = [agg[reg][nm][0] / max(agg[reg][nm][1], 1) for nm in names]
        y = np.arange(len(names))
        ax.barh(y, fr, height=0.6, color="tomato" if reg == "off" else "darkred")
        ax.set_yticks(y); ax.set_yticklabels(names, fontsize=12)
        ax.invert_yaxis()
        ax.set_xlim(0, 1.05 * max(fr + [0.05]))
        for yi, v in zip(y, fr):
            ax.text(v + 0.01, yi, f"{v:.1%}", va="center", fontsize=11, color="#333333")
        ax.set_xlabel("pass fraction of failing 2nd electrons", fontsize=12)
        ax.set_title(f"{'Offshell' if reg=='off' else 'Onshell'}  "
                     f"(N cand = {agg[reg][names[0]][1]})", fontsize=13, loc="left")
        lines.append(f"[{reg}] " + ", ".join(f"{nm} {f:.1%}" for nm, f in zip(names, fr)))
    fig.suptitle("Which ID recovers the lost 2nd electron?  (WR4000+6000, N100+N300, 2023)",
                 fontsize=15)
    fig.tight_layout()
    fig.savefig(f"{OUT}/electron_id_comparison.png", dpi=110)
    plt.close(fig)
    return lines


def main():
    lines = muon_part() + electron_part()
    text = "\n".join(lines)
    print(text)
    with open(f"{OUT}/results.txt", "w") as fh:
        fh.write(text + "\n")
    print(f"\nwrote {OUT}/sublead_muon_pt_offshell.png")
    print(f"wrote {OUT}/electron_id_comparison.png")
    print(f"wrote {OUT}/results.txt")


if __name__ == "__main__":
    main()
