# strict warning policy gate slice

- timestamp: `2026-03-19-13-21`
- source_of_truth: [../knowledge_bases/slice-experiment-lab-knowledge_base-at2026-03-19-00-45.md](../knowledge_bases/slice-experiment-lab-knowledge_base-at2026-03-19-00-45.md)
- checklist: [../checklist-forimplementation/implementation-checklist-at2026-03-19-00-45.md](../checklist-forimplementation/implementation-checklist-at2026-03-19-00-45.md)

## Goal

`quick_validate_capture` artifact의 `warnings`와 `errors`를 strict 정책으로 다시 해석해서, 현재 slice를 그대로 넘길지 아니면 hold/invalid로 멈출지 판정한다.

## Implemented Command

- `gate-strict-warning-policy`

## Decision Semantics

- `pass`
  - `status == passed`
  - `warnings == []`
  - `errors == []`
- `hold`
  - `status == passed`
  - `warnings`는 있지만 `errors`는 없음
- `invalid`
  - `status == failed`
  - 또는 `errors`가 존재함
  - 또는 capture artifact 계약 자체가 깨짐

## Smoke Artifacts

- pass:
  - [strict-warning-policy-pass-sample-at2026-03-19-13-21.json](strict-warning-policy-pass-sample-at2026-03-19-13-21.json)
  - [strict-warning-policy-pass-smoke-at2026-03-19-13-21.json](strict-warning-policy-pass-smoke-at2026-03-19-13-21.json)
  - [strict-warning-policy-pass-smoke-at2026-03-19-13-21.md](strict-warning-policy-pass-smoke-at2026-03-19-13-21.md)
- hold:
  - [strict-warning-policy-hold-sample-at2026-03-19-13-21.json](strict-warning-policy-hold-sample-at2026-03-19-13-21.json)
  - [strict-warning-policy-hold-smoke-at2026-03-19-13-21.json](strict-warning-policy-hold-smoke-at2026-03-19-13-21.json)
  - [strict-warning-policy-hold-smoke-at2026-03-19-13-21.md](strict-warning-policy-hold-smoke-at2026-03-19-13-21.md)
- invalid:
  - [strict-warning-policy-invalid-sample-at2026-03-19-13-21.json](strict-warning-policy-invalid-sample-at2026-03-19-13-21.json)
  - [strict-warning-policy-invalid-smoke-at2026-03-19-13-21.json](strict-warning-policy-invalid-smoke-at2026-03-19-13-21.json)
  - [strict-warning-policy-invalid-smoke-at2026-03-19-13-21.md](strict-warning-policy-invalid-smoke-at2026-03-19-13-21.md)

## Result

- pass sample: `decision = pass`, exit code `0`
- hold sample: `decision = hold`, exit code `2`
- invalid sample: `decision = invalid`, exit code `1`

## Notes

- 이 gate는 `quick_validate_status`를 대체하지 않는다.
- 이 gate는 `quick_validate_capture`의 경고와 오류를 strict 정책으로 한 번 더 해석하는 후속 판단 layer다.
