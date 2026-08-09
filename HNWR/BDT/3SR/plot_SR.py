import ROOT
import math
import numpy as np
import os
import sys
import argparse
import re

# ──────────────────────────────────────────────────────────────────────────────
# presel_3SR BDT ntuple → SR background(stack) + signal(line) plotter.
# Style mirrors plots/HNWR/reproduce/syst_plotter/integrated/plotter_file/year_sep/EE.py
# but reads TTrees (Central/SR_*_BDTTree_*) instead of histograms.
# MC weight: weight_Central (SF-included nominal, gen x lumi). SR is blinded → no data.
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_DATA_PATH = "/u/user/snu202527803/SKNanoOutput/presel_3SR/NoSyst/2022"

BACKGROUND_GROUPS = {
    "DYJets":    [ROOT.kYellow,   "Drell-Yan"],
    "TT":        [ROOT.kRed,      "T#bar{T}+tW"],
    "Nonprompt": [ROOT.kGreen+2,  "Nonprompt"],
    "QCD":       [ROOT.kOrange+1, "QCD (EM-enriched)"],
    "Others":    [ROOT.kBlue,     "Others"],
}

SAMPLE_MAP = {
    "DY":     "DYJets",
    "TTLL":   "TT",
    "TTLJ":   "Nonprompt",
    "ST":     "TT",
    "WJet":   "Nonprompt",
    "ST_tch": "Nonprompt",
    "ST_sch": "Nonprompt",
    # QCD_PT-*_EMEnriched, pre-skimmed by skim/ with --cuts hnwr3sr and
    # registered as Skim_HNWR3SR_QCD_PT-*. Its own group rather than a Nonprompt
    # subgroup, so the multijet contribution can be read off the stack directly.
    #
    # EM-enriched ONLY -- the muon-enriched datasets are not on the KNU storage
    # element (skim/README.md), so this constrains ELECTRON fakes. Do not read
    # the MM regions' QCD yield as a muon-fake estimate.
    "QCD":    "QCD",
}

# --split-nonprompt: Nonprompt(초록)를 구성 프로세스별로 채도 다른 초록으로 분리
# (HT bin 은 같은 프로세스이므로 합침). 색은 진한 순서 고정 매핑.
NONPROMPT_SUB_COLORS = {
    "TTLJ":             ROOT.kGreen + 3,
    "W+jets (M>120)":   ROOT.kGreen,
    "W+jets (M<120)":   ROOT.kGreen - 6,
    "Other nonprompt":  ROOT.kGreen - 9,
}


def nonprompt_subgroup(fname):
    if "TTLJ" in fname:
        return "TTLJ"
    if "WJetM0_120" in fname:
        return "W+jets (M<120)"
    if "WJetM120" in fname:
        return "W+jets (M>120)"
    return "Other nonprompt"


DATA_FILES = ["EGamma", "Muon", "SingleMuon"]
# inclusive W+jets는 HT-binned(WJetM*HT*)와 중복이므로 제외
EXCLUDE_SAMPLES = ["WJets.root", "WJets_MG.root"]

LUMI_BY_YEAR = {
    "2022":     "7.99 fb^{-1} (13.6 TeV)",
    "2022EE":   "26.68 fb^{-1} (13.6 TeV)",
    "2023":     "17.96 fb^{-1} (13.6 TeV)",
    "2023BPix": "9.68 fb^{-1} (13.6 TeV)",
}

SIGNAL_COLORS = [ROOT.kMagenta, ROOT.kCyan+1, ROOT.kOrange+7, ROOT.kSpring+5,
                 ROOT.kViolet+2, ROOT.kTeal-1]

# 기본으로 그릴 WR mass point (채널 접미사 EE/MM 은 region에서 자동 결정)
DEFAULT_SIGNAL_POINTS = ["WR2000N100", "WR2000N1100", "WR4000N100", "WR4000N2100", "WR6000N100"]

REGIONS = ["EE_resolved", "MM_resolved", "EE_boosted", "MM_boosted",
           "EE_boosted_nolep", "MM_boosted_nolep"]

_KEEPER = []


def format_signal_label(fname_base, scale):
    m = re.match(r"WR(\d+)N(\d+)(EE|MM)?", fname_base)
    if m:
        wr_tev = int(m.group(1)) / 1000.0
        n_tev  = int(m.group(2)) / 1000.0
        scale_str = f" (#times{int(scale)})" if scale != 1 else ""
        return f"WR {wr_tev:.1f} TeV N {n_tev:.1f} TeV{scale_str}"
    return fname_base


def get_tree(tfile, tree_name):
    """Central 디렉토리 안의 키 이름이 'Central/<tree>' 형태로 저장되어 있음."""
    d = tfile.Get("Central")
    if not d:
        return None
    for k in d.GetListOfKeys():
        if k.GetName().endswith(tree_name):
            return k.ReadObj()
    return None


def make_hist(tfile, tree_name, var, weight_expr, cut, bins, name):
    """트리에서 변수 히스토그램 생성 (오버플로우/언더플로우를 양끝 빈에 합산)."""
    t = get_tree(tfile, tree_name)
    if not t:
        return None
    if isinstance(bins, np.ndarray):
        h = ROOT.TH1D(name, "", len(bins) - 1, bins)
    else:
        nb, lo, hi = bins
        h = ROOT.TH1D(name, "", nb, lo, hi)
    h.Sumw2()
    ROOT.SetOwnership(h, False)
    # 일부 병합 파일의 저통계 트리에는 weight_Central 브랜치가 없음 → raw weight로 폴백
    if re.fullmatch(r"\w+", weight_expr) and not t.GetBranch(weight_expr):
        if t.GetBranch("weight"):
            print(f"     (fallback: '{weight_expr}' missing in {name.split('_')[1]}, using 'weight')")
            weight_expr = "weight"
        else:
            weight_expr = "1"
    sel = f"({weight_expr})*({cut})" if cut else f"({weight_expr})"
    # TTree::Draw는 gDirectory에서 이름으로 히스토그램을 찾으므로 Draw 후에 분리한다
    t.Draw(f"{var}>>+{name}", sel, "goff")
    h.SetDirectory(0)

    nb = h.GetNbinsX()
    # overflow → last bin
    c = h.GetBinContent(nb) + h.GetBinContent(nb + 1)
    e = math.hypot(h.GetBinError(nb), h.GetBinError(nb + 1))
    h.SetBinContent(nb, c); h.SetBinError(nb, e)
    h.SetBinContent(nb + 1, 0); h.SetBinError(nb + 1, 0)
    # underflow → first bin
    c = h.GetBinContent(1) + h.GetBinContent(0)
    e = math.hypot(h.GetBinError(1), h.GetBinError(0))
    h.SetBinContent(1, c); h.SetBinError(1, e)
    h.SetBinContent(0, 0); h.SetBinError(0, 0)
    return h


def run_plot():
    parser = argparse.ArgumentParser(description="presel_3SR BDT ntuple SR bkg+signal plotter")
    parser.add_argument("--var",          type=str, required=True,  help="브랜치 이름 또는 수식 (예: mlljj)")
    parser.add_argument("--region",       type=str, default="EE_resolved", choices=REGIONS,
                        help="SR region (트리 SR_<region 앞부분>_BDTTree_<resolved/boosted> 사용)")
    parser.add_argument("--input",        type=str, default=DEFAULT_DATA_PATH, help="ntuple 디렉토리")
    parser.add_argument("--year",         type=str, default="2022", choices=list(LUMI_BY_YEAR), help="lumi 라벨용 연도")
    parser.add_argument("--cut",          type=str, default="",     help="추가 selection (TTree::Draw 수식)")
    parser.add_argument("--nbin",         type=int, default=40)
    parser.add_argument("--xmin",         type=float, default=None)
    parser.add_argument("--xmax",         type=float, default=None)
    parser.add_argument("--bins",         type=str, default=None,   help="커스텀 빈 경계 (쉼표 구분, nbin/xmin/xmax 무시)")
    parser.add_argument("--xlabel",       type=str, default=None)
    parser.add_argument("--output",       type=str, default=None)
    parser.add_argument("--ymin",         type=float, default=1e-3)
    parser.add_argument("--ymax",         type=float, default=None)
    parser.add_argument("--logy",         action="store_false", default=True, help="Y축 로그 해제")
    parser.add_argument("--signal-scale", type=float, default=1.0,  help="시그널 라인 스케일 팩터")
    parser.add_argument("--signals",      type=str, default=",".join(DEFAULT_SIGNAL_POINTS),
                        help="쉼표 구분 WR mass point 목록, 'all'이면 채널의 모든 WR 파일")
    parser.add_argument("--weight",       type=str, default="weight_Central", help="MC weight 브랜치/수식")
    parser.add_argument("--show-sb",      action="store_true", default=False, help="빈별 S/sqrt(B) 출력")
    parser.add_argument("--split-nonprompt", action="store_true", default=False,
                        help="Nonprompt 를 구성 프로세스별 초록 채도로 분리해 쌓기")
    parser.add_argument("--data",         action="store_true", default=False,
                        help="데이터를 그려 Data/MC ratio 표시 (CR 용, blind 해제)")
    parser.add_argument("--region-label", type=str, default=None,
                        help="플롯에 표시할 region 라벨 (기본: region 이름에서 자동 생성)")
    parser.add_argument("--ratio-ymin",   type=float, default=0.5, help="ratio pad y 최소")
    parser.add_argument("--ratio-ymax",   type=float, default=1.5, help="ratio pad y 최대")
    args = parser.parse_args()

    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gErrorIgnoreLevel = ROOT.kWarning

    channel   = args.region.split("_")[0]                      # EE / MM
    tree_name = f"SR_{args.region.replace(channel + '_', channel + '_BDTTree_', 1)}"
    # SR_EE_BDTTree_resolved / SR_MM_BDTTree_boosted_nolep 형태
    LUMI_LABEL = LUMI_BY_YEAR[args.year]

    if args.bins:
        bins = np.array([float(x) for x in args.bins.split(",")], dtype=float)
        x_min, x_max = bins[0], bins[-1]
    else:
        # 범위를 안 주면 배경 전체에서 자동 결정하기 어렵지 않게 필수로 요구
        if args.xmin is None or args.xmax is None:
            print("Error: --bins 또는 --xmin/--xmax 를 지정하세요.")
            sys.exit(1)
        bins = (args.nbin, args.xmin, args.xmax)
        x_min, x_max = args.xmin, args.xmax

    out_name = args.output if args.output else f"{args.region}_{re.sub(r'[^A-Za-z0-9_]', '_', args.var)}"

    all_files = sorted(f for f in os.listdir(args.input)
                       if f.endswith(".root") and os.path.isfile(os.path.join(args.input, f)))

    sig_points = None if args.signals.strip().lower() == "all" else \
        [s.strip() for s in args.signals.split(",") if s.strip()]

    group_hists  = {g: None for g in BACKGROUND_GROUPS}
    np_sub       = {}   # --split-nonprompt 용 서브그룹 히스토그램
    signal_hists = {}
    h_data       = None

    print(f"\n>> Region: {args.region}  (tree: {tree_name}),  var: {args.var}")
    print(f">> Input : {args.input}")
    if args.data:
        print(">> DATA MODE: Data/MC ratio 표시 (CR)")
    else:
        print("!! BLIND MODE: SR data is not drawn !!")
    print("=" * 85)

    # 채널에 맞는 primary dataset 만 사용 (트리거 중복 방지)
    data_pds = ["EGamma"] if channel == "EE" else ["Muon", "SingleMuon"]

    for fname in all_files:
        # strip any skim tag, not just Skim_20002_: QCD comes in as
        # Skim_HNWR3SR_QCD_PT-*, and the display name / signal matching below
        # both assume the bare sample alias.
        base = re.sub(r"^Skim_[A-Za-z0-9]+_", "", fname.replace(".root", ""))
        path = os.path.join(args.input, fname)

        if any(df in fname for df in DATA_FILES):
            if not args.data or not any(pd in fname for pd in data_pds):
                continue
            f = ROOT.TFile.Open(path)
            if not f or f.IsZombie():
                continue
            hname = f"h_data_{base}_{ROOT.TUUID().AsString()[:8]}"
            h = make_hist(f, tree_name, args.var, "1", args.cut, bins, hname)
            f.Close()
            if not h:
                continue
            print(f"  [DATA] {base:<40}: {h.Integral():12.2f} events")
            if h_data is None:
                h_data = h.Clone("h_data"); h_data.SetDirectory(0)
                ROOT.SetOwnership(h_data, False)
            else:
                h_data.Add(h)
            continue
        if any(fname.endswith(ex) for ex in EXCLUDE_SAMPLES):
            continue

        is_signal = base.startswith("WR")
        if is_signal:
            if not base.endswith(channel):
                continue
            point = re.sub(r"(EE|MM)$", "", base)
            if sig_points is not None and point not in sig_points:
                continue

        f = ROOT.TFile.Open(path)
        if not f or f.IsZombie():
            continue
        hname = f"h_{base}_{ROOT.TUUID().AsString()[:8]}"
        h = make_hist(f, tree_name, args.var, args.weight, args.cut, bins, hname)
        f.Close()
        if not h or h.GetEntries() == 0 and h.Integral() == 0:
            continue

        if is_signal:
            print(f"  [SIG ] {base:<40}: {h.Integral():12.2f} events  (will be x{args.signal_scale})")
            signal_hists[base] = h
        else:
            matched = "Others"
            for key, grp in SAMPLE_MAP.items():
                if key in fname:
                    matched = grp; break
            if args.split_nonprompt and matched == "Nonprompt":
                sub = nonprompt_subgroup(fname)
                print(f"  [MC  ] {base:<40}: {h.Integral():12.2f} events  -> Nonprompt/{sub}")
                if sub not in np_sub:
                    np_sub[sub] = h.Clone(f"h_npsub_{sub}")
                    np_sub[sub].SetDirectory(0)
                    ROOT.SetOwnership(np_sub[sub], False)
                else:
                    np_sub[sub].Add(h)
            else:
                print(f"  [MC  ] {base:<40}: {h.Integral():12.2f} events  -> {matched}")
            if group_hists[matched] is None:
                group_hists[matched] = h.Clone(f"h_group_{matched}")
                group_hists[matched].SetDirectory(0)
                ROOT.SetOwnership(group_hists[matched], False)
            else:
                group_hists[matched].Add(h)

    h_total_mc = None
    for g in BACKGROUND_GROUPS:
        if group_hists[g]:
            if h_total_mc is None:
                h_total_mc = group_hists[g].Clone("h_total_mc"); h_total_mc.SetDirectory(0)
                ROOT.SetOwnership(h_total_mc, False)
            else:
                h_total_mc.Add(group_hists[g])
    if h_total_mc is None:
        print(f"\nError: no MC histograms loaded for '{args.var}' in {tree_name}")
        return

    print("-" * 85)
    for g in BACKGROUND_GROUPS:
        if group_hists[g]:
            print(f"  [GRP ] {g:<12}: {group_hists[g].Integral():12.2f}")
    if np_sub:
        for sub in sorted(np_sub, key=lambda s: np_sub[s].Integral(), reverse=True):
            print(f"  [NP  ]   {sub:<18}: {np_sub[sub].Integral():12.2f}")
    print(f"  [GRP ] {'Total BKG':<12}: {h_total_mc.Integral():12.2f}")
    if h_data:
        print(f"  [GRP ] {'Data':<12}: {h_data.Integral():12.2f}"
              f"  (Data/MC = {h_data.Integral()/h_total_mc.Integral():.3f})")
    print("=" * 85)

    # Stack: yield 많은 순으로 위에 쌓기 (ascending 으로 Add).
    # Nonprompt 분리 시에는 그룹 전체 yield 위치에 초록 블록을 통째로 두고,
    # 블록 안에서도 많은 서브그룹이 블록 최상단에 오도록 ascending 으로 Add.
    valid = [(g, group_hists[g].Integral()) for g in BACKGROUND_GROUPS if group_hists[g]]
    sorted_for_stack = sorted(valid, key=lambda x: x[1], reverse=False)
    stack = ROOT.THStack("stack", "")
    legend_items = []   # (hist, label) — 스택 아래→위 순서
    for g, _ in sorted_for_stack:
        if g == "Nonprompt" and np_sub:
            for sub in sorted(np_sub, key=lambda s: np_sub[s].Integral()):
                hs = np_sub[sub]
                hs.SetFillColor(NONPROMPT_SUB_COLORS[sub])
                hs.SetLineColor(NONPROMPT_SUB_COLORS[sub])
                stack.Add(hs)
                legend_items.append((hs, sub))
        else:
            h = group_hists[g]
            h.SetFillColor(BACKGROUND_GROUPS[g][0])
            h.SetLineColor(BACKGROUND_GROUPS[g][0])
            stack.Add(h)
            legend_items.append((h, BACKGROUND_GROUPS[g][1]))
    _KEEPER.extend([stack, h_total_mc])

    # Stat unc. band
    n_bins = h_total_mc.GetNbinsX()
    g_stat = ROOT.TGraphAsymmErrors(n_bins)
    for i in range(1, n_bins + 1):
        x = h_total_mc.GetBinCenter(i); y = h_total_mc.GetBinContent(i)
        w = h_total_mc.GetBinWidth(i) / 2.0; e = h_total_mc.GetBinError(i)
        g_stat.SetPoint(i - 1, x, y); g_stat.SetPointError(i - 1, w, w, e, e)
    _KEEPER.append(g_stat)

    # ── S/sqrt(B) ──
    if args.show_sb and signal_hists:
        print("\n>> Bin-by-bin S/sqrt(B)")
        print("-" * 100)
        hdr = f"{'Bin range':<20}" + "".join(f" | {re.sub(r'(EE|MM)$','',s):>16}" for s in sorted(signal_hists))
        print(hdr); print("-" * 100)
        for i in range(1, n_bins + 1):
            b = h_total_mc.GetBinContent(i)
            if b <= 0:
                continue
            rng = f"[{h_total_mc.GetBinLowEdge(i):.0f},{h_total_mc.GetBinLowEdge(i+1):.0f}]"
            line = f"{rng:<20}" + "".join(
                f" | {signal_hists[s].GetBinContent(i)/math.sqrt(b):>16.4f}" for s in sorted(signal_hists))
            print(line)
        print("-" * 100)

    # ── TSV ──
    np_sub_cols = sorted(np_sub, key=lambda s: np_sub[s].Integral(), reverse=True)
    with open(f"{out_name}.tsv", "w") as tf:
        hdr = "Bin\tBinLow\tBinHigh\tMC_Total\tDYJets\tTT\tNonprompt\tOthers"
        for sub in np_sub_cols:
            hdr += f"\tNP_{sub.replace(' ', '_')}"
        if h_data:
            hdr += "\tData"
        for s in sorted(signal_hists):
            hdr += f"\t{s}"
        tf.write(hdr + "\n")
        for i in range(1, n_bins + 1):
            row = [i, h_total_mc.GetBinLowEdge(i), h_total_mc.GetBinLowEdge(i + 1),
                   h_total_mc.GetBinContent(i)]
            row += [(group_hists[g].GetBinContent(i) if group_hists[g] else 0.0) for g in BACKGROUND_GROUPS]
            row += [np_sub[sub].GetBinContent(i) for sub in np_sub_cols]
            if h_data:
                row += [h_data.GetBinContent(i)]
            row += [signal_hists[s].GetBinContent(i) for s in sorted(signal_hists)]
            tf.write("\t".join(f"{v:.4f}" if isinstance(v, float) else str(v) for v in row) + "\n")
    print(f">> TSV saved as {out_name}.tsv")

    # ── Draw ──
    c  = ROOT.TCanvas("c", "c", 800, 900)
    p1 = ROOT.TPad("p1", "p1", 0, 0.3, 1, 1)
    p2 = ROOT.TPad("p2", "p2", 0, 0,   1, 0.3)
    _KEEPER.extend([c, p1, p2])
    p1.SetBottomMargin(0.02); p2.SetTopMargin(0.02); p2.SetBottomMargin(0.35)
    p1.Draw(); p2.Draw()

    p1.cd()
    if args.logy:
        p1.SetLogy()
    sig_max = max((h.GetMaximum() * args.signal_scale for h in signal_hists.values()), default=0)
    data_max = h_data.GetMaximum() if h_data else 0
    y_max = args.ymax if args.ymax else max(h_total_mc.GetMaximum(), sig_max, data_max) * (100 if args.logy else 1.5)

    h_dummy = h_total_mc.Clone("h_dummy"); h_dummy.Reset()
    ROOT.SetOwnership(h_dummy, False)
    h_dummy.GetYaxis().SetTitle("Events / bin")
    h_dummy.GetYaxis().SetTitleSize(0.05); h_dummy.GetYaxis().SetTitleOffset(1.1)
    h_dummy.GetXaxis().SetLabelSize(0)
    h_dummy.SetMinimum(args.ymin); h_dummy.SetMaximum(y_max)
    h_dummy.GetXaxis().SetRangeUser(x_min, x_max)
    h_dummy.Draw("HIST")

    stack.Draw("HIST SAME")
    g_stat.SetFillColorAlpha(ROOT.kGray + 2, 0.8); g_stat.SetFillStyle(3013)
    g_stat.Draw("SAME E2")

    drawn_signals = []
    for idx, (base, h_sig) in enumerate(sorted(signal_hists.items())):
        hs = h_sig.Clone(f"h_sig_scaled_{base}"); hs.SetDirectory(0)
        ROOT.SetOwnership(hs, False)
        hs.Scale(args.signal_scale)
        color = SIGNAL_COLORS[idx % len(SIGNAL_COLORS)]
        hs.SetLineColor(color); hs.SetLineWidth(3); hs.SetLineStyle(1); hs.SetFillStyle(0)
        hs.Draw("HIST SAME")
        drawn_signals.append((format_signal_label(base, args.signal_scale), hs))
        _KEEPER.append(hs)

    if h_data:
        h_data.SetMarkerStyle(20); h_data.SetMarkerSize(0.9)
        h_data.SetMarkerColor(ROOT.kBlack); h_data.SetLineColor(ROOT.kBlack)
        h_data.Draw("SAME E1 X0")

    n_leg = len(legend_items) + 1 + len(drawn_signals) + (1 if h_data else 0)
    leg = ROOT.TLegend(0.55, max(0.40, 0.88 - 0.038 * n_leg), 0.92, 0.88)
    leg.SetBorderSize(0); leg.SetFillStyle(0)
    leg.SetTextSize(0.030 if n_leg > 9 else 0.035)
    if h_data:
        leg.AddEntry(h_data, "Data", "lep")
    for h, lab in reversed(legend_items):
        leg.AddEntry(h, lab, "f")
    leg.AddEntry(g_stat, "Stat. Unc.", "f")
    for lab, hs in drawn_signals:
        leg.AddEntry(hs, lab, "l")
    leg.Draw()
    _KEEPER.append(leg)

    latex = ROOT.TLatex(); latex.SetNDC()
    latex.SetTextFont(61); latex.SetTextSize(0.045); latex.DrawLatex(0.12, 0.93, "CMS")
    latex.SetTextFont(52); latex.SetTextSize(0.035); latex.DrawLatex(0.21, 0.93, "Work in progress")
    latex.SetTextFont(42); latex.SetTextSize(0.030); latex.SetTextAlign(31)
    latex.DrawLatex(0.90, 0.93, LUMI_LABEL)
    latex.SetTextAlign(11); latex.SetTextFont(62); latex.SetTextSize(0.06)
    latex.DrawLatex(0.18, 0.82, "ee" if channel == "EE" else "#mu#mu")
    latex.SetTextFont(42); latex.SetTextSize(0.060)
    region_label = args.region_label if args.region_label else \
        args.region.replace(channel + "_", "").replace("_", " ").capitalize() + " SR"
    if len(region_label) > 14:          # 긴 라벨은 legend 와 겹치지 않게 축소
        latex.SetTextSize(0.040)
    latex.DrawLatex(0.18, 0.75, region_label)
    p1.RedrawAxis()

    # Ratio pad — 데이터 없으면 blind 문구, 있으면 Data/MC
    p2.cd()
    h_frame = h_dummy.Clone("h_frame"); h_frame.Reset()
    ROOT.SetOwnership(h_frame, False)
    h_frame.GetYaxis().SetTitle("Data / MC")
    h_frame.SetMinimum(args.ratio_ymin); h_frame.SetMaximum(args.ratio_ymax)
    h_frame.GetXaxis().SetTitle(args.xlabel if args.xlabel else args.var)
    h_frame.GetXaxis().SetTitleSize(0.1); h_frame.GetXaxis().SetLabelSize(0.11)
    h_frame.GetYaxis().SetTitleSize(0.1); h_frame.GetYaxis().SetLabelSize(0.11)
    h_frame.GetYaxis().SetTitleOffset(0.45); h_frame.GetYaxis().SetNdivisions(505)
    h_frame.GetXaxis().SetRangeUser(x_min, x_max)
    h_frame.Draw("HIST")
    if h_data:
        # MC stat unc. band (1 ± rel.err)
        g_ratio_band = ROOT.TGraphAsymmErrors(n_bins)
        for i in range(1, n_bins + 1):
            x = h_total_mc.GetBinCenter(i); w = h_total_mc.GetBinWidth(i) / 2.0
            m = h_total_mc.GetBinContent(i)
            rel = h_total_mc.GetBinError(i) / m if m > 0 else 0
            g_ratio_band.SetPoint(i - 1, x, 1.0)
            g_ratio_band.SetPointError(i - 1, w, w, rel, rel)
        g_ratio_band.SetFillColorAlpha(ROOT.kGray + 2, 0.8); g_ratio_band.SetFillStyle(3013)
        g_ratio_band.Draw("SAME E2")
        h_ratio = h_data.Clone("h_ratio"); h_ratio.SetDirectory(0)
        ROOT.SetOwnership(h_ratio, False)
        h_ratio.Divide(h_total_mc)
        h_ratio.SetMarkerStyle(20); h_ratio.SetMarkerSize(0.9)
        h_ratio.SetMarkerColor(ROOT.kBlack); h_ratio.SetLineColor(ROOT.kBlack)
        h_ratio.Draw("SAME E1 X0")
        l_one = ROOT.TLine(x_min, 1.0, x_max, 1.0)
        l_one.SetLineStyle(2); l_one.Draw("SAME")
        _KEEPER.extend([g_ratio_band, h_ratio, l_one])
    else:
        bl = ROOT.TLatex(); bl.SetNDC(); bl.SetTextAlign(22); bl.SetTextSize(0.18)
        bl.SetTextFont(62); bl.DrawLatex(0.5, 0.5, "Blinded")
        _KEEPER.append(bl)
    p2.RedrawAxis()

    c.SaveAs(f"{out_name}_plot.png")
    print(f">> Plot saved as {out_name}_plot.png")


if __name__ == "__main__":
    run_plot()
