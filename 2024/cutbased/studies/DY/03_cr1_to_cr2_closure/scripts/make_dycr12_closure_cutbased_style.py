#!/usr/bin/env python3
"""DY CR1 -> CR2 closure of the jet-pT correction R, drawn in the cutbased plotter format (plotter._draw).

Same inputs and method as chihwan/fig/05_backgrounds/2024/scripts/make_dycr12_closure.py (ee+mumu combined R):
  $SKNANO_OUTPUT/HNWR/DYCRStudy_RFlav_DYCRSplit_WeightSystOnly/2024, DYCR_ZptOnly/Central/DYCR{1,2}_<cat>_<ch>_jetpt_mlljj
  R_CR1(jet pT) = (data - non-DY)/DY in CR1;  DY_CR2^corr(mass) = sum_x R_CR1(x) DY_CR2(x, mass).
The band is the MC statistical uncertainty only (no systematic variations are propagated here).
Output: <out>/DYCR2_<Resolve|Boost><EE|MM>_{beforeR,afterR}_plot.png
    ./condor/in_container.sh python3 make_dycr12_closure_cutbased_style.py --out DIR     (from plot/cutbased)
"""
import argparse, glob, os, re, sys, types
import numpy as np, uproot, ROOT
PC = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased"
sys.path.insert(0, PC)
import config, plotter                    # noqa: E402
import chargeflip_plots as cfp            # noqa: E402  (stat_graphs)

ap = argparse.ArgumentParser()
ap.add_argument("--prod", default="/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/DYCRStudy_RFlav_DYCRSplit_WeightSystOnly/2024")
ap.add_argument("--variant", default="DYCR_ZptOnly")
ap.add_argument("--out", required=True)
ap.add_argument("--rmin", type=float, default=0.5); ap.add_argument("--rmax", type=float, default=1.5)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0); ROOT.TH1.AddDirectory(False)

RBINS = {"Resolved": [40, 100, 200, 400, 600, 800, 2000], "Boosted": [200, 400, 600, 2000]}
MBINS = {"Resolved": [800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 8000], "Boosted": [800, 1000, 1200, 1500, 1800, 8000]}
TAG = {"Resolved": "Resolve", "Boosted": "Boost"}
XL = {"Resolved": "m(lljj) (GeV)", "Boosted": "m(lJ) (GeV)"}
CHL = {"EE": "ee", "MM": "#mu#mu"}


def files():
    out = {}
    for p in sorted(glob.glob(os.path.join(a.prod, "*.root"))):
        stem = config.sample_stem(os.path.basename(p)[:-5])
        if stem is None or config.is_signal(stem):
            continue
        out[stem] = p
    for s in [s for s in out if re.match(r".*_p\d\d$", s) and re.sub(r"_p\d\d$", "", s) in out]:
        del out[s]
    return list(out.items())


def group_of(stem, ch):
    if config.is_data(stem):
        return "data" if config.is_data(stem, config.CHANNELS[ch]["data"]) else None
    return config.classify_sample(re.sub(r"_p\d\d$", "", stem))[0]


H = {}   # (cr, cat, ch, group) -> [values, variances, xedges, yedges]
for stem, p in files():
    f = uproot.open(p)
    for cr in ("DYCR1", "DYCR2"):
        for cat in RBINS:
            for ch in CHL:
                g = group_of(stem, ch); name = f"{a.variant}/Central/{cr}_{cat}_{ch}_jetpt_mlljj"
                if g is not None and name not in f and g != "DYJets":
                    name = f"Central/{cr}_{cat}_{ch}_jetpt_mlljj"      # data / non-DY from a production without the DYCRStudy twins
                if g is None or name not in f:
                    continue
                h = f[name]; key = (cr, cat, ch, g)
                if key in H:
                    H[key][0] += h.values(flow=False); H[key][1] += h.variances(flow=False)
                else:
                    H[key] = [h.values(flow=False).copy(), h.variances(flow=False).copy(), h.axis(0).edges(), h.axis(1).edges()]
    f.close()


def rx(v, xe, edges):
    i = np.searchsorted(xe, edges); return np.stack([v[i[k]:i[k + 1]].sum(0) for k in range(len(edges) - 1)])


def ry(v, ye, edges):
    i = np.searchsorted(ye, edges); return np.array([v[i[k]:i[k + 1]].sum() for k in range(len(edges) - 1)])


def th1(name, edges, val, var):
    h = ROOT.TH1D(name, "", len(edges) - 1, np.asarray(edges, dtype="float64")); h.Sumw2()
    for k in range(len(val)):
        h.SetBinContent(k + 1, float(val[k])); h.SetBinError(k + 1, float(np.sqrt(max(var[k], 0.0))))
    return h


for cat in RBINS:
    rb = np.array(RBINS[cat], float); mb = np.array(MBINS[cat], float)
    num = np.zeros(len(rb) - 1); den = np.zeros(len(rb) - 1)
    for c in CHL:
        nd = sum(rx(H[("DYCR1", cat, c, g)][0], H[("DYCR1", cat, c, g)][2], rb).sum(1) for g in ("TT", "Nonprompt", "Others") if ("DYCR1", cat, c, g) in H)
        d = H[("DYCR1", cat, c, "data")]; dy = H[("DYCR1", cat, c, "DYJets")]
        num += rx(d[0], d[2], rb).sum(1) - nd; den += rx(dy[0], dy[2], rb).sum(1)
    R = np.where(den > 0, num / np.where(den > 0, den, 1), 1.0)
    print(cat, "R_CR1 =", np.round(R, 3))
    for ch in CHL:
        dy2 = H[("DYCR2", cat, ch, "DYJets")]; ye = dy2[3]
        dv = rx(dy2[0], dy2[2], rb); dw = rx(dy2[1], dy2[2], rb)
        data = ry(H[("DYCR2", cat, ch, "data")][0].sum(0), ye, mb)
        for tag, w in (("beforeR", np.ones_like(R)), ("afterR", R)):
            keeper = []; stem = f"DYCR2_{TAG[cat]}{ch}_{tag}"
            gh = {"DYJets": th1(f"h_{stem}_DY", mb, ry((w[:, None] * dv).sum(0), ye, mb), ry((w[:, None] ** 2 * dw).sum(0), ye, mb))}
            for g in ("TT", "Nonprompt", "Others"):
                k = ("DYCR2", cat, ch, g)
                gh[g] = th1(f"h_{stem}_{g}", mb, ry(H[k][0].sum(0), ye, mb), ry(H[k][1].sum(0), ye, mb)) if k in H else None
            tot = gh["DYJets"].Clone(f"h_tot_{stem}")
            for g in ("TT", "Nonprompt", "Others"):
                if gh[g]:
                    tot.Add(gh[g])
            hd = th1(f"h_data_{stem}", mb, data, data)
            gs, grb, grs = cfp.stat_graphs(tot)
            keeper += list(gh.values()) + [tot, hd, gs, grb, grs]
            args = types.SimpleNamespace(output=stem, logy=True, ymin=0.5, ymax=None, rmin=a.rmin, rmax=a.rmax, xlabel=XL[cat], hist=stem,
                                         label1=CHL[ch], label2=f"{cat} DY CR2")
            plotter._draw(args, tot, hd, gh, gs, grb, grs, float(mb[0]), float(mb[-1]), False, os.path.join(a.out, stem), keeper)
            mc = sum(tot.GetBinContent(i) for i in range(1, tot.GetNbinsX() + 1))
            print(f"  {stem}: data/MC = {data.sum() / mc:.3f}")
