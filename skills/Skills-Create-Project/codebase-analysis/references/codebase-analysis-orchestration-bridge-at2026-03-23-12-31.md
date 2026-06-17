# Codebase-Analysis Orchestration Bridge

- recorded_at: `2026-03-23-12-31`
- purpose: `codebase-analysis`의 분석 산출물을 worker packet, worktree dispatch, tmux runtime으로 연결하는 bridge contract를 implementation support 층에서 고정하기 위한 문서
- scope: `analysis artifact -> task packet -> worktree dispatch -> tmux runtime`
- layer: `implementation support / orchestration-adjacent`

## Source Pages

- [codebase-analysis-spec-at2026-03-23-03-14.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-spec-at2026-03-23-03-14.md)
- [codebase-analysis-development-playbook-at2026-03-23-03-36.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-development-playbook-at2026-03-23-03-36.md)
- [codebase-analysis-implementation-request-at2026-03-23-10-49.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-implementation-request-at2026-03-23-10-49.md)
- [agent-task-packet/SKILL.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/agent-task-packet/SKILL.md)
- [codex-worktree-dispatch/SKILL.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-worktree-dispatch/SKILL.md)
- [codex-tmux-orchestrator/SKILL.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-tmux-orchestrator/SKILL.md)
- [Boundary-of-Responsibility-2026-03-15-00-55.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/agent-task-packet/references/Boundary-of-Responsibility-2026-03-15-00-55.md)

## Bridge Boundary

- `codebase-analysis`는 canonical analysis artifact producer다.
- task packet은 불변 작업 계약서다.
- worktree dispatch는 mutable 배치/실행 준비 상태다.
- tmux orchestrator는 ready dispatch를 실제 실행으로 연결하는 runtime layer다.
- 이 bridge 문서는 위 네 층을 연결하는 mapping만 다룬다.

## Artifact Inputs

bridge가 읽는 입력 artifact는 아래 family로 고정한다.

- canonical graph artifact:
  - `normalized_graph.json`
  - `nodes.jsonl`
  - `edges.jsonl`
- provenance sidecar:
  - `graph_meta.json`
- optional sidecar evidence artifact family
- run artifact:
  - `runs/<task-id>/plan.md`
  - `runs/<task-id>/doc.md`
  - `runs/<task-id>/report.md`
  - `runs/<task-id>/log.json`

## Sidecar Evidence Discovery

- provenance baseline으로서 `graph_meta.json.artifact_paths`는 canonical artifact triple만 보장한다.
- sidecar evidence artifact path는 baseline `graph_meta.json.artifact_paths`에 포함된다고 가정하지 않는다.
- sidecar evidence artifact가 생성되는 경우, bridge caller는 그 경로를 아래 중 하나로 명시해야 한다.
  - `runs/<task-id>/doc.md`
  - `runs/<task-id>/report.md`
  - packet `context_files`
- 위 기록이 없으면 bridge는 sidecar-derived `risk_boundaries` 입력이 없는 것으로 해석하고 canonical graph artifact와 graph summary만 사용한다.

## Launch Gate

sub-agent fan-out 또는 worker launch는 아래 조건이 모두 충족될 때만 시작한다.

- canonical artifact triple이 생성되어 있다.
- `graph_meta.json`이 존재하고 provenance baseline field를 포함한다.
- 현재 task에 대응하는 implementation request 또는 semantic review request가 존재한다.
- `allowed_paths`, `done_definition`, `required_checks`, `deliverables`가 packet 수준에서 닫혀 있다.
- target workspace root가 playbook의 worktree 규칙 또는 bounded workspace 규칙을 만족한다.

## Packet Mapping

`codebase-analysis` 산출물에서 packet으로 내려가는 필드는 아래처럼 맵핑한다.

- `tree_snapshot`
  - source: coarse survey 또는 top-level structure snapshot
- `graph_summary`
  - source: canonical graph artifact summary
- `risk_boundaries`
  - source: sidecar evidence, anomaly evidence, protected region 메모
- `size_thresholds`
  - source: coarse survey summary 또는 bounded task sizing rule
- `entrypoint_hints`
  - source: path anchor 또는 path-anchored symbol locator hint
- `artifact_destination`
  - source: `runs/<task-id>/` 또는 bounded artifact root

packet 본문에 직접 내려야 하는 고정 필드는 아래다.

- `goal`
- `allowed_paths`
- `context_files`
- `constraints`
- `done_definition`
- `required_checks`
- `deliverables`

선택 필드는 아래다.

- `forbidden_paths`
- `depends_on`
- `parallel_group`
- `non_goals`
- `trace_id`

## Dispatch Mapping

packet이 dispatch로 내려갈 때 ownership은 아래처럼 분리한다.

- packet owner:
  - `goal`
  - `done_definition`
  - `allowed_paths`
  - `forbidden_paths`
  - `depends_on`
  - `parallel_group`
- dispatch owner:
  - `branch`
  - `worktree`
  - `locked_paths`
  - `assigned_worker`
  - `status`
  - `merge_readiness`

dispatch는 아래 규칙을 유지한다.

- `locked_paths ⊆ allowed_paths`
- 하나의 dispatch는 하나의 packet만 소비한다.
- worktree path는 repo root `.worktrees/` 아래 bounded path만 사용한다.

## Runtime Mapping

ready dispatch 이후의 runtime 연결은 아래처럼 고정한다.

- dispatch status=`ready`
- tmux orchestrator가 dispatch와 packet을 입력으로 launch
- tmux orchestrator는 runtime registry, session, heartbeat, stdout/stderr path를 관리
- packet 원문은 runtime에서 수정하지 않는다.

## Worktree Allocation Rule

- code-writing workspace root는 repo root working copy 또는 `.worktrees/` 아래 bounded worktree root 중 하나다.
- 병렬 worker/sub-agent 작업은 `.worktrees/codebase-analysis-*` 하위 worktree를 우선 사용한다.
- 동일 task에서 main working copy와 worktree를 동시에 수정 대상으로 잡지 않는다.
- run artifact는 `scripts/`가 아니라 `runs/<task-id>/` 아래에만 남긴다.

## Trigger Guidance

이 bridge는 언제 orchestration으로 내려가야 하는지에 대한 최소 기준만 가진다.

- 분석 산출물만 만들면 되는 task면 `codebase-analysis`에서 멈춘다.
- bounded code 수정이 필요하고 `allowed_paths`가 닫힐 때 packet 단계로 내려간다.
- 병렬 작업 또는 worker 분리가 필요하면 dispatch 단계로 내려간다.
- dispatch status가 `ready`가 되면 tmux orchestrator 단계로 내려간다.

## Non-Goals

- `codebase-analysis`가 직접 worker를 실행하는 구조를 채택하지 않는다.
- `codebase-analysis` script 안에 dispatch/runtime 상태 관리를 넣지 않는다.
- orchestration layer가 canonical graph artifact를 source-of-truth로 대체하지 않는다.
- analysis/orchestration graph를 `merged_graph` 의미에 섞지 않는다.

## One-Line Summary

- `codebase-analysis`는 artifact producer에 머물고, worker packet/dispatch/runtime은 별도 orchestration layer가 소비한다.
