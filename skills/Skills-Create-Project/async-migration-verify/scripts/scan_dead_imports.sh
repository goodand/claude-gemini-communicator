#!/usr/bin/env bash
set -euo pipefail

TARGET_ROOT="${1:-.}"

printf '== dead import candidates ==\n'
grep -rEn "require\(('|\")(fs|node:fs)('|\")\)|from ('|\")(node:fs|fs)('|\")" "$TARGET_ROOT" \
  --exclude-dir=node_modules --exclude-dir=dist 2>/dev/null || true

printf '\n== sync api call candidates ==\n'
grep -rEn "(readFileSync|writeFileSync|existsSync|appendFileSync|mkdirSync|rmSync)" "$TARGET_ROOT" \
  --exclude-dir=node_modules --exclude-dir=dist 2>/dev/null || true
