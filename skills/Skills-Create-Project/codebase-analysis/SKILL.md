---
name: codebase-analysis
description: >-
  Use this skill when analyzing a codebase to prepare slice boundaries,
  dependency evidence, runtime coupling evidence, graph artifacts, and
  subagent orchestration inputs for later parallel execution planning.
---

# codebase-analysis

코드베이스를 분석해서 slice 경계, dependency evidence, runtime coupling, graph artifact, 그리고 subagent orchestration 입력을 준비하는 skill.

## When to use

- 코드베이스를 병렬 처리 전에 구조적으로 분해하고 싶을 때
- slice boundary, dependency evidence, runtime coupling evidence를 먼저 모으고 싶을 때
- subagent 실행 순서를 정하기 전에 codebase graph 입력을 준비하고 싶을 때
- graph artifact와 orchestration prework를 같은 skill 안에서 관리하고 싶을 때

## Read order

1. `references/setup-context-at2026-03-18-22-47.md`
2. `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-18-22-47.md`
3. `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`
4. `references/canonical-graph-artifact-contract-at2026-03-20-21-04.md`
5. `references/agent-flow-at2026-03-20-01-14.md`
6. `references/agent-class-policy-at2026-03-20-01-14.md`
7. `references/skill-usage-details-at2026-03-21-23-25.md`
8. 필요 시 `scripts/analyze_codebase.py <repo_root>`
9. agent 선택 후 `agents/<role>/AGENT.md`
10. 같은 agent의 `references/context-links-*.md`, `references/tool-capability-policy-*.md`, `bridges/<role>-handoff-contract-*.md`
