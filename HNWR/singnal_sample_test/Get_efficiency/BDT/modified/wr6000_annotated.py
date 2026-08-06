#!/usr/bin/env python3
"""WR6000 BDT summary stack panels with RED annotations showing the estimated
efficiency after the modified selection:
  MM: sublead loose muon pT > 20
  EE: HLT OR += Ele35_WPTight, lead HEEP pT > 60, loose||mvaNoIso_WP90,
      sublead pT > 20
est(region) = eff_now(region) * acc_mod(region)/acc_now(region)  (lepton+trigger
stage measured on NanoAOD; downstream efficiency assumed unchanged).
Output: WR6000_summary_annotated.png
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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import make_summary as ms

NANO = "/gv0/Users/achihwan/SKNano/Run3NanoAODv12/2023"
OUT  = os.path.dirname(os.path.abspath(__file__))
THR  = 4000.
N_LIST = [100, 300, 500]

BRC = ["LHEPart_pt", "LHEPart_eta", "LHEPart_phi", "LHEPart_mass", "LHEPart_status"]
BR_MU = ["Muon_pt", "Muon_eta", "Muon_highPtId", "Muon_tkRelIso",
         "HLT_Mu50", "HLT_CascadeMu100", "HLT_HighPtTkMu100"] + BRC
BR_EL = ["Electron_pt", "Electron_eta", "Electron_cutBased", "Electron_cutBased_HEEP",
         "Electron_mvaNoIso_WP90",
         "HLT_Photon200", "HLT_Ele115_CaloIdVT_GsfTrkIdT", "HLT_Ele35_WPTight_Gsf"] + BRC


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


def acc_ratios(n, ch):
    """(ratio_off, ratio_on) = acc_mod/acc_now per region for WR6000 N=n."""
    if ch == "MM":
        a = load(f"WRtoNMutoMuMuJJ_MWR6000_N{n}_*", BR_MU)
        m = lhe_mass(a)
        trig = np.asarray(a["HLT_Mu50"] | a["HLT_CascadeMu100"] | a["HLT_HighPtTkMu100"])
        loose = (np.abs(a["Muon_eta"]) < 2.4) & (a["Muon_highPtId"] == 2)
        tight = loose & (a["Muon_tkRelIso"] < 0.1)
        lead = np.asarray(ak.max(ak.where(tight, a["Muon_pt"], -1.), axis=1,
                                 initial=-1., mask_identity=False))
        lidx = ak.argmax(ak.where(tight, a["Muon_pt"], -1.), axis=1, keepdims=True)
        sub = np.asarray(sub_max(a["Muon_pt"], loose, lidx))
        now = trig & (lead > 60.) & (sub > 53.)
        mod = trig & (lead > 60.) & (sub > 20.)
    else:
        a = load(f"WRtoNEltoElElJJ_MWR6000_N{n}_*", BR_EL)
        m = lhe_mass(a)
        t_old = np.asarray(a["HLT_Photon200"] | a["HLT_Ele115_CaloIdVT_GsfTrkIdT"])
        t_new = np.asarray(t_old | np.asarray(a["HLT_Ele35_WPTight_Gsf"]))
        acc = np.abs(a["Electron_eta"]) < 2.5
        heep = a["Electron_cutBased_HEEP"] & acc
        loose = ((a["Electron_cutBased"] >= 2) | a["Electron_cutBased_HEEP"]) & acc
        loose_m = loose | (a["Electron_mvaNoIso_WP90"] & acc)
        lead = np.asarray(ak.max(ak.where(heep, a["Electron_pt"], -1.), axis=1,
                                 initial=-1., mask_identity=False))
        lidx = ak.argmax(ak.where(heep, a["Electron_pt"], -1.), axis=1, keepdims=True)
        s_l  = np.asarray(sub_max(a["Electron_pt"], loose, lidx))
        s_lm = np.asarray(sub_max(a["Electron_pt"], loose_m, lidx))
        now = t_old & (lead > 118.) & (s_l > 53.)
        mod = t_new & (lead > 60.) & (s_lm > 20.)
    off = np.asarray(m < THR)
    r_off = mod[off].mean() / max(now[off].mean(), 1e-9)
    r_on  = mod[~off].mean() / max(now[~off].mean(), 1e-9)
    return r_off, r_on


def main():
    sel = ms.SELECTIONS["BDT"]
    fig, axes = plt.subplots(2, 3, figsize=(21.6, 13))
    for j, n in enumerate(N_LIST):
        for i, ch in enumerate(ms.CHANNELS):
            ax = axes[i][j]
            data = ms.load_sample(6000, n, ch, sel)
            ms.draw_stack(ax, data, 6000, n, ch, sel["title"] + " · modified est. in red")
            if data is None or data["all"] is None:
                continue
            try:
                r_off, r_on = acc_ratios(n, ch)
            except Exception as err:
                print(f"N{n}{ch}: NanoAOD acc failed ({err}); skipping annotation")
                continue
            n_off, n_on = data["n_off"] or 0., data["n_on"] or 0.
            if n_off > 0:
                ro, bo = data["res_off"] / n_off, data["boo_off"] / n_off
                txt = (f"$\\rightarrow$ res {ro*r_off:.1%} (+{ro*(r_off-1):.1%})"
                       f"\n$\\rightarrow$ boo {bo*r_off:.1%} (+{bo*(r_off-1):.1%})")
                ax.text(0.03, 0.72, txt, transform=ax.transAxes, fontsize=9.5,
                        va="top", color="red", linespacing=1.4)
            if n_on > 0:
                rn, bn = data["res_on"] / n_on, data["boo_on"] / n_on
                txt = (f"res {rn*r_on:.1%} (+{rn*(r_on-1):.1%}) $\\leftarrow$"
                       f"\nboo {bn*r_on:.1%} (+{bn*(r_on-1):.1%}) $\\leftarrow$")
                ax.text(0.97, 0.72, txt, transform=ax.transAxes, fontsize=9.5,
                        va="top", ha="right", color="red", linespacing=1.4)
            tot_now = (data["res_off"] + data["boo_off"] + data["res_on"] + data["boo_on"]) \
                      / (n_off + n_on)
            tot_mod = ((data["res_off"] + data["boo_off"]) * r_off
                       + (data["res_on"] + data["boo_on"]) * r_on) / (n_off + n_on)
            ax.text(0.5, 0.02, f"TOTAL {tot_now:.1%} $\\rightarrow$ "
                    f"{tot_mod:.1%} (+{tot_mod-tot_now:.1%})",
                    transform=ax.transAxes, ha="center", va="bottom",
                    fontsize=11, color="red", fontweight="bold")
            print(f"N{n}{ch}: r_off={r_off:.3f} r_on={r_on:.3f} "
                  f"total {tot_now:.1%} -> {tot_mod:.1%}")
    fig.suptitle("WR6000 — BDT presel with modified selection (red: estimated after "
                 "MM sub>20 | EE +Ele35, lead>60, +mvaNoIsoWP90, sub>20)", fontsize=15)
    fig.tight_layout()
    fig.savefig(f"{OUT}/WR6000_summary_annotated.png", dpi=110)
    print(f"wrote {OUT}/WR6000_summary_annotated.png")


if __name__ == "__main__":
    main()
