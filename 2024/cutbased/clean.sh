#!/usr/bin/env bash
# 결과물과 condor 로그를 지운다. 스펙/코드는 건드리지 않는다.
set -euo pipefail
BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
read -rp "out/ 와 condor/logs/ 를 지운다. 계속? [y/N] " ans
[ "${ans:-N}" = "y" ] || { echo "취소"; exit 0; }
rm -rf "${BASE}/out"/* "${BASE}/condor/logs"/*
rm -f "${BASE}/condor"/*.dag.* 
echo "완료"
