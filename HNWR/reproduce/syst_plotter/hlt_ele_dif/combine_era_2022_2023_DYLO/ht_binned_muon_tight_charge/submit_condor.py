#!/usr/bin/env python3
"""
HTCondor 병렬 플롯 제출 스크립트
각 plotter.sh를 별도 job으로 제출하고, 모든 job 완료 후 organize_files.py 실행
"""

import os
import subprocess
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()

# 처리할 plotter 디렉토리 목록
PLOTTERS = [
    "boost/DY",
    "boost/FLV",
    "boost/sr",
    "resolve/DY",
    "resolve/FLV",
    "resolve/sr",
]


def create_dag_file(plotters: list, dag_path: Path, include_organize: bool = True):
    """DAG 파일 생성"""
    lines = ["# Auto-generated DAG file for parallel plotting", ""]

    plotter_jobs = []
    for i, plotter_dir in enumerate(plotters):
        job_name = plotter_dir.replace("/", "_")
        plotter_jobs.append(job_name)

        full_path = BASE_DIR / plotter_dir
        if not (full_path / "plotter.sh").exists():
            print(f"[WARNING] plotter.sh not found: {plotter_dir}")
            continue

        # JOB 정의
        lines.append(f"JOB {job_name} {BASE_DIR}/condor_files/condor_plotter.sub")
        lines.append(f'VARS {job_name} jobname="{job_name}"')
        lines.append(f'VARS {job_name} exec_script="{BASE_DIR}/condor_files/run_plotter.sh"')
        lines.append(f'VARS {job_name} work_dir="{full_path}"')
        lines.append("")

    # organize job (모든 plotter 완료 후 실행)
    if include_organize and plotter_jobs:
        lines.append("# Organize files after all plotters complete")
        lines.append(f"JOB organize {BASE_DIR}/condor_files/condor_plotter.sub")
        lines.append(f'VARS organize jobname="organize"')
        lines.append(f'VARS organize exec_script="{BASE_DIR}/condor_files/run_organize.sh"')
        lines.append(f'VARS organize work_dir="{BASE_DIR}"')
        lines.append("")

        # 의존성 설정: organize는 모든 plotter가 완료된 후 실행
        parent_list = " ".join(plotter_jobs)
        lines.append(f"PARENT {parent_list} CHILD organize")
        lines.append("")

    # Retry 설정
    lines.append("# Retry failed jobs up to 2 times")
    for job_name in plotter_jobs:
        lines.append(f"RETRY {job_name} 2")
    if include_organize:
        lines.append("RETRY organize 2")

    dag_path.write_text("\n".join(lines))
    print(f"[INFO] DAG file created: {dag_path}")


def submit_dag(dag_path: Path, dry_run: bool = False, force: bool = True):
    """DAG 제출"""
    cmd = ["condor_submit_dag"]
    if force:
        cmd.append("-force")
    if dry_run:
        cmd.append("-no_submit")
    cmd.append(str(dag_path))

    print(f"[INFO] Running: {' '.join(cmd)}")
    if not dry_run:
        result = subprocess.run(cmd, cwd=BASE_DIR)
        return result.returncode == 0
    return True


def submit_individual_jobs(plotters: list, dry_run: bool = False, include_organize: bool = True):
    """개별 job 제출 (DAG 없이)"""
    job_ids = []

    for plotter_dir in plotters:
        job_name = plotter_dir.replace("/", "_")
        full_path = BASE_DIR / plotter_dir

        if not (full_path / "plotter.sh").exists():
            print(f"[WARNING] plotter.sh not found: {plotter_dir}")
            continue

        cmd = [
            "condor_submit",
            f"jobname={job_name}",
            f"exec_script={BASE_DIR}/condor_files/run_plotter.sh {full_path}",
            f"work_dir={full_path}",
            f"{BASE_DIR}/condor_files/condor_plotter.sub",
        ]

        print(f"[INFO] Submitting: {plotter_dir}")
        if not dry_run:
            result = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[OK] {job_name} submitted")
            else:
                print(f"[ERROR] {job_name} failed: {result.stderr}")

    if include_organize:
        print("\n[NOTE] organize_files.py는 모든 job이 끝난 후 수동으로 실행하세요:")
        print(f"  cd {BASE_DIR} && python organize_files.py")


def main():
    parser = argparse.ArgumentParser(description="HTCondor 병렬 플롯 제출")
    parser.add_argument("--dry-run", action="store_true",
                        help="실제 제출 없이 DAG 파일만 생성")
    parser.add_argument("--no-dag", action="store_true",
                        help="DAG 없이 개별 job으로 제출")
    parser.add_argument("--no-organize", action="store_true",
                        help="organize_files.py 자동 실행 비활성화")
    parser.add_argument("--plotters", nargs="+", default=PLOTTERS,
                        help="제출할 plotter 디렉토리 (기본값: 전체)")
    args = parser.parse_args()

    # condor_logs 디렉토리 생성
    log_dir = BASE_DIR / "condor_files" / "condor_logs"
    log_dir.mkdir(exist_ok=True)
    print(f"[INFO] Log directory: {log_dir}")

    include_organize = not args.no_organize

    if args.no_dag:
        submit_individual_jobs(args.plotters, args.dry_run, include_organize)
    else:
        dag_path = BASE_DIR / "condor_files" / "plotter.dag"
        create_dag_file(args.plotters, dag_path, include_organize)
        submit_dag(dag_path, args.dry_run)

        if not args.dry_run:
            print("\n[INFO] DAG submitted. Monitor with:")
            print("  condor_q")
            print("  condor_watch_q")
            print(f"  tail -f {BASE_DIR}/condor_files/condor_logs/condor.log")


if __name__ == "__main__":
    main()
