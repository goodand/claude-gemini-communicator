#!/usr/bin/env bash
# m5_sync_main.sh — git sync only (checkout main + pull)
# Usage: bash scripts/m5_sync_main.sh
# Run ONLY when user explicitly requests main sync.
# Does NOT run bootstrap or verify — run m5_verify.sh separately after sync.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"

if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

: "${M5_SSH_ALIAS:?M5_SSH_ALIAS must be set in .env}"
if [ "$M5_SSH_ALIAS" = "your-ssh-alias" ]; then
  echo "ERROR: M5_SSH_ALIAS is still the placeholder value."
  exit 1
fi

: "${M5_TMUX_SESSION:?M5_TMUX_SESSION must be set in .env}"
if [ "$M5_TMUX_SESSION" = "codex-remote" ]; then
  echo "ERROR: M5_TMUX_SESSION is still the placeholder value."
  exit 1
fi

REMOTE_REPO='$HOME/Developer/claude-gemini-communicator'

echo "=== remote dirty check ==="
DIRTY="$(ssh -o BatchMode=yes -o ConnectTimeout=10 "$M5_SSH_ALIAS" \
  "zsh -lc \"cd $REMOTE_REPO && git status --short\"")"

if [ -n "$DIRTY" ]; then
  echo "FAIL: remote repo is dirty; refusing sync."
  echo "$DIRTY"
  echo "      Commit or stash remote changes before syncing."
  exit 1
fi
echo "OK: remote repo is clean."

echo ""
echo "=== git sync (checkout main + pull) ==="
ssh -o BatchMode=yes -o ConnectTimeout=30 "$M5_SSH_ALIAS" \
  "zsh -lc \"
  cd $REMOTE_REPO
  git checkout main
  git pull origin main
  git log --oneline -3
  \""

echo ""
echo "Sync complete. Run 'm5_verify.sh' to verify runtime."
