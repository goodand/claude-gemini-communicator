# MECE Subagent Fan-In For Dependency Graph Analysis

## 원칙
`depsolve-analyzer`를 main으로 두고, dependency graph 해석은 여러 subagent의 결과를 MECE하게 합쳐 수행한다.

## Main skill
- `depsolve-analyzer`
- 소유: extraction, phantom/cycle/diamond detection, machine-readable outputs

## Subagents
### 1. dependency-graph-analyst
- 역할: edge extraction, hub map, region crossing, wrapper-aware graph
- 출력: `edge_list.json`, `graph_summary.json`, `mermaid.mmd`

### 2. dependency-risk-auditor
- 역할: risk taxonomy, boundary audit, phantom/manifest/wrapper/path risk 분류
- 출력: `risk_report.md`, `highest_risk_boundaries`, `followup_checks`

### 3. dependency-slice-planner
- 역할: 병렬 분석 슬라이스 설계
- 출력: `parallel_slices.json`, `fanout_plan.md`

## MECE 분할 축
- `source graph`
- `manifest/package graph`
- `wrapper/path-mutation graph`
- `risk taxonomy`
- `parallel slice plan`

## fan-in 출력
- `summary`
- `artifacts`
- `risks`
- `highest_risk_boundaries`
- `next_checks`
- `parallel_slices`

## 사용 규칙
- graph extraction과 risk interpretation을 한 agent가 동시에 독점하지 않는다
- hotspot map과 verified graph를 같은 등급으로 취급하지 않는다
- read-only 분석 subagent를 우선 사용한다
