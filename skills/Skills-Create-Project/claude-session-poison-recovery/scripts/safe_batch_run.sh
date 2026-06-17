#!/usr/bin/env bash
# Run a long batch command safely:
# - combined stdout/stderr is sanitized and written only to a log file
# - terminal receives only a short summary by default
# - optional tail preview is re-sanitized before display
#
# Usage:
#   bash scripts/safe_batch_run.sh logs/run_latest.log -- python3 some_eval.py
#
# Optional env:
#   SAFE_BATCH_SHOW_TAIL=1       show sanitized tail after completion
#   SAFE_BATCH_TAIL_LINES=20     tail line count when SAFE_BATCH_SHOW_TAIL=1

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ $# -lt 3 || "$2" != "--" ]]; then
  echo "Usage: bash scripts/safe_batch_run.sh <log-path> -- <command...>" >&2
  exit 2
fi

LOG_PATH="$1"
shift 2
CMD=("$@")

mkdir -p "$(dirname "$LOG_PATH")"

echo "[safe-batch] start: ${CMD[*]}"
echo "[safe-batch] log: $LOG_PATH"

set +e
TERM=dumb NO_COLOR=1 CI=1 PYTHONIOENCODING=utf-8 \
  "${CMD[@]}" 2>&1 \
  | python3 "$ROOT/scripts/sanitize_stream.py" > "$LOG_PATH"
CMD_STATUS=${PIPESTATUS[0]}
set -e

echo "[safe-batch] exit_code: $CMD_STATUS"
echo "[safe-batch] done: $LOG_PATH"
echo "[safe-batch] lines: $(wc -l < "$LOG_PATH")"
echo "[safe-batch] size: $(du -h "$LOG_PATH" | cut -f1)"

if [[ "${SAFE_BATCH_SHOW_TAIL:-0}" == "1" ]]; then
  TAIL_LINES="${SAFE_BATCH_TAIL_LINES:-20}"
  echo "[safe-batch] sanitized_tail_last_${TAIL_LINES}:"
  tail -n "$TAIL_LINES" "$LOG_PATH" | python3 "$ROOT/scripts/sanitize_stream.py" || true
fi

exit "$CMD_STATUS"
