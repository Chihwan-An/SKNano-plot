#!/usr/bin/env python3
"""GlobalParT3 XWW(qq l nu) scores in the W_R signal skims (2024), per mass point -- pass rates only, no region selection.
Per event: the highest FatJet_globalParT3_XWWqqev and the highest _XWWqqmv over all AK8 fatjets of the event ("all"), and the same
over the fatjets with FatJet_lsf3 > 0.75 ("LSF>0.75"); events without such a fatjet get -1. Denominator = all events of the
HNWR3SR skim (skim preselection only). Counts are genWeight-sign sums.
Output per point: <out>/<CH>_MWR<m>_N<n>.npz: histograms of the per-event max score (200 bins in [0,1], score == 1 kept in the last
bin), for all / LSF>0.75, plus the event counts (total, with any fatjet, with any LSF>0.75 fatjet).
  fatjet_tagger_hists.py --points EE:4000:200,MM:4000:200,... --out <dir> [--mt 4] [--test]"""
import argparse, glob, os
import numpy as np
import ROOT

ap = argparse.ArgumentParser()
ap.add_argument("--points", required=True, help="comma list CH:MWR:MN (CH = EE or MM)")
ap.add_argument("--skim-dir", default="/gv0/Users/achihwan/SkimNano15/2024")
ap.add_argument("--out", required=True)
ap.add_argument("--mt", type=int, default=4)
ap.add_argument("--test", action="store_true", help="first 20000 events of each point, no MT, no output")
a = ap.parse_args()
ROOT.gROOT.SetBatch(True)
if a.mt > 1 and not a.test: ROOT.EnableImplicitMT(a.mt)
os.makedirs(a.out, exist_ok=True)

ROOT.gInterpreter.Declare(r'''
#include "ROOT/RVec.hxx"
using ROOT::VecOps::RVec;
// {max ev (all), max mv (all), max ev (lsf3 > 0.75), max mv (lsf3 > 0.75), max lsf3 (all)}; -1 = no such fatjet
RVec<float> fjMax(const RVec<float>& lsf, const RVec<float>& ev, const RVec<float>& mv) {
    RVec<float> out = {-1, -1, -1, -1, -1};
    for (size_t i = 0; i < ev.size(); ++i) {
        out[0] = std::max(out[0], ev[i]); out[1] = std::max(out[1], mv[i]); out[4] = std::max(out[4], lsf[i]);
        if (lsf[i] > 0.75) { out[2] = std::max(out[2], ev[i]); out[3] = std::max(out[3], mv[i]); }
    }
    return out;
}
''')

TAG = {"EE": "WRtoNEltoElElJJ", "MM": "WRtoNMutoMuMuJJ"}
NB = 200
COLS = {("all", "XWWqqev"): 0, ("all", "XWWqqmv"): 1, ("lsf", "XWWqqev"): 2, ("lsf", "XWWqqmv"): 3}
books = []
for p in a.points.split(","):
    ch, mwr, mn = p.split(":")
    files = sorted(glob.glob(f"{a.skim_dir}/Skim_HNWR3SR_{TAG[ch]}_MWR{mwr}_N{mn}/tree_*.root"))
    if not files: print(f"!! no files for {p}", flush=True); continue
    df = ROOT.RDataFrame("Events", files)
    if a.test: df = df.Range(20000)
    df = df.Define("w", "genWeight > 0 ? 1.0 : -1.0").Define("fm", "fjMax(FatJet_lsf3, FatJet_globalParT3_XWWqqev, FatJet_globalParT3_XWWqqmv)")
    b = {"total": df.Sum("w"), "total_raw": df.Count(), "n_anyfj": df.Filter("nFatJet > 0").Sum("w"), "n_anylsf": df.Filter("fm[2] > -0.5").Sum("w")}
    for (sel, tag), k in COLS.items():
        # clamp score == 1 into the last bin
        b[f"h_{sel}_{tag}"] = df.Define(f"s_{sel}_{tag}", f"fm[{k}] < 0 ? -1.0f : std::min(fm[{k}], 0.99999f)") \
                                .Histo1D((f"h_{p}_{sel}_{tag}", "", NB, 0., 1.), f"s_{sel}_{tag}", "w")
    # max LSF3 over all fatjets, events with >= 1 fatjet (LSF3 < 0, i.e. no lepton found, goes to the first bin)
    b["h_all_lsf3"] = df.Filter("nFatJet > 0").Define("lsfmax", "std::min(std::max(fm[4], 0.0f), 0.99999f)").Histo1D((f"h_{p}_lsf3", "", NB, 0., 1.), "lsfmax", "w")
    books.append((ch, mwr, mn, b))

ROOT.RDF.RunGraphs([v for *_, b in books for v in b.values()])
for ch, mwr, mn, b in books:
    res = {"edges": np.linspace(0, 1, NB + 1)}
    for k, v in b.items():
        if k.startswith("h_"):
            h = v.GetValue(); res[k] = np.array([h.GetBinContent(i) for i in range(1, NB + 1)])
        else:
            res[k] = float(v.GetValue())
    if not a.test: np.savez(f"{a.out}/{ch}_MWR{mwr}_N{mn}.npz", **res)
    T = res["total"]
    def eff(h, cut): return h[int(round(cut * NB)):].sum() / T
    print(f"{ch} MWR{mwr} N{mn}: events {T:.0f}, with fatjet {res['n_anyfj'] / T * 100:.1f}%, with LSF>0.75 fatjet {res['n_anylsf'] / T * 100:.1f}%; "
          f"pass XWWqqev>0.5 all {eff(res['h_all_XWWqqev'], 0.5) * 100:.1f}% / LSF {eff(res['h_lsf_XWWqqev'], 0.5) * 100:.1f}%, "
          f"XWWqqmv>0.5 all {eff(res['h_all_XWWqqmv'], 0.5) * 100:.1f}% / LSF {eff(res['h_lsf_XWWqqmv'], 0.5) * 100:.1f}%", flush=True)
print("FATJET_TAGGER_HISTS_DONE")
