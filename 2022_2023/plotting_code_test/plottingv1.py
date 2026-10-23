#!/usr/bin/env python3

import ROOT
import os
import glob
import numpy as np

# CMS 스타일 설정
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

# 데이터 디렉토리
data_dir = "/gv0/Users/achihwan/SKNanoOutput/Reproduce20_002/2023/"

# 색상 팔레트 정의
COLORS = {
    "TT+TW": ROOT.TColor.GetColor("#f89c20"),   # Orange
    "DYJets": ROOT.TColor.GetColor("#CDDC39"),  # Lime
    "Others": ROOT.TColor.GetColor("#5790fc")   # Blue
}

# ===============================================
# 1. 히스토그램 로드 함수
# ===============================================
def load_hist(file_path, hist_name, systematic="Central"):
    """ROOT 파일에서 히스토그램 하나 로드"""
    f = ROOT.TFile.Open(file_path)
    if not f or f.IsZombie():
        return None
    
    directory = f.Get(systematic)
    if not directory:
        f.Close()
        return None
    
    hist = directory.Get(hist_name)
    if not hist:
        f.Close()
        return None
    
    # 복사본 만들기
    hist_copy = hist.Clone(f"{os.path.basename(file_path)}_{hist_name}")
    hist_copy.SetDirectory(0)
    hist_copy.Sumw2()  # 에러 계산 활성화
    f.Close()
    
    return hist_copy

# ===============================================
# 2. 데이터 합치기
# ===============================================
def load_data(data_dir, hist_name):
    """EGamma 데이터 합치기"""
    print("Loading data files...")
    
    data_files = glob.glob(os.path.join(data_dir, "*.root"))
    combined_hist = None
    total_events = 0
    
    for file_path in data_files:
        filename = os.path.basename(file_path)
        
        if filename.startswith("Muon_"):
            hist = load_hist(file_path, hist_name)
            if hist:
                events = hist.Integral()
                print(f"  {filename}: {events:.1f} events")
                
                if combined_hist is None:
                    combined_hist = hist.Clone("Data")
                    combined_hist.SetDirectory(0)
                else:
                    combined_hist.Add(hist)
                
                total_events += events
    
    print(f"Total data events: {total_events:.1f}\n")
    return combined_hist

# ===============================================
# 3. MC 샘플 로드
# ===============================================
def load_mc_samples(data_dir, hist_name):
    """모든 MC 샘플 로드"""
    print("Loading MC samples...")
    
    mc_hists = {}
    mc_files = glob.glob(os.path.join(data_dir, "*.root"))
    
    for file_path in mc_files:
        filename = os.path.basename(file_path)
        sample_name = filename.replace(".root", "")
        
        # 데이터 파일 제외
        if (filename.startswith("Muon_") or 
            filename.startswith("EGamma") or
            filename.startswith("SingleMuon")):
            continue
        
        hist = load_hist(file_path, hist_name)
        if hist:
            events = hist.Integral()
            mc_hists[sample_name] = hist
            print(f"  {sample_name}: {events:.1f} events")
    
    print(f"Total MC samples: {len(mc_hists)}\n")
    return mc_hists

# ===============================================
# 4. MC 그룹으로 합치기
# ===============================================
def group_mc_samples(mc_hists):
    """MC 샘플을 카테고리별로 그룹화"""
    groups = {
        "TT+TW": [],
        "DYJets": [],
        "Others": []
    }
    
    # 샘플 분류
    for name, hist in mc_hists.items():
        if name.startswith("TTLJ") or name.startswith("TTLL") or name.startswith("ST"):
            groups["TT+TW"].append(hist)
        elif name.startswith("DYJets"):
            groups["DYJets"].append(hist)
        else:
            groups["Others"].append(hist)
    
    # 각 그룹을 하나로 합치기
    grouped_hists = {}
    for group_name, hist_list in groups.items():
        if not hist_list:
            continue
        
        combined = hist_list[0].Clone(group_name)
        combined.SetDirectory(0)
        for hist in hist_list[1:]:
            combined.Add(hist)
        
        grouped_hists[group_name] = combined
        print(f"{group_name}: {combined.Integral():.1f} events")
    
    return grouped_hists

# ===============================================
# 5. CMS 스타일 플롯 그리기
# ===============================================
def create_cms_canvas(name, width=800, height=800):
    """CMS 스타일 캔버스 생성 (2-panel)"""
    canvas = ROOT.TCanvas(name, name, width, height)
    
    # Upper pad
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
    pad1.SetBottomMargin(0.02)
    pad1.SetTopMargin(0.08)
    pad1.SetLeftMargin(0.12)
    pad1.SetRightMargin(0.05)
    pad1.SetLogy()
    pad1.Draw()
    
    # Lower pad
    pad2 = ROOT.TPad("pad2", "pad2", 0, 0.0, 1, 0.3)
    pad2.SetTopMargin(0.02)
    pad2.SetBottomMargin(0.35)
    pad2.SetLeftMargin(0.12)
    pad2.SetRightMargin(0.05)
    pad2.Draw()
    
    return canvas, pad1, pad2

def setup_cms_labels(pad):
    """CMS 라벨 추가"""
    pad.cd()
    
    # CMS label
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.045)
    latex.SetTextFont(62)
    latex.DrawLatex(0.12, 0.93, "CMS")
    
    latex.SetTextSize(0.035)
    latex.SetTextFont(52)
    latex.DrawLatex(0.20, 0.93, "Preliminary")
    
    latex.SetTextFont(42)
    latex.DrawLatex(0.73, 0.93, "26.67 fb^{-1} (13.6 TeV)")
    
    return latex

def create_legend(x1, y1, x2, y2):
    """범례 생성"""
    leg = ROOT.TLegend(x1, y1, x2, y2)
    leg.SetTextSize(0.035)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    return leg

def plot_data_mc_comparison(data_hist, mc_grouped, output_name, 
                            x_title="Variable", y_title="Events",
                            x_min=0, x_max=500):
    """Data vs MC 비교 플롯"""
    
    # 캔버스 생성
    canvas, pad1, pad2 = create_cms_canvas("canvas", 800, 800)
    
    # ===== Upper pad: Data vs MC Stack =====
    pad1.cd()
    
    # MC 스택 생성
    stack = ROOT.THStack("stack", "")
    total_mc = None
    
    # 그룹 순서 (낮은 것부터)
    group_order = ["Others", "DYJets", "TT+TW"]
    
    for group_name in group_order:
        if group_name in mc_grouped:
            hist = mc_grouped[group_name]
            hist.SetFillColor(COLORS[group_name])
            hist.SetLineColor(COLORS[group_name])
            hist.SetLineWidth(1)
            stack.Add(hist)
            
            # Total MC 계산
            if total_mc is None:
                total_mc = hist.Clone("total_mc")
                total_mc.SetDirectory(0)
            else:
                total_mc.Add(hist)
    
    # 스택 그리기
    stack.Draw("HIST")
    stack.GetXaxis().SetRangeUser(x_min, x_max)
    stack.GetYaxis().SetTitle(y_title)
    stack.GetYaxis().SetTitleSize(0.05)
    stack.GetYaxis().SetTitleOffset(1.2)
    stack.GetYaxis().SetLabelSize(0.04)
    stack.GetXaxis().SetLabelSize(0)
    stack.SetMinimum(0.1)
    stack.SetMaximum(max(data_hist.GetMaximum(), total_mc.GetMaximum()) * 10)
    
    # MC 불확실성 밴드 (빗금)
    mc_error = total_mc.Clone("mc_error")
    mc_error.SetFillColor(ROOT.kBlack)
    mc_error.SetFillStyle(3004)  # 빗금 패턴
    mc_error.SetMarkerSize(0)
    mc_error.Draw("E2 SAME")
    
    # Data 그리기
    data_hist.SetMarkerStyle(20)
    data_hist.SetMarkerSize(1.0)
    data_hist.SetMarkerColor(ROOT.kBlack)
    data_hist.SetLineColor(ROOT.kBlack)
    data_hist.SetLineWidth(2)
    data_hist.GetXaxis().SetRangeUser(x_min, x_max)
    data_hist.Draw("PE SAME")
    
    # 범례
    leg = create_legend(0.7, 0.89 - 0.05 * 6, 0.94, 0.89)
    leg.AddEntry(data_hist, "Data", "PE")
    for group_name in reversed(group_order):  # 역순으로 (위에서부터)
        if group_name in mc_grouped:
            leg.AddEntry(mc_grouped[group_name], group_name, "F")
    leg.AddEntry(mc_error, "MC stat. unc.", "F")
    leg.Draw()
    
    # CMS 라벨
    latex = setup_cms_labels(pad1)
    
    pad1.RedrawAxis()
    
    # ===== Lower pad: Ratio =====
    pad2.cd()
    
    # Ratio 계산
    ratio = data_hist.Clone("ratio")
    ratio.SetDirectory(0)
    ratio.Divide(total_mc)
    
    # Ratio 히스토그램 설정
    ratio.SetMarkerStyle(20)
    ratio.SetMarkerSize(0.8)
    ratio.SetMarkerColor(ROOT.kBlack)
    ratio.SetLineColor(ROOT.kBlack)
    ratio.SetLineWidth(1)
    
    ratio.GetYaxis().SetTitle("Data / MC")
    ratio.GetYaxis().SetTitleSize(0.12)
    ratio.GetYaxis().SetTitleOffset(0.5)
    ratio.GetYaxis().SetLabelSize(0.10)
    ratio.GetYaxis().SetNdivisions(505)
    ratio.GetYaxis().SetRangeUser(0.5, 1.5)
    
    ratio.GetXaxis().SetTitle(x_title)
    ratio.GetXaxis().SetTitleSize(0.12)
    ratio.GetXaxis().SetTitleOffset(1.0)
    ratio.GetXaxis().SetLabelSize(0.10)
    ratio.GetXaxis().SetRangeUser(x_min, x_max)
    
    ratio.Draw("PE")
    
    # MC 불확실성 밴드 (빗금)
    ratio_error = total_mc.Clone("ratio_error")
    for i in range(1, ratio_error.GetNbinsX() + 1):
        content = total_mc.GetBinContent(i)
        error = total_mc.GetBinError(i)
        if content > 0:
            ratio_error.SetBinContent(i, 1.0)
            ratio_error.SetBinError(i, error / content)
        else:
            ratio_error.SetBinContent(i, 1.0)
            ratio_error.SetBinError(i, 0.0)
    
    ratio_error.SetFillColor(ROOT.kBlack)
    ratio_error.SetFillStyle(3004)  # 빗금 패턴
    ratio_error.SetMarkerSize(0)
    ratio_error.Draw("E2 SAME")
    
    # y=1 기준선
    line = ROOT.TLine(x_min, 1.0, x_max, 1.0)
    line.SetLineStyle(2)
    line.SetLineColor(ROOT.kBlack)
    line.SetLineWidth(1)
    line.Draw()
    
    ratio.Draw("PE SAME")
    
    pad2.RedrawAxis()
    
    # 저장
    canvas.SaveAs(f"{output_name}.png")
    canvas.SaveAs(f"{output_name}.pdf")
    print(f"Saved: {output_name}.png, {output_name}.pdf")
    
    return canvas, pad1, pad2, stack, data_hist, ratio, leg, latex, line
# ===============================================
# 4-1. 리빈 함수 추가
# ===============================================
def rebin_histograms(data_hist, mc_grouped, rebin_factor=None, custom_bins=None):
    """
    히스토그램 리빈
    
    Parameters:
    - rebin_factor: 정수 (예: 2 = 2개 빈을 1개로 합침)
    - custom_bins: 가변 빈 크기 리스트 (예: [0, 50, 100, 200, 500])
    """
    
    if rebin_factor is not None:
        # 균일한 리빈
        print(f"Rebinning with factor {rebin_factor}")
        if data_hist:
            data_hist.Rebin(rebin_factor)
        for hist in mc_grouped.values():
            hist.Rebin(rebin_factor)
    
    elif custom_bins is not None:
        # 가변 빈 크기 리빈
        print(f"Rebinning with custom bins: {custom_bins}")
        from array import array
        bins = array('d', custom_bins)
        
        if data_hist:
            data_hist = data_hist.Rebin(len(bins)-1, data_hist.GetName()+"_rebin", bins)
        
        for name, hist in mc_grouped.items():
            mc_grouped[name] = hist.Rebin(len(bins)-1, hist.GetName()+"_rebin", bins)
        
        return data_hist, mc_grouped
    
    return data_hist, mc_grouped

# ===============================================
# 6. 메인 실행 (수정)
# ===============================================
def main():
    """메인 함수"""
    
    hist_name = "DYCR_Resolved_MM_pt"
    output_name = "test_plot_cms_style"
    
    print("="*50)
    print("CMS Style Plotter (ROOT)")
    print("="*50)
    
    # 1. 데이터 로드
    data_hist = load_data(data_dir, hist_name)
    
    # 2. MC 로드
    mc_hists = load_mc_samples(data_dir, hist_name)
    
    # 3. MC 그룹화
    mc_grouped = group_mc_samples(mc_hists)
    
    # 4. 리빈 설정 (선택)
    # 방법 1: 균일한 리빈 (2개씩 합치기)
    # data_hist, mc_grouped = rebin_histograms(data_hist, mc_grouped, rebin_factor=2)
    
    # 방법 2: 가변 빈 크기 (원하는 빈 경계 지정)
    data_hist, mc_grouped = rebin_histograms(
        data_hist, mc_grouped, 
        custom_bins=[0, 50, 100, 150, 200, 300, 400, 500]  # 원하는 빈 경계
    )
    
    # 방법 3: 리빈 안 함 (원본 빈 사용)
    # pass
    
    # 5. 플롯 그리기
    canvas, pad1, pad2, stack, data, ratio, leg, latex, line = plot_data_mc_comparison(
        data_hist, mc_grouped, output_name,
        x_title="Dilepton p_{T} [GeV]",
        y_title="Events",
        x_min=0, x_max=500
    )
    
    print("\nDone!")
    
    # 메모리 유지
    ROOT.SetOwnership(canvas, False)
    ROOT.SetOwnership(pad1, False)
    ROOT.SetOwnership(pad2, False)
    ROOT.SetOwnership(stack, False)
    ROOT.SetOwnership(data, False)
    ROOT.SetOwnership(ratio, False)
    ROOT.SetOwnership(leg, False)
    ROOT.SetOwnership(latex, False)
    ROOT.SetOwnership(line, False)

if __name__ == "__main__":
    main()
