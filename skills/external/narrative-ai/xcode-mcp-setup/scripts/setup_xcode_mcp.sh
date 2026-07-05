#!/usr/bin/env bash

set -euo pipefail

XCODE_PATH="/Applications/Xcode.app"
CLI="codex"
SCOPE="user"

usage() {
  cat <<'EOF'
Usage:
  bash setup_xcode_mcp.sh [--xcode-path PATH] [--cli codex|claude|gemini|all] [--scope user|project]

Examples:
  bash setup_xcode_mcp.sh --xcode-path /Applications/Xcode.app --cli codex
  bash setup_xcode_mcp.sh --xcode-path /Applications/Xcode-beta.app --cli all --scope user
EOF
}

register_codex() {
  if ! command -v codex >/dev/null 2>&1; then
    echo "Skipping Codex CLI: 'codex' command not found." >&2
    return 0
  fi

  echo
  echo "==> Registering Xcode MCP with Codex CLI"
  codex mcp add xcode -- xcrun mcpbridge || true
  codex mcp list || true
}

register_claude() {
  if ! command -v claude >/dev/null 2>&1; then
    echo "Skipping Claude Code: 'claude' command not found." >&2
    return 0
  fi

  echo
  echo "==> Registering Xcode MCP with Claude Code"
  claude mcp add --transport stdio --scope "$SCOPE" xcode -- xcrun mcpbridge || true
  claude mcp list || true
}

register_gemini() {
  if ! command -v gemini >/dev/null 2>&1; then
    echo "Skipping Gemini CLI: 'gemini' command not found." >&2
    return 0
  fi

  echo
  echo "==> Registering Xcode MCP with Gemini CLI"
  gemini mcp add -s "$SCOPE" xcode xcrun mcpbridge || true
  gemini mcp list || true
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --xcode-path)
      XCODE_PATH="${2:-}"
      shift 2
      ;;
    --cli)
      CLI="${2:-}"
      shift 2
      ;;
    --scope)
      SCOPE="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ ! -d "$XCODE_PATH" ]]; then
  echo "Error: Xcode not found at: $XCODE_PATH" >&2
  exit 1
fi

if [[ "$SCOPE" != "user" && "$SCOPE" != "project" ]]; then
  echo "Error: --scope must be 'user' or 'project'" >&2
  exit 1
fi

if [[ "$CLI" != "codex" && "$CLI" != "claude" && "$CLI" != "gemini" && "$CLI" != "all" ]]; then
  echo "Error: --cli must be one of: codex, claude, gemini, all" >&2
  exit 1
fi

echo "==> Switching active developer directory"
sudo xcode-select --switch "${XCODE_PATH}/Contents/Developer"

echo
echo "==> Verifying active Xcode"
xcode-select -p
xcodebuild -version

echo
echo "==> Running Xcode first-launch setup"
sudo xcodebuild -runFirstLaunch

echo
echo "==> Checking for mcpbridge"
if ! xcrun mcpbridge -h >/dev/null 2>&1; then
  cat >&2 <<'EOF'
Error: xcrun mcpbridge is not available.

Check:
1. The selected Xcode path is correct.
2. xcodebuild -runFirstLaunch completed successfully.
3. In Xcode, open:
   Settings > Intelligence > Model Context Protocol
   and enable:
   Xcode Tools
EOF
  exit 1
fi

echo "mcpbridge found."

case "$CLI" in
  codex)
    register_codex
    ;;
  claude)
    register_claude
    ;;
  gemini)
    register_gemini
    ;;
  all)
    register_codex
    register_claude
    register_gemini
    ;;
esac

cat <<'EOF'

Setup steps are complete.

Manual step still required:
1. Open Xcode
2. Go to:
   Settings > Intelligence > Model Context Protocol
3. Enable:
   Xcode Tools

Then keep Xcode open and approve any access prompt shown when your CLI connects.
EOF
