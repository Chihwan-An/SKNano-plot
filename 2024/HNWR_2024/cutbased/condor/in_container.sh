#!/usr/bin/env bash
# 컨테이너 + micromamba 안에서 명령을 실행한다.
#
#   in_container.sh python run_specs.py Resolve_sig_EE
#
# 이미지가 private-el9.sif 인 이유: Nano15.sif 는 얇은 이미지라 그 안에서
# ROOT 를 import 하면 죽는다 (2026-08-18 확인). micromamba 환경은 bind 로
# 들어오는 /data6 에서 가져오므로 이미지는 EL9 런타임만 제공하면 된다.
#
# /data9 bind 가 v13 대비 새로 필요하다 — 플로터 코드가 거기 있다.
#
# 아래 값들은 환경변수로 덮어쓸 수 있다.
set -uo pipefail

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${PLOT_SIF:-/data6/Users/achihwan/private-el9.sif}"
MAMBA_BIN="${PLOT_MAMBA_EXE:-/data6/Users/achihwan/.local/bin/micromamba}"
MAMBA_ROOT="${PLOT_MAMBA_ROOT:-/data6/Users/achihwan/micromamba}"
MAMBA_ENV="${PLOT_MAMBA_ENV:-Nano15}"
BINDS="${PLOT_BINDS:-/data6:/data6,/data9:/data9,/gv0:/gv0,/home/achihwan:/home/achihwan}"
# condor 의 scratch 디렉토리처럼 그때그때 달라지는 경로를 덧붙일 때 쓴다.
# 기본 BINDS 를 통째로 다시 적지 않아도 되도록 따로 뒀다.
BINDS="${BINDS}${PLOT_EXTRA_BINDS:+,${PLOT_EXTRA_BINDS}}"

if [ "$#" -eq 0 ]; then
    echo "usage: in_container.sh <command> [args...]" >&2
    exit 64
fi

CMD=""
for a in "$@"; do
    CMD+=" $(printf '%q' "$a")"
done

# 버퍼링을 끈다. 이게 없으면 파이썬 stdout 이 8KB 씩 모였다 나가서, condor 의
# .out 파일이 job 이 끝날 때까지 헤더(bash echo)만 있는 것처럼 보인다.
# 몇 시간짜리 job 의 진행 상황을 못 보게 되므로 켜 두지 않는다.
singularity exec --bind "${BINDS}" "${IMAGE}" bash -c "
    export PYTHONUNBUFFERED=1
    export MAMBA_EXE='${MAMBA_BIN}'
    export MAMBA_ROOT_PREFIX='${MAMBA_ROOT}'
    eval \"\$('${MAMBA_BIN}' shell hook -s bash)\"
    micromamba activate '${MAMBA_ENV}' || { echo 'micromamba activate ${MAMBA_ENV} 실패' >&2; exit 91; }
    cd '${BASE}' || exit 92
   ${CMD}
"
