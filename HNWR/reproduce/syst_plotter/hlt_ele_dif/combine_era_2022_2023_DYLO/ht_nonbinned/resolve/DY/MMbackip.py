import ROOT
import math
import numpy as np
import os
import sys
import argparse

# --- 1. 기본 설정 (인자가 없을 경우 사용됨) ---
DEFAULT_DATA_PATH = "/gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy/2023/"
DEFAULT_HIST_NAME = "Obj_PU_Corr_DYCR_Resolved_EE_pt"

# 샘플 그룹 및 매핑 설정
BACKGROUND_GROUPS = {
    "DYJets": [ROOT.kYellow, "Drell-Yan"],
    "TT": [ROOT.kRed, "T#bar{T}+tW"], 
    "Nonprompt": [ROOT.kGreen+2, "Nonprompt"],
    "Others": [ROOT.kBlue, "Others"]
}

SAMPLE_MAP = {
    "DYJets": "DYJets",
    "TTLL": "TT",
    "TTLJ": "TT",
    "ST": "TT",      
    "WJets": "Nonprompt",
    "ST_tch": "Nonprompt",
    "ST_sch": "Nonprompt"
}

DATA_FILES = ["Muon"]
EXCLUDE_SAMPLES = ["DYJets_MG", "Skim","EGamma"] 
SYST_LIST = ["Pileup", "ElectronID", "ElectronReco", "ElectronTrig", "MuonID", "MuonReco", "MuonTrig", "MuonIso"]

# 메모리 누수 방지용
_KEEPER = []

try:
    import cmsstyle as CMS
    CMS_STYLE = True
except:
    CMS_STYLE = False

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
    parser.add_argument("--hist", type=str, default=DEFAULT_HIST_NAME, help="불러올 히스토그램 이름")
    parser.add_argument("--rebin", type=int, default=1, help="리빈(Rebin) 수치")
    parser.add_argument("--output", type=str, default=None, help="결과물 파일 이름")
    parser.add_argument("--ymin", type=float, default=5.0, help="Y축 최소값")
    parser.add_argument("--ymax", type=float, default=None, help="Y축 최대값")
    parser.add_argument("--xmin", type=float, default=None, help="X축 최소 범위")
    parser.add_argument("--xmax", type=float, default=None, help="X축 최대 범위")
    parser.add_argument("--bins", type=str, default=None, help="커스텀 빈 (쉼표 구분)")
    parser.add_argument("--xlabel", type=str, default=None, help="X축 제목 라벨")
    parser.add_argument("--logy", action="store_false", default=True, help="Y축 로그 스케일 해제")
    # Ratio 패널 (pad2)의 Y축 범위를 위한 인자 추가
    parser.add_argument("--rmin", type=float, default=0.5, help="Ratio 패널 Y축 최소값")
    parser.add_argument("--rmax", type=float, default=1.5, help="Ratio 패널 Y축 최대값")
    args = parser.parse_args()

    HIST_NAME = args.hist
    # SR이 이름에 포함되어 있는지 확인 (Blind 모드)
    IS_BLIND = "SR" in HIST_NAME.upper()
    
    REBIN_FACTOR = args.rebin
    Y_MIN = args.ymin
    Y_MAX_USER = args.ymax
    Y_LOG = args.logy
    
    CUSTOM_BINS = None
    if args.bins:
        CUSTOM_BINS = [float(x) for x in args.bins.split(",")]
    
    # 설정된 X 범위 (경고 방지를 위해 실제 히스토그램 로드 후 보정 예정)
    X_MIN_REQ = args.xmin if args.xmin is not None else (CUSTOM_BINS[0] if CUSTOM_BINS else 40)
    X_MAX_REQ = args.xmax if args.xmax is not None else (CUSTOM_BINS[-1] if CUSTOM_BINS else 2000)
    
    PLOT_OUT_NAME = args.output if args.output else HIST_NAME

    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptStat(0)

    h_data = None
    group_hists = {g: None for g in BACKGROUND_GROUPS}
    all_files = sorted([f for f in os.listdir(DEFAULT_DATA_PATH) if f.endswith(".root")])

    print(f"\n>> Loading Central histograms for: {HIST_NAME}")
    if IS_BLIND: print("!! BLIND MODE ACTIVATED (SR detected in histogram name) !!")
    print("="*85)
    
    for fname in all_files:
        if any(ex in fname for ex in EXCLUDE_SAMPLES): continue
        path = os.path.join(DEFAULT_DATA_PATH, fname)
        is_data_file = any(df in fname for df in DATA_FILES)
        tag = "[DATA]" if is_data_file else "[MC  ]"
        
        h = get_hist_from_file(path, "Central", HIST_NAME, X_MAX_REQ, CUSTOM_BINS, REBIN_FACTOR)
        
        if h:
            print(f"  {tag} {fname:<40}: {h.Integral():12.2f} events")
            if is_data_file:
                if h_data is None: 
                    h_data = h.Clone("h_data_total")
                    h_data.SetDirectory(0)
                else: 
                    h_data.Add(h)
            else:
                matched_group = "Others"
                for key, group in SAMPLE_MAP.items():
                    if key in fname:
                        matched_group = group
                        break
                if group_hists[matched_group] is None: 
                    group_hists[matched_group] = h.Clone(f"h_group_{matched_group}")
                    group_hists[matched_group].SetDirectory(0)
                else: 
                    group_hists[matched_group].Add(h)

    # 히스토그램의 실제 범위에 맞춰 X_MIN, X_MAX 보정 (RuntimeWarning 방지)
    if h_total_mc_check := next((h for h in group_hists.values() if h), None):
        h_xmin = h_total_mc_check.GetXaxis().GetXmin()
        h_xmax = h_total_mc_check.GetXaxis().GetXmax()
        X_MIN = max(X_MIN_REQ, h_xmin)
        X_MAX = min(X_MAX_REQ, h_xmax)
    else:
        X_MIN, X_MAX = X_MIN_REQ, X_MAX_REQ

    # Stack 생성
    valid_groups = [(g, group_hists[g].Integral()) for g in BACKGROUND_GROUPS if group_hists[g]]
    sorted_for_stack = sorted(valid_groups, key=lambda x: x[1])
    stack = ROOT.THStack("stack", "")
    h_total_mc = None
    for g_key, yield_val in sorted_for_stack:
        h = group_hists[g_key]
        h.SetFillColor(BACKGROUND_GROUPS[g_key][0])
        h.SetLineColor(BACKGROUND_GROUPS[g_key][0])
        stack.Add(h)
        if h_total_mc is None: 
            h_total_mc = h.Clone("h_total_mc_nominal")
            h_total_mc.SetDirectory(0)
        else: 
            h_total_mc.Add(h)
    
    _KEEPER.extend([stack, h_total_mc, h_data])

    # 시스테마틱 계산
    print(">> Calculating Systematic Uncertainties (MC only)...")
    n_bins = h_total_mc.GetNbinsX()
    sum_sq_up = np.zeros(n_bins + 2); sum_sq_dn = np.zeros(n_bins + 2)
    
    for syst in SYST_LIST:
        h_mc_up, h_mc_dn = None, None
        for fname in all_files:
            if any(ex in fname for ex in EXCLUDE_SAMPLES) or any(df in fname for df in DATA_FILES): continue
            path = os.path.join(DEFAULT_DATA_PATH, fname)
            u = get_hist_from_file(path, f"{syst}_Up", HIST_NAME, X_MAX, CUSTOM_BINS, REBIN_FACTOR)
            d = get_hist_from_file(path, f"{syst}_Down", HIST_NAME, X_MAX, CUSTOM_BINS, REBIN_FACTOR)
            if u:
                if h_mc_up is None: h_mc_up = u.Clone("h_up"); h_mc_up.SetDirectory(0)
                else: h_mc_up.Add(u)
            if d:
                if h_mc_dn is None: h_mc_dn = d.Clone("h_dn"); h_mc_dn.SetDirectory(0)
                else: h_mc_dn.Add(d)
        
        if not h_mc_up or not h_mc_dn: continue
        for i in range(1, n_bins + 1):
            nom = h_total_mc.GetBinContent(i)
            diff_up = h_mc_up.GetBinContent(i) - nom
            diff_dn = h_mc_dn.GetBinContent(i) - nom
            sum_sq_up[i] += max(0, diff_up, diff_dn)**2
            sum_sq_dn[i] += max(0, -diff_up, -diff_dn)**2

    # --- 에러 요약 목록 출력 ---
    print("\n>> Bin-by-bin Uncertainty Summary (%)")
    print("="*145)
    print(f"{'Bin':<4} | {'Range':<18} | {'Yield':<10} | {'Stat(%)':<8} | {'SystUp(%)':<9} | {'SystDn(%)':<9} | {'TotalUp(%)':<9} | {'TotalDn(%)':<9}")
    print("-" * 145)

    g_syst = ROOT.TGraphAsymmErrors(n_bins)
    g_ratio_band = ROOT.TGraphAsymmErrors(n_bins)
    g_ratio_stat = ROOT.TGraphAsymmErrors(n_bins) # 통계 에러 전용 밴드
    _KEEPER.extend([g_syst, g_ratio_band, g_ratio_stat])

    for i in range(1, n_bins + 1):
        x, y, w = h_total_mc.GetBinCenter(i), h_total_mc.GetBinContent(i), h_total_mc.GetBinWidth(i)/2.0
        stat = h_total_mc.GetBinError(i)
        syst_up = math.sqrt(sum_sq_up[i])
        syst_dn = math.sqrt(sum_sq_dn[i])
        err_up = math.sqrt(stat**2 + sum_sq_up[i])
        err_dn = math.sqrt(stat**2 + sum_sq_dn[i])
        
        g_syst.SetPoint(i-1, x, y); g_syst.SetPointError(i-1, w, w, err_dn, err_up)
        if y > 0:
            # 합산 에러 밴드 (Stat + Syst)
            g_ratio_band.SetPoint(i-1, x, 1.0); g_ratio_band.SetPointError(i-1, w, w, err_dn/y, err_up/y)
            # 통계 에러 밴드 (Stat only)
            g_ratio_stat.SetPoint(i-1, x, 1.0); g_ratio_stat.SetPointError(i-1, w, w, stat/y, stat/y)
            
            p_stat = (stat/y)*100
            p_syst_up = (syst_up/y)*100
            p_syst_dn = (syst_dn/y)*100
            p_total_up = (err_up/y)*100
            p_total_dn = (err_dn/y)*100
            
            range_str = f"[{h_total_mc.GetBinLowEdge(i):.0f}, {h_total_mc.GetBinLowEdge(i+1):.0f}]"
            print(f"{i:<4} | {range_str:<18} | {y:10.1f} | {p_stat:7.1f}% | {p_syst_up:8.1f}% | {p_syst_dn:8.1f}% | {p_total_up:8.1f}% | {p_total_dn:8.1f}%")
    print("="*145 + "\n")

    # 5. 그리기
    c = ROOT.TCanvas("c", "c", 800, 900)
    p1 = ROOT.TPad("p1", "p1", 0, 0.3, 1, 1); p2 = ROOT.TPad("p2", "p2", 0, 0, 1, 0.3)
    _KEEPER.extend([c, p1, p2])
    p1.SetBottomMargin(0.02); p2.SetTopMargin(0.02); p2.SetBottomMargin(0.35); p1.Draw(); p2.Draw()

    p1.cd()
    if Y_LOG: p1.SetLogy()
    y_max = Y_MAX_USER if Y_MAX_USER else max(h_data.GetMaximum() if h_data and not IS_BLIND else 0, h_total_mc.GetMaximum()) * (100 if Y_LOG else 1.5)
    
    h_dummy = h_total_mc.Clone("h_dummy"); h_dummy.Reset()
    h_dummy.GetYaxis().SetTitle("Events / bin"); h_dummy.GetYaxis().SetTitleSize(0.05); h_dummy.GetYaxis().SetTitleOffset(1.1)
    h_dummy.GetXaxis().SetLabelSize(0); h_dummy.SetMinimum(Y_MIN); h_dummy.SetMaximum(y_max)
    h_dummy.GetXaxis().SetRangeUser(X_MIN, X_MAX); h_dummy.Draw("HIST")

    stack.Draw("HIST SAME")
    g_syst.SetFillColorAlpha(ROOT.kBlack, 0.6); g_syst.SetFillStyle(3013); g_syst.Draw("SAME E2")
    
    # Blind 모드가 아닐 때만 데이터 그림
    if h_data and not IS_BLIND:
        h_data.SetMarkerStyle(20); h_data.SetMarkerSize(1.2); h_data.SetLineColor(ROOT.kBlack); h_data.Draw("PE SAME")
    
    leg = ROOT.TLegend(0.55, 0.55, 0.92, 0.88); leg.SetBorderSize(0); leg.SetFillStyle(0); leg.SetTextSize(0.035)
    for g_key, v in reversed(sorted_for_stack): 
        leg.AddEntry(group_hists[g_key], BACKGROUND_GROUPS[g_key][1], "f")
    if h_data and not IS_BLIND: leg.AddEntry(h_data, "Data", "pe")
    leg.AddEntry(g_syst, "Stat + Syst Unc.", "f")
    # 범례에도 통계 에러 항목 추가
    leg.AddEntry(g_ratio_stat, "Stat. Unc.", "f")
    leg.Draw()

    latex = ROOT.TLatex(); latex.SetNDC()
    latex.SetTextFont(61); latex.SetTextSize(0.045); latex.DrawLatex(0.12, 0.93, "CMS")
    latex.SetTextFont(52); latex.SetTextSize(0.035); latex.DrawLatex(0.21, 0.93, "Preliminary")
    latex.SetTextFont(42); latex.SetTextSize(0.030); latex.SetTextAlign(31); latex.DrawLatex(0.95, 0.93, "17.8 fb^{-1} (13.6 TeV)")
    latex.SetTextAlign(11); latex.SetTextFont(62); latex.SetTextSize(0.045); latex.DrawLatex(0.18, 0.82, "\mu#mu")
    latex.SetTextFont(42); latex.SetTextSize(0.040); latex.DrawLatex(0.18, 0.77, "Resolved DY CR")
    p1.RedrawAxis()

    p2.cd()
    h_frame = h_dummy.Clone("h_frame"); h_frame.Reset()
    h_frame.GetYaxis().SetTitle("Data / MC")
    h_frame.SetMinimum(args.rmin)
    h_frame.SetMaximum(args.rmax)
    
    x_title = args.xlabel if args.xlabel else HIST_NAME.split("_")[-1] + " [GeV]"
    h_frame.GetXaxis().SetTitle(x_title)
    h_frame.GetXaxis().SetTitleSize(0.1); h_frame.GetXaxis().SetLabelSize(0.11)
    h_frame.GetYaxis().SetTitleSize(0.1); h_frame.GetYaxis().SetLabelSize(0.11); h_frame.GetYaxis().SetTitleOffset(0.45)
    h_frame.GetYaxis().SetNdivisions(505); h_frame.GetXaxis().SetRangeUser(X_MIN, X_MAX); h_frame.Draw("HIST")
    
    if IS_BLIND:
        txt = ROOT.TLatex(); txt.SetNDC(); txt.SetTextAlign(22); txt.SetTextSize(0.15); txt.SetTextFont(62); txt.SetTextColor(ROOT.kGray+2)
        txt.DrawLatex(0.5, 0.5, "BLINDED")
    else:
        # 합산 에러 밴드 (연한 패턴)
        g_ratio_band.SetFillColorAlpha(ROOT.kBlack, 0.2); g_ratio_band.SetFillStyle(1001)
        g_ratio_band.Draw("SAME E2")
        
        # 통계 에러 밴드 (진한 색상)
        g_ratio_stat.SetFillColorAlpha(ROOT.kGray+2, 0.8); g_ratio_stat.SetFillStyle(1001)
        g_ratio_stat.Draw("SAME E2")
        
        if h_data and h_total_mc:
            h_ratio = h_data.Clone("h_ratio"); h_ratio.Divide(h_total_mc); h_ratio.Draw("PE SAME")
        line = ROOT.TLine(X_MIN, 1, X_MAX, 1); line.SetLineStyle(2); line.Draw()
    
    p2.RedrawAxis()
    c.SaveAs(f"{PLOT_OUT_NAME}_plot.pdf")
    print(f">> Plot saved as {PLOT_OUT_NAME}_plot.pdf")

if __name__ == "__main__":
    run_plot()