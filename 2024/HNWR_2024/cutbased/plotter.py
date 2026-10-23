"""HNWR 2024 배경 kinematic 플롯 — 스택 + syst band + Data/MC ratio.

v13 의 syst_plotter (EE.py / MM.py) 에서 온 코드지만 세 가지가 다르다.

1. EE/MM 을 한 스크립트로 합쳤다. v13 은 두 파일이 DATA_FILES / EXCLUDE_SAMPLES /
   기본 라벨 세 줄만 다른 채로 리전마다 복사돼 20 벌이 돌아다녔다.
2. 시그널 관련 코드가 전부 빠졌다 (배경만 그린다).
3. TFile 핸들을 캐시한다. 이게 배치 실행의 핵심이다 — v13 은 플롯 하나당
   프로세스 하나였고 그 안에서 파일 85 개를 (Central + syst x Up/Down) 번
   다시 열었다. 캐시가 있으면 한 프로세스가 리전 하나를 통째로 처리하면서
   파일을 딱 한 번만 연다.

   캐시를 켜면 클론된 히스토그램을 C++ 소유로 넘기면 안 된다. v13 의
   ROOT.SetOwnership(h, False) 를 지운 이유다. 그게 남아 있으면 배치
   프로세스에서 히스토그램이 영구히 쌓인다.
"""

import argparse
import ctypes
import math
import os
import re
import shlex

import numpy as np
import ROOT

import config
import layout


# ---------------------------------------------------------------------------
# ROOT 파일 캐시
# ---------------------------------------------------------------------------

_FILE_CACHE = {}
_DIRS_CACHE = {}
# has_dir() 의 (path, dirname) -> bool. 'DYCR_Full/JES_Up' 같은 2 단 경로는
# 최상위 키 집합으로 못 재므로 TFile::GetDirectory 결과를 여기 담아둔다.
_HASDIR_CACHE = {}

# syst 디렉토리가 실제로 있었는지 집계. 없으면 Central 로 대체되는데, 그러면
# 그 샘플의 variation 기여가 0 이 되므로 조용히 넘어가면 안 된다.
SYST_COVERAGE = {}

# 파일을 열어둔 채로 f.Get() 을 하면 읽어온 히스토그램이 그 TFile 의 메모리
# 디렉토리에 등록되어 파일을 닫을 때까지 살아 있는다. 플롯 하나당 수천 번
# 읽으므로 job 하나가 수 GB 까지 부푼다 (실측: 13/34 플롯에서 2.1 GB).
# AddDirectory(False) 로 등록 자체를 막고, 읽은 객체의 소유권을 파이썬에
# 넘겨 참조가 사라지면 해제되게 한다.
ROOT.TH1.AddDirectory(False)


def open_file(path):
    f = _FILE_CACHE.get(path)
    if f is None:
        f = ROOT.TFile.Open(path)
        if not f or f.IsZombie():
            raise IOError(f"cannot open {path}")
        _FILE_CACHE[path] = f
    return f


def syst_dirs(path):
    """파일의 최상위 디렉토리 이름 집합 (Central, JES_Up, ...)."""
    dirs = _DIRS_CACHE.get(path)
    if dirs is None:
        f = open_file(path)
        dirs = {k.GetName() for k in f.GetListOfKeys()}
        _DIRS_CACHE[path] = dirs
    return dirs


def has_dir(path, dirname):
    """파일 안에 이 디렉토리가 있는가.

    'JES_Up' 같은 최상위 이름은 syst_dirs() 의 키 집합으로 재고, DYCRStudy 처럼
    'DYCR_Full/JES_Up' 로 한 단 더 들어가는 경우는 GetDirectory 로 확인한다.
    둘 다 결과를 캐시한다 — 플롯 하나가 파일당 수십 번 물어본다.
    """
    if "/" not in dirname:
        return dirname in syst_dirs(path)
    key = (path, dirname)
    hit = _HASDIR_CACHE.get(key)
    if hit is None:
        hit = bool(open_file(path).GetDirectory(dirname))
        _HASDIR_CACHE[key] = hit
    return hit


def close_all():
    for f in _FILE_CACHE.values():
        f.Close()
    _FILE_CACHE.clear()
    _DIRS_CACHE.clear()
    _HASDIR_CACHE.clear()


def root_color(spec):
    """'kGreen+2' 같은 문자열을 ROOT 색 번호로."""
    m = re.match(r"^(k[A-Za-z]+)\s*(?:([+-])\s*(\d+))?$", spec)
    if not m:
        raise ValueError(f"bad colour spec: {spec!r}")
    val = getattr(ROOT, m.group(1))
    if m.group(2):
        val = val + int(m.group(3)) if m.group(2) == "+" else val - int(m.group(3))
    return val


# ---------------------------------------------------------------------------
# 히스토그램 로드
# ---------------------------------------------------------------------------

def get_hist(path, sys_dir, hist_name, x_max, custom_bins=None, rebin_factor=1):
    """파일에서 히스토그램을 읽고 리빈 + 오버플로우 합산까지 마쳐 돌려준다.

    없으면 None. 반환된 히스토그램은 어느 TDirectory 에도 속하지 않는
    (모듈 상단의 AddDirectory(False)) 파이썬 소유 객체라, 참조가 사라지면
    해제된다. 파일을 열어둔 채 돌리므로 이게 성립해야 메모리가 안 샌다.
    """
    if not has_dir(path, sys_dir):
        return None

    f = open_file(path)
    h = f.Get(f"{sys_dir}/{hist_name}")
    if not h:
        return None
    # AddDirectory(False) 라 이 객체는 어느 디렉토리에도 속하지 않는다.
    # 파이썬이 해제하도록 소유권을 명시적으로 가져온다.
    ROOT.SetOwnership(h, True)

    if custom_bins is not None:
        bin_edges = np.array(custom_bins, dtype=float)
        h_re = h.Rebin(len(bin_edges) - 1, h.GetName() + "_re", bin_edges)
        ROOT.SetOwnership(h_re, True)
        h = h_re
    elif rebin_factor > 1:
        h.Rebin(rebin_factor)

    # 마지막 빈에 x_max 이후의 모든 값(오버플로우 포함)을 합산
    actual_xmax = min(x_max, h.GetXaxis().GetXmax())
    last_bin = h.FindBin(actual_xmax - 0.001)
    nbins = h.GetNbinsX()
    cont, err_sq = 0.0, 0.0
    for i in range(last_bin, nbins + 2):
        cont += h.GetBinContent(i)
        err_sq += h.GetBinError(i) ** 2
        if i > last_bin:
            h.SetBinContent(i, 0)
            h.SetBinError(i, 0)
    h.SetBinContent(last_bin, cont)
    h.SetBinError(last_bin, math.sqrt(err_sq))
    return h


# ---------------------------------------------------------------------------
# 입력 목록
# ---------------------------------------------------------------------------

class Inputs:
    """한 채널에서 쓸 MC/Data 파일 목록. 프로세스당 한 번만 만든다."""

    def __init__(self, channel, input_dir=None):
        self.channel = channel
        self.input_dir = input_dir or config.INPUT_DIR
        self.mc = []        # [(stem, path, group)]
        self.data = []      # [(stem, path)]
        self.unclassified = []
        self.other_output = []   # config.INPUT_PREFIX 가 안 붙은 다른 산출물
        self.signal = []         # 배경 스택에서 뺀 시그널 전체
        self._scan()
        # 스택과 별개로, 골라서 선으로 겹쳐 그릴 질량점 (--signal 일 때만 쓴다).
        self.signal_points = config.signal_files(channel, self.input_dir)
        self.signal_warned = set()

    def _scan(self):
        if not os.path.isdir(self.input_dir):
            raise IOError(f"input directory not found: {self.input_dir}")
        data_globs = config.CHANNELS[self.channel]["data"]
        for fname in sorted(os.listdir(self.input_dir)):
            if not fname.endswith(".root"):
                continue
            # 같은 디렉토리에 옛 산출물이 섞여 있다. config.INPUT_PREFIX 로 이번
            # 산출물만 고르고, 그룹 매칭은 접두사를 뗀 이름으로 한다.
            stem = config.sample_stem(fname[:-5])
            if stem is None:
                self.other_output.append(fname[:-5])
                continue
            if stem in config.EXCLUDE_STEMS:
                continue
            path = os.path.join(self.input_dir, fname)
            if config.is_signal(stem):
                self.signal.append(stem)
                continue
            if config.is_data(stem):
                # 이 채널의 스트림만 Data 로 쓰고, 다른 스트림은 통째로 버린다.
                if config.is_data(stem, data_globs):
                    self.data.append((stem, path))
                continue
            group, _rule = config.classify_sample(stem)
            if group is None:
                self.unclassified.append(stem)
                group = "Others"
            self.mc.append((stem, path, group))

    def syst_coverage(self, histdir=""):
        """{syst: (해당 디렉토리를 가진 MC 파일 수)}.

        디렉토리가 없는 샘플은 Central 로 대체되어 variation 기여가 0 이 된다.
        ZPtRw*/DYReshapeBin* 은 DY 전용이라 부분 커버리지가 정상이지만,
        0/N 인 항목은 아날라이저가 아직 그 nuisance 를 안 쓴다는 뜻이다.

        histdir 를 주면 그 아래에서 (DYCRStudy 의 'DYCR_Full/JES_Up') 센다.
        같은 Inputs 로 시나리오를 바꿔 물어볼 수 있게 histdir 별로 캐시한다.
        """
        cache = getattr(self, "_cov", None)
        if cache is None:
            cache = self._cov = {}
        if histdir in cache:
            return cache[histdir]
        pref = f"{histdir}/" if histdir else ""
        cov = {}
        for syst in config.SYST_LIST:
            n = sum(1 for _s, path, _g in self.mc
                    if has_dir(path, f"{pref}{syst}_Up") and has_dir(path, f"{pref}{syst}_Down"))
            cov[syst] = n
        cache[histdir] = cov
        return cov

    def report(self):
        lines = [f">> Input: {self.input_dir}",
                 f">> Channel {self.channel}: {len(self.mc)} MC, {len(self.data)} Data files"]
        by_group = {}
        for stem, _p, g in self.mc:
            by_group.setdefault(g, []).append(stem)
        for g in config.BACKGROUND_GROUPS:
            names = by_group.get(g, [])
            lines.append(f"   {g:<10} {len(names):>3} : {', '.join(names) if names else '(none)'}")
        if self.signal:
            lines.append(f"   -- 시그널 {len(self.signal)}개 제외 (config.SIGNAL_GLOBS)")
        if self.other_output:
            lines.append(f"   -- 접두사 {config.INPUT_PREFIX!r} 가 없거나 DROP_GLOBS(mass-binned W+jets)인 파일 "
                         f"{len(self.other_output)}개 제외 (다른 산출물)")
        if self.unclassified:
            lines.append(f"   !! SAMPLE_RULES 에 안 걸려 Others 로 넣은 파일 {len(self.unclassified)}개: "
                         + ", ".join(self.unclassified))
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# ratio 패널 포인트
# ---------------------------------------------------------------------------

def draw_ratio_points(h_ratio, r_min, r_max, x_min, x_max, keeper):
    """Data/MC points, keeping the visible part of an off-scale point's bar.

    ROOT's "PE" drops a point entirely once its marker leaves the frame, error
    bar included, so a bin that is high but still compatible with 1 disappears
    and reads as an empty bin. Here the in-range points are drawn as before and
    each off-scale one contributes the piece of its bar that lies inside the
    frame, with a small arrow at the edge marking the direction it went.
    """
    g = ROOT.TGraphAsymmErrors()
    n = 0
    span = r_max - r_min
    for i in range(1, h_ratio.GetNbinsX() + 1):
        x = h_ratio.GetBinCenter(i)
        lo_edge = h_ratio.GetBinLowEdge(i)
        up_edge = lo_edge + h_ratio.GetBinWidth(i)
        if up_edge <= x_min or lo_edge >= x_max:
            continue                      # bin lies wholly outside the frame
        y = h_ratio.GetBinContent(i)
        e = h_ratio.GetBinError(i)
        if y == 0.0 and e == 0.0:
            continue                      # bin the data never filled
        w = 0.5 * h_ratio.GetBinWidth(i)
        if r_min <= y <= r_max:
            g.SetPoint(n, x, y)
            g.SetPointError(n, w, w, e, e)
            n += 1
            continue
        lo = max(y - e, r_min)
        hi = min(y + e, r_max)
        if lo < hi:                       # the bar reaches back into the frame
            seg = ROOT.TLine(x, lo, x, hi)
            seg.SetLineColor(h_ratio.GetLineColor())
            seg.SetLineWidth(h_ratio.GetLineWidth())
            seg.Draw()
            keeper.append(seg)
        up = y > r_max
        y0 = r_max - 0.07 * span if up else r_min + 0.07 * span
        y1 = r_max - 0.01 * span if up else r_min + 0.01 * span
        arr = ROOT.TArrow(x, y0, x, y1, 0.010, "|>")
        arr.SetLineColor(h_ratio.GetLineColor())
        arr.SetFillColor(h_ratio.GetLineColor())
        arr.SetLineWidth(h_ratio.GetLineWidth())
        arr.Draw()
        keeper.append(arr)

    if n:
        g.SetMarkerStyle(h_ratio.GetMarkerStyle())
        g.SetMarkerSize(h_ratio.GetMarkerSize())
        g.SetMarkerColor(h_ratio.GetMarkerColor())
        g.SetLineColor(h_ratio.GetLineColor())
        g.SetLineWidth(h_ratio.GetLineWidth())
        g.Draw("P SAME")
        keeper.append(g)


# ---------------------------------------------------------------------------
# 인자
# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(description="HNWR 2024 배경 플롯")
    p.add_argument("--hist",   type=str, required=True, help="불러올 히스토그램 이름")
    p.add_argument("--output", type=str, required=True, help="결과물 파일 이름 (확장자 없이)")
    p.add_argument("--rebin",  type=int, default=1)
    p.add_argument("--bins",   type=str, default=None, help="커스텀 빈 경계 (쉼표 구분)")
    p.add_argument("--ymin",   type=float, default=5.0)
    p.add_argument("--ymax",   type=float, default=None)
    p.add_argument("--xmin",   type=float, default=None)
    p.add_argument("--xmax",   type=float, default=None)
    p.add_argument("--xlabel", type=str, default=None)
    p.add_argument("--logy",   action="store_false", default=True, help="Y축 로그 스케일 해제")
    p.add_argument("--rmin",   type=float, default=0.7)   # 2026-08-28: ratio pad 0.7-1.3 (user request)
    p.add_argument("--rmax",   type=float, default=1.3)
    p.add_argument("--label1", type=str, default=None, help="채널 라벨 (예: ee)")
    p.add_argument("--label2", type=str, default=None, help="영역 라벨 (예: Resolved SR)")
    p.add_argument("--channel", type=str, default=None, choices=sorted(config.CHANNELS),
                   help="데이터 스트림 선택 (배치 실행에서는 드라이버가 넣어준다)")
    p.add_argument("--outdir", type=str, default=".", help="png/tsv 를 쓸 디렉토리")
    p.add_argument("--input",  type=str, default=None, help="입력 디렉토리 (기본: config.INPUT_DIR)")
    p.add_argument("--stat-only", action="store_true", default=False,
                   help="systematic 루프를 건너뛴다 (빠른 확인용)")
    p.add_argument("--histdir", type=str, default="",
                   help="syst 디렉토리 앞에 붙일 상위 디렉토리 "
                        "(예: DYCRStudy 산출물의 DYCR_Full -> DYCR_Full/Central, "
                        "DYCR_Full/JES_Up). 기본값은 빈 문자열 = 최상위.")
    p.add_argument("--signal", action="store_true", default=False,
                   help="config.SIGNAL_POINTS 를 스택 위에 선으로 겹쳐 그린다 "
                        "(배치 실행에서는 SR job 에만 드라이버가 넣어준다)")
    return p


def parse_spec_line(line, parser):
    """스펙 파일 한 줄 -> argparse Namespace."""
    return parser.parse_args(shlex.split(line, comments=True))


# ---------------------------------------------------------------------------
# 본체
# ---------------------------------------------------------------------------

TSV_BASE_COLS = ["Bin", "BinLow", "BinHigh", "MC_Total", "Data",
                 "DYJets", "TT", "Nonprompt", "Others",
                 "Stat_pct", "SystUp_pct", "SystDn_pct", "TotalUp_pct", "TotalDn_pct"]


def tsv_header(syst_list):
    cols = list(TSV_BASE_COLS)
    cols += [f"{s}_pct" for s in syst_list]
    for g in config.BACKGROUND_GROUPS:
        cols += [f"{g}_Stat_pct", f"{g}_SystUp_pct", f"{g}_SystDn_pct",
                 f"{g}_TotalUp_pct", f"{g}_TotalDn_pct"]
        cols += [f"{g}_{s}_pct" for s in syst_list]
    return "\t".join(cols)


def _fmt_row(row):
    return "\t".join(f"{v:.4f}" if isinstance(v, float) else str(v) for v in row)


def _accumulate(acc, h, name):
    """acc 가 없으면 h 의 복제로 시작하고, 있으면 더한다."""
    if acc is None:
        acc = h.Clone(name)
        acc.SetDirectory(0)
    else:
        acc.Add(h)
    return acc


def make_plot(args, inputs, quiet=False):
    """플롯 하나. 성공하면 png 경로, MC 가 하나도 없으면 None."""
    hist_name = args.hist
    is_blind = hist_name.startswith("SR_")
    syst_list = [] if args.stat_only else config.SYST_LIST
    # DYCRStudy 처럼 syst 디렉토리가 한 단 안에 있는 산출물용. 기본값은 "" 라
    # sysdir("Central") == "Central" — 기존 산출물은 아무것도 안 달라진다.
    histdir = getattr(args, "histdir", "") or ""

    def sysdir(name):
        return f"{histdir}/{name}" if histdir else name

    custom_bins = [float(x) for x in args.bins.split(",")] if args.bins else None
    x_min_req = args.xmin if args.xmin is not None else (custom_bins[0] if custom_bins else 40)
    x_max_req = args.xmax if args.xmax is not None else (custom_bins[-1] if custom_bins else 2000)

    keeper = []

    def log(msg):
        if not quiet:
            print(msg)

    log(f"\n>> {hist_name} -> {args.output}" + ("  [BLIND]" if is_blind else ""))

    # ---- Central ----------------------------------------------------------
    h_data = None
    group_hists = {g: None for g in config.BACKGROUND_GROUPS}

    for stem, path in inputs.data:
        h = get_hist(path, sysdir("Central"), hist_name, x_max_req, custom_bins, args.rebin)
        if not h:
            continue
        if h_data is None:
            h_data = h.Clone("h_data_total")
            h_data.SetDirectory(0)
        else:
            h_data.Add(h)

    central_by_path = {}      # syst 디렉토리가 없는 샘플의 fallback 으로 재사용
    for stem, path, group in inputs.mc:
        h = get_hist(path, sysdir("Central"), hist_name, x_max_req, custom_bins, args.rebin)
        if not h:
            continue
        central_by_path[path] = h
        if group_hists[group] is None:
            group_hists[group] = h.Clone(f"h_group_{group}")
            group_hists[group].SetDirectory(0)
        else:
            group_hists[group].Add(h)

    h_total_mc = None
    for g in config.BACKGROUND_GROUPS:
        if group_hists[g] is None:
            continue
        if h_total_mc is None:
            h_total_mc = group_hists[g].Clone("h_total_mc_nominal")
            h_total_mc.SetDirectory(0)
        else:
            h_total_mc.Add(group_hists[g])

    if h_total_mc is None:
        print(f"   !! MC 히스토그램을 하나도 못 읽었다: {hist_name} — 건너뜀")
        return None

    x_min = max(x_min_req, h_total_mc.GetXaxis().GetXmin())
    x_max = min(x_max_req, h_total_mc.GetXaxis().GetXmax())
    n_bins = h_total_mc.GetNbinsX()

    # ---- 시그널 오버레이 --------------------------------------------------
    # 스택/h_total_mc/syst band/ratio/TSV 어디에도 안 들어간다. Central 만 읽고
    # 배경과 같은 binning 인자를 써서 축을 맞춘다.
    signal_hists = []                      # [(label, hist, color, style)]
    if args.signal:
        for label, path, color, style in inputs.signal_points:
            if path is None:
                if label not in inputs.signal_warned:
                    inputs.signal_warned.add(label)
                    print(f"   !! 시그널 파일 없음: {label} — 오버레이에서 뺀다")
                continue
            h_sig = get_hist(path, sysdir("Central"), hist_name, x_max_req, custom_bins, args.rebin)
            if not h_sig:
                # 안 채워진 히스토그램은 아예 안 만들어지므로 질량점마다 있는
                # 히스토그램이 다르다. 그 점만 빼고 나머지는 그대로 그린다.
                log(f"   -- 시그널 {label}: 이 히스토그램이 없다 — 건너뜀")
                continue
            signal_hists.append((label, h_sig, color, style))

    # ---- systematics ------------------------------------------------------
    sum_sq_up = np.zeros(n_bins + 2)
    sum_sq_dn = np.zeros(n_bins + 2)
    syst_per_bin = {s: np.zeros(n_bins + 2) for s in syst_list}

    sum_sq_up_group = {g: np.zeros(n_bins + 2) for g in config.BACKGROUND_GROUPS}
    sum_sq_dn_group = {g: np.zeros(n_bins + 2) for g in config.BACKGROUND_GROUPS}
    syst_per_bin_group = {s: {g: np.zeros(n_bins + 2) for g in config.BACKGROUND_GROUPS}
                          for s in syst_list}

    sum_sq_up_int = 0.0
    sum_sq_dn_int = 0.0
    syst_per_int = {s: 0.0 for s in syst_list}
    sum_sq_up_group_int = {g: 0.0 for g in config.BACKGROUND_GROUPS}
    sum_sq_dn_group_int = {g: 0.0 for g in config.BACKGROUND_GROUPS}
    syst_per_int_group = {s: {g: 0.0 for g in config.BACKGROUND_GROUPS} for s in syst_list}

    coverage = inputs.syst_coverage(histdir) if syst_list else {}
    for syst in syst_list:
        # 어떤 MC 샘플도 이 디렉토리를 안 가지고 있으면 up=down=Central 이라
        # variation 이 정확히 0 이다. 루프를 돌 이유가 없다 (TSV 에는 0 으로 남는다).
        if coverage.get(syst, 0) == 0:
            continue
        mc_sum = {"Up": None, "Down": None}
        group_sum = {"Up":   {g: None for g in config.BACKGROUND_GROUPS},
                     "Down": {g: None for g in config.BACKGROUND_GROUPS}}

        for stem, path, group in inputs.mc:
            varied = {"Up":   get_hist(path, sysdir(f"{syst}_Up"),   hist_name, x_max, custom_bins, args.rebin),
                      "Down": get_hist(path, sysdir(f"{syst}_Down"), hist_name, x_max, custom_bins, args.rebin)}
            # 이 샘플에 해당 systematic 디렉토리가 없으면 (DY 전용 syst 의 non-DY
            # 샘플 등) Central 로 대체한다. 빠뜨리면 그 샘플이 up/down 합에서
            # 통째로 빠져 가짜 variation 이 된다.
            if varied["Up"] is None or varied["Down"] is None:
                # Central 은 위에서 이미 읽어뒀다. 다시 읽으면 (특히 DY 전용 syst 의
                # non-DY 샘플에서) 같은 파일을 수백 번 더 두드리게 된다.
                central = central_by_path.get(path)
                if central is None:
                    continue
                for tag in ("Up", "Down"):
                    if varied[tag] is None:
                        varied[tag] = central

            for tag, h in varied.items():
                mc_sum[tag] = _accumulate(mc_sum[tag], h, f"h_{tag}")
                group_sum[tag][group] = _accumulate(group_sum[tag][group], h, f"h_{tag}_{group}")

        h_mc_up, h_mc_dn = mc_sum["Up"], mc_sum["Down"]
        h_group_up, h_group_dn = group_sum["Up"], group_sum["Down"]
        if not (h_mc_up and h_mc_dn):
            continue

        for i in range(1, n_bins + 1):
            nom = h_total_mc.GetBinContent(i)
            d_up = h_mc_up.GetBinContent(i) - nom
            d_dn = h_mc_dn.GetBinContent(i) - nom
            syst_per_bin[syst][i] = (max(abs(d_up), abs(d_dn)) / nom * 100) if nom > 0 else 0.0
            sum_sq_up[i] += max(0, d_up, d_dn) ** 2
            sum_sq_dn[i] += max(0, -d_up, -d_dn) ** 2

            for g in config.BACKGROUND_GROUPS:
                if not (h_group_up[g] and h_group_dn[g] and group_hists[g]):
                    continue
                g_nom = group_hists[g].GetBinContent(i)
                g_up = h_group_up[g].GetBinContent(i) - g_nom
                g_dn = h_group_dn[g].GetBinContent(i) - g_nom
                syst_per_bin_group[syst][g][i] = (max(abs(g_up), abs(g_dn)) / g_nom * 100) if g_nom > 0 else 0.0
                sum_sq_up_group[g][i] += max(0, g_up, g_dn) ** 2
                sum_sq_dn_group[g][i] += max(0, -g_up, -g_dn) ** 2

        nom_int = h_total_mc.Integral()
        du_int = h_mc_up.Integral() - nom_int
        dd_int = h_mc_dn.Integral() - nom_int
        syst_per_int[syst] = (max(abs(du_int), abs(dd_int)) / nom_int * 100) if nom_int > 0 else 0.0
        sum_sq_up_int += max(0, du_int, dd_int) ** 2
        sum_sq_dn_int += max(0, -du_int, -dd_int) ** 2

        for g in config.BACKGROUND_GROUPS:
            if not (h_group_up[g] and h_group_dn[g] and group_hists[g]):
                continue
            g_int = group_hists[g].Integral()
            gu = h_group_up[g].Integral() - g_int
            gd = h_group_dn[g].Integral() - g_int
            syst_per_int_group[syst][g] = (max(abs(gu), abs(gd)) / g_int * 100) if g_int > 0 else 0.0
            sum_sq_up_group_int[g] += max(0, gu, gd) ** 2
            sum_sq_dn_group_int[g] += max(0, -gu, -gd) ** 2

    # ---- 빈별 표 + TSV ----------------------------------------------------
    g_syst = ROOT.TGraphAsymmErrors(n_bins)
    g_ratio_band = ROOT.TGraphAsymmErrors(n_bins)
    g_ratio_stat = ROOT.TGraphAsymmErrors(n_bins)
    keeper += [g_syst, g_ratio_band, g_ratio_stat]

    rows = []
    for i in range(1, n_bins + 1):
        x = h_total_mc.GetBinCenter(i)
        y = h_total_mc.GetBinContent(i)
        w = h_total_mc.GetBinWidth(i) / 2.0
        stat = h_total_mc.GetBinError(i)
        err_up = math.sqrt(stat ** 2 + sum_sq_up[i])
        err_dn = math.sqrt(stat ** 2 + sum_sq_dn[i])

        g_syst.SetPoint(i - 1, x, y)
        g_syst.SetPointError(i - 1, w, w, err_dn, err_up)
        if y <= 0:
            continue
        g_ratio_band.SetPoint(i - 1, x, 1.0)
        g_ratio_band.SetPointError(i - 1, w, w, err_dn / y, err_up / y)
        g_ratio_stat.SetPoint(i - 1, x, 1.0)
        g_ratio_stat.SetPointError(i - 1, w, w, stat / y, stat / y)

        row = [i, h_total_mc.GetBinLowEdge(i), h_total_mc.GetBinLowEdge(i + 1), y,
               h_data.GetBinContent(i) if h_data else 0.0]
        row += [group_hists[g].GetBinContent(i) if group_hists[g] else 0.0
                for g in ("DYJets", "TT", "Nonprompt", "Others")]
        row += [stat / y * 100, math.sqrt(sum_sq_up[i]) / y * 100,
                math.sqrt(sum_sq_dn[i]) / y * 100, err_up / y * 100, err_dn / y * 100]
        row += [syst_per_bin[s][i] for s in syst_list]
        for g in config.BACKGROUND_GROUPS:
            g_nom = group_hists[g].GetBinContent(i) if group_hists[g] else 0.0
            g_stat = group_hists[g].GetBinError(i) if group_hists[g] else 0.0
            if g_nom > 0:
                row += [g_stat / g_nom * 100,
                        math.sqrt(sum_sq_up_group[g][i]) / g_nom * 100,
                        math.sqrt(sum_sq_dn_group[g][i]) / g_nom * 100,
                        math.sqrt(g_stat ** 2 + sum_sq_up_group[g][i]) / g_nom * 100,
                        math.sqrt(g_stat ** 2 + sum_sq_dn_group[g][i]) / g_nom * 100]
            else:
                row += [0.0] * 5
            row += [syst_per_bin_group[s][g][i] for s in syst_list]
        rows.append(row)

    # 리전 폴더에 평평하게 떨구지 않고 flavour/오브젝트/OS-SS 로 바로 들어간다.
    # 폴더 결정은 layout.py 가 하며 organize_files.py 와 같은 규칙을 쓴다.
    out_base = os.path.join(layout.resolve_outdir(args.outdir, args.output),
                            args.output)
    header = tsv_header(syst_list)
    with open(out_base + ".tsv", "w") as fh:
        fh.write(header + "\n")
        for row in rows:
            fh.write(_fmt_row(row) + "\n")

    # ---- 적분 TSV ---------------------------------------------------------
    total_mc = h_total_mc.Integral()
    stat_err = ctypes.c_double(0.0)
    h_total_mc.IntegralAndError(1, n_bins, stat_err)
    total_stat = stat_err.value

    int_row = ["Total", h_total_mc.GetBinLowEdge(1), h_total_mc.GetBinLowEdge(n_bins + 1),
               total_mc, h_data.Integral() if h_data else 0.0]
    int_row += [group_hists[g].Integral() if group_hists[g] else 0.0
                for g in ("DYJets", "TT", "Nonprompt", "Others")]
    if total_mc > 0:
        int_row += [total_stat / total_mc * 100,
                    math.sqrt(sum_sq_up_int) / total_mc * 100,
                    math.sqrt(sum_sq_dn_int) / total_mc * 100,
                    math.sqrt(total_stat ** 2 + sum_sq_up_int) / total_mc * 100,
                    math.sqrt(total_stat ** 2 + sum_sq_dn_int) / total_mc * 100]
        int_row += [syst_per_int[s] for s in syst_list]
    else:
        int_row += [0.0] * (5 + len(syst_list))
    for g in config.BACKGROUND_GROUPS:
        g_tot = group_hists[g].Integral() if group_hists[g] else 0.0
        g_stat_err = ctypes.c_double(0.0)
        if group_hists[g]:
            group_hists[g].IntegralAndError(1, n_bins, g_stat_err)
        g_stat = g_stat_err.value
        if g_tot > 0:
            int_row += [g_stat / g_tot * 100,
                        math.sqrt(sum_sq_up_group_int[g]) / g_tot * 100,
                        math.sqrt(sum_sq_dn_group_int[g]) / g_tot * 100,
                        math.sqrt(g_stat ** 2 + sum_sq_up_group_int[g]) / g_tot * 100,
                        math.sqrt(g_stat ** 2 + sum_sq_dn_group_int[g]) / g_tot * 100]
            int_row += [syst_per_int_group[s][g] for s in syst_list]
        else:
            int_row += [0.0] * (5 + len(syst_list))
    with open(out_base + "_integrated.tsv", "w") as fh:
        fh.write(header + "\n")
        fh.write(_fmt_row(int_row) + "\n")

    log(f"   MC {total_mc:12.1f}" +
        ("   Data blinded" if is_blind else f"   Data {h_data.Integral() if h_data else 0:12.1f}") +
        f"   ({n_bins} bins)")

    # ---- 그리기 -----------------------------------------------------------
    _draw(args, h_total_mc, h_data, group_hists, g_syst, g_ratio_band, g_ratio_stat,
          x_min, x_max, is_blind, out_base, keeper, signal_hists)
    log(f"   saved {out_base}_plot.png")
    return out_base + "_plot.png"


def _draw_xticks(pad, xticks, logy, keeper, label_size):
    """변환된 x 축 (symlog 등) 의 눈금과 라벨을 패드 아래/위 테두리에 직접 그린다.
    xticks = [(그려진 좌표, "라벨"), ...]; label_size 0 이면 눈금만 (윗 패드)."""
    pad.cd(); pad.Update()
    lo, hi = pad.GetUymin(), pad.GetUymax()

    def y(frac):
        v = lo + frac * (hi - lo)
        return 10 ** v if logy else v

    for x, lab in xticks:
        if not (pad.GetUxmin() <= x <= pad.GetUxmax()):
            continue
        for a, b in ((0.0, 0.035), (0.965, 1.0)):
            ln = ROOT.TLine(x, y(a), x, y(b)); ln.Draw(); keeper.append(ln)
        if label_size:
            t = ROOT.TLatex(); t.SetTextSize(label_size); t.SetTextFont(42); t.SetTextAlign(23)
            t.DrawLatex(x, y(-0.06), lab); keeper.append(t)
    pad.Modified()


def _draw(args, h_total_mc, h_data, group_hists, g_syst, g_ratio_band, g_ratio_stat,
          x_min, x_max, is_blind, out_base, keeper, signal_hists=()):
    # 스택은 yield 오름차순으로 쌓는다 (작은 것이 맨 아래). v13 과 같은 순서.
    valid = [(g, group_hists[g].Integral()) for g in config.BACKGROUND_GROUPS if group_hists[g]]
    ordered = sorted(valid, key=lambda t: t[1])
    stack = ROOT.THStack("stack", "")
    for g_key, _y in ordered:
        h = group_hists[g_key]
        col = root_color(config.BACKGROUND_GROUPS[g_key][0])
        h.SetFillColor(col)
        h.SetLineColor(col)
        stack.Add(h)
    keeper.append(stack)

    c = ROOT.TCanvas("c_" + args.output, "c", 800, 900)
    p1 = ROOT.TPad("p1", "p1", 0, 0.3, 1, 1)
    p2 = ROOT.TPad("p2", "p2", 0, 0, 1, 0.3)
    keeper += [c, p1, p2]
    p1.SetBottomMargin(0.02)
    p2.SetTopMargin(0.02)
    p2.SetBottomMargin(0.35)
    p1.Draw()
    p2.Draw()

    p1.cd()
    if args.logy:
        p1.SetLogy()
    # 가변 폭 비닝을 로그 x 축에 그리면 좁은 저(低)값 bin 들이 펴져서 보인다. 기본은 꺼짐이고,
    # 쓰는 쪽에서 args.logx 를 넣어줄 때만 켠다 (두 패드가 같은 축을 써야 눈금이 맞는다).
    if getattr(args, "logx", False):
        p1.SetLogx()
        p2.SetLogx()
    # x 축을 이미 변환해서 (예: symlog) 히스토그램을 채운 경우. 축 자체의 눈금은 변환된 좌표라
    # 뜻이 없으므로 지우고, args.xticks = [(변환좌표, "라벨"), ...] 를 손으로 그린다.
    xticks = getattr(args, "xticks", None)
    y_max = args.ymax if args.ymax else max(
        [h_data.GetMaximum() if (h_data and not is_blind) else 0,
         h_total_mc.GetMaximum()]
        + [h.GetMaximum() for _l, h, _c, _st in signal_hists]) * (100 if args.logy else 1.5)

    h_dummy = h_total_mc.Clone("h_dummy")
    h_dummy.Reset()
    h_dummy.GetYaxis().SetTitle(getattr(args, "ylabel", None) or "Events / bin")
    h_dummy.GetYaxis().SetTitleSize(0.05)
    h_dummy.GetYaxis().SetTitleOffset(1.1)
    h_dummy.GetXaxis().SetLabelSize(0)
    if xticks:
        h_dummy.GetXaxis().SetTickLength(0)
    h_dummy.SetMinimum(args.ymin)
    h_dummy.SetMaximum(y_max)
    h_dummy.GetXaxis().SetRangeUser(x_min, x_max)
    h_dummy.Draw("HIST")
    keeper.append(h_dummy)

    # 범례 스와치가 비지 않도록 그리기 전에 스타일을 다 잡아둔다.
    g_syst.SetFillColorAlpha(ROOT.kGray + 2, 0.8)
    g_syst.SetFillStyle(3013)
    g_ratio_stat.SetFillColorAlpha(ROOT.kOrange, 0.6)
    g_ratio_stat.SetFillStyle(1001)
    g_ratio_band.SetFillColorAlpha(ROOT.kGray + 2, 0.8)
    g_ratio_band.SetFillStyle(3013)
    for _label, h_sig, col, style in signal_hists:
        h_sig.SetLineColor(root_color(col))
        h_sig.SetLineStyle(style)
        h_sig.SetLineWidth(3)
        h_sig.SetFillStyle(0)     # 스택이 아니라 선이다

    stack.Draw("HIST SAME")
    g_syst.Draw("SAME E2")

    if h_data and not is_blind:
        h_data.SetMarkerStyle(20)
        h_data.SetMarkerSize(1.2)
        h_data.SetLineColor(ROOT.kBlack)
        h_data.Draw("PE SAME")

    for _label, h_sig, _c, _st in signal_hists:
        h_sig.Draw("HIST SAME")
        keeper.append(h_sig)

    # 시그널 2줄이 더 들어가면 기본 높이로는 빠듯하다.
    # 시그널 라벨("m_{W_{R}}=4 TeV, m_{N}=0.2 TeV")은 길어서 프레임 오른쪽
    # 끝(1 - RightMargin = 0.90)을 넘는다. 왼쪽으로 넓히고 심볼 칸을 줄인다.
    # args.legend_box = (x1, y1, x2, y2) / args.legend_text_size 로 덮어쓸 수 있다 (기본값은 그대로).
    box = getattr(args, "legend_box", None)
    if box:
        leg = ROOT.TLegend(*box)
        leg.SetMargin(0.18 if signal_hists else 0.25)
    elif signal_hists:
        leg = ROOT.TLegend(0.47, 0.52, 0.89, 0.88)
        leg.SetMargin(0.18)
    else:
        leg = ROOT.TLegend(0.55, 0.58, 0.92, 0.88)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(getattr(args, "legend_text_size", None) or 0.035)
    for g_key, _y in reversed(ordered):
        leg.AddEntry(group_hists[g_key], config.BACKGROUND_GROUPS[g_key][1], "f")
    if h_data and not is_blind:
        leg.AddEntry(h_data, "Data", "pe")
    for label, h_sig, _c, _st in signal_hists:
        leg.AddEntry(h_sig, label, "l")
    leg.AddEntry(g_syst, "Stat #oplus Syst Unc.", "f")
    if not is_blind:
        # blind 플롯은 ratio 패널을 통째로 가리므로 stat-only 밴드가 어디에도
        # 안 나온다. 범례에 남겨두면 빈 스와치가 찍힌다.
        leg.AddEntry(g_ratio_stat, "Stat. Unc.", "f")
    leg.Draw()
    keeper.append(leg)

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(61); latex.SetTextSize(0.045); latex.DrawLatex(0.12, 0.93, "CMS")
    latex.SetTextFont(52); latex.SetTextSize(0.035); latex.DrawLatex(0.21, 0.93, config.CMS_SUBLABEL)
    latex.SetTextFont(42); latex.SetTextSize(0.030); latex.SetTextAlign(31)
    latex.DrawLatex(0.90, 0.93, config.LUMI_LABEL)
    latex.SetTextAlign(11); latex.SetTextFont(62); latex.SetTextSize(0.06)
    latex.DrawLatex(0.18, 0.82, args.label1 or "")
    latex.SetTextFont(42); latex.SetTextSize(getattr(args, "label2_size", None) or 0.060)
    latex.DrawLatex(0.18, 0.75, args.label2 or "")
    if getattr(args, "label3", None):      # optional small third line under the region label
        latex.SetTextSize(0.032); latex.DrawLatex(0.18, 0.70, args.label3)
    keeper.append(latex)
    p1.RedrawAxis()
    if xticks:
        _draw_xticks(p1, xticks, args.logy, keeper, label_size=0.0)

    p2.cd()
    h_frame = h_dummy.Clone("h_frame")
    h_frame.Reset()
    h_frame.GetYaxis().SetTitle("Data / MC")
    h_frame.SetMinimum(args.rmin)
    h_frame.SetMaximum(args.rmax)
    h_frame.GetXaxis().SetTitle(args.xlabel if args.xlabel else args.hist)
    h_frame.GetXaxis().SetTitleSize(0.1); h_frame.GetXaxis().SetLabelSize(0.11)
    if xticks:
        h_frame.GetXaxis().SetTickLength(0); h_frame.GetXaxis().SetLabelSize(0)
    if xticks or getattr(args, "logx", False):
        # 로그(또는 변환) 축에서는 맨 오른쪽 라벨이 축 제목 자리에 오므로 제목을 한 줄 내린다.
        h_frame.GetXaxis().SetTitleOffset(1.25)
    h_frame.GetYaxis().SetTitleSize(0.1); h_frame.GetYaxis().SetLabelSize(0.11)
    h_frame.GetYaxis().SetTitleOffset(0.45); h_frame.GetYaxis().SetNdivisions(505)
    h_frame.GetXaxis().SetRangeUser(x_min, x_max)
    h_frame.Draw("HIST")
    keeper.append(h_frame)

    if is_blind:
        bl = ROOT.TLatex()
        bl.SetNDC(); bl.SetTextAlign(22); bl.SetTextSize(0.18)
        bl.SetTextFont(62); bl.SetTextColor(ROOT.kBlack)
        bl.DrawLatex(0.5, 0.5, "Blinded")
        keeper.append(bl)
    else:
        g_ratio_stat.Draw("SAME E2")
        g_ratio_band.Draw("SAME E2")
        if h_data:
            h_ratio = h_data.Clone("h_ratio")
            h_ratio.Divide(h_total_mc)
            draw_ratio_points(h_ratio, args.rmin, args.rmax, x_min, x_max, keeper)
            keeper.append(h_ratio)
        line = ROOT.TLine(x_min, 1, x_max, 1)
        line.SetLineStyle(2)
        line.Draw()
        keeper.append(line)

    p2.RedrawAxis()
    if xticks:
        _draw_xticks(p2, xticks, False, keeper, label_size=0.11)
    c.SaveAs(out_base + "_plot.png")
    c.Close()


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.channel is None:
        parser.error("--channel 이 필요하다 (EE 또는 MM)")
    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gErrorIgnoreLevel = ROOT.kWarning
    inputs = Inputs(args.channel, args.input)
    print(inputs.report())
    make_plot(args, inputs)
    close_all()


if __name__ == "__main__":
    main()
