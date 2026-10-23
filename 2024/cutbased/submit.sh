#!/usr/bin/env bash
# 입력 점검 -> DAG 생성 -> condor 제출.
#
#   ./submit.sh                 # 전부
#   ./submit.sh --stat-only     # syst 없이 빠르게
#   ./submit.sh --skip-check    # 점검 건너뛰기 (권장하지 않음)
#
# condor_submit_dag 가 있는 서브밋 노드에서 돌릴 것. ai-tamsa1 에는 없다.
set -uo pipefail
BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SKIP_CHECK=0
DAG_ARGS=()
for a in "$@"; do
    if [ "$a" = "--skip-check" ]; then SKIP_CHECK=1; else DAG_ARGS+=("$a"); fi
done

if [ "${SKIP_CHECK}" -eq 0 ]; then
    echo "### 1/3  입력 점검"
    if ! "${BASE}/condor/in_container.sh" python check_inputs.py --quiet-hists; then
        echo
        echo "점검에서 문제가 나왔다. 그대로 제출하려면 --skip-check 를 붙일 것." >&2
        exit 1
    fi
else
    echo "### 1/3  입력 점검 건너뜀"
fi

# job 은 --skip-existing 으로 돈다 (eviction 이 진행을 날리지 않게). 그래서
# out/ 에 남아 있는 플롯은 다시 안 그려진다. 이어서 돌리는 거면 그게 맞지만,
# 코드나 설정을 바꾼 뒤라면 낡은 플롯이 조용히 살아남는다.
EXISTING=$(find "${BASE}/out" -name '*_plot.png' 2>/dev/null | wc -l)
if [ "${EXISTING}" -gt 0 ]; then
    echo
    echo "out/ 에 png 가 이미 ${EXISTING}개 있다. job 은 이걸 다시 안 그린다."
    echo "  - evict 된 DAG 를 이어서 돌리는 중이면 -> 그대로 진행"
    echo "  - 코드/설정을 바꿔 전부 다시 그려야 하면 -> 취소하고 ./clean.sh"
    if [ -t 0 ]; then
        read -rp "이어서 진행? [y/N] " ans
        [ "${ans:-N}" = "y" ] || { echo "취소"; exit 0; }
    else
        echo "(비대화형 — 이어서 진행한다)"
    fi
fi

echo
echo "### 2/3  DAG 생성"
"${BASE}/condor/in_container.sh" python make_dag.py "${DAG_ARGS[@]+"${DAG_ARGS[@]}"}" || exit 1

echo
echo "### 3/3  제출"
if ! command -v condor_submit_dag >/dev/null 2>&1; then
    echo "condor_submit_dag 가 PATH 에 없다 ($(hostname))." >&2
    echo "서브밋 노드에서 아래를 실행할 것:" >&2
    echo "  condor_submit_dag -f ${BASE}/condor/plotter.dag" >&2
    exit 2
fi
condor_submit_dag -f "${BASE}/condor/plotter.dag"
