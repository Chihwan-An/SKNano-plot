import ROOT
import math
import numpy as np
import os
import re
import argparse

# --- 기본 설정 ---
DEFAULT_DATA_PATH = "/gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy/combined_22_23/merged/"

SCRIPT_CHANNEL = None
if "EE" in os.path.basename(__file__):
    SCRIPT_CHANNEL = "EE"
elif "MM" in os.path.basename(__file__):
    SCRIPT_CHANNEL = "MM"

BACKGROUND_GROUPS = {
    "DYJets":    "Drell-Yan",
    "TT":        "T+tW",
    "Nonprompt": "Nonprompt",
    "Others":    "Others",
}

SAMPLE_MAP = {
    "DY":     "DYJets",
    "TTLL":   "TT",
    "TTLJ":   "Nonprompt",
    "ST":     "TT",
    "WJet":   "Nonprompt",
    "ST_tch": "Nonprompt",
    "ST_sch": "Nonprompt",
}

DATA_FILES      = ["EGamma"]
EXCLUDE_SAMPLES = ["Skim", "Muon", "SingleMuon", "DYHT"]
SYST_LIST       = ["Pileup", "ElectronID", "ElectronReco", "ElectronTrig",
                   "MuonID", "MuonReco", "MuonTrig", "MuonIso", "JER", "JES"]


def get_hist_from_file(file_path, sys_dir, hist_name, x_max, custom_bins=None, rebin_factor=1):
    f = ROOT.TFile.Open(file_path)
    if not f or f.IsZombie():
        return None
    h_orig = f.Get(f"{sys_dir}/{hist_name}")
    if not h_orig:
        f.Close()
        return None
    uid = ROOT.TUUID().AsString()[:8]
    h   = h_orig.Clone(f"h_{sys_dir}_{os.path.basename(file_path).split('.')[0]}_{uid}")
    h.SetDirectory(0)
    ROOT.SetOwnership(h, False)
    if custom_bins is not None:
        bin_edges = np.array(custom_bins, dtype=float)
        h = h.Rebin(len(bin_edges)-1, h.GetName()+"_re", bin_edges)
        h.SetDirectory(0)
    elif rebin_factor > 1:
        h.Rebin(rebin_factor)
    f.Close()
    # overflow -> last bin
    last_bin = h.FindBin(min(x_max, h.GetXaxis().GetXmax()) - 0.001)
    nbins    = h.GetNbinsX()
    cont, err_sq = 0.0, 0.0
    for i in range(last_bin, nbins + 2):
        cont   += h.GetBinContent(i)
        err_sq += h.GetBinError(i)**2
        if i > last_bin:
            h.SetBinContent(i, 0)
            h.SetBinError(i, 0)
    h.SetBinContent(last_bin, cont)
    h.SetBinError(last_bin, math.sqrt(err_sq))
    return h


def load_nominal(all_files, hist_name, x_max, custom_bins, rebin_factor):
    group_hists  = {g: None for g in BACKGROUND_GROUPS}
    signal_hists = {}
    h_data       = None

    for fname in all_files:
        if any(ex in fname for ex in EXCLUDE_SAMPLES):
            continue
        fname_base = fname.replace(".root", "")
        path       = os.path.join(DEFAULT_DATA_PATH, fname)

        if fname_base.startswith("WR"):
            if SCRIPT_CHANNEL and not fname_base.endswith(SCRIPT_CHANNEL):
                continue
            h = get_hist_from_file(path, "Central", hist_name, x_max, custom_bins, rebin_factor)
            if h:
                print(f"  [SIG ] {fname:<45}: {h.Integral():.4f}")
                signal_hists[fname_base] = h
            continue

        if any(df in fname for df in DATA_FILES):
            h = get_hist_from_file(path, "Central", hist_name, x_max, custom_bins, rebin_factor)
            if h:
                print(f"  [DATA] {fname:<45}: {h.Integral():.4f}")
                if h_data is None:
                    h_data = h.Clone("h_data_total"); h_data.SetDirectory(0)
                else:
                    h_data.Add(h)
            continue

        h = get_hist_from_file(path, "Central", hist_name, x_max, custom_bins, rebin_factor)
        if h:
            matched = "Others"
            for key, group in SAMPLE_MAP.items():
                if key in fname: matched = group; break
            print(f"  [MC  ] {fname:<45}: {h.Integral():.4f}  -> {matched}")
            if group_hists[matched] is None:
                group_hists[matched] = h.Clone(f"h_group_{matched}"); group_hists[matched].SetDirectory(0)
            else:
                group_hists[matched].Add(h)

    return group_hists, signal_hists, h_data


def load_systematics(all_files, hist_name, x_max, custom_bins, rebin_factor):
    syst_hists = {}
    for syst in SYST_LIST:
        print(f"  [{syst}]", end=" ", flush=True)
        h_group_up = {g: None for g in BACKGROUND_GROUPS}
        h_group_dn = {g: None for g in BACKGROUND_GROUPS}

        for fname in all_files:
            fname_base = fname.replace(".root", "")
            if (any(ex in fname for ex in EXCLUDE_SAMPLES)
                    or any(df in fname for df in DATA_FILES)
                    or fname_base.startswith("WR")):
                continue
            matched = "Others"
            for key, group in SAMPLE_MAP.items():
                if key in fname: matched = group; break
            path = os.path.join(DEFAULT_DATA_PATH, fname)
            u = get_hist_from_file(path, f"{syst}_Up",   hist_name, x_max, custom_bins, rebin_factor)
            d = get_hist_from_file(path, f"{syst}_Down", hist_name, x_max, custom_bins, rebin_factor)
            if u:
                if h_group_up[matched] is None:
                    h_group_up[matched] = u.Clone(f"h_{syst}_up_{matched}"); h_group_up[matched].SetDirectory(0)
                else:
                    h_group_up[matched].Add(u)
            if d:
                if h_group_dn[matched] is None:
                    h_group_dn[matched] = d.Clone(f"h_{syst}_dn_{matched}"); h_group_dn[matched].SetDirectory(0)
                else:
                    h_group_dn[matched].Add(d)

        syst_hists[syst] = {}
        found = []
        for g in BACKGROUND_GROUPS:
            if h_group_up[g] and h_group_dn[g]:
                syst_hists[syst][g] = (h_group_up[g], h_group_dn[g])
                found.append(g)
        print(f"found in: {found}")

    return syst_hists


def load_signal_systematics(signal_hists, hist_name, x_max, custom_bins, rebin_factor):
    sig_syst_hists = {}
    for syst in SYST_LIST:
        sig_syst_hists[syst] = {}
        for fname_base in signal_hists.keys():
            sig_file = os.path.join(DEFAULT_DATA_PATH, fname_base + ".root")
            if not os.path.exists(sig_file):
                continue
            u = get_hist_from_file(sig_file, f"{syst}_Up",   hist_name, x_max, custom_bins, rebin_factor)
            d = get_hist_from_file(sig_file, f"{syst}_Down", hist_name, x_max, custom_bins, rebin_factor)
            if u and d:
                sig_syst_hists[syst][fname_base] = (u, d)
    return sig_syst_hists


def save_combine_root(out_path, group_hists, syst_hists,
                      signal_hists, sig_syst_hists, h_data, is_blind):
    f_out = ROOT.TFile(out_path, "RECREATE")

    # data_obs
    if not is_blind and h_data:
        h = h_data.Clone("data_obs"); h.SetDirectory(f_out); h.Write()
        print(f"  [WRITE] data_obs              integral={h_data.Integral():.4f}")
    else:
        h_asimov = None
        for g in BACKGROUND_GROUPS:
            if group_hists[g]:
                if h_asimov is None: h_asimov = group_hists[g].Clone("data_obs")
                else: h_asimov.Add(group_hists[g])
        if h_asimov:
            h_asimov.SetDirectory(f_out); h_asimov.Write()
            print(f"  [WRITE] data_obs (Asimov)     integral={h_asimov.Integral():.4f}")

    # Background nominal
    for g in BACKGROUND_GROUPS:
        if group_hists[g]:
            h = group_hists[g].Clone(g); h.SetDirectory(f_out); h.Write()
            print(f"  [WRITE] {g:<22} integral={group_hists[g].Integral():.4f}")

    # Background systematics
    for syst, group_dict in syst_hists.items():
        for g, (h_up, h_dn) in group_dict.items():
            hu = h_up.Clone(f"{g}_{syst}Up");   hu.SetDirectory(f_out); hu.Write()
            hd = h_dn.Clone(f"{g}_{syst}Down"); hd.SetDirectory(f_out); hd.Write()
        print(f"  [WRITE] {syst:<22} -> {list(group_dict.keys())}")

    # Signal nominal
    for fname_base, h_sig in signal_hists.items():
        h = h_sig.Clone(fname_base); h.SetDirectory(f_out); h.Write()
        print(f"  [WRITE] {fname_base:<30} integral={h_sig.Integral():.4f}")

    # Signal systematics
    for syst, sig_dict in sig_syst_hists.items():
        for fname_base, (h_up, h_dn) in sig_dict.items():
            hu = h_up.Clone(f"{fname_base}_{syst}Up");   hu.SetDirectory(f_out); hu.Write()
            hd = h_dn.Clone(f"{fname_base}_{syst}Down"); hd.SetDirectory(f_out); hd.Write()

    f_out.Close()
    print(f"\n>> ROOT saved: {out_path}")


def write_datacard(card_prefix, root_file, bin_name,
                   group_hists, signal_hists, syst_hists, sig_syst_hists):

    bg_names = [g for g in BACKGROUND_GROUPS if group_hists[g]]

    for sig_name in sorted(signal_hists.keys()):
        all_proc = [sig_name] + bg_names
        proc_idx = {p: i for i, p in enumerate(all_proc)}
        path     = f"{card_prefix}_{sig_name}.txt"

        def row(label, vals, w=26):
            return f"{label:<20}" + "".join(f"{v:<{w}}" for v in vals)

        lines = [
            "imax 1",
            f"jmax {len(bg_names)}",
            "kmax *",
            "-"*80,
            f"shapes * {bin_name} {os.path.basename(root_file)} $PROCESS $PROCESS_$SYSTEMATIC",
            "-"*80,
            f"bin          {bin_name}",
            "observation  -1",
            "-"*80,
            row("bin",     [bin_name] * len(all_proc)),
            row("process", all_proc),
            row("process", [str(proc_idx[p]) for p in all_proc]),
            row("rate",    ["-1"] * len(all_proc)),
            "-"*80,
            row("Lumi    lnN", ["1.018"] * len(all_proc)),
        ]

        for syst in SYST_LIST:
            vals = []
            for p in all_proc:
                if p == sig_name:
                    has = syst in sig_syst_hists and sig_name in sig_syst_hists[syst]
                else:
                    has = syst in syst_hists and p in syst_hists[syst]
                vals.append("1" if has else "-")
            lines.append(row(f"{syst:<10}shapeN2", vals))

        lines.append("* autoMCStats 0")

        with open(path, "w") as f:
            f.write("\n".join(lines) + "\n")
        print(f"  [CARD] {path}")
        print(f"         -> combine -M AsymptoticLimits {path} -n {sig_name}")


def main():
    parser = argparse.ArgumentParser(description="Combine ROOT + datacard maker")
    parser.add_argument("--hist",     type=str,   required=True)
    parser.add_argument("--output",   type=str,   required=True)
    parser.add_argument("--bins",     type=str,   default=None)
    parser.add_argument("--xmax",     type=float, default=None)
    parser.add_argument("--rebin",    type=int,   default=1)
    parser.add_argument("--bin-name", type=str,   default=None)
    parser.add_argument("--blind",    action="store_true")
    args = parser.parse_args()

    HIST_NAME    = args.hist
    CUSTOM_BINS  = [float(x) for x in args.bins.split(",")] if args.bins else None
    X_MAX        = args.xmax if args.xmax else (CUSTOM_BINS[-1] if CUSTOM_BINS else 8000)
    REBIN_FACTOR = args.rebin
    BIN_NAME     = args.bin_name if args.bin_name else args.output
    IS_BLIND     = args.blind or ("SR" in HIST_NAME.upper())

    ROOT.gROOT.SetBatch(True)
    all_files = sorted([f for f in os.listdir(DEFAULT_DATA_PATH) if f.endswith(".root")])

    print(f"\n{'='*60}")
    print(f"  Histogram : {HIST_NAME}")
    print(f"  Blind     : {IS_BLIND}")
    print(f"  Bin name  : {BIN_NAME}")
    print(f"  Output    : {args.output}")
    print(f"{'='*60}\n")

    print(">> [1/4] Loading nominal...")
    group_hists, signal_hists, h_data = load_nominal(
        all_files, HIST_NAME, X_MAX, CUSTOM_BINS, REBIN_FACTOR)

    print("\n>> [2/4] Loading background systematics...")
    syst_hists = load_systematics(
        all_files, HIST_NAME, X_MAX, CUSTOM_BINS, REBIN_FACTOR)

    print("\n>> [3/4] Loading signal systematics...")
    sig_syst_hists = load_signal_systematics(
        signal_hists, HIST_NAME, X_MAX, CUSTOM_BINS, REBIN_FACTOR)

    root_out = f"{args.output}_combine.root"
    print(f"\n>> [4/4] Writing: {root_out}")
    save_combine_root(
        out_path       = root_out,
        group_hists    = group_hists,
        syst_hists     = syst_hists,
        signal_hists   = signal_hists,
        sig_syst_hists = sig_syst_hists,
        h_data         = h_data,
        is_blind       = IS_BLIND,
    )

    print("\n>> Writing datacards...")
    write_datacard(
        card_prefix    = args.output,
        root_file      = root_out,
        bin_name       = BIN_NAME,
        group_hists    = group_hists,
        signal_hists   = signal_hists,
        syst_hists     = syst_hists,
        sig_syst_hists = sig_syst_hists,
    )

    print("\n>> Done.")


if __name__ == "__main__":
    main()