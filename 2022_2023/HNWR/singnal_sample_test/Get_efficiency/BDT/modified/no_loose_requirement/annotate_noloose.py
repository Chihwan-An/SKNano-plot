#!/usr/bin/env python3
"""Stack panels with RED annotations for the NO-LOOSE-REQUIREMENT scenario:
the BDT boosted candidate drops the extra-loose-lepton (and mll>200 pair)
requirement entirely -> candidate = trigger + lead tight + AK8 (pT>200).

Newly passing events = currently failing the loose step (no loose sublead
with pT>53) but having trigger + lead tight + an AK8 fatjet; they add to the
BOOSTED category, resolved is unchanged. Estimated at the lepton+trigger+AK8
stage on NanoAOD (noise filter / jet veto / fatjet ID not applied: a few %p
optimistic). Background caveat: without mll>200 this becomes a single-lepton
+ fatjet selection (W+jets / semileptonic ttbar enter) - signal-only numbers.

Outputs: WR4000_summary_annotated.png, WR6000_summary_annotated.png
"""

import glob, os, sys
import numpy as np
import awkward as ak
import uproot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep

hep.style.use("CMS")
GE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "..", "..", ".."))
sys.path.insert(0, GE_DIR)
import make_summary as ms

NANO = "/gv0/Users/achihwan/SKNano/Run3NanoAODv12/2023"
OUT  = os.path.dirname(os.path.abspath(__file__))
N_LIST = [100, 300, 500]

BRC = ["LHEPart_pt", "LHEPart_eta", "LHEPart_phi", "LHEPart_mass", "LHEPart_status",
       "FatJet_pt", "FatJet_eta"]
BR_MU = ["Muon_pt", "Muon_eta", "Muon_highPtId", "Muon_tkRelIso",
         "HLT_Mu50", "HLT_CascadeMu100", "HLT_HighPtTkMu100"] + BRC
BR_EL = ["Electron_pt", "Electron_eta", "Electron_cutBased", "Electron_cutBased_HEEP",
         "HLT_Photon200", "HLT_Ele115_CaloIdVT_GsfTrkIdT"] + BRC


def load(tag, br):
    fs = sorted(glob.glob(f"{NANO}/{tag}/**/*.root", recursive=True))
    return ak.concatenate([uproot.open(p)["Events"].arrays(br) for p in fs])


def lhe_mass(a):
    st1 = a["LHEPart_status"] == 1
    pt, eta, phi, m = (a[f"LHEPart_{k}"][st1] for k in ("pt", "eta", "phi", "mass"))
    px = ak.sum(pt * np.cos(phi), axis=1); py = ak.sum(pt * np.sin(phi), axis=1)
    pz = ak.sum(pt * np.sinh(eta), axis=1)
    e = ak.sum(np.sqrt((pt * np.cosh(eta))**2 + m**2), axis=1)
    return np.sqrt(np.maximum(e**2 - px**2 - py**2 - pz**2, 0.))


def sub_max(pt, mask, lidx):
    li = ak.fill_none(ak.firsts(lidx), -1)
    return ak.max(ak.where(mask & (ak.local_index(pt, axis=1) != li), pt, -1.),
                  axis=1, initial=-1., mask_identity=False)


def new_pass_fracs(wr, n, ch, thr):
    """(gain_off, gain_on): fraction of region events newly passing when the
    loose requirement is dropped (fail loose now, but trig+lead-tight+AK8)."""
    if ch == "MM":
        a = load(f"WRtoNMutoMuMuJJ_MWR{wr}_N{n}_*", BR_MU)
        trig = np.asarray(a["HLT_Mu50"] | a["HLT_CascadeMu100"] | a["HLT_HighPtTkMu100"])
        loose = (np.abs(a["Muon_eta"]) < 2.4) & (a["Muon_highPtId"] == 2)
        tight = loose & (a["Muon_tkRelIso"] < 0.1)
        lead = np.asarray(ak.max(ak.where(tight, a["Muon_pt"], -1.), axis=1,
                                 initial=-1., mask_identity=False))
        lidx = ak.argmax(ak.where(tight, a["Muon_pt"], -1.), axis=1, keepdims=True)
        sub = np.asarray(sub_max(a["Muon_pt"], loose, lidx))
        leadcut = 60.
    else:
        a = load(f"WRtoNEltoElElJJ_MWR{wr}_N{n}_*", BR_EL)
        trig = np.asarray(a["HLT_Photon200"] | a["HLT_Ele115_CaloIdVT_GsfTrkIdT"])
        acc = np.abs(a["Electron_eta"]) < 2.5
        heep = a["Electron_cutBased_HEEP"] & acc
        loose = ((a["Electron_cutBased"] >= 2) | a["Electron_cutBased_HEEP"]) & acc
        lead = np.asarray(ak.max(ak.where(heep, a["Electron_pt"], -1.), axis=1,
                                 initial=-1., mask_identity=False))
        lidx = ak.argmax(ak.where(heep, a["Electron_pt"], -1.), axis=1, keepdims=True)
        sub = np.asarray(sub_max(a["Electron_pt"], loose, lidx))
        leadcut = 118.
    m = lhe_mass(a)
    ak8 = np.asarray(ak.sum((a["FatJet_pt"] > 200.) & (np.abs(a["FatJet_eta"]) < 2.5),
                            axis=1)) >= 1
    newp = trig & (lead > leadcut) & (sub < 53.) & ak8
    off = np.asarray(m < thr)
    return newp[off].mean(), newp[~off].mean()


def main():
    sel = ms.SELECTIONS["BDT"]
    for wr in (4000, 6000):
        thr = ms.WR_POINTS[wr]
        fig, axes = plt.subplots(2, 3, figsize=(21.6, 13))
        for j, n in enumerate(N_LIST):
            for i, ch in enumerate(ms.CHANNELS):
                ax = axes[i][j]
                data = ms.load_sample(wr, n, ch, sel)
                ms.draw_stack(ax, data, wr, n, ch, sel["title"] + " · no-loose est. in red")
                if data is None or data["all"] is None:
                    continue
                try:
                    g_off, g_on = new_pass_fracs(wr, n, ch, thr)
                except Exception as err:
                    print(f"WR{wr}N{n}{ch}: NanoAOD failed ({err})")
                    continue
                n_off, n_on = data["n_off"] or 0., data["n_on"] or 0.
                if n_off > 0:
                    bo = data["boo_off"] / n_off
                    ax.text(0.03, 0.72, f"res unchanged\n$\\rightarrow$ boo "
                            f"{bo+g_off:.1%} (+{g_off:.1%})",
                            transform=ax.transAxes, fontsize=9.5, va="top",
                            color="red", linespacing=1.4)
                if n_on > 0:
                    bn = data["boo_on"] / n_on
                    ax.text(0.97, 0.72, f"res unchanged\nboo {bn+g_on:.1%} "
                            f"(+{g_on:.1%}) $\\leftarrow$",
                            transform=ax.transAxes, fontsize=9.5, va="top",
                            ha="right", color="red", linespacing=1.4)
                tot_now = (data["res_off"] + data["boo_off"]
                           + data["res_on"] + data["boo_on"]) / (n_off + n_on)
                tot_new = tot_now + (g_off * n_off + g_on * n_on) / (n_off + n_on)
                ax.text(0.5, 0.02, f"TOTAL {tot_now:.1%} $\\rightarrow$ "
                        f"{tot_new:.1%} (+{tot_new-tot_now:.1%})",
                        transform=ax.transAxes, ha="center", va="bottom",
                        fontsize=11, color="red", fontweight="bold")
                print(f"WR{wr}N{n}{ch}: off +{g_off:.1%} on +{g_on:.1%} "
                      f"total {tot_now:.1%} -> {tot_new:.1%}")
        fig.suptitle(f"WR{wr} — BDT presel, NO extra-loose-lepton requirement "
                     "(red: boosted = trig + lead tight + AK8; signal-only estimate, "
                     "mll>200 DY suppression lost)", fontsize=14)
        fig.tight_layout()
        out = f"{OUT}/WR{wr}_summary_annotated.png"
        fig.savefig(out, dpi=110)
        plt.close(fig)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
