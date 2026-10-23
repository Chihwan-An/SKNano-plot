#!/usr/bin/env bash
# 모든 플롯 job 이 끝난 뒤 결과를 계층 구조로 옮긴다.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== organize / start $(date) ==="
"${HERE}/in_container.sh" python organize_files.py
EXIT=$?
echo "=== organize / end $(date) exit ${EXIT} ==="
exit ${EXIT}
