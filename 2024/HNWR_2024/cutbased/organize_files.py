#!/usr/bin/env python3
"""리전 폴더에 평평하게 남아 있는 플롯을 계층 구조로 옮긴다.

  out/<Boost|Resolve>/<리전>/  ->  .../<flavour>/<오브젝트>/<OS|SS|Inclusive>/

plotter 는 이제 처음부터 최종 위치에 쓴다 (layout.py). 이 스크립트는 그 전에
만들어진 산출물을 뒤늦게 정리할 때만 쓰면 된다. 폴더를 정하는 규칙은
layout.py 한 곳에만 있으므로 둘이 어긋날 일은 없다.
"""

import argparse
import os
import shutil

import config
import layout


def organize(dry_run=False, out_root=None):
    out_root = out_root or config.OUT_DIR
    moved = skipped = 0
    unclassified = []

    for region in config.REGIONS:
        src_dir = os.path.join(out_root, region["dir"])
        if not os.path.isdir(src_dir):
            print(f"[WARN] 없는 디렉토리: {region['dir']}")
            continue

        for fname in sorted(os.listdir(src_dir)):
            if not (fname.endswith(".tsv") or fname.endswith(".png")):
                continue
            sub = layout.subdir(fname, region["prefix"])
            if sub is None:
                skipped += 1
                print(f"[SKIP] 이름 해석 실패: {region['dir']}/{fname}")
                continue
            if os.path.basename(os.path.dirname(sub)) == "other":
                unclassified.append(f"{region['dir']}/{fname}")

            dest_dir = os.path.join(src_dir, sub)
            if dry_run:
                print(f"[DRY] {region['dir']}/{fname}  ->  {sub}/")
            else:
                os.makedirs(dest_dir, exist_ok=True)
                shutil.move(os.path.join(src_dir, fname),
                            os.path.join(dest_dir, fname))
            moved += 1

    print(f"\n{'[DRY RUN] ' if dry_run else ''}완료: {moved}개 이동, {skipped}개 건너뜀")
    if unclassified:
        print(f"\n[주의] 분류 기준에 없어 other/ 로 간 파일 {len(unclassified)}개:")
        for item in unclassified:
            print(f"  {item}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="플롯 결과 정리")
    ap.add_argument("--dry-run", action="store_true", help="이동 없이 결과만 출력")
    ap.add_argument("--out", default=None, help="결과 루트 (기본: out/)")
    args = ap.parse_args()
    raise SystemExit(organize(dry_run=args.dry_run, out_root=args.out))
