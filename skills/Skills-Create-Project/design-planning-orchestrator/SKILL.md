---
name: design-planning-orchestrator
description: >-
  Use this skill when multi-concern design and planning must coordinate
  semantic slices, execution contracts, reverse concept lifting, dependency-safe
  slice boundaries, and typed agent-flow structure together. semantic-only는
  semantic-slice-mapper, contract-only는 execution-contract-mapper, reverse-lift는
  contract-to-concept-mapper, dependency slicing은 dependency-slice-planner,
  typed flow IR은 agent-graph-ir를 사용하라.
---

# Design Planning Orchestrator

설계/계획 band의 workflow owner.

## When to use

- concept, contract, slice, flow design이 함께 얽힌 multi-concern planning이 필요할 때
- 어떤 planning specialist를 먼저 써야 할지 불확실할 때
- 실행 전에 boundary, relation, contract surface를 한 번에 정리해야 할 때

## Do not use

- semantic relation만 정리하면 될 때
- execution contract만 만들면 될 때
- execution artifact를 concept로 되올리기만 하면 될 때
- dependency-safe slice만 계획하면 될 때
- agent flow를 typed IR로 고정하기만 하면 될 때

## Family Roles

- owner:
  - `design-planning-orchestrator`
- direct-call specialists:
  - `semantic-slice-mapper`
  - `execution-contract-mapper`
  - `contract-to-concept-mapper`
  - `dependency-slice-planner`
  - `agent-graph-ir`

## Workflow

1. 현재 planning concern이 semantic, contract, dependency, flow 중 어디에 걸치는지 분류한다.
2. narrow specialist direct call로 충분한지 먼저 판단한다.
3. multi-concern이면 owner가 planning order와 handoff shape를 정한다.
4. 필요한 downstream artifact를 concept-space / execution-space로 나눠 넘긴다.

## References

- owner band taxonomy는 [../skill-creation-process/references/owner-task-bands-at2026-04-02.md](../skill-creation-process/references/owner-task-bands-at2026-04-02.md)
- troubleshooting note는 [references/troubleshooting.md](references/troubleshooting.md)
