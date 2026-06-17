# dependency-slice-planner wrapper_path_mutation_register slice

- implementation_target: `wrapper_path_mutation_register`
- created_at: `2026-03-20-01-20`
- status: `implemented`

## Goal

`wrapper/path-mutation` evidence를 `static_dependency_overlay` 이전 단계에서 독립 artifact로 정규화한다.

## Input

- `wrapper_path_mutation_manifest.json`

## Output

- `wrapper_path_mutation_register.json`
- validation artifact

## Why This Exists

- KB는 `wrapper/path-mutation register`를 strongly recommended signal로 분리한다.
- 기존 구현에도 `wrapper_path_edges`는 있었지만, 이 slice는 upstream evidence를 root-path 기준으로 먼저 정리해 static overlay 이전 handoff artifact로 쓸 수 있게 만든다.

## Next Candidate

- `static_dependency_overlay`
