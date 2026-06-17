#!/usr/bin/env bash
# bootstrap_agent_runtime_mac.sh — Agent Skill runtime bootstrap for macOS Apple Silicon
# Prereq: run AFTER git clone, from skills/Skills-Create-Project/
# Usage: bash _shared/scripts/bootstrap_agent_runtime_mac.sh
set -euo pipefail

# ── 0. Apple Silicon Homebrew PATH ───────────────────────────────────────────
# /opt/homebrew is the arm64 prefix; Intel uses /usr/local.
# Also add python@3.13 libexec so the unversioned python3 symlink resolves to 3.13
# even when brew install python@3.13 is keg-only (not globally linked).
if [ -d /opt/homebrew/bin ] && [[ ":$PATH:" != *":/opt/homebrew/bin:"* ]]; then
  export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"
fi
if [ -d /opt/homebrew/opt/python@3.13/libexec/bin ] && \
   [[ ":$PATH:" != *":/opt/homebrew/opt/python@3.13/libexec/bin:"* ]]; then
  export PATH="/opt/homebrew/opt/python@3.13/libexec/bin:$PATH"
fi

# ── 1. CWD guard ─────────────────────────────────────────────────────────────
EXPECTED_DIR="Skills-Create-Project"
ACTUAL_DIR="$(basename "$(pwd)")"
if [ "$ACTUAL_DIR" != "$EXPECTED_DIR" ]; then
  echo "ERROR: must run from skills/Skills-Create-Project/, got: $(pwd)"
  echo "  cd <repo>/skills/Skills-Create-Project && bash _shared/scripts/bootstrap_agent_runtime_mac.sh"
  exit 1
fi
SKILLS_ROOT="$(pwd)"
echo "SKILLS_ROOT: $SKILLS_ROOT"

# ── 1b. PYTHON_BIN resolution ────────────────────────────────────────────────
# Priority: python@3.13 libexec → /opt/homebrew/bin/python3.13 → PATH python3.
# Explicit paths handle keg-only installs where 'python3' on PATH is still 3.9.
PYTHON_BIN=""
for _candidate in \
  "/opt/homebrew/opt/python@3.13/libexec/bin/python3" \
  "/opt/homebrew/bin/python3.13" \
  "$(command -v python3 2>/dev/null || true)"; do
  if [ -x "${_candidate:-}" ]; then
    PYTHON_BIN="$_candidate"
    break
  fi
done
if [ -z "$PYTHON_BIN" ]; then
  echo "ERROR: python3 not found. Install via: brew install python@3.13"
  exit 1
fi
echo ""
echo "=== Python interpreter ==="
echo "OK:      PYTHON_BIN=$PYTHON_BIN ($("$PYTHON_BIN" --version 2>&1))"

# ── 2. Dependency checks ──────────────────────────────────────────────────────
MISSING=0

check_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "MISSING: $cmd"
    MISSING=$((MISSING + 1))
  else
    echo "OK:      $cmd ($(command -v "$cmd"))"
  fi
}

check_version() {
  # Usage: check_version <cmd> <version-arg> <min_major> [min_minor] [strict]
  # strict=true: version below minimum increments MISSING (FAIL); default is WARN only.
  local cmd="$1" arg="$2" min_major="$3" min_minor="${4:-0}" strict="${5:-false}"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "MISSING: $cmd"
    MISSING=$((MISSING + 1))
    return
  fi
  local raw
  raw="$($cmd $arg 2>&1 | head -1)"
  local ver
  ver="$(echo "$raw" | grep -oE '[0-9]+\.[0-9]+' | head -1)"
  local major minor
  major="${ver%%.*}"
  minor="${ver#*.}"
  minor="${minor%%.*}"
  if [ "${major:-0}" -gt "$min_major" ] || \
     { [ "${major:-0}" -eq "$min_major" ] && [ "${minor:-0}" -ge "$min_minor" ]; }; then
    echo "OK:      $cmd $ver (>= ${min_major}.${min_minor})"
  else
    if [ "$strict" = "true" ]; then
      echo "FATAL:   $cmd $ver < required ${min_major}.${min_minor} — install via Homebrew and retry"
      MISSING=$((MISSING + 1))
    else
      echo "WARN:    $cmd $ver is below recommended ${min_major}.${min_minor}"
    fi
  fi
}

echo ""
echo "=== Dependency check ==="
check_version git          "--version"  2  40
check_version "$PYTHON_BIN" "--version"  3  11  true   # strict: FAIL if < 3.11
check_version node    "--version"  18   0
check_version tmux    "-V"         3   6
check_version rg      "--version"  13   0
check_cmd gh
check_cmd uv

if [ "$MISSING" -gt 0 ]; then
  echo ""
  echo "ERROR: $MISSING required tool(s) not found or below minimum version."
  echo "       Install missing tools via Homebrew and retry."
  exit 1
fi

# ── 3. .env setup ─────────────────────────────────────────────────────────────
echo ""
echo "=== .env setup ==="
if [ -f "$SKILLS_ROOT/.env.example" ]; then
  if [ -f "$SKILLS_ROOT/.env" ]; then
    echo "SKIP:    .env already exists — not overwritten"
  else
    cp "$SKILLS_ROOT/.env.example" "$SKILLS_ROOT/.env"
    echo "CREATED: .env from .env.example"
    echo "ACTION:  Fill in actual API keys in $SKILLS_ROOT/.env before running skills"
  fi
else
  echo "SKIP:    .env.example not found — skipping .env creation"
fi

# ── 4. .mcp.json setup ────────────────────────────────────────────────────────
echo ""
echo "=== .mcp.json setup ==="
if [ -f "$SKILLS_ROOT/.mcp.example.json" ]; then
  if [ -f "$SKILLS_ROOT/.mcp.json" ]; then
    echo "SKIP:    .mcp.json already exists — not overwritten"
  else
    cp "$SKILLS_ROOT/.mcp.example.json" "$SKILLS_ROOT/.mcp.json"
    echo "CREATED: .mcp.json from .mcp.example.json"
  fi
else
  echo "SKIP:    .mcp.example.json not found — skipping .mcp.json creation"
fi

# ── 5. venv + Python dependencies ────────────────────────────────────────────
# Create a repo-local .venv so verify_agent_runtime_mac.sh gets reproducible
# dependency state (pytest, pydantic, ...) without polluting the system Python.
# _shared/requirements-verify.txt is the source-of-truth.
echo ""
echo "=== Python venv + dependencies ==="
VENV_DIR="$SKILLS_ROOT/.venv"
REQUIREMENTS="$SKILLS_ROOT/_shared/requirements-verify.txt"
RUNTIME_DIR="$SKILLS_ROOT/.runtime"

if [ ! -f "$REQUIREMENTS" ]; then
  echo "WARN:    $REQUIREMENTS not found — skipping venv setup"
  echo "         verify may fail at dependency preflight"
else
  # Create venv if absent
  if [ ! -d "$VENV_DIR" ]; then
    echo "Creating .venv with $PYTHON_BIN ..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
    echo "OK:      .venv created at $VENV_DIR"
  else
    echo "OK:      .venv already exists at $VENV_DIR"
  fi

  VENV_PYTHON="$VENV_DIR/bin/python"

  echo "Installing from _shared/requirements-verify.txt ..."
  "$VENV_PYTHON" -m pip install --quiet -r "$REQUIREMENTS"
  echo "OK:      installed: $(tr '\n' ' ' < "$REQUIREMENTS")"

  # Write .runtime/python_bin so verify_agent_runtime_mac.sh uses the same interpreter.
  mkdir -p "$RUNTIME_DIR"
  echo "$VENV_PYTHON" > "$RUNTIME_DIR/python_bin"
  echo "OK:      interpreter pinned → .runtime/python_bin ($VENV_PYTHON)"
fi

# ── 6. Absolute path scan (warning, non-blocking) ─────────────────────────────
# Scans .py, .sh, and .json runtime files.
# Excludes frozen artifact dirs (evals, backups, references, .claude) — not runtime defaults.
# Excludes this script and verify_agent_runtime_mac.sh (which contain the pattern as a grep literal).
echo ""
echo "=== Absolute path scan (runtime scripts only) ==="
ABS_HITS_BOOTSTRAP="$(grep -r "/Users/" "$SKILLS_ROOT" \
  --include="*.py" --include="*.sh" --include="*.json" \
  --exclude-dir=__pycache__ --exclude-dir=.git \
  --exclude-dir=evals --exclude-dir=backups \
  --exclude-dir=references --exclude-dir=.claude \
  --exclude-dir=.venv --exclude-dir=.runtime \
  --exclude="bootstrap_agent_runtime_mac.sh" \
  --exclude="verify_agent_runtime_mac.sh" \
  -l 2>/dev/null || true)"
if [ -n "$ABS_HITS_BOOTSTRAP" ]; then
  echo "WARN:    /Users/ absolute path(s) found in runtime scripts:"
  echo "$ABS_HITS_BOOTSTRAP" | sed 's/^/  /'
  echo "         Replace with \$SKILLS_ROOT or relative paths before new-Mac deploy."
  echo "         (non-blocking in bootstrap; verify_agent_runtime_mac.sh treats this as FAIL)"
else
  echo "OK:      no /Users/ absolute paths in runtime scripts"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "=== Bootstrap complete ==="
echo "Next: bash _shared/scripts/verify_agent_runtime_mac.sh"
echo "      (API keys in .env are NOT required for verify to pass)"
exit 0
