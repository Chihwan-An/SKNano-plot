# ===========================================
# 루트 파일에서 데이터 가져오는 방법 (초보자 가이드)
# ===========================================

# 1. 데이터 디렉토리 경로 설정
# 루트 파일들이 저장된 폴더의 경로를 지정합니다
data_directory = "/gv0/Users/achihwan/SKNanoRunlog/out/LRSM_TBChannel/2022EE/"


import ROOT
import cmsstyle as CMS
import os
ttlj = ROOT.TH1F("CutFlow" + "TTLJ", "CutFlow" + "TTLJ", 7, 0, 7)
ttll = ROOT.TH1F("CutFlow" + "TTLL", "CutFlow" + "TTLL", 7, 0, 7)
st = ROOT.TH1F("CutFlow" + "ST", "CutFlow" + "ST", 7, 0, 7)
ttx = ROOT.TH1F("CutFlow" + "TTX", "CutFlow" + "TTX", 7, 0, 7)



for file in os.listdir(data_directory):
    if not file.startswith("TB") and not file.startswith("TTLJ") and not file.startswith("TTLL") and not file.startswith("ST") and not file.startswith("TTX"):
        continue

    root_file = ROOT.TFile.Open(os.path.join(data_directory, file))
    
    central_dir = root_file.Get("Central")  # Central 디렉토리로 이동
    if not central_dir:
        print(f"Central directory not found in {file}")
        continue
    hist = central_dir.Get("CutFlow")       # Central 안에서 CutFlow 가져오기
    
    
    hist_clone = hist.Clone("CutFlow")
    hist_clone.SetDirectory(0)
    ROOT.SetOwnership(hist_clone, False)
    
    hist_new = ROOT.TH1F("CutFlow" + file, "CutFlow" + file, 7, 0, 7)
    if file.startswith("TTLJ"):
        hist_new = ttlj
    elif file.startswith("TTLL"):
        hist_new = ttll
    elif file.startswith("ST"):
        hist_new = st
    elif file.startswith("TTX"):
        hist_new = ttx
    
    print("file name", file)
    # 빈 번호는 1부터 시작 (0번은 언더플로우)
    print("hist_clone.GetNbinsX()", hist_clone.GetNbinsX())
    for i in range(1, 7):
        bin_content = hist_clone.GetBinContent(i)    
        print("bin number", i, "bin content", bin_content)
        next_bin_content = hist_clone.GetBinContent(i+1)
        if i == hist_clone.GetNbinsX():
            next_bin_content = bin_content
        content_diff =   bin_content - next_bin_content
        if content_diff == 0:
            hist_new.SetBinContent(i, 0)
            continue
        percent = content_diff / bin_content * 100 
        hist_new.SetBinContent(i, percent)
    final_content = hist_clone.GetBinContent(7)
    initial_content = hist_clone.GetBinContent(1)
    content_diff = initial_content - final_content
    percent = 100- content_diff / initial_content * 100
    hist_new.SetBinContent(7, percent)
    hist_new.GetXaxis().SetBinLabel(1, "Trigger pass")
    hist_new.GetXaxis().SetBinLabel(2, "Muon ID ")
    hist_new.GetXaxis().SetBinLabel(3, "Muon pt , eta")
    hist_new.GetXaxis().SetBinLabel(4, "Dilepton cut")
    hist_new.GetXaxis().SetBinLabel(5, "top tagger , SDM , pt , eta")
    hist_new.GetXaxis().SetBinLabel(6, "B Tagger , pt , eta")
    hist_new.GetXaxis().SetBinLabel(7, "final left")
    
    canvas = ROOT.TCanvas("canvas", "canvas", 800, 600)

    hist_new.Draw()
    hist_new.SetTitle("CutFlow" + file)
    hist_new.GetXaxis().SetTitle("Cut Stage")
    hist_new.GetXaxis().SetTitleOffset(1.2)
    hist_new.GetYaxis().SetTitle("Percent %")
    hist_new.SetLineColor(ROOT.kBlue)
    hist_new.SetLineWidth(2)
    hist_new.SetMaximum(100)
    hist_new.SetStats(0)
    if not file.startswith("TB"):
        canvas.SetLogy()

    
    canvas.Update()
    
    if file.startswith("TTLJ"):
        canvas.SaveAs("CutFlow" + "TTLJ" + ".png")
    elif file.startswith("TTLL"):
        canvas.SaveAs("CutFlow" + "TTLL" + ".png")
    elif file.startswith("ST"):
        canvas.SaveAs("CutFlow" + "ST" + ".png")
    elif file.startswith("TTX"):
        canvas.SaveAs("CutFlow" + "TTX" + ".png")
    else:
        canvas.SaveAs("CutFlow" + file.replace('.root', '') + ".png")
    canvas.Close()

    

    root_file.Close()







#
# ===========================================
# 실제 사용 예시 (CR_2022EE.py에서 사용된 방법):
# ===========================================
#
# def load_histogram(file_path, hist_name, systematic="Central"):
#     # 1. 루트 파일 열기
#     root_file = ROOT.TFile.Open(file_path)
#     if not root_file or root_file.IsZombie():
#         print(f"파일을 열 수 없습니다: {file_path}")
#         return None
#     
#     # 2. 시스템틱 디렉토리로 이동 (예: "Central", "Up", "Down")
#     directory = root_file.Get(systematic)
#     if not directory:
#         print(f"디렉토리를 찾을 수 없습니다: {systematic}")
#         root_file.Close()
#         return None
#     
#     # 3. 히스토그램 가져오기
#     hist = directory.Get(hist_name)
#     if not hist:
#         print(f"히스토그램을 찾을 수 없습니다: {hist_name}")
#         root_file.Close()
#         return None
#     
#     # 4. 히스토그램 복사 (파일이 닫혀도 사용 가능)
#     hist_clone = hist.Clone(f"{os.path.basename(file_path)}_{hist_name}")
#     hist_clone.SetDirectory(0)  # 메모리에 저장
#     
#     # 6. 파일 닫기
#     root_file.Close()
#     
#     return hist_clone
#
# ===========================================
# 루트 파일 구조 이해하기:
# ===========================================
# 루트 파일은 다음과 같은 구조를 가집니다:
# 
# 파일명.root
# ├── Central/          # 중앙값 (기본값)
# │   ├── Topjetnum     # 히스토그램들
# │   ├── Jetpt
# │   └── ...
# ├── Up/               # 위쪽 시스템틱
# │   ├── Topjetnum
# │   └── ...
# └── Down/             # 아래쪽 시스템틱
#     ├── Topjetnum
#     └── ...
#
# ===========================================
# 주의사항:
# ===========================================
# 1. 파일을 열었으면 반드시 닫아야 합니다 (메모리 누수 방지)
# 2. 히스토그램을 복사해서 사용해야 파일이 닫힌 후에도 사용 가능
# 3. SetDirectory(0)을 사용해서 히스토그램을 메모리에 저장
# 4. 파일이 손상되었는지 IsZombie()로 확인
# 6. 객체가 존재하는지 None 체크 필수

# ===========================================
# 실제 사용 예시 함수들:
# ===========================================



# ===========================================
# 메인 실행 부분:
# ===========================================
'''
if __name__ == "__main__":
    # 테스트 실행 (주석 해제해서 사용)
    # 테스트_실행()
    
    print("💡 이 파일은 루트 파일에서 데이터를 가져오는 방법을 설명합니다.")
    print("💡 테스트를 실행하려면 '테스트_실행()' 함수의 주석을 해제하세요.")
    print("💡 실제 사용 예시:")
    print("   hist = 간단한_히스토그램_가져오기('파일경로.root', 'Topjetnum')")
'''