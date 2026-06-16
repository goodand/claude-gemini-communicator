---
name: edge-case-generator
description: >-
  workspace-artifact-production-process family의 validation-input generation
  specialist. Use this skill when Phase 5-2 test inputs for a skill's validate
  function must be generated from extracted validation rules. broader artifact
  production order는 workspace-artifact-production-process를 사용하라.
---

# Edge Case Generator

validate 함수의 검증 규칙을 파싱하여 Phase 5-2 실전 테스트 입력을 자동 생성한다.

## When to use

- 새 스킬의 Phase 5-2 실전 테스트를 준비할 때
- validate 함수를 수정한 후 기존 테스트 케이스를 갱신할 때
- "이 validate가 어떤 입력을 놓치는지" 알고 싶을 때
- Codex 실전 테스트에 넣을 edge case 목록이 필요할 때

## Workflow

1. **규칙 추출** — `scripts/edgegen.py analyze --script <script.py>` → validate 함수에서 검증 규칙 목록 추출
2. **케이스 생성** — `scripts/edgegen.py generate --script <script.py> [--output <dir>]` → 규칙별 경계값·무효값 JSON 파일 자동 생성
3. **실행** — `scripts/edgegen.py run --script <script.py> --cases <dir>` → 각 케이스로 validate 호출 → pass/fail 매트릭스 출력
4. **보고** — `scripts/edgegen.py report --results <results.json>` → 누락 검증 규칙·예상 외 통과 케이스 요약

## Scripts

- `scripts/edgegen.py` — analyze/generate/run/report 통합 래퍼. `python3 scripts/edgegen.py --help`

## References

- `references/rule-taxonomy.md` — 검증 규칙 분류 체계 (7종) + 각 종류별 edge case 생성 전략
- `references/troubleshooting.md` — 실전 버그 케이스

## Notes

- **분석 대상은 validate 함수** — 스크립트 전체가 아니라 `def validate_*` 함수만 파싱
- **생성된 케이스는 "통과하면 안 되는 것"이 핵심** — 정상 케이스보다 실패해야 하는 케이스가 중요
- **결과가 예상과 다르면 버그** — 실패해야 하는데 통과 = validate 누락, 통과해야 하는데 실패 = 과잉 검증
- **파일시스템 케이스는 run 단계 setup이 있을 수 있음** — symlink 같은 환경 의존 검증은 실제 fixture를 만든 뒤 실행
- 기존 스킬의 troubleshooting CASE 패턴에서 edge case 유형을 지속 확장 (→ `references/rule-taxonomy.md`)
