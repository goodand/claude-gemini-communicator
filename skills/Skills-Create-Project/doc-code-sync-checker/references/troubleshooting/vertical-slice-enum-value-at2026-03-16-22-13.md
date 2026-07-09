# Vertical Slice Definition: enum_value

- generated_at: `2026-03-16-22-13`
- target skill: `doc-code-sync-checker`
- implementation target: `scripts/doc_code_sync.py`

## Purpose

`enum_value`를 네 번째 slice로 추가해, 문서의 허용값 집합과 코드의 허용값 집합이
같은지 pairwise smoke-check 한다.

## Fixed Pair

- reference 문서: [dispatch-fields.md](../../codex-worktree-dispatch/references/dispatch-fields.md)
- code script: [dispatch_manager.py](../../codex-worktree-dispatch/scripts/dispatch_manager.py)

## Why This Pair

- 문서 쪽에서 `status` 필드는 enum이며, 상태 전이표에서 실제 허용 상태 집합을 복원할 수 있다.
- 코드 쪽에 `VALID_STATUSES` set이 있다.
- `status enum`과 `transition_rule`은 관련은 있지만 서로 다른 계약이라 별도 slice로 유지할 가치가 있다.

## First Rule Type

- rule kind: `enum_value`

## Minimal Rule Schema

```json
{
  "kind": "enum_value",
  "name": "status:queued",
  "source": "doc",
  "value": true,
  "evidence": "유효 전이 테이블 unique status value"
}
```

필수 최소 필드:
- `kind`
- `name`
- `source`
- `value`
- `evidence`

## extract-doc Scope

- `dispatch-fields.md`의 `### 유효 전이 테이블`에서 `From`, `To`의 unique status 값을 모은다.
- 각 허용값을 `status:<value>` 규칙으로 변환한다.
- `status` 필드가 enum이라는 사실은 scope justification으로만 쓰고 compare key는 허용값 집합으로 둔다.

## extract-code Scope

- `dispatch_manager.py`의 `VALID_STATUSES` set literal을 읽는다.
- 각 허용값을 `status:<value>` 규칙으로 변환한다.

## compare Semantics

- `missing_in_code`
  - 문서 허용값 집합에는 있는데 `VALID_STATUSES`에는 없음
- `missing_in_doc`
  - `VALID_STATUSES`에는 있는데 문서 허용값 집합에는 없음
- `mismatch`
  - v0.1 enum slice에서는 기본적으로 비워 둔다

## Success Criteria

- `extract-doc`가 문서에서 status enum value 집합을 JSON으로 출력한다.
- `extract-code`가 코드에서 `VALID_STATUSES`를 JSON으로 출력한다.
- `compare`가 enum drift를 계산한다.
- real pair smoke report를 남긴다.

## Current Smoke Result

- 현재 real pair 결과:
  - `missing_in_code = 0`
  - `missing_in_doc = 0`
  - `mismatch = 0`
- 해석:
  - status enum 허용값 집합은 현재 문서와 코드가 정합적이다
  - 최신 smoke report: `references/enum-value-smoke-report-at2026-03-16-22-13.md`
