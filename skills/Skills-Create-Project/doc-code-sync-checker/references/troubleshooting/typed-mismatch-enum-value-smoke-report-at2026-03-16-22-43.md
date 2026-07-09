# Doc-Code Drift Report

- pair: synthetic-doc-rules(enum_value) <-> synthetic-code-rules(enum_value)
- rule_kind: `enum_value`
- compared_at: `2026-03-16T22:43:20+09:00`

- missing_in_code: 1
  - status:ready -> VALID_STATUSES에 'status:ready' 허용값 추가 검토
- missing_in_doc: 1
  - status:running -> status enum 문서에 'status:running' 허용값 문서화 검토
- mismatch: 0
  - 없음
- typed_mismatch: 1
  - [enum_value_set_changed] status | doc_only=ready | code_only=running -> status enum의 doc/code 허용값 집합 정렬 검토
