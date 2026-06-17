# codex-tmux-orchestrator Implementation Alignment Checklist
- version: `v0.1.0`
- created_at: `2026-03-15`
- purpose: `codex-tmux-orchestrator` 구현이 reference와 knowledge base에 기능적으로 정합한지 판단하기 위한 상세 체크리스트
- scope: `tmux 기반 Codex CLI runtime orchestration`
- based_on:
  - `codex-tmux-orchestrator-reference-2026-03-15-03-12.md`
  - `codex-tmux-orchestrator-knowledge_base-2026-03-15-02-49.md`
  - `tmux-controller/SKILL.md`
  - `worktree-parallel/SKILL.md`

---

## 0. 사용 방법

이 체크리스트는 "기능이 있는가"만 보는 문서가 아니다.  
아래 3가지를 동시에 본다.

1. 구현이 존재하는가
2. 구현이 책임 경계를 지키는가
3. 구현이 reference가 보여준 핵심 failure mode를 실제로 막는가

판정 레벨은 아래처럼 나눈다.

- `L0 Draft`
  - 문서만 있고 실제 코드나 검증이 불충분
- `L1 Testable`
  - 최소 CLI/스크립트/상태 파일이 있고 수동 검증 가능
- `L2 Operational`
  - launch/restart/cleanup/status가 돌아가고 failure handling이 있다
- `L3 Trusted`
  - 실제 tmux + Codex 실험으로 반복 검증됐고 bug pattern이 축적됐다

이 체크리스트는 `v0.1`에서 최소 `L1.5~L2`를 목표로 한다.

---

## 1. Reference 정합성 기준

이 Skill 구현은 아래 reference 축을 어느 정도 충족해야 한다.

| Reference | 구현이 가져와야 하는 핵심 |
|---|---|
| `par` | deterministic naming, worktree-session 결합 UX |
| `ccmanager` | runtime state detection, hooks, multi-session 감각 |
| `codex-cli-farm` | Codex-specific long-lived session, logging, monitoring |
| `kosho` | repo-local registry, cleanup/prune/repair |
| `agentree` | launch 전 runnable workspace preflight |
| `gwq` | human-readable status/watch UX |
| `tmux-controller` | tmux primitive 재사용 |
| `worktree-parallel` | dispatch/worktree ownership 및 merge/cleanup 정합성 |
| `tmux wiki` | tmux session/socket semantics |

정합성 판정 원칙:
- 전체 reference를 복제할 필요는 없다.
- 하지만 각 reference가 대표하는 **핵심 축**은 구현에 반영돼야 한다.
- 구현이 reference보다 단순해도 괜찮지만, 핵심 failure mode를 무시하면 정합하지 않은 것으로 본다.

---

## 2. Identity / Responsibility Alignment

### 2.1 Skill 정체성
- [ ] 이 Skill은 스스로를 `tmux helper`가 아니라 `runtime orchestrator`로 정의한다.
- [ ] 문서에서 `dispatch-first` 실행 모델을 명시한다.
- [ ] 구현이 `task-packet -> dispatch -> runtime launch` 흐름을 전제로 한다.
- [ ] 구현이 `session-first`가 아니라 `dispatch-first`로 설계돼 있다.
- [ ] 단순히 tmux session을 만드는 것만으로 성공 처리하지 않는다.
- [ ] launch 성공과 worker health를 구분한다.
- [ ] runtime registry를 별도로 유지한다.
- [ ] 이 Skill이 worktree canonical ownership을 가져오지 않는다.
- [ ] 이 Skill이 task goal 원문을 수정하지 않는다.
- [ ] 이 Skill이 acceptance grading을 수행하지 않는다.

### 2.2 책임 경계 위반 금지
- [ ] `task-packet` 필드 원문은 읽기 전용이다.
- [ ] `dispatch`의 branch/worktree/locked_paths/status는 읽기 또는 제한적 상태 반영만 한다.
- [ ] runtime 상태는 별도 registry에 저장한다.
- [ ] merge readiness 최종 판정은 dispatch 또는 상위 gate로 남겨둔다.
- [ ] overlap resolution은 orchestrator 본체의 책임이 아니다.
- [ ] orchestrator가 worktree spawn의 canonical owner가 아니다.
- [ ] monitor UI 기능이 본체에 과도하게 섞이지 않는다.

---

## 3. Dependency Alignment

### 3.1 하드 의존성 확인
- [ ] `codex-task-packet` 없이 launch가 불가능하다.
- [ ] `codex-worktree-dispatch` 없이 launch가 불가능하다.
- [ ] `tmux-controller`와의 연결이 명시돼 있다.
- [ ] `worktree-parallel`과의 관계가 명시돼 있다.
- [ ] `tmux`가 환경에 없을 때 명확한 실패 메시지를 낸다.
- [ ] `codex` CLI가 없을 때 명확한 실패 메시지를 낸다.
- [ ] worktree가 사전 생성되지 않았을 때 launch를 거부한다.
- [ ] dependency resolution 결과를 launch readiness에 반영한다.

### 3.2 Soft dependency 분리
- [ ] `session-monitor` 부재 상태에서도 v0.1 기능이 동작한다.
- [ ] notification hook 부재 상태에서도 launch 본체가 동작한다.
- [ ] dashboard UI가 없어도 status 출력이 가능하다.
- [ ] multi-project 확장이 없어도 단일 repo 운영이 가능하다.

---

## 4. Trigger Alignment

### 4.1 언제 이 Skill을 써야 하는가
- [ ] dispatch가 `ready`일 때만 launch trigger가 생긴다.
- [ ] 이미 active runtime이 있으면 재launch를 기본 거부한다.
- [ ] stale/failed 상태에서는 restart path로만 진입한다.
- [ ] `queued/blocked` 상태에서는 launch를 하지 않는다.
- [ ] packet revision mismatch가 있으면 launch를 막는다.
- [ ] branch/worktree mismatch가 있으면 launch를 막는다.

### 4.2 언제 이 Skill을 쓰면 안 되는가
- [ ] task definition 단계에서 이 Skill이 호출되지 않는다.
- [ ] worktree planning 단계에서 이 Skill이 호출되지 않는다.
- [ ] acceptance grading 단계에서 이 Skill이 호출되지 않는다.
- [ ] merge execution 단계 전체를 이 Skill이 소유하지 않는다.

---

## 5. Input Contract Alignment

### 5.1 Packet 입력 검증
- [ ] packet path 존재 확인이 있다.
- [ ] packet schema validation이 있다.
- [ ] `task_id` 존재 확인이 있다.
- [ ] `allowed_paths` 존재 확인이 있다.
- [ ] `done_definition` 존재 확인이 있다.
- [ ] `revision` 필드 확인이 있다.
- [ ] packet revision snapshot을 runtime에 저장한다.

### 5.2 Dispatch 입력 검증
- [ ] dispatch path 존재 확인이 있다.
- [ ] dispatch schema validation이 있다.
- [ ] `dispatch_id` 존재 확인이 있다.
- [ ] `worktree_path` 존재 확인이 있다.
- [ ] `branch` 존재 확인이 있다.
- [ ] `status` 확인이 있다.
- [ ] `assigned_agent` 또는 equivalent 필드 확인이 있다.
- [ ] `locked_paths` 확인이 있다.
- [ ] `status=ready`가 아니면 launch 금지다.

### 5.3 Runtime preset 입력 검증
- [ ] Codex command template이 존재한다.
- [ ] launch mode가 resolve 된다.
- [ ] log path template이 resolve 된다.
- [ ] heartbeat path template이 resolve 된다.
- [ ] session naming template이 resolve 된다.
- [ ] non-ASCII path quoting 전략이 명시돼 있다.

---

## 6. Worktree Binding Alignment

### 6.1 Worktree correctness
- [ ] `worktree_path`가 실제 디렉토리인지 확인한다.
- [ ] `git rev-parse --show-toplevel`로 올바른 repo인지 확인한다.
- [ ] 현재 branch가 dispatch branch와 일치하는지 확인한다.
- [ ] detached HEAD 상태를 감지한다.
- [ ] wrong repo launch를 감지한다.
- [ ] wrong branch launch를 감지한다.
- [ ] wrong worktree launch를 감지한다.

### 6.2 Runnable workspace preflight
- [ ] `.env` 또는 필요한 config 존재 여부를 확인할 수 있다.
- [ ] optional bootstrap hook가 있다면 launch 전에 실행한다.
- [ ] dependency install 여부를 강제할지 명시돼 있다.
- [ ] worktree가 존재만 하고 실행 불가능한 상태를 구분한다.
- [ ] bootstrap failure를 launch failure와 구분한다.

### 6.3 Dispatch ownership respect
- [ ] orchestrator가 branch를 임의로 바꾸지 않는다.
- [ ] orchestrator가 worktree를 임의로 바꾸지 않는다.
- [ ] orchestrator가 lock 범위를 넓히지 않는다.
- [ ] orchestrator가 overlap conflict를 임의 override 하지 않는다.

---

## 7. Session Naming / Identity Alignment

### 7.1 Deterministic naming
- [ ] session name은 deterministic하다.
- [ ] session name은 `task_id` 또는 `dispatch_id`를 포함한다.
- [ ] attempt와 primary session identity를 구분한다.
- [ ] random suffix에 의존하지 않는다.
- [ ] 이름 규칙이 문서화돼 있다.
- [ ] 사람이 session name만 보고 어떤 dispatch인지 추적 가능하다.

### 7.2 Collision handling
- [ ] 동일 session name live collision을 감지한다.
- [ ] collision 시 기본은 실패다.
- [ ] override 정책이 있으면 명시적으로만 허용한다.
- [ ] dead session stale metadata와 live session을 구분한다.
- [ ] session reuse 정책이 문서화돼 있다.

### 7.3 Socket / namespace
- [ ] isolated socket 또는 equivalent namespace 전략이 있다.
- [ ] 다른 unrelated tmux session과 충돌하지 않는다.
- [ ] socket naming 또는 session grouping 규칙이 있다.
- [ ] cleanup 시 socket 범위를 잘못 건드리지 않는다.

---

## 8. Launch Contract Alignment

### 8.1 Preflight gate
- [ ] packet exists
- [ ] dispatch exists
- [ ] dispatch ready
- [ ] worktree exists
- [ ] branch matches
- [ ] runtime collision 없음
- [ ] log path collision 없음
- [ ] session collision 없음
- [ ] command preset resolve 성공
- [ ] stale runtime unresolved case 차단

### 8.2 Launch execution
- [ ] runtime registry 파일을 launch 직전 생성한다.
- [ ] log file을 allocate 한다.
- [ ] heartbeat file을 initialize 한다.
- [ ] tmux session create 실행이 있다.
- [ ] Codex command send 단계가 있다.
- [ ] start marker를 기록한다.
- [ ] 첫 heartbeat 또는 equivalent signal을 기다린다.
- [ ] launch success를 `session exists`만으로 판단하지 않는다.

### 8.3 Launch success / failure distinction
- [ ] session 생성 성공과 worker launch 성공을 구분한다.
- [ ] command send 성공과 first heartbeat 성공을 구분한다.
- [ ] launch 중간 실패 시 `failed`로 명확히 떨어진다.
- [ ] launch partial state가 남을 경우 cleanup/repair 경로가 있다.

---

## 9. Runtime Registry Alignment

### 9.1 Registry 디렉토리 구조
- [ ] `.codex/runtime/` 또는 equivalent가 있다.
- [ ] `.codex/logs/` 또는 equivalent가 있다.
- [ ] `.codex/heartbeats/` 또는 equivalent가 있다.
- [ ] `.codex/sessions/` 또는 equivalent가 있다.
- [ ] registry 구조가 repo-local 기준으로 안정적이다.

### 9.2 Runtime record schema
- [ ] `runtime_version`
- [ ] `task_id`
- [ ] `dispatch_id`
- [ ] `packet_revision`
- [ ] `branch`
- [ ] `worktree_path`
- [ ] `session_name`
- [ ] `launch_command`
- [ ] `attempt_number`
- [ ] `runtime_status`
- [ ] `started_at`
- [ ] `last_seen_at`
- [ ] `completed_at`
- [ ] `exit_code`
- [ ] `exit_reason`
- [ ] `log_path`
- [ ] `heartbeat_path`
- [ ] `restart_count`
- [ ] `previous_attempts`

### 9.3 Canonical ownership
- [ ] current runtime state의 canonical source가 registry 파일이다.
- [ ] `tmux ls`만으로 truth를 판정하지 않는다.
- [ ] log만으로 truth를 판정하지 않는다.
- [ ] registry와 tmux/live process 불일치 시 repair path가 있다.
- [ ] dispatch당 canonical runtime record 하나 원칙이 있다.

### 9.4 Attempt lineage
- [ ] restart 시 attempt number가 증가한다.
- [ ] 이전 log를 덮어쓰지 않는다.
- [ ] 이전 attempt metadata를 유지한다.
- [ ] current attempt와 history가 분리된다.
- [ ] lineage를 통해 stale/failed/completed 이력을 재구성할 수 있다.

---

## 10. Marker Protocol Alignment

### 10.1 Marker 존재 여부
- [ ] start marker가 있다.
- [ ] heartbeat marker 또는 동등한 liveness signal이 있다.
- [ ] done marker가 있다.
- [ ] fail marker 또는 equivalent failure record가 있다.

### 10.2 Marker uniqueness
- [ ] marker에 `dispatch_id`가 포함된다.
- [ ] marker에 `attempt_number`가 포함된다.
- [ ] marker에 timestamp가 포함된다.
- [ ] 일반 문자열과 혼동되기 어려운 prefix를 쓴다.
- [ ] false positive를 최소화하는 규칙이 있다.

### 10.3 Completion rules
- [ ] done marker 없이는 `completed`로 판정하지 않는다.
- [ ] exit code 없이 정상 종료로 간주하지 않는다.
- [ ] fail marker가 있으면 `completed`로 가지 않는다.
- [ ] marker parse 실패 시 unknown success로 넘기지 않는다.

---

## 11. Heartbeat / Health Detection Alignment

### 11.1 Health detection
- [ ] session 존재와 worker health를 구분한다.
- [ ] first heartbeat 도착 전에는 `running` 판정을 유보한다.
- [ ] heartbeat timeout 규칙이 있다.
- [ ] long-running 작업에 대한 timeout 완화 규칙이 있다.
- [ ] stale 전환 규칙이 있다.

### 11.2 Heartbeat storage
- [ ] heartbeat file schema가 있다.
- [ ] `last_seen_at`를 저장한다.
- [ ] `attempt_number`를 저장한다.
- [ ] `session_name`를 저장한다.
- [ ] 마지막 marker 종류를 저장하거나 추론 가능하다.

### 11.3 Health edge cases
- [ ] shell만 살아 있고 Codex worker는 죽은 상태를 탐지할 수 있다.
- [ ] heartbeat file만 남고 session은 없는 상태를 stale로 본다.
- [ ] tmux session은 있지만 heartbeat가 오래 멈춘 상태를 stale로 본다.
- [ ] done marker가 있는데 session이 남아 있는 상태를 completed 처리할 정책이 있다.

---

## 12. State Machine Alignment

### 12.1 상태 집합
- [ ] `planned`
- [ ] `launching`
- [ ] `running`
- [ ] `waiting_input`
- [ ] `completed`
- [ ] `failed`
- [ ] `stale`
- [ ] `killed`
- [ ] `abandoned`
- [ ] `archived`

### 12.2 허용 전이
- [ ] `planned -> launching`
- [ ] `launching -> running`
- [ ] `launching -> failed`
- [ ] `running -> waiting_input`
- [ ] `running -> completed`
- [ ] `running -> failed`
- [ ] `running -> stale`
- [ ] `stale -> launching`
- [ ] `failed -> launching`
- [ ] `running -> killed`
- [ ] `completed -> archived`
- [ ] `failed -> archived`

### 12.3 금지 전이
- [ ] `planned -> completed` 금지
- [ ] `planned -> running` 직접 전이 금지
- [ ] `failed -> completed` 금지
- [ ] `archived -> running` 금지
- [ ] `running -> planned` 금지

### 12.4 State history
- [ ] 상태 전이 history를 남긴다.
- [ ] 각 전이에 `from`, `to`, `at`, `reason`가 남는다.
- [ ] 수동 전이와 자동 전이를 구분할 수 있다.
- [ ] history와 current state가 모순되지 않는다.

---

## 13. Logging Alignment

### 13.1 Log file policy
- [ ] attempt별 log file을 분리한다.
- [ ] log path naming 규칙이 deterministic하다.
- [ ] log path collision을 사전 감지한다.
- [ ] restart가 기존 log를 덮어쓰지 않는다.
- [ ] stdout/stderr capture 전략이 문서화돼 있다.

### 13.2 Debuggability
- [ ] launch command 기록이 log 또는 registry에 남는다.
- [ ] start marker가 log에 남는다.
- [ ] done/fail signal이 log에 남는다.
- [ ] failure reason을 사람이 읽을 수 있는 형태로 남긴다.
- [ ] 마지막 output line 또는 equivalent summary가 status에 반영될 수 있다.

### 13.3 Retention / cleanup
- [ ] cleanup이 log를 즉시 삭제할지 보존할지 정책이 있다.
- [ ] failed run log는 보존되는 편이 낫다.
- [ ] archived runtime log 경로를 추적할 수 있다.

---

## 14. Status / Operator UX Alignment

### 14.1 Human-readable status
- [ ] `status` 명령이 있다.
- [ ] 현재 state를 사람이 읽을 수 있다.
- [ ] task_id / dispatch_id / session_name / worktree_path를 같이 보여준다.
- [ ] last_seen_at 또는 equivalent를 보여준다.
- [ ] restart 필요 여부를 판단할 힌트를 준다.

### 14.2 Machine-readable status
- [ ] `--json` 또는 equivalent 옵션이 있다.
- [ ] automation-friendly output이 있다.
- [ ] field naming이 stable하다.
- [ ] current state와 history를 모두 노출할 수 있다.

### 14.3 Watch / monitoring readiness
- [ ] watch-friendly 출력 형식이 있다.
- [ ] future `session-monitor`가 읽을 수 있는 canonical fields가 있다.
- [ ] operator가 attach/restart/cleanup 대상 선택을 쉽게 할 수 있다.

---

## 15. Restart / Recovery Alignment

### 15.1 Restart preconditions
- [ ] `stale` 또는 `failed`에서만 restart가 허용된다.
- [ ] `running` 중복 restart는 기본 금지다.
- [ ] restart 전 preflight를 다시 수행한다.
- [ ] restart는 새 attempt로 기록된다.

### 15.2 Recovery correctness
- [ ] restart가 wrong worktree를 재사용하지 않는다.
- [ ] restart가 old packet revision을 사용하지 않는다.
- [ ] restart가 session collision을 다시 검사한다.
- [ ] restart가 previous log를 보존한다.
- [ ] restart 후 first heartbeat가 다시 확인된다.

### 15.3 Repair path
- [ ] stale registry만 있고 session이 없는 경우 repair 가능하다.
- [ ] session만 있고 registry가 없는 경우 repair 또는 manual intervention policy가 있다.
- [ ] half-cleanup 상태를 진단할 수 있다.
- [ ] orphan runtime record를 찾아낼 수 있다.

---

## 16. Cleanup / Archive Alignment

### 16.1 Cleanup correctness
- [ ] cleanup이 tmux session을 정리한다.
- [ ] cleanup이 runtime registry를 정리하거나 archive 상태로 전환한다.
- [ ] cleanup이 heartbeat file을 정리한다.
- [ ] cleanup이 log retention policy를 따른다.
- [ ] cleanup이 idempotent하다.

### 16.2 Half-cleanup 방지
- [ ] session만 죽이고 registry를 남겨두는 실수를 방지한다.
- [ ] registry만 지우고 session을 남겨두는 실수를 방지한다.
- [ ] heartbeat만 남는 경우를 정리한다.
- [ ] cleanup 결과를 status에서 검증할 수 있다.

### 16.3 Archive policy
- [ ] `completed -> archived`가 가능하다.
- [ ] `failed -> archived`가 가능하다.
- [ ] archived runtime를 나중에 조사할 수 있다.
- [ ] archived log 경로를 잃어버리지 않는다.

---

## 17. Hook / Bootstrap Alignment

### 17.1 Hook support
- [ ] preflight hook가 있다거나 향후 hook 지점이 정의돼 있다.
- [ ] post-launch hook 지점이 있다.
- [ ] completion hook 지점이 있다.
- [ ] cleanup hook 지점이 있다.

### 17.2 Hook isolation
- [ ] hook 실패가 본체 registry를 깨뜨리지 않는다.
- [ ] hook 실패를 별도 reason으로 기록한다.
- [ ] optional hook absence가 launch 실패를 만들지 않는다.

### 17.3 Bootstrap alignment
- [ ] env/config/dependency bootstrap을 optional 단계로 둘 수 있다.
- [ ] bootstrap 미완료 상태를 preflight에서 감지할 수 있다.
- [ ] bootstrap과 runtime failure를 구분한다.

---

## 18. tmux Semantics Alignment

### 18.1 Official tmux model respect
- [ ] server/client/session/window/pane 개념이 문서에 반영돼 있다.
- [ ] detached session 모델을 올바르게 사용한다.
- [ ] attach/detach를 작업 continuity와 연결해서 해석한다.
- [ ] `tmux ls` 결과를 보조 신호로만 사용한다.

### 18.2 Command handling
- [ ] tmux command 실패를 감지한다.
- [ ] tmux session create 실패를 무시하지 않는다.
- [ ] send-keys quoting 문제를 고려한다.
- [ ] non-ASCII 경로가 있는 환경에서 실패하지 않도록 quoting을 강화한다.

### 18.3 Socket isolation
- [ ] unrelated session을 잘못 캡처하지 않도록 socket/namespace 전략이 있다.
- [ ] multi-session 환경에서 capture 대상이 명확하다.
- [ ] attach 대상이 deterministic하다.

---

## 19. Codex-Specific Alignment

### 19.1 Codex launch semantics
- [ ] `codex exec` 또는 equivalent long-running command 사용 방식이 문서화돼 있다.
- [ ] auth failure를 감지한다.
- [ ] command flag drift 가능성을 고려한다.
- [ ] network 제한 상황에서 launch failure를 명확히 기록한다.

### 19.2 Codex runtime health
- [ ] Codex worker가 시작 직후 죽는 케이스를 탐지한다.
- [ ] Codex가 interactive wait 상태로 들어간 경우를 분리해 본다.
- [ ] Codex output marker 전략이 tmux marker 전략과 충돌하지 않는다.

### 19.3 Long-running operation support
- [ ] 장시간 실행 task에 맞는 timeout policy가 있다.
- [ ] 장시간 무출력 상태를 stale로 오판하지 않는 완화 로직이 있다.
- [ ] 장시간 run의 로그 누적이 관리된다.

---

## 20. Security / Safety Alignment

### 20.1 Path safety
- [ ] worktree path가 repo 외부로 탈출하지 않는지 확인한다.
- [ ] relative path traversal을 방지한다.
- [ ] symlink 경유 잘못된 경로를 방지한다.

### 20.2 Command safety
- [ ] launch command quoting이 안전하다.
- [ ] user-provided free-form string을 그대로 shell에 넣지 않는다.
- [ ] command template과 variable substitution 경계가 명시돼 있다.

### 20.3 Concurrency safety
- [ ] 동일 dispatch에 복수 active runtime 금지 정책이 있다.
- [ ] collision을 operator override 없이는 통과시키지 않는다.
- [ ] cleanup이 다른 unrelated session을 건드리지 않는다.

---

## 21. CLI Surface Alignment

### 21.1 최소 명령 집합
- [ ] `preflight`
- [ ] `launch`
- [ ] `status`
- [ ] `restart`
- [ ] `cleanup`
- [ ] `registry-validate`

### 21.2 권장 명령
- [ ] `watch`
- [ ] `tail`
- [ ] `attach`
- [ ] `repair`

### 21.3 UX 원칙
- [ ] 명령명은 기능과 직관적으로 대응한다.
- [ ] human summary와 machine output이 공존한다.
- [ ] dry-run 옵션이 있으면 좋다.
- [ ] exit code 정책이 일관적이다.

---

## 22. Testing Alignment

### 22.1 Positive tests
- [ ] ready dispatch 1개 정상 launch 테스트
- [ ] first heartbeat 수신 테스트
- [ ] done marker 종료 테스트
- [ ] completed 상태 finalize 테스트
- [ ] stale -> restart -> running 복구 테스트

### 22.2 Negative tests
- [ ] packet 없음 -> launch 실패
- [ ] dispatch 없음 -> launch 실패
- [ ] dispatch not ready -> launch 실패
- [ ] wrong worktree -> launch 실패
- [ ] wrong branch -> launch 실패
- [ ] duplicate session -> launch 실패
- [ ] no heartbeat -> stale 전환
- [ ] done marker 없음 -> completed 금지
- [ ] cleanup half-state -> repair 필요 판정

### 22.3 Regression tests
- [ ] non-ASCII path launch 테스트
- [ ] long-running idle-ish output 테스트
- [ ] log rotation / attempt increment 테스트
- [ ] stale registry recovery 테스트
- [ ] restart after revision mismatch 차단 테스트

---

## 23. Documentation Alignment

### 23.1 Required docs
- [ ] `LAUNCH_CONTRACT.md`
- [ ] `SESSION_STATE_MACHINE.md`
- [ ] `RUNTIME_REGISTRY_SCHEMA.md`
- [ ] `MARKER_PROTOCOL.md`
- [ ] `HEARTBEAT_POLICY.md`
- [ ] `FAILURE_CASES.md`
- [ ] `CLEANUP_RULES.md`

### 23.2 Doc-code consistency
- [ ] 문서의 상태 이름과 코드의 상태 이름이 일치한다.
- [ ] 문서의 session naming 규칙과 코드가 일치한다.
- [ ] 문서의 registry path와 코드가 일치한다.
- [ ] 문서의 restart policy와 코드가 일치한다.
- [ ] 문서의 cleanup policy와 코드가 일치한다.

### 23.3 Reference hygiene
- [ ] reference 문서가 product-wide scope와 v0.1 scope를 구분해 준다.
- [ ] KB와 checklist가 서로 모순되지 않는다.
- [ ] SKILL.md에 reference loading guidance가 있다.

---

## 24. tmux + Codex 실제 실험 준비도

### 24.1 Ready for live run
- [ ] 실제 tmux 세션에서 Codex CLI를 띄울 수 있다.
- [ ] 실제 worktree 경로에서 Codex가 시작된다.
- [ ] launch 후 registry가 생성된다.
- [ ] launch 후 log가 생긴다.
- [ ] launch 후 heartbeat가 갱신된다.

### 24.2 Debuggability in live runs
- [ ] 실패 시 마지막 로그를 바로 볼 수 있다.
- [ ] 어떤 dispatch가 어떤 session인지 바로 찾을 수 있다.
- [ ] stale가 왜 stale인지 reason이 보인다.
- [ ] cleanup 전/후 차이를 상태로 확인할 수 있다.

### 24.3 Iteration support
- [ ] bug pattern을 별도 references 문서에 축적할 수 있다.
- [ ] success pattern도 문서화할 수 있다.
- [ ] live run 결과를 바탕으로 command preset이나 timeout 정책을 조정할 수 있다.

---

## 25. 최소 합격선

### v0.1 Minimum Pass
아래 항목을 모두 만족해야 `v0.1 usable`로 본다.

- [ ] dispatch-first launch
- [ ] wrong worktree 방지
- [ ] deterministic session naming
- [ ] runtime registry 생성
- [ ] attempt별 log 보존
- [ ] heartbeat 기반 running 판정
- [ ] stale 탐지
- [ ] restart 1회 동작
- [ ] cleanup idempotent
- [ ] human-readable status
- [ ] machine-readable status
- [ ] half-cleanup 진단 가능

### v0.2 Operational Pass
- [ ] batch launch
- [ ] queue/policy 기반 release
- [ ] richer watch UX
- [ ] hook integration
- [ ] grouped status summary

### v0.3 Trusted Pass
- [ ] live long-running sessions 반복 검증
- [ ] bug/trouble 패턴 reference 축적
- [ ] monitor integration
- [ ] multi-project 확장성 검증

---

## 26. 구현 전 반드시 결정할 15가지

- [ ] session naming rule
- [ ] socket/namespace rule
- [ ] runtime registry path
- [ ] heartbeat file schema
- [ ] attempt numbering rule
- [ ] log rotation rule
- [ ] stale timeout policy
- [ ] waiting_input detection rule
- [ ] done/fail marker rule
- [ ] restart allowed conditions
- [ ] cleanup retention rule
- [ ] session collision rule
- [ ] packet revision mismatch policy
- [ ] shell quoting policy
- [ ] machine-readable status schema

---

## 27. 최종 판정 질문

아래 질문에 모두 `예`라고 답할 수 있어야 이 Skill은 reference와 구현이 정합하다고 본다.

- [ ] 이 구현은 `dispatch-first`인가?
- [ ] 이 구현은 잘못된 worktree launch를 막는가?
- [ ] 이 구현은 `session exists`와 `worker healthy`를 구분하는가?
- [ ] 이 구현은 runtime state를 file registry로 복구 가능하게 남기는가?
- [ ] 이 구현은 stale/duplicate/half-cleanup을 운영자가 진단 가능하게 만드는가?
- [ ] 이 구현은 `tmux-controller`와 `worktree-parallel`의 책임을 침범하지 않는가?
- [ ] 이 구현은 Codex-specific long-running runtime 문제를 실질적으로 다루는가?
- [ ] 이 구현은 v0.1 scope를 넘어서 과도하게 비대해지지 않았는가?

이 8개 중 하나라도 `아니오`면, 구현은 아직 reference 정합성이 불충분하다고 봐야 한다.
