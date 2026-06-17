# doc-code-sync-checker Vertical Slice: typed mismatch (`transition_rule_set_changed`)

## Purpose

- 두 번째 typed mismatch slice를 실제 구현으로 고정한다.
- 이 slice는 상태 전이 집합이 문서와 코드에서 다를 때 `transition_rule_set_changed` 1건으로 요약한다.

## Scope

- 기반 rule kind: `transition_rule`
- 대상 비교 단위: `from->to`
- 현재 대상 contract: dispatch status transition set
- pairwise local analysis만 다룬다.

## Rule Shape

```json
{
  "kind": "transition_rule_set_changed",
  "name": "status_transitions",
  "doc_values": ["queued->blocked", "ready->running"],
  "code_values": ["queued->ready", "ready->running"],
  "doc_only": ["queued->blocked"],
  "code_only": ["queued->ready"],
  "doc_evidence": ["..."],
  "code_evidence": ["..."],
  "reason": "상태 전이 집합이 문서와 코드에서 다름",
  "action": "전이표와 VALID_TRANSITIONS 정렬 검토"
}
```

## Strategy

1. 문서 transition rule과 코드 transition rule을 같은 `from->to` shape로 정규화한다.
2. 전체 전이 집합을 양쪽에서 만든다.
3. 집합이 다르면 `transition_rule_set_changed` 1건을 생성한다.
4. 기존 `missing_in_code`, `missing_in_doc`는 그대로 유지한다.

## Non-goals

- 조건부 semantic 해석까지 확장하지 않는다.
- 자연어 의미 유사도만으로 mismatch를 확정하지 않는다.
- repo-wide state machine diff로 확장하지 않는다.

## Evidence

- synthetic smoke JSON:
  - [typed-mismatch-transition-rule-smoke-report-at2026-03-16-22-57.json](./typed-mismatch-transition-rule-smoke-report-at2026-03-16-22-57.json)
- synthetic smoke report:
  - [typed-mismatch-transition-rule-smoke-report-at2026-03-16-22-57.md](./typed-mismatch-transition-rule-smoke-report-at2026-03-16-22-57.md)

## Current Result

- `missing_in_code = 1`
- `missing_in_doc = 1`
- `typed_mismatch = 1`
- 두 번째 typed mismatch category는 기대대로 `transition_rule_set_changed`로 재현됐다.
