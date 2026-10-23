#!/usr/bin/env python3
"""Step 6: signal-inclusive Asimov fit prototype for resolved SS mumu (MC only).

Channels  SS_{TT,TL,LT,LL}_{Low,High}: iso category x non-overlapping mlljj window
          (Low 800-1600, High >=1600), all inside the SR, each event used once.
Processes sig (every channel, common r), prompt (truth PP), undet (a U muon, no F),
          np_PF / np_FP / np_FF (truth nonprompt, by which leg is fake).
Nonprompt response (per window w, per leg):
    fake leg   T: K_w            L: (1 - K_w fbar)/(1 - fbar)
    prompt leg T: lam            L: (1 - lam ebar)/(1 - ebar)
    K_Low = k_Low (param, calibration prior), K_High = k_Low * tau (tau: low->high transfer prior)
    and a free normalisation N_w per window (rateParam) shared by all nonprompt classes.
The formulas conserve the FO count of each leg, so N_w is the nonprompt FO yield scale and
the fail categories (TL/LT/LL) of the same window constrain it; they are fit channels only,
never also used to build a fixed template.
Prompt: lnN + lam response.  Signal: lnN; its L categories are prompt non-isolated muons,
          given a separate lnN (no lam response - see the memo).
data_obs  = Asimov: sum of the MC expectations (+ inj * signal), optionally with a
          mis-modelled High fake rate (--data-kHigh) to test the transfer prior.
"""
import argparse
import json
import os

import numpy as np
import ROOT

import folib as L

WIN_EDGES = {"Low": np.array([800, 1000, 1200, 1400, 1600], float),
             "High": np.array([1600, 2000, 2400, 2800, 8000], float)}
CLASSES = {"np_PF": ("P", "F"), "np_FP": ("F", "P"), "np_FF": ("F", "F")}


def leg_state(cat, leg):
    return cat[leg]  # "T" or "L"; cat string is lead+sub, e.g. "TL"


def histo(name, x, w, edges):
    h = ROOT.TH1D(name, name, len(edges) - 1, edges)
    h.Sumw2()
    x = np.minimum(np.asarray(x, float), edges[-1] - 1e-3)
    for xi, wi in zip(x, np.asarray(w, float)):
        h.Fill(xi, wi)
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--signal", required=True, help="e.g. MWR4000_N200")
    ap.add_argument("--out", required=True)
    ap.add_argument("--inj", type=float, default=0.0, help="signal strength in the Asimov data")
    ap.add_argument("--data-kHigh", type=float, default=1.0, help="true K_High used to build the Asimov data")
    ap.add_argument("--sigma-kLow", type=float, default=None, help="calibration prior (default from 04c json)")
    ap.add_argument("--sigma-tau", type=float, default=None, help="transfer prior (default from 04c json)")
    ap.add_argument("--sigma-lam", type=float, default=0.02)
    ap.add_argument("--qcd", action="store_true", help="include QCD MC in the background")
    ap.add_argument("--skim", default=L.SKIM)
    a = ap.parse_args()

    d, _ = L.load(a.skim)
    build(d, a)


def build(d, a):
    isq = np.array([p.startswith("QCD") for p in d["proc"]])
    bkg = ~d["isSig"] & (~isq if not a.qcd else np.ones_like(isq))
    hasF = (d["t1"] == "F") | (d["t2"] == "F")
    hasU = ((d["t1"] == "U") | (d["t2"] == "U")) & ~hasF
    pp = (d["t1"] == "P") & (d["t2"] == "P")

    # priors from the closure study unless given
    clo = json.load(open(os.path.join(L.RESULTS, "04c_closure.json")))
    key = "High|QCD" if a.qcd else "High|noQCD"
    r = clo[key]["FF, AR truth-F only"]
    tgt = np.sum(clo[key]["target"])
    nonclosure = abs(r["tot"] / tgt - 1) if tgt > 0 else 1.0
    stat = np.hypot(r["tot_err_mc"], np.sqrt(np.sum(clo[key]["target_err2"]))) / tgt if tgt > 0 else 1.0
    sigma_tau = a.sigma_tau if a.sigma_tau is not None else float(np.hypot(nonclosure, stat))
    lowkey = "Low|QCD" if a.qcd else "Low|noQCD"
    rl = clo[lowkey]["FF, AR truth-F only"]
    sigma_kLow = a.sigma_kLow if a.sigma_kLow is not None else float(rl["tot_err_map"] / rl["tot"]) if rl["tot"] else 0.3

    os.makedirs(a.out, exist_ok=True)
    fout = ROOT.TFile(os.path.join(a.out, "shapes.root"), "RECREATE")
    info = {"signal": a.signal, "inj": a.inj, "data_kHigh": a.data_kHigh, "sigma_kLow": sigma_kLow,
            "sigma_tau": sigma_tau, "sigma_lam": a.sigma_lam, "qcd": a.qcd, "fbar": {}, "ebar": {},
            "fixed_negative_bins": [], "yields": {}}
    procs = ["sig", "prompt", "undet", "np_PF", "np_FP", "np_FF"]
    channels = []
    for win, edges in WIN_EDGES.items():
        reg = L.sel(d, "SS", win)
        # effective rates in this window (FO-level, all iso categories pooled)
        num = den = 0.0
        for leg in (1, 2):
            m = reg & bkg & (d[f"t{leg}"] == "F")
            num += d["weight"][m & (d[f"mu{leg}_tkRelIso"] < L.TIGHT_ISO)].sum(); den += d["weight"][m].sum()
        pooled = num / den if den > 0 else float("nan")
        info["fbar_pooled_" + win] = pooled
        for cls, (t1, t2) in CLASSES.items():
            m = reg & bkg & (d["t1"] == t1) & (d["t2"] == t2)
            for leg, tt in ((1, t1), (2, t2)):
                if tt != "F":
                    continue
                tight = d[f"mu{leg}_tkRelIso"] < L.TIGHT_ISO
                den = d["weight"][m].sum()
                fb = d["weight"][m & tight].sum() / den if den > 0 else float("nan")
                if not (0 <= fb < 1):
                    info.setdefault("fbar_fallback", []).append(f"{win}|{cls}|{leg}: {fb} -> pooled {pooled}")
                    fb = pooled
                info["fbar"][f"{win}|{cls}|{leg}"] = float(fb)
        pm = []
        for leg in (1, 2):
            m = reg & bkg & (d[f"t{leg}"] == "P")
            pm.append((d["weight"][m & (d[f"mu{leg}_tkRelIso"] < L.TIGHT_ISO)].sum(), d["weight"][m].sum()))
        info["ebar"][win] = float(sum(x[0] for x in pm) / sum(x[1] for x in pm))
        for cat in L.CATS:
            ch = f"SS_{cat}_{win}"
            channels.append(ch)
            dd = fout.mkdir(ch)
            dd.cd()
            mc = reg & (d["cat"] == cat)
            masks = {"sig": mc & (d["proc"] == "SIG_" + a.signal), "prompt": mc & bkg & pp,
                     "undet": mc & bkg & hasU}
            for cls, (t1, t2) in CLASSES.items():
                masks[cls] = mc & bkg & (d["t1"] == t1) & (d["t2"] == t2)
            data = None
            for p in procs:
                h = histo(p, d["mlljj"][masks[p]], d["weight"][masks[p]], edges)
                info["yields"][f"{ch}|{p}"] = h.Integral()
                # data (Asimov) before protecting bins: optional mis-modelled K_High
                hd = h.Clone(p + "_data")
                if p.startswith("np_") and win == "High" and a.data_kHigh != 1.0:
                    s = 1.0
                    for leg, tt in ((0, CLASSES[p][0]), (1, CLASSES[p][1])):
                        if tt == "F":
                            fb = info["fbar"][f"High|{p}|{leg + 1}"]
                            s *= a.data_kHigh if cat[leg] == "T" else (1 - a.data_kHigh * fb) / (1 - fb)
                    hd.Scale(s)
                if p == "sig":
                    hd.Scale(a.inj)
                if data is None:
                    data = hd
                else:
                    data.Add(hd)
                for b in range(1, h.GetNbinsX() + 1):
                    if h.GetBinContent(b) <= 0:
                        info["fixed_negative_bins"].append([ch, p, b, h.GetBinContent(b)])
                        h.SetBinContent(b, 1e-6)
                        h.SetBinError(b, max(h.GetBinError(b), 1e-6))
                h.Write(p)
            for b in range(1, data.GetNbinsX() + 1):
                data.SetBinContent(b, max(data.GetBinContent(b), 0.0))
            data.Write("data_obs")
    fout.Close()

    # ------------------------------------------------------------ card
    lines = [f"# Asimov prototype, signal {a.signal}, inj {a.inj}, data K_High {a.data_kHigh}",
             "imax *", "jmax *", "kmax *", "-" * 40,
             "shapes * * shapes.root $CHANNEL/$PROCESS", "-" * 40,
             "bin " + " ".join(channels), "observation " + " ".join(["-1"] * len(channels)), "-" * 40]
    colb, colp, colr = [], [], []
    for ch in channels:
        for p in procs:
            colb.append(ch); colp.append(p); colr.append("-1")
    coli = [str(procs.index(p)) for p in colp]  # sig = 0 (signal), others > 0
    lines += ["bin " + " ".join(colb), "process " + " ".join(colp), "process " + " ".join(coli),
              "rate " + " ".join(colr), "-" * 40]

    def lnN(name, val, sel):
        lines.append(f"{name} lnN " + " ".join(val if sel(c, p) else "-" for c, p in zip(colb, colp)))

    lnN("lumi", "1.014", lambda c, p: p in ("sig", "prompt", "undet"))
    lnN("prompt_norm", "1.10", lambda c, p: p == "prompt")
    lnN("undet_norm", "1.50", lambda c, p: p == "undet")
    lnN("sig_iso_L", "1.05", lambda c, p: p == "sig" and "_TT_" not in c)
    lines.append(f"k_Low param 1.0 {sigma_kLow:.4f}")
    lines.append(f"tau param 1.0 {sigma_tau:.4f}")
    lines.append(f"lam param 1.0 {a.sigma_lam:.4f}")
    # free window normalisation
    for win in WIN_EDGES:
        lines.append(f"N_{win} rateParam SS_*_{win} np_* 1 [0,20]")
    # response formulas per (channel, process)
    for ch in channels:
        _, cat, win = ch.split("_")
        eb = info["ebar"][win]
        for p in ("prompt", "np_PF", "np_FP", "np_FF"):
            legs = ("P", "P") if p == "prompt" else CLASSES[p]
            terms, args = [], []
            for leg, tt in enumerate(legs):
                st = cat[leg]
                if tt == "P":
                    if "lam" not in args:
                        args.append("lam")
                    ia = args.index("lam")
                    if st == "T":
                        terms.append(f"@{ia}")
                    elif 1 - eb > 1e-4:
                        terms.append(f"((1-@{ia}*{eb:.6f})/(1-{eb:.6f}))")
                    else:  # no prompt L content in this window: factor undefined, template ~0
                        info.setdefault("degenerate_L_factor", []).append(f"{ch}|{p}|prompt leg {leg + 1}")
                else:
                    fb = info["fbar"][f"{win}|{p}|{leg + 1}"]
                    if "k_Low" not in args:
                        args.append("k_Low")
                    ik = args.index("k_Low")
                    if win == "High" and "tau" not in args:
                        args.append("tau")
                    K = f"@{ik}" if win == "Low" else f"(@{ik}*@{args.index('tau')})"
                    if st == "T":
                        terms.append(K)
                    elif 1 - fb > 1e-4:
                        terms.append(f"((1-{K}*{fb:.6f})/(1-{fb:.6f}))")
                    else:
                        info.setdefault("degenerate_L_factor", []).append(f"{ch}|{p}|fake leg {leg + 1}")
            if not terms:
                continue
            used = sorted({int(t) for t in __import__("re").findall(r"@(\d+)", "*".join(terms))})
            if used != list(range(len(args))):  # drop args no remaining term refers to
                remap = {o: n for n, o in enumerate(used)}
                terms = [__import__("re").sub(r"@(\d+)", lambda mm: f"@{remap[int(mm.group(1))]}", t) for t in terms]
                args = [args[o] for o in used]
            lines.append(f"resp_{ch}_{p} rateParam {ch} {p} ({'*'.join(terms)}) {','.join(args)}")
    lines.append("* autoMCStats 10")
    open(os.path.join(a.out, "card.txt"), "w").write("\n".join(lines) + "\n")
    json.dump(info, open(os.path.join(a.out, "info.json"), "w"), indent=1, default=float)
    print(f"[cards] {a.out}: sigma_kLow {sigma_kLow:.3f} sigma_tau {sigma_tau:.3f}; "
          f"{len(info['fixed_negative_bins'])} non-positive template bins set to 1e-6")


def parser():
    ap = argparse.ArgumentParser()
    return ap


if __name__ == "__main__":
    main()
