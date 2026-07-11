#!/usr/bin/env bash
# 가정 원장(ASSUMPTIONS.md)의 자동화 가능한 probe를 한 번에 돌려 집계한다.
# 순수 shell — 어떤 agent/사람/CI든, 어느 머신에서든 실행 가능. 하나라도 실패 시 exit 1.
# '언제 도나'(트리거)는 머신마다 로컬 cron/launchd로 등록 (ASSUMPTIONS.md 하단 참조).
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
fail=0

probe() {  # probe <이름> <명령...>
  local name="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "PASS  $name"
  else
    echo "FAIL  $name"; fail=1
  fi
}

probe "① 복원 키트 이식성 리허설"        bash migration/rehearse.sh
probe "② catalog↔resolver drift 0"       python3 skills/catalog_resolver_audit.py
probe "③ 통합 gate 통과"                 python3 skills/integration-gate/run_integration_gate.py
probe "④ resolver 사용자명 하드코딩 0"   bash -c '! grep -q /Users/jaehyuntak skills/resolve_skill.py'
probe "⑤ 실행코드 하드코딩 경로 0"       bash -c '! git grep -qE "/Users/[^/]+/(Desktop|control|agent)" -- "*.py" "*.sh"'

echo "---"
if [ "$fail" = 0 ]; then
  echo "ALL GREEN — 원장의 자동 probe 전부 통과"
else
  echo "일부 FAIL — ASSUMPTIONS.md에서 해당 줄을 열어 조사"
fi
exit "$fail"
