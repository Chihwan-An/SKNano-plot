#!/usr/bin/env python3
"""Plots for the resolved SS mumu nonprompt study (MC only). Reads results/*.json,
writes png+pdf to plot/cutbased/out/nonprompt_ssmm/<topic>/.

  plot_results.py [--only composition,coverage,fakerate,closure,signal,fit]
"""
import argparse
import glob
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import mplhep as hep  # noqa: E402
import numpy as np  # noqa: E402

import folib as L  # noqa: E402

hep.style.use("CMS")
LABEL = dict(label="Preliminary", data=False, lumi=None, com=13.6, year="2024", fontsize=18)
PROC_COL = {"TTLJ": "#e76300", "TTLL": "#f89c20", "tW": "#ffd166", "ST s/t": "#b9ac70", "ttV": "#a96b59",
            "DY": "#5790fc", "W+jets(MLNu)": "#86c8dd", "W+jets(HT)": "#86c8dd", "VV": "#964a8b", "VVV": "#9c9ca1",
            "QCD_MuEnriched": "#7a21dd", "QCD_EMEnriched": "#c849a9", "QCD_bcToE": "#e42536"}
PAIR_COL = {"PP": "#5790fc", "PF": "#e42536", "FP": "#f89c20", "FF": "#964a8b", "PU": "#b9d7f0", "UP": "#8fb8de",
            "FU": "#e8a0a0", "UF": "#f5c98a", "UU": "#707070"}
ORIGIN_COL = {"b direct": "#e42536", "b->c cascade": "#f89c20", "c (no b)": "#ffd166", "nonprompt tau": "#964a8b",
              "light/other": "#9c9ca1", "no gen mu": "#5790fc", "chain inconclusive": "#86c8dd"}


def save(fig, topic, name):
    d = os.path.join(L.PLOTS, topic)
    os.makedirs(d, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(d, f"{name}.{ext}"), bbox_inches="tight")
    plt.close(fig)


def load(name):
    p = os.path.join(L.RESULTS, name + ".json")
    return json.load(open(p)) if os.path.exists(p) else None


def composition():
    J = load("03_composition")
    if not J:
        return
    procs = [p for p in L.PROCS_ORDER if any(k.split("|")[2] == p for k in J)]
    for ch in ("SS", "OS"):
        for win in ("Full", "Low", "High"):
            # 1) process stack per iso category
            fig, ax = plt.subplots(figsize=(10, 8))
            bottom = np.zeros(4)
            for p in procs:
                v = np.array([J.get(f"{ch}|{win}|{p}|{c}", [0, 0, 0])[0] for c in L.CATS])
                ax.bar(range(4), v, bottom=bottom, color=PROC_COL.get(p, "grey"), label=p, edgecolor="k", lw=0.3)
                bottom += v
            ax.set_xticks(range(4), [f"iso-{c}" for c in L.CATS])
            ax.set_ylabel("Expected events (MC, signed sumw)")
            ax.set_yscale("log"); ax.set_ylim(max(1e-2, bottom[bottom > 0].min() / 20 if (bottom > 0).any() else 1e-2), bottom.max() * 30)
            ax.legend(ncol=2, fontsize=13, loc="upper right")
            ax.set_title(f"{ch} $\\mu\\mu$, {win}, $m_{{\\mu\\mu}}>400$", fontsize=16, loc="left", pad=34)
            hep.cms.label(ax=ax, **LABEL)
            save(fig, "composition", f"process_{ch}_{win}")
            # 2) truth pair fractions, bkg noQCD and +QCD
            for tag, key in (("noQCD", "pair"), ("withQCD", "pairQ")):
                pairs = sorted({k.split("|")[3] for k in J if k.startswith(f"{ch}|{win}|{key}|")})
                if not pairs:
                    continue
                fig, ax = plt.subplots(figsize=(10, 8))
                tot = np.zeros(4)
                vals = {}
                for pr in pairs:
                    vals[pr] = np.array([J.get(f"{ch}|{win}|{key}|{pr}|{c}", [0])[0] for c in L.CATS])
                    tot += vals[pr]
                bottom = np.zeros(4)
                for pr in pairs:
                    f = np.divide(vals[pr], tot, out=np.zeros(4), where=tot != 0)
                    ax.bar(range(4), f, bottom=bottom, color=PAIR_COL.get(pr, "#cccccc"), label=pr, edgecolor="k", lw=0.3)
                    bottom += f
                ax.set_xticks(range(4), [f"iso-{c}" for c in L.CATS]); ax.set_ylim(0, 1.25)
                ax.set_ylabel("Fraction of background (truth lead,sub)")
                ax.legend(ncol=4, fontsize=13, loc="upper center")
                ax.set_title(f"{ch} {win}, bkg {tag}; P prompt F nonprompt U undetermined", fontsize=14, loc="left", pad=34)
                hep.cms.label(ax=ax, **LABEL)
                save(fig, "composition", f"truthpair_{ch}_{win}_{tag}")
            # 3) origin of nonprompt / undetermined muons
            fig, ax = plt.subplots(figsize=(11, 8))
            names = list(ORIGIN_COL)
            bottom = np.zeros(8)
            xl = [f"{c}\n{t}" for c in L.CATS for t in ("T", "L")]
            for o in names:
                v = []
                for c in L.CATS:
                    org = J.get(f"{ch}|{win}|origin|{c}", {})
                    v += [org.get(f"{o}|T", 0), org.get(f"{o}|L", 0)]
                v = np.array(v)
                ax.bar(range(8), v, bottom=bottom, color=ORIGIN_COL[o], label=o, edgecolor="k", lw=0.3)
                bottom += v
            ax.set_xticks(range(8), xl, fontsize=13)
            ax.set_ylabel("Non-prompt / undetermined muons (sumw)")
            ax.legend(fontsize=12, ncol=2)
            ax.set_title(f"{ch} {win}: origin of non-prompt muons by iso category and muon T/L", fontsize=13, loc="left", pad=34)
            hep.cms.label(ax=ax, **LABEL)
            save(fig, "composition", f"origin_{ch}_{win}")
        # 4) signal S/B per category and window
        fig, ax = plt.subplots(figsize=(12, 8))
        for i, s in enumerate(L.SIGNALS6):
            y = []
            xl = []
            for win in ("Low", "High"):
                for c in L.CATS:
                    S = J.get(f"{ch}|{win}|SIG_{s}|{c}", [0])[0]
                    B = J.get(f"{ch}|{win}|sum noQCD|{c}", [0])[0]
                    y.append(S / B if B > 0 else np.nan)
                    xl.append(f"{win}\n{c}")
            ax.plot(range(8), y, "o-", label=s)
        ax.set_xticks(range(8), xl, fontsize=13); ax.set_yscale("log")
        ax.set_ylabel("raw S / B (B = MC bkg without QCD)")
        ax.axvline(3.5, color="k", ls=":")
        ax.legend(fontsize=12, ncol=2)
        ax.set_title(f"{ch}: signal/background per iso category and window", fontsize=14, loc="left", pad=34)
        hep.cms.label(ax=ax, **LABEL)
        save(fig, "signal", f"SoverB_{ch}")


def coverage():
    J = load("04a_coverage")
    if not J:
        return
    e = np.array(J["fine_edges"])
    for tr in ("F", "P"):
        fig, ax = plt.subplots(figsize=(10, 8))
        for win, ls in (("Low", "-"), ("High", "--")):
            for tl, col in (("T", "#e42536"), ("L", "#5790fc")):
                k = f"{win}|{tr}|{tl}"
                if k not in J or not J[k]["tot"]:
                    continue
                h = np.array(J[k]["pt_sumw"]) / J[k]["tot"]
                hep.histplot(h, e, ax=ax, ls=ls, color=col, label=f"{win}, {tl} (sumw {J[k]['tot']:.1f})")
        ax.set_xscale("log"); ax.set_xlabel(r"muon $p_T$ [GeV]"); ax.set_ylabel("fraction per bin")
        ax.legend(fontsize=13)
        ax.set_title(f"SS: truth-{'nonprompt' if tr == 'F' else 'prompt'} FO muons, low vs high $m_{{\\mu\\mu jj}}$", fontsize=14, loc="left", pad=34)
        hep.cms.label(ax=ax, **LABEL)
        save(fig, "coverage", f"pt_{tr}")


def fakerate():
    J = load("04b_fakerate")
    if not J:
        return
    groups = {"compare_windows": ["F_lowSS", "F_highSS", "F_lowSSOS"],
              "compare_origin": ["F_lowSS", "F_lowSS_bOrigin", "F_lowSS_TTLJ", "F_lowSS_QCD"],
              "prompt_eff": ["P_lowSS", "P_highSS"]}
    for gname, keys in groups.items():
        m0 = J[keys[0]]
        neta = len(m0["eta"]) - 1
        fig, axs = plt.subplots(1, neta, figsize=(9 * neta, 8), sharey=True)
        axs = np.atleast_1d(axs)
        for j in range(neta):
            ax = axs[j]
            for i, k in enumerate(keys):
                if k not in J:
                    continue
                m = J[k]
                pt = np.array(m["pt"]); r = np.array(m["r"])[:, j]; er = np.array(m["err"])[:, j]
                hi = np.minimum(pt[1:], 500.0)  # open last bin: place the point inside the populated range
                x = np.sqrt(pt[:-1] * hi) * (1 + 0.04 * (i - len(keys) / 2))
                ok = r >= 0
                ax.errorbar(x[ok], r[ok], yerr=er[ok], xerr=None, fmt="o", label=k, capsize=3)
            ax.set_xscale("log"); ax.set_xlabel(r"muon $p_T$ [GeV]")
            ax.text(0.05, 0.93, f"$|\\eta|$ {m0['eta'][j]}-{m0['eta'][j + 1]}", transform=ax.transAxes, fontsize=16)
            if j == 0:
                ax.set_ylabel("T / FO rate (weighted MC)")
                hep.cms.label(ax=ax, **LABEL)
            ax.legend(fontsize=12)
        save(fig, "fakerate", gname)


def closure():
    J = load("04c_closure")
    if not J:
        return
    for key, res in J.items():
        e = np.array(res["edges"])
        tgt = np.array(res["target"]); et = np.sqrt(np.array(res["target_err2"]))
        fig, (ax, rx) = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
        hep.histplot(tgt, e, yerr=et, ax=ax, histtype="errorbar", color="k", label="truth nonprompt iso-TT (MC)")
        cols = ["#e42536", "#5790fc", "#f89c20", "#964a8b"]
        names = [n for n in res if isinstance(res[n], dict) and "pred" in res[n]]
        for c, n in zip(cols, names):
            p = np.array(res[n]["pred"])
            ep = np.sqrt(np.array(res[n]["pred_err2_mc"]) + np.array(res[n].get("pred_err_map", np.zeros(len(p)))) ** 2)
            hep.histplot(p, e, ax=ax, color=c, label=f"{n}: {p.sum():.2f}")
            with np.errstate(divide="ignore", invalid="ignore"):
                rx.errorbar(0.5 * (e[1:] + e[:-1]), p / tgt, yerr=ep / tgt, fmt="o", color=c, ms=4)
        rx.axhline(1, color="k", ls=":"); rx.set_ylim(0, 3); rx.set_ylabel("pred / truth")
        rx.set_xlabel(r"$m_{\mu\mu jj}$ [GeV]"); rx.set_xscale("log")
        ax.set_ylabel("events / bin"); ax.legend(fontsize=11)
        ax.set_title(f"closure SS {key}: map from SS Low; target {tgt.sum():.2f}", fontsize=13, loc="left", pad=34)
        hep.cms.label(ax=ax, **LABEL)
        save(fig, "closure", f"closure_{key.replace('|', '_')}")


def signal():
    J = load("05_signal_leakage")
    if not J:
        return
    e = np.array(J["edges"])
    for what in ("WS/S_TT", "WS/B_np_TT", "fail/TT"):
        fig, ax = plt.subplots(figsize=(11, 8))
        for s in L.SIGNALS6:
            if s not in J:
                continue
            stt = np.array(J[s]["TT"][0]); ws = np.array(J[s]["WS"])
            fail = np.array(J[s]["TL"][0]) + np.array(J[s]["LT"][0]) + np.array(J[s]["LL"][0])
            with np.errstate(divide="ignore", invalid="ignore"):
                y = {"WS/S_TT": ws / stt, "WS/B_np_TT": ws / np.array(J["B_np_TT"]), "fail/TT": fail / stt}[what]
            hep.histplot(y, e, ax=ax, label=s)
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel(r"$m_{\mu\mu jj}$ [GeV]")
        ax.set_ylabel(what); ax.legend(fontsize=12, ncol=2)
        ax.set_title(f"SS signal leakage: {what}", fontsize=14, loc="left", pad=34)
        hep.cms.label(ax=ax, **LABEL)
        save(fig, "signal", "leak_" + what.replace("/", "_over_"))


def fit():
    rows = []
    for f in sorted(glob.glob(os.path.join(L.STUDY, "fit", "*", "fit_result.json"))):
        tag = os.path.basename(os.path.dirname(f))
        if tag.startswith(("smoke", "_")):
            continue
        r = json.load(open(f))["r_mdf"]
        if len(r) >= 3:
            rows.append((tag, r[0][0], r[0][0] - r[1][0], r[2][0] - r[0][0]))
    if not rows:
        return
    fig, ax = plt.subplots(figsize=(11, 0.5 * len(rows) + 3))
    for i, (tag, c, lo, hi) in enumerate(rows):
        ax.errorbar([c], [i], xerr=[[lo], [hi]], fmt="o", color="k")
    ax.set_yticks(range(len(rows)), [t for t, *_ in rows], fontsize=11)
    ax.set_xlabel("fitted r (Asimov, 68% CL)")
    ax.axvline(0, color="grey", ls=":"); ax.axvline(1, color="grey", ls=":")
    hep.cms.label(ax=ax, **LABEL)
    save(fig, "fit", "r_summary")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="composition,coverage,fakerate,closure,signal,fit")
    a = ap.parse_args()
    for s in a.only.split(","):
        globals()[s]()
    print("plots in", L.PLOTS)


if __name__ == "__main__":
    main()
