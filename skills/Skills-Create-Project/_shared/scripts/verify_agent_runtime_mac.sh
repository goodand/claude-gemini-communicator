#!/usr/bin/env bash
# verify_agent_runtime_mac.sh — Agent Skill runtime verification for macOS Apple Silicon
# Usage: bash _shared/scripts/verify_agent_runtime_mac.sh
# CWD REQUIRED: skills/Skills-Create-Project/
set -euo pipefail

PASS=0
FAIL=0
WARN=0

ok()   { echo "PASS: $*"; PASS=$((PASS+1)); }
fail() { echo "FAIL: $*"; FAIL=$((FAIL+1)); }
warn() { echo "WARN: $*"; WARN=$((WARN+1)); }

# ── 0. Apple Silicon Homebrew PATH ───────────────────────────────────────────
if [ -d /opt/homebrew/bin ] && [[ ":$PATH:" != *":/opt/homebrew/bin:"* ]]; then
  export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"
fi

# ── 1. CWD guard (blocking) ───────────────────────────────────────────────────
EXPECTED_DIR="Skills-Create-Project"
ACTUAL_DIR="$(basename "$(pwd)")"
if [ "$ACTUAL_DIR" != "$EXPECTED_DIR" ]; then
  echo "ERROR: CWD must be skills/Skills-Create-Project/"
  echo "  Got: $(pwd)"
  echo "  Fix: cd <repo>/skills/Skills-Create-Project && bash _shared/scripts/verify_agent_runtime_mac.sh"
  exit 1
fi
SKILLS_ROOT="$(pwd)"

echo "=== verify_agent_runtime_mac.sh ==="
echo "SKILLS_ROOT: $SKILLS_ROOT"
echo ""

# ── 1b. PYTHON_BIN resolution ────────────────────────────────────────────────
# Resolve canonical python3 (post-Homebrew PATH prepend) for all gate commands.
PYTHON_BIN="$(command -v python3 2>/dev/null || echo '')"
if [ -z "$PYTHON_BIN" ]; then
  echo "ERROR: python3 not found on PATH after Homebrew prepend"
  exit 1
fi

# ── 1c. Required-file preflight (blocking) ────────────────────────────────────
echo "--- Gate: preflight ---"
PREFLIGHT_FAIL=0
for required_file in \
  "_shared/scripts/smoke_runner.py" \
  "_shared/scripts/audit_cross_skill_dependencies.py"; do
  if [ ! -f "$required_file" ]; then
    echo "MISSING: $required_file"
    PREFLIGHT_FAIL=$((PREFLIGHT_FAIL + 1))
  else
    echo "OK:      $required_file"
  fi
done
if [ "$PREFLIGHT_FAIL" -gt 0 ]; then
  echo ""
  echo "ERROR: $PREFLIGHT_FAIL required script(s) missing."
  echo "       Run bootstrap first, or ensure feat/skill-v0-import-baseline is merged."
  exit 1
fi

# ── 2. Smoke 34/34 ───────────────────────────────────────────────────────────
echo "--- Gate: smoke ---"
SMOKE_OUT="$("$PYTHON_BIN" _shared/scripts/smoke_runner.py --skills-root . 2>&1)"
SMOKE_PASSED="$(echo "$SMOKE_OUT" | "$PYTHON_BIN" -c "import sys,json; d=json.load(sys.stdin); print(d.get('passed',0))" 2>/dev/null || echo 0)"
SMOKE_FAILED="$(echo "$SMOKE_OUT" | "$PYTHON_BIN" -c "import sys,json; d=json.load(sys.stdin); print(d.get('failed',0))" 2>/dev/null || echo -1)"
if [ "$SMOKE_PASSED" -eq 34 ] && [ "$SMOKE_FAILED" -eq 0 ]; then
  ok "smoke ${SMOKE_PASSED}/34 PASS"
else
  fail "smoke ${SMOKE_PASSED}/34 (failed=${SMOKE_FAILED})"
  echo "$SMOKE_OUT" | "$PYTHON_BIN" -c "
import sys, json
try:
  d = json.load(sys.stdin)
  for s, errs in d.get('failed_skills', {}).items():
    print(f'  FAIL skill: {s}')
    for e in errs:
      print(f'    {e}')
except Exception:
  pass
" 2>/dev/null || true
fi

# ── 3. Unit 446/446 ───────────────────────────────────────────────────────────
# --ignore-glob="**/backups/**": skip test files inside backups/ dirs to prevent
# pycache import-file-mismatch on dev machines that have backups/ present.
# On a clean clone (no backups/), this flag has no effect.
# -p no:cacheprovider: do not write .pytest_cache (CI-safe).
# CWD MUST be skills/Skills-Create-Project/ (enforced by guard above).
echo ""
echo "--- Gate: unit ---"
set +e
PYTEST_OUT="$("$PYTHON_BIN" -m pytest . -q -p no:cacheprovider --ignore-glob="**/backups/**" 2>&1)"
PYTEST_EXIT=$?
set -e
PYTEST_SUMMARY="$(echo "$PYTEST_OUT" | tail -1)"
if [ "$PYTEST_EXIT" -eq 0 ] && echo "$PYTEST_SUMMARY" | grep -q "446 passed"; then
  ok "unit 446/446 PASS"
elif [ "$PYTEST_EXIT" -eq 0 ]; then
  warn "unit pytest exit 0 but count unexpected: $PYTEST_SUMMARY"
else
  fail "unit pytest exit $PYTEST_EXIT — $PYTEST_SUMMARY"
  echo "$PYTEST_OUT" | grep -E "FAILED|ERROR|ModuleNotFoundError|no module" | head -10
fi

# ── 4. Audit ──────────────────────────────────────────────────────────────────
echo ""
echo "--- Gate: audit ---"
set +e
"$PYTHON_BIN" _shared/scripts/audit_cross_skill_dependencies.py --skills-root . >/dev/null 2>&1
AUDIT_EXIT=$?
set -e
if [ "$AUDIT_EXIT" -eq 0 ]; then
  ok "audit exit 0 PASS"
else
  fail "audit exit $AUDIT_EXIT"
fi

# ── 5. No-abs-path scan (blocking) ────────────────────────────────────────────
# Scans .py, .sh, and .json — covers .mcp.example.json and other runtime config files.
# Excludes frozen artifact dirs (evals, backups, references, .claude) — they may
# legitimately contain captured absolute paths and are not runtime defaults.
# Excludes this script and bootstrap (which contain "/Users/" as the grep pattern literal).
# Note: grep no-match = exit 1 — use || true to avoid set -e triggering.
echo ""
echo "--- Gate: no-abs-path ---"
ABS_HITS="$(grep -r "/Users/" . \
  --include="*.py" --include="*.sh" --include="*.json" \
  --exclude-dir=__pycache__ --exclude-dir=.git \
  --exclude-dir=evals --exclude-dir=backups \
  --exclude-dir=references --exclude-dir=.claude \
  --exclude="bootstrap_agent_runtime_mac.sh" \
  --exclude="verify_agent_runtime_mac.sh" \
  -l 2>/dev/null || true)"
if [ -n "$ABS_HITS" ]; then
  fail "absolute path /Users/ found in runtime scripts:"
  echo "$ABS_HITS" | sed 's/^/  /'
else
  ok "no /Users/ absolute paths in runtime scripts"
fi

# ── 6. MCP dry-run (non-blocking) ─────────────────────────────────────────────
echo ""
echo "--- Gate: MCP dry-run (non-blocking) ---"
if command -v uvx >/dev/null 2>&1; then
  set +e
  uvx codex-as-mcp@latest --version >/dev/null 2>&1
  MCP_EXIT=$?
  set -e
  if [ "$MCP_EXIT" -eq 0 ]; then
    warn "MCP codex-subagent: uvx OK (non-blocking)"
  else
    warn "MCP codex-subagent: uvx present but codex-as-mcp@latest failed (network/pkg issue) — non-blocking"
  fi
else
  warn "uvx not found — MCP dry-run skipped (non-blocking)"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "=== Verify summary ==="
echo "  PASS: $PASS  FAIL: $FAIL  WARN: $WARN"
echo ""

REQUIRED_PASS=4   # smoke, unit, audit, no-abs-path
if [ "$PASS" -ge "$REQUIRED_PASS" ] && [ "$FAIL" -eq 0 ]; then
  echo "verify: ALL GATES PASS"
  exit 0
else
  echo "verify: FAILED ($FAIL gate(s) failed)"
  exit 1
fi
