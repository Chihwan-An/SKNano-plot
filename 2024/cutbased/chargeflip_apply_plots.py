#!/usr/bin/env python3
"""Cutbased-style plots of the charge-flip method applied to the resolved DY CR (EE), with the datacard systematics
(12 SF-category fit errors, P_gen MC stat, 5% closure on the flip prediction; normalisation lnN on the MC non-flip):
observed SS data vs stacked [charge-flip prediction = OS data x w(P_final)] + [MC non-flip SS: WZ/ZZ, nonprompt,
DY gen-SS/unmatched, TT without a flipped electron]. Same inputs/definitions as BDT/SR/test/scripts/chargeflip_ddss.py.

  out/Resolve/DY/EE/<obj>/SS_flip/ResolveDYEE_SS_flip_<var>_plot.png   (obj = lepton / dilepton / jet_lepton / jet)
    chargeflip_apply_plots.py --dumps <RFlav tree dumps> --json <chargeflip_method json> [--out out/Resolve/DY]
"""
import argparse, glob, json, os, re, sys
import numpy as np
import ROOT
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chargeflip_plots as cfp

ETA = np.array([0.0, 0.8, 1.479, 2.0, 2.5]); PTB = np.array([53., 70., 100., 150., 250., 400., 1000.])
ETA_SIGNED = np.array([-2.5, -2.0, -1.479, -0.8, 0.0, 0.8, 1.479, 2.0, 2.5])
NETA = 4     # set from the json ("signed_eta") in main(); the SF tables and the syst loop follow it
GROUPS = {"Flip": ("kOrange", "Charge flip (OS #times w)"), "DYJets": ("kYellow", "Drell-Yan non-flip"),
          "TT": ("kRed", "T#bar{T}+tW non-flip"), "Nonprompt": ("kGreen+2", "Nonprompt"), "Others": ("kBlue", "Others (WZ/ZZ)")}
VARS = [  # (var, obj, edges, xlabel, stem suffix, logx)
    ("m_lljj", "jet_lepton", np.array([800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3800, 5000, 8000.]), "SS m_{lljj} (GeV)", "mlljj", False),
    ("l1_pt", "lepton", np.array([53, 70, 100, 150, 250, 400, 1000.]), "SS Leading Lepton p_{T} (GeV)", "leading_lep_pt", False),
    ("l2_pt", "lepton", np.array([53, 70, 100, 150, 250, 400, 1000.]), "SS Sub-leading Lepton p_{T} (GeV)", "subleading_lep_pt", False),
    ("l1_scEta", "lepton", np.linspace(-2.5, 2.5, 11), "SS Leading Lepton #eta_{SC}", "leading_lep_eta", False),
    ("l2_scEta", "lepton", np.linspace(-2.5, 2.5, 11), "SS Sub-leading Lepton #eta_{SC}", "subleading_lep_eta", False),
    ("m_l1l2", "dilepton", np.linspace(60, 150, 10), "SS Dilepton Mass (GeV)", "dilepton_mass", False),
    ("pt_l1l2", "dilepton", np.array([0, 50, 100, 150, 200, 300, 400, 600, 1000.]), "SS Dilepton p_{T} (GeV)", "dilepton_pt", False),
    ("nJet", "jet", np.arange(1.5, 8.5, 1.0), "SS Number of jets", "njet", False),
    # conversion handles (obj folder "conversion"). HEEP applies no conversion veto and only requires missing inner
    # hits <= 1, so a photon-conversion leg passes with a random charge -- these two are where that shows up.
    ("convVeto_min", "conversion", np.array([-0.5, 0.5, 1.5]), "SS conversion veto (0 = one e fails)", "convVeto", False),
    ("lostHits_max", "conversion", np.array([-0.5, 0.5, 1.5, 2.5]), "SS max lost inner hits of the two e", "lostHits", False),
    ("l1_lostHits", "conversion", np.array([-0.5, 0.5, 1.5, 2.5]), "SS Leading Lepton lost inner hits", "leading_lep_lostHits", False),
    ("l2_lostHits", "conversion", np.array([-0.5, 0.5, 1.5, 2.5]), "SS Sub-leading Lepton lost inner hits", "subleading_lep_lostHits", False),
]


def sign_mode(a, d, isdata, sel, itc):
    """e+e+ / e-e- separately with the charge-split P_final (chargeflip_method_sign.py)."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../BDT/SR/test/scripts"))
    import chargeflip_ddss as dd
    S = json.load(open(a.sign_json)); tcs = S["tc_order"]
    P = {1: np.nan_to_num(np.array(S["P_final"]["plus"])), -1: np.nan_to_num(np.array(S["P_final"]["minus"]))}
    Pg = {1: np.nan_to_num(np.array(S["P_gen"]["plus"])), -1: np.nan_to_num(np.array(S["P_gen"]["minus"]))}
    SF = {1: np.array(S["SF"]["plus"]).reshape(NETA, 3), -1: np.array(S["SF"]["minus"]).reshape(NETA, 3)}
    eSF = {1: np.array(S["SF_err"]["plus"]).reshape(NETA, 3), -1: np.array(S["SF_err"]["minus"]).reshape(NETA, 3)}
    neg1 = d["l1_charge"] < 0
    def wsign(Pp_, Pm_):
        P1p = Pp_[d["l1_ipt"], d["l1_ieta"], itc[1]]; P2p = Pp_[d["l2_ipt"], d["l2_ieta"], itc[2]]
        P1m = Pm_[d["l1_ipt"], d["l1_ieta"], itc[1]]; P2m = Pm_[d["l2_ipt"], d["l2_ieta"], itc[2]]
        Ppos = np.where(neg1, P2p, P1p); Pneg = np.where(neg1, P1m, P2m); D = (1 - Ppos) * (1 - Pneg) + Ppos * Pneg
        return {1: Pneg * (1 - Ppos) / D, -1: Ppos * (1 - Pneg) / D}
    w0 = wsign(P[1], P[-1])
    wvar = []
    for sgn in (1, -1):
        for j in range(NETA):
            for k in range(3):
                rel = eSF[sgn][j, k] / SF[sgn][j, k] if SF[sgn][j, k] > 0 else 0.0
                Pu = {1: P[1].copy(), -1: P[-1].copy()}; Pd = {1: P[1].copy(), -1: P[-1].copy()}
                Pu[sgn][:, j, k] *= 1 + rel; Pd[sgn][:, j, k] *= max(1 - rel, 0.0)
                wvar.append((wsign(Pu[1], Pu[-1]), wsign(Pd[1], Pd[-1])))
    grp = np.array([dd.GROUP.get(g, "x") for g in d["grp"]]); NORM = {"DYJets": 0.5, "TT": 0.3, "Nonprompt": 1.0, "Others": 0.5}
    n = 0
    for sgn, folder, lab in [(1, "SS_flip_pp", "e^{+}e^{+}"), (-1, "SS_flip_mm", "e^{-}e^{-}")]:
        os_ = sel & isdata & ~d["ss"]; ssd = sel & isdata & d["ss"] & (d["l1_charge"] == sgn)
        nf = sel & ~isdata & d["ss"] & (d["l1_charge"] == sgn) & ~(d["l1_flip"] | d["l2_flip"])
        keys = np.where(os_, "Flip", np.where(ssd, "DATA", np.where(nf, grp, "x"))); w = np.where(os_, w0[sgn], np.where(ssd, 1.0, d["weight"])); use = keys != "x"
        L = {v: d[v][use] for v, *_ in VARS}; L["w"] = w[use]; K = keys[use]
        comps = [(g, K == g) for g in GROUPS]; dm = K == "DATA"
        for var, obj, edges, xl, suf, logx in VARS:
            xf = d[var][os_]; s2 = np.zeros(len(edges) - 1)
            for (u, dn) in wvar:
                hu, _ = np.histogram(xf, edges, weights=u[sgn][os_]); hd, _ = np.histogram(xf, edges, weights=dn[sgn][os_]); s2 += (0.5 * (hu - hd)) ** 2
            hf, _ = np.histogram(xf, edges, weights=w0[sgn][os_]); s2 += (0.05 * hf) ** 2
            for g, rel in NORM.items():
                m = nf & (grp == g); hg, _ = np.histogram(d[var][m], edges, weights=d["weight"][m]); s2 += (rel * hg) ** 2
            outdir = os.path.join(a.out, "EE", obj, folder); os.makedirs(outdir, exist_ok=True)
            cfp.draw_1d(outdir, f"ResolveDYEE_{folder}_{suf}", GROUPS, comps, dm, L, var, edges, xl.replace("SS ", f"SS {lab} "), f"ee SS {lab}", "Resolved DY CR", logx, syst2=s2, rmin=0.5, rmax=2.0); n += 1
        tot = sum(L["w"][K == g].sum() for g in GROUPS); print(f"{folder}: obs {dm.sum()}  pred {tot:.1f} (flip {L['w'][K=='Flip'].sum():.1f})  obs/pred {dm.sum()/tot:.3f}")
    print(f"{n} plots under {a.out}/EE/*/SS_flip_pp, SS_flip_mm")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dumps", required=True); ap.add_argument("--json", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out/Resolve/DY"))
    ap.add_argument("--region", default="DYCR", choices=["DYCR", "SR"], help="SR = resolved EE SR (m_ee>400, m_lljj>800), blinded: prediction only, out/Resolve/sig")
    ap.add_argument("--tc2-only", action="store_true", help="pairs with both electrons tightCharge==2 only (use with the tc=2-only method json); folder SS_flip_tc2")
    ap.add_argument("--ymin", type=float, default=None, help="y minimum of the DY CR plots (default: draw_1d default, 0.5; 0.05 for pt)")
    ap.add_argument("--only", default=None, metavar="REGEX", help="draw only variables whose stem suffix matches (e.g. '^mlljj$')")
    ap.add_argument("--folder", default=None, help="output sub-folder name (default SS_flip / SS_flip_tc2)")
    ap.add_argument("--sign-json", default=None, help="chargeflip_method_sign.py json: use P_final(e+)/P_final(e-) and draw e+e+ / e-e- separately (folders SS_flip_pp, SS_flip_mm)")
    ap.add_argument("--mlljj-window", default=None, metavar="LO,HI", help="DY CR only: keep LO <= m_lljj < HI (m_lljj plot in 200 GeV bins); the folder gets a _mlljjLOtoHI suffix")
    ap.add_argument("--keep-tt", action="store_true", help="leave the TT+tW group untouched (all its MC SS, flipped or not) and take its flip out of the "
                                                            "data-driven part: Flip = (OS data - OS TT MC) x w; folder suffix _keepTT")
    ap.add_argument("--extra-vars", action="store_true", help="also draw fine m_ll, the pair eta_SC category (SF regions of the json), min tightCharge, dphi(l1,l2), MET, "
                                                               "jet pT, and write obs/pred per eta category x m_ll peak (76-106) / sideband to <out>/EE/<folder>_yields.md")
    a = ap.parse_args()
    ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0)
    J = json.load(open(a.json))
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../BDT/SR/test/scripts"))
    import chargeflip_ddss as dd
    NEW = dd.new_format(J)   # AN-style json (chargeflip_ptshift.py): P[eta6][pt7] x SF(barrel/endcap), 3 nuisances
    if not NEW:
        tcs = J["tc_order"]; Pfin = np.nan_to_num(np.array(J["step5"]["P_final"]))
        Pgen = np.nan_to_num(np.array(J["step1"]["P_gen"])); Egen = np.nan_to_num(np.array(J["step1"]["err"]))
        SF = np.array(J["step4"]["SF"]); eSF = np.array(J["step4"]["err"])
    # load (same grouping as chargeflip_ddss)
    d = dd.load(a.dumps); isdata = d["grp"] == "DATA"
    SR = a.region == "SR"
    sel = ((d["passResolved"] > 0) & (d["m_l1l2"] > 400) & (d["m_lljj"] > 800)) if SR else (d["isDYCR"] > 0)
    if SR:
        a.out = a.out.replace("out/Resolve/DY", "out/Resolve/sig")
        for k, v in enumerate(VARS):
            if v[0] == "m_l1l2": VARS[k] = ("m_l1l2", "dilepton", np.array([400, 500, 600, 800, 1000, 1500, 2000, 3000.]), "SS Dilepton Mass (GeV)", "dilepton_mass", False)
            if v[0] == "m_lljj": VARS[k] = ("m_lljj", "jet_lepton", np.array([800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 3561, 4643, 5533, 8000.]), "SS m_{lljj} (GeV)", "mlljj", False)
    # pair-level conversion handles: the veto fails if EITHER leg fails, lost hits taken as the worse of the two
    d["convVeto_min"] = np.minimum(d["l1_convVeto"], d["l2_convVeto"])
    d["lostHits_max"] = np.maximum(d["l1_lostHits"], d["l2_lostHits"])
    d["dphi_l1l2"] = np.abs((d["l1_phi"] - d["l2_phi"] + np.pi) % (2 * np.pi) - np.pi)
    d["tc_min"] = np.minimum(d["l1_tightCharge"], d["l2_tightCharge"])
    # pair eta_SC category from the SF regions of the json (SF3: inner barrel / outer barrel / endcap, else barrel / endcap);
    # -1 = at least one electron outside every region (crack), which gets P = 0 in the flip weight
    sfreg = list(J["sf"]["SF3"]["regions"].items()) if NEW and "SF3" in J["sf"] else [("barrel", (0.0, 1.4442)), ("endcap", (1.566, 2.5))]
    def ireg(eta):
        r = np.full(len(eta), -1); ae = np.abs(eta)
        for k, (_, (lo, hi)) in enumerate(sfreg): r[(ae >= lo) & (ae < hi)] = k
        return r
    r1, r2 = ireg(d["l1_scEta"]), ireg(d["l2_scEta"])
    PAIRS = [(i, j) for i in range(len(sfreg)) for j in range(i, len(sfreg))]
    CATLAB = ["crack"] + [f"{sfreg[i][0]}-{sfreg[j][0]}" for i, j in PAIRS]
    d["eta_cat"] = np.full(len(r1), -1.0)
    for k, (i, j) in enumerate(PAIRS): d["eta_cat"][(np.minimum(r1, r2) == i) & (np.maximum(r1, r2) == j) & (r1 >= 0) & (r2 >= 0)] = k
    if a.extra_vars:
        print("eta_cat: " + ", ".join(f"{k - 1} = {n}" for k, n in enumerate(CATLAB)))
        jpt = np.array([0, 100, 200, 300, 400, 600, 800, 1000, 1500.])
        VARS.extend([
            ("m_l1l2", "dilepton", np.arange(60, 151, 3.0), "SS Dilepton Mass (GeV)", "dilepton_mass_fine", False),
            ("eta_cat", "lepton", np.arange(-1.5, len(PAIRS) + 0.5, 1.0), " ".join(f"{k - 1}:{n}" for k, n in enumerate(CATLAB[1:], 1)).replace("inner_barrel", "IB").replace("outer_barrel", "OB").replace("endcap", "E"), "eta_category", False),
            ("tc_min", "lepton", np.array([-0.5, 0.5, 1.5, 2.5]), "SS min tightCharge of the two e", "tightCharge_min", False),
            ("dphi_l1l2", "dilepton", np.linspace(0, np.pi, 11), "SS #Delta#phi(l_{1},l_{2})", "dilepton_dphi", False),
            ("met_pt", "event", np.array([0, 20, 40, 60, 80, 100, 150, 200, 300.]), "SS p_{T}^{miss} (GeV)", "met", False),
            ("j1_pt", "jet", jpt, "SS Leading jet p_{T} (GeV)", "leading_jet_pt", False),
            ("j2_pt", "jet", jpt, "SS Sub-leading jet p_{T} (GeV)", "subleading_jet_pt", False)])
    # The eta binning is whatever the json was fitted with. chargeflip_ddss.load() always builds |eta| indices, so
    # redo them here when the json is a signed-eta fit -- otherwise P_final would be looked up in the wrong bins.
    global NETA
    Jsigned = bool(J.get("signed_eta", False)) or (a.sign_json and bool(json.load(open(a.sign_json)).get("signed_eta", False)))
    if Jsigned:
        edges = ETA_SIGNED; NETA = len(edges) - 1
        for i in (1, 2):
            d[f"l{i}_ieta"] = np.clip(np.searchsorted(edges, d[f"l{i}_scEta"], side="right") - 1, 0, NETA - 1)
    print(f"eta binning: {'signed' if Jsigned else '|eta|'} ({NETA} bins)")
    if a.tc2_only: sel = sel & (d["l1_tightCharge"] == 2) & (d["l2_tightCharge"] == 2)
    folder = a.folder or ("SS_flip_tc2" if a.tc2_only else "SS_flip")
    wtxt = ""
    if a.mlljj_window and not SR:
        wlo, whi = [float(x) for x in a.mlljj_window.split(",")]
        sel = sel & (d["m_lljj"] >= wlo) & (d["m_lljj"] < whi); folder += f"_mlljj{wlo:.0f}to{whi:.0f}"; wtxt = f", {wlo:.0f}-{whi:.0f} GeV"
        for k, v in enumerate(VARS):
            if v[0] == "m_lljj": VARS[k] = ("m_lljj", "jet_lepton", np.arange(wlo, whi + 1, 200.0), "SS m_{lljj} (GeV)", "mlljj", False)
    os_ = sel & isdata & ~d["ss"]
    if NEW:
        wflip, var_all = dd.new_weights(J, d); wvar = [(wu, wd) for _, wu, wd in var_all]
    else:
        itc = {i: np.array([tcs.index(int(t)) if int(t) in tcs else 0 for t in d[f"l{i}_tightCharge"]]) for i in (1, 2)}
        def wof(P): return dd.flip_weight(P[d["l1_ipt"], d["l1_ieta"], itc[1]], P[d["l2_ipt"], d["l2_ieta"], itc[2]])
        wflip = wof(Pfin)
        if a.sign_json:
            return sign_mode(a, d, isdata, sel, itc)
        # systematic variations of the flip weight (same set as the datacard, chargeflip_ddss.py):
        # 12 (|eta|,tc) SF fit errors (independent), P_MC,gen MC-stat (coherent), closure 5% (lnN)
        wvar = []
        for j in range(NETA):
            for k in range(SF.shape[1]):
                rel = eSF[j, k] / SF[j, k] if SF[j, k] > 0 else 0.0
                Pu = Pfin.copy(); Pu[:, j, k] *= 1 + rel; Pd = Pfin.copy(); Pd[:, j, k] *= max(1 - rel, 0.0)
                wvar.append((wof(Pu), wof(Pd)))
        wvar.append((wof(np.clip(Pgen + Egen, 0, None) * SF[None, :, :]), wof(np.clip(Pgen - Egen, 0, None) * SF[None, :, :])))
    NORM = {"DYJets": 0.5, "TT": 0.3, "Nonprompt": 1.0, "Others": 0.5}   # non-flip MC normalisation lnN of the card
    nonflip = sel & ~isdata & d["ss"] & ~(d["l1_flip"] | d["l2_flip"])
    grp_all = np.array([dd.GROUP.get(g, "x") for g in d["grp"]])
    if a.keep_tt:   # TT group = its full MC SS; its flips leave the data-driven part: Flip = OS data x w - OS TT MC x w
        nonflip = nonflip | (sel & ~isdata & d["ss"] & (grp_all == "TT"))
        folder += "_keepTT"; GROUPS["TT"] = ("kRed", "T#bar{T}+tW (MC SS, untouched)"); GROUPS["Flip"] = ("kOrange", "Charge flip (TT MC subtracted)")   # 긴 라벨은 범례 상자를 넘어간다
    ssdata = sel & isdata & d["ss"] & (not SR)   # SR: blinded, no data
    os_tt = sel & ~isdata & ~d["ss"] & (grp_all == "TT") & a.keep_tt
    # one concatenated table: component key + weight
    keys = np.where(os_ | os_tt, "Flip", np.where(ssdata, "DATA", np.where(nonflip, grp_all, "x")))
    w = np.where(os_, wflip, np.where(os_tt, -wflip * d["weight"], np.where(ssdata, 1.0, d["weight"])))
    use = keys != "x"
    L = {v: d[v][use] for v, *_ in VARS}; L["w"] = w[use]; K = keys[use]
    comps = [(g, K == g) for g in GROUPS]; data_mask = K == "DATA"
    label1 = ("ee SS, both tc=2" if a.tc2_only else "ee SS") + wtxt.replace(" GeV", ""); label2 = "Resolved SR (blinded)" if SR else "Resolved DY CR"
    if a.extra_vars and not SR:
        grpname = np.array([dd.GROUP.get(x, "x") for x in d["grp"]]); nf = nonflip & (grpname != "x")
        peak = (d["m_l1l2"] > 76) & (d["m_l1l2"] < 106)
        rows = ["| pair eta_SC | m_ll | obs SS | pred | flip | non-flip MC | (nonprompt) | obs/pred |", "|---|---|---|---|---|---|---|---|"]
        for k, n in enumerate(CATLAB):
            for mlab, mm in [("76-106", peak), ("60-76, 106-150", ~peak), ("all", np.ones(len(peak), bool))]:
                c = (d["eta_cat"] == k - 1) & mm
                ob = int((ssdata & c).sum()); fl = wflip[os_ & c].sum(); mc = d["weight"][nf & c].sum(); npr = d["weight"][nf & c & (grpname == "Nonprompt")].sum(); pr = fl + mc
                rows.append(f"| {n} | {mlab} | {ob} | {pr:.1f} | {fl:.1f} | {mc:.1f} | {npr:.1f} | {ob / pr if pr > 0 else float('nan'):.2f} |")
        md = os.path.join(a.out, "EE", f"{folder}_yields.md"); os.makedirs(os.path.dirname(md), exist_ok=True)
        open(md, "w").write(f"# DY CR EE SS: observed vs predicted per pair eta_SC category\n\njson {os.path.basename(a.json)}{wtxt}\n\n" + "\n".join(rows) + "\n")
        print("\n".join(rows)); print("wrote", md)
    n = 0
    def syst2_of(var, edges):
        xf = d[var][os_]; s2 = np.zeros(len(edges) - 1)
        for wu, wd in wvar:
            hu, _ = np.histogram(xf, edges, weights=wu[os_]); hd, _ = np.histogram(xf, edges, weights=wd[os_]); s2 += (0.5 * (hu - hd)) ** 2
        hf, _ = np.histogram(xf, edges, weights=wflip[os_]); s2 += (0.05 * hf) ** 2
        if a.keep_tt:   # the subtracted OS TT x w carries the TT normalisation uncertainty
            ht, _ = np.histogram(d[var][os_tt], edges, weights=(wflip * d["weight"])[os_tt]); s2 += (NORM["TT"] * ht) ** 2
        for g, rel in NORM.items():
            m = nonflip & (grp_all == g)
            hg, _ = np.histogram(d[var][m], edges, weights=d["weight"][m]); s2 += (rel * hg) ** 2
        return s2
    for var, obj, edges, xl, suf, logx in VARS:
        if a.only and not re.search(a.only, suf): continue
        outdir = os.path.join(a.out, "EE", obj, folder); os.makedirs(outdir, exist_ok=True)
        cfp.draw_1d(outdir, f"{'ResolveSREE' if SR else 'ResolveDYEE'}_{folder}_{suf}", GROUPS, comps, data_mask, L, var, edges, xl, label1, label2, logx,
                    syst2=syst2_of(var, edges), blind=SR, ymin=0.01 if SR else a.ymin); n += 1
    tot = sum(L["w"][K == g].sum() for g in GROUPS); obs = data_mask.sum()
    print(f"{n} plots under {a.out}/EE/*/{folder} ; {a.region} SS: obs {obs if not SR else 'blinded'}  pred {tot:.1f} (flip {L['w'][K=='Flip'].sum():.1f})" + (f" obs/pred {obs / tot:.3f}" if not SR else ""))


if __name__ == "__main__":
    main()
