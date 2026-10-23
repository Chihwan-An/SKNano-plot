# ===========================================
# 루트 파일에서 데이터 가져오는 방법 (초보자 가이드)
# ===========================================

# 1. 데이터 디렉토리 경로 설정
# 루트 파일들이 저장된 폴더의 경로를 지정합니다
data_directory = "/gv0/Users/achihwan/SKNanoRunlog/out/LRSM_TBChannel/2022EE/"


import ROOT
import cmsstyle as CMS
import os
ttlj = ROOT.TH1F("CutFlow" + "TTLJ", "CutFlow" + "TTLJ", 5, 0, 5)
ttll = ROOT.TH1F("CutFlow" + "TTLL", "CutFlow" + "TTLL", 5, 0, 5)
st = ROOT.TH1F("CutFlow" + "ST", "CutFlow" + "ST", 5, 0, 5)
ttx = ROOT.TH1F("CutFlow" + "TTX", "CutFlow" + "TTX", 5, 0, 5)



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
    
    hist_new = ROOT.TH1F("CutFlow" + file, "CutFlow" + file, 5, 0, 5)
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
    for i in range(1, 7):
        bin_content = hist_clone.GetBinContent(i)    
        print("bin number", i, "bin content", bin_content)
        next_bin_content = hist_clone.GetBinContent(i+1)
        if i == hist_clone.GetNbinsX():
            next_bin_content = bin_content
        content_diff =   bin_content - next_bin_content
        if content_diff == 0:
            continue
        percent = content_diff / bin_content * 100 
        hist_new.SetBinContent(i-1, percent)
    
    hist_new.GetXaxis().SetBinLabel(1, "Trigger pass")
    hist_new.GetXaxis().SetBinLabel(2, "Muon ID , pt , eta")
    hist_new.GetXaxis().SetBinLabel(3, "Dilepton cut")
    hist_new.GetXaxis().SetBinLabel(4, "top tagger , SDM , pt , eta")
    hist_new.GetXaxis().SetBinLabel(5, "B Tagger , pt , eta")
    
    
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
#     # 5. 파일 닫기
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
# 5. 객체가 존재하는지 None 체크 필수

# ===========================================
# 실제 사용 예시 함수들:
# ===========================================

def 간단한_히스토그램_가져오기(파일경로, 히스토그램이름):
    """
    루트 파일에서 히스토그램을 가져오는 가장 간단한 방법
    초보자를 위한 예시 함수
    """
    # 1단계: 파일 열기
    root_file = ROOT.TFile.Open(파일경로)
    if not root_file or root_file.IsZombie():
        print(f"❌ 파일을 열 수 없습니다: {파일경로}")
        return None
    
    # 2단계: 파일 내용 확인 (디버깅용)
    print("📁 파일 내부 구조:")
    root_file.ls()
    
    # 3단계: 히스토그램 가져오기
    hist = root_file.Get(히스토그램이름)
    if not hist:
        print(f"❌ 히스토그램을 찾을 수 없습니다: {히스토그램이름}")
        root_file.Close()
        return None
    
    # 4단계: 히스토그램 복사
    hist_clone = hist.Clone(f"복사본_{히스토그램이름}")
    hist_clone.SetDirectory(0)  # 메모리에 저장
    
    # 5단계: 파일 닫기
    root_file.Close()
    
    print(f"✅ 히스토그램 가져오기 성공: {히스토그램이름}")
    print(f"   - 총 이벤트 수: {hist_clone.Integral():.1f}")
    print(f"   - 빈 개수: {hist_clone.GetNbinsX()}")
    
    return hist_clone

def 시스템틱_히스토그램_가져오기(파일경로, 히스토그램이름, 시스템틱="Central"):
    """
    시스템틱 디렉토리에서 히스토그램을 가져오는 방법
    (Central, Up, Down 등)
    """
    # 1단계: 파일 열기
    root_file = ROOT.TFile.Open(파일경로)
    if not root_file or root_file.IsZombie():
        print(f"❌ 파일을 열 수 없습니다: {파일경로}")
        return None
    
    # 2단계: 시스템틱 디렉토리로 이동
    directory = root_file.Get(시스템틱)
    if not directory:
        print(f"❌ 디렉토리를 찾을 수 없습니다: {시스템틱}")
        root_file.Close()
        return None
    
    # 3단계: 히스토그램 가져오기
    hist = directory.Get(히스토그램이름)
    if not hist:
        print(f"❌ 히스토그램을 찾을 수 없습니다: {히스토그램이름}")
        root_file.Close()
        return None
    
    # 4단계: 히스토그램 복사
    hist_clone = hist.Clone(f"{시스템틱}_{히스토그램이름}")
    hist_clone.SetDirectory(0)
    
    # 5단계: 파일 닫기
    root_file.Close()
    
    print(f"✅ 시스템틱 히스토그램 가져오기 성공: {시스템틱}/{히스토그램이름}")
    return hist_clone

def 여러_파일에서_히스토그램_가져오기(디렉토리경로, 히스토그램이름):
    """
    여러 루트 파일에서 같은 히스토그램을 가져와서 합치는 방법
    """
    import glob
    import os
    
    # 디렉토리에서 모든 .root 파일 찾기
    root_files = glob.glob(os.path.join(디렉토리경로, "*.root"))
    
    if not root_files:
        print(f"❌ 루트 파일을 찾을 수 없습니다: {디렉토리경로}")
        return None
    
    print(f"📁 {len(root_files)}개의 루트 파일을 찾았습니다")
    
    히스토그램들 = []
    
    for 파일경로 in root_files:
        파일명 = os.path.basename(파일경로)
        print(f"📖 처리 중: {파일명}")
        
        # 각 파일에서 히스토그램 가져오기
        hist = 시스템틱_히스토그램_가져오기(파일경로, 히스토그램이름)
        if hist:
            히스토그램들.append((파일명, hist))
    
    if not 히스토그램들:
        print("❌ 가져올 수 있는 히스토그램이 없습니다")
        return None
    
    # 첫 번째 히스토그램을 기준으로 합치기
    합친_히스토그램 = 히스토그램들[0][1].Clone(f"합친_{히스토그램이름}")
    
    # 나머지 히스토그램들 더하기
    for 파일명, hist in 히스토그램들[1:]:
        합친_히스토그램.Add(hist)
        print(f"➕ {파일명} 추가됨")
    
    print(f"✅ 총 {len(히스토그램들)}개 파일에서 히스토그램 합치기 완료")
    print(f"   - 최종 이벤트 수: {합친_히스토그램.Integral():.1f}")
    
    return 합친_히스토그램

# ===========================================
# 사용 예시:
# ===========================================
# 
# # 1. 단일 파일에서 히스토그램 가져오기
# hist = 간단한_히스토그램_가져오기("파일경로/파일명.root", "Topjetnum")
# 
# # 2. 시스템틱 히스토그램 가져오기
# hist_central = 시스템틱_히스토그램_가져오기("파일경로/파일명.root", "Topjetnum", "Central")
# hist_up = 시스템틱_히스토그램_가져오기("파일경로/파일명.root", "Topjetnum", "Up")
# hist_down = 시스템틱_히스토그램_가져오기("파일경로/파일명.root", "Topjetnum", "Down")
# 
# # 3. 여러 파일에서 히스토그램 합치기
# combined_hist = 여러_파일에서_히스토그램_가져오기(data_directory, "Topjetnum")
# 
# # 4. 히스토그램 그리기
# if hist:
#     hist.Draw()
#     ROOT.gPad.Update()

# ===========================================
# 실제 테스트 코드 (주석 해제해서 사용):
# ===========================================

def 테스트_실행():
    """
    루트 파일에서 데이터 가져오기 테스트
    실제 파일이 있는지 확인하고 테스트 실행
    """
    import os
    import glob
    
    print("🧪 루트 파일 데이터 가져오기 테스트 시작")
    print("=" * 50)
    
    # 1. 데이터 디렉토리 확인
    if not os.path.exists(data_directory):
        print(f"❌ 데이터 디렉토리가 존재하지 않습니다: {data_directory}")
        return
    
    # 2. 루트 파일 목록 확인
    root_files = glob.glob(os.path.join(data_directory, "*.root"))
    if not root_files:
        print(f"❌ 루트 파일을 찾을 수 없습니다: {data_directory}")
        return
    
    print(f"✅ {len(root_files)}개의 루트 파일을 찾았습니다")
    
    # 3. 첫 번째 파일로 테스트
    test_file = root_files[0]
    print(f"📁 테스트 파일: {os.path.basename(test_file)}")
    
    # 4. 파일 내부 구조 확인
    print("\n📋 파일 내부 구조:")
    root_file = ROOT.TFile.Open(test_file)
    if root_file and not root_file.IsZombie():
        root_file.ls()
        root_file.Close()
    else:
        print("❌ 파일을 열 수 없습니다")
        return
    
    # 5. 히스토그램 가져오기 테스트
    print("\n🔍 히스토그램 가져오기 테스트:")
    test_hist = 간단한_히스토그램_가져오기(test_file, "Topjetnum")
    
    if test_hist:
        print("✅ 테스트 성공!")
        
        # 6. 히스토그램 정보 출력
        print(f"\n📊 히스토그램 정보:")
        print(f"   - 이름: {test_hist.GetName()}")
        print(f"   - 제목: {test_hist.GetTitle()}")
        print(f"   - 빈 개수: {test_hist.GetNbinsX()}")
        print(f"   - X축 범위: {test_hist.GetXaxis().GetXmin():.1f} ~ {test_hist.GetXaxis().GetXmax():.1f}")
        print(f"   - 총 이벤트 수: {test_hist.Integral():.1f}")
        
        # 7. 간단한 플롯 생성
        print("\n🎨 간단한 플롯 생성 중...")
        canvas = ROOT.TCanvas("test_canvas", "Test Plot", 800, 600)
        test_hist.Draw("HIST")
        canvas.Update()
        
        # 8. 플롯 저장
        output_file = "test_histogram.png"
        canvas.SaveAs(output_file)
        print(f"✅ 플롯 저장됨: {output_file}")
        
        canvas.Close()
    else:
        print("❌ 테스트 실패!")

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