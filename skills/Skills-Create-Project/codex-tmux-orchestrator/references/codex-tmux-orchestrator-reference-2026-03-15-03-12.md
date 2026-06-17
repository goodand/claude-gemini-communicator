# codex-tmux-orchestrator Reference
- version: `v0.2.0`
- created_at: `2026-03-15`
- updated_at: `2026-03-15`
- purpose: `codex-tmux-orchestrator` Skill의 정체성, 의존성, reference 해석, runtime contract, registry 설계, 실패 패턴, 구현 범위, 확장 방향을 매우 구체적으로 고정하기 위한 설계 reference
- status: `active-draft`
- related_skill: `codex-tmux-orchestrator`
- scope: `tmux 기반 Codex CLI 세션 오케스트레이션`
- non_scope: `task 계약 정의`, `worktree 배치 정책의 canonical ownership`, `acceptance grading`, `UI dashboard 구현`

---

## 1. 이 문서의 목적

이 문서는 `codex-tmux-orchestrator`를 단순한 `tmux helper`가 아니라, **Codex CLI 런타임 오케스트레이션 계층**으로 설계하기 위한 reference 문서다.

이 Skill은 아래 질문에 답할 수 있어야 한다.

1. 어떤 `task`를 어떤 `worktree`에서 실행할 것인가
2. 어떤 `tmux session`과 어떤 `Codex launch command`를 사용할 것인가
3. 실행이 실제로 시작됐는지, 단지 세션만 살아 있는 것인지 어떻게 구분할 것인가
4. 로그, heartbeat, 상태, 재시도, 정리를 어떤 파일 구조로 남길 것인가
5. stale session, duplicate launch, wrong worktree launch 같은 운영 실패를 어떻게 차단할 것인가

즉 이 Skill의 본질은 `tmux` 조작 자체가 아니라 아래 두 구조를 이어 붙이는 것이다.

- 상위 planning / dispatch layer
- 하위 terminal runtime / process layer

---

## 2. 이 Skill이 꼭 필요한 이유

현재 병렬 에이전트 운영에서 기능 층은 최소 네 개로 나뉜다.

### 2.1 작업 정의 층
여기서는 작업의 의미를 고정한다.

예:
- 무엇을 수정해야 하는가
- 어떤 파일 범위를 건드려도 되는가
- 완료 조건은 무엇인가
- 어떤 체크를 통과해야 하는가

이 층은 `codex-task-packet`의 책임이다.

### 2.2 배치 층
여기서는 작업을 실제 개발 공간에 배치한다.

예:
- 어느 branch에 태울 것인가
- 어느 worktree를 쓸 것인가
- 어느 파일을 lock할 것인가
- 어떤 작업과 충돌하는가
- 지금 `queued`인지 `ready`인지 `blocked`인지

이 층은 `codex-worktree-dispatch`의 책임이다.

### 2.3 실행 층
여기서는 이미 준비된 배치를 실제 세션으로 실행한다.

예:
- tmux session 이름은 무엇인가
- Codex CLI 커맨드는 무엇인가
- stdout/stderr/log/heartbeat는 어디에 남는가
- stale session은 어떻게 감지하는가
- 재시작은 가능한가
- launch 실패는 어떻게 기록하는가

이 층이 바로 `codex-tmux-orchestrator`의 책임이다.

### 2.4 관측 층
여기서는 지금 살아 있는 세션들을 사람과 자동화가 읽을 수 있게 만든다.

예:
- 현재 running/failed/stale/killed/completed는 몇 개인가
- 어떤 session이 오래 멈췄는가
- 마지막 output line은 무엇인가
- 어떤 dispatch가 launch 전인지 launch 후인지

이 층은 나중의 `codex-session-monitor` 책임에 가깝다.

핵심은, 3번이 비어 있으면 1번과 2번이 아무리 잘 돼도 실제 병렬 Codex 운영은 불안정해진다는 점이다.

---

## 3. `codex-tmux-orchestrator`의 정체성

### 3.1 이 Skill이 아닌 것
이 Skill은 아래 것들이 아니다.

- 단순 `tmux new-session` 래퍼
- 단순 worktree 생성기
- 단순 session viewer
- 단순 log tail 도구
- task prompt 생성기
- acceptance gate evaluator
- merge manager
- code review manager
- issue tracker sync 도구

### 3.2 이 Skill인 것
이 Skill은 아래 역할을 가져야 한다.

- `task-packet`과 `dispatch`를 읽고 실행 가능한 runtime plan으로 바꾸는 skill
- 준비된 worktree 안에서 Codex CLI를 launch 하는 skill
- tmux session, log file, heartbeat file, runtime state file을 함께 관리하는 skill
- launch, restart, kill, cleanup, stale detection을 일관된 contract로 제공하는 skill
- `tmux-controller`의 primitive를 재사용하되, task-aware runtime ownership을 추가하는 skill
- `worktree-parallel`의 worktree ownership을 침범하지 않으면서 실행 계층을 덧붙이는 skill

### 3.3 가장 간단한 한 줄 정의
`codex-tmux-orchestrator`는 **ready 상태의 dispatch를 받아 올바른 worktree에서 Codex CLI 세션으로 실행하고, 그 실행 상태를 세션·로그·heartbeat·registry로 추적하는 runtime coordinator**다.

---

## 4. 내부 Skill과의 관계

### 4.1 `tmux-controller`와의 관계
내부 참조:
- `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/tmux-controller/SKILL.md`
- `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/tmux-controller/references/troubleshooting.md`

`tmux-controller`가 잘하는 것:
- tmux session 생성
- 명령 전송
- capture
- wait 패턴
- restart/kill
- stale session 기본 정리

`tmux-controller`가 모르는 것:
- task packet
- dispatch readiness
- worktree correctness
- branch/worktree/task/session 4자 연결
- Codex launch 성공 여부와 세션 존재 여부의 차이
- launch registry canonical ownership

따라서 `codex-tmux-orchestrator`는 `tmux-controller`를 대체하면 안 된다.  
오히려 아래처럼 써야 한다.

- `tmux-controller` = terminal primitive layer
- `codex-tmux-orchestrator` = task-aware runtime coordination layer

### 4.2 `worktree-parallel`과의 관계
내부 참조:
- `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/worktree-parallel/SKILL.md`
- `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/worktree-parallel/references/troubleshooting.md`

`worktree-parallel`이 잘하는 것:
- parallel worktree lifecycle
- task-to-worktree 분리 사고
- status / validate / merge-check / cleanup
- architect vs builder 분리
- orphan state / false success 같은 운영 실패 인식

`worktree-parallel`이 모르는 것:
- tmux session launch
- Codex CLI 실행 계약
- session retry
- heartbeat tracking
- runtime stale detection
- session/log registry

따라서 `codex-tmux-orchestrator`는 worktree ownership을 가져오면 안 된다.  
이 Skill은 `dispatch`가 이미 정해준 worktree를 소비해야 한다.

### 4.3 이상적인 계층 구조
- `codex-task-packet`
- `codex-worktree-dispatch`
- `codex-tmux-orchestrator`
- `codex-session-monitor`

이 순서가 맞다.

---

## 5. 기능적 의존성

### 5.1 하드 의존성
이 Skill은 아래 없이는 설계가 흔들린다.

#### `codex-task-packet`
필요한 이유:
- task goal
- allowed paths
- done definition
- required checks
- task revision
- worker prompt source

#### `codex-worktree-dispatch`
필요한 이유:
- worktree path
- branch
- assigned agent
- dispatch status
- locked paths
- readiness
- dependency resolution 결과

#### `tmux-controller`
필요한 이유:
- tmux lifecycle primitive 재사용
- create/exec/capture/wait/kill/restart 재구현 방지

#### `worktree-parallel`
필요한 이유:
- worktree lifecycle 기준
- merge-check와 cleanup semantics 정합성
- spawn/validate 상태 개념 재사용

### 5.2 소프트 의존성
이건 있으면 좋지만 없어도 v0.1은 가능하다.

- `codex-session-monitor`
- notification hook
- dashboard UI
- multi-project overview
- branch divergence visualizer

---

## 6. 외부 GitHub Reference 분석

---

## 6.1 `par`
- URL: `https://github.com/coplane/par`

### 무엇을 하는 도구인가
`par`는 label 기반으로 branch, worktree, tmux session을 함께 관리하는 CLI다.  
병렬 개발을 위한 session/workspace orchestration UX가 매우 직접적이다.

### 이 레퍼런스가 중요한 이유
`codex-tmux-orchestrator`는 결국 “어떤 작업이 어떤 session으로 연결되는가”를 매끄럽게 다뤄야 한다.  
`par`는 이 문제를 label 중심으로 단순화한다.

### 꼭 배워야 하는 점
- worktree와 tmux를 같은 흐름에서 다룸
- deterministic naming
- `start`, `ls`, `open`, `send` 같은 operator-centric UX
- initialization command를 worktree 시작 시 자동 실행하는 방식
- 세션과 workspace를 분리하지 않고 operator가 하나의 실행 단위로 취급할 수 있게 만듦

### 우리 설계에 가져와야 하는 것
- `dispatch -> session_name` deterministic mapping
- launch 시 bootstrap command chain
- 사람이 읽을 수 있는 list/status 명령
- task label 또는 slug 중심 naming 규칙

### 그대로 가져오면 안 되는 것
- `par`는 범용 세션 관리자다
- 우리는 `dispatch`와 `task-packet`을 canonical source로 쓰는 project-specific runtime orchestrator다
- 따라서 `session`이 출발점이면 안 되고, `dispatch`가 출발점이어야 한다

---

## 6.2 `ccmanager`
- URL: `https://github.com/kbwo/ccmanager`

### 무엇을 하는 도구인가
여러 AI coding assistant session을 git worktree 위에서 관리한다.  
Codex CLI, Claude Code, Gemini CLI 등 여러 도구를 다루고, 상태 감지와 hook 체계가 강하다.

### 이 레퍼런스가 중요한 이유
이 도구는 단순 worktree manager가 아니라 **runtime state manager**에 가깝다.  
`codex-tmux-orchestrator`는 session이 실제로 busy인지 waiting인지 idle인지와 같은 런타임 감각을 배워야 한다.

### 꼭 배워야 하는 점
- session state detection
- status change hooks
- worktree hooks
- multi-project support
- command preset/fallback
- auto-generated worktree directory patterns
- host에서 관리하되, 실제 agent는 container/worktree 안에서 실행하는 사고

### 우리 설계에 가져와야 하는 것
- runtime state는 단순 `running/not-running`보다 풍부해야 함
- launch success와 worker progress를 분리해야 함
- session state 변화에 hook를 걸 수 있어야 함
- 향후 multi-project 확장이 가능해야 함
- Codex CLI command preset 계층이 있어야 함

### 특히 중요한 설계 교훈
tmux session이 살아 있는 것과 Codex worker가 실제로 의미 있게 실행 중인 것은 다르다.  
`codex-tmux-orchestrator`는 반드시 둘을 분리해서 봐야 한다.

---

## 6.3 `emdash`
- URL: `https://github.com/generalaction/emdash`

### 무엇을 하는 도구인가
여러 coding agent를 isolated git worktree에 병렬로 실행하는 orchestration layer다.

### 이 레퍼런스가 중요한 이유
이 도구는 단순 도구 모음이 아니라 “parallel coding agents orchestration”이라는 제품적 시야를 보여준다.  
`codex-tmux-orchestrator`도 단순 launch wrapper가 아니라 orchestration component로 생각해야 한다.

### 꼭 배워야 하는 점
- provider-agnostic orchestration
- isolated worktree를 기본값으로 삼음
- task/ticket handoff
- diff review fan-in
- local-first 운영

### 우리 설계에 가져와야 하는 것
- orchestrator는 launch만이 아니라 reconciliation을 고려해야 함
- runtime registry는 review/merge 이전 단계에서 의미를 가져야 함
- isolated worktree는 선택이 아니라 기본 safety primitive여야 함

### 그대로 가져오면 안 되는 것
- `emdash` 수준의 전체 product scope를 초기 Skill에 다 넣으면 실패한다
- 우리는 먼저 `Codex + tmux + dispatch`에 집중해야 한다

---

## 6.4 `gwq`
- URL: `https://github.com/d-kuro/gwq`

### 무엇을 하는 도구인가
git worktree manager에 fuzzy finder, status dashboard, tmux, task queue 개념이 붙은 CLI다.

### 중요한 점
`gwq`는 registry-less discovery와 watch-friendly UX를 보여준다.

### 꼭 배워야 하는 점
- `status --watch`
- worktree 활동 요약
- 전역 overview
- AI coding workflow를 위한 task/dependency/resource 표현
- tmux 연동

### 우리 설계에 주는 의미
- `codex-tmux-orchestrator`도 사람이 즉시 읽을 수 있는 상태 출력이 필요하다
- JSON registry만 있으면 운영성이 떨어진다
- 최소한 `status`와 `status --watch` 비슷한 인간 친화 출력이 있어야 한다

### 조심할 점
`gwq`는 filesystem scanning 접근을 쓰기 쉽다.  
하지만 우리 구조에서는 canonical registry도 필요하다.  
즉, `tmux ls` 또는 worktree scan만으로 truth를 재구성하면 안 된다.

---

## 6.5 `agentree`
- URL: `https://github.com/AryaLabsHQ/agentree`

### 무엇을 하는 도구인가
AI coding agent용 isolated worktree를 빠르게 만들고, env 복사/설정 복사/dependency 설치까지 자동화한다.

### 중요한 점
worktree가 단순히 “존재”하는 것과, 실제 agent가 “작동 가능한 상태”인 것은 다르다.

### 꼭 배워야 하는 점
- worktree bootstrap
- env file 복사
- dependency install
- tool config 복사
- 즉시 runnable 상태까지 끌고 가는 운영 감각

### 우리 설계에 가져와야 하는 것
- orchestrator launch 전 preflight에서 runnable 여부를 봐야 함
- `.env`나 config 없어서 session만 뜨고 worker가 즉시 실패하는 케이스를 줄여야 함
- launch는 “세션 생성”이 아니라 “실행 준비 완료 + worker 시작”이어야 함

---

## 6.6 `kosho`
- URL: `https://github.com/carlsverre/kosho`

### 무엇을 하는 도구인가
repo-local metadata와 hooks를 활용하는 lightweight concurrent worktree CLI다.

### 중요한 점
repo 내부에 관리 디렉토리를 두고 lifecycle을 명료하게 만드는 설계가 좋다.

### 꼭 배워야 하는 점
- repo-local registry
- create hook
- run hook
- prune semantics
- 환경 변수 기반 hook context 전달

### 우리 설계에 가져와야 하는 것
- `.codex/` 아래 registry를 두는 접근
- create/run/pre-launch hook 설계
- cleanup과 prune 분리

---

## 6.7 `codex-cli-farm`
- URL: `https://github.com/waskosky/codex-cli-farm`

### 무엇을 하는 도구인가
Codex CLI를 tmux에서 장기 운영하고, centralized logging, unified monitoring, snapshot/restore를 제공하는 farm 구조다.

### 이 레퍼런스가 가장 직접적인 이유
이름 그대로 `Codex + tmux + monitoring` 문제를 다룬다.

### 꼭 배워야 하는 점
- long-lived sessions
- 개별 로그 파일
- 통합 모니터링
- manifest snapshot/restore
- main session + board session 구분

### 우리 설계에 가져와야 하는 것
- session은 일회성보다 장기 생존과 복구를 고려해야 함
- 로그 파일은 pane 단위/attempt 단위로 안정적으로 분리되어야 함
- 상태 재구성에 snapshot/manifest 사고가 유용함

### 그대로 가져오면 안 되는 것
- 이 도구는 Codex farm 운영 자체가 중심이다
- 우리는 `dispatch` 기반 launch semantics가 중심이다
- 그래서 “window first”가 아니라 “dispatch first”여야 한다

---

## 6.8 `commander`
- URL: `https://github.com/autohandai/commander`

### 무엇을 하는 도구인가
여러 CLI coding agent를 local worktree 기반으로 orchestration하는 commander center다.

### 꼭 배워야 하는 점
- multi-agent control plane
- worktree under project-local hidden dir
- live streaming
- project lifecycle management
- branch/status metadata persistence

### 우리 설계에 가져와야 하는 것
- 나중에 중앙 관제형 구조로 확장 가능하도록 registry 설계
- session summary와 project metadata 연동 가능성
- local-first orchestration

---

## 6.9 `cmux`
- URL: `https://github.com/manaflow-ai/cmux`
- URL: `https://github.com/coder/cmux`

### 무엇을 하는 도구인가
병렬 coding agent 실행을 위한 중앙 orchestration/product 계층을 제공한다.

### 중요한 점
세션을 단순 terminal pane이 아니라 **검증 가능한 isolated workspace execution**으로 본다.

### 꼭 배워야 하는 점
- 여러 coding CLIs를 동시에 다룸
- parallel task execution
- central overview
- restart/resume UX
- isolated workspace discipline

### 우리 설계에 가져와야 하는 것
- runtime registry 설계
- cross-session status summary
- 실패 후 resume 흐름
- 단순 launch가 아니라 lifecycle 전체를 보는 시야

---

## 6.10 `phantom`
- URL: `https://github.com/aku11i/phantom`

### 무엇을 하는 도구인가
parallel development용 worktree CLI이며 tmux, editor, AI launch를 가볍게 연결한다.

### 꼭 배워야 하는 점
- worktree path를 기억하기 쉬운 규칙으로 중앙 관리
- `phantom ai` 같은 직관적 command surface
- `exec`, `shell`, `tmux`를 명확히 분리

### 우리 설계에 가져와야 하는 것
- v0.1 command surface는 작고 명확해야 함
- branch/worktree/session 이름은 사람이 외울 수 있어야 함
- operator UX는 복잡한 config보다 강한 convention이 유리함

---

## 6.11 `claude-squad`
- URL: `https://github.com/smtg-ai/claude-squad`

### 무엇을 하는 도구인가
여러 terminal agent를 분리된 workspace에서 관리하는 terminal app이다.

### 중요한 점
background 작업, review-before-apply, isolated workspace를 한 번에 다룬다.

### 우리 설계에 주는 시사점
- long-running agent를 foreground 도구처럼 취급하면 안 된다
- review 가능한 intermediate state가 중요하다
- background worker orchestration이 핵심이다

---

## 7. 최종적으로 받아들여야 할 설계 결론

위 reference를 종합하면 `codex-tmux-orchestrator`는 아래 원칙을 따라야 한다.

1. launch의 출발점은 `dispatch`다
2. session 이름은 deterministic 해야 한다
3. `tmux session exists`와 `Codex worker is healthy`를 분리해야 한다
4. heartbeat와 marker protocol이 필요하다
5. registry 파일이 canonical source여야 한다
6. cleanup과 restart는 1급 기능이어야 한다
7. wrong-worktree, duplicate-launch, stale-runtime을 초기에 강하게 막아야 한다
8. bootstrap / preflight / hooks는 launch보다 먼저 검증돼야 한다
9. v0.1은 작게 시작하되 runtime contract는 처음부터 제대로 고정해야 한다

---

## 8. 책임 경계

### 8.1 `codex-task-packet`이 소유하는 것
- `task_id`
- `goal`
- `why`
- `allowed_paths`
- `forbidden_paths`
- `context_files`
- `done_definition`
- `required_checks`
- `deliverables`
- `revision`

### 8.2 `codex-worktree-dispatch`가 소유하는 것
- `dispatch_id`
- `task_id`
- `branch`
- `worktree_path`
- `assigned_agent`
- `locked_paths`
- `status`
- `history`
- `retry_count`
- `merge_target`

### 8.3 `codex-tmux-orchestrator`가 소유하는 것
- `session_name`
- `session_socket`
- `launch_command`
- `attempt_number`
- `runtime_status`
- `log_path`
- `heartbeat_path`
- `registry_path`
- `started_at`
- `last_seen_at`
- `restart_count`
- `exit_code`
- `exit_reason`
- `marker_protocol_version`

### 8.4 `codex-session-monitor`가 소유할 것
- read-only dashboards
- stale detection summaries
- aggregated status views
- alerts / anomalies

### 8.5 이 Skill이 절대 소유하면 안 되는 것
- task goal 원문 수정
- worktree canonical assignment 수정
- path overlap resolution 로직의 최종 소유권
- merge readiness의 최종 판정
- acceptance grade

---

## 9. Launch 전제 조건

`codex-tmux-orchestrator`는 아래 전제가 충족되지 않으면 launch를 거부해야 한다.

1. packet file이 존재한다
2. dispatch file이 존재한다
3. dispatch status가 `ready`다
4. dispatch가 가리키는 worktree가 실제 존재한다
5. 해당 worktree가 올바른 git repo다
6. 현재 branch가 dispatch branch와 일치한다
7. packet revision mismatch가 없다
8. log path collision이 없다
9. 기존 active runtime collision이 없다
10. lock conflict가 없다
11. Codex CLI command preset이 resolve 가능하다
12. session name collision이 없다

이 중 하나라도 실패하면 `planned -> launching` 전환을 하면 안 된다.

---

## 10. Runtime Registry 설계

### 10.1 왜 registry가 필요한가
아래 둘은 충분하지 않다.

- `tmux ls`
- log file grep

이유:
- tmux session이 살아 있어도 worker가 실패했을 수 있다
- log file만으로는 canonical current state를 재구성하기 어렵다
- restart와 cleanup에서 lineage를 추적하기 어렵다

### 10.2 추천 디렉토리 구조
- `.codex/runtime/`
- `.codex/runtime/<dispatch_id>.json`
- `.codex/logs/`
- `.codex/logs/<dispatch_id>-attempt-001.log`
- `.codex/heartbeats/`
- `.codex/heartbeats/<dispatch_id>.json`
- `.codex/sessions/`
- `.codex/sessions/<session_name>.json`

### 10.3 runtime record가 포함해야 하는 것
- `runtime_version`
- `task_id`
- `dispatch_id`
- `packet_revision`
- `branch`
- `worktree_path`
- `session_name`
- `socket_name`
- `launch_command`
- `attempt_number`
- `runtime_status`
- `started_at`
- `last_seen_at`
- `completed_at`
- `exit_code`
- `exit_reason`
- `log_path`
- `heartbeat_path`
- `marker_protocol_version`
- `restart_count`
- `previous_attempts`
- `notes`

### 10.4 설계 규칙
- 하나의 dispatch에는 canonical runtime record 하나만 있어야 한다
- attempt history는 그 파일 안에서 누적 관리하는 편이 낫다
- log는 attempt별 파일로 분리하는 편이 낫다
- heartbeat는 overwrite 방식 단일 파일이 실용적이다

---

## 11. Marker Protocol

### 11.1 왜 필요한가
단순 문자열 `DONE` 같은 것은 false positive를 만들기 쉽다.  
또 `tmux wait`만 믿으면 shell은 살아 있고 worker는 죽은 상태를 놓칠 수 있다.

### 11.2 권장 마커
- `__CODEX_ORCH_START__:<dispatch_id>:<attempt>:<timestamp>`
- `__CODEX_ORCH_HEARTBEAT__:<dispatch_id>:<attempt>:<timestamp>`
- `__CODEX_ORCH_DONE__:<dispatch_id>:<attempt>:<exit_code>:<timestamp>`
- `__CODEX_ORCH_FAIL__:<dispatch_id>:<attempt>:<reason>:<timestamp>`

### 11.3 규칙
- 모든 marker는 `dispatch_id`를 포함해야 한다
- 모든 marker는 `attempt_number`를 포함해야 한다
- 종료 marker 없이는 `completed`로 판정하면 안 된다
- heartbeat는 log와 heartbeat file 둘 다에 반영하는 편이 유리하다
- 사람이 쳐 넣을 수 있는 흔한 문자열은 쓰면 안 된다

---

## 12. Heartbeat 설계

### 12.1 왜 heartbeat가 필요한가
세션 존재 = worker health가 아니다.

예:
- tmux session은 살아 있다
- shell prompt도 남아 있다
- 그런데 Codex CLI는 인증 실패로 바로 죽었다
- operator는 여전히 `running`으로 착각한다

이 상황을 막으려면 heartbeat가 필요하다.

### 12.2 heartbeat file 추천 구조
- `dispatch_id`
- `attempt_number`
- `session_name`
- `last_seen_at`
- `last_marker`
- `pid_or_tmux_identity`
- `status_hint`

### 12.3 heartbeat timeout 정책
v0.1 기준 추천:
- short timeout: `90s`
- long-running tolerate timeout: `300s`
- stale transition은 timeout과 session existence를 함께 본다

### 12.4 stale 판정 조건 예시
- tmux session 없음 -> 즉시 stale 또는 failed
- tmux session 있음 + heartbeat timeout 초과 -> stale
- heartbeat 있음 + done marker 있음 -> completed
- heartbeat 없음 + launch 직후 매우 짧은 시간 -> launching 유지

---

## 13. 상태 머신

### 13.1 추천 상태
- `planned`
- `launching`
- `running`
- `waiting_input`
- `completed`
- `failed`
- `stale`
- `killed`
- `abandoned`
- `archived`

### 13.2 상태 의미
- `planned`: runtime record만 있고 아직 launch 전
- `launching`: session 생성과 command dispatch 중
- `running`: session과 heartbeat가 확인된 상태
- `waiting_input`: Codex가 사용자 입력 대기 또는 interactive block 상태
- `completed`: 종료 marker와 exit code가 정상적으로 기록됨
- `failed`: launch 실패 또는 runtime 실패가 명시적으로 기록됨
- `stale`: session/heartbeat 불일치로 건강 상태 불명
- `killed`: 운영자가 session을 종료시킴
- `abandoned`: task를 더 진행하지 않기로 결정
- `archived`: 완료/실패 후 보관 상태

### 13.3 허용 전이
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
- `failed -> archived`
- `killed -> archived`

### 13.4 금지 전이
- `planned -> completed`
- `planned -> running`
- `failed -> completed`
- `archived -> running`
- `running -> planned`

---

## 14. Launch Contract

### 14.1 입력
- `task_id`
- `dispatch_id`
- `packet_path`
- `dispatch_path`
- `worktree_path`
- `branch`
- `session_name`
- `codex_command_template`
- `launch_mode`
- `log_path`
- `heartbeat_path`
- `attempt_number`

### 14.2 출력
- `runtime_status`
- `session_name`
- `socket_name`
- `started_at`
- `last_seen_at`
- `exit_code`
- `exit_reason`
- `log_path`
- `heartbeat_path`
- `registry_path`

### 14.3 launch 절차
1. packet read
2. dispatch read
3. schema validate
4. dispatch readiness validate
5. branch/worktree validate
6. runtime collision validate
7. log path allocate
8. runtime registry create
9. tmux session create
10. launch marker write
11. Codex command send
12. first heartbeat 확인
13. `launching -> running` 전환
14. failure 시 rollback 또는 failed record finalize

---

## 15. 실제 launch 시퀀스 상세안

### 15.1 preflight 단계
- packet 존재 확인
- dispatch 존재 확인
- packet revision 기록
- dispatch status 확인
- worktree 경로 존재 확인
- `git rev-parse --show-toplevel` 확인
- `git branch --show-current` 확인
- branch mismatch면 즉시 실패
- 현재 dispatch에 active runtime 있는지 확인
- session name 충돌 확인
- log file path 충돌 확인
- heartbeat file previous stale 여부 확인

### 15.2 runtime bootstrap 단계
- attempt number 증가
- runtime JSON 생성
- log file allocate
- heartbeat file initialize
- start marker 생성
- session 생성 또는 재활용 정책 결정
- Codex command compose
- non-ASCII path quote 처리
- command send

### 15.3 verification 단계
- tmux session 존재 확인
- 첫 output capture
- heartbeat first write 확인
- launch success marker 확인
- `launching -> running` 상태 전환

### 15.4 steady-state 단계
- periodic status refresh
- heartbeat 갱신
- operator status 출력 지원
- stale timeout 검사

### 15.5 completion 단계
- done marker 확인
- exit code 기록
- runtime JSON finalize
- `running -> completed` 또는 `failed`
- cleanup candidate 상태로 표시

---

## 16. 실패 패턴 분류

### 16.1 launch 이전 실패
#### packet 없음
영향:
- task provenance 자체가 없음

#### dispatch 없음
영향:
- worktree and status provenance 없음

#### dispatch not ready
영향:
- dependency 미충족 또는 overlap unresolved 상태에서 launch 발생

#### worktree 없음
영향:
- wrong path, stale dispatch, cleanup mismatch

#### branch mismatch
영향:
- 잘못된 코드 공간에서 작업 시작

#### session name collision
영향:
- 기존 live session 덮어쓰기 위험

#### log path collision
영향:
- 로그 오염

### 16.2 launch 중 실패
#### tmux session create 실패
원인:
- socket 권한
- naming collision
- tmux unavailable

#### command send 실패
원인:
- quoting 오류
- non-ASCII path
- shell escape 오류

#### Codex CLI start 실패
원인:
- codex not installed
- auth 미완료
- flag mismatch
- network restrictions

#### first heartbeat 미도착
원인:
- Codex start 즉시 종료
- shell만 살아 있음
- marker protocol 문제

### 16.3 running 중 실패
#### session 살아 있으나 worker dead
대응:
- heartbeat timeout -> stale

#### log가 남지 않음
대응:
- registry에는 있지만 디버깅 불가
- launch contract 위반

#### duplicate runtime
대응:
- 동일 dispatch 두 세션 발생
- 강제 uniqueness 필요

#### wrong-worktree relaunch
대응:
- 재시작 시 preflight를 생략하면 발생
- restart도 launch와 동일 검증 필요

### 16.4 completion 실패
#### done marker 없이 종료
대응:
- failed 또는 stale로 남겨야 함
- completed 금지

#### exit code 없는 종료
대응:
- runtime failed로 남기고 reason에 protocol mismatch 기록

### 16.5 cleanup 실패
#### session만 죽이고 registry 남김
영향:
- ghost active runtime

#### registry만 지우고 tmux는 남김
영향:
- zombie worker

#### heartbeat만 남음
영향:
- stale false positive

---

## 17. 이 프로젝트에서 특히 중요한 로컬 실패 포인트

이 프로젝트 경로에는 한글과 공백에 가까운 구간이 있다.  
따라서 아래 문제가 실제로 중요하다.

### 17.1 non-ASCII path quoting
예:
- `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/...`

영향:
- shell command compose 실패
- tmux send-keys quoting 실패
- Codex launch path resolution 실패

대응:
- 모든 launch command는 shell-safe quoting 강제
- path를 직접 문자열 이어붙이기 하지 말 것
- session launch 전에 `pwd` 확인 절차 추가

### 17.2 sandbox / permission mismatch
내부 troubleshooting에서 이미 드러난 패턴:
- worktree spawn은 sandbox에서 막힐 수 있음
- long-running CLI가 network 제한에 걸릴 수 있음

대응:
- orchestrator는 spawn 자체를 소유하지 않고 pre-created worktree를 전제로 해야 함
- network-required Codex mode는 preflight에 명시해야 함

### 17.3 marker false positive
내부 `tmux-controller` troubleshooting에서 중요했던 포인트:
- 너무 일반적인 문자열을 wait 패턴으로 쓰면 오판한다

대응:
- dispatch-specific marker를 강제
- marker protocol을 버전 포함으로 설계

### 17.4 stale session 잔존
내부 `tmux-controller`와 `worktree-parallel` troubleshooting을 합치면,
가장 흔한 운영 실패는 “세션은 정리됐는데 상태 파일이 남거나, 상태 파일은 정리됐는데 세션이 남는” 식의 반쪽 cleanup이다.

대응:
- cleanup은 항상 4자 정합성을 봐야 함
- session
- runtime registry
- heartbeat
- log reference

---

## 18. v0.1 범위

v0.1은 반드시 작게 잡아야 한다.

### 필수 포함
- dispatch 기반 launch
- deterministic session naming
- session create
- Codex command send
- log file allocate
- heartbeat file allocate
- runtime registry 생성
- `status` 조회
- restart 1회
- stale cleanup
- launch preflight
- duplicate launch 방지
- wrong worktree 방지

### 제외
- multi-project overview
- interactive dashboard
- advanced queue scheduler
- auto issue sync
- acceptance grading
- merge automation
- fan-out planning
- full TUI

---

## 19. v0.2 범위

### 추가 가능
- batch launch
- priority ordering
- dependency-aware queue release
- grouped status
- configurable retry policy
- post-completion hooks
- per-model command presets
- board session summary

---

## 20. v0.3 범위

### 추가 가능
- multi-project orchestration
- session-monitor deep integration
- central view on git divergence
- adaptive restart policy
- pause/resume semantics
- container/devcontainer execution target
- richer audit trail and trace viewer

---

## 21. 이 Skill이 직접 만들지 말아야 할 것

초기 구현에서 유혹적이지만 분리해야 하는 것:

- 자체 task packet authoring
- 자체 dispatch planner
- 자체 worktree spawn engine
- 자체 acceptance gate engine
- 자체 code review UI
- PR creation orchestration 전부
- complex dashboard frontend

하나의 Skill에 planning, dispatch, runtime, monitor, grading을 다 넣으면 실패한다.

---

## 22. 구현 전에 반드시 고정해야 할 설계 항목

1. session naming 규칙
2. runtime registry path
3. log file naming 규칙
4. heartbeat format
5. stale timeout 기준
6. marker protocol
7. attempt numbering 규칙
8. restart allowed conditions
9. duplicate session 처리 규칙
10. cleanup idempotency 규칙
11. dispatch revision mismatch 처리 규칙
12. human-readable status 출력 형식
13. machine-readable status JSON 형식
14. Codex CLI command preset 위치
15. shell quoting 전략

---

## 23. 구현 시 필요한 하위 문서

### 반드시 필요
- `LAUNCH_CONTRACT.md`
- `SESSION_STATE_MACHINE.md`
- `RUNTIME_REGISTRY_SCHEMA.md`
- `MARKER_PROTOCOL.md`
- `HEARTBEAT_POLICY.md`
- `FAILURE_CASES.md`
- `RESTART_POLICY.md`
- `CLEANUP_RULES.md`

### 있으면 좋은 것
- `COMMAND_PRESETS.md`
- `MULTI_PROJECT_FUTURE.md`
- `STATUS_OUTPUT_SPEC.md`

---

## 24. 구현 시 필요한 scripts

### 필수
- `orchestrator_preflight.py`
- `orchestrator_launch.py`
- `orchestrator_status.py`
- `orchestrator_restart.py`
- `orchestrator_cleanup.py`
- `orchestrator_registry_validate.py`
- `orchestrator_markers.py`

### 권장
- `orchestrator_tail.py`
- `orchestrator_watch.py`
- `orchestrator_repair.py`

---

## 25. 최종 설계 판단

`codex-tmux-orchestrator`를 제대로 만들려면, 이 Skill을 `tmux helper`로 생각하면 안 된다.  
반드시 아래처럼 봐야 한다.

- 입력은 `task-packet`과 `dispatch`
- 실행 기반은 `tmux-controller`
- 배치 기반은 `worktree-parallel`
- 출력은 `session + log + heartbeat + runtime registry`
- 목적은 “Codex CLI를 안전하게 병렬 실행하는 것”
- 핵심 실패 방지 대상은 `wrong-worktree`, `duplicate-launch`, `stale-runtime`, `marker-false-positive`

즉 이 Skill의 성공 기준은 “tmux 세션을 만들 수 있다”가 아니다.  
정확한 성공 기준은 다음과 같다.

1. 올바른 dispatch만 launch 한다
2. 올바른 worktree에서만 launch 한다
3. 실행 상태를 파일 registry로 복구 가능하게 남긴다
4. stale와 duplicate를 조기에 탐지한다
5. restart와 cleanup이 일관되게 동작한다

---

## 26. 우선 채택할 Reference 우선순위

### 1순위
- `par`
- `ccmanager`
- 내부 `tmux-controller`
- 내부 `worktree-parallel`

### 2순위
- `codex-cli-farm`
- `emdash`
- `gwq`

### 3순위
- `agentree`
- `kosho`
- `phantom`
- `commander`
- `cmux`
- `coder/mux`
- `claude-squad`

---

## 27. Source Map

### Local References
- `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/tmux-controller/SKILL.md`
- `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/tmux-controller/references/troubleshooting.md`
- `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/worktree-parallel/SKILL.md`
- `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/worktree-parallel/references/troubleshooting.md`

### GitHub / Web References
- `https://github.com/coplane/par`
- `https://github.com/kbwo/ccmanager`
- `https://github.com/generalaction/emdash`
- `https://github.com/d-kuro/gwq`
- `https://github.com/AryaLabsHQ/agentree`
- `https://github.com/carlsverre/kosho`
- `https://github.com/waskosky/codex-cli-farm`
- `https://github.com/autohandai/commander`
- `https://github.com/manaflow-ai/cmux`
- `https://github.com/coder/cmux`
- `https://github.com/aku11i/phantom`
- `https://github.com/smtg-ai/claude-squad`
