#!/usr/bin/env bash
# m5_verify.sh — bootstrap + verify on current remote checkout, no git mutation
# Usage: bash scripts/m5_verify.sh
# Prereq: .env with M5_SSH_ALIAS set to actual alias (not placeholder)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"

if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

# Fail-fast: M5_SSH_ALIAS must be set and must not be the placeholder value
: "${M5_SSH_ALIAS:?M5_SSH_ALIAS must be set in .env (copy .env.example and fill in actual values)}"
if [ "$M5_SSH_ALIAS" = "your-ssh-alias" ]; then
  echo "ERROR: M5_SSH_ALIAS is still the placeholder value."
  echo "       Edit .env and set M5_SSH_ALIAS to your actual SSH alias."
  exit 1
fi

# Fail-fast: M5_TMUX_SESSION must not be the placeholder value
: "${M5_TMUX_SESSION:?M5_TMUX_SESSION must be set in .env}"
if [ "$M5_TMUX_SESSION" = "codex-remote" ]; then
  echo "ERROR: M5_TMUX_SESSION is still the placeholder value."
  echo "       Edit .env and set M5_TMUX_SESSION to your actual tmux session name."
  exit 1
fi

# Remote path — single-quoted to prevent local $HOME expansion
REMOTE_SKILLS_ROOT='$HOME/Developer/claude-gemini-communicator/skills/Skills-Create-Project'

echo "=== SSH health check ==="
ssh -o BatchMode=yes -o ConnectTimeout=5 "$M5_SSH_ALIAS" \
  'zsh -lc "hostname && whoami && which python3 && python3 --version"'

echo ""
echo "=== bootstrap + verify (no git mutation) ==="
ssh -o BatchMode=yes -o ConnectTimeout=120 "$M5_SSH_ALIAS" \
  "zsh -lc \"
  set -euo pipefail
  cd $REMOTE_SKILLS_ROOT
  bash _shared/scripts/bootstrap_agent_runtime_mac.sh
  bash _shared/scripts/verify_agent_runtime_mac.sh
  echo ''
  echo '=== git status ==='
  git status --short
  git check-ignore -v .env .mcp.json
  \""
