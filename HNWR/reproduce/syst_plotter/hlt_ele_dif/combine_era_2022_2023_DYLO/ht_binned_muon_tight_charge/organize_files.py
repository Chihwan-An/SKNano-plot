#!/usr/bin/env python3
"""
파일 정리 스크립트: ht_binned_tight_charge 폴더 내 파일을 계층 구조로 분류
hierarchy: boost/resolve → DY/FLV/SR → EE/MM/E_Mu/Mu_E → jet/lepton/dilepton/jet_lepton/pileup → OS_tight/OS_not_tight/SS_tight/SS_not_tight
"""

import os
import re
import shutil
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 플레이버 태그 → 폴더명 매핑
FLAVOR_MAP = {
    'EMJ':  'E_Mu',
    'MEJ':  'Mu_E',
    'MMv2': 'MM',
    'MM':   'MM',
    'EE':   'EE',
    'EM':   'E_Mu',
}

# 처리할 서브디렉토리 → 파일명 region prefix 매핑
SUBDIRS = {
    'boost/DY':   'BoostDY',
    'boost/FLV':  'BoostFLV',
    'boost/sr':   'BoostSR',
    'resolve/DY': 'ResolveDY',
    'resolve/FLV':'ResolveFLV',
    'resolve/sr': 'ResolveSR',
}

SIGN_TC_TAGS = ('OS_tight', 'OS_not_tight', 'SS_tight', 'SS_not_tight')


def classify_variable(var: str) -> str:
    """변수명으로부터 오브젝트 타입 폴더 결정"""

    # pileup
    if var in ('punum', 'pv'):
        return 'pileup'

    # lepton
    if re.match(r'(leading|subleading)_lep_', var):
        return 'lepton'
    if var in ('LeadingLepPt', 'SubLeadingLepPt', 'leadlep_lsf'):
        return 'lepton'

    # jet
    if re.match(r'(leading|subleading)_(jet|fatjet)', var):
        return 'jet'
    if re.match(r'fatjet_|deltaR_|dphi_', var):
        return 'jet'
    if var == 'jetnum':
        return 'jet'

    # dilepton
    if re.match(r'dilepton_|ll_pt$|Dilepton_pt$', var):
        return 'dilepton'
    if var in ('mll', 'll_pt', 'Dilepton_pt', 'pt', 'eta', 'phi', 'mass'):
        return 'dilepton'

    # jet_lepton
    if re.match(r'WR_|mlljj|l1j1j2_|l2j1j2_', var):
        return 'jet_lepton'
    if var == 'WRMass':
        return 'jet_lepton'

    return 'other'


def parse_filename(fname: str, region_key: str):
    """
    파일명에서 플레이버 태그, sign_tc, 변수명 추출
    e.g. BoostDYMM_OS_tight_dilepton_eta.tsv  →  ('MM', 'OS_tight', 'dilepton_eta')
         BoostFLVEMJ_SS_not_tight_fatjet_pt.png → ('EMJ', 'SS_not_tight', 'fatjet_pt')
         ResolveSRMMv2_SS_tight_mlljj.tsv      → ('MMv2', 'SS_tight', 'mlljj')
    """
    stem = os.path.splitext(fname)[0]
    # png 파일은 변수명 끝에 _plot 이 붙음 → 제거
    if stem.endswith('_plot'):
        stem = stem[:-5]

    if not stem.startswith(region_key):
        return None, None, None
    rest = stem[len(region_key):]  # e.g. MM_OS_tight_dilepton_eta

    for flavor_tag in ('EMJ', 'MEJ', 'MMv2', 'MM', 'EE', 'EM'):
        if rest.startswith(flavor_tag + '_'):
            rest2 = rest[len(flavor_tag) + 1:]  # e.g. OS_tight_dilepton_eta
            for sign_tc in SIGN_TC_TAGS:
                if rest2.startswith(sign_tc + '_'):
                    var = rest2[len(sign_tc) + 1:]
                    return flavor_tag, sign_tc, var
            return None, None, None

    return None, None, None


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

            flavor_tag, sign_tc, var = parse_filename(fname, region_key)
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

            # 최종 경로: flavor_dir / obj_dir / sign_tc
            dest_dir = os.path.join(src_dir, flavor_dir, obj_dir, sign_tc)
            src_path  = os.path.join(src_dir, fname)
            dest_path = os.path.join(dest_dir, fname)

            if dry_run:
                print(f"[DRY] {rel_dir}/{fname}  →  {flavor_dir}/{obj_dir}/{sign_tc}/")
            else:
                os.makedirs(dest_dir, exist_ok=True)
                shutil.move(src_path, dest_path)
                print(f"[MOVED] {rel_dir}/{fname}  →  {flavor_dir}/{obj_dir}/{sign_tc}/")
            moved += 1

    print(f"\n{'[DRY RUN] ' if dry_run else ''}완료: {moved}개 이동, {skipped}개 건너뜀")
    if unclassified:
        print(f"\n[주의] 분류 기준에 없는 변수 {len(unclassified)}개 (other 폴더로 이동):")
        for item in unclassified:
            print(f"  {item}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot 파일 정리 스크립트 (tight charge 버전)')
    parser.add_argument('--dry-run', action='store_true',
                        help='실제 이동 없이 결과만 출력')
    args = parser.parse_args()

    if args.dry_run:
        print("=== DRY RUN 모드 (파일 이동 없음) ===\n")
    organize(dry_run=args.dry_run)
