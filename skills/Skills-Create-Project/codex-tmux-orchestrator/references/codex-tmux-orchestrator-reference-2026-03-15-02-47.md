- version: `v0.1.0`
  - created_at: `2026-03-15`
  - purpose: `codex-tmux-orchestrator` Skill의 역할, 경계, 의존성, 외부 reference, 구현 방향을 정리한 설계 reference
  - status: `draft-reference`
  - related_skill: `codex-tmux-orchestrator`

  ## 1. 문서 목적

  이 문서는 `codex-tmux-orchestrator`를 새 Skill로 설계할 때 필요한 기준 reference를 모아 둔 문서다.

  이 Skill의 목적은 단순히 `tmux` 명령을 대신 치는 것이 아니다.
  핵심은 아래 세 가지를 안정적으로 묶는 것이다.

  1. 이미 정의된 task/dispatch를 읽는다.
  2. 해당 task를 올바른 worktree에서 `Codex CLI` 세션으로 실행한다.
  3. 세션, 로그, heartbeat, 재시작, 상태 동기화까지 관리한다.

  즉 `codex-tmux-orchestrator`는 다음 두 내부 Skill의 빈틈을 메우는 상위 runtime layer다.

  - `tmux-controller`
  - `worktree-parallel`

  ---

  ## 2. 이 Skill이 필요한 이유

  현재 병렬 Codex 운영에서 필요한 기능은 네 층으로 분리된다.

  1. 작업 계약
  - 무엇을 할지
  - 어디를 수정할지
  - 무엇이 완료인지

  2. 배치
  - 어느 branch/worktree에 배정할지
  - 어떤 경로를 점유할지
  - 충돌이 없는지

  3. 실행
  - 어떤 `tmux session`에서
  - 어떤 `codex exec` 명령으로
  - 어떤 로그/heartbeat 규약으로 돌릴지

  4. 관측
  - 지금 살아 있는지
  - 멈췄는지
  - stale인지
  - 재시작이 필요한지

  이 중 3번이 현재 비어 있다.
  `tmux-controller`는 `tmux` primitive를 제공하지만 task-aware runtime orchestrator는 아니다.
  `worktree-parallel`은 worktree fan-out/fan-in을 다루지만 session launch manager는 아니다.

  따라서 `codex-tmux-orchestrator`는 다음 빈 공간을 메워야 한다.

  - `dispatch -> tmux session` 변환
  - `dispatch -> codex launch command` 변환
  - `session/log/heartbeat -> runtime state` 기록
  - 재실행/복구/정리 표준화

  ---

  ## 3. 내부 기준점: 현재 이미 있는 두 Skill

  ### 3.1 `tmux-controller`에서 가져와야 하는 것
  내부 참조:
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/
  tmux-controller/SKILL.md`
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/
  tmux-controller/references/troubleshooting.md`

  핵심 계승 포인트:
  - tmux 세션 생성/명령 실행/capture/wait/restart/kill 패턴
  - isolated socket 사용
  - stale session 정리
  - 완료 마커 기반 wait 패턴
  - `codex exec --full-auto` 같은 장시간 실행 커맨드 취급
  - long-running command와 log tail 운영 방식

  주의 포인트:
  - `tmux-controller`는 task semantic을 모른다.
  - 즉 `session`을 만들 수는 있어도, 어떤 dispatch와 연결되는지 canonical ownership을 가지지 않는다.
  - 따라서 `codex-tmux-orchestrator`는 `tmux-controller`를 하위 실행 계층으로 쓰되, 별도의 registry/state를 가져야 한
  다.

  ### 3.2 `worktree-parallel`에서 가져와야 하는 것
  내부 참조:
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/
  worktree-parallel/SKILL.md`
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/
  worktree-parallel/references/troubleshooting.md`

  핵심 계승 포인트:
  - main/architect vs builder/worktree 분리 사고방식
  - spawn/status/validate/merge-check/cleanup의 lifecycle
  - `.agent-status/` 같은 상태 파일 사고방식
  - sandbox에서 spawn 제약이 있다는 운영 현실
  - orphan state / false success / merge timing 같은 실패 패턴

  주의 포인트:
  - `worktree-parallel`은 session runtime을 소유하지 않는다.
  - 어떤 worktree에 무엇이 떠 있는지, 어떤 tmux pane에서 Codex가 살아 있는지까지는 관리 범위가 아니다.

  ---

  ## 4. 외부 GitHub Reference 요약

  ### 4.1 `par`
  - URL: https://github.com/coplane/par
  - 핵심: label 기반으로 branch, worktree, tmux session을 함께 관리하는 parallel worktree & session manager
  - 왜 중요한가:
    - `codex-tmux-orchestrator`가 가져야 하는 가장 직접적인 UX reference
    - `task/label -> worktree -> session` 매핑을 한 흐름으로 다룬다
  - 배울 점:
    - deterministic naming
    - global listing/open/send/control-center
    - session/workspace를 label 중심으로 조작하는 인터페이스
  - 그대로 복제하면 안 되는 점:
    - `par`는 범용 세션 관리자다
    - 우리는 `Codex CLI runtime`과 `dispatch metadata`에 더 강하게 결합돼야 한다

  ### 4.2 `ccmanager`
  - URL: https://github.com/kbwo/ccmanager
  - 핵심: 여러 AI coding assistant session을 git worktree와 project 단위로 관리하는 session manager
  - 왜 중요한가:
    - 상태 감지, hook, multi-project, session copy, preset/fallback 개념이 매우 강함
  - 배울 점:
    - state detection 전략
    - status change hooks
    - worktree lifecycle 후 자동화
    - multi-project registry
    - CLI별 command preset
  - 특히 중요한 포인트:
    - busy/waiting/idle 같은 상태 표현
    - worktree 생성 성공과 session start 성공을 분리해서 보는 운영 감각

  ### 4.3 `emdash`
  - URL: https://github.com/generalaction/emdash
  - 핵심: isolated git worktree에서 여러 coding agent를 병렬 실행하는 orchestration layer
  - 왜 중요한가:
    - `codex-tmux-orchestrator`의 상위 product 방향과 가장 유사하다
    - provider-agnostic, worktree-isolated, fan-out/fan-in 흐름이 명확하다
  - 배울 점:
    - ticket/task를 agent 실행 단위로 fan-out
    - review/reconciliation 전 단계 분리
    - 병렬 에이전트를 단순 실행이 아니라 orchestration workflow로 취급

  ### 4.4 `gwq`
  - URL: https://github.com/d-kuro/gwq
  - 핵심: git worktree manager + status watch + tmux + task queue 요소를 포함한 병렬 AI coding workflow 도구
  - 왜 중요한가:
    - CLI에서 watchable status를 어떻게 보여줄지 참고하기 좋다
  - 배울 점:
    - global discovery
    - `status --watch`
    - `tmux run/list/attach/kill`
    - task/dependency/resource 관리 방향
  - 우리에게 주는 시사점:
    - `codex-tmux-orchestrator`도 status 출력이 사람이 읽을 수 있어야 한다
    - 단순 JSON 파일만 남기면 운영성이 약하다

  ### 4.5 `agentree`
  - URL: https://github.com/AryaLabsHQ/agentree
  - 핵심: AI coding agent용 worktree bootstrap 자동화
  - 왜 중요한가:
    - 실행 직전 bootstrap 개념을 잘 보여준다
  - 배울 점:
    - env 복사
    - dependency 설치
    - AI tool 설정 복사
    - worktree ready-state를 “실제로 실행 가능한 상태”까지 끌고 간다
  - 우리에게 주는 시사점:
    - orchestrator는 launch 전에 worktree가 runnable 상태인지 확인해야 한다
    - 단순히 branch/worktree가 있다고 바로 Codex를 띄우면 안 된다

  ### 4.6 `kosho`
  - URL: https://github.com/carlsverre/kosho
  - 핵심: repo-local `.kosho/` registry와 hook을 가진 lightweight worktree manager
  - 왜 중요한가:
    - 로컬 registry 디렉토리 구조가 단순하고 명확하다
  - 배울 점:
    - `.kosho/worktrees/` 같은 repo-local metadata 구조
    - create hook
    - prune 개념
  - 우리에게 주는 시사점:
    - `.codex/sessions/`, `.codex/logs/`, `.codex/runtime/` 같은 repo-local registry 설계가 적합할 가능성이 높다

  ### 4.7 `codex-cli-farm`
  - URL: https://github.com/waskosky/codex-cli-farm
  - 핵심: Codex CLI 인스턴스를 tmux에서 장기 운영하고 snapshot/restore/watch를 제공하는 farm 패턴
  - 왜 중요한가:
    - 이름 그대로 `Codex + tmux + monitoring` reference다
  - 배울 점:
    - long-lived session
    - centralized logging
    - unified monitoring
    - manifest snapshot/restore
  - 우리에게 주는 시사점:
    - `codex-tmux-orchestrator`는 단발성 launch만이 아니라 재개/복구도 고려해야 한다

  ### 4.8 `commander`
  - URL: https://github.com/autohandai/commander
  - 핵심: 여러 CLI coding agent를 local worktree 기반으로 orchestration 하는 commander center
  - 왜 중요한가:
    - multi-agent control-plane 사고방식을 보여준다
  - 배울 점:
    - project lifecycle
    - branch/worktree selector
    - parallel session tracking
  - 우리에게 주는 시사점:
    - 나중에 `codex-session-monitor`와 결합될 중앙 관제형 설계의 방향성을 보여준다

  ### 4.9 `coder/mux` 및 `manaflow-ai/cmux`
  - URL: https://github.com/coder/cmux
  - URL: https://github.com/manaflow-ai/cmux
  - 핵심: 병렬 에이전트 개발을 위한 중앙 orchestrator/manager
  - 왜 중요한가:
    - worktree/isolated workspace 위에서 여러 agent를 동시에 관리하는 product-level 사고를 제공한다
  - 배울 점:
    - central overview
    - multiple models / multiple tasks
    - restart-resume UX
    - git divergence visibility
  - 우리에게 주는 시사점:
    - 단순 `tmux wrapper`로 끝내지 말고 runtime registry와 session summary를 같이 설계해야 한다

  ### 4.10 `phantom`
  - URL: https://github.com/aku11i/phantom
  - 핵심: worktree 생성과 tmux/editor/AI launch를 가볍게 붙여 주는 CLI
  - 왜 중요한가:
    - “작고 빠른 실행 UX”가 좋다
  - 배울 점:
    - `create`, `exec`, `shell`, `ai`, `tmux`
    - centrally managed worktree path
  - 우리에게 주는 시사점:
    - v0.1에서는 heavy orchestration보다 command surface를 작게 시작하는 게 낫다

  ### 4.11 `worksfornow` gist
  - URL: https://gist.github.com/worksfornow
  - 핵심: tmux + git worktree + markdown prompt 기반으로 병렬 task를 delegate하는 scrappy workflow
  - 왜 중요한가:
    - 가장 raw한 운영 패턴을 보여준다
  - 배울 점:
    - task list 조회
    - task별 prompt 조립
    - tmux agent spawn
  - 우리에게 주는 시사점:
    - `codex-task-packet -> orchestrator` 연결부를 단순하게 유지해야 한다

  ### 4.12 `claude-squad`
  - URL: https://github.com/smtg-ai/claude-squad
  - 핵심: 여러 terminal agent를 별도 workspace에서 관리하는 TUI/terminal manager
  - 왜 중요한가:
    - isolated workspace + background task + review-before-apply 개념이 강함
  - 배울 점:
    - long-running background management
    - review-centric orchestration
  - 우리에게 주는 시사점:
    - orchestrator는 실행만 하지 말고 “검토 가능한 상태”를 유지해야 한다

  ---

  ## 5. `codex-tmux-orchestrator`의 정체성 정의

  ### 이 Skill이 아닌 것
  - 단순 `tmux helper`
  - 단순 `git worktree spawn helper`
  - 단순 `session monitor`
  - 단순 `task packet renderer`
  - acceptance gate evaluator

  ### 이 Skill인 것
  - `task-packet`과 `dispatch`를 소비하는 실행 계층
  - Codex 세션의 launch/restart/cleanup을 담당하는 runtime orchestrator
  - session/log/heartbeat/status를 canonical runtime registry에 기록하는 skill
  - `tmux-controller`와 `worktree-parallel` 사이를 연결하는 상위 adapter

  ---

  ## 6. 책임 경계

  ### 이 Skill이 소유해야 하는 것
  - `session_name`
  - `session_socket` 또는 socket namespace
  - `launch_command`
  - `log_path`
  - `heartbeat_path`
  - `runtime_status`
  - `launch_started_at`
  - `launch_finished_at`
  - `last_seen_at`
  - `restart_count`
  - `exit_reason`
  - `marker protocol`
  - `capture protocol`

  ### 이 Skill이 읽기만 해야 하는 것
  - `task-packet.goal`
  - `task-packet.allowed_paths`
  - `task-packet.done_definition`
  - `dispatch.worktree_path`
  - `dispatch.branch`
  - `dispatch.assigned_agent`
  - `dispatch.status`
  - `dispatch.locked_paths`

  ### 이 Skill이 소유하면 안 되는 것
  - task goal 원문 변경
  - worktree spawn 자체의 canonical ownership
  - merge readiness 단독 판정
  - path overlap 판정
  - acceptance grading
  - long-term project planning

  ---

  ## 7. 하드 의존성

  이 Skill은 아래 선행 Skill/구조 없이는 완성될 수 없다.

  ### 7.1 `codex-task-packet`
  필요 이유:
  - 어떤 작업인지 알아야 한다
  - worker prompt를 deterministic하게 생성해야 한다
  - done definition과 allowed scope를 launch context에 반영해야 한다

  ### 7.2 `codex-worktree-dispatch`
  필요 이유:
  - 어느 worktree에서 실행해야 하는지 알아야 한다
  - branch/worktree/assigned agent/status를 읽어야 한다
  - launch 가능 상태(`ready`)인지 판단해야 한다

  ### 7.3 `tmux-controller`
  필요 이유:
  - 실제 tmux 세션 lifecycle 제어를 재사용하기 위함
  - create/exec/capture/wait/restart/kill primitive를 직접 다시 만들 필요가 없다

  ### 7.4 `worktree-parallel`
  필요 이유:
  - 병렬 worktree 운영 규칙과 merge-check lifecycle을 재사용하기 위함
  - orchestrator가 worktree ownership 정책을 임의로 바꾸면 안 된다

  ---

  ## 8. 설계 원칙

  ### 8.1 One Dispatch -> One Primary Runtime
  - 하나의 dispatch는 기본적으로 하나의 주 session만 가진다
  - 재시도는 같은 runtime lineage에서 관리한다
  - 복수 tmux session fan-out은 v0.1에서 금지하는 편이 안전하다

  ### 8.2 Deterministic Naming
  - `task_id`, `dispatch_id`, `branch`, `worktree_path`에서 session name이 결정돼야 한다
  - 예:
    - `codex-<task_slug>`
    - `codex-<dispatch_id>`
  - 이름이 랜덤이면 restart/recovery가 약해진다

  ### 8.3 Explicit Registry
  - runtime registry는 파일로 남아야 한다
  - 추천 디렉토리:
    - `.codex/sessions/`
    - `.codex/logs/`
    - `.codex/runtime/`
  - `tmux ls`만 source of truth로 쓰면 안 된다

  ### 8.4 Marker-based Completion
  - `tmux wait`나 raw output string 매칭만 믿지 않는다
  - 명시적 시작/종료 마커가 필요하다
  - 예:
    - `__CODEX_RUN_START__:<dispatch_id>:<timestamp>`
    - `__CODEX_RUN_DONE__:<dispatch_id>:<exit_code>:<timestamp>`

  ### 8.5 Heartbeat Before “Running”
  - session이 생성됐다고 바로 `running`으로 보지 않는다
  - 최소 한 번의 launch success marker 또는 heartbeat가 있어야 `running` 판정 가능

  ### 8.6 Launch Must Validate Worktree
  - 존재하는 worktree인지
  - branch가 맞는지
  - repo root가 맞는지
  - dispatch revision mismatch가 없는지
  - 이 검증 없이 launch 금지

  ---

  ## 9. 최소 상태 머신 제안

  ### Runtime 상태
  - `planned`
  - `launching`
  - `running`
  - `waiting_input`
  - `completed`
  - `failed`
  - `stale`
  - `killed`
  - `abandoned`

  ### 핵심 전이
  - `planned -> launching`
  - `launching -> running`
  - `launching -> failed`
  - `running -> waiting_input`
  - `running -> completed`
  - `running -> failed`
  - `running -> stale`
  - `stale -> launching`
  - `failed -> launching`
  - `running -> killed`
  - `completed -> archived`

  ### 전이 규칙
  - `planned -> launching`은 dispatch가 `ready`일 때만 허용
  - `launching -> running`은 session 존재 + heartbeat 확인 후
  - `running -> stale`은 heartbeat timeout 또는 session disappear
  - `failed -> launching`은 restart policy 충족 시에만
  - `completed`는 종료 marker 기록 후에만

  ---

  ## 10. Launch Contract 제안

  이 Skill은 결국 아래 계약을 실행 가능한 형태로 고정해야 한다.

  ### 입력
  - `task_id`
  - `dispatch_id`
  - `packet_path`
  - `worktree_path`
  - `branch`
  - `launch_mode`
  - `codex_command_template`
  - `log_path`
  - `heartbeat_path`

  ### 출력
  - `session_name`
  - `runtime_status`
  - `started_at`
  - `last_seen_at`
  - `pid/session metadata`
  - `exit_code`
  - `failure_reason`
  - `artifacts`

  ### Launch 전 필수 체크
  - packet exists
  - dispatch exists
  - dispatch status is `ready`
  - worktree exists
  - branch matches
  - locked paths conflict 없음
  - runtime registry collision 없음
  - log path collision 없음

  ### Launch 후 필수 기록
  - session created
  - log path allocated
  - heartbeat initialized
  - launch marker written
  - runtime registry file created

  ---

  ## 11. 실패 패턴: 반드시 먼저 막아야 할 것

  ### 11.1 잘못된 worktree에서 launch
  원인:
  - dispatch가 오래됐거나
  - session reuse가 잘못됐거나
  - branch/worktree mapping이 틀림

  영향:
  - 다른 task 결과를 덮어씀
  - diff provenance가 깨짐

  대응:
  - launch 직전 `pwd`, `git branch --show-current`, repo root 검증
  - dispatch revision과 branch/worktree 재검증

  ### 11.2 같은 dispatch를 두 번 launch
  원인:
  - stale 상태 오판
  - previous session 미정리
  - operator가 다시 실행

  영향:
  - 로그 충돌
  - 상태 오염
  - 동일 task 이중 진행

  대응:
  - active session registry uniqueness 검사
  - same `dispatch_id` live session 금지
  - override는 명시 플래그 필요

  ### 11.3 wait marker false positive
  원인:
  - 너무 흔한 문자열을 완료 마커로 씀

  영향:
  - 실제로는 안 끝났는데 completed로 오판

  대응:
  - dispatch-specific marker 사용
  - stdout/stderr 합성 log에서도 충돌 안 나는 긴 marker 사용

  ### 11.4 heartbeat 없이 session만 살아 있음
  원인:
  - Codex launch 실패
  - shell만 살아 있고 worker는 죽음

  영향:
  - running으로 보이지만 실질 dead

  대응:
  - session existence와 worker liveness를 분리
  - 일정 시간 heartbeat 없으면 `stale`

  ### 11.5 log path collision
  원인:
  - deterministic naming이 부족함
  - restart가 old log를 덮어씀

  영향:
  - 런 기록 손실
  - 디버깅 불가

  대응:
  - `task_id + dispatch_id + attempt_no` 기반 로그명
  - append vs rotate 정책 분리

  ### 11.6 revision mismatch launch
  원인:
  - packet이 업데이트됐는데 old render prompt로 실행

  영향:
  - 잘못된 task 수행
  - acceptance 판단 무효

  대응:
  - packet revision snapshot 저장
  - launch 시 current revision과 비교

  ### 11.7 stale session cleanup 누락
  원인:
  - tmux 세션만 죽였고 runtime registry 정리를 안 함

  영향:
  - 영구 blocked 상태
  - 재실행 불가 오판

  대응:
  - cleanup은 session + registry + heartbeat + locks 관점에서 일관되게 수행

  ---

  ## 12. v0.1 / v0.2 / v0.3 범위 제안

  ### v0.1
  필수:
  - 하나의 dispatch를 하나의 tmux Codex 세션으로 launch
  - deterministic session naming
  - log file 기록
  - heartbeat file 기록
  - status 조회
  - restart 1회
  - stale cleanup
  - launch preflight validation

  제외:
  - multi-project overview
  - session dashboard UI
  - auto queue scheduling
  - agent handoff graph

  ### v0.2
  추가:
  - 여러 ready dispatch를 batch launch
  - priority queue
  - retry policy
  - grouped status view
  - per-agent preset
  - post-completion hook

  ### v0.3
  추가:
  - multi-project orchestration
  - richer monitor integration
  - branch divergence summary
  - paused/resume semantics
  - adaptive restart policy
  - cross-repo workspace bundle

  ---

  ## 13. 이 Skill이 직접 만들지 말아야 하는 것

  다음은 tempting하지만 초기 구현에서 분리해야 한다.

  - 자체 worktree spawn engine
  - acceptance grading engine
  - full dashboard UI
  - code review UI
  - merge automation 전체
  - issue tracker sync 전체
  - model/router abstraction 전체

  이걸 한 Skill에 다 넣으면 실패한다.
  `codex-tmux-orchestrator`는 runtime coordination까지만 잘해야 한다.

  ---

  ## 14. 구현 시 바로 필요한 reference 문서들

  이 Skill을 만들 때 같이 분리해서 있어야 하는 문서:

  1. `LAUNCH_CONTRACT.md`
  - 입력/출력/exit code/markers 정의

  2. `SESSION_STATE_MACHINE.md`
  - runtime 상태와 허용 전이

  3. `REGISTRY_SCHEMA.md`
  - `.codex/sessions/*.json` 구조
  - `.codex/runtime/*.json` 구조

  4. `FAILURE_CASES.md`
  - stale, duplicate, wrong-worktree, heartbeat-missing

  5. `MARKER_PROTOCOL.md`
  - 시작/종료/heartbeat marker 규약

  6. `RESTART_POLICY.md`
  - 어떤 실패에서 자동 재시작 가능한지

  ---

  ## 15. 구현 시 바로 필요한 scripts

  추천 최소 scripts:

  1. `orchestrator_launch.py`
  - dispatch를 읽고 launch 수행

  2. `orchestrator_status.py`
  - runtime/session 상태 요약

  3. `orchestrator_restart.py`
  - stale/failed session 재시작

  4. `orchestrator_cleanup.py`
  - session + registry + heartbeat 정리

  5. `orchestrator_registry_validate.py`
  - orphan/stale/collision 검사

  6. `orchestrator_markers.py`
  - marker 생성/파싱 도우미

  7. `orchestrator_preflight.py`
  - launch 전 packet/dispatch/worktree 검증

  ---

  ## 16. 구현 체크포인트

  다음 항목이 없으면 이 Skill은 “동작한다”고 보기 어렵다.

  - dispatch 없이 launch 금지
  - ready 아닌 dispatch launch 금지
  - wrong worktree detection
  - duplicate session detection
  - deterministic log path
  - heartbeat timeout rule
  - restart policy
  - cleanup consistency
  - machine-readable status output
  - human-readable summary output

  ---

  ## 17. 최종 판단

  `codex-tmux-orchestrator`는 새로운 `tmux` Skill이 아니라,
  이미 존재하는 `tmux-controller`와 `worktree-parallel` 위에 올라가는 **Codex runtime coordinator**로 설계하는 것이
  맞다.

  가장 중요한 설계 포인트는 세 가지다.

  1. `dispatch -> session`의 deterministic mapping
  2. `session/log/heartbeat`를 파일 registry로 남기는 것
  3. `wrong launch / duplicate launch / stale runtime`를 초기에 강하게 막는 것

  이 세 가지가 안 되면 병렬 Codex 운영은 곧바로 불안정해진다.

  ---

  ## 18. 우선 채택할 Reference 우선순위

  ### 1순위
  - `par`
  - `ccmanager`
  - 내부 `tmux-controller`
  - 내부 `worktree-parallel`

  ### 2순위
  - `emdash`
  - `gwq`
  - `codex-cli-farm`

  ### 3순위
  - `agentree`
  - `kosho`
  - `phantom`
  - `commander`
  - `coder/mux`
  - `cmux`
  - `worksfornow` gist
  - `claude-squad`

  ---

  ## 19. Sources

  ### Local
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/
  tmux-controller/SKILL.md`
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/
  tmux-controller/references/troubleshooting.md`
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/
  worktree-parallel/SKILL.md`
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/
  worktree-parallel/references/troubleshooting.md`

  ### GitHub / Web
  - https://github.com/coplane/par
  - https://github.com/kbwo/ccmanager
  - https://github.com/generalaction/emdash
  - https://github.com/d-kuro/gwq
  - https://github.com/AryaLabsHQ/agentree
  - https://github.com/carlsverre/kosho
  - https://github.com/waskosky/codex-cli-farm
  - https://github.com/autohandai/commander
  - https://github.com/coder/cmux
  - https://github.com/manaflow-ai/cmux
  - https://github.com/aku11i/phantom
  - https://github.com/smtg-ai/claude-squad
  - https://gist.github.com/worksfornow