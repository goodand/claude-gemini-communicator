# Vertical Slice Definition: required_field

- generated_at: `2026-03-16-20-03`
- target skill: `doc-code-sync-checker`
- implementation target: `scripts/doc_code_sync.py`

## Purpose

`doc-code-sync-checker`를 범용 규칙 엔진으로 바로 확장하지 않고, `required_field` 1종으로
`extract-doc -> extract-code -> compare -> report`를 end-to-end로 먼저 닫는다.

## Fixed Pair

- reference 문서: [packet-fields.md](../../agent-task-packet/references/packet-fields.md)
- code script: [packet_builder.py](../../agent-task-packet/scripts/packet_builder.py)

## Why This Pair

- 문서 쪽에 `## 필수 필드` 표가 명확하게 있다.
- 코드 쪽에 `REQUIRED_FIELDS` set과 `validate_packet()` missing-field 검증이 있다.
- 첫 slice에서 문서 추출, 코드 추출, 비교 기준을 명확하게 고정할 수 있다.

## First Rule Type

- rule kind: `required_field`

## Minimal Rule Schema

```json
{
  "kind": "required_field",
  "name": "task_id",
  "source": "doc",
  "value": true,
  "evidence": "## 필수 필드 표의 task_id 행"
}
```

필수 최소 필드:
- `kind`
- `name`
- `source`
- `value`
- `evidence`

## extract-doc Scope

- `packet-fields.md`의 `## 필수 필드` 바로 아래 표만 읽는다.
- 각 행의 `필드` 열을 `required_field.name`으로 변환한다.
- `설명` 열은 compare key가 아니라 evidence로 남긴다.
- `## 선택 필드`, `## 금지 필드`, 중첩 구조 설명은 이번 slice에서 제외한다.

## extract-code Scope

- `packet_builder.py`의 `REQUIRED_FIELDS` set literal을 읽는다.
- 각 항목을 `required_field.name`으로 변환한다.
- `validate_packet()`의 `missing = REQUIRED_FIELDS - set(data.keys())` 분기를 보조 evidence로 남긴다.
- `goal` 최소 길이, `why` 최소 길이, path 중복 검사 등 세부 validator는 이번 slice에서 제외한다.

## compare Semantics

- `missing_in_code`
  - 문서에는 required field가 있는데 code의 `REQUIRED_FIELDS`에는 없음
- `missing_in_doc`
  - code의 `REQUIRED_FIELDS`에는 있는데 문서의 `## 필수 필드` 표에는 없음
- `mismatch`
  - v0.1 required_field slice에서는 기본적으로 비워 둔다
  - 단, 동일 이름 field에 대해 source evidence가 구조적으로 충돌할 때만 사용 가능

## report Expectations

- 사람이 읽는 요약 3~6줄
- 아래 3개를 항상 포함
  - pair 정보
  - `missing_in_code` 요약
  - `missing_in_doc` 요약
- mismatch가 비어 있으면 `없음`으로 명시

## Success Criteria

- `extract-doc`가 `packet-fields.md`에서 필수 필드 목록을 JSON으로 출력한다.
- `extract-code`가 `packet_builder.py`에서 동일한 required field 목록을 JSON으로 출력한다.
- `compare`가 두 목록을 비교해 drift를 계산한다.
- `report`가 사람이 읽는 요약을 출력한다.
- 최소 1개 negative fixture로 `missing_in_code` 또는 `missing_in_doc`를 재현하는 테스트가 있다.

## Non-Goals For This Slice

- 선택 필드 비교
- 필드 설명 문장의 semantic diff
- `goal >= 10자` 같은 value constraint 비교
- enum/상수 집합 비교
- 상태 전이표 비교
- path safety 비교
- repo-wide crawl

## Next Slice Candidates

- `enum_value`
- `path_safety`
- `transition_rule`
