#!/usr/bin/env python3
"""
파일 정리 스크립트: combine_era_2022_2023 폴더 내 파일을 계층 구조로 분류
hierarchy: boost/resolve → DY/FLV/SR → EE/MM/E_Mu/Mu_E → jet/lepton/dilepton/jet_lepton/pileup → OS/SS/Inclusive
"""

import os
import re
import shutil
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 플레이버 태그 → 폴더명 매핑
FLAVOR_MAP = {
    'EMJ': 'E_Mu',
    'MEJ': 'Mu_E',
    'MM':  'MM',
    'EE':  'EE',
    'EM':  'E_Mu',   # resolve FLV용
}

# 처리할 서브디렉토리 → 파일명 prefix 매핑
SUBDIRS = {
    'boost/DY':   'BoostDY',
    'boost/FLV':  'BoostFLV',
    'boost/sr':   'BoostSR',
    'resolve/DY': 'ResolveDY',
    'resolve/FLV':'ResolveFLV',
    'resolve/sr': 'ResolveSR',
}


def classify_variable(var: str) -> str:
    """변수명으로부터 오브젝트 타입 폴더 결정 (OS_/SS_ prefix 제거 후 판단)"""

    # OS_/SS_ prefix 제거 후 순수 변수명으로 분류
    pure = re.sub(r'^(OS_|SS_)', '', var)

    # pileup
    if pure == 'punum':
        return 'pileup'

    # lepton
    if re.match(r'(leading|subleading)_lep_', pure):
        return 'lepton'

    # jet
    if re.match(r'(leading|subleading)_(jet|fatjet)', pure):
        return 'jet'
    if re.match(r'fatjet_|leading_fatjet_|j1j2_|deltaR_|dphi_', pure):
        return 'jet'
    if pure == 'jetnum':
        return 'jet'

    # dilepton
    if re.match(r'dilepton_|ll_pt$|Dilepton_pt$', pure):
        return 'dilepton'
    if pure in ('mll', 'll_pt', 'Dilepton_pt', 'pt', 'eta', 'phi', 'mass'):
        return 'dilepton'

    # jet_lepton
    if re.match(r'WR_|mlljj|l1j1j2_|l2j1j2_', pure):
        return 'jet_lepton'
    if pure == 'WRMass':
        return 'jet_lepton'

    return 'other'


def parse_filename(fname: str, region_key: str):
    """
    파일명에서 플레이버 태그와 변수명 추출
    e.g. BoostDYEE_leading_lep_pt.tsv  →  flavor='EE', var='leading_lep_pt'
    """
    stem = os.path.splitext(fname)[0]          # 확장자 제거
    if not stem.startswith(region_key):
        return None, None
    rest = stem[len(region_key):]              # e.g. EE_leading_lep_pt

    # 긴 태그 먼저 체크 (EMJ, MEJ, MM, EE, EM 순)
    for flavor_tag in ('EMJ', 'MEJ', 'MM', 'EE', 'EM'):
        if rest.startswith(flavor_tag + '_'):
            var = rest[len(flavor_tag) + 1:]   # _ 이후
            # png 파일은 변수명 끝에 _plot 이 붙음 → 제거
            if var.endswith('_plot'):
                var = var[:-5]
            return flavor_tag, var

    return None, None


def organize(dry_run: bool = False):
    moved = 0
    skipped = 0
    unclassified = []

    for rel_dir, region_key in SUBDIRS.items():
        src_dir = os.path.join(BASE_DIR, rel_dir)
        if not os.path.isdir(src_dir):
            print(f"[WARNING] 존재하지 않는 디렉토리: {rel_dir}")
            continue

        for fname in sorted(os.listdir(src_dir)):
            if not (fname.endswith('.tsv') or fname.endswith('.png')):
                continue

            flavor_tag, var = parse_filename(fname, region_key)
            if flavor_tag is None:
                skipped += 1
                print(f"[SKIP] prefix 매칭 실패: {rel_dir}/{fname}")
                continue

            flavor_dir = FLAVOR_MAP.get(flavor_tag)
            if flavor_dir is None:
                skipped += 1
                print(f"[SKIP] 알 수 없는 플레이버: {rel_dir}/{fname}")
                continue

            obj_dir = classify_variable(var)
            if obj_dir == 'other':
                unclassified.append(f"{rel_dir}/{fname}  (var={var})")

            # --- OS / SS 폴더 추가 분류 ---
            if var.startswith('OS_'):
                sign_dir = 'OS'
            elif var.startswith('SS_'):
                sign_dir = 'SS'
            else:
                sign_dir = 'Inclusive' # OS/SS 명시가 없는 변수들

            # 최종 경로에 sign_dir (OS/SS/Inclusive) 추가
            dest_dir = os.path.join(src_dir, flavor_dir, obj_dir, sign_dir)
            src_path  = os.path.join(src_dir, fname)
            dest_path = os.path.join(dest_dir, fname)

            if dry_run:
                print(f"[DRY] {rel_dir}/{fname}  →  {flavor_dir}/{obj_dir}/{sign_dir}/")
            else:
                os.makedirs(dest_dir, exist_ok=True)
                shutil.move(src_path, dest_path)
                print(f"[MOVED] {rel_dir}/{fname}  →  {flavor_dir}/{obj_dir}/{sign_dir}/")
            moved += 1

    print(f"\n{'[DRY RUN] ' if dry_run else ''}완료: {moved}개 이동, {skipped}개 건너뜀")
    if unclassified:
        print(f"\n[주의] 분류 기준에 없는 변수 {len(unclassified)}개 (other 폴더로 이동):")
        for item in unclassified:
            print(f"  {item}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot 파일 정리 스크립트')
    parser.add_argument('--dry-run', action='store_true',
                        help='실제 이동 없이 결과만 출력')
    args = parser.parse_args()

    if args.dry_run:
        print("=== DRY RUN 모드 (파일 이동 없음) ===\n")
    organize(dry_run=args.dry_run)