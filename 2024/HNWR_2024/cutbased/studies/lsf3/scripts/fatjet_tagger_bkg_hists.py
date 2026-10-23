#!/usr/bin/env python3
"""Background (DY HT-binned, TT 2L, tW 2L) counterpart of fatjet_tagger_hists.py, on the HNWR skims (2024), one chunk of files.
Per event: the highest FatJet_globalParT3_XWWqqev / _XWWqqmv over the fatjets with FatJet_lsf3 > 0.75 (-1 if none).
Weights = genWeight (the sample normalisation xsec / sumW is applied when plotting).
Output: <out>/<sample>_<chunk>.npz with genWeight-summed histograms (200 bins in [0,1], score == 1 kept in the last bin) of the
per-event max score, the genWeight sum of all events and of the events with at least one LSF3 > 0.75 fatjet.
  fatjet_tagger_bkg_hists.py --sample DYto2L-4Jets_Bin-HT-400to800-MLL-50to120 --file-list <txt> --out <dir> [--mt 4] [--test]"""
import argparse, os
import numpy as np
import ROOT

ap = argparse.ArgumentParser()
ap.add_argument("--sample", required=True)
ap.add_argument("--file-list", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--mt", type=int, default=4)
ap.add_argument("--test", action="store_true", help="first file, 50000 events, no MT, no output")
a = ap.parse_args()
ROOT.gROOT.SetBatch(True)
if a.mt > 1 and not a.test: ROOT.EnableImplicitMT(a.mt)
os.makedirs(a.out, exist_ok=True)

ROOT.gInterpreter.Declare(r'''
#include "ROOT/RVec.hxx"
using ROOT::VecOps::RVec;
// {max ev, max mv} over fatjets with lsf3 > 0.75 (-1 = none), max lsf3 over all fatjets (-1 = no fatjet)
RVec<float> fjMaxLSF(const RVec<float>& lsf, const RVec<float>& ev, const RVec<float>& mv) {
    RVec<float> out = {-1, -1, -1};
    for (size_t i = 0; i < ev.size(); ++i) {
        out[2] = std::max(out[2], lsf[i]);
        if (lsf[i] > 0.75) { out[0] = std::max(out[0], ev[i]); out[1] = std::max(out[1], mv[i]); }
    }
    return out;
}
''')

files = [l.strip() for l in open(a.file_list) if l.strip()]
if a.test: files = files[:1]
df = ROOT.RDataFrame("Events", files)
if a.test: df = df.Range(50000)
df = df.Define("w", "double(genWeight)").Define("fm", "fjMaxLSF(FatJet_lsf3, FatJet_globalParT3_XWWqqev, FatJet_globalParT3_XWWqqmv)")
dl = df.Filter("fm[0] > -0.5")
b = {"total": df.Sum("w"), "total_raw": df.Count(), "n_anylsf": dl.Sum("w"), "nraw_anylsf": dl.Count()}
for k, tag in enumerate(("XWWqqev", "XWWqqmv")):
    b[f"h_lsf_{tag}"] = dl.Define(f"s{k}", f"std::min(fm[{k}], 0.99999f)").Histo1D((f"h_{tag}", "", 200, 0., 1.), f"s{k}", "w")
# max LSF3 over all fatjets, events with >= 1 fatjet (LSF3 < 0 goes to the first bin)
da = df.Filter("nFatJet > 0")
b["n_anyfj"] = da.Sum("w")
b["h_all_lsf3"] = da.Define("lsfmax", "std::min(std::max(fm[2], 0.0f), 0.99999f)").Histo1D(("h_lsf3", "", 200, 0., 1.), "lsfmax", "w")
ROOT.RDF.RunGraphs(list(b.values()))
res = {"sample": a.sample, "nfiles": len(files)}
for k, v in b.items():
    if k.startswith("h_"):
        h = v.GetValue(); res[k] = np.array([h.GetBinContent(i) for i in range(1, 201)])
    else:
        res[k] = float(v.GetValue())
tag = os.path.basename(a.file_list)
if not a.test: np.savez(f"{a.out}/{tag}.npz", **res)
T = res["n_anylsf"]
print(f"{a.sample} [{tag}]: {res['total_raw']:.0f} events, with LSF>0.75 fatjet {res['nraw_anylsf']:.0f} "
      f"({res['n_anylsf'] / res['total'] * 100:.1f}% of sumw); of those XWWqqev>0.5 {res['h_lsf_XWWqqev'][100:].sum() / T * 100:.2f}%, "
      f"XWWqqmv>0.5 {res['h_lsf_XWWqqmv'][100:].sum() / T * 100:.2f}%", flush=True)
print("FATJET_TAGGER_BKG_HISTS_DONE")
