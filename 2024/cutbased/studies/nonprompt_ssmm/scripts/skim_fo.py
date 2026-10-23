#!/usr/bin/env python3
"""Skim the HNWR FOMode RNTuple (Central/FO_MM_resolved) of one MC output file to npz,
together with the integrals of the standard resolved SR MM mlljj histograms of the same
file (for the event-level validation iso-TT == HNWR SR).

  skim_fo.py --file <HNWR FOMode output.root> --out <out.npz>
  skim_fo.py --allow-data ...   # FOMode,FODYCR production (DY CR window only; data allowed)
"""
import argparse
import os
import sys

import numpy as np
import ROOT

TREE = "Central_FO_MM_resolved"
HISTS = ["SR_Resolved_MM_SS", "SR_Resolved_MM_OS", "SR_Resolved_MM", "DYCR_Resolved_MM"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="merged sample file")
    ap.add_argument("--glob", help="per-job files of one sample (summed), used before the DAG hadd")
    ap.add_argument("--out", required=True)
    ap.add_argument("--allow-data", action="store_true",
                    help="FODYCR production: the data FO tree holds only the DY CR window")
    a = ap.parse_args()
    import glob as _g
    files = sorted(_g.glob(a.glob)) if a.glob else [a.file]
    base = os.path.basename(a.out)
    if not a.allow_data and base.startswith(("Skim_HNWR_EGamma", "Skim_HNWR_Muon", "EGamma", "Muon")):
        print(f"refusing data sample {base}")
        return 2
    out = {}
    keys = set()
    tree_files, n = [], 0
    for fn in files:
        tf = ROOT.TFile.Open(fn)
        fk = {k.GetName() for k in tf.GetListOfKeys()}
        keys |= fk
        for h in HISTS:
            obj = tf.Get(f"Central/{h}_mlljj")
            if obj:
                nb = obj.GetNbinsX()
                c = np.array([obj.GetBinContent(i) for i in range(0, nb + 2)])
                e2 = np.array([obj.GetBinError(i) ** 2 for i in range(0, nb + 2)])
                k = f"hist__{h}_mlljj"
                out[k] = out.get(k, 0) + c
                out[k + "__err2"] = out.get(k + "__err2", 0) + e2
                out[k + "__edges"] = np.array([obj.GetXaxis().GetBinLowEdge(i) for i in range(1, nb + 2)])
        tf.Close()
        if TREE in fk:
            r = ROOT.RNTupleReader.Open(TREE, fn)
            cols = [f.GetFieldName() for f in r.GetDescriptor().GetTopLevelFields()]
            ne = r.GetNEntries()
            del r
            if ne > 0:
                tree_files.append(fn); n += ne
    print(f"[skim_fo] {base}: {len(files)} input files")
    if TREE in keys:
        if n > 0:
            v = ROOT.std.vector("std::string")()
            for fn in tree_files:
                v.push_back(fn)
            arr = ROOT.RDataFrame(TREE, v).AsNumpy(cols)
            for c, v in arr.items():
                out[f"FO__{c}"] = np.asarray(v)
        else:
            for c in cols:
                out[f"FO__{c}"] = np.zeros(0)
        print(f"[skim_fo] {base}: {n} FO entries")
    else:
        print(f"[skim_fo] {base}: no {TREE}")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    tmp = a.out + ".tmp.npz"
    np.savez_compressed(tmp, **out)
    os.replace(tmp, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
