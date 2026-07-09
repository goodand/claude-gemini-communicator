# Vertical Slice Definition: path_safety

- generated_at: `2026-03-16-20-44`
- target skill: `doc-code-sync-checker`
- implementation target: `scripts/doc_code_sync.py`

## Purpose

`required_field` 다음 slice로 `path_safety`를 추가해, 문서의 경로 제약 규칙과
코드의 실제 경로 검증 로직이 일치하는지 pairwise로 smoke-check 한다.

## Fixed Pair

- reference 문서: [dispatch-fields.md](../../codex-worktree-dispatch/references/dispatch-fields.md)
- code script: [dispatch_manager.py](../../codex-worktree-dispatch/scripts/dispatch_manager.py)

## Why This Pair

- 문서 쪽에 `## locked_paths 규칙`이 명시되어 있다.
- 코드 쪽에 `validate_dispatch()`의 `locked_paths` 검증이 명시적으로 들어 있다.
- 실제로 `..`, 절대경로, symlink, `allowed_paths` 범위 제약이 drift 후보였던 이력이 있다.

## First Rule Type

- rule kind: `path_safety`

## Minimal Rule Schema

```json
{
  "kind": "path_safety",
  "name": "forbid_path_traversal",
  "source": "doc",
  "value": true,
  "evidence": "## locked_paths 규칙 bullet"
}
```

필수 최소 필드:
- `kind`
- `name`
- `source`
- `value`
- `evidence`

## Rule Names In v0.1

- `locked_paths_subset_allowed_paths`
- `normalize_trailing_slash`
- `forbid_path_traversal`
- `forbid_absolute_path`
- `forbid_symlink`

## extract-doc Scope

- `dispatch-fields.md`의 `## locked_paths 규칙` bullet만 읽는다.
- 현재 slice에서 문서에서 뽑는 규칙은 아래 4개다.
  - `locked_paths_subset_allowed_paths`
  - `normalize_trailing_slash`
  - `forbid_path_traversal`
  - `forbid_symlink`
- `prefix-level overlap`과 `status 해제 규칙`은 이번 slice에서 제외한다.

## extract-code Scope

- `dispatch_manager.py`의 `_normalize_path()`와 `validate_dispatch()`를 읽는다.
- 현재 slice에서 코드에서 뽑는 규칙은 아래 5개다.
  - `locked_paths_subset_allowed_paths`
  - `normalize_trailing_slash`
  - `forbid_path_traversal`
  - `forbid_absolute_path`
  - `forbid_symlink`
- overlap helper `_paths_overlap()`은 이번 slice에서 제외한다.

## compare Semantics

- `missing_in_code`
  - 문서에 있는 경로 규칙이 코드 구현에 없음
- `missing_in_doc`
  - 코드에 있는 경로 규칙이 문서에 없음
- `mismatch`
  - v0.1 path_safety slice에서는 기본적으로 비워 둔다

## Success Criteria

- `extract-doc`가 `dispatch-fields.md`에서 path safety rule set을 JSON으로 출력한다.
- `extract-code`가 `dispatch_manager.py`에서 path safety rule set을 JSON으로 출력한다.
- `compare`가 path safety drift를 계산한다.
- 실제 pair에서 drift가 있으면 그것을 결과로 남긴다.

## Current Smoke Result

- 현재 real pair 결과:
  - `missing_in_code = 0`
  - `missing_in_doc = 0`
  - `mismatch = 0`
- 해석:
  - `dispatch-fields.md`의 `## locked_paths 규칙`에 절대경로 금지를 추가한 뒤 drift가 닫혔다
  - 최신 smoke report: `references/path-safety-smoke-report-at2026-03-16-21-15.md`
