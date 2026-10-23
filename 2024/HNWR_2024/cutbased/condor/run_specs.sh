#!/usr/bin/env bash
# condor job 본체 — 스펙 파일 하나를 처리한다.
#   run_specs.sh <job 이름> [run_specs.py 에 넘길 추가 인자...]
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JOB="${1:?usage: run_specs.sh <job name> [extra args...]}"
shift || true

# condor 가 preemption 으로 job 을 되돌린다 (실측: 시작 후 33~41분). job 하나는
# 23~25 분이라 아슬아슬하다 — 빠른 노드에 걸리면 살아남고, 느린 노드에 걸리면
# 33 분을 넘겨 evict 되고 재개가 없으면 처음부터 다시 그린다. 그러면 영원히
# 안 끝난다 (실측: 19 job / 39 실행 / 22 evict / 2 완주).
# --skip-existing 이 이미 그린 플롯을 건너뛰므로 재시작이 이어서 진행한다.
OPTS=(--skip-existing)

# 입력을 워커 로컬 디스크로 복사한다. 플롯 시간의 99% 가 TDirectoryFile::Get 인데
# (cProfile: 47.4 s 중 46.9 s), /gv0 의 cold read 는 35.6 ms 인 반면 로컬 사본은
# 3.6 ms 다 — 한 번도 안 읽은 히스토그램으로 실측한 10 배 차이다.
#   복사 없음: 34 플롯 x 47 s        = 26 분
#   복사 있음: 6.9 분 + 34 x 7.2 s   = 11 분
# 33 분 eviction 문턱 아래로 내려가는 게 핵심이다.
#
# 주의: 캐시된 히스토그램을 재면 1.9 ms 가 나온다. 그 숫자로 판단하면 안 된다.
#
# 컨테이너가 scratch 를 볼 수 있어야 하므로 bind 도 같이 넣는다.
if [ -n "${_CONDOR_SCRATCH_DIR:-}" ]; then
    export PLOT_EXTRA_BINDS="${_CONDOR_SCRATCH_DIR}:${_CONDOR_SCRATCH_DIR}"
    OPTS+=(--copy-local "${_CONDOR_SCRATCH_DIR}/inputs")
else
    echo "=== _CONDOR_SCRATCH_DIR 없음 — /gv0 에서 직접 읽는다 ==="
fi

echo "=== job ${JOB} ==="
echo "=== start $(date) ==="
"${HERE}/in_container.sh" python run_specs.py "${JOB}" "${OPTS[@]}" "$@"
EXIT=$?
echo "=== end $(date) ==="
echo "=== exit ${EXIT} ==="
exit ${EXIT}
