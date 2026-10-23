#!/usr/bin/env python3
"""v13 plotter.sh -> specs/*.txt 1회성 변환기.

546 줄을 손으로 옮기면 반드시 오타가 난다. v13 트리에서 기계적으로 뽑아
specs/ 에 넣고, 그 뒤로는 specs/ 가 원본이 된다.

변환 규칙
  * `python "$DIR/EE.py" ...` 줄에서 스크립트 뒤 인자만 남긴다.
  * --signal-scale / --year 는 버린다 (배경 전용, 2024 고정).
  * --label1 / --label2 / --channel / --outdir 은 넣지 않는다.
    run_specs.py 가 config.REGIONS 에서 채워 넣는다.
  * `charge_split ...` (v13 기본 비활성) 줄은 specs/chargesplit/ 로 따로 뺀다.
  * 주석 처리된 줄은 버린다.
"""

import os
import re
import shlex
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402

V13_ROOT = ("/data6/Users/achihwan/SKNanoAnalyzer-v13/plots/HNWR/reproduce/"
            "syst_plotter/integrated/charge_inclusive_year_sep/2024")

DROP_WITH_VALUE = {"--signal-scale", "--year"}
DROP_FLAGS = {"--show-sb"}

LINE_RE = re.compile(r'^(charge_split\s+)?python\s+"\$DIR/(EE|MM)\.py"\s*(.*)$')


def clean_tokens(tokens):
    out = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in DROP_WITH_VALUE:
            i += 2
            continue
        if t in DROP_FLAGS:
            i += 1
            continue
        out.append(t)
        i += 1
    return out


def convert():
    os.makedirs(config.SPEC_DIR, exist_ok=True)
    cs_dir = os.path.join(config.SPEC_DIR, "chargesplit")
    os.makedirs(cs_dir, exist_ok=True)

    total, total_cs = 0, 0
    for region in config.REGIONS:
        src = os.path.join(V13_ROOT, region["dir"], "plotter.sh")
        if not os.path.isfile(src):
            print(f"!! v13 원본 없음: {src}")
            continue

        # 이 리전에서 스크립트 채널 -> flavour 태그
        ch_to_flavour = {ch: fl for ch, fl in region["channels"]}
        buckets = {fl: [] for fl in ch_to_flavour.values()}
        cs_buckets = {fl: [] for fl in ch_to_flavour.values()}

        for raw in open(src):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m = LINE_RE.match(line)
            if not m:
                continue
            is_cs, script_ch, rest = bool(m.group(1)), m.group(2), m.group(3)
            flavour = ch_to_flavour.get(script_ch)
            if flavour is None:
                print(f"!! {region['dir']}: {script_ch}.py 줄이 있는데 "
                      f"config 의 channels 에는 없다 — 건너뜀")
                continue
            tokens = clean_tokens(shlex.split(rest))
            (cs_buckets if is_cs else buckets)[flavour].append(" ".join(shlex.quote(t) for t in tokens))

        for flavour, lines in buckets.items():
            name = f"{region['key']}_{flavour}.txt"
            path = os.path.join(config.SPEC_DIR, name)
            lines, dropped = dedupe_by_output(lines)
            write_spec(path, region, flavour, lines)
            total += len(lines)
            note = f"  (중복 --output {len(dropped)}개 제거: {', '.join(dropped)})" if dropped else ""
            print(f"  {name:<28} {len(lines):>3} plots{note}")
        for flavour, lines in cs_buckets.items():
            if not lines:
                continue
            name = f"{region['key']}_{flavour}.txt"
            write_spec(os.path.join(cs_dir, name), region, flavour, lines)
            total_cs += len(lines)

    print(f"\n총 {total} plots -> specs/")
    print(f"총 {total_cs} plots -> specs/chargesplit/  (OS/SS 분리, DAG 에는 안 들어감)")


def dedupe_by_output(lines):
    """--output 이 같은 줄이 여러 개면 마지막 것만 남긴다.

    v13 은 같은 플롯을 ratio 범위만 바꿔 두 번 그렸고, 뒤에 그린 것이 앞의
    파일을 덮어썼다. 결과물은 어차피 마지막 것이므로 앞의 것을 미리 버려
    같은 그림을 두 번 그리는 시간을 없앤다.
    """
    seen_last = {}
    for idx, line in enumerate(lines):
        toks = shlex.split(line)
        out = toks[toks.index("--output") + 1] if "--output" in toks else f"__{idx}"
        seen_last[out] = idx
    keep = set(seen_last.values())
    dropped = sorted(o for o, i in seen_last.items() if sum(1 for l in lines
                     if f"--output {o} " in l + " " or l.endswith(f"--output {o}")) > 1)
    return [l for i, l in enumerate(lines) if i in keep], dropped


def write_spec(path, region, flavour, lines):
    with open(path, "w") as fh:
        fh.write(f"# {region['key']} / {flavour}  ({region['dir']})\n")
        fh.write(f"# label1={config.FLAVOUR_LABELS[flavour]}  label2={region['label2']}\n")
        fh.write("# 한 줄이 플롯 하나. --channel/--outdir/--label1/--label2 는 "
                 "run_specs.py 가 config 에서 채운다.\n")
        for line in lines:
            fh.write(line + "\n")


if __name__ == "__main__":
    convert()
