책임 경계표

  먼저 원칙부터 고정해야 한다.

  - codex-task-packet은 **불변 작업 계약서 (immutable task contract)** 다.
  - codex-worktree-dispatch는 **canonical mutable execution-prep state** 다.
  - codex-tmux-orchestrator는 **launch/session/log ownership layer** 다.
  - codex-session-monitor는 관측기다.

  즉:

  - task-packet은 무엇을 왜 어디까지 할지 — **계약은 불변이며 runtime/session/process 정보를 포함하지 않는다**
  - worktree-dispatch는 누가 어디서 어떤 브랜치로 할지 — **branch/worktree allocation과 mutable status transition의 canonical owner**
  - tmux-orchestrator는 실제로 어떻게 띄우고 재시작할지 — **tmux session, heartbeat, stdout/stderr/log의 owner**
  - session-monitor는 지금 살아 있는지, 멈췄는지, 실패했는지

  를 담당한다.

  | 책임 항목 | codex-task-packet | codex-worktree-dispatch | codex-tmux-orchestrator | codex-session-monitor |
  |---|---|---|---|---|
  | task_id 생성 규칙 | Owner | Consumer | Consumer | Consumer |
  | 작업 목표 goal | Owner | Consumer | Consumer | Read-only |
  | 완료 정의 done_definition | Owner | Consumer | Consumer | Read-only |
  | 허용 경로 allowed_paths | Owner | Consumer | Consumer | Read-only |
  | 금지 경로 forbidden_paths | Owner | Consumer | Consumer | Read-only |
  | 입력 컨텍스트 파일 목록 | Owner | Consumer | Consumer | Read-only |
  | 작업 우선순위 | Owner | Consumer | Consumer | Read-only |
  | 선행 작업 의존성 depends_on | Owner | Consumer | Consumer | Read-only |
  | 병렬 그룹 parallel_group | Owner | Consumer | Consumer | Read-only |
  | 브랜치 이름 | Hint만 가능 | Owner | Consumer | Read-only |
  | worktree 경로 | Hint만 가능 | Owner | Consumer | Read-only |
  | 파일 잠금/경로 점유 | No | Owner | Consumer | Read-only |
  | 담당 agent / worker | No | Owner | Consumer | Read-only |
  | tmux session 이름 | No | Hint 가능 | Owner | Consumer |
  | 실행 명령 템플릿 | Hint 가능 | Hint 가능 | Owner | Read-only |
  | heartbeat 파일 | No | No | Owner | Consumer |
  | stdout/stderr 로그 파일 | No | No | Owner | Consumer |
  | 상태 전이 queued/running/... | No | Owner | Producer/Updater | Consumer |
  | 재시도 횟수 | Hint 가능 | Owner | Consumer/Updater | Read-only |
  | merge readiness | No | Owner | No | Read-only |
  | 실시간 출력 요약 | No | No | Producer | Owner |
  | stale/failure 탐지 | No | No | Partial | Owner |
  | dashboard/report | No | Partial | Partial | Owner |

  핵심 경계: task-packet vs worktree-dispatch

  | 질문 | 답하는 스킬 |
  |---|---|
  | 이 작업의 본질은 무엇인가 | codex-task-packet |
  | 이 작업이 수정하면 안 되는 경로는 어디인가 | codex-task-packet |
  | 이 작업은 언제 끝난 것으로 볼 것인가 | codex-task-packet |
  | 이 작업은 어떤 선행 작업 뒤에 실행해야 하나 | codex-task-packet |
  | 이 작업을 어느 worktree에 배치할 것인가 | codex-worktree-dispatch |
  | 어떤 브랜치명을 쓸 것인가 | codex-worktree-dispatch |
  | 어떤 다른 작업과 파일 충돌 위험이 있는가 | codex-worktree-dispatch |
  | 현재 누가 맡고 있는가 | codex-worktree-dispatch |
  | 지금 상태가 queued인지 running인지 complete인지 | codex-worktree-dispatch |
  | merge 가능한가 | codex-worktree-dispatch |

  강한 규칙

  - task-packet 안에 `status`, `session_id`, `pid`, `heartbeat`, `log_path`를 넣지 않는다. packet은 runtime/session/process field를 금지한다.
  - worktree-dispatch 안에 `goal`, `why`, `done_definition`, `required_checks`, `deliverables` 원문을 canonical source처럼 중복 저장하지 않는다. dispatch는 `packet_path`로 참조만 한다.
  - task-packet은 재사용 가능한 불변 계약서여야 한다.
  - worktree-dispatch는 canonical mutable execution-prep state다.
  - tmux-orchestrator는 launch/session/log ownership layer다. packet contract를 수정하지 않고, dispatch를 대체하지 않는다.
  - `branch_hint`, `worktree_hint`, `launch_hint`는 **hint only**다. 실제 branch/worktree/session ownership은 dispatch와 runtime에 있다.
  - local progress/state가 필요해도 dispatch canonical state를 대체하지 않는다. local companion은 worker-local phase note, observations, scratch metric 수준까지만 허용한다.
  - 하나의 task-packet이 여러 개의 dispatch를 가질 수는 있어도, 하나의 dispatch가 여러 packet을 섞어선 안 된다.