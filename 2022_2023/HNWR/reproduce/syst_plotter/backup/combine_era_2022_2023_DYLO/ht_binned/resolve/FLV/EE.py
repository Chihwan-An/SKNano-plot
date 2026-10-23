import ROOT
import math
import numpy as np
import os
import sys
import argparse
import ctypes
import re

# --- 1. 기본 설정 (인자가 없을 경우 사용됨) ---
DEFAULT_DATA_PATH = "/gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy/combined_22_23/merged/"
DEFAULT_HIST_NAME = "Obj_PU_Corr_DYCR_Resolved_EE_pt"

# 스크립트 이름으로 채널 자동 감지 (EE.py → "EE", MM.py → "MM")
SCRIPT_CHANNEL = None
if "EE" in os.path.basename(__file__):
    SCRIPT_CHANNEL = "EE"
elif "MM" in os.path.basename(__file__):
    SCRIPT_CHANNEL = "MM"

# 샘플 그룹 및 매핑 설정
BACKGROUND_GROUPS = {
    "DYJets": [ROOT.kYellow, "Drell-Yan"],
    "TT": [ROOT.kRed, "t#bar{t}(lep)+tW"],
    "Nonprompt": [ROOT.kGreen+2, "Nonprompt"],
    "Others": [ROOT.kBlue, "Others"]
}

SAMPLE_MAP = {
    "DY": "DYJets",
    "TTLL": "TT",
    "TTLJ": "Nonprompt",
    "ST": "TT",
    "WJet": "Nonprompt",
    "ST_tch": "Nonprompt",
    "ST_sch": "Nonprompt"
}

DATA_FILES = ["EGamma"]
EXCLUDE_SAMPLES = ["Skim", "Muon", "SingleMuon", "DYHT"]
SYST_LIST = ["Pileup", "ElectronID", "ElectronReco", "ElectronTrig",
             "MuonID", "MuonReco", "MuonTrig", "MuonIso", "JER", "JES"]

# 시그널 선 색상 목록 (여러 WR 샘플 대응)
SIGNAL_COLORS = [ROOT.kMagenta, ROOT.kCyan+1, ROOT.kOrange+7, ROOT.kSpring+5,
                 ROOT.kViolet+2, ROOT.kTeal-1]

# 메모리 누수 방지용
_KEEPER = []

try:
    import cmsstyle as CMS
    CMS_STYLE = True
except:
    CMS_STYLE = False


def format_signal_label(fname_base, scale):
    """
    'WR4000N2100EE' -> 'WR 4.0 TeV N 2.1 TeV (x10)'
    """
    m = re.match(r"WR(\d+)N(\d+)(EE|MM)?", fname_base)
    if m:
        wr_tev = int(m.group(1)) / 1000.0
        n_tev  = int(m.group(2)) / 1000.0
        scale_int = int(scale)
        scale_str = f" (#times{scale_int})" if scale != 1 else ""
        return f"WR {wr_tev:.1f} TeV N {n_tev:.1f} TeV{scale_str}"
    return fname_base


def get_hist_from_file(file_path, sys_dir, hist_name, x_max, custom_bins=None, rebin_factor=1):
    """파일에서 히스토그램 로드 및 전처리 (오버플로우 포함)"""
    f = ROOT.TFile.Open(file_path)
    if not f or f.IsZombie():
        return None

    h_orig = f.Get(f"{sys_dir}/{hist_name}")
    if not h_orig:
        f.Close()
        return None

    h_name = f"h_{sys_dir}_{os.path.basename(file_path).split('.')[0]}_{ROOT.TUUID().AsString()[:8]}"
    h = h_orig.Clone(h_name)
    h.SetDirectory(0)
    ROOT.SetOwnership(h, False)

    # 리빈 로드 (커스텀 빈 우선 적용)
    if custom_bins is not None:
        bin_edges = np.array(custom_bins, dtype=float)
        h_new = h.Rebin(len(bin_edges)-1, h.GetName() + "_re", bin_edges)
        h = h_new
        h.SetDirectory(0)
    elif rebin_factor > 1:
        h.Rebin(rebin_factor)

    f.Close()

    # 마지막 빈에 x_max 이후의 모든 값(오버플로우 포함) 합산
    h_xmax = h.GetXaxis().GetXmax()
    actual_xmax = min(x_max, h_xmax)

    last_bin = h.FindBin(actual_xmax - 0.001)
    nbins = h.GetNbinsX()
    cont, err_sq = 0, 0
    for i in range(last_bin, nbins + 2):
        cont += h.GetBinContent(i)
        err_sq += h.GetBinError(i)**2
        if i > last_bin:
            h.SetBinContent(i, 0); h.SetBinError(i, 0)
    h.SetBinContent(last_bin, cont)
    h.SetBinError(last_bin, math.sqrt(err_sq))

    return h


def run_plot():
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="명령줄 인자를 사용한 시스테마틱 플랏 스크립트")
    parser.add_argument("--hist",         type=str,   default=DEFAULT_HIST_NAME, help="불러올 히스토그램 이름")
    parser.add_argument("--rebin",        type=int,   default=1,                 help="리빈(Rebin) 수치")
    parser.add_argument("--output",       type=str,   default=None,              help="결과물 파일 이름")
    parser.add_argument("--ymin",         type=float, default=5.0,               help="Y축 최소값")
    parser.add_argument("--ymax",         type=float, default=None,              help="Y축 최대값")
    parser.add_argument("--xmin",         type=float, default=None,              help="X축 최소 범위")
    parser.add_argument("--xmax",         type=float, default=None,              help="X축 최대 범위")
    parser.add_argument("--bins",         type=str,   default=None,              help="커스텀 빈 (쉼표 구분)")
    parser.add_argument("--xlabel",       type=str,   default=None,              help="X축 제목 라벨")
    parser.add_argument("--logy",         action="store_false", default=True,    help="Y축 로그 스케일 해제")
    parser.add_argument("--rmin",         type=float, default=0.5,               help="Ratio 패널 Y축 최소값")
    parser.add_argument("--rmax",         type=float, default=1.5,               help="Ratio 패널 Y축 최대값")
    parser.add_argument("--signal-scale", type=float, default=1.0,              help="Signal(WR) 히스토그램에 곱할 스케일 팩터 (기본값: 10)")
    args = parser.parse_args()

    HIST_NAME    = args.hist
    IS_BLIND     = "SR" in HIST_NAME.upper()
    REBIN_FACTOR = args.rebin
    Y_LOG        = args.logy

    CUSTOM_BINS = [float(x) for x in args.bins.split(",")] if args.bins else None

    X_MIN_REQ = args.xmin if args.xmin is not None else (CUSTOM_BINS[0]  if CUSTOM_BINS else 40)
    X_MAX_REQ = args.xmax if args.xmax is not None else (CUSTOM_BINS[-1] if CUSTOM_BINS else 2000)

    PLOT_OUT_NAME = args.output if args.output else HIST_NAME

    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptStat(0)

    h_data       = None
    group_hists  = {g: None for g in BACKGROUND_GROUPS}
    signal_hists = {}   # { fname_base: TH1 }
    all_files    = sorted([f for f in os.listdir(DEFAULT_DATA_PATH) if f.endswith(".root")])

    print(f"\n>> Loading Central histograms for: {HIST_NAME}")
    if IS_BLIND:
        print("!! BLIND MODE ACTIVATED (SR detected in histogram name) !!")
    if SCRIPT_CHANNEL:
        print(f">> Channel filter active: only WR files ending with '{SCRIPT_CHANNEL}' will be loaded")
    print("="*85)

    for fname in all_files:
        if any(ex in fname for ex in EXCLUDE_SAMPLES):
            continue

        fname_base = fname.replace(".root", "")
        path       = os.path.join(DEFAULT_DATA_PATH, fname)

        # ── WR 시그널 파일 처리 ──────────────────────────────────────────
        if fname_base.startswith("WR"):
            # 채널 필터: EE.py → WR...EE 만, MM.py → WR...MM 만 사용
            if SCRIPT_CHANNEL and not fname_base.endswith(SCRIPT_CHANNEL):
                continue
            h = get_hist_from_file(path, "Central", HIST_NAME, X_MAX_REQ, CUSTOM_BINS, REBIN_FACTOR)
            if h:
                print(f"  [SIG ] {fname:<40}: {h.Integral():12.2f} events  (will be x{args.signal_scale})")
                signal_hists[fname_base] = h
            continue   # 배경/데이터 처리로 넘어가지 않음
        # ─────────────────────────────────────────────────────────────────

        is_data_file = any(df in fname for df in DATA_FILES)
        tag = "[DATA]" if is_data_file else "[MC  ]"

        h = get_hist_from_file(path, "Central", HIST_NAME, X_MAX_REQ, CUSTOM_BINS, REBIN_FACTOR)

        if h:
            print(f"  {tag} {fname:<40}: {h.Integral():12.2f} events")
            if is_data_file:
                if h_data is None:
                    h_data = h.Clone("h_data_total"); h_data.SetDirectory(0)
                else:
                    h_data.Add(h)
            else:
                matched_group = "Others"
                for key, group in SAMPLE_MAP.items():
                    if key in fname: matched_group = group; break
                if group_hists[matched_group] is None:
                    group_hists[matched_group] = h.Clone(f"h_group_{matched_group}")
                    group_hists[matched_group].SetDirectory(0)
                else:
                    group_hists[matched_group].Add(h)

    # 전체 MC 합계 생성
    h_total_mc = None
    for g_key in BACKGROUND_GROUPS:
        if group_hists[g_key]:
            if h_total_mc is None:
                h_total_mc = group_hists[g_key].Clone("h_total_mc_nominal"); h_total_mc.SetDirectory(0)
            else:
                h_total_mc.Add(group_hists[g_key])

    if h_total_mc is None:
        print(f"\nError: No MC histograms were loaded for '{HIST_NAME}'.")
        return

    h_xmin = h_total_mc.GetXaxis().GetXmin()
    h_xmax = h_total_mc.GetXaxis().GetXmax()
    X_MIN  = max(X_MIN_REQ, h_xmin)
    X_MAX  = min(X_MAX_REQ, h_xmax)

    # Stack 생성
    valid_groups      = [(g, group_hists[g].Integral()) for g in BACKGROUND_GROUPS if group_hists[g]]
    sorted_for_stack = sorted(valid_groups, key=lambda x: x[1], reverse=False)    
    stack = ROOT.THStack("stack", "")
    for g_key, yield_val in sorted_for_stack:
        h = group_hists[g_key]
        h.SetFillColor(BACKGROUND_GROUPS[g_key][0])
        h.SetLineColor(BACKGROUND_GROUPS[g_key][0])
        stack.Add(h)

    _KEEPER.extend([stack, h_total_mc, h_data])

    # 시스테마틱 계산
    print(">> Calculating Systematic Uncertainties (MC only)...")
    n_bins     = h_total_mc.GetNbinsX()
    sum_sq_up  = np.zeros(n_bins + 2)
    sum_sq_dn  = np.zeros(n_bins + 2)

    syst_per_bin = {syst: np.zeros(n_bins + 2) for syst in SYST_LIST}

    for syst in SYST_LIST:
        h_mc_up, h_mc_dn = None, None
        for fname in all_files:
            fname_base = fname.replace(".root", "")
            # WR 시그널, EXCLUDE, DATA 제외
            if (any(ex in fname for ex in EXCLUDE_SAMPLES)
                    or any(df in fname for df in DATA_FILES)
                    or fname_base.startswith("WR")):
                continue
            path = os.path.join(DEFAULT_DATA_PATH, fname)
            u = get_hist_from_file(path, f"{syst}_Up",   HIST_NAME, X_MAX, CUSTOM_BINS, REBIN_FACTOR)
            d = get_hist_from_file(path, f"{syst}_Down", HIST_NAME, X_MAX, CUSTOM_BINS, REBIN_FACTOR)
            if u:
                if h_mc_up is None: h_mc_up = u.Clone("h_up"); h_mc_up.SetDirectory(0)
                else: h_mc_up.Add(u)
            if d:
                if h_mc_dn is None: h_mc_dn = d.Clone("h_dn"); h_mc_dn.SetDirectory(0)
                else: h_mc_dn.Add(d)

        if h_mc_up and h_mc_dn:
            for i in range(1, n_bins + 1):
                nom      = h_total_mc.GetBinContent(i)
                diff_up  = h_mc_up.GetBinContent(i) - nom
                diff_dn  = h_mc_dn.GetBinContent(i) - nom
                max_diff = max(abs(diff_up), abs(diff_dn))
                syst_per_bin[syst][i] = (max_diff / nom * 100) if nom > 0 else 0
                sum_sq_up[i] += max(0, diff_up, diff_dn)**2
                sum_sq_dn[i] += max(0, -diff_up, -diff_dn)**2

    # --- 에러 및 데이터 요약 목록 출력 ---
    print("\n>> Bin-by-bin Uncertainty & Data Summary")
    print("="*160)
    print(f"{'Bin':<4} | {'Range':<18} | {'Yield(MC)':<10} | {'Data':<10} | {'Stat(%)':<8} | {'SystUp(%)':<9} | {'SystDn(%)':<9} | {'TotalUp(%)':<9} | {'TotalDn(%)':<9}")
    print("-" * 160)

    g_syst       = ROOT.TGraphAsymmErrors(n_bins)
    g_ratio_band = ROOT.TGraphAsymmErrors(n_bins)
    g_ratio_stat = ROOT.TGraphAsymmErrors(n_bins)
    _KEEPER.extend([g_syst, g_ratio_band, g_ratio_stat])

    csv_rows = []
    for i in range(1, n_bins + 1):
        x, y, w = h_total_mc.GetBinCenter(i), h_total_mc.GetBinContent(i), h_total_mc.GetBinWidth(i)/2.0
        stat     = h_total_mc.GetBinError(i)
        syst_up  = math.sqrt(sum_sq_up[i])
        syst_dn  = math.sqrt(sum_sq_dn[i])
        err_up   = math.sqrt(stat**2 + sum_sq_up[i])
        err_dn   = math.sqrt(stat**2 + sum_sq_dn[i])

        data_val = h_data.GetBinContent(i) if h_data else 0.0
        data_str = f"{data_val:10.1f}" if not IS_BLIND else f"{'Blinded':>10}"

        g_syst.SetPoint(i-1, x, y); g_syst.SetPointError(i-1, w, w, err_dn, err_up)
        if y > 0:
            g_ratio_band.SetPoint(i-1, x, 1.0); g_ratio_band.SetPointError(i-1, w, w, err_dn/y, err_up/y)
            g_ratio_stat.SetPoint(i-1, x, 1.0); g_ratio_stat.SetPointError(i-1, w, w, stat/y, stat/y)

            p_stat      = (stat/y)*100
            p_syst_up   = (syst_up/y)*100
            p_syst_dn   = (syst_dn/y)*100
            p_total_up  = (err_up/y)*100
            p_total_dn  = (err_dn/y)*100

            range_str = f"[{h_total_mc.GetBinLowEdge(i):.0f}, {h_total_mc.GetBinLowEdge(i+1):.0f}]"
            print(f"{i:<4} | {range_str:<18} | {y:10.1f} | {data_str} | {p_stat:7.1f}% | {p_syst_up:8.1f}% | {p_syst_dn:8.1f}% | {p_total_up:8.1f}% | {p_total_dn:8.1f}%")
            row_data = [i, h_total_mc.GetBinLowEdge(i), h_total_mc.GetBinLowEdge(i+1),
                        y, data_val,
                        group_hists["DYJets"].GetBinContent(i)    if group_hists["DYJets"]    else 0,
                        group_hists["TT"].GetBinContent(i)        if group_hists["TT"]        else 0,
                        group_hists["Nonprompt"].GetBinContent(i) if group_hists["Nonprompt"] else 0,
                        group_hists["Others"].GetBinContent(i)    if group_hists["Others"]    else 0,
                        p_stat, p_syst_up, p_syst_dn, p_total_up, p_total_dn]
            for syst in SYST_LIST:
                row_data.append(syst_per_bin[syst][i])
            csv_rows.append(row_data)
    print("="*160 + "\n")

    # Per-systematic summary
    print(">> Per-Systematic Contribution Summary (averaged over bins with yield > 0):")
    print("-"*60)
    valid_bins = [i for i in range(1, n_bins + 1) if h_total_mc.GetBinContent(i) > 0]
    syst_avg = []
    for syst in SYST_LIST:
        avg = np.mean([syst_per_bin[syst][i] for i in valid_bins]) if valid_bins else 0
        syst_avg.append((syst, avg))
        print(f"  {syst:<15}: {avg:8.2f}%")
    syst_avg.sort(key=lambda x: x[1], reverse=True)
    print("-"*60)
    print(">> Ranked by contribution:")
    for rank, (s, avg) in enumerate(syst_avg, 1):
        print(f"  {rank:>2}. {s:<15}: {avg:8.2f}%")
    print("="*60 + "\n")

    tsv_file = f"{PLOT_OUT_NAME}.tsv"
    with open(tsv_file, "w") as tsvf:
        header = "Bin\tBinLow\tBinHigh\tMC_Total\tData\tDYJets\tTT\tNonprompt\tOthers\tStat_pct\tSystUp_pct\tSystDn_pct\tTotalUp_pct\tTotalDn_pct"
        for syst in SYST_LIST:
            header += f"\t{syst}_pct"
        tsvf.write(header + "\n")
        for row in csv_rows:
            tsvf.write("\t".join(f"{v:.4f}" if isinstance(v, float) else str(v) for v in row) + "\n")
    print(f">> TSV saved as {tsv_file}")

    # --- 그리기 ---
    c  = ROOT.TCanvas("c", "c", 800, 900)
    p1 = ROOT.TPad("p1", "p1", 0, 0.3, 1, 1)
    p2 = ROOT.TPad("p2", "p2", 0, 0,   1, 0.3)
    _KEEPER.extend([c, p1, p2])
    p1.SetBottomMargin(0.02); p2.SetTopMargin(0.02); p2.SetBottomMargin(0.35)
    p1.Draw(); p2.Draw()

    p1.cd()
    if Y_LOG:
        p1.SetLogy()
    y_max = args.ymax if args.ymax else max(
        h_data.GetMaximum() if h_data and not IS_BLIND else 0,
        h_total_mc.GetMaximum()
    ) * (100 if Y_LOG else 1.5)

    h_dummy = h_total_mc.Clone("h_dummy"); h_dummy.Reset()
    h_dummy.GetYaxis().SetTitle("Events / bin")
    h_dummy.GetYaxis().SetTitleSize(0.05); h_dummy.GetYaxis().SetTitleOffset(1.1)
    h_dummy.GetXaxis().SetLabelSize(0)
    h_dummy.SetMinimum(args.ymin); h_dummy.SetMaximum(y_max)
    h_dummy.GetXaxis().SetRangeUser(X_MIN, X_MAX)
    h_dummy.Draw("HIST")

    stack.Draw("HIST SAME")
    g_syst.SetFillColorAlpha(ROOT.kGray+2, 0.8); g_syst.SetFillStyle(3013)
    g_syst.Draw("SAME E2")

    # ── WR 시그널 선 그리기 (pad1 최상단) ────────────────────────────────
    drawn_signals = []   # (label, h_scaled) — 레전드용
    for idx, (fname_base, h_sig) in enumerate(sorted(signal_hists.items())):
        h_sig_scaled = h_sig.Clone(f"h_sig_scaled_{fname_base}")
        h_sig_scaled.SetDirectory(0)
        h_sig_scaled.Scale(args.signal_scale)

        color = SIGNAL_COLORS[idx % len(SIGNAL_COLORS)]
        h_sig_scaled.SetLineColor(color)
        h_sig_scaled.SetLineWidth(3)
        h_sig_scaled.SetLineStyle(1)   # 실선
        h_sig_scaled.SetFillStyle(0)
        h_sig_scaled.Draw("HIST SAME")

        label = format_signal_label(fname_base, args.signal_scale)
        drawn_signals.append((label, h_sig_scaled))
        _KEEPER.append(h_sig_scaled)
    # ─────────────────────────────────────────────────────────────────────

    if h_data and not IS_BLIND:
        h_data.SetMarkerStyle(20); h_data.SetMarkerSize(1.2)
        h_data.SetLineColor(ROOT.kBlack)
        h_data.Draw("PE SAME")

    # 레전드
    leg = ROOT.TLegend(0.55, 0.50, 0.92, 0.88)
    leg.SetBorderSize(0); leg.SetFillStyle(0); leg.SetTextSize(0.035)
    for g_key, v in reversed(sorted_for_stack):
        leg.AddEntry(group_hists[g_key], BACKGROUND_GROUPS[g_key][1], "f")
    if h_data and not IS_BLIND:
        leg.AddEntry(h_data, "Data", "pe")
    leg.AddEntry(g_syst,       "Stat #oplus Syst Unc.", "f")
    leg.AddEntry(g_ratio_stat, "Stat. Unc.", "f")
    # 시그널 항목 추가
    for sig_label, h_sig_scaled in drawn_signals:
        leg.AddEntry(h_sig_scaled, sig_label, "l")
    leg.Draw()

    latex = ROOT.TLatex(); latex.SetNDC()
    latex.SetTextFont(61); latex.SetTextSize(0.045); latex.DrawLatex(0.12, 0.93, "CMS")
    latex.SetTextFont(52); latex.SetTextSize(0.035); latex.DrawLatex(0.21, 0.93, "Work in progress")
    latex.SetTextFont(42); latex.SetTextSize(0.030); latex.SetTextAlign(31)
    latex.DrawLatex(0.90, 0.93, "62.31 fb^{-1} (13.6 TeV)")
    latex.SetTextAlign(11); latex.SetTextFont(62); latex.SetTextSize(0.06)
    latex.DrawLatex(0.18, 0.82, "ee")
    latex.SetTextFont(42); latex.SetTextSize(0.060)
    latex.DrawLatex(0.18, 0.75, "Signal Region" if IS_BLIND else "Resolved FLV CR")
    p1.RedrawAxis()

    # --- Ratio pad ---
    p2.cd()
    h_frame = h_dummy.Clone("h_frame"); h_frame.Reset()
    h_frame.GetYaxis().SetTitle("Data / MC")
    h_frame.SetMinimum(args.rmin); h_frame.SetMaximum(args.rmax)
    h_frame.GetXaxis().SetTitle(args.xlabel if args.xlabel else HIST_NAME.split("_")[-2] + " [GeV]")
    h_frame.GetXaxis().SetTitleSize(0.1); h_frame.GetXaxis().SetLabelSize(0.11)
    h_frame.GetYaxis().SetTitleSize(0.1); h_frame.GetYaxis().SetLabelSize(0.11)
    h_frame.GetYaxis().SetTitleOffset(0.45); h_frame.GetYaxis().SetNdivisions(505)
    h_frame.GetXaxis().SetRangeUser(X_MIN, X_MAX)
    h_frame.Draw("HIST")

    if IS_BLIND:
        bl_txt = ROOT.TLatex()
        bl_txt.SetNDC(); bl_txt.SetTextAlign(22); bl_txt.SetTextSize(0.18)
        bl_txt.SetTextFont(62); bl_txt.SetTextColor(ROOT.kBlack)
        bl_txt.DrawLatex(0.5, 0.5, "Blinded")
        _KEEPER.append(bl_txt)
    else:
        g_ratio_stat.SetFillColorAlpha(ROOT.kOrange, 0.6); g_ratio_stat.SetFillStyle(1001)
        g_ratio_stat.Draw("SAME E2")
        g_ratio_band.SetFillColorAlpha(ROOT.kGray+2, 0.8); g_ratio_band.SetFillStyle(3013)
        g_ratio_band.Draw("SAME E2")
        if h_data and h_total_mc:
            h_ratio = h_data.Clone("h_ratio"); h_ratio.Divide(h_total_mc)
            h_ratio.Draw("PE SAME")
            _KEEPER.append(h_ratio)
        line = ROOT.TLine(X_MIN, 1, X_MAX, 1); line.SetLineStyle(2); line.Draw()

    p2.RedrawAxis()
    c.SaveAs(f"{PLOT_OUT_NAME}_plot.png")
    print(f">> Plot saved as {PLOT_OUT_NAME}_plot.png")


if __name__ == "__main__":
    run_plot()