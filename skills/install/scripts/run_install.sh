#!/bin/zsh
set -euo pipefail

# claude-gemini-communicator 3-Agent 시스템 설치/제거 스크립트.
# 다른 프로젝트에서 이 스크립트를 실행하면 Hook + Skills가 설치된다.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMMUNICATOR_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
CLI_PATH="${COMMUNICATOR_ROOT}/src/cli.py"
PYTHON="${COMMUNICATOR_PYTHON:-python3.13}"

TARGET_DIR=""
UNINSTALL=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  run_install.sh [OPTIONS]

Options:
  --target DIR    대상 프로젝트 디렉토리 (기본: 현재 디렉토리)
  --uninstall     설치 제거
  --dry-run       실행하지 않고 정보만 출력
  -h, --help      도움말

Examples:
  run_install.sh                              # 현재 디렉토리에 설치
  run_install.sh --target /path/to/project    # 지정 디렉토리에 설치
  run_install.sh --uninstall                  # 현재 디렉토리에서 제거
  run_install.sh --dry-run                    # 설치 전 확인
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET_DIR="$2"
      shift 2
      ;;
    --uninstall)
      UNINSTALL=1
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
      echo "[ERROR] 알 수 없는 옵션: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

# 대상 디렉토리 결정: --target > git root > cwd
if [[ -z "${TARGET_DIR}" ]]; then
  if command -v git >/dev/null 2>&1; then
    GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
    if [[ -n "${GIT_ROOT}" ]]; then
      TARGET_DIR="${GIT_ROOT}"
    fi
  fi
fi

if [[ -z "${TARGET_DIR}" ]]; then
  TARGET_DIR="$(pwd)"
fi

TARGET_DIR="$(cd "${TARGET_DIR}" && pwd)"

# Python 확인
if ! command -v "${PYTHON}" >/dev/null 2>&1; then
  # fallback
  for py in python3.13 python3.12 python3.11 python3; do
    if command -v "${py}" >/dev/null 2>&1; then
      PYTHON="${py}"
      break
    fi
  done
fi

if ! command -v "${PYTHON}" >/dev/null 2>&1; then
  echo "[ERROR] Python을 찾을 수 없습니다." >&2
  exit 1
fi

# CLI 존재 확인
if [[ ! -f "${CLI_PATH}" ]]; then
  echo "[ERROR] cli.py를 찾을 수 없습니다: ${CLI_PATH}" >&2
  echo "communicator 프로젝트 구조가 올바른지 확인하세요." >&2
  exit 1
fi

# dry-run
if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "COMMUNICATOR_ROOT=${COMMUNICATOR_ROOT}"
  echo "TARGET_DIR=${TARGET_DIR}"
  echo "PYTHON=${PYTHON}"
  echo "CLI_PATH=${CLI_PATH}"
  if [[ "${UNINSTALL}" -eq 1 ]]; then
    echo "ACTION=uninstall"
  else
    echo "ACTION=install"
  fi
  exit 0
fi

# 실행
if [[ "${UNINSTALL}" -eq 1 ]]; then
  "${PYTHON}" "${CLI_PATH}" uninstall --target "${TARGET_DIR}"
else
  "${PYTHON}" "${CLI_PATH}" install --target "${TARGET_DIR}"
fi
