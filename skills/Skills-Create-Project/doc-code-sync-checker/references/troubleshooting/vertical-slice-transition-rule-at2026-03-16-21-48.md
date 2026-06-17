# Vertical Slice Definition: transition_rule

- generated_at: `2026-03-16-21-48`
- target skill: `doc-code-sync-checker`
- implementation target: `scripts/doc_code_sync.py`

## Purpose

`transition_rule`를 세 번째 slice로 추가해, 문서의 상태 전이표와 코드의 실제 전이 dict가
동일한 관계 집합을 가지는지 pairwise smoke-check 한다.

## Fixed Pair

- reference 문서: [dispatch-fields.md](../../codex-worktree-dispatch/references/dispatch-fields.md)
- code script: [dispatch_manager.py](../../codex-worktree-dispatch/scripts/dispatch_manager.py)

## Why This Pair

- 문서 쪽에 `### 유효 전이 테이블`이 있다.
- 코드 쪽에 `VALID_TRANSITIONS` dict가 있다.
- `queued -> blocked` 같은 전이 drift 이력이 있어 재검증 가치가 높다.

## First Rule Type

- rule kind: `transition_rule`

## Minimal Rule Schema

```json
{
  "kind": "transition_rule",
  "name": "queued->blocked",
  "source": "doc",
  "value": true,
  "evidence": "유효 전이 테이블 row"
}
```

필수 최소 필드:
- `kind`
- `name`
- `source`
- `value`
- `evidence`

## extract-doc Scope

- `dispatch-fields.md`의 `### 유효 전이 테이블`만 읽는다.
- 각 행의 `From`, `To`를 `from->to` 규칙으로 변환한다.
- `조건` 열은 compare key가 아니라 evidence로 남긴다.
- 상태 머신 ASCII 다이어그램은 이번 slice에서 제외한다.

## extract-code Scope

- `dispatch_manager.py`의 `VALID_TRANSITIONS` dict literal만 읽는다.
- 각 `from -> to` 관계를 `from->to` 규칙으로 변환한다.
- 상태 처리 함수 본문은 이번 slice에서 제외한다.

## compare Semantics

- `missing_in_code`
  - 문서 전이표에는 있는데 code의 `VALID_TRANSITIONS`에는 없음
- `missing_in_doc`
  - code의 `VALID_TRANSITIONS`에는 있는데 문서 전이표에는 없음
- `mismatch`
  - v0.1 transition slice에서는 기본적으로 비워 둔다

## Success Criteria

- `extract-doc`가 `dispatch-fields.md` 전이표에서 transition rule set을 JSON으로 출력한다.
- `extract-code`가 `dispatch_manager.py`의 `VALID_TRANSITIONS`에서 같은 형태의 rule set을 JSON으로 출력한다.
- `compare`가 drift를 계산한다.
- real pair smoke report를 남긴다.

## Current Smoke Result

- 현재 real pair 결과:
  - `missing_in_code = 0`
  - `missing_in_doc = 0`
  - `mismatch = 0`
- 해석:
  - 전이표와 `VALID_TRANSITIONS`는 현재 slice 기준으로 정합적이다
  - 최신 smoke report: `references/transition-rule-smoke-report-at2026-03-16-21-48.md`
