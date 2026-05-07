import ROOT
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
import csv
import argparse

# ---- Default configuration ----
DEFAULT_ROOT_PATH = "/gv0/Users/achihwan/SKNanoRunlog/2026_02_06_202448_Reproduce20_002/2023/WRtoNEltoElElJJ_MWR4000_N2100/output/hists_0.root"
DEFAULT_DIR = "Central"

HIST_CONFIGS = {
    "Cutflow_for_Boosted_SR": {
        "title": "Cutflow for Boosted SR",
        "labels": {
            1: "Total",
            2: "Met filter",
            3: "! 4 object resolved",
            4: "Lead lep tight, pt, eta, id, iso",
            5: "Trigger",
            6: "! m(ll) 60~150",
            7: "fatjet pt eta sdm, dphi",
            8: "no more tight lep",
            9: "loose lep in fatjet pt eta pt eta ",
            10: "no of loose lep in fatjet ",
            11: "m(ll)> 200",
            12: "M(llJ) > 800",
        },
    },
    "Cutflow_for_reseolved_SR": {
        "title": "Cutflow for Resolved SR",
        "labels": {
            1: "Total",
            2: "Met filter",
            3: "2 tight lep, pt,eta,id,iso",
            4: "Trigger pass",
            5: "Jet >=2 , pt ,eta",
            6: "4 object separation",
            7: "m(ll) > 200",
            8: "WR mass 800",
            9: "m(ll) > 400",
        },
    },
}


def load_cutflow(root_path, dir_name, hist_name):
    """Load cutflow histogram and return bin numbers and values."""
    f = ROOT.TFile.Open(root_path)
    if not f or f.IsZombie():
        raise FileNotFoundError(f"Cannot open {root_path}")

    h = f.Get(f"{dir_name}/{hist_name}")
    if not h:
        f.Close()
        raise KeyError(f"Histogram '{dir_name}/{hist_name}' not found")

    nbins = h.GetNbinsX()
    all_bins = list(range(1, nbins + 1))
    all_values = [h.GetBinContent(i) for i in all_bins]
    f.Close()

    # Skip leading zero-value bins (e.g. empty "Initial" bin)
    start = 0
    for i, v in enumerate(all_values):
        if v > 0:
            start = i
            break
    bins = list(range(1, len(all_values) - start + 1))
    values = all_values[start:]
    return bins, values


def compute_reduction(values):
    """Compute percentage reduction between consecutive bins.
    reduction[i] = (values[i] - values[i+1]) / values[i] * 100
    Returns lists of same length as values; first entry is 0 (no previous bin).
    """
    reduction = [0.0]  # no reduction for the first bin
    for i in range(len(values) - 1):
        if values[i] > 0:
            red = (values[i] - values[i + 1]) / values[i] * 100.0
        else:
            red = 0.0
        reduction.append(red)
    return reduction


def compute_survival(values):
    """Compute percentage survival between consecutive bins.
    survival[i] = values[i+1] / values[i] * 100
    Returns lists of same length as values; first entry is 100 (no previous bin).
    """
    survival = [100.0]  # 100% survival for the first bin
    for i in range(len(values) - 1):
        if values[i] > 0:
            surv = (values[i + 1] / values[i]) * 100.0
        else:
            surv = 0.0
        survival.append(surv)
    return survival


def plot_single_cutflow(ax_top, ax_bot, bins, values, reduction, survival, config):
    """Draw cutflow, reduction, and survival on the given axes pair."""
    labels = config.get("labels", {})
    title = config.get("title", "Cutflow")

    x = np.array(bins)
    y = np.array(values)
    red = np.array(reduction)
    surv = np.array(survival)

    # Reference value for percentage: first non-zero bin
    y_nonzero = y[y > 0]
    y_ref = y_nonzero[0] if len(y_nonzero) > 0 else 1.0

    # -- Top panel: cutflow values --
    ax_top.bar(x, y, color="steelblue", edgecolor="navy", alpha=0.85, width=0.6)
    for xi, yi in zip(x, y):
        if yi > 0:
            pct = yi / y_ref * 100.0
            ax_top.text(xi, yi * 1.03, f"{yi:.0f}\n({pct:.1f}%)",
                        ha="center", va="bottom", fontsize=6.5, rotation=45)
    ax_top.set_ylabel("Events", fontsize=12)
    ax_top.set_title(title, fontsize=14, fontweight="bold")
    ax_top.set_yscale("log")
    ax_top.set_ylim(bottom=max(1, min(y[y > 0]) * 0.3) if np.any(y > 0) else 1,
                     top=max(y) * 15)
    ax_top.set_xlim(x[0] - 0.5, x[-1] + 0.5)
    ax_top.xaxis.set_major_locator(ticker.FixedLocator(x))
    ax_top.set_xticklabels([])  # hide x labels on top panel

    # -- Bottom panel: reduction and survival percentages --
    # Bar plot for reduction
    colors = ["gray" if r == 0 else ("tomato" if r > 0 else "limegreen") for r in red]
    ax_bot.bar(x, red, color=colors, edgecolor="black", alpha=0.6, width=0.6, label="Reduction")

    # Line plot for survival with markers
    ax_bot_twin = ax_bot.twinx()
    ax_bot_twin.plot(x, surv, color="green", marker="o", linewidth=2, markersize=6,
                     alpha=0.8, label="Survival", zorder=10)

    # Annotations for reduction
    for xi, ri in zip(x, red):
        if ri != 0:
            ax_bot.text(xi - 0.15, ri + (1.5 if ri >= 0 else -3.5), f"{ri:.1f}%",
                        ha="center", va="bottom" if ri >= 0 else "top", fontsize=6.5,
                        rotation=45, color="darkred")

    # Annotations for survival
    for xi, si in zip(x, surv):
        if si < 100:  # Skip first bin (always 100%)
            ax_bot_twin.text(xi + 0.15, si + 2, f"{si:.1f}%",
                            ha="center", va="bottom", fontsize=6.5, rotation=45, color="darkgreen")

    ax_bot.set_ylabel("Reduction (%)", fontsize=12, color="darkred")
    ax_bot_twin.set_ylabel("Survival (%)", fontsize=12, color="darkgreen")
    ax_bot.set_xlabel("Cut step", fontsize=12)
    ax_bot.set_xlim(x[0] - 0.5, x[-1] + 0.5)
    ax_bot.xaxis.set_major_locator(ticker.FixedLocator(x))
    tick_labels = [labels.get(b, str(b)) for b in bins]
    ax_bot.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=8)
    ax_bot.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax_bot.set_ylim(-5, 105)
    ax_bot_twin.set_ylim(-5, 105)
    ax_bot.tick_params(axis='y', labelcolor="darkred")
    ax_bot_twin.tick_params(axis='y', labelcolor="darkgreen")

    # Add legend
    lines1, labels1 = ax_bot.get_legend_handles_labels()
    lines2, labels2 = ax_bot_twin.get_legend_handles_labels()
    ax_bot.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=9)


def main():
    parser = argparse.ArgumentParser(description="Cutflow plotter for Boosted and Resolved SR")
    parser.add_argument("--input", type=str, default=DEFAULT_ROOT_PATH, help="Input ROOT file path")
    parser.add_argument("--dir", type=str, default=DEFAULT_DIR, help="TDirectory name inside ROOT file")
    parser.add_argument("--output", type=str, default="Cutflow_SR", help="Output file name (without extension)")
    args = parser.parse_args()

    ROOT.gROOT.SetBatch(True)

    # Select which cutflows to plot based on the input path
    input_path = args.input
    if "N100" in input_path:
        selected = {"Cutflow_for_Boosted_SR": HIST_CONFIGS["Cutflow_for_Boosted_SR"]}
        print(">> Detected 'N100' in path -> Boosted SR only")
    elif "2100" in input_path:
        selected = {"Cutflow_for_reseolved_SR": HIST_CONFIGS["Cutflow_for_reseolved_SR"]}
        print(">> Detected '2100' in path -> Resolved SR only")
    elif "1100" in input_path:
        selected = {"Cutflow_for_reseolved_SR": HIST_CONFIGS["Cutflow_for_reseolved_SR"]}
        print(">> Detected '1100' in path -> Resolved SR only")
    else:
        selected = HIST_CONFIGS
        print(">> Plotting both Boosted and Resolved SR")

    ncols = len(selected)
    fig, axes = plt.subplots(2, ncols, figsize=(10 * ncols, 10),
                             gridspec_kw={"height_ratios": [3, 1.5], "hspace": 0.05, "wspace": 0.3},
                             squeeze=False)

    for col, (hist_name, config) in enumerate(selected.items()):
        print(f"Loading: {hist_name}")
        bins, values = load_cutflow(args.input, args.dir, hist_name)
        reduction = compute_reduction(values)
        survival = compute_survival(values)

        # Print table
        labels = config.get("labels", {})
        ref_val = next((v for v in values if v > 0), 1.0)
        print(f"\n{'Bin':>4}  {'Label':<25}  {'Events':>12}  {'% of Total':>12}  {'Reduction (%)':>15}  {'Survival (%)':>14}")
        print("-" * 98)
        for b, v, r, s in zip(bins, values, reduction, survival):
            lbl = labels.get(b, str(b))
            pct = v / ref_val * 100.0 if ref_val > 0 else 0.0
            print(f"{b:>4}  {lbl:<25}  {v:>12.0f}  {pct:>11.1f}%  {r:>14.1f}%  {s:>13.1f}%")
        print()

        plot_single_cutflow(axes[0, col], axes[1, col], bins, values, reduction, survival, config)

        # Save CSV
        csv_name = f"{args.output}_{config['title'].replace(' ', '_')}.csv"
        with open(csv_name, "w", newline="") as csvf:
            writer = csv.writer(csvf)
            writer.writerow(["Bin", "Cut", "Events", "% of Total", "Reduction (%)", "Survival (%)"])
            for b, v, r, s in zip(bins, values, reduction, survival):
                lbl = labels.get(b, str(b))
                pct = v / ref_val * 100.0 if ref_val > 0 else 0.0
                writer.writerow([b, lbl, int(v), f"{pct:.1f}", f"{r:.1f}", f"{s:.1f}"])
        print(f">> CSV saved: {csv_name}")

    # Add sample label
    sample_name = os.path.basename(os.path.dirname(os.path.dirname(args.input)))
    fig.suptitle(f"Signal Cutflow  —  {sample_name}", fontsize=16, fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    out_pdf = f"{args.output}.pdf"
    out_png = f"{args.output}.png"
    fig.savefig(out_pdf, dpi=150, bbox_inches="tight")
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    print(f">> Saved: {out_pdf}")
    print(f">> Saved: {out_png}")
    plt.close(fig)


if __name__ == "__main__":
    main()
