#!/bin/zsh
set -euo pipefail

# 사용자 로그인 컨텍스트 강제:
# - HOME을 사용자 홈으로 고정
# - OPENAI_* 환경변수 충돌 제거
# - 계정 로그인 기반 (API 키 불필요)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMMUNICATOR_ROOT="$(cd "${SKILL_ROOT}/../.." && pwd)"

USER_HOME="${CODEX_USER_HOME:-${HOME}}"
PROJECT_DIR="${CODEX_PROJECT_DIR:-}"
MODEL="${CODEX_MODEL:-gpt-5.3-codex}"
FALLBACK_MODEL="${CODEX_FALLBACK_MODEL:-gpt-5}"
SANDBOX="${CODEX_SANDBOX:-}"
FEEDBACK_DIR="${CODEX_FEEDBACK_DIR:-$(pwd)/plans/codex}"
DRY_RUN=0
FULL_AUTO=0
SAVE_FEEDBACK=0
FILE_PATH=""
PROMPT=""

usage() {
  cat <<'EOF'
Usage:
  run_codex_user_context.sh [OPTIONS] "PROMPT"

Options:
  --model MODEL       사용할 모델 (기본: gpt-5.3-codex)
  --project DIR       작업 디렉토리 (기본: git root → cwd)
  --file PATH         리뷰할 파일 경로 (내용을 프롬프트에 첨부)
  --sandbox MODE      샌드박스 모드: read-only | workspace-write | danger-full-access
  --full-auto         자동 실행 모드
  --save              결과를 codex_feedback.md에 기록
  --dry-run           실행하지 않고 명령만 출력
  -h, --help          도움말

Examples:
  run_codex_user_context.sh "Reply exactly: OK"
  run_codex_user_context.sh --model gpt-5 "코드 리뷰해줘"
  run_codex_user_context.sh --file src/app.py "이 코드를 리뷰해줘"
  run_codex_user_context.sh --sandbox danger-full-access "외부 API 호출 필요한 작업"
  run_codex_user_context.sh --full-auto --save "설계안 작성해줘"
  CODEX_FALLBACK_MODEL=gpt-5 run_codex_user_context.sh "test"
EOF
}

# 인자 파싱
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
    --file)
      FILE_PATH="$2"
      shift 2
      ;;
    --sandbox)
      SANDBOX="$2"
      shift 2
      ;;
    --full-auto)
      FULL_AUTO=1
      shift
      ;;
    --save)
      SAVE_FEEDBACK=1
      shift
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

# Codex CLI 존재 확인
if ! command -v codex >/dev/null 2>&1; then
  echo "[ERROR] Codex CLI를 찾을 수 없습니다." >&2
  echo "설치: npm install -g @openai/codex 또는 https://github.com/openai/codex" >&2
  exit 1
fi

# 파일 내용 첨부
FULL_PROMPT="${PROMPT}"
if [[ -n "${FILE_PATH}" ]]; then
  if [[ ! -f "${FILE_PATH}" ]]; then
    echo "[ERROR] 파일을 찾을 수 없습니다: ${FILE_PATH}" >&2
    exit 1
  fi
  FILE_CONTENT="$(cat "${FILE_PATH}")"
  FULL_PROMPT="${PROMPT}

--- 파일: ${FILE_PATH} ---
${FILE_CONTENT}"
elif [[ ! -t 0 ]]; then
  # stdin 파이프 입력
  STDIN_CONTENT="$(cat)"
  if [[ -n "${STDIN_CONTENT}" ]]; then
    FULL_PROMPT="${PROMPT}

--- stdin ---
${STDIN_CONTENT}"
  fi
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

# dry-run
if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "HOME=${HOME}"
  echo "PROJECT_DIR=${PROJECT_DIR}"
  echo "MODEL=${MODEL}"
  echo "FALLBACK_MODEL=${FALLBACK_MODEL}"
  echo "SANDBOX=${SANDBOX:-default}"
  echo "FULL_AUTO=${FULL_AUTO}"
  echo "FILE_PATH=${FILE_PATH}"
  echo "SAVE_FEEDBACK=${SAVE_FEEDBACK}"
  echo "FEEDBACK_DIR=${FEEDBACK_DIR}"
  exit 0
fi

cd "${PROJECT_DIR}"

run_cmd() {
  local target_model="$1"
  local cmd_args=(codex exec -m "${target_model}")

  if [[ "${FULL_AUTO}" -eq 1 ]]; then
    cmd_args+=(--full-auto)
  fi

  if [[ -n "${SANDBOX}" ]]; then
    cmd_args+=(--sandbox "${SANDBOX}")
  fi

  cmd_args+=("${FULL_PROMPT}")

  local output
  set +e
  output="$("${cmd_args[@]}" 2>&1)"
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

# 피드백 기록
save_to_feedback() {
  local output="$1"
  local used_model="$2"
  local rc="$3"

  if [[ "${SAVE_FEEDBACK}" -ne 1 ]]; then
    return
  fi

  local feedback_file="${FEEDBACK_DIR}/codex_feedback.md"
  mkdir -p "${FEEDBACK_DIR}"

  # 헤더가 없으면 생성
  if [[ ! -f "${feedback_file}" ]]; then
    cat > "${feedback_file}" <<'HEADER'
# Codex Feedback Log

이 파일은 Codex CLI 실행 결과가 자동으로 추가됩니다.
`tail -f codex_feedback.md`로 실시간 모니터링 가능합니다.
HEADER
  fi

  local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
  local file_info=""
  if [[ -n "${FILE_PATH}" ]]; then
    file_info=" | 대상: \`${FILE_PATH}\`"
  fi
  local status="성공"
  if [[ "${rc}" -ne 0 ]]; then
    status="실패 (exit ${rc})"
  fi

  cat >> "${feedback_file}" <<ENTRY

---

## [${timestamp}] Codex CLI | 모델: ${used_model} | ${status}${file_info}

${output}
ENTRY

  echo "[INFO] 피드백 기록: ${feedback_file}" >&2
}

# 실행 + fallback
set +e
FIRST_OUTPUT="$(run_cmd "${MODEL}")"
FIRST_RC=$?
set -e

if [[ "${MODEL}" == "gpt-5.3-codex" ]] && is_model_access_error "${FIRST_OUTPUT}"; then
  echo "[INFO] model fallback: ${MODEL} -> ${FALLBACK_MODEL}" >&2
  set +e
  SECOND_OUTPUT="$(run_cmd "${FALLBACK_MODEL}")"
  SECOND_RC=$?
  set -e
  printf "%s\n" "${SECOND_OUTPUT}"
  save_to_feedback "${SECOND_OUTPUT}" "${FALLBACK_MODEL}" "${SECOND_RC}"
  exit ${SECOND_RC}
fi

printf "%s\n" "${FIRST_OUTPUT}"
save_to_feedback "${FIRST_OUTPUT}" "${MODEL}" "${FIRST_RC}"
exit ${FIRST_RC}
