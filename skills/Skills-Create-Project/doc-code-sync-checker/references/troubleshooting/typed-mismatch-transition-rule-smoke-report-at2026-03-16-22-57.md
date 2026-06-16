# Doc-Code Drift Report

- pair: synthetic-doc-rules(transition_rule) <-> synthetic-code-rules(transition_rule)
- rule_kind: `transition_rule`
- compared_at: `2026-03-16T22:57:43+09:00`

- missing_in_code: 1
  - queued->blocked -> VALID_TRANSITIONS에 'queued->blocked' 전이 추가 검토
- missing_in_doc: 1
  - queued->ready -> ### 유효 전이 테이블에 'queued->ready' 전이 문서화 검토
- mismatch: 0
  - 없음
- typed_mismatch: 1
  - [transition_rule_set_changed] status_transitions | doc_only=queued->blocked | code_only=queued->ready -> 전이표와 VALID_TRANSITIONS 정렬 검토
