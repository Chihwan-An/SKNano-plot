#!/usr/bin/env python3
"""SS data vs charge-flip prediction split by pair charge (e+e+ / e-e-), cutbased style, three regions:
  jetincl     60<m_ee<150, no jet requirement
  mlljj_gt800 resolved, 60<m_ee<150, m_lljj>800 (= DY CR)
  mlljj_lt800 resolved, 60<m_ee<150, m_lljj<800
Charge-aware flip prediction from OS data: an OS pair becomes ++ when its e- flips and -- when its e+ flips, so
  w(++) = P(e-)(1-P(e+)) / D,  w(--) = P(e+)(1-P(e-)) / D,  D = (1-P1)(1-P2)+P1P2   (w(++)+w(--) = the usual w).
Non-flip SS from MC (no flipped electron), split by the pair sign. Systematic band as in chargeflip_apply_plots.py.
  out/Resolve/DY/chargeflip/ss_sign/<region>/<pp|mm>/<var>_plot.png
"""
import argparse, json, os, sys
import numpy as np
import ROOT
NANO15 = os.path.join(os.environ.get("SKNANO_HOME", "/data9/Users/achihwan/nano15/SKNanoAnalyzer"), "Nano15_Analyzers")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chargeflip_plots as cfp
sys.path.insert(0, os.path.join(NANO15, "BDT/SR/test/scripts"))
import chargeflip_ddss as dd

GROUPS = {"Flip": ("kOrange", "Charge flip (OS #times w)"), "DYJets": ("kYellow", "Drell-Yan non-flip"),
          "TT": ("kRed", "T#bar{T}+tW non-flip"), "Nonprompt": ("kGreen+2", "Nonprompt"), "Others": ("kBlue", "Others (WZ/ZZ)")}
MLL = lambda d: (d["m_l1l2"] > 60) & (d["m_l1l2"] < 150)
REG = {"jetincl": (MLL, "jet-inclusive"),
       "mlljj_gt800": (lambda d: d["isDYCR"] > 0, "m_{lljj} > 800"),
       "mlljj_lt800": (lambda d: (d["passResolved"] > 0) & MLL(d) & (d["m_lljj"] < 800), "m_{lljj} < 800")}
REG7 = {"jetincl_zpeak": (lambda d: (d["m_l1l2"] > 80) & (d["m_l1l2"] < 100), "jet-incl, 80<m_{ee}<100"),
        "jetincl_60to150": (MLL, "jet-incl, 60<m_{ee}<150"),
        "jetincl_sideband": (lambda d: ((d["m_l1l2"] > 60) & (d["m_l1l2"] < 80)) | ((d["m_l1l2"] > 100) & (d["m_l1l2"] < 150)), "jet-incl, m_{ee} sidebands"),
        "jetincl_60to80": (lambda d: (d["m_l1l2"] > 60) & (d["m_l1l2"] < 80), "jet-incl, 60<m_{ee}<80"),
        "jetincl_100to150": (lambda d: (d["m_l1l2"] > 100) & (d["m_l1l2"] < 150), "jet-incl, 100<m_{ee}<150"),
        "njet0": (lambda d: (d["nJet"] == 0) & MLL(d), "N_{jet} = 0"),
        "njet1": (lambda d: (d["nJet"] == 1) & MLL(d), "N_{jet} = 1"),
        "njet2_all": (lambda d: (d["passResolved"] > 0) & MLL(d), "N_{jet} #geq 2 (resolved)"),
        "njet2_mlljj_gt800": (lambda d: d["isDYCR"] > 0, "N_{jet} #geq 2, m_{lljj} > 800"),
        "dycr_mlljj_1600to2000": (lambda d: (d["isDYCR"] > 0) & (d["m_lljj"] >= 1600) & (d["m_lljj"] < 2000),
                                  "DY CR, 1600 < m_{lljj} < 2000"),
        # scenarios for the DY CR: HEEP applies no conversion veto and only missing hits <= 1, so a photon
        # conversion leg can pass. These split the CR by the conversion handles and by MET.
        "dycr_convpass": (lambda d: (d["isDYCR"] > 0) & (np.minimum(d["l1_convVeto"], d["l2_convVeto"]) == 1),
                          "DY CR, both e pass conv veto"),
        "dycr_convfail": (lambda d: (d["isDYCR"] > 0) & (np.minimum(d["l1_convVeto"], d["l2_convVeto"]) == 0),
                          "DY CR, one e fails conv veto"),
        "dycr_lh0": (lambda d: (d["isDYCR"] > 0) & (np.maximum(d["l1_lostHits"], d["l2_lostHits"]) == 0),
                     "DY CR, no lost inner hits"),
        "dycr_clean": (lambda d: (d["isDYCR"] > 0) & (np.minimum(d["l1_convVeto"], d["l2_convVeto"]) == 1)
                       & (np.maximum(d["l1_lostHits"], d["l2_lostHits"]) == 0),
                       "DY CR, conv veto + no lost hits"),
        "dycr_met_lt50": (lambda d: (d["isDYCR"] > 0) & (d["met_pt"] < 50), "DY CR, MET < 50"),
        "dycr_met_ge50": (lambda d: (d["isDYCR"] > 0) & (d["met_pt"] >= 50), "DY CR, MET #geq 50")}
VARS = [("m_l1l2", np.linspace(60, 150, 10), "SS m_{ee} (GeV)", "dilepton_mass"),
        ("l1_scEta", np.linspace(-2.5, 2.5, 11), "SS Leading Lepton #eta_{SC}", "leading_lep_eta"),
        ("l2_scEta", np.linspace(-2.5, 2.5, 11), "SS Sub-leading Lepton #eta_{SC}", "subleading_lep_eta"),
        ("l1_pt", np.array([53, 70, 100, 150, 250, 400, 1000.]), "SS Leading Lepton p_{T} (GeV)", "leading_lep_pt"),
        ("l2_pt", np.array([53, 70, 100, 150, 250, 400, 1000.]), "SS Sub-leading Lepton p_{T} (GeV)", "subleading_lep_pt"),
        ("pt_l1l2", np.array([0, 25, 50, 75, 100, 150, 200, 300, 500, 1000.]), "SS p_{T}(ee) (GeV)", "dilepton_pt"),
        ("m_lljj", np.array([800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 8000.]), "SS m_{lljj} (GeV)", "mlljj"),
        ("nJet", np.arange(-0.5, 7.5, 1.0), "SS N_{jet} (p_{T} > 40 GeV)", "njet"),
        ("met_pt", np.array([0, 20, 40, 60, 80, 100, 150, 200, 400.]), "SS PUPPI MET (GeV)", "met"),
        ("lostHits_max", np.arange(-0.5, 3.5, 1.0), "SS max lost inner hits of the two e", "lostHits"),
        ("convVeto_min", np.arange(-0.5, 2.5, 1.0), "SS conversion veto (0 = one e fails)", "convVeto"),
        ("dphi_ll", np.array([0., 1.5, 2.5, 3.0, np.pi]), "SS #Delta#phi(e,e)", "dilepton_dphi"),
        ("dphi_ll", np.linspace(0., np.pi, 13), "SS #Delta#phi(e,e)", "dilepton_dphi_fine")]
NORM = {"DYJets": 0.5, "TT": 0.3, "Nonprompt": 1.0, "Others": 0.5}
DPHI_EDGES = np.array([0., 1.5, 2.5, 3.0, np.pi])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dumps", required=True); ap.add_argument("--json", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out/Resolve/DY/chargeflip/ss_sign"))
    ap.add_argument("--sign-json", default=None, help="chargeflip_method_sign.py json: use P_final(e+)/P_final(e-) instead of the common P_final")
    ap.add_argument("--regions", default="3", choices=["3", "7"], help="3 = jetincl/mlljj_gt800/mlljj_lt800, 7 = the region-test set")
    a = ap.parse_args()
    ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0)
    J = json.load(open(a.json)); tcs = J["tc_order"]; Pfin = np.nan_to_num(np.array(J["step5"]["P_final"]))
    Pgen = np.nan_to_num(np.array(J["step1"]["P_gen"])); Egen = np.nan_to_num(np.array(J["step1"]["err"]))
    SF = np.array(J["step4"]["SF"]); eSF = np.array(J["step4"]["err"])
    PS = None
    if a.sign_json:   # charge-split P_final: P+ for the positive electron, P- for the negative one
        S = json.load(open(a.sign_json)); PS = {1: np.nan_to_num(np.array(S["P_final"]["plus"])), -1: np.nan_to_num(np.array(S["P_final"]["minus"]))}
        SFS = {1: np.array(S["SF"]["plus"]).reshape(4, 3), -1: np.array(S["SF"]["minus"]).reshape(4, 3)}; eSFS = {1: np.array(S["SF_err"]["plus"]).reshape(4, 3), -1: np.array(S["SF_err"]["minus"]).reshape(4, 3)}
    regions = REG7 if a.regions == "7" else REG
    d = dd.load(a.dumps); isdata = d["grp"] == "DATA"
    d["lostHits_max"] = np.maximum(d["l1_lostHits"], d["l2_lostHits"])
    d["convVeto_min"] = np.minimum(d["l1_convVeto"], d["l2_convVeto"])
    d["dphi_ll"] = np.arccos(np.clip((d["pt_l1l2"] ** 2 - d["l1_pt"] ** 2 - d["l2_pt"] ** 2) / (2 * d["l1_pt"] * d["l2_pt"]), -1, 1))
    itc = {i: np.array([tcs.index(int(t)) if int(t) in tcs else 0 for t in d[f"l{i}_tightCharge"]]) for i in (1, 2)}
    grp = np.array([dd.GROUP.get(g, "x") for g in d["grp"]])
    neg1 = d["l1_charge"] < 0   # in an OS pair exactly one electron is negative
    def wsign(P, Pm=None):
        """P: table for the positive electron (and the negative one when Pm is None)."""
        Pm = P if Pm is None else Pm
        P1p = P[d["l1_ipt"], d["l1_ieta"], itc[1]]; P2p = P[d["l2_ipt"], d["l2_ieta"], itc[2]]
        P1m = Pm[d["l1_ipt"], d["l1_ieta"], itc[1]]; P2m = Pm[d["l2_ipt"], d["l2_ieta"], itc[2]]
        Ppos = np.where(neg1, P2p, P1p); Pneg = np.where(neg1, P1m, P2m); D = (1 - Ppos) * (1 - Pneg) + Ppos * Pneg
        return Pneg * (1 - Ppos) / D, Ppos * (1 - Pneg) / D      # (w_pp, w_mm)
    vars_ = []
    if PS is None:
        wpp, wmm = wsign(Pfin)
        for j in range(4):
            for k in range(SF.shape[1]):
                rel = eSF[j, k] / SF[j, k] if SF[j, k] > 0 else 0.0
                Pu = Pfin.copy(); Pu[:, j, k] *= 1 + rel; Pd = Pfin.copy(); Pd[:, j, k] *= max(1 - rel, 0.0); vars_.append((wsign(Pu), wsign(Pd)))
        vars_.append((wsign(np.clip(Pgen + Egen, 0, None) * SF[None, :, :]), wsign(np.clip(Pgen - Egen, 0, None) * SF[None, :, :])))
    else:
        wpp, wmm = wsign(PS[1], PS[-1])
        for sgn in (1, -1):
            for j in range(4):
                for k in range(3):
                    rel = eSFS[sgn][j, k] / SFS[sgn][j, k] if SFS[sgn][j, k] > 0 else 0.0
                    Pu = {1: PS[1].copy(), -1: PS[-1].copy()}; Pd = {1: PS[1].copy(), -1: PS[-1].copy()}
                    Pu[sgn][:, j, k] *= 1 + rel; Pd[sgn][:, j, k] *= max(1 - rel, 0.0); vars_.append((wsign(Pu[1], Pu[-1]), wsign(Pd[1], Pd[-1])))
    n = 0; dphi_rows = []
    for rk, (rsel, rlab) in regions.items():
        sel = rsel(d)
        for sgn, tag, lab in [(1, "pp", "e^{+}e^{+}"), (-1, "mm", "e^{-}e^{-}")]:
            os_ = sel & isdata & ~d["ss"]; wf = wpp if sgn > 0 else wmm; si = 0 if sgn > 0 else 1
            ssd = sel & isdata & d["ss"] & (d["l1_charge"] == sgn)
            nf = sel & ~isdata & d["ss"] & (d["l1_charge"] == sgn) & ~(d["l1_flip"] | d["l2_flip"])
            keys = np.where(os_, "Flip", np.where(ssd, "DATA", np.where(nf, grp, "x")))
            w = np.where(os_, wf, np.where(ssd, 1.0, d["weight"])); use = keys != "x"
            L = {v: d[v][use] for v, *_ in VARS}; L["w"] = w[use]; K = keys[use]
            comps = [(g, K == g) for g in GROUPS]; dm = K == "DATA"
            outdir = os.path.join(a.out, rk, tag); os.makedirs(outdir, exist_ok=True)
            for var, edges, xl, suf in VARS:
                xf = d[var][os_]; s2 = np.zeros(len(edges) - 1)
                for (u, dn) in vars_:
                    hu, _ = np.histogram(xf, edges, weights=u[si][os_]); hd, _ = np.histogram(xf, edges, weights=dn[si][os_]); s2 += (0.5 * (hu - hd)) ** 2
                hf, _ = np.histogram(xf, edges, weights=wf[os_]); s2 += (0.05 * hf) ** 2
                for g, rel in NORM.items():
                    m = nf & (grp == g); hg, _ = np.histogram(d[var][m], edges, weights=d["weight"][m]); s2 += (rel * hg) ** 2
                cfp.draw_1d(outdir, f"SS_{tag}_{suf}", GROUPS, comps, dm, L, var, edges, xl, f"ee SS {lab}", rlab, False, syst2=s2, rmin=0.5, rmax=2.0); n += 1
            tot = sum(L["w"][K == g].sum() for g in GROUPS); print(f"{rk:12s} {lab:10s} obs {dm.sum():5d}  pred {tot:7.1f} (flip {L['w'][K=='Flip'].sum():7.1f})  obs/pred {dm.sum()/tot:.3f}")
            dphi_rows.append((rk, tag, np.histogram(L["dphi_ll"][dm], DPHI_EDGES)[0],
                              sum(np.histogram(L["dphi_ll"][K == g], DPHI_EDGES, weights=L["w"][K == g])[0] for g in GROUPS)))
    print(f"{n} plots under {a.out}")
    # obs / pred per dphi bin, one line per region x pair sign
    hdr = [f"{DPHI_EDGES[i]:.2f}-{DPHI_EDGES[i+1]:.2f}" for i in range(len(DPHI_EDGES) - 1)]
    print("\n=== obs/pred vs dphi(e,e)  [obs | pred] ===")
    print(f"{'region':20s} {'sign':>4s} | " + " | ".join(f"{h:^17s}" for h in hdr))
    md = ["| region | sign | " + " | ".join(hdr) + " |", "|" + "|".join("---" for _ in range(len(hdr) + 2)) + "|"]
    for rk, tag, o, pr in dphi_rows:
        print(f"{rk:20s} {tag:>4s} | " + " | ".join(f"{int(o[i]):4d} |{pr[i]:7.1f} {o[i]/pr[i] if pr[i] > 0 else float('nan'):5.2f}" for i in range(len(hdr))))
        md.append(f"| {rk} | {'e+e+' if tag == 'pp' else 'e-e-'} | " + " | ".join(
            (f"{int(o[i])} / {pr[i]:.1f} = **{o[i]/pr[i]:.2f}**" if pr[i] > 0 else "(none)") for i in range(len(hdr))) + " |")
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "dphi_table.md"), "w").write(
        "# SS obs / charge-flip prediction vs #Delta#phi(e,e)\n\nCells: obs / pred = **obs/pred**\n\n" + "\n".join(md) + "\n")
    print("table:", os.path.join(a.out, "dphi_table.md"))


if __name__ == "__main__":
    main()
