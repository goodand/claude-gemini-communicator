#!/usr/bin/env bash
set -euo pipefail

MODE=""
WORKSPACE=""
FILE=""
WINDOW_FLAG="--reuse-window"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="$2"
      shift 2
      ;;
    --workspace)
      WORKSPACE="$2"
      shift 2
      ;;
    --file)
      FILE="$2"
      shift 2
      ;;
    --reuse-window)
      WINDOW_FLAG="--reuse-window"
      shift
      ;;
    --new-window)
      WINDOW_FLAG="--new-window"
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$MODE" || -z "$WORKSPACE" ]]; then
  echo "Usage: $0 --workspace <dir> --mode fabriqa|text|clear [--file <file>] [--reuse-window|--new-window]" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 "$SCRIPT_DIR/switch_vscode_markdown_mode.py" \
  --workspace "$WORKSPACE" \
  --mode "$MODE"

code "$WINDOW_FLAG" "$WORKSPACE"

if [[ -n "$FILE" ]]; then
  code "$WINDOW_FLAG" -g "$FILE"
fi

echo "Opened VS Code with mode=$MODE"
echo "Workspace: $WORKSPACE"
if [[ -n "$FILE" ]]; then
  echo "File: $FILE"
fi
