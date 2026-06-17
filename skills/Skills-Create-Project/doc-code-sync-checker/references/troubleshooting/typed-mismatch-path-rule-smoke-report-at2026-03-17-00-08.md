# Doc-Code Drift Report

- pair: /tmp/doc_code_sync_path_typed/pre_doc.json <-> /tmp/doc_code_sync_path_typed/pre_code.json
- rule_kind: `path_safety`
- compared_at: `2026-03-17T00:09:26+09:00`

- missing_in_code: 1
  - forbid_path_traversal -> validate_dispatch 경로 검증에 'forbid_path_traversal' 규칙 구현 검토
- missing_in_doc: 1
  - forbid_absolute_path -> ## locked_paths 규칙에 'forbid_absolute_path' 규칙 문서화 검토
- mismatch: 0
  - 없음
- typed_mismatch: 1
  - [path_rule_condition_changed] locked_paths_conditions | doc_only=forbid_path_traversal | code_only=forbid_absolute_path -> locked_paths 경로 규칙의 doc/code 조건 집합 정렬 검토
