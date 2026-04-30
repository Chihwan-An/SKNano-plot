#!/usr/bin/env python3
"""
파일 정리 스크립트: ht_binned_both_tight_charge 폴더 내 파일을 계층 구조로 분류
hierarchy: boost/resolve → DY/FLV/SR → EE/MM/E_Mu/Mu_E → jet/lepton/dilepton/jet_lepton/pileup → <tight_tag>

Tight tags by channel:
  MM (DY/SR)    : OS_tight / OS_not_tight / SS_tight / SS_not_tight
  EE (DY)       : OS_2e_tight / OS_1e_tight / OS_0e_tight / SS_2e_tight / SS_1e_tight / SS_0e_tight
  EMJ (FLV, OS) : OS_M_tight_E_tight / OS_M_tight_E_not_tight / OS_M_not_tight_E_tight / OS_M_not_tight_E_not_tight
  EMJ (FLV, SS) : SS_tight
  MEJ (FLV)     : OS/SS × M_tight_E_tight / M_tight_E_not_tight / M_not_tight_E_tight / M_not_tight_E_not_tight
  EM  (FLV resolve): OS_tight / OS_not_tight / SS_tight / SS_not_tight
"""

import os
import re
import shutil
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FLAVOR_MAP = {
    'EMJ':  'E_Mu',
    'MEJ':  'Mu_E',
    'MMv2': 'MM',
    'MM':   'MM',
    'EE':   'EE',
    'EM':   'E_Mu',
}

SUBDIRS = {
    'boost/DY':   'BoostDY',
    'boost/FLV':  'BoostFLV',
    'boost/sr':   'BoostSR',
    'resolve/DY': 'ResolveDY',
    'resolve/FLV':'ResolveFLV',
    'resolve/sr': 'ResolveSR',
}

# Order matters: longer/more-specific tags first to avoid partial matches
SIGN_TC_TAGS = (
    # EMJ/MEJ 4-combo: both M and E tight status
    'OS_M_tight_E_tight',
    'OS_M_tight_E_not_tight',
    'OS_M_not_tight_E_tight',
    'OS_M_not_tight_E_not_tight',
    'SS_M_tight_E_tight',
    'SS_M_tight_E_not_tight',
    'SS_M_not_tight_E_tight',
    'SS_M_not_tight_E_not_tight',
    # EE electron tight count
    'OS_2e_tight',
    'OS_1e_tight',
    'OS_0e_tight',
    'SS_2e_tight',
    'SS_1e_tight',
    'SS_0e_tight',
    # MM/EM muon tight (also EMJ SS_tight falls here)
    'OS_not_tight',
    'SS_not_tight',
    'OS_tight',
    'SS_tight',
)


def classify_variable(var: str) -> str:
    if var in ('punum', 'pv', 'pvgood'):
        return 'pileup'
    if re.match(r'(leading|subleading)_lep_', var):
        return 'lepton'
    if var in ('LeadingLepPt', 'SubLeadingLepPt', 'leadlep_lsf'):
        return 'lepton'
    if re.match(r'(leading|subleading)_(jet|fatjet)', var):
        return 'jet'
    if re.match(r'fatjet_|deltaR_|dphi_', var):
        return 'jet'
    if var == 'jetnum':
        return 'jet'
    if re.match(r'dilepton_|ll_pt$|Dilepton_pt$', var):
        return 'dilepton'
    if var in ('mll', 'll_pt', 'Dilepton_pt', 'pt', 'eta', 'phi', 'mass',
               'dilepton_pt', 'dilepton_eta', 'dilepton_phi', 'dilepton_mass'):
        return 'dilepton'
    if re.match(r'WR_|mlljj|l1j1j2_|l2j1j2_|j1j2_', var):
        return 'jet_lepton'
    if var in ('WRMass', 'WR_pt', 'WR_eta', 'WR_phi'):
        return 'jet_lepton'
    return 'other'


def parse_filename(fname: str, region_key: str):
    """
    파일명에서 플레이버 태그, tight_tag, 변수명 추출
    e.g. BoostDYMM_OS_tight_mlljj.tsv              → ('MM', 'OS_tight', 'mlljj')
         BoostDYEE_OS_2e_tight_dilepton_pt.png     → ('EE', 'OS_2e_tight', 'dilepton_pt')
         BoostFLVEMJ_OS_M_tight_E_tight_mlljj.tsv → ('EMJ', 'OS_M_tight_E_tight', 'mlljj')
         BoostFLVMEJ_SS_M_not_tight_E_tight_mll.tsv → ('MEJ', 'SS_M_not_tight_E_tight', 'mll')
         ResolveFLVEM_OS_tight_dilepton_pt.png     → ('EM', 'OS_tight', 'dilepton_pt')
    """
    stem = os.path.splitext(fname)[0]
    if stem.endswith('_plot'):
        stem = stem[:-5]

    if not stem.startswith(region_key):
        return None, None, None
    rest = stem[len(region_key):]  # e.g. MM_OS_tight_mlljj

    for flavor_tag in ('EMJ', 'MEJ', 'MMv2', 'MM', 'EE', 'EM'):
        if rest.startswith(flavor_tag + '_'):
            rest2 = rest[len(flavor_tag) + 1:]  # e.g. OS_tight_mlljj
            for tag in SIGN_TC_TAGS:
                if rest2.startswith(tag + '_'):
                    var = rest2[len(tag) + 1:]
                    return flavor_tag, tag, var
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

            flavor_tag, tight_tag, var = parse_filename(fname, region_key)
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

            # 최종 경로: flavor_dir / obj_dir / tight_tag
            dest_dir = os.path.join(src_dir, flavor_dir, obj_dir, tight_tag)
            src_path  = os.path.join(src_dir, fname)
            dest_path = os.path.join(dest_dir, fname)

            if dry_run:
                print(f"[DRY] {rel_dir}/{fname}  →  {flavor_dir}/{obj_dir}/{tight_tag}/")
            else:
                os.makedirs(dest_dir, exist_ok=True)
                shutil.move(src_path, dest_path)
                print(f"[MOVED] {rel_dir}/{fname}  →  {flavor_dir}/{obj_dir}/{tight_tag}/")
            moved += 1

    print(f"\n{'[DRY RUN] ' if dry_run else ''}완료: {moved}개 이동, {skipped}개 건너뜀")
    if unclassified:
        print(f"\n[주의] 분류 기준에 없는 변수 {len(unclassified)}개 (other 폴더로 이동):")
        for item in unclassified:
            print(f"  {item}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot 파일 정리 스크립트 (both tight charge 버전)')
    parser.add_argument('--dry-run', action='store_true',
                        help='실제 이동 없이 결과만 출력')
    args = parser.parse_args()

    if args.dry_run:
        print("=== DRY RUN 모드 (파일 이동 없음) ===\n")
    organize(dry_run=args.dry_run)
