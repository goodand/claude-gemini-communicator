---
name: codebase-analysis
description: >-
  Codebase Evidence family의 workflow owner. Use this skill when multi-concern
  codebase evidence such as dependency, class, runtime, and graph structure
  must be gathered for later modeling, export, or review. progress-only는
  codebase-progress, GitHub-only structured research는 github-deep-research를
  사용하라.
---

# codebase-analysis

코드베이스의 구조, 런타임, 의존성 증거와 graph artifact를 분석하는 skill.

## When to use

- 코드베이스의 top-level 구조와 active tree를 먼저 파악하고 싶을 때
- dependency, class structure, runtime overlay를 graph evidence 중심으로 모으고 싶을 때
- normalized graph artifact와 export 전제를 준비하고 싶을 때
- graph core에 남길 증거와 sidecar evidence file로 뺄 저연결 정보를 구분하고 싶을 때
- 분석 결과를 handoff-ready evidence package로 묶고 싶을 때

## Do not use

- progress scanning(TODO/git/drift)만 하면 될 때 → `codebase-progress`
- GitHub structured research만 하면 될 때 → `github-deep-research`

## Family Roles

- owner:
  - `codebase-analysis`
- direct-call specialists:
  - `codebase-progress`
  - `github-deep-research`

## Workflow

1. **active tree 파악** — top-level 구조, 핵심 디렉토리, 진입점 확인
2. **evidence layer 수집** — dependency, class structure, runtime overlay를 graph evidence로 수집
3. **graph artifact 정규화** — normalized graph core와 sidecar evidence file 분리
4. **handoff-ready evidence package** — 수집된 evidence를 downstream consumer가 바로 읽을 수 있는 package로 묶기 (KB/checklist 생산 자체는 `workspace-artifact-production-process`)

## Read order

1. `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`
2. `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`
3. `references/canonical-graph-artifact-contract-at2026-03-20-21-04.md`
4. `references/normalized-graph-json-sample-schema-at2026-03-20-21-51.md`
5. `references/skill-usage-details-at2026-03-21-23-25.md`
6. 필요 시 `scripts/analyze_codebase.py <repo_root>`

## Notes

- `graph evidence`가 이 skill의 핵심 키워드이고, dependency/class/runtime overlay는 그 하위 evidence layer로 본다.
- `slice`는 `dependency-slice-planner`, `handoff`와 `fan-in`은 `codex-subagent-setup` 소관으로 두고 이 skill은 analysis 본체만 다룬다.
- graph core에는 연결성이 높은 구조 증거를 두고, 저연결 risk note·ownership 예외·weak signal은 sidecar evidence file로 분리한다.
- 정합성 평가용 checklist는 skill 의도와 canonical KB의 교집합만 평가하도록 만든다.
- gate-sequence seed와 handoff seed는 supporting appendix로 두고, canonical base KB와 graph representation KB를 먼저 읽는다.
- 분석 중 발생한 smoke/실행 예외는 `references/troubleshooting.md`와 관련 evidence 문서에 누적한다.
