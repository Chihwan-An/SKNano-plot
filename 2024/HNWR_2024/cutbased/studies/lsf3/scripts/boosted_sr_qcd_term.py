#!/usr/bin/env python3
"""Does the QCD term of the JMAR discriminant do anything in the boosted SR?  Two plots that answer it.

A term in the denominator of  D = P_S / (P_S + a_top P_top + a_QCD P_QCD)  can only help if the ratio it adds,
r = P_bkg / P_S, is LARGE for background and SMALL for signal.  If signal and background have the same r, the
term shifts every event by the same amount and changes nothing.  So:

  <out>/ratio_<region>.png   the two ratios themselves, r_top and r_QCD, signal against background, unit area.
                             Each panel carries the AUC of that ratio used alone as a discriminant: 0.5 means
                             the ratio is blind to the difference between signal and background.
  <out>/roc_<region>.png     the consequence: ROC of the top-only, QCD-only and combined discriminant.  If the
                             QCD term carried information the combined curve would sit above the top-only one.
  <out>/alpha2d_<region>.png the full (a_top, a_QCD) plane.  AUC is constant along every ray through the origin,
                             because scaling both coefficients together leaves the event ordering untouched --
                             the contours coming out as straight lines through the origin is the check of that.
  <out>/roc_LSF3_<region>.png LSF3, the cut the tagger is meant to replace, against the tagger discriminants on
                             the same events -- the head-to-head the whole study is about.
  <out>/roc_XWW_<region>.png every non-empty combination of the three XWW classes that could make up P_S in this
                             region -- the channel-matched semileptonic one, XWW3q and XWW4q -- so that whether
                             the hadronic classes carry anything is read off directly.
  <out>/roc_PS_<region>.png  the same question asked of the NUMERATOR: which P_S separates best, the single
                             channel-matched class or the sum of all four XWW classes that JMAR writes down.
                             Same denominator (P_S + P_top) throughout, so only the numerator is being compared.

Background: every chunk of trees_boosted_bkg_full, each sample scaled by xsec / (sum of genEventSumw over its
chunks).  Signal: xsec / sumsign from the registry json.  Efficiencies are lumi-weighted, so a sample counts for
what it is worth in the region, not for how many MC events it happens to have.
  boosted_sr_qcd_term.py [--bkg trees_boosted_bkg_full] [--mass 3000]"""
import argparse, glob, itertools, json, os, re
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import mplhep as hep
import ROOT

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NANO15 = os.path.join(os.environ.get("SKNANO_HOME", "/data9/Users/achihwan/nano15/SKNanoAnalyzer"), "Nano15_Analyzers")
ap = argparse.ArgumentParser()
ap.add_argument("--sig", default=f"{S}/trees_boosted_sig")
ap.add_argument("--bkg", default=f"{S}/trees_boosted_bkg_full")
ap.add_argument("--xsec", default=f"{S}/condor/bkg_xsec_all.json")
ap.add_argument("--sig-json", default=os.path.join(NANO15, "HNWR/data/Sample/2024"))
ap.add_argument("--out", default=f"{S}/fatjet_taggers/globalpart3_D")
ap.add_argument("--roc-dir", default=None)
ap.add_argument("--scan-dir", default=None)
ap.add_argument("--mass", type=int, default=3000, help="mass point for the ratio / ROC plots")
ap.add_argument("--scan-masses", default="1000,3000,5000,7000")
a = ap.parse_args()
ROOT.gROOT.SetBatch(True)
hep.style.use("CMS")
ROC = a.roc_dir or f"{a.out}/04_roc"
SCAN = a.scan_dir or f"{a.out}/03_alpha_scan"
for _d in (ROC, SCAN): os.makedirs(_d, exist_ok=True)

LUMI = 109.8
TOP = ["TopbWev", "TopbWmv", "TopbWq", "TopbWqq", "TopbWtauhv"]
XWW = ["XWW3q", "XWW4q", "XWWqqev", "XWWqqmv"]
SIGTAG = {"EE": "WRtoNEltoElElJJ", "MM": "WRtoNMutoMuMuJJ"}
REG = {"SR_EE": ("isEE==1", "XWWqqev", "$W_R \\to eN \\to eejj$, boosted SR"),
       "SR_MM": ("isEE==0", "XWWqqmv", "$W_R \\to \\mu N \\to \\mu\\mu jj$, boosted SR")}
X = json.load(open(a.xsec))
SCAN_MASSES = [int(m) for m in a.scan_masses.split(",")]
LSFCUT = 0.75          # the LSF3 working point the tagger is being compared against
EFFREF = 0.80          # working point used to quote a D cut: keep this fraction of the signal
CHUNK = re.compile(r"_c\d{3}$")


def grab(path, sel, sig_name):
    """Per-event P_S, P_top, P_QCD, the four XWW classes on their own, and the weight."""
    d = ROOT.RDataFrame("tagger", path).Filter(f"region==1 && {sel}")
    A = d.AsNumpy([f"p_{sig_name}", "p_QCD", "w", "lsf3"] + [f"p_{t}" for t in TOP] + [f"p_{x}" for x in XWW])
    if len(A["w"]) == 0:
        return None
    out = {"S": A[f"p_{sig_name}"], "top": sum(A[f"p_{t}"] for t in TOP), "QCD": A["p_QCD"],
           "w": A["w"], "lsf3": A["lsf3"]}
    for x in XWW:
        out[x] = A[f"p_{x}"]
    return out


def roc_points(sc, lab, wt, grid=np.arange(0.1, 1.0, 0.1)):
    """Signal efficiency at fixed background efficiency, with the MC statistical error on both.

    Not drawn: a ROC is conventionally a plain curve, and here the error is ~0.003, thinner than the line.
    Kept because the numbers are worth quoting when asking whether two curves really differ.

    The samples are weighted, so the binomial error uses effective entries N_eff = (sum w)^2 / sum w^2:
    a sample of few high-weight events carries a bigger error than its raw count suggests.
    """
    o = np.argsort(-sc)
    y, w = lab[o], wt[o]
    cs, cb = np.cumsum(w * (y == 1)), np.cumsum(w * (y == 0))
    es, eb = cs / cs[-1], cb / cb[-1]
    neff = {k: (w[y == k].sum() ** 2) / (w[y == k] ** 2).sum() for k in (0, 1)}
    i = np.searchsorted(eb, grid)
    i = i[i < len(eb)]
    xs, ys = eb[i], es[i]
    return xs, ys, np.sqrt(ys * (1 - ys) / neff[1]), np.sqrt(xs * (1 - xs) / neff[0]), neff


def auc(score, lab, wt):
    """Weighted AUC: the probability that a random signal event scores above a random background one."""
    o = np.argsort(score); y, w = lab[o], wt[o]
    cw = np.cumsum(w * (y == 0))                       # background weight below each event
    tot_b = cw[-1]; tot_s = (w * (y == 1)).sum()
    if tot_b <= 0 or tot_s <= 0:
        return float("nan")
    return float((w[y == 1] * cw[y == 1]).sum() / (tot_s * tot_b))


for region, (sel, sig_name, chlab) in REG.items():
    ch = region.split("_")[1]
    r = grab(f"{a.sig}/{ch}_MWR{a.mass}_N200.root", sel, sig_name)
    if r is None:
        continue
    j = json.load(open(f"{a.sig_json}/{SIGTAG[ch]}_MWR{a.mass}_N200.json"))
    r["w"] = r["w"] * (LUMI * 1000.0 * j["xsec"] / j["sumsign"])
    SIG = r

    # background: sum genEventSumw over the chunks of each sample before scaling
    sumw = {}
    for p in sorted(glob.glob(f"{a.bkg}/*.norm.json")):
        nm = json.load(open(p)); sumw[nm["sample"]] = sumw.get(nm["sample"], 0.0) + nm["sumw"]
    parts = []
    for p in sorted(glob.glob(f"{a.bkg}/*.root")):
        s = CHUNK.sub("", os.path.basename(p)[:-5])
        if s not in X or s not in sumw:
            print(f"!! no xsec/sumw for {s}"); continue
        g = grab(p, sel, sig_name)
        if g is None:
            continue
        g["w"] = g["w"] * (LUMI * 1000.0 * X[s]["xsec"] / sumw[s])
        parts.append(g)
    if not parts:
        continue
    BKGD = {k: np.concatenate([g[k] for g in parts]) for k in parts[0]}
    print(f"\n== {region}  signal {a.mass/1000:g} TeV {SIG['w'].sum():.1f} ev | background {BKGD['w'].sum():.1f} ev "
          f"from {len(sumw)} samples, {len(BKGD['w'])} raw entries")

    C = lambda k: np.r_[SIG[k], BKGD[k]]          # signal then background, in one array
    Ss, Bs = SIG["S"], BKGD["S"]
    lab = np.r_[np.ones(len(Ss)), np.zeros(len(Bs))]
    wt = C("w")
    PS = C("S")
    ratios = {"top": (C("top") / np.maximum(PS, 1e-30), "$r_{top} = P_{top}\\,/\\,P_S$", "tab:red"),
              "QCD": (C("QCD") / np.maximum(PS, 1e-30), "$r_{QCD} = P_{QCD}\\,/\\,P_S$", "tab:blue")}

    # ---- the two ratios ------------------------------------------------------------------------------------------
    eb = np.logspace(-6, 4, 61)
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    for ax, key in zip(axes, ("top", "QCD")):
        rr, xl, _ = ratios[key]
        # a high ratio means background-like, so 1 - AUC to read it as "signal scores low"
        A = 1.0 - auc(rr, lab, wt)
        for m, c, l in ((lab == 1, "tab:green", f"signal {a.mass/1000:g} TeV"), (lab == 0, "black", "background (all)")):
            h = np.histogram(np.clip(rr[m], eb[0], eb[-1]), bins=eb, weights=wt[m])[0]
            ax.stairs(h / h.sum(), eb, color=c, lw=3.5, ls="-" if c == "tab:green" else "--", label=l)
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(eb[0], eb[-1])
        ax.set_xlabel(xl); ax.set_ylabel("fraction of events")
        ax.grid(alpha=0.3, which="both")
        ax.text(0.04, 0.95, f"AUC = {A:.3f}", transform=ax.transAxes, va="top", fontsize=20,
                bbox=dict(fc="white", ec="0.6", alpha=0.9))
        ax.legend(fontsize=14, loc="upper right")
    # no verdict in the titles: r_QCD does separate on its own (AUC well above 0.5), it just adds little
    # on top of r_top -- that is what the ROC and the alpha scan are for, not this panel.
    hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=axes[0], fontsize=15)
    fig.suptitle(f"{chlab}   ($m_{{W_R}}$ = {a.mass/1000:g} TeV)", fontsize=17)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(f"{ROC}/ratio_{region}.png", dpi=110); plt.close(fig)
    print(f"   wrote {a.out}/ratio_{region}.png")

    # ---- ROC of the three discriminants ---------------------------------------------------------------------------
    Ps, Pt, Pq = C("S"), C("top"), C("QCD")
    variants = [("$P_S/(P_S + P_{top})$  (top only)", "tab:red", Ps / np.maximum(Ps + Pt, 1e-30)),
                ("$P_S/(P_S + P_{QCD})$  (QCD only)", "tab:blue", Ps / np.maximum(Ps + Pq, 1e-30)),
                ("$P_S/(P_S + P_{top} + P_{QCD})$", "tab:purple", Ps / np.maximum(Ps + Pt + Pq, 1e-30))]
    fig, ax = plt.subplots(figsize=(11, 9))
    for l, c, sc in variants:
        o = np.argsort(-sc)
        es = np.cumsum(wt[o] * (lab[o] == 1)) / (wt * (lab == 1)).sum()
        eb_ = np.cumsum(wt[o] * (lab[o] == 0)) / (wt * (lab == 0)).sum()
        ax.plot(np.maximum(eb_, 1e-6), es, color=c, lw=3, label=f"{l}   AUC {auc(sc, lab, wt):.4f}")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)      # linear x: the log axis only stretched a region nobody uses
    ax.set_xlabel("background efficiency"); ax.set_ylabel("signal efficiency")
    ax.grid(alpha=0.3, which="both")
    hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=15)
    ax.legend(fontsize=13, loc="lower right",
              title=f"{chlab}\n$m_{{W_R}}$ = {a.mass/1000:g} TeV, $m_N$ = 200 GeV", title_fontsize=13)
    fig.tight_layout(); fig.savefig(f"{ROC}/roc_{region}.png", dpi=110); plt.close(fig)
    print(f"   wrote {a.out}/roc_{region}.png")

    # ---- which numerator?  same denominator, only P_S changes -----------------------------------------------------
    matched = sig_name                       # XWWqqev in SR EE, XWWqqmv in SR MM
    other = "XWWqqmv" if matched == "XWWqqev" else "XWWqqev"
    nums = [(f"{matched} (channel matched)", "tab:green", C(matched)),
            (f"{matched} + XWW3q", "tab:orange", C(matched) + C("XWW3q")),
            (f"{matched} + {other}", "tab:brown", C(matched) + C(other)),
            ("all four XWW (JMAR)", "tab:purple", sum(C(x) for x in XWW))]
    fig, ax = plt.subplots(figsize=(11, 9))
    print(f"   numerator scan ({region}):")
    for l, c, num in nums:
        sc = num / np.maximum(num + Pt, 1e-30)
        o = np.argsort(-sc)
        es = np.cumsum(wt[o] * (lab[o] == 1)) / (wt * (lab == 1)).sum()
        ebk = np.cumsum(wt[o] * (lab[o] == 0)) / (wt * (lab == 0)).sum()
        A = auc(sc, lab, wt)
        ax.plot(np.maximum(ebk, 1e-6), es, color=c, lw=3, label=f"{l}   AUC {A:.4f}")
        print(f"      {l:34s} AUC {A:.4f}")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)      # linear x: the log axis only stretched a region nobody uses
    ax.set_xlabel("background efficiency"); ax.set_ylabel("signal efficiency")
    ax.grid(alpha=0.3, which="both")
    hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=15)
    ax.legend(fontsize=13, loc="lower right",
              title=f"{chlab}\n$D = P_S/(P_S + P_{{top}})$, numerator varied", title_fontsize=13)
    fig.tight_layout(); fig.savefig(f"{ROC}/roc_PS_{region}.png", dpi=110); plt.close(fig)
    print(f"   wrote {a.out}/roc_PS_{region}.png")

    # ---- the seven subsets of {matched, XWW3q, XWW4q} --------------------------------------------------------------
    trio = [matched, "XWW3q", "XWW4q"]
    combos = []
    for k in (1, 2, 3):
        for cc in itertools.combinations(trio, k):
            combos.append((" + ".join(cc), sum(C(f) for f in cc)))
    cmap7 = plt.get_cmap("tab10")
    fig, ax = plt.subplots(figsize=(11, 9))
    print(f"   XWW subset scan ({region}), denominator = P_S + P_top + P_QCD:")
    rows = []
    for k, (l, num) in enumerate(combos):
        sc = num / np.maximum(num + Pt + Pq, 1e-30)
        o = np.argsort(-sc)
        es = np.cumsum(wt[o] * (lab[o] == 1)) / (wt * (lab == 1)).sum()
        ebk = np.cumsum(wt[o] * (lab[o] == 0)) / (wt * (lab == 0)).sum()
        A = auc(sc, lab, wt)
        rows.append((A, l))
        ax.plot(np.maximum(ebk, 1e-6), es, color=cmap7(k), lw=3,
                ls="-" if matched in l else "--", label=f"{l}   {A:.4f}")
    for A, l in sorted(rows, reverse=True):
        print(f"      {A:.4f}  {l}")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("background efficiency"); ax.set_ylabel("signal efficiency")
    ax.grid(alpha=0.3, which="both")
    hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=15)
    ax.legend(fontsize=12, loc="lower right",
              title=f"{chlab}, $m_{{W_R}}$ = {a.mass/1000:g} TeV\n"
                    f"$D = P_S/(P_S + P_{{top}} + P_{{QCD}})$,  $P_S$ = the listed classes\n"
                    f"dashed = without {matched};  AUC at the right", title_fontsize=11)
    fig.tight_layout(); fig.savefig(f"{ROC}/roc_XWW_{region}.png", dpi=110); plt.close(fig)
    print(f"   wrote {ROC}/roc_XWW_{region}.png")

    # ---- LSF3 against the tagger -----------------------------------------------------------------------------------
    L = C("lsf3")
    head = [("LSF$_3$", "tab:green", L),
            ("$P_S/(P_S + P_{top})$", "tab:red", Ps / np.maximum(Ps + Pt, 1e-30)),
            ("$P_S/(P_S + P_{top} + P_{QCD})$", "tab:purple", Ps / np.maximum(Ps + Pt + Pq, 1e-30))]
    fig, ax = plt.subplots(figsize=(11, 9))
    print(f"   LSF3 vs tagger ({region}):")
    for l, c, sc in head:
        o = np.argsort(-sc)
        es = np.cumsum(wt[o] * (lab[o] == 1)) / (wt * (lab == 1)).sum()
        ebk = np.cumsum(wt[o] * (lab[o] == 0)) / (wt * (lab == 0)).sum()
        A = auc(sc, lab, wt)
        ax.plot(np.maximum(ebk, 1e-6), es, color=c, lw=3.5 if "LSF" in l else 3,
                ls="-" if "LSF" in l else "--", label=f"{l}   AUC {A:.4f}")
        print(f"      {l:34s} AUC {A:.4f}")
        if "LSF" in l:      # the working point actually in use
            # the working point actually in use today
            m = sc > LSFCUT
            es75 = wt[(lab == 1) & m].sum() / wt[lab == 1].sum()
            eb75 = wt[(lab == 0) & m].sum() / wt[lab == 0].sum()
            ax.plot([eb75], [es75], marker="o", ms=11, color=c, mec="white", mew=1.5,
                    label=f"LSF$_3$ > {LSFCUT:g}  ({es75*100:.0f}% sig, {eb75*100:.0f}% bkg)")
            print(f"      LSF3 > {LSFCUT:g}: signal {es75*100:.1f}%, background {eb75*100:.1f}%")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("background efficiency"); ax.set_ylabel("signal efficiency")
    ax.grid(alpha=0.3, which="both")
    hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=15)
    ax.legend(fontsize=12, loc="lower right",
              title=f"{chlab}\n$m_{{W_R}}$ = {a.mass/1000:g} TeV, $m_N$ = 200 GeV", title_fontsize=12)
    fig.tight_layout(); fig.savefig(f"{ROC}/roc_LSF3_{region}.png", dpi=110); plt.close(fig)
    print(f"   wrote {ROC}/roc_LSF3_{region}.png")

    # ---- alpha scan ----------------------------------------------------------------------------------------------
    # Scaling a_top and a_QCD together leaves the ordering untouched, so a_top is fixed to 1 and only the ratio
    # is scanned: a_QCD = 0 is the top-only discriminant, a_QCD -> inf is the QCD-only one.
    AQ = np.concatenate([[0.0], np.logspace(-3, 3, 61)])
    fig, ax = plt.subplots(figsize=(11, 9))
    print(f"   alpha scan ({region}):")
    for m, c in zip(SCAN_MASSES, plt.cm.viridis(np.linspace(0, 0.92, len(SCAN_MASSES)))):
        rs = grab(f"{a.sig}/{ch}_MWR{m}_N200.root", sel, sig_name)
        if rs is None:
            continue
        jj = json.load(open(f"{a.sig_json}/{SIGTAG[ch]}_MWR{m}_N200.json"))
        ws = rs["w"] * (LUMI * 1000.0 * jj["xsec"] / jj["sumsign"])
        lb = np.r_[np.ones(len(ws)), np.zeros(len(BKGD["w"]))]
        wg = np.r_[ws, BKGD["w"]]
        ps = np.r_[rs["S"], BKGD["S"]]; pt = np.r_[rs["top"], BKGD["top"]]; pq = np.r_[rs["QCD"], BKGD["QCD"]]
        ys = np.array([auc(ps / np.maximum(ps + pt + q * pq, 1e-30), lb, wg) for q in AQ])
        ax.plot(np.maximum(AQ, 1e-4), ys, color=c, lw=3, label=f"$m_{{W_R}}$ = {m/1000:g} TeV")
        best = int(np.nanargmax(ys))
        ax.plot([max(AQ[best], 1e-4)], [ys[best]], marker="o", ms=9, color=c)
        print(f"      {m/1000:g} TeV: a_QCD=0 -> {ys[0]:.4f}, a_QCD=1 -> {ys[np.argmin(abs(AQ-1))]:.4f}, "
              f"best {ys[best]:.4f} at a_QCD={AQ[best]:.3g}")
    ax.set_xscale("log"); ax.set_xlabel("$\\alpha_{QCD}$   ($\\alpha_{top}$ = 1; leftmost point is $\\alpha_{QCD}$ = 0)")
    ax.set_ylabel("AUC (signal vs all background)")
    ax.axvline(1.0, color="0.6", ls=":", lw=2)
    ax.text(1.05, 0.02, "JMAR default 1:1", transform=ax.get_xaxis_transform(), fontsize=13, color="0.4")
    ax.grid(alpha=0.3, which="both")
    hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=15)
    ax.legend(fontsize=13, loc="lower right", title=f"{chlab}\n$m_N$ = 200 GeV, best marked", title_fontsize=13)
    fig.tight_layout(); fig.savefig(f"{SCAN}/alphascan_{region}.png", dpi=110); plt.close(fig)
    print(f"   wrote {a.out}/alphascan_{region}.png")

    # ---- the (alpha, beta) plane ---------------------------------------------------------------------------------
    # Scaling both coefficients together leaves the ordering of events untouched, so AUC can only depend on the
    # ratio: the contours have to come out as straight lines through the origin.  That is the check.
    AT = np.logspace(-2, 2, 33)          # alpha, on P_top
    AB = np.logspace(-2, 2, 33)          # beta,  on P_QCD
    ps, pt, pq = C("S"), C("top"), C("QCD")
    Z = np.array([[auc(ps / np.maximum(ps + at * pt + ab * pq, 1e-30), lab, wt) for at in AT] for ab in AB])
    fig, ax = plt.subplots(figsize=(11, 9))
    m = ax.pcolormesh(AT, AB, Z, shading="nearest", cmap="viridis")
    cs = ax.contour(AT, AB, Z, levels=8, colors="white", linewidths=1.0, alpha=0.7)
    ax.clabel(cs, inline=True, fontsize=9, fmt="%.3f")
    fig.colorbar(m, ax=ax, label="AUC (signal vs all background)")
    jb, ja = np.unravel_index(np.nanargmax(Z), Z.shape)
    # AUC is cut-independent, so the point carries no D value on its own; quote the cut of a fixed working
    # point instead -- the D that keeps EFFREF of the signal, which is defined for every (alpha, beta).
    def dcut(at, ab):
        d = ps / np.maximum(ps + at * pt + ab * pq, 1e-30)
        ds, ws = d[lab == 1], wt[lab == 1]
        o = np.argsort(-ds)
        c = np.cumsum(ws[o]) / ws.sum()
        return float(ds[o][np.searchsorted(c, EFFREF)])
    dm, d11 = dcut(AT[ja], AB[jb]), dcut(1.0, 1.0)
    ax.plot([AT[ja]], [AB[jb]], marker="o", ms=12, color="red", mec="white", mew=1.5,
            label=f"max AUC {Z[jb, ja]:.4f} at ({AT[ja]:.2g}, {AB[jb]:.2g})")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("$\\alpha$  (coefficient of $P_{top}$)"); ax.set_ylabel("$\\beta$  (coefficient of $P_{QCD}$)")
    hep.cms.label("Work in progress", data=False, lumi=LUMI, com=13.6, ax=ax, fontsize=15)
    ax.legend(fontsize=12, loc="lower right", framealpha=0.9,
              title=f"{chlab}\n$m_{{W_R}}$ = {a.mass/1000:g} TeV,  $D = P_S/(P_S + \\alpha P_{{top}} + \\beta P_{{QCD}})$",
              title_fontsize=11)
    fig.tight_layout(); fig.savefig(f"{SCAN}/alpha2d_{region}.png", dpi=110); plt.close(fig)
    a11 = Z[np.argmin(abs(AB - 1)), np.argmin(abs(AT - 1))]
    print(f"   wrote alpha2d_{region}.png  max AUC {Z[jb, ja]:.4f} at (alpha {AT[ja]:.3g}, beta {AB[jb]:.3g}), "
          f"D>{dm:.3f} for {EFFREF*100:.0f}% signal; (1,1) gives AUC {a11:.4f} at D>{d11:.3f}")
print("BOOSTED_SR_QCD_TERM_DONE")
