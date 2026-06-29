#!/usr/bin/env python3
"""
submit_cutflow.py — Generate condor submit file and optionally submit it.

Scans SIG_DIR for all WR{wr}N{n}{EE,MM}.root files,
collects unique (WR, N) mass points, and submits one condor job per point.

Usage:
  python submit_cutflow.py              # generate + submit
  python submit_cutflow.py --dry-run    # generate only, print what would be submitted
"""

import argparse
import os
import re
import subprocess
import sys

SIG_DIR = "/gv0/Users/achihwan/SKNanoOutput/Reproduce20_002_copy/2023/sig/"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTDIR     = os.path.join(SCRIPT_DIR, "cutflow_output")
LOG_DIR    = os.path.join(SCRIPT_DIR, "condor_logs")
SUB_FILE   = os.path.join(SCRIPT_DIR, "cutflow_condor.sub")
WRAPPER    = os.path.join(SCRIPT_DIR, "run_cutflow.sh")


def collect_mass_points():
    pattern = re.compile(r"WR(\d+)N(\d+)(EE|MM)\.root")
    pairs = set()
    for fname in os.listdir(SIG_DIR):
        m = pattern.match(fname)
        if m:
            wr, n, _ = m.groups()
            pairs.add((int(wr), int(n)))
    return sorted(pairs)


def write_submit_file(mass_points):
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(OUTDIR, exist_ok=True)

    header = f"""\
universe   = vanilla
executable = {WRAPPER}
getenv     = True

request_cpus   = 1
request_memory = 2GB
request_disk   = 1GB
notification   = Never
should_transfer_files = NO

log    = {LOG_DIR}/cutflow_$(WR)_$(N).log
output = {LOG_DIR}/cutflow_$(WR)_$(N).out
error  = {LOG_DIR}/cutflow_$(WR)_$(N).err

"""

    with open(SUB_FILE, "w") as f:
        f.write(header)
        for wr, n in mass_points:
            f.write(f"arguments = {wr} {n} {OUTDIR}\n")
            f.write(f"WR={wr}\nN={n}\nqueue\n\n")

    print(f"Written: {SUB_FILE}  ({len(mass_points)} jobs)")


def main():
    parser = argparse.ArgumentParser(description="Submit cutflow condor jobs for all signal mass points")
    parser.add_argument("--dry-run", action="store_true", help="Generate submit file but do not submit")
    args = parser.parse_args()

    mass_points = collect_mass_points()
    print(f"Found {len(mass_points)} mass points")

    write_submit_file(mass_points)

    if args.dry_run:
        print("Dry run — not submitting. Run without --dry-run to submit.")
        print(f"First 5 mass points: {mass_points[:5]}")
        return

    result = subprocess.run(["condor_submit", SUB_FILE], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
