#!/bin/zsh
set -euo pipefail

# 사용자 로그인 컨텍스트 강제:
# - HOME을 사용자 홈으로 고정
# - OPENAI_* 환경변수 충돌 제거

USER_HOME="${CODEX_USER_HOME:-${HOME}}"
PROJECT_DIR="${CODEX_PROJECT_DIR:-}"
MODEL="${CODEX_MODEL:-gpt-5.3-codex}"
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  run_codex_user_context.sh [--model MODEL] [--project DIR] [--dry-run] "PROMPT"

Examples:
  run_codex_user_context.sh "Reply exactly: OK"
  run_codex_user_context.sh --model gpt-5 "코드 리뷰해줘"
  CODEX_MODEL=gpt-5 run_codex_user_context.sh --dry-run "test"
EOF
}

PROMPT=""
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

CMD=(codex exec -m "${MODEL}" "${PROMPT}")

if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "HOME=${HOME}"
  echo "PROJECT_DIR=${PROJECT_DIR}"
  echo "MODEL=${MODEL}"
  printf 'CMD='
  printf '%q ' "${CMD[@]}"
  echo
  exit 0
fi

cd "${PROJECT_DIR}"
exec "${CMD[@]}"
