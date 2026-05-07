#!/usr/bin/env python3
"""
HTCondor 병렬 플롯 제출 스크립트
charge_tight_year_sep, charge_inclusive_year_sep 각 연도를 별도 job으로 제출
"""

import os
import subprocess
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
DATA6_BASE = Path("/data6/Users/achihwan/SKNanoAnalyzer-v13/plots/HNWR/reproduce/syst_plotter/hlt_ele_dif")

TYPES = [
    "charge_tight_year_sep",
    "charge_inclusive_year_sep",
]

YEARS = ["2022", "2022EE", "2023", "2023BPix"]


def create_dag_file(dag_path: Path):
    lines = ["# Auto-generated DAG file for parallel plotting", ""]

    job_names = []
    for type_name in TYPES:
        for year in YEARS:
            work_dir = DATA6_BASE / type_name / year
            job_name = f"{type_name}_{year}"
            job_names.append(job_name)

            exec_script = DATA6_BASE / "condor_files" / "run_plot.sh"
            sub_file = DATA6_BASE / "condor_files" / "condor_plot.sub"

            lines.append(f"JOB {job_name} {sub_file}")
            lines.append(f'VARS {job_name} jobname="{job_name}"')
            lines.append(f'VARS {job_name} exec_script="{exec_script}"')
            lines.append(f'VARS {job_name} work_dir="{work_dir}"')
            lines.append("")

    lines.append("# Retry failed jobs up to 2 times")
    for job_name in job_names:
        lines.append(f"RETRY {job_name} 2")

    dag_path.write_text("\n".join(lines))
    print(f"[INFO] DAG file created: {dag_path}")


def submit_dag(dag_path: Path, dry_run: bool = False):
    cmd = ["condor_submit_dag", "-f"]
    if dry_run:
        cmd.append("-no_submit")
    cmd.append(str(dag_path))

    print(f"[INFO] Running: {' '.join(cmd)}")
    if not dry_run:
        result = subprocess.run(cmd, cwd=BASE_DIR)
        return result.returncode == 0
    return True


def main():
    parser = argparse.ArgumentParser(description="HTCondor 병렬 플롯 제출")
    parser.add_argument("--dry-run", action="store_true",
                        help="실제 제출 없이 DAG 파일만 생성")
    args = parser.parse_args()

    log_dir = DATA6_BASE / "condor_files" / "condor_logs"
    log_dir.mkdir(exist_ok=True)
    print(f"[INFO] Log directory: {log_dir}")

    dag_path = DATA6_BASE / "condor_files" / "plotter.dag"
    create_dag_file(dag_path)
    submit_dag(dag_path, args.dry_run)

    if not args.dry_run:
        print("\n[INFO] DAG submitted. Monitor with:")
        print("  condor_q")
        print("  condor_watch_q")
        print(f"  tail -f {DATA6_BASE}/condor_files/condor_logs/condor.log")


if __name__ == "__main__":
    main()
