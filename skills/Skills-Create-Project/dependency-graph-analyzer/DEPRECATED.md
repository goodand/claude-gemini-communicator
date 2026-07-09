# dependency-graph-analyzer Deprecated

이 디렉토리는 active skill에서 제외됐다.

## 이유
- 독립 skill로 두기에는 범위가 넓고 추상적이었다.
- 실제 메인 책임은 `depsolve-analyzer`가 더 자연스럽게 가진다.
- dependency graph 추출은 `depsolve-analyzer`의 하위 계약 `analyze_dependency_graph`로 내리는 것이 더 맞다.
- risk taxonomy와 slice refinement는 top-level skill이 아니라 subagent 역할로 두는 편이 책임 경계가 명확하다.

## Replacement
- Main skill: `depsolve-analyzer`
- Sub contract/tool: `analyze_dependency_graph`
- Optional subagents: `dependency-graph-analyst`, `dependency-risk-auditor`, `dependency-slice-planner`

## Archived snapshot
- `legacy/2026-03-18-21-22-pre-depsolve-main/`
