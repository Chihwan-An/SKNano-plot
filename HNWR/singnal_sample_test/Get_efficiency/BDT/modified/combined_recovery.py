#!/usr/bin/env python3
"""(1) EE sublead-electron pT spectrum (offshell), filled = passes the loose
proxy (cutBased>=2 || HEEP), outline = any reco electron -> the gap is the
ID-lost part that a pT change cannot recover.

(2) Combined recovery: lepton+trigger-stage acceptance per region, current vs
modified selection, and an estimated final (res+boo) efficiency obtained by
scaling with the observed downstream efficiency ratio
  est_final = acc_mod * (SR_eff_now / acc_now)
(downstream jets/mll/category efficiency assumed unchanged - an estimate).

Modified selection:
  MM: sublead loose(highPtId) muon pT > 20 (instead of 53)
  EE: HLT OR += Ele35_WPTight, lead HEEP pT > 60 (instead of 118 safe cut),
      sublead loose OR mvaNoIso_WP90, pT kept at 53
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
ANA  = "/gv0/Users/achihwan/SKNanoOutput/WRGenRecoMass/2023"
OUT  = os.path.dirname(os.path.abspath(__file__))
THR  = {4000: 2000., 6000: 4000.}
SAMPLES = [(wr, n) for wr in (4000, 6000) for n in (100, 300)]

BR_COMMON = ["LHEPart_pt", "LHEPart_eta", "LHEPart_phi", "LHEPart_mass", "LHEPart_status"]
BR_MU = ["Muon_pt", "Muon_eta", "Muon_highPtId", "Muon_tkRelIso",
         "HLT_Mu50", "HLT_CascadeMu100", "HLT_HighPtTkMu100"] + BR_COMMON
BR_EL = ["Electron_pt", "Electron_eta", "Electron_cutBased", "Electron_cutBased_HEEP",
         "Electron_mvaNoIso_WP90",
         "HLT_Photon200", "HLT_Ele115_CaloIdVT_GsfTrkIdT", "HLT_Ele35_WPTight_Gsf"] + BR_COMMON


def load(tag, branches):
    files = sorted(glob.glob(f"{NANO}/{tag}/**/*.root", recursive=True))
    return ak.concatenate([uproot.open(p)["Events"].arrays(branches) for p in files])


def lhe_mass(a):
    st1 = a["LHEPart_status"] == 1
    pt, eta, phi, m = (a[f"LHEPart_{k}"][st1] for k in ("pt", "eta", "phi", "mass"))
    px = ak.sum(pt * np.cos(phi), axis=1)
    py = ak.sum(pt * np.sin(phi), axis=1)
    pz = ak.sum(pt * np.sinh(eta), axis=1)
    e  = ak.sum(np.sqrt((pt * np.cosh(eta))**2 + m**2), axis=1)
    return np.sqrt(np.maximum(e**2 - px**2 - py**2 - pz**2, 0.))


def sub_max(pt, mask, lead_idx):
    li = ak.fill_none(ak.firsts(lead_idx), -1)
    notlead = ak.local_index(pt, axis=1) != li
    return ak.max(ak.where(mask & notlead, pt, -1.), axis=1, initial=-1., mask_identity=False)


def sr_eff_now(wr, n, ch, lo, hi):
    with uproot.open(f"{ANA}/WR{wr}N{n}{ch}.root") as f:
        def ig(name):
            v = f[name].values(); e = f[name].axis().edges()
            return float(v[(e[:-1] >= lo) & (e[:-1] < hi)].sum())
        N = ig("LHE_mass_sumall_all_noweight")
        return (ig(f"Central/BDTSR_Resolved_{ch}_lhe_mass_noweight")
                + ig(f"Central/BDTSR_Boosted_{ch}_lhe_mass_noweight")) / N


def main():
    lines = []
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    rows = []
    for iax, (wr, n) in enumerate(SAMPLES):
        # ---------------- MM ----------------
        a = load(f"WRtoNMutoMuMuJJ_MWR{wr}_N{n}_*", BR_MU)
        m = lhe_mass(a)
        trig_mu = a["HLT_Mu50"] | a["HLT_CascadeMu100"] | a["HLT_HighPtTkMu100"]
        loose = (np.abs(a["Muon_eta"]) < 2.4) & (a["Muon_highPtId"] == 2)
        tight = loose & (a["Muon_tkRelIso"] < 0.1)
        lead_pt = ak.max(ak.where(tight, a["Muon_pt"], -1.), axis=1,
                         initial=-1., mask_identity=False)
        lidx = ak.argmax(ak.where(tight, a["Muon_pt"], -1.), axis=1, keepdims=True)
        sub = sub_max(a["Muon_pt"], loose, lidx)
        acc_now = np.asarray(trig_mu) & (np.asarray(lead_pt) > 60.) & (np.asarray(sub) > 53.)
        acc_mod = np.asarray(trig_mu) & (np.asarray(lead_pt) > 60.) & (np.asarray(sub) > 20.)
        for reg, sel in (("off", m < THR[wr]), ("on", m >= THR[wr])):
            s = np.asarray(sel)
            a0, a1 = acc_now[s].mean(), acc_mod[s].mean()
            eff = sr_eff_now(wr, n, "MM", *((0., THR[wr]) if reg == "off" else (THR[wr], 1e9)))
            est = eff * a1 / max(a0, 1e-9)
            rows.append((f"WR{wr}N{n}", "MM", reg, a0, a1, eff, est))
        # ---------------- EE ----------------
        a = load(f"WRtoNEltoElElJJ_MWR{wr}_N{n}_*", BR_EL)
        m = lhe_mass(a)
        trig_old = a["HLT_Photon200"] | a["HLT_Ele115_CaloIdVT_GsfTrkIdT"]
        trig_new = trig_old | a["HLT_Ele35_WPTight_Gsf"]
        in_acc = np.abs(a["Electron_eta"]) < 2.5
        heep = a["Electron_cutBased_HEEP"] & in_acc
        loose = ((a["Electron_cutBased"] >= 2) | a["Electron_cutBased_HEEP"]) & in_acc
        loose_mod = (loose | (a["Electron_mvaNoIso_WP90"] & in_acc))
        lead_pt = ak.max(ak.where(heep, a["Electron_pt"], -1.), axis=1,
                         initial=-1., mask_identity=False)
        lidx = ak.argmax(ak.where(heep, a["Electron_pt"], -1.), axis=1, keepdims=True)
        sub_l  = sub_max(a["Electron_pt"], loose, lidx)
        sub_lm = sub_max(a["Electron_pt"], loose_mod, lidx)
        sub_all = sub_max(a["Electron_pt"], in_acc & (a["Electron_pt"] > 10.), lidx)
        acc_now = (np.asarray(trig_old) & (np.asarray(lead_pt) > 118.)
                   & (np.asarray(sub_l) > 53.))
        acc_mod = (np.asarray(trig_new) & (np.asarray(lead_pt) > 60.)
                   & (np.asarray(sub_lm) > 53.))
        for reg, sel in (("off", m < THR[wr]), ("on", m >= THR[wr])):
            s = np.asarray(sel)
            a0, a1 = acc_now[s].mean(), acc_mod[s].mean()
            eff = sr_eff_now(wr, n, "EE", *((0., THR[wr]) if reg == "off" else (THR[wr], 1e9)))
            est = eff * a1 / max(a0, 1e-9)
            rows.append((f"WR{wr}N{n}", "EE", reg, a0, a1, eff, est))
        # ---- sublead-electron pT spectrum (offshell), loose vs all-reco ----
        ax = axes.flatten()[iax]
        off = np.asarray(m < THR[wr]) & (np.asarray(lead_pt) > 0.)
        n_off = int(np.asarray(m < THR[wr]).sum())
        v_l = np.asarray(sub_l[off]);  v_l = v_l[v_l > 0.]
        v_a = np.asarray(sub_all[off]); v_a = v_a[v_a > 0.]
        bins = np.linspace(0., 100., 51)
        ax.hist(v_a, bins=bins, weights=np.ones_like(v_a) / n_off,
                histtype="step", color="dimgray", lw=1.8, label="any reco e")
        ax.hist(v_l, bins=bins, weights=np.ones_like(v_l) / n_off,
                color="tomato", alpha=0.85, label="passes loose (proxy)")
        ax.axvline(53., color="black", ls=":", lw=1.5)
        cums = {t: ((v_l >= t).sum() - (v_l >= 53.).sum()) / n_off for t in (20., 30., 40.)}
        ax.text(0.97, 0.72, "recover vs cut (loose):\n" +
                "\n".join(f"  >{t:.0f}: +{v:.1%}" for t, v in cums.items()),
                transform=ax.transAxes, ha="right", va="top", fontsize=10, color="#444444")
        ax.set_xlabel(r"sublead e $p_T$ [GeV]", fontsize=12)
        ax.set_ylabel("fraction of offshell events / 2 GeV", fontsize=12)
        ax.set_title(f"WR{wr} N{n} EE (offshell)", fontsize=13, loc="left")
        ax.legend(fontsize=10, frameon=False)
    fig.tight_layout()
    fig.savefig(f"{OUT}/sublead_electron_pt_offshell.png", dpi=110)
    plt.close(fig)

    lines.append("=== combined recovery: lepton+trigger acceptance & estimated final eff ===")
    lines.append("modified = MM sublead>20 | EE +Ele35, lead>60, loose||mvaNoIsoWP90")
    lines.append(f"{'sample':12s} {'ch':3s} {'reg':4s} {'acc now':>8s} {'acc mod':>8s} "
                 f"{'eff now':>8s} {'est eff':>8s} {'gain':>7s}")
    for smp, ch, reg, a0, a1, eff, est in rows:
        lines.append(f"{smp:12s} {ch:3s} {reg:4s} {a0:8.1%} {a1:8.1%} "
                     f"{eff:8.1%} {est:8.1%} {est-eff:+7.1%}")
    text = "\n".join(lines)
    print(text)
    with open(f"{OUT}/combined_recovery.txt", "w") as fh:
        fh.write(text + "\n")
    print(f"\nwrote {OUT}/sublead_electron_pt_offshell.png")


if __name__ == "__main__":
    main()
