#!/usr/bin/env python3
"""Data/MC of the generator study drawn in the cutbased plotter format (plotter._draw): stacked
DY / TT / Nonprompt / Others, data points, MC-stat band, ratio pad.

The stack holds ONE Drell-Yan prediction, so every DY source gets its own figure:
    <out>/<Region><CH>_<var>__DY-<tag>_plot.png
The DY source is named in the second label line of the plot.

  --preset resolved2D   DYCR_Resolved_<CH>_mll_ptll (2D): m(ll) and pT(ll) after reco pT(ll) > --ptll-min
  --preset boosted1D    the boosted DY CR 1D histograms: mll, ll_pt, leading AK8 jet pT, m(lJ)
  --preset resolved1D   the analyzer's 1D DY CR histograms: mass, pt, leading/subleading jet pT, mlljj
  --preset lowjet0|1    LowJet_<CH>_nJet{0,1}_mll_ptll (2D): m(ll) to 2 TeV and pT(ll)
  --logx --per-gev      log x axis and Events / GeV, i.e. the axes of the make_dy_datamc_3gen.py
                    overlay figures, so a figure here can be read bin-for-bin against its overlay
  --dy TAG=DIR[:KIND[:HISTDIR[:LABEL]]]   KIND: LO (default) | FxFx | POWHEG;  HISTDIR default
                    Central (e.g. DYCR_COnly/Central for a DYCRStudy production); LABEL is what the
                    plot says when the folder-safe TAG is too terse, and defaults to TAG.
Data and non-DY MC come from --nondy-base (Central). Grouping, colours and the data stream per
channel are the plotter's own (config.SAMPLE_RULES / BACKGROUND_GROUPS / CHANNELS); the HT-binned
W+jets aliases, which carry no skim prefix, are added to Nonprompt explicitly.
The band is the MC statistical uncertainty only -- these productions are WeightSystOnly / Central.

    cd plot/HNWR_2024/cutbased; PLOT_EXTRA_BINDS="/tmp:/tmp" ./condor/in_container.sh python3 \\
        studies/DY/09_three_generators/scripts/draw_datamc_cutbased_format.py --preset ... --out DIR
"""
import argparse, glob, os, re, sys, types
import numpy as np, uproot, ROOT
PC = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased"
sys.path.insert(0, PC)
import config, plotter                    # noqa: E402
import chargeflip_plots as cfp            # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--nondy-base", default="/gv0/Users/achihwan/SKNanoOutput_dy3gen/HNWR/DYCRSplit_NoDYCorr_WeightSystOnly/2024")
ap.add_argument("--dy", action="append", required=True)
ap.add_argument("--preset", required=True, choices=["resolved2D", "resolved1D", "boosted1D", "lowjet0", "lowjet1"])
ap.add_argument("--ptll-min", type=float, default=50.)
ap.add_argument("--out", required=True)
ap.add_argument("--rmin", type=float, default=0.5); ap.add_argument("--rmax", type=float, default=1.5)
# The overlay figures of make_dy_datamc_3gen.py draw the same edges on a log x axis as a density;
# --logx --per-gev reproduce that here, so a cutbased-format figure can be read against its overlay.
ap.add_argument("--logx", action="store_true", help="log x axis (the overlay figures' axis)")
ap.add_argument("--per-gev", action="store_true", help="divide by the bin width: Events / GeV, not Events / bin")
ap.add_argument("--ymin", type=float, default=None, help="y-axis floor (default 0.5, or 0.005 with --per-gev)")
a = ap.parse_args()
YMIN = a.ymin if a.ymin is not None else (0.005 if a.per_gev else 0.5)
os.makedirs(a.out, exist_ok=True)
ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetOptTitle(0); ROOT.TH1.AddDirectory(False)

CHL = {"EE": "ee", "MM": "#mu#mu"}
MLL_CR = list(np.arange(60., 151., 5.))
MLL_WIDE = [60, 70, 80, 85, 90, 95, 100, 110, 120, 150, 200, 250, 300, 400, 500, 600, 800, 1000, 1500, 2000]
PTLL = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 150, 200, 250, 350, 500, 1000]
cut = f"p_{{T}}(ll) > {a.ptll_min:.0f} GeV" if a.ptll_min > 0 else "no p_{T}(ll) cut"
if a.preset == "resolved2D":
    REGION, TAG, H2 = "Resolved DY CR", "ResolveDY", "DYCR_Resolved_{ch}_mll_ptll"
    VARS = [("mll", "x", MLL_CR, "m(ll) (GeV)"), ("dilepton_pt", "y", PTLL, "p_{T}(ll) (GeV)")]
elif a.preset.startswith("lowjet"):
    n = a.preset[-1]
    REGION, TAG, H2 = f"{n} jet, no AK8", f"LowJet{n}j", "LowJet_{ch}_nJet" + n + "_mll_ptll"
    VARS = [("mll", "x", MLL_WIDE, "m(ll) (GeV)"), ("dilepton_pt", "y", PTLL, "p_{T}(ll) (GeV)")]
elif a.preset == "boosted1D":
    REGION, TAG, H2, H1 = "Boosted DY CR", "BoostDY", None, "DYCR_Boosted_{ch}_{how}"
    cut = ""
    VARS = [("mll", "mll", list(np.arange(60., 151., 10.)), "m(ll) (GeV)"),
            ("dilepton_pt", "ll_pt", [0, 100, 200, 300, 400, 500, 700, 1000], "p_{T}(ll) (GeV)"),
            ("leading_fatjet_pt", "leading_fatjet_pt", [200, 300, 400, 500, 600, 800, 1200, 2000], "Leading AK8 jet p_{T} (GeV)"),
            ("mlljj", "mlljj", [800, 1000, 1200, 1500, 1800, 2400, 8000], "m(lJ) (GeV)")]
else:
    REGION, TAG, H2, H1 = "Resolved DY CR", "ResolveDY", None, "DYCR_Resolved_{ch}_{how}"
    cut = ""
    VARS = [("mll", "mass", MLL_CR, "m(ll) (GeV)"),
            ("dilepton_pt", "pt", [0, 50, 70, 100, 150, 200, 250, 300, 400, 500, 700, 1000], "p_{T}(ll) (GeV)"),
            ("leading_jet_pt", "leading_jet_pt", [40, 60, 80, 100, 150, 200, 300, 400, 600, 800, 1200, 2000], "Leading jet p_{T} (GeV)"),
            ("subleading_jet_pt", "subleading_jet_pt", [40, 60, 80, 100, 150, 200, 300, 400, 600, 1000, 2000], "Subleading jet p_{T} (GeV)"),
            ("mlljj", "mlljj", [800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 4000, 8000], "m(lljj) (GeV)")]


def group_of(fname, ch):
    """plotter group of a non-DY / data file, or None."""
    stem = config.sample_stem(fname)
    if stem is None:
        return "Nonprompt" if fname.startswith("WtoLNu_") else None      # HT-binned W+jets, no skim prefix
    if config.is_signal(stem):
        return None
    if config.is_data(stem):
        return "data" if config.is_data(stem, config.CHANNELS[ch]["data"]) else None
    g = config.classify_sample(re.sub(r"_p\d\d$", "", stem))[0]
    return None if g == "DYJets" else g


def dy_files(d, kind):
    fs = sorted(glob.glob(os.path.join(d, "*.root")))
    b = os.path.basename
    if kind == "FxFx":
        return [f for f in fs if b(f).endswith("_FxFx.root")]
    if kind == "POWHEG":
        return [f for f in fs if re.match(r"DYto2(E|Mu)_MLL", b(f)) and not b(f).endswith("_FxFx.root")]
    return [f for f in fs if b(f).startswith("Skim_HNWR_DYto2L-4Jets")]


def get(path, hdir, ch, how, edges):
    """(values, variances) of one file on `edges`; how = 'x' | 'y' (projection of the 2D) or a 1D suffix."""
    edges = np.asarray(edges, float)
    f = uproot.open(path)
    name = f"{hdir}/" + (H2.format(ch=ch) if how in ("x", "y") else H1.format(ch=ch, how=how))
    if name not in f:
        return None
    h = f[name]
    if how in ("x", "y"):
        v, w = h.values(), h.variances(); ex, ey = h.axis(0).edges(), h.axis(1).edges()
        ys = ey[:-1] >= a.ptll_min
        if how == "x":
            v, w, src = v[:, ys].sum(1), w[:, ys].sum(1), ex
        else:
            v, w, src = np.where(ys, v.sum(0), 0.), np.where(ys, w.sum(0), 0.), ey
    else:
        v, w, src = h.values(), h.variances(), h.axis().edges()
    c = 0.5 * (src[:-1] + src[1:]); idx = np.searchsorted(edges, c, side="right") - 1
    ok = (idx >= 0) & (idx < len(edges) - 1)
    ov, ow = np.zeros(len(edges) - 1), np.zeros(len(edges) - 1)
    np.add.at(ov, idx[ok], v[ok]); np.add.at(ow, idx[ok], w[ok])
    return ov, ow


def fit(s, nmax=13):
    """Both label lines sit left of the legend at text size 0.06, which holds ~13 glyphs; anything
    longer runs into the legend, so shrink it to fit. TLatex commands (#mu, #times) are one glyph."""
    n = len(re.sub(r"#[a-zA-Z]+", "x", s))
    return s if n <= nmax else f"#scale[{nmax / n:.2f}]{{{s}}}"


SYMLOG_LINTHRESH, SYMLOG_LINSCALE = 50., 0.4      # matplotlib defaults used by make_dy_datamc_3gen.py


def symlog(x):
    """matplotlib's symlog transform (base 10): linear up to LINTHRESH, log above, so a binning that
    starts at 0 can be drawn on a log-like axis. ROOT has no such scale -- the histogram is filled on
    the transformed edges and drawn linearly, with the real values written on the axis by hand."""
    x = np.asarray(x, float)
    adj = SYMLOG_LINSCALE / (1. - 0.1)
    L = SYMLOG_LINTHRESH
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.sign(x) * L * (adj + np.log10(np.abs(x) / L))
    return np.where(np.abs(x) <= L, x * adj, out)


def th1(name, edges, val, var):
    h = ROOT.TH1D(name, "", len(edges) - 1, np.asarray(edges, dtype="float64")); h.Sumw2()
    for k in range(len(val)):
        h.SetBinContent(k + 1, float(val[k])); h.SetBinError(k + 1, float(np.sqrt(max(var[k], 0.0))))
    return h


dys = []
for spec in a.dy:
    tag, rest = spec.split("=", 1); bits = rest.split(":")
    dys.append((tag, bits[0], bits[1] if len(bits) > 1 and bits[1] else "LO",
                bits[2] if len(bits) > 2 and bits[2] else "Central", bits[3] if len(bits) > 3 and bits[3] else tag))
nondy_files = sorted(glob.glob(os.path.join(a.nondy_base, "*.root")))

for ch in CHL:
    for vname, how, edges, xl in VARS:
        if how == "y":
            edges = [e for e in edges if e >= a.ptll_min]
        # A log axis cannot show a bin that starts at 0, so there --logx means symlog: the histograms
        # are filled on the transformed edges, the pad stays linear, and the ticks are drawn by hand.
        sym = a.logx and float(edges[0]) <= 0.
        draw_edges = symlog(edges) if sym else np.asarray(edges, float)
        xticks = None
        if sym:
            xticks = [(float(symlog(v)), lab) for v, lab in
                      ((0, "0"), (10, "10"), (100, "10^{2}"), (1000, "10^{3}"), (10000, "10^{4}"))
                      if edges[0] <= v <= edges[-1]]
        widths = np.diff(np.asarray(edges, float))
        base = {}
        for p in nondy_files:
            g = group_of(os.path.basename(p)[:-5], ch)
            if g is None:
                continue
            got = get(p, "Central", ch, how, edges)
            if got is None:
                continue
            base[g] = [got[0], got[1]] if g not in base else [base[g][0] + got[0], base[g][1] + got[1]]
        if "data" not in base:
            print(f"[skip] {ch} {vname}: no data"); continue
        for tag, ddir, kind, hdir, disp in dys:
            dv = None
            for p in dy_files(ddir, kind):
                got = get(p, hdir, ch, how, edges)
                if got is not None:
                    dv = [got[0], got[1]] if dv is None else [dv[0] + got[0], dv[1] + got[1]]
            if dv is None:
                print(f"[skip] {ch} {vname} DY-{tag}: no histogram"); continue
            keeper = []; stem = f"{TAG}{ch}_{vname}__DY-{tag}"
            gh = {"DYJets": th1(f"h_{stem}_DY", draw_edges, dv[0], dv[1])}
            for g in ("TT", "Nonprompt", "Others"):
                gh[g] = th1(f"h_{stem}_{g}", draw_edges, base[g][0], base[g][1]) if g in base else None
            tot = gh["DYJets"].Clone(f"h_tot_{stem}")
            for g in ("TT", "Nonprompt", "Others"):
                if gh[g]:
                    tot.Add(gh[g])
            hd = th1(f"h_data_{stem}", draw_edges, base["data"][0], base["data"][0])
            mc = sum(tot.GetBinContent(i) for i in range(1, tot.GetNbinsX() + 1))   # yield, before --per-gev
            if a.per_gev:
                # Divide by the PHYSICAL bin width (the drawn edges may be transformed), so the stack,
                # the data points and the bands all become densities; the ratio is unchanged.
                for h in [h for h in gh.values() if h] + [tot, hd]:
                    for i, w in enumerate(widths, 1):
                        h.SetBinContent(i, h.GetBinContent(i) / w); h.SetBinError(i, h.GetBinError(i) / w)
            gs, grb, grs = cfp.stat_graphs(tot)
            keeper += [h for h in gh.values() if h] + [tot, hd, gs, grb, grs]
            # The DY source goes next to the channel, the region on the second line; the pT(ll) cut is
            # in the folder name. fit() shrinks a line that would otherwise reach into the legend.
            args = types.SimpleNamespace(output=stem, logy=True, ymin=YMIN, ymax=None, rmin=a.rmin, rmax=a.rmax,
                                         xlabel=xl, hist=stem, label1=fit(f"{CHL[ch]}, DY: {disp}"),
                                         label2=fit(REGION), logx=a.logx and not sym, xticks=xticks,
                                         ylabel="Events / GeV" if a.per_gev else None)
            plotter._draw(args, tot, hd, gh, gs, grb, grs, float(draw_edges[0]), float(draw_edges[-1]),
                          False, os.path.join(a.out, stem), keeper)
            print(f"  {stem}: data {base['data'][0].sum():.0f}  MC {mc:.1f}  data/MC = {base['data'][0].sum() / mc:.3f}")
