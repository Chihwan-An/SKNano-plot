#!/usr/bin/env python3
"""Build every Asimov card set of step 6 with one data load (MC only).
Configs per signal:
  bkg      : Asimov = background only (inj 0)
  inj1     : Asimov = background + 1 x signal
  misHigh  : inj 1, and the Asimov High-window nonprompt built with K_High = 1.3 (true transfer 30% off)
  fixed    : comparison 'fixed template' model -- iso-TT channels only, nonprompt = FF prediction from
             the fail categories of the SAME Asimov (bkg + inj x signal, so signal leaks in), lnN prior
"""
import argparse
import os
import types

import numpy as np
import ROOT

import folib as L
import fo_analysis as A
import make_asimov_cards as M

CONFIGS = {"bkg": dict(inj=0.0, data_kHigh=1.0), "inj1": dict(inj=1.0, data_kHigh=1.0),
           "misHigh": dict(inj=1.0, data_kHigh=1.3)}


def fixed_template_cards(d, sig, out, inj, sigma):
    """TT-only model with the nonprompt template taken from the fail categories (FF, SS-Low MC map)."""
    fmap = A.maps(d)["F_lowSS"]
    isq = np.array([p.startswith("QCD") for p in d["proc"]])
    bkg = ~d["isSig"] & ~isq
    hasF = (d["t1"] == "F") | (d["t2"] == "F")
    hasU = ((d["t1"] == "U") | (d["t2"] == "U")) & ~hasF
    pp = (d["t1"] == "P") & (d["t2"] == "P")
    os.makedirs(out, exist_ok=True)
    f = ROOT.TFile(os.path.join(out, "shapes.root"), "RECREATE")
    chans = []
    for win, edges in M.WIN_EDGES.items():
        reg = L.sel(d, "SS", win)
        ch = f"SS_TT_{win}"; chans.append(ch)
        dd = f.mkdir(ch); dd.cd()
        tt = reg & (d["cat"] == "TT")
        hs = M.histo("sig", d["mlljj"][tt & (d["proc"] == "SIG_" + sig)], d["weight"][tt & (d["proc"] == "SIG_" + sig)], edges)
        hp = M.histo("prompt", d["mlljj"][tt & bkg & pp], d["weight"][tt & bkg & pp], edges)
        hu = M.histo("undet", d["mlljj"][tt & bkg & hasU], d["weight"][tt & bkg & hasU], edges)
        hn_true = M.histo("np_true", d["mlljj"][tt & bkg & hasF], d["weight"][tt & bkg & hasF], edges)
        # template from the Asimov AR: background AR (all - PP, prompt-subtracted) + inj x signal AR
        ar = reg & np.isin(d["cat"], ["TL", "LT", "LL"])
        mb = ar & bkg & ~pp
        ms = ar & (d["proc"] == "SIG_" + sig)
        hnp = M.histo("np", np.concatenate([d["mlljj"][mb], d["mlljj"][ms]]),
                      np.concatenate([np.nan_to_num(L.ff_prediction(d, mb, fmap)),
                                      inj * np.nan_to_num(L.ff_prediction(d, ms, fmap))]), edges)
        data = hs.Clone("data_obs"); data.Scale(inj); data.Add(hp); data.Add(hu); data.Add(hn_true)
        for h in (hs, hp, hu, hnp):
            for b in range(1, h.GetNbinsX() + 1):
                if h.GetBinContent(b) <= 0:
                    h.SetBinContent(b, 1e-6)
            h.Write(h.GetName())
        data.Write("data_obs")
    f.Close()
    procs = ["sig", "prompt", "undet", "np"]
    colb = [c for c in chans for _ in procs]; colp = procs * len(chans)
    lines = ["imax *", "jmax *", "kmax *", "-" * 30, "shapes * * shapes.root $CHANNEL/$PROCESS", "-" * 30,
             "bin " + " ".join(chans), "observation " + " ".join(["-1"] * len(chans)), "-" * 30,
             "bin " + " ".join(colb), "process " + " ".join(colp),
             "process " + " ".join(str(procs.index(p)) for p in colp), "rate " + " ".join(["-1"] * len(colb)), "-" * 30,
             "lumi lnN " + " ".join("1.014" if p in ("sig", "prompt", "undet") else "-" for p in colp),
             "prompt_norm lnN " + " ".join("1.10" if p == "prompt" else "-" for p in colp),
             "undet_norm lnN " + " ".join("1.50" if p == "undet" else "-" for p in colp),
             f"np_fixed lnN " + " ".join(f"{1 + sigma:.3f}" if p == "np" else "-" for p in colp),
             "* autoMCStats 10"]
    open(os.path.join(out, "card.txt"), "w").write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--signals", default=",".join(L.SIGNALS6))
    ap.add_argument("--outbase", default=os.path.join(L.STUDY, "fit"))
    ap.add_argument("--qcd", action="store_true")
    a = ap.parse_args()
    d, _ = L.load(L.SKIM)
    for sig in a.signals.split(","):
        for cname, cfg in CONFIGS.items():
            ns = types.SimpleNamespace(signal=sig, out=os.path.join(a.outbase, f"{sig}_{cname}{'_QCD' if a.qcd else ''}"),
                                       inj=cfg["inj"], data_kHigh=cfg["data_kHigh"], sigma_kLow=None, sigma_tau=None,
                                       sigma_lam=0.02, qcd=a.qcd, skim=L.SKIM)
            M.build(d, ns)
        if a.qcd:
            print("[fit_driver] cards (QCD) for", sig)
            continue
        info = __import__("json").load(open(os.path.join(a.outbase, f"{sig}_bkg", "info.json")))
        sig_np = float(np.hypot(info["sigma_kLow"], info["sigma_tau"]))
        for inj in (0.0, 1.0):
            fixed_template_cards(d, sig, os.path.join(a.outbase, f"{sig}_fixed_inj{int(inj)}"), inj, sig_np)
        print("[fit_driver] cards for", sig)


if __name__ == "__main__":
    main()
