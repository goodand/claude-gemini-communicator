# skill-workflow-bridge-eval 정합성 평가 체크리스트

> 5개 reference 문서(Boundary, Concept, Checklist, Knowledge Base, Reference) 간
> 그리고 이 skill과 외부 skill 간의 **내부 정합성**을 검증한다.
> SKILL.md/scripts/evals 구현 전에 이 체크리스트를 통과해야 한다.

---

## A. 정체성·책임 경계 정합

이 skill이 "무엇인지"와 "무엇이 아닌지"가 문서 전체에서 일관되는가.

- [ ] **A-01**: "bridge + eval + decision controller"로 일관 정의 (Boundary §직접소유, Reference §3, Checklist §2)
- [ ] **A-02**: "NOT generator, NOT executor, NOT worktree manager" 금지 목록 3문서 일치 (Boundary §절대불가, Reference §3, Checklist §2)
- [ ] **A-03**: "output 의미를 평가하고 다음 흐름을 결정" — 1문장 정의가 Boundary와 Reference §3 one-liner에서 동일
- [ ] **A-04**: tmux 세션 생성/종료, worktree 생성/삭제, task-packet 작성을 이 skill이 하지 않음이 명시 (Boundary §절대불가)
- [ ] **A-05**: skill-acceptance-gate와의 구분: gate=skill 작동 여부, this=handoff 준비 여부 (Boundary, Reference §5, Checklist §15)
- [ ] **A-06**: eval-runner와의 구분: this=step 결과+결정 추적(upstream), eval-runner=실험 실행+보고(downstream) (Reference §5, Checklist §15)
- [ ] **A-07**: codex-tmux-orchestrator와의 구분: this=output consumer+decider, orchestrator=executor (Boundary, Reference §5)

---

## B. 의사결정 집합(Decision Set) 정합

8개 결정이 모든 문서에서 동일하게 정의되는가.

- [ ] **B-01**: 정확히 8개: `pass`, `retry`, `reroute`, `loop`, `stop`, `escalate`, `fanout`, `fanin_hold` (Boundary, Reference §12, Checklist §8)
- [ ] **B-02**: 각 결정의 트리거 조건이 Reference §12.1~12.8과 Checklist §8에서 모순 없음
- [ ] **B-03**: `pass` 조건 — contract 충족 + next_step_ready=true + evidence 충분 + ambiguity 낮음 (Reference §12.1, Concept)
- [ ] **B-04**: `retry` 조건 — repairable + unmet conditions fixable (Reference §12.2, Concept 재시도 규칙)
- [ ] **B-05**: `reroute` 조건 — 동일 실패 2-3회 반복 또는 현재 skill 부적합 (Reference §12.3, Concept)
- [ ] **B-06**: `loop` 조건 — score < threshold + repairable + max_iter 미도달 + no_progress=false (Reference §12.4)
- [ ] **B-07**: `stop` 조건 — unsafe, upstream 누락, 전제 붕괴, 복구 불가 (Reference §12.5, Concept)
- [ ] **B-08**: `escalate` 조건 — 정책 충돌, 극단적 모호성, 고위험 (Reference §12.6)
- [ ] **B-09**: `fanout`/`fanin_hold` — 다관점 필요 / 브랜치 미완료 (Reference §12.7~12.8, Checklist §11)
- [ ] **B-10**: 무효 결정 방지 규칙 3문서 일치: next_step_ready=false → pass 불가, retryable=false → retry 불가, no_progress=true → 무한 loop 불가 (Checklist §8)

---

## C. Canonical Artifact 스키마 정합

4개 산출물의 필드가 모든 문서에서 동일한가.

### C-1. `bridge_eval.json`
- [ ] **C-01**: 필수 필드 일치 — `run_id`, `step_id`, `skill_name`, `output_type`, `pass`, `score`, `confidence`, `failure_type`, `recommended_action`, `unmet_conditions`, `evidence`, `next_step_ready` (Reference §10.3, Checklist §6)
- [ ] **C-02**: `failure_type` 값이 Failure Taxonomy(§F)와 일치
- [ ] **C-03**: `recommended_action` 값이 Decision Set(§B) 8개 중 하나

### C-2. `retry_spec.json`
- [ ] **C-04**: 필수 필드 일치 — `retryable`, `retry_count`, `max_retries`, `failure_type`, `unmet_conditions`, `repair_instructions`, `no_progress_signal` (Reference §10.4, Checklist §6)
- [ ] **C-05**: `repair_instructions`가 빈 배열이면 blind retry → 금지 규칙 위반 (Concept, Reference §13)

### C-3. `handoff_packet.json`
- [ ] **C-06**: 필수 필드 일치 — `ready`, `decision`, `next_skill`, `normalized_summary`, `key_outputs`, `missing_items`, `confidence`, `source_artifacts` (Reference §10.5, Checklist §6)
- [ ] **C-07**: downstream은 `handoff_packet.json`을 canonical input으로 사용, `raw_output.md`를 직접 읽지 않음 (Boundary, Reference §10, Checklist §6)

### C-4. `raw_output.md`
- [ ] **C-08**: forensic source로만 사용, downstream canonical input 아님 (Reference §10.2, Boundary)
- [ ] **C-09**: 원본 무수정 보존 원칙 명시 (Reference §10.2)

---

## D. Workflow Mode 정합

3개 모드의 정의·계약이 문서 전체에서 일관되는가.

### D-1. Sequential (A→B→C)
- [ ] **D-01**: "A 결과 평가 → B 입력 계약 충족 확인 → handoff_packet 생성 or retry/reroute" 흐름이 Reference §6.1과 Checklist §3에서 일치
- [ ] **D-02**: A output이 B의 required fields를 포함하는지 검증 (Reference §6.1)

### D-2. Parallel (fan-out + fan-in)
- [ ] **D-03**: 브랜치별 bridge_eval 개별 생성 → 정규화 → fan-in 정책 적용 흐름 (Reference §6.2, §14, Checklist §11)
- [ ] **D-04**: fan-in 정책 종류가 Reference §14과 Checklist §11에서 일치: majority, weighted, expert-first, safety-first, structured-first
- [ ] **D-05**: `fanin_hold` 결정이 브랜치 미완료/재시도 필요/confidence 불일치 시 발동 (Reference §12.8, Checklist §11)

### D-3. Evaluator-Optimizer (Loop)
- [ ] **D-06**: generation → evaluation → bridge_eval → retry_spec → loop_state 흐름 (Reference §6.3, §15)
- [ ] **D-07**: loop_state 필드: `loop_id`, `iteration`, `max_iterations`, `target_threshold`, `current_score`, `no_progress_signal`, `last_decision` (Reference §15)
- [ ] **D-08**: 종료 조건: retry_count ≥ max_retries, score ≥ threshold, no_progress=true, failure_type=irrecoverable (Reference §13, §15)

---

## E. Natural Language 처리 정합

"자연어 출력 = 주장(claim), 결과(result) 아님" 원칙이 일관되는가.

- [ ] **E-01**: "NL output은 CLAIM이지 RESULT가 아니다" 원칙이 Concept 핵심, Reference §9, Checklist §5에서 동일
- [ ] **E-02**: 처리 체인: raw → extract → grade → decide → handoff_packet (Concept, Reference §11, Checklist §7)
- [ ] **E-03**: extract 필드 7개 일치: `task_completion_claim`, `key_outputs`, `missing_items`, `open_questions`, `evidence`, `confidence`, `next_step_ready` (Concept, Reference §11.1, Checklist §7)
- [ ] **E-04**: grade 기준 7개 일치: required items, format, evidence sufficiency, ambiguity, self-contradiction, handoff readiness, repair feasibility (Concept, Reference §11.2, Checklist §7)
- [ ] **E-05**: "완료했습니다" 같은 completion claim만으로 pass 불가 — artifact 존재 > 자기 보고 (Concept, Reference §9, KB 실패 모드 #1)
- [ ] **E-06**: evidence 우선순위: 파일 존재, artifact 경로 >> 자기 보고 (Checklist §7)

---

## F. Failure Taxonomy 정합

실패 유형이 모든 문서에서 동일하게 분류되는가.

- [ ] **F-01**: 최소 6개 유형: `recoverable`, `irrecoverable`, `ambiguous`, `external_blocked`, `no_progress`, `unsafe` (Reference, Checklist §13)
- [ ] **F-02**: `recoverable` → retry 후보 (Reference §12.2, §13)
- [ ] **F-03**: `irrecoverable` → stop (Reference §12.5, §13)
- [ ] **F-04**: `ambiguous` → escalate (Reference §12.6, §13)
- [ ] **F-05**: `no_progress` → loop 종료 signal (Reference §15, Checklist §13)
- [ ] **F-06**: `unsafe` → stop 또는 escalate (Reference §12.5~12.6, Checklist §13)
- [ ] **F-07**: Boundary의 "감지해야 하지만 직접 해결 불가" 목록(runtime crash, worktree corruption, git conflict, API outage)이 `external_blocked`에 매핑

---

## G. Retry 정책 정합

"blind retry 금지" 원칙이 모든 곳에서 일관되는가.

- [ ] **G-01**: blind retry(동일 입력 재실행) 금지가 Concept, Reference §13, Checklist §9에서 동일
- [ ] **G-02**: 모든 retry에 `retry_spec.json` 동반 필수 (Reference §13, Checklist §9)
- [ ] **G-03**: retry_spec 필수 내용: unmet_conditions + repair_instructions + 이전 시도 대비 delta (Concept, Reference §13, Checklist §9)
- [ ] **G-04**: retry_count 증가 규칙: 매 retry마다 +1 (Reference §13, Checklist §9)
- [ ] **G-05**: 동일 unmet_conditions 2-3회 반복 → reroute 전환 (Concept, Reference §12.3, §13)
- [ ] **G-06**: max_retries 초과 → 더 이상 retry 불가, stop 또는 reroute (Reference §13)

---

## H. Trace·Lineage 정합

추적 ID와 이벤트 로그가 일관되는가.

- [ ] **H-01**: `workflow_run_id` + `step_run_id` 식별자 쌍이 Reference §17, Checklist §12에서 일치
- [ ] **H-02**: 이벤트 로그 최소 6개: `STEP_STARTED`, `OUTPUT_CAPTURED`, `NORMALIZATION_COMPLETED`, `GRADE_COMPLETED`, `DECISION_MADE`, `HANDOFF_CREATED` (Reference §17, Checklist §12)
- [ ] **H-03**: 추적 체인: raw_output → bridge_eval → retry_spec → handoff_packet → downstream (Reference §17, Checklist §12)
- [ ] **H-04**: "왜 다음 단계를 이렇게 결정했는가"를 기록 (실행 내용이 아님) (Reference §17)

---

## I. Output Type 분류 정합

4가지 출력 유형이 일관되는가.

- [ ] **I-01**: 4개 유형: `script_result`, `structured_json`, `natural_language`, `mixed` (Concept, Reference §8, Checklist §5)
- [ ] **I-02**: 유형별 평가 방법 차별화: script=exit code+artifact, json=schema+fields, nl=extract→grade, mixed=layered (Reference §8, Checklist §5)
- [ ] **I-03**: 분류가 평가 전 별도 단계로 수행 (Checklist §5)
- [ ] **I-04**: 분류에 confidence + reasoning 포함 (Checklist §5)

---

## J. 외부 Skill 연동 정합

다른 skill과의 인터페이스가 일관되는가.

- [ ] **J-01**: agent-task-packet의 `done_definition`/`required_checks`를 downstream contract으로 참조 가능 (Boundary 읽기 전용)
- [ ] **J-02**: codex-worktree-dispatch의 `status` 전이와 이 skill의 decision이 매핑 가능: pass→complete, retry→running(재시도), stop→failed
- [ ] **J-03**: eval-runner에 JSON artifact + step-level trace를 제공 (Checklist §15)
- [ ] **J-04**: handoff_packet.json이 downstream skill의 입력으로 직접 사용 가능한 구조 (Reference §10.5, Boundary)
- [ ] **J-05**: skill-creation-process의 Progressive Context Injection 원칙 준수: SKILL.md(~45줄) → scripts/(--help) → references/(깊은 컨텍스트)

---

## K. Script 커버리지 정합

Reference와 Checklist에서 요구하는 스크립트가 일치하는가.

- [ ] **K-01**: 필수 스크립트 8개 목록이 Reference §23과 Checklist §16에서 일치:
  1. `bridge_eval_runner.py` — output → eval
  2. `output_type_classifier.py` — 유형 분류
  3. `nl_output_extractor.py` — NL → 구조화 추출
  4. `decision_engine.py` — eval → 결정
  5. `retry_spec_builder.py` — unmet → repair spec
  6. `handoff_packet_builder.py` — canonical downstream input
  7. `fanin_aggregator.py` — 병렬 브랜치 합산
  8. `loop_controller.py` — evaluator-optimizer loop 관리
- [ ] **K-02**: 각 스크립트의 입출력이 Canonical Artifact 스키마(§C)와 일치
- [ ] **K-03**: 모든 스크립트가 exit code 계약 준수 (0=성공, 1=실패)
- [ ] **K-04**: `--help` 지원 필수

---

## L. v0.1 최소 범위 정합

v0.1에서 반드시 구현할 항목이 문서 간 일치하는가.

- [ ] **L-01**: Sequential 모드 동작 (Reference §21, Checklist §20)
- [ ] **L-02**: NL extraction 동작 (Reference §21, Checklist §20)
- [ ] **L-03**: bridge_eval.json, retry_spec.json, handoff_packet.json 생성 (Checklist §20)
- [ ] **L-04**: 최소 4개 결정 동작: `pass`, `retry`, `reroute`, `stop` (Checklist §20)
- [ ] **L-05**: blind retry 금지 구현 (Checklist §20)
- [ ] **L-06**: no-progress 감지 (기본) (Checklist §20)
- [ ] **L-07**: 이벤트 로그 존재 (Checklist §20)
- [ ] **L-08**: downstream canonical input = handoff_packet (raw 아님) (Checklist §20)

---

## M. Knowledge Base 커버리지 정합

KB의 8개 설계 차원이 Reference/Checklist에 모두 반영되었는가.

- [ ] **M-01**: D1 Workflow Mode — Reference §6, Checklist §3에 반영
- [ ] **M-02**: D2 Output Type — Reference §8, Checklist §5에 반영
- [ ] **M-03**: D3 Handoff Readiness — Reference §10.5, Checklist §6에 반영
- [ ] **M-04**: D4 Retry Quality — Reference §13, Checklist §9에 반영
- [ ] **M-05**: D5 Decision Algebra — Reference §12, Checklist §8에 반영
- [ ] **M-06**: D6 Trace/Lineage — Reference §17, Checklist §12에 반영
- [ ] **M-07**: D7 Fan-in/Aggregation — Reference §14, Checklist §11에 반영
- [ ] **M-08**: D8 Robustness — Reference §9(NL=claim), Checklist §14에 반영

---

## N. 15개 사전 설계 결정 확정 여부

구현 전에 확정해야 하는 설계 결정 (Checklist §23).

- [ ] **N-01**: Output type taxonomy 확정 (4개: script_result/structured_json/natural_language/mixed)
- [ ] **N-02**: Canonical artifact 파일명 확정 (raw_output.md, bridge_eval.json, retry_spec.json, handoff_packet.json)
- [ ] **N-03**: bridge_eval.json 스키마 확정
- [ ] **N-04**: retry_spec.json 스키마 확정
- [ ] **N-05**: handoff_packet.json 스키마 확정
- [ ] **N-06**: Decision set 확정 (8개)
- [ ] **N-07**: Failure taxonomy 확정 (6개)
- [ ] **N-08**: score/confidence 의미론 확정 (0.0~1.0 범위, threshold 기본값)
- [ ] **N-09**: next_step_ready 의미론 확정 (boolean, 어떤 조건이면 true)
- [ ] **N-10**: max_retries 기본값 확정
- [ ] **N-11**: max_iterations(loop) 기본값 확정
- [ ] **N-12**: no-progress 규칙 확정 (동일 unmet 반복, score 개선 < ε)
- [ ] **N-13**: fan-in policy set 확정 (majority/weighted/expert-first/safety-first)
- [ ] **N-14**: event log 스키마 확정
- [ ] **N-15**: eval-runner handoff format 확정

---

## O. 최종 판정 질문 (Checklist §24)

모두 "예"여야 구현 착수 가능.

- [ ] **O-01**: 복수의 workflow mode를 실제로 처리하는가?
- [ ] **O-02**: 자연어 출력을 claim으로 취급하고 정규화하는가?
- [ ] **O-03**: blind retry를 금지하고 repair retry를 수행하는가?
- [ ] **O-04**: 다음 단계 handoff를 canonical packet으로 전달하는가?
- [ ] **O-05**: 병렬 브랜치를 정규화한 후 fan-in하는가?
- [ ] **O-06**: run/step/decision trace를 보존하는가?
- [ ] **O-07**: 오해의 소지가 있는 completion claim을 직접 성공으로 처리하지 않는가?
- [ ] **O-08**: runtime/worktree/task 소유권을 침범하지 않는가?

---

## 사용법

1. **구현 전**: §N(사전 설계 결정) 전체 확정 → §O(최종 판정) 전체 "예" 확인
2. **SKILL.md 작성 시**: §A(정체성), §B(결정), §D(workflow mode) 기준으로 검증
3. **Scripts 작성 시**: §C(artifact 스키마), §K(스크립트 목록) 기준으로 검증
4. **Evals 작성 시**: §L(v0.1 범위) 기준으로 테스트 케이스 설계
5. **실전 테스트 후**: 발견된 불일치를 이 체크리스트에 반영 + `references/troubleshooting.md`에 케이스 추가
