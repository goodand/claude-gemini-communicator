# Boundary of Responsibility
- skill: `skill-workflow-bridge-eval`
- version: `v0.1.0`
- created_at: `2026-03-16`
- purpose: `skill-workflow-bridge-eval`이 무엇을 소유하고 무엇을 소유하지 않는지, 어떤 입력을 읽고 어떤 출력을 만들며, 어떤 decision을 내릴 수 있는지 canonical boundary를 고정하기 위한 문서
- status: `canonical-boundary`

---

## 1. 문서 목적

이 문서는 `skill-workflow-bridge-eval`의 책임 경계를 고정한다.

이 Skill은 여러 Skill의 사이에 끼어 있는 "연결부"이기 때문에, 경계가 조금만 흐려져도 아래 문제가 생긴다.

- task planning skill과 역할이 섞임
- runtime orchestrator와 역할이 섞임
- acceptance gate와 역할이 섞임
- 개별 skill의 본문 생성 책임과 섞임
- fan-in 도구인지 reroute 도구인지 모호해짐

따라서 이 문서의 목적은 간단하다.

1. 이 Skill이 직접 소유하는 것
2. 이 Skill이 읽기만 하는 것
3. 이 Skill이 절대 소유하면 안 되는 것
4. 이 Skill이 만들어야 하는 canonical artifact
5. 이 Skill이 내릴 수 있는 decision

을 고정한다.

---

## 2. 이 Skill의 한 줄 정체성

`skill-workflow-bridge-eval`은 **앞 단계 Skill의 출력과 실행 상태를 평가해, 다음 Skill로의 handoff 가능 여부를 판단하고, 필요하면 retry / reroute / loop / stop 결정을 내리는 workflow bridge controller**다.

즉 이 Skill의 책임은 아래 두 가지를 동시에 갖는다.

- `bridge`
- `eval`

하지만 아래는 아니다.

- 본문 생성
- 실제 terminal session 실행
- git worktree 배치
- 최종 acceptance gate 전체 대체

---

## 3. 이 Skill이 직접 소유하는 것

### 3.1 Workflow-level decision ownership
이 Skill은 다음 실행 결정을 소유한다.

- `pass`
- `retry`
- `reroute`
- `loop`
- `stop`
- `escalate`
- `fanout`
- `fanin_hold`

이 decision은 이 Skill의 핵심 책임이다.

### 3.2 Handoff readiness 판단
이 Skill은 현재 출력이 다음 Skill로 넘어갈 수 있는지 판단한다.

즉 아래를 소유한다.

- `next_step_ready`
- `handoff_possible`
- `downstream_contract_satisfied`
- `repairable_failure`
- `retryable`

### 3.3 Output normalization ownership
특히 자연어 출력에 대해 이 Skill은 정규화 책임을 가진다.

즉 아래를 소유한다.

- output type classification
- natural language extraction
- bridge evaluation
- retry spec generation
- handoff packet generation

### 3.4 Workflow trace ownership
이 Skill은 run-level trace를 남겨야 한다.

즉 아래를 소유한다.

- `workflow_run_id`
- `step_run_id`
- `bridge_eval.json`
- `retry_spec.json`
- `handoff_packet.json`
- decision trace
- event log

### 3.5 Fan-in policy execution ownership
parallel workflow에서 이 Skill은 결과를 어떻게 다음 단계로 넘길지 판단하는 ownership을 가진다.

즉 아래를 소유한다.

- branch result normalization
- branch confidence 비교
- branch unmet condition 비교
- fan-in readiness 판단
- `fanin_hold` 여부 판단

---

## 4. 이 Skill이 읽기만 해야 하는 것

### 4.1 Upstream skill output
이 Skill은 앞 단계 Skill의 raw output을 읽는다.

예:
- 자연어 출력
- JSON 출력
- script stdout/stderr
- 생성 파일 목록
- 실행 로그 요약

하지만 이 raw output 자체를 수정해서는 안 된다.

### 4.2 Task / plan / context 정의
아래는 읽기만 가능하다.

- task goal
- upstream task packet
- workflow mode
- downstream expected format
- required sections / required checks
- evaluation threshold

### 4.3 Runtime metadata
실행 환경 metadata는 읽기 가능하지만 canonical ownership은 다른 Skill에 있다.

예:
- tmux session name
- worktree path
- branch
- runtime status
- codex exit status

---

## 5. 이 Skill이 절대 소유하면 안 되는 것

### 5.1 개별 Skill의 본문 생성 책임
이 Skill은 아래를 직접 만들면 안 된다.

- 초안 본문 자체
- 코드 수정안 자체
- 보고서 본문 자체
- 개별 Skill이 원래 생성해야 하는 최종 산출물 본체

이 Skill은 생성자가 아니라 evaluator/bridge다.

### 5.2 Runtime execution ownership
이 Skill은 아래를 canonical하게 소유하면 안 된다.

- tmux session lifecycle
- codex launch primitive
- process kill/restart primitive 자체
- heartbeat file canonical ownership
- log file canonical ownership

이건 `codex-tmux-orchestrator` 또는 runtime layer 쪽 책임이다.

### 5.3 Worktree / branch ownership
이 Skill은 아래를 canonical하게 소유하면 안 된다.

- worktree 생성
- branch 배정
- file lock
- overlap resolution
- merge readiness 최종 판정

이건 dispatch/worktree skill 쪽 책임이다.

### 5.4 Acceptance gate 전체 대체
이 Skill은 개별 Skill 자체의 동작 검증을 완전히 대체하면 안 된다.

즉 아래는 별도 skill 또는 별도 gate 책임으로 둔다.

- skill 자체의 schema validation
- tool installation check
- UI metadata validity
- SKILL.md correctness

### 5.5 무제한 router 역할
이 Skill은 full graph scheduler가 아니다.

즉 아래를 처음부터 다 소유하면 안 된다.

- 임의 DAG scheduling 전체
- resource scheduler 전체
- multi-project queue orchestrator 전체
- 전역 priority arbiter 전체

---

## 6. 입력 경계

### 6.1 최소 입력 단위
이 Skill은 최소 아래를 입력으로 받아야 한다.

- `workflow_run_id`
- `step_id`
- `skill_name`
- `output_type` 또는 raw output
- `raw_output`
- `upstream_artifacts`
- `expected_downstream_contract`
- `workflow_mode`

### 6.2 허용 입력 타입
- `script_result`
- `structured_json`
- `natural_language`
- `mixed`

### 6.3 입력으로 받아도 되지만 소유하지 않는 것
- runtime logs
- raw stdout
- evaluation prompt
- task packet
- dispatch metadata
- external artifacts

---

## 7. 출력 경계

이 Skill의 canonical output은 아래 네 가지다.

### 7.1 `raw_output.md`
- 원문 보존
- forensic/debugging source
- evaluator input source

### 7.2 `bridge_eval.json`
이 Skill의 핵심 평가 결과 파일이다.

최소 포함해야 할 것:
- `run_id`
- `step_id`
- `skill_name`
- `output_type`
- `pass`
- `score`
- `confidence`
- `failure_type`
- `recommended_action`
- `unmet_conditions`
- `evidence`
- `next_step_ready`

### 7.3 `retry_spec.json`
재실행이 필요할 때 생성하는 repair guidance 파일이다.

최소 포함해야 할 것:
- `retryable`
- `retry_count`
- `max_retries`
- `failure_type`
- `unmet_conditions`
- `repair_instructions`
- `no_progress_signal`

### 7.4 `handoff_packet.json`
다음 Skill이 읽는 canonical handoff artifact다.

최소 포함해야 할 것:
- `ready`
- `decision`
- `next_skill`
- `normalized_summary`
- `key_outputs`
- `missing_items`
- `confidence`
- `source_artifacts`

---

## 8. decision ownership

### 8.1 이 Skill이 직접 내려야 하는 decision
- `pass`
- `retry`
- `reroute`
- `loop`
- `stop`
- `escalate`
- `fanout`
- `fanin_hold`

### 8.2 이 Skill이 직접 내리면 안 되는 decision
- git merge 수행 여부
- runtime 세션 kill 방식 세부 선택
- worktree spawn 여부
- branch naming rule 생성
- 최종 production release 여부

---

## 9. retry에 대한 책임 경계

이 부분은 특히 중요하다.

### 9.1 이 Skill은 retry 여부를 결정한다
이건 핵심 책임이다.

### 9.2 이 Skill은 blind retry를 금지한다
즉 같은 입력을 그대로 다시 던지는 것은 이 Skill의 올바른 동작이 아니다.

### 9.3 이 Skill은 repair retry spec을 만든다
즉 retry 시 아래를 구조화해 넘겨야 한다.

- 무엇이 부족했는가
- 어떤 형식이 틀렸는가
- 무엇을 추가해야 하는가
- 이전 시도 대비 무엇이 개선되어야 하는가

### 9.4 실제 재실행 primitive는 다른 layer가 맡을 수 있다
예:
- orchestrator
- runner
- upstream controller

즉 `retry decision ownership`과 `retry execution ownership`은 분리할 수 있다.

---

## 10. reroute에 대한 책임 경계

### 10.1 이 Skill은 reroute 필요 여부를 판단한다
예:
- 현재 Skill보다 extractor skill이 더 적합
- generation은 됐으나 normalization skill이 필요
- evaluator branch를 추가해야 함

### 10.2 실제 reroute destination resolution은 정책 layer와 분리 가능하다
즉 이 Skill은 아래를 직접 하지 않아도 된다.

- 모든 가능한 skill graph 탐색
- global scheduling
- resource arbitration

하지만 아래는 해야 한다.

- `recommended_next_skill`
- `reroute_reason`
- `destination_contract`

---

## 11. natural language output 처리 경계

### 11.1 이 Skill이 직접 해야 하는 것
자연어 출력은 그대로 downstream에 넘기면 안 된다.  
따라서 아래는 이 Skill의 직접 책임이다.

- raw 자연어 보존
- 핵심 정보 추출
- completion claim과 evidence 분리
- handoff readiness 평가
- normalized summary 생성
- missing item 추출
- retry/repair instructions 생성

### 11.2 이 Skill이 직접 하지 않아도 되는 것
- 자연어 본문 자체 다시 작성
- 완전한 semantic truth verification 전체
- domain-specific factuality auditing 전체

이런 건 별도 evaluator skill로 분리할 수 있다.

---

## 12. workflow mode별 책임 경계

### 12.1 Sequential
이 Skill이 해야 하는 것:
- A 출력 평가
- B로 handoff 가능 여부 판단
- A 재실행 필요 여부 판단

이 Skill이 하지 않는 것:
- A 자체 구현
- B 자체 구현

### 12.2 Parallel
이 Skill이 해야 하는 것:
- branch 결과 표준화
- branch별 quality 비교
- fan-in 가능 여부 판단
- branch별 retry 필요 여부 판단

이 Skill이 하지 않는 것:
- 병렬 branch 실행 primitive 전체
- branch resource scheduling 전체

### 12.3 Evaluator-Optimizer
이 Skill이 해야 하는 것:
- evaluator feedback 구조화
- retry_spec 생성
- loop 상태 추적
- no-progress 판정

이 Skill이 하지 않는 것:
- generator 자체 구현
- evaluator 자체 구현

---

## 13. 다른 Skill과의 경계표

| 역할 | skill-workflow-bridge-eval | 다른 skill |
|---|---|---|
| 개별 산출물 생성 | No | 생성 skill |
| task goal 정의 | No | task/plan skill |
| worktree 배치 | No | dispatch/worktree skill |
| tmux/Codex 실행 | No | orchestrator/runtime skill |
| 출력 정규화 | Yes | - |
| handoff readiness 평가 | Yes | - |
| retry/reroute/loop/stop decision | Yes | - |
| acceptance gate 전체 | Partial only | acceptance skill |
| fan-in decision | Yes | branch skill outputs are inputs |
| 최종 release/merge | No | release/integration layer |

---

## 14. canonical source of truth

### 14.1 이 Skill에서 canonical인 것
- `bridge_eval.json`
- `retry_spec.json`
- `handoff_packet.json`
- decision trace

### 14.2 canonical이 아닌 것
- raw 자연어 자체
- 콘솔 stdout 그대로
- 임시 메모
- 사람이 쓴 completion claim

즉 downstream skill은 가능하면 raw output보다 `handoff_packet.json`을 우선적으로 읽어야 한다.

---

## 15. 실패 책임 경계

이 Skill은 아래 실패를 감지해야 한다.

- downstream contract 미충족
- evidence 부족
- completion claim과 실제 output 불일치
- ambiguity 과다
- no-progress retry loop
- parallel fan-in 불가

하지만 아래 실패는 직접 해결하지 않을 수 있다.

- runtime process crash 자체
- worktree corruption 자체
- git merge conflict 자체
- external API outage 자체

대신 그 실패를 `external_blocked` 또는 유사 taxonomy로 기록하고 상위 layer에 넘겨야 한다.

---

## 16. 실패 taxonomy ownership

이 Skill은 최소 아래 taxonomy를 소유하는 것이 좋다.

- `recoverable`
- `irrecoverable`
- `ambiguous`
- `external_blocked`
- `no_progress`
- `unsafe`

이 taxonomy는 `bridge_eval.json`과 `retry_spec.json`의 핵심 field가 된다.

---

## 17. boundary 규칙 요약

### 규칙 1
이 Skill은 **출력의 의미를 평가하고 다음 흐름을 결정**한다.

### 규칙 2
이 Skill은 **직접 생성하지 않는다**.

### 규칙 3
이 Skill은 **직접 실행 primitive를 소유하지 않는다**.

### 규칙 4
이 Skill은 **자연어 출력을 canonical packet으로 정규화**해야 한다.

### 규칙 5
이 Skill은 **retry decision은 소유하지만, retry execution primitive는 분리 가능**하다.

### 규칙 6
이 Skill은 **raw output보다 bridge artifacts를 canonical source로 사용**한다.

---

## 18. 구현 전 최종 질문

아래 질문에 모두 `예`라고 답할 수 있어야 경계가 제대로 잡힌 것이다.

- [ ] 이 Skill은 생성자가 아니라 bridge/evaluator인가?
- [ ] 이 Skill은 raw output을 그대로 handoff하지 않는가?
- [ ] 이 Skill은 retry를 blind retry가 아니라 repair retry로 취급하는가?
- [ ] 이 Skill은 runtime orchestration과 worktree dispatch ownership을 침범하지 않는가?
- [ ] 이 Skill의 canonical outputs가 명확한가?
- [ ] 이 Skill이 내리는 decision set이 명확한가?
- [ ] downstream skill은 raw output이 아니라 handoff packet을 읽도록 설계돼 있는가?
- [ ] natural language output이 result가 아니라 claim으로 먼저 취급되는가?

이 중 하나라도 `아니오`면, `skill-workflow-bridge-eval`의 책임 경계는 아직 충분히 고정되지 않은 것이다.
