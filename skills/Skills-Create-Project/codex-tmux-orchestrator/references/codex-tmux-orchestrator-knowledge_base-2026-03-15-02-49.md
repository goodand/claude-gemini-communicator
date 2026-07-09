# research URL Knowledge Base
- ver: `v0.1.0`
- generated_at: `2026-03-15`
- updated_at: `2026-03-15` (v0.1.0: codex-tmux-orchestrator GitHub/runtime reference 장문 인덱스 추가)
- format: `- [한 줄 설명](URL)`
- generation_method: `manual curation based on GitHub repositories, official tmux documentation, and internal skill documents for tmux-based Codex orchestration design`
- total_urls: `14`
- paper_like_urls: `0`
- other_urls: `14`

## Document Map

| 문서 | 역할 |
|------|------|
| [../../tmux-controller/SKILL.md](../../tmux-controller/SKILL.md) | tmux primitive 제어를 담당하는 하위 Skill |
| [../../worktree-parallel/SKILL.md](../../worktree-parallel/SKILL.md) | worktree fan-out/fan-in 및 배치 규칙을 담당하는 하위 Skill |
| [codex-tmux-orchestrator-reference-2026-03-15-03-12.md](./codex-tmux-orchestrator-reference-2026-03-15-03-12.md) | 장문 설계 reference · 역할/경계/상태 머신/registry 방향성 |
| `codex-tmux-orchestrator-knowledge_base-2026-03-15-02-49.md` (이 파일) | 외부 GitHub/공식 URL 14개 인덱스와 구현 포인트 매핑 |
| [codex-tmux-orchestrator-checklist-2026-03-15-02-51.md](./codex-tmux-orchestrator-checklist-2026-03-15-02-51.md) | 구현 정합성 평가 체크리스트 |

## Table of Contents
- [Paper-like URLs](#paper-like-urls)
- [Other research References URLs](#other-research-references-urls)
- [How To Use This Knowledge Base](#how-to-use-this-knowledge-base)
- [Runtime-Orchestration Dimensions](#runtime-orchestration-dimensions)
- [Coverage Matrix](#coverage-matrix)
- [Direct Mapping To Planned Skill Artifacts](#direct-mapping-to-planned-skill-artifacts)
- [Recommended Reading Order](#recommended-reading-order)
- [Common Failure Modes This KB Is Trying To Prevent](#common-failure-modes-this-kb-is-trying-to-prevent)
- [Suggested Minimal Reference Stack For v01](#suggested-minimal-reference-stack-for-v01)
- [Suggested Next Files To Create In references](#suggested-next-files-to-create-in-references)
- [Suggested Next Scripts To Create In scripts](#suggested-next-scripts-to-create-in-scripts)

## Paper-like URLs

- 없음

## Other research References URLs

- [Par는 label 중심으로 branch, worktree, tmux session을 함께 관리하는 parallel worktree & session manager로, dispatch-to-session deterministic mapping의 가장 직접적인 reference다](https://github.com/coplane/par)
  - sources: `github_readme_manual_review_2026-03-15` + `local_skill_alignment_review_2026-03-15`
  - agent: `A00`
  - taxonomy: [[worktree-session-manager, label-mapping, deterministic-naming]] · Axis O
  - role_in_skill: `codex-tmux-orchestrator`가 dispatch/label/session/worktree를 일관된 이름 체계로 연결할 때 참고할 1순위 UX/CLI reference.
  - key_idea: launch 단위를 "터미널 세션"이 아니라 "이름 있는 병렬 개발 context"로 취급하고, branch/worktree/tmux를 하나의 operator-facing surface로 묶는다.
  - adoption_targets:
    - `dispatch_id -> session_name` 규칙
    - `status/list/open/send`류 operator UX
    - bootstrap command chain
    - session/workspace naming convention
  - cautions:
    - `par`는 범용 session/worktree manager이며, 우리 구조처럼 `task-packet`과 `dispatch`를 canonical source로 강하게 두지는 않는다.
    - 따라서 `session-first`가 아니라 `dispatch-first`로 재해석해야 한다.
  - pseudocode_3lines:
    - 1) 주어진 task label 또는 dispatch_id로 branch/worktree/session 이름을 deterministic하게 생성한다.
    - 2) 해당 이름 체계로 isolated worktree와 tmux session을 결합된 개발 context로 취급한다.
    - 3) launch 후에는 list/open/send/status 명령으로 operator가 모든 context를 다시 찾아갈 수 있게 한다.

- [CCManager는 Claude Code, Gemini CLI, Codex CLI 등을 git worktree와 project 단위로 관리하며 state detection, hooks, multi-project 운영을 지원하는 session manager다](https://github.com/kbwo/ccmanager)
  - sources: `github_readme_manual_review_2026-03-15` + `runtime_state_design_notes_2026-03-15`
  - agent: `A00`
  - taxonomy: [[session-manager, state-detection, hooks, multi-project]] · Axis O
  - role_in_skill: session이 단순히 "살아 있음"인지, 실제로 `busy / waiting / idle` 상태인지를 분리해서 보게 만드는 runtime-state reference.
  - key_idea: 세션 실행과 세션 상태 감지를 분리하고, 상태 변화마다 hook와 자동화를 붙여 실운영 가능한 session manager를 만든다.
  - adoption_targets:
    - runtime state machine (`launching/running/waiting_input/stale/failed`)
    - state change hook 설계
    - command preset / fallback preset
    - multi-project 확장 여지
  - cautions:
    - CCManager는 tmux 없는 경로도 전제로 하고 UI 중심성이 있다.
    - 우리는 tmux 기반 Codex runtime에 더 좁고 강하게 결합된다.
  - pseudocode_3lines:
    - 1) agent session을 worktree와 project identity에 묶어서 registry에 기록한다.
    - 2) output/프롬프트 패턴을 통해 session 상태를 busy, waiting, idle 등으로 감지한다.
    - 3) 상태 변화마다 hook 또는 후속 자동화를 실행해 운영자의 개입 비용을 줄인다.

- [Emdash는 isolated Git worktree에서 여러 coding agent를 병렬 실행하는 orchestration layer로, parallel fan-out과 review fan-in의 상위 구조를 보여준다](https://github.com/generalaction/emdash)
  - sources: `github_readme_manual_review_2026-03-15` + `orchestration_scope_review_2026-03-15`
  - agent: `A00`
  - taxonomy: [[agent-orchestration, parallel-worktrees, review-fanin, provider-agnostic]] · Axis O
  - role_in_skill: `codex-tmux-orchestrator`가 단순 launch wrapper가 아니라 orchestration component라는 관점을 제공하는 상위 reference.
  - key_idea: task/ticket를 여러 agent에 병렬 fan-out하고, isolated worktree에서 실행한 뒤, review와 reconciliation 단계를 거쳐 다시 fan-in한다.
  - adoption_targets:
    - isolated worktree default 원칙
    - orchestration vocabulary
    - review 이전 단계 registry 보존
    - provider-agnostic 확장성
  - cautions:
    - Emdash는 product-level scope가 크다.
    - 초기 skill 구현은 `Codex + tmux + dispatch runtime`에 한정해야 한다.
  - pseudocode_3lines:
    - 1) 상위 작업을 여러 isolated agent execution unit으로 분해한다.
    - 2) 각 unit을 별도 worktree에서 병렬 실행하고 상태를 추적한다.
    - 3) 실행 결과를 다시 review/reconciliation 단계에서 수렴시킨다.

- [GWQ는 fuzzy finder 기반 git worktree manager이지만 status watch, tmux session, task queue까지 포함하며 병렬 AI coding workflow의 watchable 운영성을 보여준다](https://github.com/d-kuro/gwq)
  - sources: `github_readme_manual_review_2026-03-15` + `status_watch_review_2026-03-15`
  - agent: `A00`
  - taxonomy: [[worktree-manager, status-watch, task-queue, tmux-integration]] · Axis O
  - role_in_skill: canonical registry와 별개로 사람이 즉시 읽을 수 있는 `status --watch`류 출력이 왜 필요한지 보여주는 운영 reference.
  - key_idea: 여러 worktree와 장기 실행 프로세스를 단순 파일 목록이 아니라 살아 있는 운영 대시보드처럼 보여 줌으로써 병렬 작업의 가시성을 높인다.
  - adoption_targets:
    - human-readable status output
    - watch-friendly summary
    - global discovery 보조 사고
    - 장기 작업 상태 관찰 UX
  - cautions:
    - GWQ는 registry-less filesystem scanning 성향이 있다.
    - 우리는 `tmux ls`와 스캔만으로 truth를 재구성하지 않고, file registry를 canonical source로 유지해야 한다.
  - pseudocode_3lines:
    - 1) 여러 worktree와 장기 실행 작업을 전역 또는 repo 범위에서 발견한다.
    - 2) 상태를 watch 모드로 요약해 operator가 한눈에 진행 상황을 보게 한다.
    - 3) 필요할 때 특정 context로 빠르게 이동하거나 실행 세션을 제어한다.

- [Agentree는 AI coding agent용 isolated worktree를 만들면서 env 복사, dependency 설치, 설정 복사까지 자동화해 runnable workspace bootstrap reference를 제공한다](https://github.com/AryaLabsHQ/agentree)
  - sources: `github_readme_manual_review_2026-03-15` + `bootstrap_requirements_review_2026-03-15`
  - agent: `A00`
  - taxonomy: [[bootstrap, env-copy, dependency-install, ai-worktree]] · Axis O
  - role_in_skill: launch 전에 단순히 worktree가 있는지보다, 실제로 Codex가 실행 가능한 상태인지 확인해야 한다는 점을 뒷받침하는 reference.
  - key_idea: isolated worktree를 만드는 것만으로는 충분하지 않고, env/config/dependency를 복제해 실제 agent가 바로 작업 가능한 상태까지 끌어올려야 한다.
  - adoption_targets:
    - preflight runnable check
    - optional bootstrap hook
    - `.env` / config presence 검증
    - dependency preflight or lazy install policy
  - cautions:
    - orchestrator가 bootstrap 전체를 소유하면 scope가 커진다.
    - v0.1에서는 hook contract만 잡고, 실제 bootstrap은 optional step으로 두는 편이 낫다.
  - pseudocode_3lines:
    - 1) branch와 worktree를 만든 뒤 실행에 필요한 env/config/dependency를 복사 또는 설치한다.
    - 2) agent가 바로 코딩을 시작할 수 있는 runnable 상태인지 사전 검증한다.
    - 3) 준비가 끝난 worktree에서만 장기 실행 agent session을 launch 한다.

- [Kosho는 `.kosho/` 아래 repo-local registry와 hooks를 두고 worktree를 관리해 repo-local metadata 구조와 prune/cleanup 설계의 좋은 reference가 된다](https://github.com/carlsverre/kosho)
  - sources: `github_readme_manual_review_2026-03-15` + `registry_layout_review_2026-03-15`
  - agent: `A00`
  - taxonomy: [[repo-local-registry, hooks, prune, cleanup]] · Axis O
  - role_in_skill: `.codex/` 아래 runtime/session/log/heartbeat registry를 두는 설계 방향을 강화하는 reference.
  - key_idea: repo 내부에 숨김 관리 디렉토리를 두고 worktree/hook/prune를 일관되게 관리하면, local-first concurrent development 운영이 단순해진다.
  - adoption_targets:
    - `.codex/` 디렉토리 구조
    - create/run/cleanup hook idea
    - prune / repair / orphan cleanup
    - repo-local canonical state
  - cautions:
    - Kosho는 worktree manager다.
    - 우리 skill은 runtime orchestration이므로, worktree canonical ownership은 dispatch 쪽에 두고 runtime metadata만 `.codex/`에 둬야 한다.
  - pseudocode_3lines:
    - 1) repo root 아래 숨김 metadata 디렉토리에 worktree 관련 상태와 hooks를 둔다.
    - 2) 작업 생성과 실행 시점에 환경 초기화 또는 후속 자동화를 수행한다.
    - 3) prune/cleanup으로 dangling worktree와 metadata를 정리한다.

- [Codex CLI Farm은 tmux에서 여러 Codex CLI 인스턴스를 장기 운영하고 pane별 로그와 unified monitoring을 제공하는 Codex-specific runtime reference다](https://github.com/waskosky/codex-cli-farm)
  - sources: `github_readme_manual_review_2026-03-15` + `codex_runtime_specific_review_2026-03-15`
  - agent: `A00`
  - taxonomy: [[codex-specific, tmux-farm, long-lived-sessions, unified-monitoring]] · Axis O
  - role_in_skill: `Codex + tmux + monitoring` 문제를 직접 다루는 가장 가까운 외부 reference로, attempt별 로그와 장기 세션 관리 관점이 특히 유용하다.
  - key_idea: Codex CLI를 일회성 실행이 아니라 farm처럼 장기 운영 대상으로 보고, pane별 로그와 중앙 모니터링, 복구 가능한 세션 구조를 제공한다.
  - adoption_targets:
    - attempt별 log rotation
    - unified monitoring 개념
    - snapshot/restore thinking
    - long-lived Codex session handling
  - cautions:
    - farm 관점은 session-first다.
    - 우리는 dispatch-first로 재해석해야 하며, canonical identity는 pane이 아니라 `dispatch_id`여야 한다.
  - pseudocode_3lines:
    - 1) 여러 Codex CLI 인스턴스를 장기 세션으로 분리해 실행한다.
    - 2) 각 실행 단위의 output을 개별 로그로 저장하면서 중앙에서 모니터링한다.
    - 3) 필요 시 세션을 복구하거나 다시 attach 할 수 있게 상태를 보존한다.

- [Commander는 여러 CLI coding agent를 local worktree 기반으로 orchestration하는 desktop control plane으로, project-local workspace와 session 추적 구조를 보여준다](https://github.com/autohandai/commander)
  - sources: `github_readme_manual_review_2026-03-15` + `control_plane_review_2026-03-15`
  - agent: `A00`
  - taxonomy: [[desktop-control-plane, local-first, workspaces, project-lifecycle]] · Axis O
  - role_in_skill: 현재는 CLI skill이지만, 나중에 중앙 관제형 `session-monitor`로 갈 때 필요한 control-plane 사고를 제공하는 reference.
  - key_idea: project-local workspace, session persistence, provider settings, diff/history view를 한 control plane 안에서 통합하면 다중 agent 운영이 한층 관리 가능해진다.
  - adoption_targets:
    - project-local hidden workspace directory 관념
    - agent enablement / provider preset
    - session metadata persistence
    - 상태 요약 UI를 위한 backend schema
  - cautions:
    - desktop UI scope는 v0.1에 과하다.
    - 현재 skill은 headless/CLI-friendly backend contract만 가져와야 한다.
  - pseudocode_3lines:
    - 1) project root를 기준으로 agent workspace와 provider 설정을 로컬에 저장한다.
    - 2) 각 workspace에서 실행되는 여러 CLI agent의 상태와 history를 중앙에서 추적한다.
    - 3) 필요할 때 history, diff, session control 정보를 한곳에서 재구성한다.

- [cmux는 Claude Code, Codex CLI, Gemini CLI 등 여러 coding agent CLI를 병렬로 돌리는 manager로, parallel agent runtime과 isolated workspace UX reference를 제공한다](https://github.com/manaflow-ai/cmux)
  - sources: `github_readme_manual_review_2026-03-15` + `multi-agent-runtime_review_2026-03-15`
  - agent: `A00`
  - taxonomy: [[agent-multiplexer, isolated-workspaces, parallel-runtime, codex-compatible]] · Axis O
  - role_in_skill: 단일 Codex 런타임을 넘어서 future multi-agent launcher로 확장될 때 필요한 공통 runtime abstraction reference.
  - key_idea: 서로 다른 coding agent CLI를 동일한 병렬 execution surface에 올리되, 각 실행은 isolated workspace 안에서 이뤄져 검토 가능성과 안전성을 유지한다.
  - adoption_targets:
    - launch abstraction layer
    - isolated workspace requirement
    - model/provider agnostic future hooks
    - restart/resume UX 방향성
  - cautions:
    - cmux는 product scale이 크고 UI/desktop 요소가 있다.
    - v0.1 skill은 Codex-specific runtime contract를 먼저 고정하는 편이 낫다.
  - pseudocode_3lines:
    - 1) 각 task를 isolated workspace 위의 병렬 agent run으로 변환한다.
    - 2) 여러 coding CLI를 동일한 orchestration surface에서 launch/monitor 한다.
    - 3) 결과를 검토 가능한 상태로 유지하며 필요 시 resume 또는 restart 한다.

- [coder/mux는 isolated parallel agentic development를 위한 desktop app으로, git divergence와 long-running background agent resume 문제를 잘 다룬다](https://github.com/coder/cmux)
  - sources: `github_readme_manual_review_2026-03-15` + `background_resume_review_2026-03-15`
  - agent: `A00`
  - taxonomy: [[desktop-orchestration, git-divergence, background-agents, resume]] · Axis O
  - role_in_skill: long-running background agent가 restart 이후에도 상태 continuity를 가져야 한다는 점, 그리고 git divergence visibility가 중요하다는 점을 보여주는 reference.
  - key_idea: 병렬 에이전트 개발은 단순 spawn이 아니라, 장시간 백그라운드 작업의 continuity와 git divergence 인식까지 포함해야 실제 생산성으로 이어진다.
  - adoption_targets:
    - background run resume 사고
    - session continuity / intermittent recovery
    - git divergence summary future field
  - cautions:
    - desktop app 수준의 기능을 초기 스킬에 그대로 흡수하면 안 된다.
    - 현재는 registry schema에 divergence/continuity 확장 필드만 예약하는 정도가 적절하다.
  - pseudocode_3lines:
    - 1) 여러 장시간 agent run을 isolated workspace에서 병렬 유지한다.
    - 2) 중간 연결 끊김이나 재시작 이후에도 run continuity를 복구한다.
    - 3) 각 workspace의 git divergence와 상태를 중앙에서 다시 볼 수 있게 만든다.

- [Phantom은 central worktree path와 tmux/editor/AI launch를 직관적 CLI로 연결하는 lightweight parallel-development tool이다](https://github.com/aku11i/phantom)
  - sources: `github_readme_manual_review_2026-03-15` + `lightweight_cli_surface_review_2026-03-15`
  - agent: `A00`
  - taxonomy: [[lightweight-launch, central-worktree-path, ai-launch, tmux-integration]] · Axis O
  - role_in_skill: v0.1 command surface를 너무 무겁게 만들지 않고, 기억하기 쉬운 naming과 중앙 경로 관리로 단순하게 시작해야 함을 보여주는 reference.
  - key_idea: 복잡한 parallel workflow도 operator가 외울 수 있는 작은 명령 집합과 강한 convention으로 감싸면 일상적으로 사용할 수 있다.
  - adoption_targets:
    - simple CLI verbs (`launch`, `status`, `restart`, `cleanup`)
    - central worktree path notion
    - AI launch helper concept
    - 기억하기 쉬운 naming
  - cautions:
    - Phantom은 worktree lifecycle 비중이 크다.
    - 우리 skill은 runtime lifecycle 중심이어야 하므로, worktree create 기능을 직접 소유하면 scope가 흐려진다.
  - pseudocode_3lines:
    - 1) branch/worktree를 사람이 기억하기 쉬운 이름 체계로 관리한다.
    - 2) 특정 worktree에서 shell, editor, AI command를 간단한 명령으로 실행한다.
    - 3) 경량 CLI surface로 parallel development의 진입장벽을 낮춘다.

- [Claude Squad는 tmux와 git worktree를 조합해 여러 terminal agent를 한 창에서 관리하는 TUI로, background task와 isolated workspace 운영 reference다](https://github.com/smtg-ai/claude-squad)
  - sources: `github_readme_manual_review_2026-03-15` + `tui_background_management_review_2026-03-15`
  - agent: `A00`
  - taxonomy: [[tmux-tui, background-agents, isolated-workspace, review-before-apply]] · Axis O
  - role_in_skill: tmux 기반 장기 세션과 review-before-apply 흐름이 실제 운영에서 어떻게 쓰이는지 보여주는 reference.
  - key_idea: 각 task를 isolated workspace와 tmux session으로 분리하면, 여러 AI terminal agent를 한 화면에서 병렬 관리하면서도 충돌을 줄일 수 있다.
  - adoption_targets:
    - background task management
    - isolated workspace discipline
    - attach/detach/resume UX
    - review-before-apply future concept
  - cautions:
    - TUI 자체는 초기 skill scope가 아니다.
    - 현재는 backend state와 CLI contracts만 가져오고, UI는 나중 단계로 미뤄야 한다.
  - pseudocode_3lines:
    - 1) 각 작업을 별도 tmux session과 별도 workspace에 배치한다.
    - 2) 중앙 화면에서 여러 agent의 상태를 조회하고 attach/detach/resume 한다.
    - 3) apply 또는 push 전에 변경 내용을 review 가능한 흐름으로 유지한다.

- [tmux Getting Started Wiki는 tmux의 server-client-session-window-pane 개념과 detach/attach/command model을 설명해 orchestrator의 기본 실행 모델을 고정하는 공식 문서다](https://github.com/tmux/tmux/wiki/Getting-Started)
  - sources: `official_tmux_wiki_review_2026-03-15`
  - agent: `A00`
  - taxonomy: [[official-tmux-semantics, server-client-model, detach-attach, command-model]] · Axis O
  - role_in_skill: session/socket/server/client 개념을 잘못 이해하면 orchestrator registry와 lifecycle이 틀어지므로, tmux 기본 semantics를 고정하는 공식 reference.
  - key_idea: tmux는 server와 client를 분리하고, session/window/pane을 계층적으로 관리하며, detach/attach/command prompt를 통해 장기 프로세스를 유지한다.
  - adoption_targets:
    - server/client/socket terminology
    - session naming and attach semantics
    - command-vs-keybinding 사고
    - detached long-running process model
  - cautions:
    - tmux 개념과 우리 runtime registry는 별개의 층이다.
    - tmux object를 곧바로 canonical task identity로 사용하면 안 된다.
  - pseudocode_3lines:
    - 1) tmux server는 session/window/pane 상태를 유지하고 client는 attach/detach 한다.
    - 2) 명령은 shell 또는 tmux command prompt를 통해 실행되어 장기 프로세스를 관리한다.
    - 3) session lifecycle과 socket model을 이해한 뒤에만 상위 orchestrator registry를 설계한다.

- [tmux 공식 소스 저장소는 tmux 자체의 기본 계약과 문서 위치, build/runtime 전제를 보여주는 최종 기준점이다](https://github.com/tmux/tmux)
  - sources: `official_tmux_repo_review_2026-03-15`
  - agent: `A00`
  - taxonomy: [[official-source, terminal-multiplexer, command-contract, implementation-baseline]] · Axis O
  - role_in_skill: 위키/블로그 수준이 아니라 tmux의 공식 source-of-truth를 참조해 장기적으로 의존할 command contract와 문서 위치를 확인하는 기준점.
  - key_idea: tmux는 terminal multiplexer로서 세션을 백그라운드에서 유지하고, 문서와 manpage를 통해 command/flag/behavior contract를 제공한다.
  - adoption_targets:
    - official command assumptions
    - manpage-first troubleshooting
    - tmux version compatibility awareness
  - cautions:
    - 구현 상세를 지금 당장 skill에 흡수할 필요는 없다.
    - 하지만 version drift가 생기면 launch/capture behavior가 바뀔 수 있으므로 official source를 최종 기준으로 삼아야 한다.
  - pseudocode_3lines:
    - 1) tmux의 공식 command/flag/behavior를 source와 manpage 기준으로 확인한다.
    - 2) orchestrator가 기대하는 session/socket/attach semantics가 실제 tmux와 맞는지 검증한다.
    - 3) version drift가 의심되면 공식 repo와 manpage를 다시 참조해 contract를 재고정한다.

## How To Use This Knowledge Base

이 knowledge base는 단순 링크 모음이 아니다.  
`codex-tmux-orchestrator`를 만들 때 어떤 reference에서 어떤 설계 요소를 가져와야 하는지 빠르게 분해하기 위한 작업용 인덱스다.

권장 사용 방법은 아래와 같다.

1. 먼저 `codex-tmux-orchestrator-reference-2026-03-15-03-12.md`를 읽는다.
- 여기서 skill의 정체성, 책임 경계, 상태 머신 방향성을 먼저 이해한다.

2. 그 다음 이 knowledge base의 `Coverage Matrix`를 본다.
- 어떤 reference가 어느 축을 잘 덮는지 확인한다.
- 모든 reference를 같은 비중으로 읽을 필요는 없다.

3. 현재 구현하려는 문서/스크립트에 맞는 URL만 읽는다.
- 예: `SESSION_STATE_MACHINE.md`를 쓸 때는 `ccmanager`, `codex-cli-farm`, `tmux wiki`가 핵심이다.
- 예: `RUNTIME_REGISTRY_SCHEMA.md`를 쓸 때는 `kosho`, `codex-cli-farm`, `coder/mux`가 핵심이다.

4. 외부 reference의 product-wide scope를 그대로 복제하지 않는다.
- 각 reference에서 필요한 축만 추출한다.
- 초기 skill은 `dispatch-first runtime orchestration`에만 집중한다.

5. 구현 후에는 반드시 checklist로 다시 되돌아간다.
- [codex-tmux-orchestrator-checklist-2026-03-15-02-51.md](./codex-tmux-orchestrator-checklist-2026-03-15-02-51.md)
- reference에서 아이디어를 가져왔다고 해서 구현이 정합한 것은 아니다.

## Runtime-Orchestration Dimensions

`codex-tmux-orchestrator`를 설계할 때 중요한 축은 아래 8개다.

### D1. Session Lifecycle
- session 생성
- command 전송
- launch success 판정
- completed/failed/killed/stale 전이
- restart
- cleanup

### D2. Worktree Binding
- dispatch가 지정한 worktree와 실제 launch 위치 일치 여부
- branch correctness
- wrong-worktree 방지

### D3. Registry & Recovery
- runtime JSON
- log file
- heartbeat file
- session metadata
- attempt history
- orphan/stale repair

### D4. Health Detection
- tmux session exists vs worker healthy 구분
- busy/waiting/idle/stale/fail 구분
- marker protocol
- heartbeat timeout

### D5. Operator UX
- list/status/watch
- attach/restart/cleanup
- 사람이 읽을 수 있는 naming
- machine-readable output과 human-readable summary 동시 제공

### D6. Bootstrap & Hooks
- preflight validation
- env/config/dependency bootstrap
- state hooks
- create/run/cleanup hooks

### D7. Multi-Project Future
- 여러 repo를 다룰 때 확장 가능성
- provider preset
- global discovery
- central control plane

### D8. Codex-Specific Runtime Semantics
- Codex CLI long-running behavior
- auth/network failure handling
- quote-safe launch
- pane/log/session attempt lineage

## Coverage Matrix

| Reference | D1 Session Lifecycle | D2 Worktree Binding | D3 Registry & Recovery | D4 Health Detection | D5 Operator UX | D6 Bootstrap & Hooks | D7 Multi-Project Future | D8 Codex-Specific Runtime |
|---|---|---|---|---|---|---|---|---|
| `par` | Y | Y | partial | partial | Y | partial | partial | partial |
| `ccmanager` | Y | Y | Y | Y | Y | Y | Y | partial |
| `emdash` | partial | Y | partial | partial | partial | partial | Y | partial |
| `gwq` | partial | Y | low | partial | Y | low | partial | low |
| `agentree` | low | Y | low | low | partial | Y | low | low |
| `kosho` | partial | Y | Y | low | partial | Y | low | low |
| `codex-cli-farm` | Y | low | Y | Y | Y | low | low | Y |
| `commander` | partial | Y | Y | partial | Y | partial | Y | Y |
| `cmux` | partial | Y | partial | partial | Y | low | Y | Y |
| `coder/mux` | Y | Y | Y | partial | Y | low | Y | partial |
| `phantom` | partial | Y | partial | low | Y | partial | low | partial |
| `claude-squad` | Y | Y | low | partial | Y | low | low | partial |
| `tmux wiki` | Y | low | low | low | partial | low | low | low |
| `tmux repo` | Y | low | low | low | low | low | low | low |

해석 포인트:
- `par`는 naming과 context UX가 강하다.
- `ccmanager`는 state detection과 hooks가 강하다.
- `codex-cli-farm`은 Codex-specific logging과 unified monitoring이 강하다.
- `kosho`는 repo-local registry와 prune/cleanup 사고가 강하다.
- `tmux wiki`와 `tmux repo`는 공식 계약 확인용이다.
- 한 reference만으로는 충분하지 않다.

## Direct Mapping To Planned Skill Artifacts

### 1. `LAUNCH_CONTRACT.md`
주요 reference:
- `tmux wiki`
- `par`
- `codex-cli-farm`
- 내부 `tmux-controller`

이 문서에서 결정해야 할 것:
- 입력 필드
- 출력 필드
- launch 전제 조건
- start/done/fail marker contract
- session/socket/log path allocation

### 2. `SESSION_STATE_MACHINE.md`
주요 reference:
- `ccmanager`
- `codex-cli-farm`
- `claude-squad`
- 내부 `tmux-controller` troubleshooting

이 문서에서 결정해야 할 것:
- `planned / launching / running / waiting_input / stale / failed / completed / killed / archived`
- 허용 전이
- 금지 전이
- stale 판정 규칙
- restart 후 상태 복귀 규칙

### 3. `RUNTIME_REGISTRY_SCHEMA.md`
주요 reference:
- `kosho`
- `codex-cli-farm`
- `coder/mux`
- `commander`

이 문서에서 결정해야 할 것:
- `.codex/runtime/*.json`
- `.codex/logs/*.log`
- `.codex/heartbeats/*.json`
- session metadata
- attempt history
- lineage / previous_attempts

### 4. `MARKER_PROTOCOL.md`
주요 reference:
- 내부 `tmux-controller` troubleshooting
- `codex-cli-farm`
- `tmux wiki`

이 문서에서 결정해야 할 것:
- start marker
- heartbeat marker
- done marker
- fail marker
- false positive 방지 규칙
- attempt/version tagging

### 5. `HEARTBEAT_POLICY.md`
주요 reference:
- `ccmanager`
- `codex-cli-farm`
- `coder/mux`

이 문서에서 결정해야 할 것:
- heartbeat file schema
- first-heartbeat rule
- stale timeout
- session exists vs worker healthy distinction

### 6. `FAILURE_CASES.md`
주요 reference:
- 내부 `tmux-controller` troubleshooting
- 내부 `worktree-parallel` troubleshooting
- `ccmanager`
- `claude-squad`
- `codex-cli-farm`

이 문서에서 결정해야 할 것:
- duplicate launch
- wrong worktree
- log path collision
- stale registry
- half-cleanup
- marker false positive
- revision mismatch
- auth/network launch failure

### 7. `CLEANUP_RULES.md`
주요 reference:
- `kosho`
- `par`
- 내부 `worktree-parallel`
- `codex-cli-farm`

이 문서에서 결정해야 할 것:
- session kill
- registry cleanup
- heartbeat cleanup
- log retention vs deletion
- idempotent cleanup
- repair vs delete 구분

### 8. Scripts
- `orchestrator_preflight.py`
  - 참조: `agentree`, `tmux wiki`, `par`, 내부 `worktree-parallel`
- `orchestrator_launch.py`
  - 참조: `par`, `codex-cli-farm`, `tmux-controller`
- `orchestrator_status.py`
  - 참조: `gwq`, `ccmanager`, `claude-squad`
- `orchestrator_restart.py`
  - 참조: `ccmanager`, `coder/mux`, `codex-cli-farm`
- `orchestrator_cleanup.py`
  - 참조: `kosho`, `par`, `worktree-parallel`
- `orchestrator_registry_validate.py`
  - 참조: `kosho`, `commander`, `coder/mux`
- `orchestrator_markers.py`
  - 참조: 내부 `tmux-controller` troubleshooting + `tmux wiki`

## Recommended Reading Order

### Stage 1. 최소 개념 고정
1. `tmux wiki`
2. 내부 `tmux-controller/SKILL.md`
3. 내부 `worktree-parallel/SKILL.md`

목표:
- tmux server/client/session/pane 개념 고정
- worktree ownership과 tmux ownership이 다른 층이라는 점 고정

### Stage 2. Naming / State / Registry
4. `par`
5. `ccmanager`
6. `kosho`
7. `codex-cli-farm`

목표:
- naming 규칙
- runtime 상태
- registry 파일
- long-lived session handling

### Stage 3. UX / 확장 시야
8. `gwq`
9. `claude-squad`
10. `phantom`
11. `commander`
12. `coder/mux`
13. `cmux`
14. `emdash`

목표:
- status/watch UX
- future central control plane
- multi-agent/multi-project 확장 감각

## Common Failure Modes This KB Is Trying To Prevent

이 knowledge base는 아래 실패 패턴을 줄이기 위해 수집되었다.

### 1. `tmux session exists`를 곧바로 `worker healthy`로 오판
필요 reference:
- `ccmanager`
- `codex-cli-farm`
- `tmux wiki`

### 2. 잘못된 worktree에서 Codex launch
필요 reference:
- `par`
- `agentree`
- 내부 `worktree-parallel`

### 3. duplicate launch
필요 reference:
- `par`
- `codex-cli-farm`
- `kosho`

### 4. log path collision / attempt lineage 상실
필요 reference:
- `codex-cli-farm`
- `coder/mux`
- `commander`

### 5. stale session cleanup 누락
필요 reference:
- `kosho`
- 내부 `tmux-controller` troubleshooting
- 내부 `worktree-parallel` troubleshooting

### 6. 사람이 읽기 어려운 운영 상태
필요 reference:
- `gwq`
- `claude-squad`
- `ccmanager`

### 7. bootstrap 미흡으로 launch 직후 실패
필요 reference:
- `agentree`
- `kosho`
- `commander`

### 8. product-wide scope를 초기 skill에 과하게 복제
필요 reference:
- `emdash`
- `cmux`
- `coder/mux`

이 세 개는 매우 유용하지만, 초기 skill scope를 과도하게 키우는 함정도 함께 준다.

## Suggested Minimal Reference Stack For v01

v0.1을 만드는 데 꼭 필요한 최소 묶음은 아래다.

### Must Read
- `tmux wiki`
- 내부 `tmux-controller/SKILL.md`
- 내부 `worktree-parallel/SKILL.md`
- `par`
- `ccmanager`
- `codex-cli-farm`
- `kosho`

### Read If Needed
- `agentree`
- `gwq`
- `claude-squad`
- `phantom`

### Later / Expansion
- `emdash`
- `commander`
- `cmux`
- `coder/mux`

이 구분의 이유:
- `Must Read`는 v0.1의 launch/status/restart/cleanup contract에 직접 필요하다.
- `Read If Needed`는 UX와 bootstrap 보강에 좋다.
- `Later / Expansion`은 multi-agent control plane 또는 product-level orchestration에 유용하지만, 초기에 다 가져오면 scope가 커진다.

## Suggested Next Files To Create In references

1. `LAUNCH_CONTRACT.md`
- launch 입력/출력/exit code/marker contract

2. `SESSION_STATE_MACHINE.md`
- runtime status와 허용 전이

3. `RUNTIME_REGISTRY_SCHEMA.md`
- `.codex/runtime`, `.codex/logs`, `.codex/heartbeats`, `.codex/sessions`

4. `MARKER_PROTOCOL.md`
- start/heartbeat/done/fail marker 정의

5. `HEARTBEAT_POLICY.md`
- stale timeout, first heartbeat, worker liveness 판정

6. `FAILURE_CASES.md`
- duplicate launch / wrong worktree / half-cleanup / auth failure

7. `CLEANUP_RULES.md`
- session/registry/heartbeat/log 정리 규칙

8. `COMMAND_PRESETS.md`
- Codex CLI launch command variants와 quoting policy

## Suggested Next Scripts To Create In scripts

1. `orchestrator_preflight.py`
- packet/dispatch/worktree/branch/log-path/session-name 충돌 검사

2. `orchestrator_launch.py`
- session 생성 + command send + registry write + first heartbeat 확인

3. `orchestrator_status.py`
- human-readable + machine-readable 상태 출력

4. `orchestrator_restart.py`
- stale/failed dispatch 재시작

5. `orchestrator_cleanup.py`
- session kill + runtime registry cleanup + heartbeat cleanup

6. `orchestrator_registry_validate.py`
- orphan/stale/collision 검사 및 repair suggestion

7. `orchestrator_markers.py`
- marker 생성/파싱/검증 유틸리티

8. `orchestrator_watch.py`
- watch-friendly runtime summary 출력

## Suggested Minimal Acceptance Plan

### Step 1. Static validation
- registry schema validation
- deterministic naming validation
- log path uniqueness validation

### Step 2. Local smoke run
- ready dispatch 1개 launch
- first heartbeat 확인
- done marker 확인
- runtime file finalize 확인

### Step 3. Failure injection
- wrong branch launch
- missing worktree
- duplicate session name
- no-heartbeat run
- half-cleanup case

### Step 4. Restart test
- running -> stale
- stale -> relaunch
- attempt number increment
- previous log 보존

### Step 5. CLI ergonomics
- `status`
- `status --json`
- `restart`
- `cleanup`
- `watch`

최소 acceptance 기준:
- wrong-worktree launch 차단
- duplicate-launch 차단
- stale 탐지 가능
- registry로 current runtime 상태 복구 가능
- cleanup idempotent
