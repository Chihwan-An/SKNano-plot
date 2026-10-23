#!/usr/bin/env python3
"""condor 제출 전 30초 점검.

19 개 job 을 날리고 몇 시간 뒤에 오타를 발견하는 걸 막는다.

  1. 입력 디렉토리와 .root 파일 목록
  2. 샘플 -> 배경 그룹 매핑 (SAMPLE_RULES 에 안 걸리는 파일 경고)
  3. systematic 디렉토리 커버리지
  4. 스펙에 적힌 모든 히스토그램 이름이 실제로 존재하는지

  ./check_inputs.py                 # 전부
  ./check_inputs.py --job Resolve_sig_EE
"""

import argparse
import os
import shlex
import sys

import ROOT

import config
import plotter


def central_keys(path):
    """파일의 Central/ 안에 있는 히스토그램 이름 집합."""
    f = plotter.open_file(path)
    d = f.Get("Central")
    if not d:
        return set()
    return {k.GetName() for k in d.GetListOfKeys()}


def spec_hists(job):
    """스펙 파일의 (히스토그램 이름, --output) 목록."""
    out = []
    for raw in open(job["spec"]):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        toks = shlex.split(line)
        try:
            out.append((toks[toks.index("--hist") + 1], toks[toks.index("--output") + 1]))
        except ValueError:
            out.append((None, line))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default=None, help="입력 디렉토리 (기본: config.INPUT_DIR)")
    ap.add_argument("--job", default=None, help="이 job 만 점검")
    ap.add_argument("--quiet-hists", action="store_true", help="누락 목록을 줄여서 출력")
    opts = ap.parse_args()

    ROOT.gROOT.SetBatch(True)
    ROOT.gErrorIgnoreLevel = ROOT.kError

    input_dir = opts.input or config.INPUT_DIR
    problems = []

    print("=" * 78)
    print(f"입력 디렉토리: {input_dir}")
    if not os.path.isdir(input_dir):
        print("  !! 존재하지 않는다.")
        return 1
    roots = sorted(f for f in os.listdir(input_dir) if f.endswith(".root"))
    print(f"  .root 파일 {len(roots)}개")
    if not roots:
        print("  !! 비어 있다. 아날라이저가 아직 안 돌았거나 경로가 다르다.")
        return 1
    if config.INPUT_PREFIX:
        n_use = sum(1 for f in roots if f.startswith(config.INPUT_PREFIX))
        print(f"  그중 접두사 {config.INPUT_PREFIX!r} 인 {n_use}개만 쓴다 "
              f"(나머지 {len(roots) - n_use}개는 다른 산출물)")
        if not n_use:
            print("  !! 접두사가 맞는 파일이 하나도 없다. config.INPUT_PREFIX 를 확인할 것.")
            return 1

    jobs = [config.job_by_name(opts.job)] if opts.job else config.spec_jobs()
    channels = sorted({j["channel"] for j in jobs})

    # --- 1. 샘플 그룹 매핑 -------------------------------------------------
    inputs_by_ch = {}
    for ch in channels:
        print("\n" + "=" * 78)
        inp = plotter.Inputs(ch, input_dir)
        inputs_by_ch[ch] = inp
        print(inp.report())
        if inp.unclassified:
            problems.append(f"[{ch}] SAMPLE_RULES 미분류 {len(inp.unclassified)}개")
        if not inp.data:
            problems.append(f"[{ch}] Data 파일이 하나도 없다")

    # --- 2. systematic 커버리지 -------------------------------------------
    for ch in channels:
        inp = inputs_by_ch[ch]
        print("\n" + "-" * 78)
        print(f"[{ch}] systematic 디렉토리 커버리지 (MC {len(inp.mc)}개 기준)")
        cov = inp.syst_coverage()
        n_mc = len(inp.mc)
        for syst in config.SYST_LIST:
            n = cov[syst]
            mark = "OK  " if n == n_mc else ("부분" if n else "없음")
            if n != n_mc:
                print(f"   {mark} {syst:<24} {n:>3}/{n_mc}")
        missing = [s for s, n in cov.items() if n == 0]
        if missing:
            problems.append(f"[{ch}] syst 디렉토리가 전무한 nuisance {len(missing)}개: "
                            + ", ".join(missing[:6]) + (" ..." if len(missing) > 6 else ""))
        print(f"   -> 전체 커버 {sum(1 for n in cov.values() if n == n_mc)}"
              f" / 부분 {sum(1 for n in cov.values() if 0 < n < n_mc)}"
              f" / 없음 {len(missing)}")

    # --- 3. 히스토그램 존재 여부 -------------------------------------------
    print("\n" + "=" * 78)
    print("히스토그램 존재 확인 (Central/ 기준)")
    keycache = {}
    for job in jobs:
        inp = inputs_by_ch[job["channel"]]
        pairs = spec_hists(job)
        bad_spec = [o for h, o in pairs if h is None]
        names = [h for h, _o in pairs if h]

        mc_paths = [p for _s, p, _g in inp.mc]
        data_paths = [p for _s, p in inp.data]
        for path in mc_paths + data_paths:
            if path not in keycache:
                keycache[path] = central_keys(path)

        missing_mc, missing_data = [], []
        for h in names:
            if not any(h in keycache[p] for p in mc_paths):
                missing_mc.append(h)
            elif not any(h in keycache[p] for p in data_paths):
                missing_data.append(h)

        # SR 히스토그램은 데이터에 안 채워지는 게 정상이다 (blind).
        data_blind = [h for h in missing_data if h.startswith("SR_")]
        data_real = [h for h in missing_data if not h.startswith("SR_")]
        status = "OK" if not (missing_mc or bad_spec or data_real) else "!!"
        note = f" (+SR blind {len(data_blind)})" if data_blind else ""
        print(f"  {status} {job['name']:<24} {len(names):>3} hists"
              f"   MC 누락 {len(missing_mc):>3}   Data 누락 {len(data_real):>3}{note}")
        # 시그널 오버레이는 SR job 에만 붙는다. 질량점마다 채워진 히스토그램이
        # 다르므로 부분 커버리지는 정상이고, 0 개일 때만 문제로 잡는다.
        if job["region"]["key"] in config.SIGNAL_REGIONS:
            for label, path, _c, _st in inp.signal_points:
                if path is None:
                    print(f"       !! 시그널 파일 없음: {label}")
                    problems.append(f"[{job['name']}] 시그널 파일 없음: {label}")
                    continue
                if path not in keycache:
                    keycache[path] = central_keys(path)
                have = sum(1 for h in names if h in keycache[path])
                mark = "OK" if have == len(names) else "--"
                print(f"       {mark} 시그널 {label:<34} {have:>3}/{len(names)} hists")
                if have == 0:
                    problems.append(f"[{job['name']}] 시그널 {label} 에 "
                                    "스펙 히스토그램이 하나도 없다")

        if bad_spec:
            problems.append(f"[{job['name']}] --hist/--output 없는 스펙 줄 {len(bad_spec)}개")
        if missing_mc:
            problems.append(f"[{job['name']}] 어떤 MC 파일에도 없는 히스토그램 {len(missing_mc)}개")
            show = missing_mc if not opts.quiet_hists else missing_mc[:5]
            for h in show:
                print(f"       MC 없음  : {h}")
            if len(show) < len(missing_mc):
                print(f"       ... 외 {len(missing_mc) - len(show)}개")
        if data_real:
            for h in data_real[:5]:
                print(f"       Data 없음: {h}   <- CR 인데 데이터가 없다")
            if len(data_real) > 5:
                print(f"       ... 외 {len(data_real) - 5}개")
            problems.append(f"[{job['name']}] CR 인데 Data 에 없는 히스토그램 {len(data_real)}개")

    plotter.close_all()

    print("\n" + "=" * 78)
    if problems:
        print(f"문제 {len(problems)}건:")
        for p in problems:
            print(f"  - {p}")
        print("\n제출 전에 위 항목을 확인할 것.")
        return 1
    print("문제 없음. condor 제출 가능.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
