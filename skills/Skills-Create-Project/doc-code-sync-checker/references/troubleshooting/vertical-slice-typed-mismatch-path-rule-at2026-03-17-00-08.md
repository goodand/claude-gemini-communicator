# doc-code-sync-checker Vertical Slice: typed mismatch (`path_rule_condition_changed`)

## Purpose

- 세 번째 typed mismatch slice를 실제 구현으로 고정한다.
- 이 slice는 경로 안전 규칙 조건 집합이 문서와 코드에서 다를 때 `path_rule_condition_changed` 1건으로 요약한다.

## Scope

- 기반 rule kind: `path_safety`
- 현재 대상 contract: `locked_paths` path safety conditions
- pairwise local analysis만 다룬다.

## Rule Shape

```json
{
  "kind": "path_rule_condition_changed",
  "name": "locked_paths_conditions",
  "doc_values": ["forbid_path_traversal", "forbid_symlink"],
  "code_values": ["forbid_absolute_path", "forbid_symlink"],
  "doc_only": ["forbid_path_traversal"],
  "code_only": ["forbid_absolute_path"],
  "doc_evidence": ["..."],
  "code_evidence": ["..."],
  "reason": "경로 안전 규칙 조건 집합이 문서와 코드에서 다름",
  "action": "locked_paths 경로 규칙의 doc/code 조건 집합 정렬 검토"
}
```

## Strategy

1. 문서 path rule과 코드 path rule을 같은 name set으로 정규화한다.
2. 전체 path safety 조건 집합을 양쪽에서 만든다.
3. 집합이 다르면 `path_rule_condition_changed` 1건을 생성한다.
4. 기존 `missing_in_code`, `missing_in_doc`는 그대로 유지한다.

## Non-goals

- 경로 존재 여부나 실제 파일 시스템 검증까지 확장하지 않는다.
- 자연어 의미 유사도만으로 mismatch를 확정하지 않는다.
- repo-wide path policy diff로 확장하지 않는다.

## Evidence

- synthetic smoke JSON:
  - [typed-mismatch-path-rule-smoke-report-at2026-03-17-00-08.json](./typed-mismatch-path-rule-smoke-report-at2026-03-17-00-08.json)
- synthetic smoke report:
  - [typed-mismatch-path-rule-smoke-report-at2026-03-17-00-08.md](./typed-mismatch-path-rule-smoke-report-at2026-03-17-00-08.md)

## Current Result

- `missing_in_code = 1`
- `missing_in_doc = 1`
- `typed_mismatch = 1`
- 세 번째 typed mismatch category는 기대대로 `path_rule_condition_changed`로 재현됐다.
