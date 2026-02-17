#!/bin/zsh
set -euo pipefail

# 사용자 로그인 컨텍스트 강제:
# - HOME을 사용자 홈으로 고정
# - OPENAI_* 환경변수 충돌 제거

USER_HOME="${CODEX_USER_HOME:-${HOME}}"
PROJECT_DIR="${CODEX_PROJECT_DIR:-}"
MODEL="${CODEX_MODEL:-gpt-5.3-codex}"
FALLBACK_MODEL="${CODEX_FALLBACK_MODEL:-gpt-5}"
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  run_codex_user_context.sh [--model MODEL] [--project DIR] [--dry-run] "PROMPT"

Examples:
  run_codex_user_context.sh "Reply exactly: OK"
  run_codex_user_context.sh --model gpt-5 "코드 리뷰해줘"
  CODEX_FALLBACK_MODEL=gpt-5 run_codex_user_context.sh "test"
  CODEX_MODEL=gpt-5 run_codex_user_context.sh --dry-run "test"
EOF
}

PROMPT=""
FULL_AUTO=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      MODEL="$2"
      shift 2
      ;;
    --project)
      PROJECT_DIR="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --full-auto)
      FULL_AUTO=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      PROMPT="$1"
      shift
      ;;
  esac
done

if [[ -z "${PROMPT}" ]]; then
  echo "[ERROR] PROMPT가 필요합니다." >&2
  usage >&2
  exit 1
fi

# 프로젝트 경로 자동 탐지:
# 1) --project / CODEX_PROJECT_DIR
# 2) git root
# 3) 현재 디렉토리
if [[ -z "${PROJECT_DIR}" ]]; then
  if command -v git >/dev/null 2>&1; then
    GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
    if [[ -n "${GIT_ROOT}" ]]; then
      PROJECT_DIR="${GIT_ROOT}"
    fi
  fi
fi

if [[ -z "${PROJECT_DIR}" ]]; then
  PROJECT_DIR="$(pwd)"
fi

export HOME="${USER_HOME}"
unset OPENAI_API_KEY OPENAI_BASE_URL OPENAI_ORG_ID

if [[ "${FULL_AUTO}" -eq 1 ]]; then
  CMD=(codex exec --full-auto -m "${MODEL}" "${PROMPT}")
else
  CMD=(codex exec -m "${MODEL}" "${PROMPT}")
fi

if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "HOME=${HOME}"
  echo "PROJECT_DIR=${PROJECT_DIR}"
  echo "MODEL=${MODEL}"
  echo "FALLBACK_MODEL=${FALLBACK_MODEL}"
  printf 'CMD='
  printf '%q ' "${CMD[@]}"
  echo
  exit 0
fi

cd "${PROJECT_DIR}"

run_cmd() {
  local target_model="$1"
  local output
  set +e
  output="$(codex exec -m "${target_model}" "${PROMPT}" 2>&1)"
  local rc=$?
  set -e
  printf "%s\n" "${output}"
  return ${rc}
}

is_model_access_error() {
  local text="$1"
  [[ "${text}" == *"does not exist or you do not have access to it"* ]] || \
    [[ "${text}" == *"not supported when using Codex with a ChatGPT account"* ]]
}

set +e
FIRST_OUTPUT="$(run_cmd "${MODEL}")"
FIRST_RC=$?
set -e
printf "%s\n" "${FIRST_OUTPUT}"

if [[ "${MODEL}" == "gpt-5.3-codex" ]] && is_model_access_error "${FIRST_OUTPUT}"; then
  echo "[INFO] model fallback: ${MODEL} -> ${FALLBACK_MODEL}" >&2
  set +e
  SECOND_OUTPUT="$(run_cmd "${FALLBACK_MODEL}")"
  SECOND_RC=$?
  set -e
  printf "%s\n" "${SECOND_OUTPUT}"
  exit ${SECOND_RC}
fi

if [[ ${FIRST_RC} -eq 0 ]]; then
  exit 0
fi

exit ${FIRST_RC}
