# Codebase-Analysis Orchestration Consumer Spec

- recorded_at: `2026-03-23-13-08`
- purpose: `codebase-analysis` 산출물을 orchestration 계층이 재사용 가능한 방식으로 소비할 때 필요한 입력 보장, 비보장, discovery rule, ownership split을 고정하기 위한 consumer-facing spec 문서
- role: `producer spec 과 task-specific request 사이의 reusable consumer contract`
- scope: `canonical analysis artifact -> packet seed -> dispatch precondition -> runtime handoff`
- layer: `implementation support / orchestration-consumer`

## Source Pages

- [codebase-analysis-spec-at2026-03-23-03-14.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-spec-at2026-03-23-03-14.md)
- [codebase-analysis-development-playbook-at2026-03-23-03-36.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-development-playbook-at2026-03-23-03-36.md)
- [codebase-analysis-orchestration-bridge-at2026-03-23-12-31.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-orchestration-bridge-at2026-03-23-12-31.md)
- [agent-task-packet/SKILL.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/agent-task-packet/SKILL.md)
- [codex-subagent-setup/SKILL.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/SKILL.md)
- [setup-context-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/references/setup-context-at2026-03-18-22-47.md)
- [codex-subagent-setup-knowledge_base-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/knowledge_bases/codex-subagent-setup-knowledge_base-at2026-03-18-22-47.md)
- [codex-subagent-setup-3layer-production-kb-at2026-03-20-17-21.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/knowledge_bases/codex-subagent-setup-3layer-production-kb-at2026-03-20-17-21.md)
- [agent-flow-at2026-03-20-01-14.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/references/agent-flow-at2026-03-20-01-14.md)
- [agent-class-policy-at2026-03-20-01-14.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/references/agent-class-policy-at2026-03-20-01-14.md)
- [codex-worktree-dispatch/SKILL.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-worktree-dispatch/SKILL.md)
- [codex-tmux-orchestrator/SKILL.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-tmux-orchestrator/SKILL.md)

## Consumer Boundary

- `codebase-analysis`는 canonical analysis artifact producer에 머문다.
- orchestration consumer는 producer가 보장한 artifact와 support note를 읽어 packet, dispatch, runtime 단계로 내린다.
- packet schema owner는 `agent-task-packet`이다.
- orchestration-side setup context, read order, progressive context routing, bridge discipline은 `codex-subagent-setup`이 소유한다.
- mutable dispatch state는 `codex-worktree-dispatch`가 소유한다.
- runtime registry, session, heartbeat, launch는 `codex-tmux-orchestrator`가 소유한다.
- 이 문서는 위 ownership split을 덮어쓰지 않고, `codebase-analysis` 산출물을 consumer가 어떻게 읽어야 하는지만 고정한다.

## Guaranteed Consumer Inputs

orchestration consumer는 아래 입력을 producer guarantee로 읽을 수 있다.

- canonical source-of-truth triple:
  - `normalized_graph.json`
  - `nodes.jsonl`
  - `edges.jsonl`
- required provenance sidecar:
  - `graph_meta.json`
- optional sidecar evidence artifact family
- optional run support artifact:
  - `runs/<task-id>/plan.md`
  - `runs/<task-id>/doc.md`
  - `runs/<task-id>/report.md`
  - `runs/<task-id>/log.json`

## Non-Guaranteed Inputs

consumer는 아래를 producer guarantee로 가정하지 않는다.

- sidecar evidence artifact path가 `graph_meta.json.artifact_paths` 안에 들어 있다고 가정하지 않는다.
- packet 본문 전체가 `codebase-analysis`에서 자동 생성된다고 가정하지 않는다.
- dispatch state, runtime registry, tmux session 정보가 `codebase-analysis` artifact에 포함된다고 가정하지 않는다.
- optional slice stage artifact family는 이번 범위에서 가정하지 않는다.
- `merged_graph`가 analysis/orchestration graph 병합을 뜻한다고 가정하지 않는다.

## Canonical Triple And Provenance Sidecar

- canonical source of truth는 계속 `normalized_graph.json + nodes.jsonl + edges.jsonl`이다.
- `graph_meta.json`은 source of truth triple을 대체하지 않는 required provenance sidecar다.
- orchestration consumer는 launch-side provenance 확인이 필요할 때 `graph_meta.json`을 읽는다.
- consumer가 `graph_meta.json`을 읽는 이유는 provenance baseline과 artifact location을 확인하기 위해서지, canonical graph 내용을 대체하기 위해서가 아니다.

## Artifact Discovery Contract

- consumer launch 입력의 baseline은 canonical triple + `graph_meta.json`이다.
- `graph_meta.json.artifact_paths`는 canonical triple path만 baseline으로 보장한다.
- sidecar evidence artifact가 존재하면 caller는 그 경로를 아래 중 하나로 별도 명시해야 한다.
  - `runs/<task-id>/doc.md`
  - `runs/<task-id>/report.md`
  - packet `context_files`
- 위 명시가 없으면 consumer는 sidecar-derived `risk_boundaries` 입력이 없는 것으로 해석한다.
- `runs/<task-id>/` 아래 문서는 canonical input이 아니라 launch support artifact다.

## graph_meta Consumer Contract

- orchestration consumer는 `graph_meta.json`에서 아래 역할만 기대한다.
  - producer run provenance 확인
  - artifact root/location 확인
  - canonical triple path 확인
  - `graph_kind` 확인
- baseline provenance field는 `trace_id + artifact_location`이다.
- `graph_meta.json` required top-level field set은 producer spec을 따른다.
- consumer는 `graph_meta.json` 단독으로 graph structure를 해석하지 않는다.

## Packet Seed Mapping

producer artifact에서 orchestration packet seed로 내려가는 최소 mapping은 아래다.

- `tree_snapshot`
  - source: coarse survey summary 또는 top-level structure snapshot
- `graph_summary`
  - source: canonical graph artifact summary
- `risk_boundaries`
  - source: explicit sidecar evidence, anomaly evidence, protected-region note
- `size_thresholds`
  - source: summary count 또는 bounded sizing rule
- `entrypoint_hints`
  - source: path anchor 또는 path-anchored symbol locator hint
- `artifact_destination`
  - source: `runs/<task-id>/` 또는 bounded artifact root

packet required field set 자체는 `agent-task-packet` contract를 따르며, 이 문서는 seed mapping만 다룬다.

## Launch Preconditions

orchestration consumer가 packet -> dispatch -> runtime 단계로 내려가기 전에 아래 조건이 닫혀 있어야 한다.

- canonical triple이 존재한다.
- `graph_meta.json`이 존재하고 provenance baseline을 포함한다.
- bounded packet의 `goal`, `allowed_paths`, `context_files`, `constraints`, `done_definition`, `required_checks`, `deliverables`가 고정돼 있다.
- target workspace root가 playbook의 bounded workspace/worktree rule을 만족한다.
- 사용할 agent package 또는 runtime class가 선택돼 있다.
- progressive context injection에 필요한 `setup context -> role AGENT -> context links` 읽기 순서가 고정돼 있다.
- runtime launch는 ready dispatch 이후에만 시작한다.

## Ownership Split For Reuse

- producer artifact contract owner: `codebase-analysis spec`
- packet schema owner: `agent-task-packet`
- orchestration-side setup / read-order / bridge owner: `codex-subagent-setup`
- dispatch state owner: `codex-worktree-dispatch`
- runtime launch owner: `codex-tmux-orchestrator`

이 문서는 ownership을 새로 정의하지 않고 위 split을 consumer 해석 규칙으로만 고정한다.

## Task-Specific Seeds

아래 문서는 reusable source-of-truth가 아니라 task-specific seed 또는 example로만 사용한다.

- [codebase-analysis-implementation-request-at2026-03-23-10-49.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-implementation-request-at2026-03-23-10-49.md)
- [codebase-analysis-semantic-review-request-at2026-03-23-11-27.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-semantic-review-request-at2026-03-23-11-27.md)

consumer implementation은 위 seed를 복사해 쓸 수 있지만, 이 문서의 canonical source pages를 대체하지 않는다.

## Non-Goals

- `codebase-analysis` script 안에 dispatch/runtime orchestration을 넣지 않는다.
- packet schema를 이 문서에서 다시 정의하지 않는다.
- sidecar discovery가 없을 때 임의 heuristic으로 risk boundary를 생성하지 않는다.
- analysis/orchestration graph를 `merged_graph` 의미에 섞지 않는다.

## One-Line Summary

- `codebase-analysis`는 producer, orchestration consumer는 artifact reader이며, packet/dispatch/runtime ownership은 인접 orchestration skill이 소유한다.
