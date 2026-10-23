#!/usr/bin/env python3
"""D3 test card: the v2 card + two ad-hoc m_lljj slope nuisances, MassSlopeDY (DYJets) and MassSlopeTT (TT).

Hypothesis under test: JES_2024 (+2.9 sigma, constraint ~0.5-0.7) is being used as a knob for the rising data/MC vs
m_lljj in the CRs. If a dedicated slope knob exists, JES should relax towards 0 with a ~prior-sized error.

Slope template (shape only, per channel and process): f_b = exp(K * u_b), u_b = ln(m_b / 800) / ln(3000 / 800),
m_b = geometric bin centre (upper edge capped at 5000), so +1 sigma tilts the process by about +K between 800 GeV and
3 TeV. Up = N * f, Down = N / f, both renormalised to the nominal integral (the free rateParams carry the normalisation).
One nuisance per process, correlated across all channels (resolved and boosted).

  python3 make_slope_card.py <card.txt> <out_dir> [--k 0.10]
Writes <out_dir>/card_slope.txt and <out_dir>/shapes_slope.root (a full copy of the card's shapes file plus the new histograms).
"""
import argparse, math, os, re
import ROOT
ROOT.gROOT.SetBatch(True); ROOT.TH1.AddDirectory(False)

PROCS = {"DYJets": "MassSlopeDY", "TT": "MassSlopeTT"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("card"); ap.add_argument("out"); ap.add_argument("--k", type=float, default=0.10)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    lines = open(a.card).read().splitlines()
    shp = [l for l in lines if l.startswith("shapes")]
    src = shp[0].split()[3]
    assert all(l.split()[3] == src for l in shp), "card uses more than one shapes file"
    dst = os.path.join(a.out, "shapes_slope.root")
    fi = ROOT.TFile.Open(src); fo = ROOT.TFile(dst, "RECREATE")
    for kd in fi.GetListOfKeys():
        ch = kd.GetName(); di = fi.Get(ch); do = fo.mkdir(ch)
        hs = {k.GetName(): di.Get(k.GetName()) for k in di.GetListOfKeys()}
        for n, h in hs.items(): do.WriteTObject(h, n)
        for p, nuis in PROCS.items():
            if p not in hs: continue
            h = hs[p]; tot = h.Integral()
            if tot <= 0:   # empty template: the card still asks for Up/Down, write flat copies
                for s in ("Up", "Down"): do.WriteTObject(h.Clone(f"{p}_{nuis}{s}"), f"{p}_{nuis}{s}")
                continue
            up, dn = h.Clone(f"{p}_{nuis}Up"), h.Clone(f"{p}_{nuis}Down")
            for b in range(1, h.GetNbinsX() + 1):
                lo, hi = h.GetXaxis().GetBinLowEdge(b), min(h.GetXaxis().GetBinUpEdge(b), 5000.)
                u = math.log(math.sqrt(lo * hi) / 800.) / math.log(3000. / 800.)
                f = math.exp(a.k * u)
                up.SetBinContent(b, h.GetBinContent(b) * f); dn.SetBinContent(b, h.GetBinContent(b) / f)
            for x in (up, dn):
                if x.Integral() > 0: x.Scale(tot / x.Integral())
                do.WriteTObject(x, x.GetName())
    fo.Close(); fi.Close()

    out = []
    for l in lines:
        if l.startswith("shapes"): l = l.replace(src, dst)
        out.append(l)
    # process columns: the 'bin' / 'process' rows right after the observation block
    bins = procs = None
    for l in lines:
        t = l.split()
        if t and t[0] == "bin" and bins is None and len(t) > 13: bins = t[1:]
        if t and t[0] == "process" and procs is None and not re.match(r"^-?\d+$", t[1]): procs = t[1:]
    assert bins and procs and len(bins) == len(procs)
    # insert the two shape lines before the first rateParam line
    i = next(k for k, l in enumerate(out) if "rateParam" in l)
    for p, nuis in PROCS.items():
        out.insert(i, f"{nuis}  shape  " + "  ".join("1.0" if pr == p else "-" for pr in procs))
    open(os.path.join(a.out, "card_slope.txt"), "w").write("\n".join(out) + "\n")
    print("wrote", a.out, "K =", a.k)


if __name__ == "__main__":
    main()
