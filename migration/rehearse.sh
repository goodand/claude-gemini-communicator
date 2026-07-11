#!/usr/bin/env bash
# 마이그레이션 리허설 — 합성 $HOME에서 심링크 복원 스크립트를 돌려
# 이식성(사용자명/경로 독립)을 실제 이사 전에 검증한다.
# 네트워크·실제 clone 없이 기제만 확인(타겟은 stub). exit 0=PASS.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="$REPO/migration/restore-global-symlinks.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# 1) 복원 스크립트가 만들 링크의 '타겟'을 합성 HOME 아래 stub 디렉토리로 생성
grep '^link ' "$SCRIPT" | sed -E 's/^link "([^"]+)".*/\1/' \
  | sed "s|\$HOME|$TMP|" | while IFS= read -r t; do mkdir -p "$t"; done

# 2) 합성 HOME으로 복원 실행 (여기서 $HOME 치환이 실제로 동작하는지 검증됨)
HOME="$TMP" bash "$SCRIPT" >/dev/null

# 3) 검증
expected=$(grep -c '^link ' "$SCRIPT")
roots=("$TMP/.codex/skills" "$TMP/.claude/skills" "$TMP/.claude/agents" "$TMP/control" "$TMP/agent")
created=$(find "${roots[@]}" -type l 2>/dev/null | wc -l | tr -d ' ')
dangling=0
while IFS= read -r l; do [ -e "$l" ] || dangling=$((dangling+1)); done \
  < <(find "${roots[@]}" -type l 2>/dev/null)
# 생성된 링크가 원래 사용자명을 문자열로 물고 있으면 $HOME 치환 실패
leaked=$(find "$TMP" -type l -exec readlink {} \; 2>/dev/null \
         | grep -c "/Users/jaehyuntak" || true)

echo "리허설: 기대 $expected / 생성 $created / 깨짐 $dangling / 사용자명누수 $leaked"
if [ "$created" = "$expected" ] && [ "$dangling" = 0 ] && [ "$leaked" = 0 ]; then
  echo "PASS — 키트는 다른 \$HOME(=다른 사용자명)에서도 이식 가능"
  exit 0
fi
echo "FAIL — 이식성 문제 (위 수치 확인)"
exit 1
