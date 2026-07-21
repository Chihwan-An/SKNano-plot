import ROOT

def draw_multiline_text(x, y, color, lines, text_size=0.035, line_spacing=1.2, font=42):
    """
    NDC 좌표 (x, y)를 중심으로 여러 줄의 텍스트를 그립니다.
    """
    latex = ROOT.TLatex()
    latex.SetTextAlign(22)  # 가로/세로 정중앙 정렬
    latex.SetTextSize(text_size)
    latex.SetTextColor(color)
    latex.SetTextFont(font)
    
    n_lines = len(lines)
    # 줄 간격을 고려한 전체 높이 계산
    total_height = (n_lines - 1) * text_size * line_spacing
    
    for i, line in enumerate(lines):
        # 각 줄의 y 좌표 오프셋 계산 (중앙 정렬)
        y_offset = (total_height / 2.0) - (i * text_size * line_spacing)
        latex.DrawLatexNDC(x, y + y_offset, line)

# 기본 설정값
y_split = 0.55  # 가로 구분선 (Same Flavor / Different Flavor)
x_cut1 = 0.5    # 150 GeV 선
x_cut2 = 0.7    # 200 GeV 선
x_min = 0.1     # 축 시작점
x_max = 1.0     # 축 끝점
y_min = 0.1
y_max = 1.0

# 캔버스 생성
canvas = ROOT.TCanvas("canvas", "Physics Regions", 1000, 800)
canvas.SetMargin(0.15, 0.05, 0.15, 0.05) # 여백 설정

# --- 1. 배경 영역 색칠 (TBox 사용) ---
# TBox(x1, y1, x2, y2)
boxes = []
def add_region_box(x1, y1, x2, y2, color, alpha=0.2):
    box = ROOT.TBox(x1, y1, x2, y2)
    box.SetFillColorAlpha(color, alpha)
    box.Draw()
    boxes.append(box) # 가비지 컬렉션 방지

# Top Left: Low mll (Same Flavor)
add_region_box(x_min, y_split, x_cut1, y_max, ROOT.kRed)
# Bottom Left: Low mll (Different Flavor)
add_region_box(x_min, y_min, x_cut1, y_split, ROOT.kGray)
# Top Middle: Validation? (Same Flavor)
add_region_box(x_cut1, y_split, x_cut2, y_max, ROOT.kGray)
# Bottom Middle: Validation? (Different Flavor)
add_region_box(x_cut1, y_min, x_cut2, y_split, ROOT.kGray)
# Top Right: Signal Region (Same Flavor)
add_region_box(x_cut2, y_split, x_max, y_max, ROOT.kBlue)
# Bottom Right: Application Region (Different Flavor)
add_region_box(x_cut2, y_min, x_max, y_split, ROOT.kGreen)

# --- 2. 축 및 구분선 그리기 ---
# X축 화살표
arrow_x = ROOT.TArrow(x_min, y_min, x_max, y_min, 0.03, "|>")
arrow_x.SetLineWidth(3)
arrow_x.Draw()

# Y축 화살표
arrow_y = ROOT.TArrow(x_min, y_min, x_min, y_max, 0.03, "|>")
arrow_y.SetLineWidth(3)
arrow_y.Draw()

# 점선 구분선들
lines = []
def draw_dash_line(x1, y1, x2, y2):
    l = ROOT.TLine(x1, y1, x2, y2)
    l.SetLineStyle(2)
    l.SetLineWidth(2)
    l.Draw()
    lines.append(l)

draw_dash_line(x_min, y_split, x_max, y_split) # 가로선
draw_dash_line(x_cut1, y_min, x_cut1, y_max)   # 150선
draw_dash_line(x_cut2, y_min, x_cut2, y_max)   # 200선

# --- 3. 텍스트 라벨 (축) ---
latex = ROOT.TLatex()
latex.SetTextFont(42)
latex.SetTextSize(0.045)

# X축 눈금값
latex.DrawLatexNDC(x_min-0.02, 0.06, "60")
latex.DrawLatexNDC(x_cut1-0.03, 0.06, "150")
latex.DrawLatexNDC(x_cut2-0.03, 0.06, "400")
latex.DrawLatexNDC(x_max-0.15, 0.05, "m(ll) [GeV]")

# Y축 영역 이름 (회전 90도)
latex.SetTextAngle(90)
latex.DrawLatexNDC(0.06, (y_split + y_max)/2.0 - 0.1, "Same Flavor")
latex.DrawLatexNDC(0.06, (y_min + y_split)/2.0 - 0.1, "Different Flavor")
latex.SetTextAngle(0)

# --- 4. 영역별 중앙 텍스트 배치 ---
# 함수: draw_multiline_text(중앙x, 중앙y, 색상, 내용리스트, 크기)

# 1. Low m(ll) Region (Top Left)
draw_multiline_text((x_min + x_cut1)/2, (y_split + y_max)/2, ROOT.kRed+2, 
                    ["Resolved", "DY CR"], 0.04, font=62)

# 2. Low m(ll) AR Region (Bottom Left)
#draw_multiline_text((x_min + x_cut1)/2, (y_min + y_split)/2, ROOT.kOrange+2, 
#                    ["QCD Fake", "Measurement", "Region", "(AR-like)"], 0.04, font=62)

# 3. Signal Region (Top Right)
draw_multiline_text((x_cut2 + x_max)/2, (y_split + y_max)/2, ROOT.kBlue+2, 
                    ["Resolved", "SR"], 0.045, font=62)

# 4. Application Region (Bottom Right)
draw_multiline_text((x_cut2 + x_max)/2, (y_min + y_split)/2, ROOT.kGreen+2, 
                    ["Resolved", "Flavor CR"], 0.045, font=62)


# 출력 및 저장
canvas.Update()
canvas.SaveAs("Regions_resolved_refined.png")