#!/usr/bin/env python3
"""WR6000 N100/N300 priority study: overall (offshell+onshell weighted)
estimated efficiency for each selection change applied alone and combined.
est_final(region) = acc_mod(region) * eff_now(region) / acc_now(region),
then combined over regions with their event fractions."""

import glob, os
import numpy as np
import awkward as ak
import uproot

NANO = "/gv0/Users/achihwan/SKNano/Run3NanoAODv12/2023"
ANA  = "/gv0/Users/achihwan/SKNanoOutput/WRGenRecoMass/2023"
OUT  = os.path.dirname(os.path.abspath(__file__))
THR  = 4000.

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


def sr_eff(n, ch, lo, hi):
    with uproot.open(f"{ANA}/WR6000N{n}{ch}.root") as f:
        def ig(name):
            v = f[name].values(); e = f[name].axis().edges()
            return float(v[(e[:-1] >= lo) & (e[:-1] < hi)].sum())
        N = ig("LHE_mass_sumall_all_noweight")
        return (ig(f"Central/BDTSR_Resolved_{ch}_lhe_mass_noweight")
                + ig(f"Central/BDTSR_Boosted_{ch}_lhe_mass_noweight")) / N


def report(n, ch, m, acc_now, variants):
    off = np.asarray(m < THR); on = ~off
    f_off = off.mean()
    lines = [f"--- WR6000 N{n} {ch}  (offshell fraction {f_off:.1%}) ---"]
    e_off, e_on = sr_eff(n, ch, 0., THR), sr_eff(n, ch, THR, 1e9)
    tot_now = f_off * e_off + (1 - f_off) * e_on
    lines.append(f"{'now':28s} off {e_off:6.1%}  on {e_on:6.1%}  TOTAL {tot_now:6.1%}")
    for name, acc in variants:
        est_off = e_off * acc[off].mean() / max(acc_now[off].mean(), 1e-9)
        est_on  = e_on  * acc[on].mean()  / max(acc_now[on].mean(), 1e-9)
        tot = f_off * est_off + (1 - f_off) * est_on
        lines.append(f"{name:28s} off {est_off:6.1%}  on {est_on:6.1%}  "
                     f"TOTAL {tot:6.1%}  (+{tot-tot_now:.1%})")
    return lines


def main():
    out = []
    for n in (100, 300):
        # ---------------- MM ----------------
        a = load(f"WRtoNMutoMuMuJJ_MWR6000_N{n}_*", BR_MU)
        m = lhe_mass(a)
        trig = np.asarray(a["HLT_Mu50"] | a["HLT_CascadeMu100"] | a["HLT_HighPtTkMu100"])
        loose = (np.abs(a["Muon_eta"]) < 2.4) & (a["Muon_highPtId"] == 2)
        tight = loose & (a["Muon_tkRelIso"] < 0.1)
        lead = np.asarray(ak.max(ak.where(tight, a["Muon_pt"], -1.), axis=1,
                                 initial=-1., mask_identity=False))
        lidx = ak.argmax(ak.where(tight, a["Muon_pt"], -1.), axis=1, keepdims=True)
        sub = np.asarray(sub_max(a["Muon_pt"], loose, lidx))
        acc_now = trig & (lead > 60.) & (sub > 53.)
        out += report(n, "MM", m, acc_now, [
            ("sublead > 40", trig & (lead > 60.) & (sub > 40.)),
            ("sublead > 30", trig & (lead > 60.) & (sub > 30.)),
            ("sublead > 20", trig & (lead > 60.) & (sub > 20.)),
        ])
        # ---------------- EE ----------------
        a = load(f"WRtoNEltoElElJJ_MWR6000_N{n}_*", BR_EL)
        m = lhe_mass(a)
        t_old = np.asarray(a["HLT_Photon200"] | a["HLT_Ele115_CaloIdVT_GsfTrkIdT"])
        t_new = np.asarray(t_old | np.asarray(a["HLT_Ele35_WPTight_Gsf"]))
        acc_e = np.abs(a["Electron_eta"]) < 2.5
        heep = a["Electron_cutBased_HEEP"] & acc_e
        loose = ((a["Electron_cutBased"] >= 2) | a["Electron_cutBased_HEEP"]) & acc_e
        loose_m = loose | (a["Electron_mvaNoIso_WP90"] & acc_e)
        lead = np.asarray(ak.max(ak.where(heep, a["Electron_pt"], -1.), axis=1,
                                 initial=-1., mask_identity=False))
        lidx = ak.argmax(ak.where(heep, a["Electron_pt"], -1.), axis=1, keepdims=True)
        s_l  = np.asarray(sub_max(a["Electron_pt"], loose, lidx))
        s_lm = np.asarray(sub_max(a["Electron_pt"], loose_m, lidx))
        acc_now = t_old & (lead > 118.) & (s_l > 53.)
        out += report(n, "EE", m, acc_now, [
            ("+Ele35, lead>60",           t_new & (lead > 60.) & (s_l > 53.)),
            ("+mvaNoIsoWP90 only",        t_old & (lead > 118.) & (s_lm > 53.)),
            ("sublead>20 only",           t_old & (lead > 118.) & (s_l > 20.)),
            ("Ele35+lead60+ID",           t_new & (lead > 60.) & (s_lm > 53.)),
            ("Ele35+lead60+ID+sub20",     t_new & (lead > 60.) & (s_lm > 20.)),
        ])
        out.append("")
    text = "\n".join(out)
    print(text)
    open(f"{OUT}/wr6000_priority.txt", "w").write(text + "\n")


if __name__ == "__main__":
    main()
