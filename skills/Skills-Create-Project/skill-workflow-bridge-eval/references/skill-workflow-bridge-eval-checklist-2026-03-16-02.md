# skill-workflow-bridge-eval Implementation Alignment Checklist
- version: `v0.1.0`
- created_at: `2026-03-16`
- purpose: `skill-workflow-bridge-eval` 구현이 knowledge base, reference, boundary 문서와 기능적으로 정합한지 판단하기 위한 상세 체크리스트
- scope: `workflow bridge / handoff evaluation / retry decision / fan-in control`
- based_on:
  - `Boundary-of-Responsibility-2026-03-15-03-56.md`
  - `skill-workflow-bridge-eval-reference-2026-03-16-01.md`
  - `skill-workflow-bridge-eval-knowledge_base2026-03-16-00.md`

---

## 0. 사용 방법

이 체크리스트는 단순히 기능이 있는지 보는 문서가 아니다.  
다음 세 가지를 동시에 본다.

1. 기능이 실제로 구현되어 있는가
2. 구현이 이 Skill의 책임 경계를 지키는가
3. 구현이 reference가 강조한 failure mode를 실제로 막는가

판정 레벨은 아래처럼 나눈다.

- `L0 Draft`
  - 문서나 메모만 있고 실제 스크립트/아티팩트/검증이 없다.
- `L1 Testable`
  - 최소 스크립트나 manual flow가 있고 수동 검증이 가능하다.
- `L2 Operational`
  - workflow mode, decision, retry, handoff, logging이 반복 실행 가능하다.
- `L3 Trusted`
  - 실제 multi-skill runs에 써서 bug pattern과 success pattern이 축적됐다.

`v0.1` 최소 목표는 `L1.5 ~ L2`다.

---

## 1. Reference Alignment Summary

이 Skill 구현은 아래 reference 축과 기능적으로 대응해야 한다.

| Reference | 구현이 반드시 반영해야 하는 핵심 |
|---|---|
| `Anthropic effective agents` | sequential / parallel / evaluator-optimizer 모드 구분 |
| `Anthropic multi-agent system` | raw output dump가 아니라 structured handoff artifact |
| `OpenAI agent evals` | run-level / step-level trace와 artifact lineage |
| `OpenAI trace grading` | intermediate handoff trace 평가 |
| `OpenAI graders` | 자연어 출력의 structured grading |
| `OpenAI eval best practices` | failure taxonomy와 retry/reroute 기준 명시 |
| `Inspect tracing/scorers` | scorer abstraction, trace 저장, evaluator reuse |
| `Promptfoo simulated user` | downstream consumer 관점의 handoff 평가 |
| `AWS agent-evaluation` | target skill과 evaluator 역할 분리 |
| `DeepEval` | custom bridge metric 설계 |
| `MCP workflows overview` | workflow mode abstraction |
| `MCP evaluator_optimizer` | repair retry / loop state |
| `AgentBench/AgentBoard` | progress/trajectory 평가 |
| `τ-bench` | interaction quality를 handoff quality로 확장 |
| `AgentDojo` | misleading output/unsafe output robustness |
| `SWE-bench` | executable evidence 우선 원칙 |

정합성 판정 원칙:
- 모든 reference를 그대로 복제할 필요는 없다.
- 하지만 각 reference가 대표하는 핵심 축은 구현에 실제 반영돼야 한다.
- 특히 이 Skill은 `decision + normalization + trace + retry quality` 축을 놓치면 reference 정합성이 낮다고 본다.

---

## 2. Identity / Boundary Alignment

### 2.1 정체성
- [ ] 이 Skill은 스스로를 `bridge + eval + decision` skill로 정의한다.
- [ ] 이 Skill은 개별 산출물을 생성하는 creator skill이 아님이 문서와 코드에서 명확하다.
- [ ] 이 Skill은 runtime executor가 아님이 명확하다.
- [ ] 이 Skill은 worktree/dispatch canonical owner가 아님이 명확하다.
- [ ] 이 Skill은 raw output을 다음 skill로 그대로 넘기지 않는다는 원칙이 명시돼 있다.

### 2.2 Boundary 문서 정합성
- [ ] `Boundary-of-Responsibility-2026-03-15-03-56.md`와 구현이 일치한다.
- [ ] 구현이 `pass/retry/reroute/loop/stop/escalate/fanout/fanin_hold` decision set을 반영한다.
- [ ] 구현이 `raw_output.md`, `bridge_eval.json`, `retry_spec.json`, `handoff_packet.json` canonical artifacts를 반영한다.
- [ ] 구현이 개별 skill의 본문 생성 책임을 침범하지 않는다.
- [ ] 구현이 tmux/worktree/runtime ownership을 침범하지 않는다.

### 2.3 금지 경계 위반 방지
- [ ] 이 Skill이 task goal 자체를 새로 정의하지 않는다.
- [ ] 이 Skill이 worktree/branch/file lock을 직접 배정하지 않는다.
- [ ] 이 Skill이 final merge/release gate 전체를 대체하지 않는다.
- [ ] 이 Skill이 acceptance-gate 전체를 대체하지 않는다.
- [ ] 이 Skill이 full DAG scheduler처럼 범위를 무리하게 확장하지 않는다.

---

## 3. Workflow Mode Alignment

### 3.1 Sequential Mode
- [ ] sequential mode가 존재한다.
- [ ] step A output을 평가한 뒤 step B handoff 가능 여부를 판단한다.
- [ ] next step readiness가 없으면 B로 직접 handoff하지 않는다.
- [ ] sequential retry가 blind retry가 아니라 repair retry다.
- [ ] reroute가 sequential flow 안에서도 가능하다.
- [ ] sequential trace가 `workflow_run_id`, `step_run_id` 단위로 남는다.

### 3.2 Parallel Mode
- [ ] parallel mode가 존재한다.
- [ ] 여러 branch output을 branch별 artifact로 수집한다.
- [ ] 각 branch를 normalization 후 비교한다.
- [ ] fan-in 전 branch readiness를 평가한다.
- [ ] branch별 retry가 가능하다.
- [ ] `fanin_hold` decision이 있다.
- [ ] branch conflict 처리 정책이 있다.

### 3.3 Evaluator-Optimizer Mode
- [ ] evaluator-optimizer mode가 존재한다.
- [ ] generator output과 evaluator feedback이 분리된다.
- [ ] evaluator feedback이 `retry_spec`으로 구조화된다.
- [ ] max iterations가 있다.
- [ ] target threshold가 있다.
- [ ] no-progress detection이 있다.
- [ ] loop 종료 조건이 있다.

### 3.4 Future Hybrid / Router Readiness
- [ ] 현재는 full router graph가 아니지만 reroute decision을 수용할 수 있다.
- [ ] future graph-based expansion을 막지 않는 state/decision 구조다.
- [ ] direct recursion이나 uncontrolled DAG spawning이 없다.

---

## 4. Input Contract Alignment

### 4.1 최소 입력 단위
- [ ] `workflow_run_id`
- [ ] `step_id`
- [ ] `skill_name`
- [ ] `workflow_mode`
- [ ] `raw_output` 또는 equivalent artifact path
- [ ] `expected_downstream_contract`
- [ ] `upstream_artifacts`
- [ ] `output_type` 또는 classifier input

### 4.2 입력 타입
- [ ] `script_result`를 지원한다.
- [ ] `structured_json`를 지원한다.
- [ ] `natural_language`를 지원한다.
- [ ] `mixed`를 지원한다.

### 4.3 입력 검증
- [ ] raw output artifact 존재 확인이 있다.
- [ ] expected contract schema 또는 최소 필수 필드가 있다.
- [ ] missing upstream artifact를 `external_blocked` 또는 equivalent로 분리한다.
- [ ] malformed JSON과 plain text를 구분한다.
- [ ] output type classifier가 실패했을 때 fallback 규칙이 있다.

---

## 5. Output Type Classification Alignment

### 5.1 분류 단계 존재 여부
- [ ] output type classification 단계가 있다.
- [ ] classification 결과를 trace에 남긴다.
- [ ] classifier confidence 또는 equivalent reasoning이 있다.

### 5.2 Natural Language Handling
- [ ] natural_language output을 result가 아니라 claim으로 취급한다.
- [ ] natural language output을 즉시 downstream handoff하지 않는다.
- [ ] extraction 단계가 존재한다.
- [ ] extraction 결과가 structured artifact로 남는다.

### 5.3 Structured Output Handling
- [ ] structured_json output은 schema validation을 거친다.
- [ ] schema invalid output은 retry/reroute 대상으로 분류 가능하다.
- [ ] required field completeness를 점검한다.

### 5.4 Script Result Handling
- [ ] script_result는 exit code를 본다.
- [ ] stdout/stderr를 읽는다.
- [ ] artifact existence를 점검한다.
- [ ] self-report 대신 executable evidence를 우선한다.

### 5.5 Mixed Output Handling
- [ ] mixed output에서 natural language와 structured 부분을 구분할 수 있다.
- [ ] partial extraction 또는 layered grading이 가능하다.

---

## 6. Canonical Artifact Alignment

### 6.1 `raw_output.md`
- [ ] 원문을 그대로 보존한다.
- [ ] 사람이 검토 가능하다.
- [ ] downstream canonical input으로 직접 쓰지 않는다.

### 6.2 `bridge_eval.json`
- [ ] 존재한다.
- [ ] `run_id`가 있다.
- [ ] `step_id`가 있다.
- [ ] `skill_name`이 있다.
- [ ] `output_type`이 있다.
- [ ] `pass`가 있다.
- [ ] `score`가 있다.
- [ ] `confidence`가 있다.
- [ ] `failure_type`이 있다.
- [ ] `recommended_action`이 있다.
- [ ] `unmet_conditions`가 있다.
- [ ] `evidence`가 있다.
- [ ] `next_step_ready`가 있다.

### 6.3 `retry_spec.json`
- [ ] 존재한다.
- [ ] `retryable`가 있다.
- [ ] `retry_count`가 있다.
- [ ] `max_retries`가 있다.
- [ ] `failure_type`이 있다.
- [ ] `unmet_conditions`가 있다.
- [ ] `repair_instructions`가 있다.
- [ ] `no_progress_signal`이 있다.

### 6.4 `handoff_packet.json`
- [ ] 존재한다.
- [ ] `ready`가 있다.
- [ ] `decision`이 있다.
- [ ] `next_skill`이 있다.
- [ ] `normalized_summary`가 있다.
- [ ] `key_outputs`가 있다.
- [ ] `missing_items`가 있다.
- [ ] `confidence`가 있다.
- [ ] `source_artifacts`가 있다.

### 6.5 Artifact Canonicality
- [ ] downstream skill은 raw output보다 `handoff_packet.json`을 우선 읽도록 설계된다.
- [ ] trace/debugging에는 `raw_output.md`가 유지된다.
- [ ] decision source는 `bridge_eval.json`이다.
- [ ] retry source는 `retry_spec.json`이다.

---

## 7. Natural Language Normalization Alignment

### 7.1 Extraction Fields
- [ ] `task_completion_claim`
- [ ] `key_outputs`
- [ ] `missing_items`
- [ ] `open_questions`
- [ ] `evidence`
- [ ] `confidence`
- [ ] `next_step_ready`

### 7.2 Claim vs Evidence 분리
- [ ] completion claim을 evidence와 분리한다.
- [ ] “완료했습니다”를 성공 증거로 직접 사용하지 않는다.
- [ ] file existence, artifact path, explicit output sections 등 더 강한 근거를 우선한다.

### 7.3 Ambiguity Handling
- [ ] ambiguous natural language를 감지할 수 있다.
- [ ] ambiguous output을 pass로 넘기지 않는다.
- [ ] ambiguity는 retry 또는 escalate로 연결될 수 있다.

### 7.4 Misleading Output Robustness
- [ ] self-report만 있고 artifact가 없는 경우 실패 처리할 수 있다.
- [ ] natural language가 구조적으로 handoff 불가하면 retry/reroute 가능하다.
- [ ] misleading completion claim을 AgentDojo 스타일 failure로 분류할 수 있다.

---

## 8. Decision Algebra Alignment

### 8.1 Decision Set 존재 여부
- [ ] `pass`
- [ ] `retry`
- [ ] `reroute`
- [ ] `loop`
- [ ] `stop`
- [ ] `escalate`
- [ ] `fanout`
- [ ] `fanin_hold`

### 8.2 Decision Criteria Explicitness
- [ ] 각 decision에 대한 명시적 조건이 있다.
- [ ] decision이 score만으로 정해지지 않는다.
- [ ] unmet_conditions와 failure_type을 함께 본다.
- [ ] next_step_ready를 함께 본다.
- [ ] recoverable vs irrecoverable 구분이 있다.

### 8.3 Invalid Decision 방지
- [ ] `next_step_ready=false`인데 `pass`가 되지 않는다.
- [ ] `retryable=false`인데 `retry`가 되지 않는다.
- [ ] `no_progress_signal=true`인데 무한 `loop`가 되지 않는다.
- [ ] branch 미완료인데 `fanin_ready`로 오판하지 않는다.

---

## 9. Retry Quality Alignment

### 9.1 Blind Retry 금지
- [ ] blind retry가 기본 전략이 아니다.
- [ ] retry는 항상 `retry_spec`을 동반한다.
- [ ] retry input에 repair instruction이 포함된다.

### 9.2 Repair Retry
- [ ] unmet condition이 구조화된다.
- [ ] repair instruction이 구체적이다.
- [ ] 이전 시도 대비 무엇이 달라져야 하는지 명시된다.
- [ ] retry count가 증가한다.

### 9.3 No-Progress Detection
- [ ] 반복 실패를 감지한다.
- [ ] same unmet condition 반복을 감지한다.
- [ ] score improvement < epsilon 같은 규칙이 있거나 equivalent signal이 있다.
- [ ] no-progress 시 reroute/stop/escalate로 전환할 수 있다.

### 9.4 Retry Termination
- [ ] `max_retries`가 있다.
- [ ] `max_iterations`가 있다.
- [ ] retry exhaustion 후 fallback decision이 있다.
- [ ] retry exhaustion이 무한 loop로 이어지지 않는다.

---

## 10. Reroute Alignment

### 10.1 Reroute Trigger
- [ ] 현재 skill capability mismatch 감지 가능
- [ ] 같은 실패 반복 시 reroute 고려
- [ ] generation 문제와 normalization 문제를 구분
- [ ] extractor skill / formatter skill / evaluator skill 등으로 reroute 가능성 판단

### 10.2 Reroute Metadata
- [ ] `recommended_next_skill` 또는 equivalent 필드가 있다.
- [ ] `reroute_reason`이 있다.
- [ ] destination contract를 함께 기록한다.

### 10.3 Scope Control
- [ ] full router graph scheduler가 되지 않는다.
- [ ] global resource allocation까지 소유하지 않는다.
- [ ] reroute는 policy hint 또는 next-step decision 수준에 머문다.

---

## 11. Fan-out / Fan-in Alignment

### 11.1 Parallel Branch Collection
- [ ] branch별 raw outputs를 별도 보존한다.
- [ ] branch별 bridge_eval을 만든다.
- [ ] branch별 confidence를 비교할 수 있다.
- [ ] branch별 unmet_conditions를 비교할 수 있다.

### 11.2 Aggregation Policy
- [ ] aggregation policy가 존재한다.
- [ ] majority vote, weighted merge, expert-first, safety-first 등 최소 하나 이상의 정책이 있다.
- [ ] policy를 문서화한다.
- [ ] policy가 ad-hoc if-else가 아니라 명시적 규칙으로 존재한다.

### 11.3 `fanin_hold`
- [ ] 일부 branch만 미충족일 때 fan-in을 보류할 수 있다.
- [ ] fan-in 전에 branch별 retry를 허용할 수 있다.
- [ ] fanin_hold 이유를 artifact에 남긴다.

### 11.4 Conflict Handling
- [ ] branch 간 상충 결과를 감지한다.
- [ ] conflict resolution reason을 남긴다.
- [ ] safety-critical conflict는 stop/escalate가 가능하다.

---

## 12. Trace / Lineage Alignment

### 12.1 Run IDs
- [ ] `workflow_run_id`가 있다.
- [ ] `step_run_id`가 있다.
- [ ] branch run id가 필요하면 별도 구분된다.

### 12.2 Event Log
- [ ] event log가 있다.
- [ ] 최소 `STEP_STARTED`가 있다.
- [ ] 최소 `OUTPUT_CAPTURED`가 있다.
- [ ] 최소 `NORMALIZATION_COMPLETED`가 있다.
- [ ] 최소 `GRADE_COMPLETED`가 있다.
- [ ] 최소 `DECISION_MADE`가 있다.
- [ ] 최소 `HANDOFF_CREATED` 또는 equivalent가 있다.

### 12.3 Traceability
- [ ] 어떤 raw output에서 어떤 bridge_eval이 나왔는지 추적 가능하다.
- [ ] 어떤 bridge_eval에서 어떤 retry_spec이 나왔는지 추적 가능하다.
- [ ] 어떤 handoff_packet이 어떤 downstream skill로 갔는지 추적 가능하다.
- [ ] final stop/retry/reroute가 왜 났는지 근거가 남는다.

---

## 13. Failure Taxonomy Alignment

### 13.1 최소 taxonomy
- [ ] `recoverable`
- [ ] `irrecoverable`
- [ ] `ambiguous`
- [ ] `external_blocked`
- [ ] `no_progress`
- [ ] `unsafe`

### 13.2 Taxonomy Usage
- [ ] failure type이 `bridge_eval.json`에 기록된다.
- [ ] failure type이 retry/reroute/stop decision에 반영된다.
- [ ] malformed output과 missing artifact를 구분한다.
- [ ] unsafe output을 별도 처리한다.

### 13.3 Misclassification 방지
- [ ] external outage를 model failure로 오판하지 않는다.
- [ ] ambiguous output을 pass로 오판하지 않는다.
- [ ] recoverable failure를 곧바로 stop으로 보내지 않는다.

---

## 14. Robustness Alignment

### 14.1 Misleading Completion Claim
- [ ] completion claim만으로 성공 처리하지 않는다.
- [ ] evidence 부족 시 retry/stop/escalate가 가능하다.
- [ ] artifact existence를 더 강한 신호로 본다.

### 14.2 Malformed Output
- [ ] partial JSON / broken JSON 감지 가능
- [ ] malformed natural language format 감지 가능
- [ ] downstream contract violation 감지 가능

### 14.3 Unsafe / High-Risk Output
- [ ] unsafe output을 별도 taxonomy로 처리한다.
- [ ] unsafe output이 자동 handoff되지 않는다.
- [ ] 필요한 경우 escalate 또는 stop으로 간다.

---

## 15. Integration Alignment

### 15.1 `eval-runner`와의 연결
- [ ] workflow_run 결과를 eval-runner가 소비 가능한 형태로 저장할 수 있다.
- [ ] 최소한 JSON artifact가 있다.
- [ ] step-level trace를 별도 수집 가능하다.
- [ ] fan-in 결과를 summary로 낼 수 있다.

### 15.2 `skill-acceptance-gate`와의 관계
- [ ] acceptance gate와 책임이 섞이지 않는다.
- [ ] 이 Skill은 handoff readiness를 본다.
- [ ] acceptance gate는 개별 skill readiness를 본다.
- [ ] 둘을 조합할 수 있는 필드가 있다.

### 15.3 `codex-tmux-orchestrator`와의 관계
- [ ] runtime output consumer로 동작 가능하다.
- [ ] raw logs만 읽는 게 아니라 structured result artifacts도 읽을 수 있다.
- [ ] runtime execution primitive를 다시 구현하지 않는다.

---

## 16. CLI / Script Surface Alignment

### 16.1 필수 scripts
- [ ] `bridge_eval_runner.py`
- [ ] `output_type_classifier.py`
- [ ] `nl_output_extractor.py`
- [ ] `decision_engine.py`
- [ ] `retry_spec_builder.py`
- [ ] `handoff_packet_builder.py`
- [ ] `fanin_aggregator.py`
- [ ] `loop_controller.py`

### 16.2 CLI usability
- [ ] human-readable summary 출력이 있다.
- [ ] machine-readable JSON 출력이 있다.
- [ ] dry-run 옵션이 있으면 좋다.
- [ ] non-interactive 사용이 가능하다.

### 16.3 Composition readiness
- [ ] classifier -> extractor -> grader -> decision engine 조합이 가능하다.
- [ ] 부분 실행도 가능하다.
- [ ] full pipeline execution도 가능하다.

---

## 17. Testing Alignment

### 17.1 Positive Tests
- [ ] structured_json output -> pass -> handoff_packet 생성
- [ ] natural_language output -> extract -> grade -> retry decision
- [ ] evaluator feedback -> retry_spec 생성
- [ ] parallel branch 2개 -> fan-in summary 생성
- [ ] loop iteration 1회 이상 정상 작동

### 17.2 Negative Tests
- [ ] missing raw_output -> external_blocked or failure
- [ ] malformed JSON -> retry/reroute
- [ ] completion claim only -> pass 금지
- [ ] no evidence -> pass 금지
- [ ] repeated same unmet condition -> no_progress 감지
- [ ] conflicting branch outputs -> fanin_hold or escalate

### 17.3 Regression Tests
- [ ] natural-language normalization fields regression
- [ ] retry_spec schema regression
- [ ] handoff_packet schema regression
- [ ] decision set regression
- [ ] event log field regression

---

## 18. Documentation Alignment

### 18.1 Required docs
- [ ] `Boundary-of-Responsibility`가 canonical이다.
- [ ] reference 문서와 checklist가 존재한다.
- [ ] knowledge base와 checklist가 서로 모순되지 않는다.
- [ ] `WORKFLOW_MODES.md`를 추가할 준비가 되어 있다.
- [ ] `DECISION_ALGEBRA.md`를 추가할 준비가 되어 있다.
- [ ] `ARTIFACT_SCHEMA.md`를 추가할 준비가 되어 있다.

### 18.2 Doc-code consistency
- [ ] 문서의 decision set과 코드가 일치한다.
- [ ] 문서의 artifact schema와 코드가 일치한다.
- [ ] 문서의 failure taxonomy와 코드가 일치한다.
- [ ] 문서의 workflow modes와 코드가 일치한다.
- [ ] 문서의 retry policy와 코드가 일치한다.

---

## 19. Minimal Acceptance Gates

### Gate 1. Boundary Gate
- [ ] 이 Skill이 생성자나 runtime executor로 변질되지 않는다.

### Gate 2. Natural-Language Gate
- [ ] 자연어 출력은 raw 그대로 downstream에 가지 않는다.

### Gate 3. Retry Gate
- [ ] retry는 항상 repair instructions와 함께 발생한다.

### Gate 4. Decision Gate
- [ ] 모든 step 결과는 최소 하나의 explicit decision으로 귀결된다.

### Gate 5. Trace Gate
- [ ] decision과 artifacts lineage가 추적 가능하다.

### Gate 6. Fan-in Gate
- [ ] parallel branch는 정규화 없이 합쳐지지 않는다.

### Gate 7. Loop Gate
- [ ] evaluator-optimizer loop는 max_iterations 또는 no-progress 조건이 있다.

---

## 20. v0.1 Minimum Pass

아래 항목을 모두 충족하면 `v0.1 usable`로 본다.

- [ ] sequential mode 동작
- [ ] natural-language extraction 동작
- [ ] `bridge_eval.json` 생성
- [ ] `retry_spec.json` 생성
- [ ] `handoff_packet.json` 생성
- [ ] `pass/retry/reroute/stop` 최소 4개 decision 동작
- [ ] blind retry 금지
- [ ] no-progress 감지 기초 구현
- [ ] event log 존재
- [ ] downstream canonical input이 raw output이 아니라 handoff packet임

## 21. v0.2 Operational Pass

- [ ] full evaluator-optimizer loop
- [ ] fanout/fanin_hold 동작
- [ ] parallel aggregation policy 2개 이상
- [ ] richer failure taxonomy
- [ ] eval-runner 연결 자동화

## 22. v0.3 Trusted Pass

- [ ] 실제 multi-skill tmux runs에 사용
- [ ] bug patterns 축적
- [ ] repair retry 성공 패턴 축적
- [ ] ambiguous/misleading output robustness 검증

---

## 23. 구현 전 반드시 결정할 15가지

- [ ] output type taxonomy
- [ ] canonical artifact names
- [ ] bridge_eval schema
- [ ] retry_spec schema
- [ ] handoff_packet schema
- [ ] decision set
- [ ] failure taxonomy
- [ ] score / confidence semantics
- [ ] next_step_ready semantics
- [ ] max_retries
- [ ] max_iterations
- [ ] no-progress rule
- [ ] fan-in policy set
- [ ] event log schema
- [ ] eval-runner handoff format

---

## 24. 최종 판정 질문

아래 질문에 모두 `예`라고 답할 수 있어야 이 Skill 구현은 knowledge base와 정합하다고 본다.

- [ ] 이 구현은 여러 workflow mode를 실제로 구분해 다루는가?
- [ ] 이 구현은 자연어 출력을 claim으로 취급하고 정규화하는가?
- [ ] 이 구현은 blind retry를 금지하고 repair retry를 수행하는가?
- [ ] 이 구현은 next-step handoff를 canonical packet으로 만드는가?
- [ ] 이 구현은 parallel branch 결과를 fan-in 전에 정규화하는가?
- [ ] 이 구현은 run/step/decision trace를 남기는가?
- [ ] 이 구현은 misleading completion claim을 직접 성공으로 보지 않는가?
- [ ] 이 구현은 runtime/worktree/task ownership을 침범하지 않는가?

이 중 하나라도 `아니오`면, `skill-workflow-bridge-eval`은 아직 구현 정합성이 부족하다고 판단해야 한다.
