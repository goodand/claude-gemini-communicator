---
name: dependency-graph-analyzer
description: >-
  Use this skill when extracting module dependency graphs, import graphs, cycle
  risks, hub modules, package-level dependency problems, and graph-ready
  artifacts for architecture review or subagent parallel analysis. 의존성 그래프,
  import graph, cycle, hub module, 병렬 분석용 graph artifact를 만들 때 사용한다.
---

# Dependency Graph Analyzer

코드베이스 의존성 구조를 추출하고, 그래프 형태로 정규화하고, 병렬 분석 가능한 슬라이스로 내리는 skill.

## When to use

- "의존성 분석", "dependency graph", "import graph", "call graph" 요청
- 순환 의존성, 허브 모듈, 팬텀 의존성, 레이어 침범을 점검할 때
- Mermaid / GraphML / JSON edge-list 형태의 그래프 산출물이 필요할 때
- 코드베이스를 병렬 subagent 분석용 슬라이스로 나눌 때
- 논문/체크리스트와 실제 코드 구조가 맞는지 정합성을 볼 때

## Workflow

1. 입력 범위 고정 — repo root, include/exclude, 언어(Python/JS/혼합)와 출력 목적(분석/시각화/병렬 분할)을 먼저 고정
2. 구조 추출 — `codebase-architecture-mapper` 계열로 module/class/import edges 추출
3. 의존성 검증 — `depsolve-analyzer` 계열로 phantom/cycle/diamond/conflict 확인
4. 그래프 분류 — `graph-structure-classifier` 계열로 Tree/DAG/cyclic 여부와 위험 노드 분류
5. 산출물 정규화 — `graph_summary.json`, `edge_list.json`, `mermaid.mmd`, `risk_report.md`, `parallel_slices.json` 생성
6. 병렬 분석 handoff — subagent에 넘길 slice packet을 생성하고 fan-out 계획을 만든다

## Planned Artifacts

- `graph_summary.json` — 노드/엣지 수, SCC, hub, layer violation 요약
- `edge_list.json` — machine-readable dependency edge list
- `mermaid.mmd` — 발표/검토용 그래프
- `risk_report.md` — cycle, phantom, hub, unstable boundary 보고서
- `parallel_slices.json` — subagent 병렬 분석용 코드 슬라이스 묶음

## References

- `references/dependency-graph-analyzer-reference-2026-03-18-20-50.md`
- `knowledge_bases/dependency-graph-analyzer-knowledge_base-2026-03-18-20-50.md`
- `checklist-forconsistency-evaluation/dependency-graph-analyzer-checklist-2026-03-18-20-50.md`
- `references/Boundary-of-Responsibility-2026-03-18-20-50.md`
- `references/subagent-design-2026-03-18-20-50.md`

## Notes

- v0.1은 직접 코드 수정보다 read-heavy 분석 skill로 시작하는 것이 맞다
- static dependency graph와 runtime call graph는 분리한다
- Python/JS 혼합 repo에서는 package dependency와 source import dependency를 따로 본다
- graph는 목적별로 나눈다: `analysis graph`, `presentation graph`, `subagent slice graph`
