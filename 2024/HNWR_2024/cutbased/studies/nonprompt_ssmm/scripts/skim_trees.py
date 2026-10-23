#!/usr/bin/env python3
"""Skim the resolved MuMu trees of one HNWR_BDT_presel_3SR output file to a compact npz.

Only MC is ever passed (the driver never lists EGamma*/Muon* data files).
Every event of each requested tree is kept (the trees already carry mll>200); the
analysis cuts are applied downstream so the skim can be reused for every region.

  skim_trees.py --file <in.root> --trees Central_SR_MM_BDTTree_resolved,Central_SR_LL_MM_BDTTree_resolved --out <out.npz>
"""
import argparse
import os
import sys

import numpy as np
import ROOT

BASE_COLS = [
    "mu1_pt", "mu1_eta", "mu1_phi", "mu1_charge", "mu1_tkRelIso", "mu1_genPartFlav_truth", "mu1_genPartIdx_truth",
    "mu1_passLooseID", "mu1_passTightID", "mu1_isFilled",
    "mu2_pt", "mu2_eta", "mu2_phi", "mu2_charge", "mu2_tkRelIso", "mu2_genPartFlav_truth", "mu2_genPartIdx_truth",
    "mu2_passLooseID", "mu2_passTightID", "mu2_isFilled",
    "ele1_isFilled",
    "mll", "mlljj", "lepChargeProduct", "nJet", "jet1_pt", "jet2_pt", "jet1_eta", "jet2_eta",
    "nLooseLepton", "nLooseMuon", "nLooseElectron", "nTightMuon", "nTightElectron", "nLepton",
    "passTrigMuon", "channel", "weight", "weight_Central", "weight_MuonIso_Up", "weight_MuonIso_Down",
    "dR_l1_j1", "dR_l1_j2", "dR_l2_j1", "dR_l2_j2", "dRll",
]
FO_COLS = ["mu1_genOrigin", "mu1_genMatchType", "mu1_genMatchDR",
           "mu2_genOrigin", "mu2_genMatchType", "mu2_genMatchDR"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--trees", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    out = {}
    tf = ROOT.TFile.Open(a.file)
    keys = {k.GetName() for k in tf.GetListOfKeys()}
    tf.Close()
    for tree in a.trees.split(","):
        tag = tree.replace("Central_", "").replace("_BDTTree_resolved", "")
        if tree not in keys:
            print(f"[skim] {os.path.basename(a.file)}: no {tree}")
            continue
        reader = ROOT.RNTupleReader.Open(tree, a.file)
        names = {f.GetFieldName() for f in reader.GetDescriptor().GetTopLevelFields()}
        n = reader.GetNEntries()
        del reader
        cols = [c for c in BASE_COLS + FO_COLS if c in names]
        missing = [c for c in BASE_COLS if c not in names]
        if missing:
            print(f"[skim] {tree}: missing base columns {missing}")
        if n == 0:
            arr = {c: np.zeros(0) for c in cols}
        else:
            df = ROOT.RDataFrame(tree, a.file)
            arr = df.AsNumpy(cols)
        for c, v in arr.items():
            out[f"{tag}__{c}"] = np.asarray(v)
        print(f"[skim] {os.path.basename(a.file)} {tree}: {n} entries, {len(cols)} cols")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    tmp = a.out + ".tmp.npz"
    np.savez_compressed(tmp, **out)
    os.replace(tmp, a.out)
    print(f"[skim] wrote {a.out}")


if __name__ == "__main__":
    sys.exit(main())
