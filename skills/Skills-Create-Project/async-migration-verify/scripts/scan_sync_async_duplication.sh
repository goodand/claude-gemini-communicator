#!/usr/bin/env bash
set -euo pipefail

TARGET_ROOT="${1:-.}"

printf '== sync/async function pair candidates ==\n'
grep -rEn "function [A-Za-z0-9_]+(Sync|Async)|const [A-Za-z0-9_]+ = async |async function [A-Za-z0-9_]+" "$TARGET_ROOT" \
  --exclude-dir=node_modules --exclude-dir=dist 2>/dev/null || true

printf '\n== parser / normalize / validate duplication hints ==\n'
grep -rEn "(parse|normalize|validate)[A-Za-z0-9_]*" "$TARGET_ROOT" \
  --exclude-dir=node_modules --exclude-dir=dist 2>/dev/null || true
