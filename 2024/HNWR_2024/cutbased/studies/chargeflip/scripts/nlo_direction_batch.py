"""Bounded NLO check, four independent analyzer processes, restartable."""
import concurrent.futures
import json
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parents[1]
OUT = BASE/'data/nlo_direction_v1'
MASS = ('10to50','50to120','120to200','200to400','400to800','800to1500',
        '1500to2500','2500to4000','4000to6000','6000toInf')


def run(item):
    sample, cap = item
    meta = OUT/(sample+'.json')
    if meta.exists():
        print('CACHED', sample, flush=True)
        return
    cmd = ['bash', str(BASE/'scripts/run_nlo_direction.sh'), '--sample', sample,
           '--max-events', str(cap), '--out-dir', str(OUT)]
    print('START', sample, cap, flush=True)
    with (OUT/(sample+'.log')).open('w') as log:
        result = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'{sample} failed: see {OUT/(sample+".log")}')
    print('DONE', sample, json.loads(meta.read_text())['selected_rows'], flush=True)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    tasks = [('DYto2'+flav+'_MLL'+m, 2000000 if m=='50to120' else 200000)
             for m in MASS for flav in ('E','Mu')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(run, tasks))
