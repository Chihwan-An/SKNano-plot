#!/usr/bin/env python3
"""스펙 파일 하나를 한 프로세스에서 전부 처리 — condor job 의 본체.

한 프로세스가 (리전, 채널) 하나를 통째로 맡는 게 요점이다. plotter 의 TFile
캐시 덕분에 입력 ROOT 파일을 딱 한 번만 열고, 그 안에서 히스토그램 수십 개를
읽는다. v13 처럼 플롯마다 프로세스를 새로 띄우면 같은 파일을 수천 번 다시 연다.

  ./run_specs.py Resolve_sig_EE
  ./run_specs.py Resolve_sig_EE --stat-only --limit 2      # 빠른 확인
"""

import argparse
import os
import re
import shlex
import shutil
import sys
import time
import traceback

import ROOT

import config
import layout
import plotter


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("job", help="job 이름 (예: Resolve_sig_EE) — config.spec_jobs() 참고")
    ap.add_argument("--input", default=None, help="입력 디렉토리 (기본: config.INPUT_DIR)")
    ap.add_argument("--outdir", default=None, help="출력 디렉토리 (기본: out/<리전>)")
    ap.add_argument("--spec", default=None, metavar="FILE",
                    help="스펙 파일을 바꿔 끼운다 (기본: specs/<job>.txt). specs/tightcharge/ 같은 변형용")
    ap.add_argument("--stat-only", action="store_true", help="systematic 루프 생략")
    ap.add_argument("--histdir", default="", metavar="DIR",
                    help="syst 디렉토리 앞에 붙일 상위 디렉토리 "
                         "(DYCRStudy 산출물의 DYCR_Full / DYCR_ZptOnly / DYCR_NoCorr). "
                         "기본값은 빈 문자열 = 최상위 — 기존 산출물 그대로.")
    ap.add_argument("--limit", type=int, default=None, help="앞에서 N 개 플롯만 (스모크 테스트)")
    ap.add_argument("--match", default=None, metavar="REGEX",
                    help="--output 이 이 정규식에 걸리는 플롯만 그린다 "
                         r"(예: --match '_(mlljj|WRMass)(_fine)?$' -> mass 만)")
    ap.add_argument("--quiet", action="store_true", help="플롯별 로그 줄이기")
    ap.add_argument("--skip-existing", action="store_true",
                    help="png 가 이미 있는 플롯은 건너뛴다 (condor eviction 후 이어서)")
    ap.add_argument("--copy-local", default=None, metavar="DIR",
                    help="읽을 입력만 DIR 로 복사해서 거기서 읽는다 (워커 로컬 디스크)")
    opts = ap.parse_args()

    job = config.job_by_name(opts.job)
    if opts.spec:
        job = dict(job, spec=os.path.abspath(opts.spec))
    outdir = opts.outdir or job["outdir"]

    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptStat(0)
    # 히스토그램이 없을 때마다 나오는 ROOT 경고는 우리가 직접 다루므로 끈다.
    ROOT.gErrorIgnoreLevel = ROOT.kError

    t0 = time.time()
    print("=" * 78)
    print(f">> job {job['name']}   region={job['region']['dir']}   "
          f"channel={job['channel']}   flavour={job['flavour']}")
    print(f">> outdir {outdir}")

    inputs = plotter.Inputs(job["channel"], opts.input)
    print(inputs.report())

    draw_signal = job["region"]["key"] in config.SIGNAL_REGIONS
    if draw_signal:
        print(">> 시그널 오버레이: " + ", ".join(
            f"{lab}{'' if path else ' (파일 없음!)'}"
            for lab, path, _c, _st in inputs.signal_points))

    # 복사는 syst_coverage_report 앞에 와야 한다 — 거기서 처음으로 파일을 연다.
    if opts.copy_local:
        inputs = copy_inputs_local(inputs, opts.copy_local, job["channel"], draw_signal)

    print(syst_coverage_report(inputs, opts.stat_only, opts.histdir))

    parser = plotter.build_parser()
    defaults = ["--channel", job["channel"], "--outdir", outdir,
                "--label1", job["label1"], "--label2", job["label2"]]
    if opts.histdir:
        defaults += ["--histdir", opts.histdir]
    if opts.stat_only:
        defaults.append("--stat-only")
    if draw_signal:
        defaults.append("--signal")

    lines = read_spec(job["spec"])
    if opts.match:
        pat = re.compile(opts.match)
        before = len(lines)
        lines = [l for l in lines if pat.search(_arg_of(l, "--output"))]
        print(f">> --match {opts.match!r}: {before} -> {len(lines)} plots")
    if opts.limit:
        lines = lines[:opts.limit]
    print(f">> {len(lines)} plots from {os.path.relpath(job['spec'], config.BASE_DIR)}")
    print("=" * 78)

    ok, skipped, failed = 0, 0, []
    for n, line in enumerate(lines, 1):
        try:
            args = parser.parse_args(defaults + shlex.split(line))
        except SystemExit:
            failed.append((n, line, "인자 파싱 실패"))
            continue
        # png 는 두 tsv 다음에 쓰이므로, png 가 있으면 그 플롯은 끝난 것이다.
        # plotter 와 같은 규칙으로 하위 폴더까지 짚어야 한다 (layout.subdir).
        sub = layout.subdir(args.output, job["region"]["prefix"])
        done = os.path.join(outdir, sub or "", args.output + "_plot.png")
        if opts.skip_existing and os.path.isfile(done):
            skipped += 1
            continue
        try:
            if plotter.make_plot(args, inputs, quiet=opts.quiet):
                ok += 1
            else:
                failed.append((n, line, "MC 히스토그램 없음"))
        except Exception as exc:            # 한 플롯이 죽어도 나머지는 계속
            traceback.print_exc()
            failed.append((n, line, f"{type(exc).__name__}: {exc}"))

    plotter.close_all()

    dt = time.time() - t0
    print("\n" + "=" * 78)
    drawn = len(lines) - skipped
    print(f">> {job['name']}: {ok}/{drawn} plots, {dt/60:.1f} min "
          f"({dt/max(drawn,1):.1f} s/plot)"
          + (f"   (이미 있어서 건너뜀 {skipped})" if skipped else ""))
    if failed:
        print(f">> 실패 {len(failed)}개:")
        for n, line, why in failed:
            hist = _arg_of(line, "--hist")
            print(f"   line {n:>3}  {hist:<45} {why}")
    print("=" * 78)
    # condor 가 재시도할 수 있도록 실패는 non-zero 로 알린다.
    return 1 if failed else 0


def copy_inputs_local(inputs, dest, channel, draw_signal):
    """job 이 실제로 여는 파일만 dest 로 복사하고 거기를 보는 Inputs 를 돌려준다.

    왜: 플롯 하나가 히스토그램을 약 2,000 번 읽는다 (Central 60 + syst 22종 x
    Up/Down x MC 44). cProfile 로 재면 플롯 하나 47.4 s 중 46.9 s (99%) 가
    TDirectoryFile::Get 이다. 히스토그램 자체는 몇 KB 라 대역폭이 아니라 지연이
    전부다.

    한 번도 안 읽은 히스토그램으로 실측한 read 당 시간:

        /gv0 cold   35.6 ms
        로컬 사본    3.6 ms      -> 10 배

        복사 없음:  34 플롯 x 47 s       = 26 분
        복사 있음:  6.9 분 + 34 x 7.2 s  = 11 분   (복사 18 MB/s 기준)

    job 이 33 분 eviction 문턱 아래로 내려가는 게 핵심이다.

    함정: 이미 읽은 히스토그램을 다시 재면 1.9 ms 가 나온다 (NFS 클라이언트
    캐시). 그 숫자로는 "I/O 는 병목이 아니다" 라는 반대 결론이 나오므로,
    다시 잴 일이 있으면 반드시 안 건드린 히스토그램으로 잴 것.

    복사가 안 되면 원래 inputs 를 그대로 돌려준다 — 느릴 뿐 결과는 같다.
    """
    paths = [p for _s, p, _g in inputs.mc] + [p for _s, p in inputs.data]
    if draw_signal:
        paths += [p for _l, p, _c, _st in inputs.signal_points if p]

    total = sum(os.path.getsize(p) for p in paths)
    print(f">> 입력 {len(paths)}개 {total / 2**30:.1f} GB -> {dest}")
    t0 = time.time()
    try:
        os.makedirs(dest, exist_ok=True)
        free = shutil.disk_usage(dest).free
        if free < total * 1.05:
            print(f"   !! 공간 부족: 여유 {free / 2**30:.1f} GB < 필요 "
                  f"{total / 2**30:.1f} GB — 원래 경로에서 읽는다 "
                  "(condor_plotter.sub 의 request_disk 를 늘릴 것)")
            return inputs
        for src in paths:
            shutil.copyfile(src, os.path.join(dest, os.path.basename(src)))
    except OSError as exc:
        print(f"   !! 복사 실패 ({exc}) — 원래 경로에서 읽는다")
        return inputs

    dt = max(time.time() - t0, 1e-9)
    print(f">> 복사 완료 {dt:.0f} s ({total / 2**20 / dt:.0f} MB/s)")

    # 복사본을 같은 규칙으로 다시 분류해서 구성이 같은지 확인한다. 다르면
    # (복사 누락 등) 조용히 틀린 배경으로 그리느니 원래 경로로 되돌린다.
    local = plotter.Inputs(channel, dest)
    if len(local.mc) != len(inputs.mc) or len(local.data) != len(inputs.data):
        print(f"   !! 복사본 구성이 다르다 (MC {len(local.mc)}/{len(inputs.mc)}, "
              f"Data {len(local.data)}/{len(inputs.data)}) — 원래 경로에서 읽는다")
        return inputs
    print(f"   복사본 확인: MC {len(local.mc)}, Data {len(local.data)}"
          + (f", 시그널 {sum(1 for _l, p, _c, _s in local.signal_points if p)}"
             if draw_signal else ""))
    return local


def _arg_of(line, flag):
    toks = shlex.split(line)
    return toks[toks.index(flag) + 1] if flag in toks else "?"


def read_spec(path):
    if not os.path.isfile(path):
        raise IOError(f"스펙 파일 없음: {path}")
    out = []
    for raw in open(path):
        line = raw.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def syst_coverage_report(inputs, stat_only, histdir=""):
    if stat_only:
        return ">> --stat-only: systematic 루프를 건너뛴다"
    cov = inputs.syst_coverage(histdir)
    n_mc = len(inputs.mc)
    full = [s for s, n in cov.items() if n == n_mc]
    part = [(s, n) for s, n in cov.items() if 0 < n < n_mc]
    none = [s for s, n in cov.items() if n == 0]
    lines = [f">> Systematics: {len(cov)} requested, {n_mc} MC files"
             + (f"   (histdir {histdir}/)" if histdir else "")]
    lines.append(f"   전체 커버 {len(full):>2}: {', '.join(full) if full else '(none)'}")
    if part:
        lines.append("   부분 커버   : " + ", ".join(f"{s}({n}/{n_mc})" for s, n in part)
                     + "   <- DY 전용이면 정상")
    if none:
        lines.append(f"   !! 디렉토리 전무 {len(none)}: " + ", ".join(none))
        lines.append("      -> 이 nuisance 들은 band 에 0 으로 들어간다. "
                     "아날라이저가 아직 안 쓰는 것이면 정상, 아니면 입력이 잘못된 것.")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
