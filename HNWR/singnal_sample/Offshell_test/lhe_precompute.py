#!/home/achihwan/miniconda3/envs/hep-py-env/bin/python3
"""Compute summed LHE mass for one (WR, N) point and save to npz cache."""

import argparse
import glob
import sys
import numpy as np
import uproot
import awkward as ak
import vector

vector.register_awkward()

NANO_BASE = "/gv0/Users/achihwan/SKNano/Run3NanoAODv12/2023"
CACHE_DIR = "/data6/Users/achihwan/SKNanoAnalyzer-v13/plots/HNWR/singnal_sample/Offshell_test/lhe_cache"


def get_lhe_mass(wr, n):
    pattern = (
        f"{NANO_BASE}/WRtoNMutoMuMuJJ_MWR{wr}_N{n}_"
        f"TuneCP5_13p6TeV_madgraph-pythia8/**/*.root"
    )
    files = sorted(glob.glob(pattern, recursive=True))
    if not files:
        print(f"[WARN] No NanoAOD files found for WR{wr} N{n}", flush=True)
        return np.array([])

    print(f"Found {len(files)} file(s) for WR{wr} N{n}", flush=True)
    masses = []
    for fpath in files:
        print(f"  Reading {fpath}", flush=True)
        root_file = uproot.open(fpath)
        for chunk in root_file["Events"].iterate(
            ["LHEPart_pt", "LHEPart_eta", "LHEPart_phi", "LHEPart_mass"],
            step_size="200 MB",
            library="ak",
        ):
            p4 = ak.zip(
                {
                    "pt":   chunk["LHEPart_pt"],
                    "eta":  chunk["LHEPart_eta"],
                    "phi":  chunk["LHEPart_phi"],
                    "mass": chunk["LHEPart_mass"],
                },
                with_name="Momentum4D",
            )
            m = ak.to_numpy(ak.sum(p4, axis=1).mass)
            masses.append(m[np.isfinite(m)])

    return np.concatenate(masses) if masses else np.array([])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wr", type=int, required=True)
    parser.add_argument("--n",  type=int, required=True)
    args = parser.parse_args()

    out_path = f"{CACHE_DIR}/WR{args.wr}_N{args.n}.npz"

    mass = get_lhe_mass(args.wr, args.n)
    np.savez_compressed(out_path, mass=mass)

    n_total = len(mass)
    n_below = int(np.count_nonzero(mass < 800))
    frac    = n_below / n_total if n_total > 0 else float("nan")
    print(f"Saved {n_total} events → {out_path}", flush=True)
    print(f"LHE < 800 GeV: {n_below}/{n_total} = {frac:.2%}", flush=True)


if __name__ == "__main__":
    main()
