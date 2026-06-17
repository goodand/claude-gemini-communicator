---
name: agent-graph-ir
description: >-
  design-planning-orchestrator family의 typed agent-flow IR specialist. Use
  this skill when an agent workflow must be expressed as typed JSON IR with
  nodes, edges, scopes, condition ASTs, and Langfuse-compatible trace records.
  broader multi-concern planning은 design-planning-orchestrator를 사용하라.
---

# Agent Graph IR

복잡한 agent flow를 사람이 읽는 그림이 아니라 typed IR로 먼저 고정하는 skill.
DOT/Mermaid는 파생 출력이고, runtime trace는 같은 ID 체계로 연결한다.

## When to use

- agent workflow를 `nodes + edges + scopes + conditions + trace`로 명시해야 할 때
- nested router / loop 구조를 JSON schema와 validator로 고정할 때
- Graphviz DOT, Mermaid, Langfuse-compatible trace를 같은 source에서 파생할 때
- screenshot / desktop / GUI agent flow를 구조적으로 정의하고 검증할 때

## Workflow

1. `references/entrypoint-details.md`를 읽고 first slice 범위를 고정한다
2. `scripts/agent_graph_ir.py`로 `AgentSpec` / `AgentRun`을 validate한다
3. screenshot flow면 같은 스크립트에서 capture route plan, single observe event, screenshot skill stdout bridge, 또는 partial capture run bridge를 먼저 만든다
4. 필요하면 같은 spec에서 DOT / Mermaid / trace JSON을 파생한다
5. 시각화와 trace가 충돌하면 항상 typed IR를 source of truth로 본다

## Scripts

- `scripts/agent_graph_ir.py` — Pydantic IR, validator, DOT/Mermaid renderer, trace emitter, capture route planner, observe-event CLI, screenshot stdout bridge, partial capture-run bridge
- `scripts/test_agent_graph_ir.py` — first-slice TDD

## References

- `references/entrypoint-details.md` — CLI usage, owned surface, first-slice boundaries
- `references/troubleshooting.md` — 구현/실험 중 발견된 오류 기록
- upstream capture policy reference: `openai/skills` curated `screenshot` skill

## Not owned here

- 실제 screenshot capture substrate 선택/운영 → OpenAI curated `screenshot` skill 또는 native-devtools 계열
- Mermaid authoring/debugging 전략 → `mermaid-authoring-strategy`
- Langfuse score taxonomy와 push workflow → `langfuse-codex-prompt`
- broader contract slicing / checklist derivation → `execution-contract-mapper`
