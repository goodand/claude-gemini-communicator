아래 체크리스트는 codex-worktree-dispatch 구현이 레퍼런스 GitHub 자료들과 기능적으로 정합한지 판단하기 위한 기준이
  다.
  기준은 “1:1 복제”가 아니라 핵심 설계 의도와 운영 기능이 동등한가다.

  참조 축
  | Reference | 핵심 시사점 | dispatch에 반영할 축 |
  |---|---|---|
  | emdash | task/ticket를 에이전트와 worktree에 배정하고 fan-out/fan-in 한다 | task-to-worktree 매핑, review/merge
  gate |
  | par | label 중심으로 branch/worktree/session을 함께 관리한다 | deterministic naming, registry, dispatch launch
  metadata |
  | ccmanager | 상태 감지, hook, multi-project, worktree lifecycle 관리 | state machine, hooks, project scope |
  | git-worktree-toolbox | new/archive/prompt/doctor/clean lifecycle | archive/doctor/cleanup/pr-resume metadata |
  | agentree | env 복사, deps 설치, AI config bootstrap | post-create bootstrap hooks |
  | gwq | global discovery, status watch, tmux/task queue | global registry, watchable status |
  | kosho | repo-local .kosho/ registry와 create hook | repo-local metadata dir, hooks, prune |

  정합성 판정 원칙

  - codex-worktree-dispatch는 worktree 생성기만이어서는 안 된다.
  - 최소한 task 배정 + 상태 관리 + 충돌 방지 + merge readiness + cleanup까지 가져야 한다.
  - tmux 실행 자체는 codex-tmux-orchestrator의 책임이지만, dispatch는 그 실행을 위한 launchable metadata를 제공해야
    한다.
  - 구현 범위를 v0.1 필수, v0.2 권장, v0.3 확장으로 나눠 평가하는 게 맞다.

  ———

  # codex-worktree-dispatch 정합성 체크리스트

  ## A. 정체성 / 책임 경계

  - [ ] codex-worktree-dispatch가 task packet을 읽어 배치 상태 객체를 생성하는 책임을 가진다.
  - [ ] goal, why, done_definition의 원문 소유권은 task-packet에 있고, dispatch는 이를 중복 저장하지 않는다.
  - [ ] branch, worktree_path, assigned_agent, status, locked_paths의 소유권은 dispatch에 있다.
  - [ ] dispatch가 session 실행기가 아니라는 점이 코드와 문서에 명확하다.
  - [ ] 반대로, dispatch가 단순 메모 파일이 아니라 운영 상태의 canonical source라는 점이 명확하다.
  - [ ] dispatch는 정확히 하나의 task_id만 참조한다.
  - [ ] dispatch는 정확히 하나의 branch와 하나의 worktree_path만 가진다.
  - [ ] dispatch는 런타임 세션이 없어도 존재할 수 있다.
  - [ ] dispatch는 task-packet 없는 상태로 생성될 수 없다.
  - [ ] dispatch와 tmux session은 1:1일 수도, 1:0일 수도 있지만 1:N은 금지하거나 명시적으로 문서화되어 있다.

  ## B. 식별자 / 네이밍 / 레지스트리

  - [ ] dispatch_id 규칙이 deterministic 하거나 충돌 없이 생성된다.
  - [ ] task_id -> branch -> worktree_path 매핑 규칙이 일관적이다.
  - [ ] branch naming 규칙이 명시돼 있다. 예: feat/codex-<slug>.
  - [ ] worktree path naming 규칙이 명시돼 있다. 예: .worktrees/<slug>.
  - [ ] registry 저장 위치가 명시돼 있다. 예: .codex/dispatch/.
  - [ ] repo-local registry 전략인지, global registry 전략인지 명확하다.
  - [ ] repo-local registry를 쓰면 kosho처럼 repo 내부 metadata 디렉토리를 가진다.
  - [ ] global discovery를 쓰면 gwq처럼 filesystem scan 또는 multi-project discovery 전략이 있다.
  - [ ] 같은 task_id로 중복 dispatch 생성 시 정책이 있다.
  - [ ] 같은 branch 이름 충돌 시 정책이 있다.
  - [ ] 같은 worktree path 충돌 시 정책이 있다.
  - [ ] rename/retry/reopen 시 idempotent 동작이 정의돼 있다.

  ## C. task-packet 입력 정합성

  - [ ] dispatch 생성 전에 task-packet schema validation을 강제한다.
  - [ ] allowed_paths가 비어 있으면 dispatch 생성이 실패한다.
  - [ ] forbidden_paths가 allowed_paths와 충돌하면 dispatch 생성이 실패한다.
  - [ ] depends_on이 있는 task는 dependency graph를 읽는다.
  - [ ] parallel_group이 있으면 dispatch metadata에 보존한다.
  - [ ] priority가 있으면 dispatch ordering에 반영된다.
  - [ ] deliverables가 있으면 merge readiness 판단에 반영된다.
  - [ ] required_checks가 있으면 complete 전환 전에 검증된다.
  - [ ] packet revision mismatch를 감지할 수 있다.
  - [ ] packet이 갱신되면 stale dispatch를 감지할 수 있다.

  ## D. worktree 생성 / 연결

  - [ ] 실제 git worktree add를 수행하거나, 하위 툴을 감싸더라도 성공/실패 return code를 엄격히 확인한다.
  - [ ] 생성 성공 전에 상태 파일을 쓰지 않는다.
  - [ ] 생성 실패 시 orphan dispatch/state가 남지 않는다.
  - [ ] worktree 생성 후 branch checkout 결과를 확인한다.
  - [ ] 생성된 worktree가 실제 git worktree list에 나타나는지 검증한다.
  - [ ] 기존 worktree가 이미 있으면 재사용/실패/repair 중 하나의 정책이 있다.
  - [ ] .gitignore에 worktree 관련 디렉토리 예외 처리가 문서화돼 있다.
  - [ ] agentree처럼 post-create bootstrap 훅을 붙일 수 있다.
  - [ ] bootstrap이 없어도 최소 기능은 동작한다.
  - [ ] bootstrap은 dispatch 본체와 분리된 선택 기능으로 설계돼 있다.

  ## E. 경로 점유 / 충돌 방지

  - [ ] locked_paths 개념이 있다.
  - [ ] locked_paths는 allowed_paths보다 넓을 수 없다.
  - [ ] path overlap 검사기가 있다.
  - [ ] 동일 파일 겹침뿐 아니라 상위 디렉토리 prefix 충돌도 잡는다.
  - [ ] 충돌 dispatch는 ready 또는 running으로 갈 수 없다.
  - [ ] 병렬 그룹이라도 path overlap이 있으면 동시에 돌리지 않는다.
  - [ ] overlap 검사 로직이 worktree 내부 상태와 별개로 registry 기준으로 동작한다.
  - [ ] resolved/abandoned/merged 상태가 되면 해당 path lock이 해제된다.
  - [ ] 강제 override가 있더라도 history에 남는다.
  - [ ] symlink나 path traversal(..) 악용을 막는다.

  ## F. 상태 머신 / 상태 전이

  - [ ] 상태 집합이 명확하다. 예: queued, ready, running, blocked, failed, complete, merged, abandoned.
  - [ ] 허용 상태 전이 표가 있다.
  - [ ] invalid transition을 validator가 막는다.
  - [ ] queued -> ready 전환에 dependency 충족 조건이 있다.
  - [ ] ready -> running 전환에 worktree/session 준비 조건이 있다.
  - [ ] running -> complete 전환에 required checks 통과 조건이 있다.
  - [ ] complete -> merged 전환에 merge confirmation 조건이 있다.
  - [ ] failed -> ready 재시도 전환 조건이 있다.
  - [ ] blocked 상태를 수동/자동 모두 지원할지 정책이 있다.
  - [ ] 각 상태 전이에 reason, at, by가 남는다.
  - [ ] state history가 append-only로 유지된다.
  - [ ] 현재 상태와 history가 서로 모순되지 않는다.

  ## G. agent 할당 / 런타임 준비

  - [ ] assigned_agent 또는 assigned_worker 필드가 있다.
  - [ ] owner_model 또는 runtime_type 필드가 있다. 예: codex, claude-code, gemini-cli.
  - [ ] launch_command_hint 또는 동등한 필드가 있다.
  - [ ] tmux_session_hint 또는 동등한 필드가 있다.
  - [ ] 아직 세션이 안 떠도 dispatch는 유효하다.
  - [ ] 세션이 뜬 이후 연결할 필드가 예약돼 있다. 예: session_id, log_path, heartbeat_path.
  - [ ] 런타임 세부정보가 없더라도 merge-check는 돌아간다.
  - [ ] launch metadata가 packet 원문을 오염시키지 않는다.
  - [ ] par처럼 label 기반으로 session/worktree naming을 일관되게 만들 수 있다.
  - [ ] emdash처럼 task/ticket source와 agent assignment를 연결할 수 있다.

  ## H. hook / bootstrap / 자동화

  - [ ] worktree create 후 hook을 실행할 수 있다.
  - [ ] 상태 전이 후 hook을 실행할 수 있다.
  - [ ] hook 실패가 dispatch 본체를 손상시키지 않는다.
  - [ ] env 복사 hook을 둘 수 있다.
  - [ ] dependency install hook을 둘 수 있다.
  - [ ] AI tool config 복사 hook을 둘 수 있다.
  - [ ] IDE/editor open hook을 둘 수 있다.
  - [ ] notify hook을 둘 수 있다.
  - [ ] hook 결과 로그를 남긴다.
  - [ ] ccmanager의 status hooks, kosho의 create hook, agentree의 bootstrap 개념 중 어떤 것을 채택했는지 명시돼 있다.

  ## I. merge readiness / review gate

  - [ ] merge-check 서브커맨드 또는 동등 기능이 있다.
  - [ ] status=complete가 아니면 merge-check가 실패한다.
  - [ ] dirty worktree면 merge-check가 실패한다.
  - [ ] branch가 실제 존재하지 않으면 merge-check가 실패한다.
  - [ ] base branch와의 충돌 가능성을 검사한다.
  - [ ] required deliverables가 없으면 merge-check가 실패한다.
  - [ ] required checks 결과가 없으면 merge-check가 실패한다.
  - [ ] merged 후 상태를 merged로 전환하는 절차가 있다.
  - [ ] emdash처럼 fan-in 이전 review/reconciliation 단계가 있다.
  - [ ] git-worktree-toolbox처럼 PR/changes lifecycle로 연결 가능한 metadata가 있다.

  ## J. archive / cleanup / doctor

  - [ ] 완료된 dispatch를 archive할 수 있다.
  - [ ] archive가 packet 원본을 삭제하지 않는다.
  - [ ] cleanup이 worktree, branch, state file을 일관되게 정리한다.
  - [ ] orphan state file을 정리할 수 있다.
  - [ ] orphan worktree를 감지할 수 있다.
  - [ ] dispatch가 가리키는 worktree가 사라졌을 때 doctor/repair가 가능하다.
  - [ ] branch는 있는데 worktree가 없는 경우를 탐지한다.
  - [ ] worktree는 있는데 registry가 없는 경우를 탐지한다.
  - [ ] stale dispatch를 탐지한다.
  - [ ] git-worktree-toolbox의 doctor/clean/archive, kosho의 prune와 기능적으로 대응된다.

  ## K. multi-project / 전역 운영성

  - [ ] 단일 repo 전용인지 multi-project를 지원하는지 명확하다.
  - [ ] multi-project 모드가 있으면 project root 식별 규칙이 있다.
  - [ ] project별 dispatch namespace가 분리된다.
  - [ ] 전역 list/status가 가능하다.
  - [ ] repo-local 상태와 global overview가 함께 가능하다.
  - [ ] ccmanager처럼 여러 repo를 한 화면/한 CLI에서 다룰 수 있는 확장 여지가 있다.
  - [ ] gwq처럼 global discovery 전략이 있거나 명시적으로 범위를 제한한다.
  - [ ] 전역 명령이 repo 경계를 넘는 path lock 충돌을 어떻게 처리하는지 정의돼 있다.
  - [ ] 상태 파일 경로에 project identity가 반영된다.
  - [ ] archive/cleanup가 다른 project 상태를 오염시키지 않는다.

  ## L. 관측 가능성 / 모니터링 준비도

  - [ ] dispatch 상태를 기계적으로 읽을 수 있다.
  - [ ] 사람이 읽을 수 있는 summary 출력도 있다.
  - [ ] status --watch 또는 watch-friendly 출력 형식이 있다.
  - [ ] future monitor를 위한 last_seen_at, heartbeat_path, log_path 자리가 있다.
  - [ ] monitor가 dispatch를 canonical source로 삼을 수 있다.
  - [ ] status 출력이 queued/ready/running/blocked/failed/complete를 구분한다.
  - [ ] blockers를 구조적으로 출력한다.
  - [ ] assignment와 worktree 경로를 함께 보여준다.
  - [ ] 최근 상태 전이 시각을 보여준다.
  - [ ] gwq status --watch, ccmanager의 session state UI와 기능적으로 유사한 관측 가능성을 목표로 한다.

  ## M. CLI / UX 정합성

  - [ ] 최소 명령 집합이 있다. 예: new, status, validate, check-overlap, merge-check, archive, cleanup, doctor.
  - [ ] 명령명이 일관적이다.
  - [ ] dry-run 옵션이 있다.
  - [ ] 실패 시 stderr와 exit code가 일관적이다.
  - [ ] machine output JSON 옵션이 있다.
  - [ ] human summary 출력이 있다.
  - [ ] --project, --task, --dispatch-id 같은 선택자 체계가 있다.
  - [ ] non-interactive 사용이 가능하다.
  - [ ] deterministic output이 가능하다.
  - [ ] help 텍스트가 packet/dispatch/orchestrator 책임 경계를 설명한다.

  ## N. 테스트 / 검증

  - [ ] packet 없는 dispatch 생성 실패 테스트가 있다.
  - [ ] invalid state transition 실패 테스트가 있다.
  - [ ] overlap 감지 테스트가 있다.
  - [ ] dependency gate 테스트가 있다.
  - [ ] worktree 생성 실패 시 orphan state 미생성 테스트가 있다.
  - [ ] cleanup이 orphan file을 정리하는 테스트가 있다.
  - [ ] merge-check success/failure 테스트가 있다.
  - [ ] archive 후 packet 보존 테스트가 있다.
  - [ ] stale revision mismatch 테스트가 있다.
  - [ ] branch/path naming deterministic 테스트가 있다.
  - [ ] multi-project scope 테스트가 있다.
  - [ ] hook failure isolation 테스트가 있다.
  - [ ] doctor가 metadata inconsistency를 감지하는 테스트가 있다.
  - [ ] JSON schema validation 테스트가 있다.
  - [ ] snapshot test 또는 golden output test가 있다.

  ## O. 문서 / 운영 규약

  - [ ] SKILL.md가 언제 이 스킬을 써야 하는지 명확히 말한다.
  - [ ] packet과 dispatch의 차이를 SKILL.md가 직접 설명한다.
  - [ ] reference 문서가 분리돼 있다.
  - [ ] 상태 머신 문서가 있다.
  - [ ] overlap 규칙 문서가 있다.
  - [ ] merge gate 문서가 있다.
  - [ ] cleanup/doctor 문서가 있다.
  - [ ] 미래 tmux-orchestrator와의 연결 규약이 있다.
  - [ ] 미래 session-monitor와의 연결 규약이 있다.
  - [ ] source of truth가 어디인지 문서상 모호하지 않다.

  ———

  # 판정 기준

  ## v0.1 최소 정합

  - [ ] A, B, C, D, E, F, I, N 섹션의 필수 항목이 대부분 충족된다.
  - [ ] 특히 아래 8개는 반드시 충족한다.
  - [ ] packet 없이는 dispatch 생성 불가
  - [ ] deterministic branch/worktree naming
  - [ ] 실제 worktree 생성 성공 전 state 확정 금지
  - [ ] path overlap 감지
  - [ ] dependency gate
  - [ ] valid state machine
  - [ ] merge-check
  - [ ] cleanup/orphan 정리

  ## v0.2 운영 정합

  - [ ] hook/bootstrap, archive/doctor, watchable status가 추가된다.
  - [ ] multi-project 또는 global discovery 전략이 생긴다.
  - [ ] future tmux/session integration 필드가 정리된다.

  ## v0.3 레퍼런스 강정합

  - [ ] par 수준의 branch/worktree/session label 일관성
  - [ ] ccmanager 수준의 상태 감지/후크
  - [ ] git-worktree-toolbox 수준의 doctor/archive/lifecycle
  - [ ] emdash 수준의 task fan-out / review fan-in 흐름
  - [ ] agentree 수준의 bootstrap
  - [ ] gwq 수준의 status watch / global overview
  - [ ] kosho 수준의 repo-local registry/prune 훅

  ———

  # 구현 전에 꼭 결정할 10가지

  - [ ] canonical state file은 .codex/dispatch/*.json로 할 것인가
  - [ ] .agent-status/와의 관계를 어떻게 둘 것인가
  - [ ] global registry를 둘 것인가 repo-local만 둘 것인가
  - [ ] branch naming 규칙을 무엇으로 할 것인가
  - [ ] worktree path root를 어디로 할 것인가
  - [ ] retry는 같은 dispatch를 갱신할 것인가 새 dispatch를 만들 것인가
  - [ ] archive는 soft-delete인지 hard-delete인지
  - [ ] hook 실패 시 상태를 failed로 둘지 blocked로 둘지
  - [ ] merge-check에서 실제 git merge simulation을 할지 여부
  - [ ] future tmux/session metadata를 dispatch에 어느 수준까지 미리 넣을지

  사용한 레퍼런스:
  - generalaction/emdash (https://github.com/generalaction/emdash)
  - coplane/par (https://github.com/coplane/par)
  - kbwo/ccmanager (https://github.com/kbwo/ccmanager)
  - ben-rogerson/git-worktree-toolbox (https://github.com/ben-rogerson/git-worktree-toolbox)
  - AryaLabsHQ/agentree (https://github.com/AryaLabsHQ/agentree)
  - d-kuro/gwq (https://github.com/d-kuro/gwq)
  - carlsverre/kosho (https://github.com/carlsverre/kosho)