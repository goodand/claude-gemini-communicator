# doc-code-sync-checker Vertical Slice: typed mismatch (`enum_value_set_changed`)

## Purpose

- `mismatch`를 자유형 semantic 판정으로 확장하지 않고, 첫 typed mismatch slice 하나를 실제 구현으로 고정한다.
- 첫 slice는 `enum_value_set_changed`다.

## Scope

- 기반 rule kind: `enum_value`
- 대상 비교 단위: `field:value`
- 현재 대상 field: `status`
- pairwise local analysis만 다룬다.

## Rule Shape

```json
{
  "kind": "enum_value_set_changed",
  "name": "status",
  "doc_values": ["queued", "ready"],
  "code_values": ["queued", "running"],
  "doc_only": ["ready"],
  "code_only": ["running"],
  "doc_evidence": ["..."],
  "code_evidence": ["..."],
  "reason": "status 허용값 집합이 문서와 코드에서 다름",
  "action": "status enum의 doc/code 허용값 집합 정렬 검토"
}
```

## Strategy

1. 문서 enum rule과 코드 enum rule을 같은 `field:value` shape로 정규화한다.
2. 같은 field에 대해 양쪽 값 집합을 만든다.
3. 값 집합이 다르면 `enum_value_set_changed` 1건을 생성한다.
4. 기존 `missing_in_code`, `missing_in_doc`는 그대로 유지한다.

## Non-goals

- 자연어 의미 유사도만으로 mismatch를 확정하지 않는다.
- LLM judge를 필수 전제로 두지 않는다.
- repo-wide semantic diff로 확장하지 않는다.

## Evidence

- synthetic smoke JSON:
  - [typed-mismatch-enum-value-smoke-report-at2026-03-16-22-43.json](./typed-mismatch-enum-value-smoke-report-at2026-03-16-22-43.json)
- synthetic smoke report:
  - [typed-mismatch-enum-value-smoke-report-at2026-03-16-22-43.md](./typed-mismatch-enum-value-smoke-report-at2026-03-16-22-43.md)

## Current Result

- `missing_in_code = 1`
- `missing_in_doc = 1`
- `typed_mismatch = 1`
- 첫 typed mismatch category는 기대대로 `enum_value_set_changed`로 재현됐다.
