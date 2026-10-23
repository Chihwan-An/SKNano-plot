#!/usr/bin/env python3
"""condor 제출 파일 생성 — condor/condor_plotter.sub 와 condor/plotter.dag.

job 하나 = 스펙 파일 하나 = (리전, 채널). 플롯 job 전부가 끝나면 organize
job 하나가 결과를 계층 구조로 옮긴다.

경로를 파일에 박아 넣으므로 트리를 옮겼으면 다시 돌려야 한다.

  ./make_dag.py                 # 전부
  ./make_dag.py --stat-only     # 각 job 을 --stat-only 로 (빠른 확인용)
  ./make_dag.py --job Resolve_sig_EE --job Resolve_sig_MM
"""

import argparse
import os

import config

SUB_TEMPLATE = """\
universe = vanilla
executable = $(exec_script)
arguments = "$(jobargs)"

initialdir = {base}

output = {logs}/$(jobname).out
error  = {logs}/$(jobname).err
log    = {logs}/condor.log

# 컨테이너는 wrapper 가 직접 띄운다 (+singularityimage 를 쓰지 않는다).
getenv = True

request_memory = {memory}
request_cpus = 1
request_disk = 2GB

notification = Never
should_transfer_files = NO

queue
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--job", action="append", default=None,
                    help="이 job 만 DAG 에 넣는다 (반복 가능)")
    ap.add_argument("--stat-only", action="store_true", help="모든 job 에 --stat-only")
    ap.add_argument("--input", default=None, help="입력 디렉토리 override")
    ap.add_argument("--memory", default="4GB", help="request_memory (기본 4GB)")
    ap.add_argument("--retry", type=int, default=2, help="실패 시 재시도 횟수")
    ap.add_argument("--no-organize", action="store_true", help="organize job 을 넣지 않는다")
    ap.add_argument("--name", default="plotter", help="DAG 파일 이름 (기본: plotter)")
    opts = ap.parse_args()

    base = config.BASE_DIR
    cdir = os.path.join(base, "condor")
    logs = os.path.join(cdir, "logs")
    os.makedirs(logs, exist_ok=True)

    sub_path = os.path.join(cdir, "condor_plotter.sub")
    with open(sub_path, "w") as fh:
        fh.write(SUB_TEMPLATE.format(base=base, logs=logs, memory=opts.memory))

    jobs = config.spec_jobs()
    if opts.job:
        wanted = set(opts.job)
        unknown = wanted - {j["name"] for j in jobs}
        if unknown:
            raise SystemExit(f"모르는 job: {', '.join(sorted(unknown))}")
        jobs = [j for j in jobs if j["name"] in wanted]

    extra = []
    if opts.stat_only:
        extra.append("--stat-only")
    if opts.input:
        extra += ["--input", opts.input]
    extra_str = (" " + " ".join(extra)) if extra else ""

    run_specs = os.path.join(cdir, "run_specs.sh")
    run_org = os.path.join(cdir, "run_organize.sh")

    dag_path = os.path.join(cdir, f"{opts.name}.dag")
    with open(dag_path, "w") as fh:
        fh.write(f"# HNWR 2024 배경 플롯 DAG — {len(jobs)} plot jobs"
                 f"{'' if opts.no_organize else ' + 1 organize'}\n")
        fh.write(f"# make_dag.py 가 생성. 손으로 고치지 말고 make_dag.py 를 다시 돌릴 것.\n\n")
        for j in jobs:
            fh.write(f"JOB {j['name']} {sub_path}\n")
            fh.write(f'VARS {j["name"]} jobname="{j["name"]}"\n')
            fh.write(f'VARS {j["name"]} exec_script="{run_specs}"\n')
            fh.write(f'VARS {j["name"]} jobargs="{j["name"]}{extra_str}"\n\n')

        if not opts.no_organize:
            fh.write(f"# 모든 플롯 job 이 끝난 뒤 결과 정리\n")
            fh.write(f"JOB organize {sub_path}\n")
            fh.write('VARS organize jobname="organize"\n')
            fh.write(f'VARS organize exec_script="{run_org}"\n')
            fh.write('VARS organize jobargs=""\n\n')
            fh.write("PARENT " + " ".join(j["name"] for j in jobs) + " CHILD organize\n\n")

        fh.write(f"# 실패한 job 은 {opts.retry} 번까지 재시도\n")
        for j in jobs:
            fh.write(f"RETRY {j['name']} {opts.retry}\n")
        if not opts.no_organize:
            fh.write(f"RETRY organize {opts.retry}\n")

    n_plots = sum(count_plots(j["spec"]) for j in jobs)
    print(f"생성: {sub_path}")
    print(f"생성: {dag_path}")
    print(f"  plot jobs {len(jobs)}개, 플롯 총 {n_plots}개"
          f"{'' if opts.no_organize else ', organize job 1개'}")
    if extra:
        print(f"  각 job 추가 인자: {' '.join(extra)}")
    print(f"\n제출 (condor 서브밋 노드에서):")
    print(f"  condor_submit_dag -f {dag_path}")


def count_plots(spec):
    if not os.path.isfile(spec):
        return 0
    return sum(1 for line in open(spec)
               if line.strip() and not line.strip().startswith("#"))


if __name__ == "__main__":
    main()
