#!/bin/zsh
set -euo pipefail

# Gemini CLI 비대화형 호출 스크립트.
# API 키 불필요 — Google OAuth(gemini CLI 로그인)만 있으면 동작.
#
# Usage:
#   run_gemini_cli.sh [OPTIONS] "PROMPT"
#   cat file.py | run_gemini_cli.sh "리뷰해줘"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMMUNICATOR_ROOT="$(cd "${SKILL_ROOT}/../.." && pwd)"

GEMINI_CMD="${GEMINI_CLI_PATH:-gemini}"
MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"
FALLBACK_MODEL="${GEMINI_FALLBACK_MODEL:-gemini-2.0-flash}"
TIMEOUT="${GEMINI_TIMEOUT:-120}"
FEEDBACK_DIR="${GEMINI_FEEDBACK_DIR:-${COMMUNICATOR_ROOT}/plans/gemini}"
DRY_RUN=0
YOLO=0
SAVE_FEEDBACK=0
FILE_PATH=""
PROMPT=""

usage() {
  cat <<'EOF'
Usage:
  run_gemini_cli.sh [--model MODEL] [--file PATH] [--yolo] [--dry-run] "PROMPT"

Options:
  --model MODEL    사용할 모델 (기본: gemini-2.5-flash)
  --file PATH      리뷰할 파일 경로 (내용을 프롬프트에 첨부)
  --yolo           도구 사용 자동 승인
  --dry-run        실행하지 않고 명령만 출력
  --timeout SEC    타임아웃 초 (기본: 120)
  --save           결과를 gemini_feedback.md에 기록
  -h, --help       도움말

Examples:
  run_gemini_cli.sh "Python best practices?"
  run_gemini_cli.sh --file src/app.py "이 코드를 리뷰해줘"
  cat file.py | run_gemini_cli.sh "리뷰해줘"
  GEMINI_MODEL=gemini-2.5-pro run_gemini_cli.sh "심층 분석"
EOF
}

# 인자 파싱
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      MODEL="$2"
      shift 2
      ;;
    --file)
      FILE_PATH="$2"
      shift 2
      ;;
    --yolo)
      YOLO=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --timeout)
      TIMEOUT="$2"
      shift 2
      ;;
    --save)
      SAVE_FEEDBACK=1
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

# Gemini CLI 존재 확인
if ! command -v "${GEMINI_CMD}" >/dev/null 2>&1; then
  echo "[ERROR] Gemini CLI를 찾을 수 없습니다: ${GEMINI_CMD}" >&2
  echo "설치: npm install -g @anthropic-ai/gemini-cli 또는 https://github.com/anthropic-ai/gemini-cli" >&2
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

# 명령 구성
CMD=("${GEMINI_CMD}" -m "${MODEL}" -p "${FULL_PROMPT}")
if [[ "${YOLO}" -eq 1 ]]; then
  CMD+=(-y)
fi

# dry-run
if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "GEMINI_CMD=${GEMINI_CMD}"
  echo "MODEL=${MODEL}"
  echo "FALLBACK_MODEL=${FALLBACK_MODEL}"
  echo "TIMEOUT=${TIMEOUT}"
  echo "FILE_PATH=${FILE_PATH}"
  echo "YOLO=${YOLO}"
  echo "SAVE_FEEDBACK=${SAVE_FEEDBACK}"
  echo "FEEDBACK_DIR=${FEEDBACK_DIR}"
  printf 'CMD='
  printf '%q ' "${CMD[@]}"
  echo
  exit 0
fi

# 피드백 기록
save_to_feedback() {
  local output="$1"
  local used_model="$2"
  local rc="$3"

  if [[ "${SAVE_FEEDBACK}" -ne 1 ]]; then
    return
  fi

  local feedback_file="${FEEDBACK_DIR}/gemini_feedback.md"
  mkdir -p "${FEEDBACK_DIR}"

  # 헤더가 없으면 생성
  if [[ ! -f "${feedback_file}" ]]; then
    cat > "${feedback_file}" <<'HEADER'
# Gemini Feedback Log

이 파일은 Gemini CLI 평가 결과가 자동으로 추가됩니다.
`tail -f gemini_feedback.md`로 실시간 모니터링 가능합니다.
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

## [${timestamp}] Gemini CLI Skill | 모델: ${used_model} | ${status}${file_info}

${output}
ENTRY

  echo "[INFO] 피드백 기록: ${feedback_file}" >&2
}

# 타임아웃 유틸리티 (macOS 호환 — timeout/gtimeout 없이 동작)
_run_with_timeout() {
  local secs="$1"
  shift
  "$@" &
  local pid=$!
  (sleep "${secs}" && kill "${pid}" 2>/dev/null) &
  local watchdog=$!
  wait "${pid}" 2>/dev/null
  local rc=$?
  kill "${watchdog}" 2>/dev/null
  wait "${watchdog}" 2>/dev/null
  return ${rc}
}

# 실행 + fallback
run_gemini() {
  local target_model="$1"
  local output
  local actual_cmd=("${GEMINI_CMD}" -m "${target_model}" -p "${FULL_PROMPT}")
  if [[ "${YOLO}" -eq 1 ]]; then
    actual_cmd+=(-y)
  fi

  set +e
  output="$("${actual_cmd[@]}" 2>&1)"
  local rc=$?
  set -e

  printf "%s\n" "${output}"
  return ${rc}
}

is_model_error() {
  local text="$1"
  [[ "${text}" == *"not found"* ]] || \
    [[ "${text}" == *"not supported"* ]] || \
    [[ "${text}" == *"invalid model"* ]] || \
    [[ "${text}" == *"does not exist"* ]]
}

set +e
FIRST_OUTPUT="$(run_gemini "${MODEL}")"
FIRST_RC=$?
set -e

if [[ ${FIRST_RC} -ne 0 ]] && is_model_error "${FIRST_OUTPUT}"; then
  echo "[INFO] model fallback: ${MODEL} -> ${FALLBACK_MODEL}" >&2
  set +e
  SECOND_OUTPUT="$(run_gemini "${FALLBACK_MODEL}")"
  SECOND_RC=$?
  set -e
  printf "%s\n" "${SECOND_OUTPUT}"
  save_to_feedback "${SECOND_OUTPUT}" "${FALLBACK_MODEL}" "${SECOND_RC}"
  exit ${SECOND_RC}
fi

printf "%s\n" "${FIRST_OUTPUT}"
save_to_feedback "${FIRST_OUTPUT}" "${MODEL}" "${FIRST_RC}"
exit ${FIRST_RC}
