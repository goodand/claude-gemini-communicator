# skill-workflow-bridge-eval Reference
- version: `v0.1.0`
- created_at: `2026-03-16`
- updated_at: `2026-03-16`
- purpose: `skill-workflow-bridge-eval`의 역할, 경계, workflow 모드, 자연어 출력 처리 방식, 재실행 루프, decision model, canonical artifacts, 외부 reference 해석을 매우 구체적으로 고정하기 위한 장문 설계 reference
- status: `active-draft`
- related_skill: `skill-workflow-bridge-eval`
- scope: `skills 간 handoff·판정·재시도·우회·fan-in을 관리하는 workflow control layer`
- non_scope: `개별 skill 자체 구현`, `tmux 세션 실행 primitive`, `worktree canonical ownership`, `최종 acceptance grading 전체 대체`

---

## 1. 이 문서의 목적

이 문서는 `skill-workflow-bridge-eval`을 단순한 결과 집계기가 아니라, **여러 Skill 사이의 흐름을 제어하고 다음 Skill 실행을 결정하는 meta-skill**로 설계하기 위한 reference 문서다.

이 Skill이 실제로 해결하려는 문제는 아래와 같다.

1. 앞 Skill의 출력이 다음 Skill에 바로 넘길 수 있는 상태인지 판단해야 한다.
2. 출력이 조건 미충족이면 그냥 실패로 끝낼 게 아니라, **재실행 루프**를 돌릴지 결정해야 한다.
3. 출력이 자연어일 때는 그대로 handoff 하면 안 되고, 정규화·평가·판정 단계를 거쳐야 한다.
4. 여러 Skill을 순차·병렬·평가자-최적화 구조로 연결할 때, 각 단계의 입력/출력/로그/판정을 추적해야 한다.
5. 최종적으로는 이 흐름을 `eval-runner` 또는 유사한 평가 계층과 연결해, 어느 지점에서 pipeline이 막히는지 볼 수 있어야 한다.

즉 이 Skill의 본질은 "생성"보다 **harness**, "실행"보다 **bridge**, "단순 fan-in"보다 **decision-and-handoff control**에 있다.

---

## 2. 왜 이 Skill이 필요한가

일반적인 multi-skill pipeline에서 가장 자주 깨지는 지점은 개별 Skill의 성능보다도, **한 Skill의 출력이 다음 Skill의 입력 계약을 만족하는지 검증되지 않은 채 넘어가는 순간**이다.

예를 들어 아래 같은 상황이 자주 발생한다.

### 2.1 순차 워크플로우에서의 깨짐
- Skill A가 초안을 생성한다.
- Skill B는 그 초안을 구조화된 JSON이나 특정 섹션 형식으로 기대한다.
- 그런데 Skill A 출력이 자연어 설명 중심이라면, Skill B는 입력을 제대로 소비하지 못한다.
- 문제는 Skill A가 “완료했습니다”라고 말했기 때문에 상위 orchestrator가 성공으로 오인하기 쉽다는 점이다.

### 2.2 병렬 워크플로우에서의 깨짐
- 여러 Skill이 서로 다른 관점에서 동시에 결과를 낸다.
- 어떤 결과는 구조화돼 있고, 어떤 결과는 장문의 자연어다.
- 이걸 fan-in할 때 aggregation 로직이 없다면, 단순 concat 또는 첫 번째 우선 방식으로 흐르게 된다.
- 이 경우 실질적으로는 quality loss와 provenance loss가 같이 생긴다.

### 2.3 evaluator-optimizer 구조에서의 깨짐
- 생성 Skill이 결과를 낸다.
- 평가 Skill이 “불충분”이라고 말한다.
- 그런데 그 불충분 사유가 구조화되지 않으면, 다음 재실행은 blind retry가 된다.
- blind retry는 같은 실패를 반복할 가능성이 높다.

즉, 이 Skill은 단순 orchestration이 아니라 **출력의 해석, 판정, 정규화, handoff packet 생성, retry guidance 생성**을 담당해야 한다.

---

## 3. 이 Skill의 핵심 정체성

### 3.1 이 Skill이 아닌 것
이 Skill은 아래가 아니다.

- tmux session manager
- worktree manager
- task packet authoring tool
- acceptance grader 전체를 대체하는 tool
- code execution harness 자체
- data pipeline executor 자체
- single-skill evaluator

### 3.2 이 Skill인 것
이 Skill은 아래 역할을 가져야 한다.

- 여러 Skill의 출력과 실행 로그를 읽고 **다음 실행 결정**을 내리는 workflow control layer
- Skill 간 output contract mismatch를 감지하는 bridge layer
- 출력이 자연어일 때 `extract -> grade -> decide -> retry_spec -> handoff_packet`으로 정규화하는 layer
- sequential, parallel, evaluator-optimizer 세 가지 workflow를 하나의 decision algebra 위에서 다루는 meta-skill
- 개별 step 결과를 run record와 event log 형태로 추적하는 layer
- 최종적으로는 `eval-runner`나 그와 유사한 평가 실행기와 연결되는 fan-in bridge

### 3.3 한 줄 정의
`skill-workflow-bridge-eval`은 **앞 단계 Skill의 출력과 실행 상태를 평가해, 다음 Skill 실행·재실행·우회·중단·fan-in을 결정하고 그 흐름을 기록하는 workflow control skill**이다.

---

## 4. 이 Skill이 직접 해결해야 하는 핵심 질문

이 Skill이 제대로 설계되려면 아래 질문에 명확히 답해야 한다.

1. 현재 step 출력은 다음 step에 넘길 만큼 충분한가?
2. 부족하다면 그 부족은 retry로 회복 가능한가, 아니면 reroute가 필요한가?
3. 자연어 출력에서 실제 handoff 가능한 핵심 정보는 무엇인가?
4. 어느 정도까지 evidence가 있어야 `pass`로 볼 것인가?
5. 같은 실패가 반복될 때 언제 blind retry를 중단하고 다른 route로 바꿀 것인가?
6. parallel fan-out 결과를 어떤 기준으로 fan-in할 것인가?
7. evaluator-optimizer loop는 언제 종료해야 하는가?
8. 어느 artifact를 다음 Skill이 source-of-truth로 읽어야 하는가?

---

## 5. 기존 Skill들과의 관계

### 5.1 `skill-acceptance-gate`와의 관계
`skill-acceptance-gate`가 개별 Skill의 작동 기준을 평가하는 meta-skill이라면, `skill-workflow-bridge-eval`은 **여러 Skill을 연결한 실행 흐름 전체에서 bridge와 decision을 담당**한다.

정리하면:
- `skill-acceptance-gate` = “이 Skill 자체가 잘 동작하는가?”
- `skill-workflow-bridge-eval` = “이 Skill의 출력이 다음 Skill로 제대로 흘러갈 수 있는가?”

### 5.2 `eval-runner`와의 관계
`eval-runner`는 실험 실행과 평가 아티팩트 생성에 강하다.  
`skill-workflow-bridge-eval`은 그 앞단에서 **각 step의 outcome과 decision trace를 구조화해서 eval-runner가 소비할 수 있게 연결하는 bridge** 역할을 한다.

즉:
- `eval-runner` = 실행/측정/리포트
- `skill-workflow-bridge-eval` = step-to-step handoff 평가 + decision trace + fan-in

### 5.3 `codex-tmux-orchestrator`와의 관계
`codex-tmux-orchestrator`는 실제 Codex 세션 실행을 담당한다.  
`skill-workflow-bridge-eval`은 그 실행 결과를 읽고 다음 Skill을 돌릴지 판단한다.

즉:
- `codex-tmux-orchestrator` = runtime executor
- `skill-workflow-bridge-eval` = runtime output consumer + next-step decider

### 5.4 `codex-task-packet` / `codex-worktree-dispatch`와의 관계
이 둘이 task와 execution placement를 고정한다면, `skill-workflow-bridge-eval`은 **실행 후 result lineage와 next-step lineage**를 고정한다.

---

## 6. workflow 모드 정의

이 Skill은 최소 세 가지 workflow 모드를 지원해야 한다.

---

## 6.1 Sequential Workflow

### 정의
A -> B -> C처럼 단계가 선형으로 흐르는 구조다.

### 적합한 경우
- 단계 간 의존성이 명확할 때
- upstream 산출물이 downstream 입력 계약에 강하게 묶여 있을 때
- 결과를 한 단계씩 검증하고 축적해야 할 때

### 대표 예시
- 문서 추출 -> 구조화 -> 검증
- 분석 초안 -> 체크리스트 생성 -> 최종 보고
- 코드 변경안 생성 -> 테스트 명령 생성 -> 실행 검토

### 이 Skill이 해야 할 일
- step A 결과를 평가한다.
- A 결과가 B 입력 계약을 만족하는지 본다.
- 만족하면 `handoff_packet`을 생성해 B로 넘긴다.
- 미충족이면 `retry` 또는 `reroute`를 결정한다.

### Sequential에서 중요한 판정 질문
- 현재 step 출력이 downstream skill이 요구하는 필드를 포함하는가?
- 결과가 자연어라면 downstream이 이해 가능한 구조로 정규화되었는가?
- step A를 다시 돌리는 것이 더 나은가, 아니면 다른 skill로 우회하는 것이 더 나은가?

---

## 6.2 Parallel Workflow

### 정의
독립적이거나 준독립적인 작업을 동시에 여러 Skill에 fan-out하고, 결과를 fan-in하는 구조다.

### 적합한 경우
- 한 문제를 여러 관점에서 동시에 보고 싶을 때
- 여러 평가자 또는 specialist skill이 각기 다른 책임을 맡을 때
- 비교/집계/가중치 결합이 필요할 때

### 대표 예시
- 코드 리뷰: 보안 / 성능 / 스타일 병렬
- 문서 분석: 사실성 / 구조성 / 논리성 병렬
- 계획 검토: 구현성 / 위험성 / 일정성 병렬

### 이 Skill이 해야 할 일
- fan-out 단위를 정의한다.
- 각 Skill 실행 결과를 표준 artifact로 수집한다.
- 각 결과의 신뢰도, coverage, 충돌 여부를 본다.
- fan-in policy에 따라 aggregation한다.

### Parallel에서 중요한 판정 질문
- 모든 branch output을 동등하게 취급할 것인가?
- 특정 evaluator에 가중치를 둘 것인가?
- 서로 충돌하는 결과는 vote로 해결할 것인가, expert-first로 해결할 것인가?
- fan-in 전에 branch별 retry를 돌릴 것인가?

---

## 6.3 Evaluator-Optimizer Workflow

### 정의
생성 Skill과 평가 Skill이 반복 피드백 루프를 돌며 품질 임계값에 도달할 때까지 개선하는 구조다.

### 적합한 경우
- 품질 기준이 높고, 한 번에 완성되기 어려운 작업
- 형식과 내용 둘 다 맞아야 하는 작업
- retry를 무작정 돌리기보다 evaluator feedback을 구조화할 필요가 있는 작업

### 대표 예시
- API 문서 자동 작성
- SQL/스크립트 생성 후 정책/정확성 평가
- 고품질 보고서 작성
- 자연어 초안 -> 평가 -> 수정 반복

### 이 Skill이 해야 할 일
- 생성 결과를 evaluator에게 넘긴다.
- evaluator output을 구조화한다.
- 실패 이유를 `retry_spec`로 바꾼다.
- 최대 반복 횟수, score threshold, no-progress 신호를 관리한다.

### Evaluator-Optimizer에서 중요한 판정 질문
- 현재 실패가 repairable한가?
- 같은 unmet condition이 반복되고 있는가?
- no-progress 상태인가?
- threshold를 넘길 가능성이 아직 있는가?

---

## 6.4 Router / Hybrid Workflow (선택 확장)

v0.1 필수는 아니지만, 장기적으로는 router 또는 hybrid mode도 고려할 수 있다.

### 정의
현재 출력 또는 task 조건에 따라 다음 실행 경로 자체를 바꾸는 구조다.

예:
- 구조화 JSON이면 바로 downstream 실행
- 자연어면 normalize branch로 보냄
- low confidence면 evaluator loop branch로 보냄

이건 결국 `reroute` 결정이 누적되면 자연스럽게 필요해진다.

---

## 7. 핵심 설계 결론

이 Skill은 단순 fan-in skill이 아니라 **bridge + gate + decision + lineage**를 모두 가져야 한다.

가장 중요한 설계 결론은 다음이다.

1. 출력이 자연어든 script result든, 모두 먼저 canonical artifact로 정리돼야 한다.
2. canonical artifact 없이 다음 Skill로 직접 넘기면 안 된다.
3. 미충족 시 retry는 blind retry가 아니라 **repair retry**여야 한다.
4. reroute와 stop은 retry가 실패했을 때의 예외가 아니라, 처음부터 동등한 decision option이어야 한다.
5. 모든 decision은 traceable해야 한다.

---

## 8. 출력 타입 분류

이 Skill은 각 step output을 먼저 분류해야 한다.

### 8.1 최소 분류
- `script_result`
- `structured_json`
- `natural_language`
- `mixed`

### 8.2 분류 이유
출력 타입에 따라 평가 방식이 달라지기 때문이다.

#### `script_result`
- exit code
- stdout/stderr
- 파일 생성 여부
- artifact existence
가 중요하다.

#### `structured_json`
- schema validity
- required field completeness
- value consistency
가 중요하다.

#### `natural_language`
- 포함 항목
- 명확성
- 근거
- 모순 여부
- handoff readiness
가 중요하다.

#### `mixed`
- 설명 + 파일 경로 + 결과 요약이 섞여 있는 경우
- 이 경우도 자연어 처리 규칙이 필요하다.

---

## 9. 자연어 출력 처리 원칙

이 문서에서 가장 중요한 설계 포인트는 여기다.

### 9.1 자연어 출력은 "결과"가 아니라 우선 "주장"이다
자연어는 종종 이렇게 말한다.

- 완료했습니다
- 분석했습니다
- 파일을 생성했습니다
- 충분히 검토했습니다
- 문제를 해결했습니다

하지만 이건 **completion claim**일 뿐이다.  
다음 Skill의 입력으로 바로 넘길 수 있는 보장된 artifact가 아니다.

따라서 자연어 출력은 아래 절차를 반드시 거쳐야 한다.

1. raw 보존
2. 정보 추출
3. 조건 평가
4. decision 생성
5. retry_spec 또는 handoff_packet 생성

### 9.2 자연어 출력은 직접 handoff 금지
자연어 그대로를 downstream skill에 넘기면 다음 문제가 생긴다.

- 필수 정보 누락
- 형식 불일치
- 모호한 지시
- self-report를 성공으로 오인
- evidence 없이 claim만 전달
- 재시도 시 무엇을 고쳐야 하는지 알 수 없음

따라서 canonical intermediate artifact가 필요하다.

---

## 10. 권장 canonical artifact 구조

### 10.1 최소 4개 artifact
1. `raw_output.md`
2. `bridge_eval.json`
3. `retry_spec.json`
4. `handoff_packet.json`

### 10.2 `raw_output.md`
원문 그대로 저장한다.

역할:
- 사람 검토
- forensic debugging
- evaluator input source
- 나중에 extraction 개선 시 재처리 source

### 10.3 `bridge_eval.json`
출력의 평가 결과를 구조화한 핵심 artifact다.

권장 필드 예시:

```json
{
  "run_id": "RUN-001",
  "step_id": "STEP-A",
  "skill_name": "draft-writer",
  "output_type": "natural_language",
  "pass": false,
  "score": 0.62,
  "confidence": 0.74,
  "failure_type": "recoverable",
  "recommended_action": "retry",
  "unmet_conditions": [
    "필수 섹션 누락",
    "다음 Skill 입력 포맷 불일치"
  ],
  "evidence": [
    "원문에 절대경로가 없음",
    "체크리스트 항목 없음"
  ],
  "next_step_ready": false
}
```

### 10.4 `retry_spec.json`
retry를 할 경우, 무엇을 어떻게 고쳐야 하는지 구조화한다.

```json
{
  "retryable": true,
  "retry_count": 1,
  "max_retries": 3,
  "failure_type": "recoverable",
  "unmet_conditions": [
    "필수 섹션 누락",
    "근거 문장 없음"
  ],
  "repair_instructions": [
    "필수 섹션 4개를 모두 포함할 것",
    "각 주장마다 근거 1개 이상 붙일 것",
    "결과 파일 경로를 절대경로로 제시할 것"
  ],
  "no_progress_signal": false
}
```

### 10.5 `handoff_packet.json`
다음 Skill이 읽을 canonical input이다.

```json
{
  "ready": false,
  "decision": "retry",
  "next_skill": null,
  "normalized_summary": "초안은 생성되었으나 필수 절대경로와 체크리스트가 누락됨",
  "key_outputs": [
    "초안 작성"
  ],
  "missing_items": [
    "체크리스트",
    "절대경로"
  ],
  "confidence": 0.62,
  "source_artifacts": [
    "raw_output.md",
    "bridge_eval.json"
  ]
}
```

---

## 11. 자연어 출력에 대한 처리 단계

### 11.1 Extract
자연어에서 다음 정보를 추출한다.

- `task_completion_claim`
- `key_outputs`
- `missing_items`
- `open_questions`
- `evidence`
- `confidence`
- `next_step_ready`

### 11.2 Grade
다음 축으로 평가한다.

- 필수 항목 충족 여부
- 형식 적합성
- 근거 충분성
- 모호성
- self-contradiction
- downstream handoff readiness
- repair 가능성

### 11.3 Decide
grade 결과를 decision으로 바꾼다.

- `pass`
- `retry`
- `reroute`
- `loop`
- `stop`
- `escalate`
- `fanout`
- `fanin_hold`

---

## 12. Decision Algebra

이 Skill은 최소 아래 decision set을 가져야 한다.

### 12.1 `pass`
의미:
- 현재 출력이 다음 Skill 입력 계약을 만족한다.
- handoff 가능하다.

조건 예시:
- 필수 필드 모두 존재
- evidence 충분
- ambiguity 낮음
- next_step_ready=true

### 12.2 `retry`
의미:
- 같은 Skill을 다시 실행하되, repair instructions를 반영해야 한다.

조건 예시:
- 필수 항목 누락
- 형식 불일치
- 근거 부족
- 자연어가 너무 모호함
- recoverable error

### 12.3 `reroute`
의미:
- 같은 Skill 재실행보다 다른 Skill로 보내는 것이 낫다.

조건 예시:
- 현재 Skill 능력 밖
- 동일 실패 반복
- extraction/normalization 전용 Skill이 더 적합
- 병목 원인이 generation이 아니라 format transformation

### 12.4 `loop`
의미:
- evaluator-optimizer 루프로 들어가 계속 개선한다.

조건 예시:
- 품질 점수가 threshold 아래
- repairable함
- max iteration 안쪽
- no-progress 아님

### 12.5 `stop`
의미:
- 더 진행해도 의미가 없거나 unsafe하다.

조건 예시:
- upstream artifact 없음
- 핵심 전제 붕괴
- retry 불가능
- unsafe operation 가능성

### 12.6 `escalate`
의미:
- 사람 또는 상위 orchestrator 판단이 필요하다.

조건 예시:
- 정책 충돌
- 모호성 너무 큼
- conflicting outputs high-stakes

### 12.7 `fanout`
의미:
- 한 결과를 여러 specialist skill로 병렬 평가 또는 병렬 변환에 보낸다.

조건 예시:
- 여러 관점을 동시에 봐야 함
- 단일 evaluator보다 specialist review가 더 적합

### 12.8 `fanin_hold`
의미:
- 병렬 branch 일부가 아직 불완전해서 fan-in을 보류한다.

조건 예시:
- branch별 quality 불균형
- 일부 branch retry 필요
- aggregation 전 confidence mismatch

---

## 13. 재실행 루프 설계

### 13.1 가장 중요한 원칙
재실행은 blind retry가 아니라 **repair retry**여야 한다.

즉 같은 prompt를 다시 던지는 것이 아니라, evaluator가 실패 이유를 구조화한 뒤 그걸 다음 실행 입력에 주입해야 한다.

### 13.2 Blind Retry의 문제
- 같은 실패 반복
- 토큰/시간 낭비
- 실패 원인 trace 손실
- no-progress 판정 불가

### 13.3 Repair Retry의 구조
1. 실패를 구조화한다.
2. unmet_conditions를 적는다.
3. repair_instructions를 만든다.
4. retry_count를 올린다.
5. 다음 실행 입력에 repair context를 주입한다.

### 13.4 Retry 조건
다음은 retry가 적합하다.

- 필수 섹션 누락
- 형식 불일치
- 절대경로/파일명 누락
- 근거 부족
- 자연어가 너무 장황하고 구조화 안 됨
- confidence 낮음
- minor contradiction

### 13.5 Reroute 조건
다음은 reroute가 더 적합하다.

- 같은 unmet condition이 2~3회 반복
- 현재 Skill보다 다른 Skill이 구조 변환에 더 적합
- generation은 되었지만 normalization이 문제
- extraction 전용 evaluator가 필요

### 13.6 Loop 종료 조건
- `retry_count >= max_retries`
- `score >= threshold`
- `no_progress_signal = true`
- `failure_type = irrecoverable`

---

## 14. Parallel Fan-in 설계

### 14.1 병렬 branch의 공통 문제
병렬 결과는 모으는 것보다 **어떻게 모을지**가 더 어렵다.

대표 문제:
- output format이 다름
- 한 branch는 자연어, 다른 branch는 JSON
- 서로 상충하는 결론
- confidence score scale 불일치
- 일부 branch만 충분 조건 충족

### 14.2 fan-in 전에 필요한 것
- branch별 canonical artifact normalization
- branch별 `bridge_eval`
- branch별 confidence/coverage 정렬
- branch별 missing items 파악

### 14.3 fan-in policy 예시
- 다수결
- expert-first
- weighted score
- safety-first veto
- structured-first preference

### 14.4 이 Skill이 해야 할 최소 역할
- branch별 pass/fail 판정
- branch별 retry 가능성 판정
- fan-in 가능 여부 판정
- `fanin_hold` 결정 지원

---

## 15. evaluator-optimizer loop 설계

### 15.1 외부 reference 관점
Anthropic의 workflow 패턴과 mcp-agent의 evaluator-optimizer 패턴은 공통적으로 아래를 강조한다.

- 생성과 평가를 분리할 것
- evaluator feedback을 구체적으로 만들 것
- 종료 조건을 명시할 것
- 무한 루프를 막을 것

### 15.2 이 Skill에 필요한 최소 구조
- `candidate_output`
- `evaluator_feedback`
- `bridge_eval`
- `retry_spec`
- `loop_state`

### 15.3 loop state 예시
```json
{
  "loop_id": "LOOP-01",
  "iteration": 2,
  "max_iterations": 4,
  "target_threshold": 0.85,
  "current_score": 0.71,
  "no_progress_signal": false,
  "last_decision": "loop"
}
```

### 15.4 no-progress 판정 예시
- 같은 unmet condition 반복
- score improvement < epsilon
- output format remains invalid
- same ambiguity persists

---

## 16. State Model

이 Skill 자체도 상태를 가져야 한다.

### 16.1 step-level 상태
- `created`
- `running`
- `output_captured`
- `normalized`
- `graded`
- `decided`
- `handoff_ready`
- `blocked`
- `stopped`

### 16.2 workflow-level 상태
- `idle`
- `sequential_running`
- `parallel_running`
- `fanin_pending`
- `loop_running`
- `completed`
- `failed`
- `stopped`
- `escalated`

### 16.3 중요한 전이
- `output_captured -> normalized`
- `normalized -> graded`
- `graded -> decided`
- `decided -> handoff_ready`
- `decided -> blocked`
- `decided -> retry`
- `decided -> reroute`
- `decided -> stop`

---

## 17. Run Record 설계

이 Skill은 최종적으로 "무엇을 실행했는가"보다 "왜 다음 단계를 그렇게 결정했는가"를 남겨야 한다.

### 17.1 최소 run record
```json
{
  "workflow_run_id": "WF-001",
  "step_run_id": "STEP-RUN-003",
  "workflow_mode": "sequential",
  "upstream_skill": "draft-skill",
  "downstream_skill": "checklist-skill",
  "output_type": "natural_language",
  "decision": "retry",
  "score": 0.62,
  "confidence": 0.74,
  "unmet_conditions": [
    "절대경로 누락",
    "체크리스트 없음"
  ],
  "repair_instructions": [
    "절대경로 포함",
    "체크리스트 추가"
  ],
  "artifacts": {
    "raw_output": "raw_output.md",
    "bridge_eval": "bridge_eval.json",
    "retry_spec": "retry_spec.json"
  }
}
```

### 17.2 event log
가능하면 append-only event log가 있으면 좋다.

예:
- `STEP_STARTED`
- `OUTPUT_CAPTURED`
- `NORMALIZATION_COMPLETED`
- `GRADE_COMPLETED`
- `DECISION_RETRY`
- `HANDOFF_CREATED`

---

## 18. 외부 검색 기반 Reference 해석

아래는 이번 문서에 반영한 핵심 검색 source들이다.

---

## 18.1 Anthropic - Building Effective Agents
- URL: `https://www.anthropic.com/research/building-effective-agents`

### 왜 중요한가
사용자가 직접 언급한 workflow 분류와 가장 가까운 공식 reference다.

### 이 문서에서 가져와야 하는 핵심
- workflow는 목적과 의존성에 따라 나뉜다.
- sequential, parallel, evaluator-optimizer는 서로 다른 failure mode와 cost structure를 가진다.
- 무조건 복잡한 multi-agent로 가지 말고, 단일 agent로 먼저 baseline을 잡아야 한다.

### 우리 Skill에 주는 설계 교훈
- `skill-workflow-bridge-eval`은 workflow mode를 추상적으로 지원하는 것이 아니라, 각 mode별 decision 기준을 달리 가져야 한다.
- evaluator-optimizer는 반드시 종료 조건이 있어야 한다.
- parallel fan-in에는 aggregation policy가 필요하다.

---

## 18.2 Anthropic - How we built our multi-agent research system
- URL: `https://www.anthropic.com/engineering/built-multi-agent-research-system`

### 왜 중요한가
실제 multi-agent system을 어떻게 분해하고 orchestration했는지 보여준다.

### 이 문서에서 가져와야 하는 핵심
- research/planning/writing/verification을 여러 agent로 나눌 수 있다.
- 하지만 중요한 것은 역할 분리만이 아니라 **agent 간 handoff 설계**다.
- long context와 tool outputs를 그냥 이어붙이는 게 아니라 역할별로 재구성한다.

### 우리 Skill에 주는 설계 교훈
- `handoff_packet`은 raw output dump가 아니라 다음 step을 위한 구조화된 packet이어야 한다.
- skill 간 bridge layer가 필요하다.

---

## 18.3 OpenAI - Agent Evals
- URL: `https://platform.openai.com/docs/guides/agent-evals`

### 왜 중요한가
agent workflow 평가를 black-box가 아니라 task-level/trajectory-level로 설계하는 기준을 제공한다.

### 핵심 교훈
- 평가 기준은 미리 구조화해야 한다.
- run 단위와 trace 단위 모두 필요하다.
- pass/fail만이 아니라 richer metadata를 남겨야 한다.

### 우리 Skill에 주는 설계 교훈
- `bridge_eval.json`은 단순 score 파일이 아니라 traceable decision file이어야 한다.
- run id / step id / artifact lineage가 필요하다.

---

## 18.4 OpenAI - Trace Grading
- URL: `https://platform.openai.com/docs/guides/trace-grading`

### 왜 중요한가
최종 답변만 보는 것이 아니라 intermediate trace를 평가 대상으로 삼는다는 점이 중요하다.

### 우리 Skill에 주는 설계 교훈
- `skill-workflow-bridge-eval`은 final output grading보다 intermediate handoff grading에 특화되어야 한다.
- 각 decision은 근거와 함께 trace에 남아야 한다.

---

## 18.5 OpenAI - Graders
- URL: `https://platform.openai.com/docs/guides/graders/`

### 왜 중요한가
grader는 자연어 평가를 structured score 또는 pass/fail로 바꾸는 핵심 모듈이다.

### 우리 Skill에 주는 설계 교훈
- extraction grader와 decision grader를 분리할 수 있다.
- natural-language output도 structured grading으로 전환 가능하다.

---

## 18.6 OpenAI - Evaluation Best Practices
- URL: `https://platform.openai.com/docs/guides/evaluation-best-practices`

### 왜 중요한가
평가 기준, test set, failure taxonomy를 미리 정의하라는 원칙이 중요하다.

### 우리 Skill에 주는 설계 교훈
- retry/reroute/stop 기준은 ad-hoc면 안 된다.
- failure type을 `recoverable / irrecoverable / ambiguous / external-blocked`처럼 taxonomy로 두는 게 좋다.

---

## 18.7 Inspect AI
- GitHub: `https://github.com/UKGovernmentBEIS/inspect_ai`
- Tracing docs: `https://inspect.aisi.org.uk/tracing.html`
- Scorers docs: `https://inspect.aisi.org.uk/scorers.html`
- Log viewer docs: `https://inspect.aisi.org.uk/log-viewer.html`

### 왜 중요한가
multi-step eval과 trace/scorer 구조가 잘 정리돼 있다.

### 우리 Skill에 주는 설계 교훈
- scorer abstraction을 두면 자연어와 structured output을 같은 pipeline 안에서 평가하기 쉬워진다.
- log viewer적 사고가 있으면 `workflow_run`과 `step_run`을 나눠 기록하는 근거가 생긴다.
- tracing이 없으면 reroute/retry 원인 분석이 어렵다.

---

## 18.8 Promptfoo - Simulated User
- URL: `https://www.promptfoo.dev/docs/providers/simulated-user/`

### 왜 중요한가
multi-turn interaction에서 결과를 평가할 때 simulated user/evaluator loop를 어떻게 넣을지 보여준다.

### 우리 Skill에 주는 설계 교훈
- evaluator-optimizer loop는 단순 static grader가 아니라 상호작용형 evaluator로 확장 가능하다.
- downstream skill이 사실상 simulated consumer 역할을 할 수도 있다.

---

## 18.9 AWS Agent Evaluation
- URL: `https://github.com/awslabs/agent-evaluation`

### 왜 중요한가
target agent와 evaluator agent를 분리해서 multi-turn evaluation을 돌리는 구조가 있다.

### 우리 Skill에 주는 설계 교훈
- evaluator agent와 worker agent를 분리한 설계가 자연스럽다.
- workflow bridge에서도 "producer skill"과 "bridge evaluator"의 역할 분리가 유효하다.

---

## 18.10 DeepEval
- URL: `https://github.com/confident-ai/deepeval`

### 왜 중요한가
LLM application / agent output을 component-level로 평가하는 감각이 강하다.

### 우리 Skill에 주는 설계 교훈
- bridge layer 역시 component-level metric을 가질 수 있다.
- 예: handoff readiness, repairability, ambiguity score, evidence sufficiency score

---

## 18.11 MCP Agent - Workflows Overview
- URL: `https://docs.mcp-agent.com/patterns/workflows/overview`

### 왜 중요한가
workflow pattern을 실제 agent system 설계로 연결한다.

### 우리 Skill에 주는 설계 교훈
- sequential / parallel / evaluator-optimizer는 추상 개념이 아니라 agent workflow pattern으로 구현 가능한 단위다.
- `skill-workflow-bridge-eval`은 이 세 패턴을 통합 관리하는 meta-layer가 될 수 있다.

---

## 18.12 MCP Agent - Evaluator Optimizer
- URL: `https://docs.mcp-agent.com/patterns/workflows/evaluator_optimizer`

### 왜 중요한가
evaluator-optimizer loop를 실제 workflow로 어떻게 구현하는지 매우 직접적으로 보여준다.

### 우리 Skill에 주는 설계 교훈
- `retry_spec`와 `loop_state`는 선택이 아니라 핵심 artifact다.
- 최대 반복 횟수와 품질 기준이 필요하다.

---

## 18.13 AgentBench
- URL: `https://arxiv.org/abs/2308.03688`

### 왜 중요한가
agent를 단발 질문응답이 아니라 환경 속 행동 단위로 평가해야 한다는 관점을 제공한다.

### 우리 Skill에 주는 설계 교훈
- step-level outcome만 볼 게 아니라 workflow progression도 봐야 한다.
- `skill-workflow-bridge-eval`은 step accuracy보다 flow continuity를 같이 평가해야 한다.

---

## 18.14 AgentBoard
- URL: `https://arxiv.org/abs/2401.13178`

### 왜 중요한가
final score만이 아니라 과정/trajectory/progress를 보는 analytical evaluation board 개념이 중요하다.

### 우리 Skill에 주는 설계 교훈
- `bridge_eval`은 단순 pass/fail이 아니라 analytical record여야 한다.
- 어느 step에서 막혔는지, 왜 막혔는지 분석 가능해야 한다.

---

## 18.15 τ-bench
- URL: `https://arxiv.org/abs/2406.12045`

### 왜 중요한가
tool-agent-user interaction을 실제적인 도메인 상호작용으로 본다.

### 우리 Skill에 주는 설계 교훈
- downstream skill은 사실상 user/tool/consumer 역할을 할 수 있다.
- handoff evaluation도 interaction quality로 볼 수 있다.

---

## 18.16 AgentDojo
- URL: `https://arxiv.org/abs/2406.13352`

### 왜 중요한가
agent robustness와 adversarial failure를 평가한다.

### 우리 Skill에 주는 설계 교훈
- bridge layer도 prompt injection, malformed output, misleading completion claim에 취약할 수 있다.
- 따라서 raw_output을 무조건 신뢰하면 안 된다.

---

## 19. 이 reference들이 종합적으로 말해주는 것

위 자료들을 합치면 `skill-workflow-bridge-eval`은 아래 기능을 가져야 한다.

1. workflow mode aware
2. output type aware
3. natural-language normalization aware
4. repair retry aware
5. decision trace aware
6. run lineage aware
7. fan-in aware
8. evaluator loop aware

즉 이 Skill은 단순 orchestrator도 아니고 단순 evaluator도 아니다.  
**workflow control evaluator**가 더 정확한 표현이다.

---

## 20. v0.1에서 반드시 고정해야 할 설계 항목

1. output type taxonomy
2. decision set
3. retry_spec schema
4. handoff_packet schema
5. bridge_eval schema
6. workflow_run / step_run id 규칙
7. max retry / max loop 규칙
8. no-progress 판정 규칙
9. natural-language extraction 필드
10. sequential / parallel / evaluator-optimizer 세 모드의 최소 contract

---

## 21. v0.1 범위

### 포함
- sequential mode
- parallel mode
- evaluator-optimizer mode
- output type classification
- natural language normalization
- bridge_eval generation
- retry_spec generation
- handoff_packet generation
- decision trace logging

### 제외
- full router graph engine
- complex scheduler
- UI dashboard
- multi-project control plane
- heavy-weight benchmark harness 전부

---

## 22. 이 Skill이 직접 만들면 좋은 reference 하위 문서

1. `WORKFLOW_MODES.md`
- sequential / parallel / evaluator-optimizer contract

2. `DECISION_ALGEBRA.md`
- pass / retry / reroute / loop / stop / escalate / fanout / fanin_hold

3. `NATURAL_LANGUAGE_OUTPUT_POLICY.md`
- extract / grade / decide / normalize 정책

4. `ARTIFACT_SCHEMA.md`
- raw_output.md
- bridge_eval.json
- retry_spec.json
- handoff_packet.json

5. `FAILURE_TAXONOMY.md`
- recoverable / irrecoverable / ambiguous / external_blocked / no_progress

6. `LOOP_POLICY.md`
- max retries, max iterations, threshold, no-progress detection

7. `FANIN_POLICY.md`
- weighted merge / expert-first / structured-first / safety veto

---

## 23. 이 Skill이 직접 만들면 좋은 scripts

1. `bridge_eval_runner.py`
- step output을 읽어 bridge_eval 생성

2. `output_type_classifier.py`
- output type 분류

3. `nl_output_extractor.py`
- 자연어 출력에서 구조화 정보 추출

4. `decision_engine.py`
- bridge_eval -> decision 변환

5. `retry_spec_builder.py`
- unmet_conditions -> repair retry spec 생성

6. `handoff_packet_builder.py`
- downstream skill 입력용 canonical packet 생성

7. `fanin_aggregator.py`
- parallel outputs fan-in

8. `loop_controller.py`
- evaluator-optimizer 반복 제어

---

## 24. 최종 설계 판단

`skill-workflow-bridge-eval`은 여러 Skill 사이에서 **무엇을 실행할지**보다 **왜 다음을 그렇게 실행해야 하는지**를 결정하고 기록하는 Skill이다.

가장 중요한 설계 포인트는 아래 셋이다.

1. 자연어 출력은 그대로 handoff 하지 않는다.
2. 조건 미충족 시 retry는 blind retry가 아니라 repair retry다.
3. 모든 decision은 artifact와 trace로 남아야 한다.

이 세 가지가 빠지면, 이 Skill은 단순 결과 집계기나 step router로 축소된다.  
반대로 이 세 가지가 들어가면, 이 Skill은 실제 multi-skill orchestration에서 가장 중요한 병목을 해결하는 bridge layer가 된다.

---

## 25. Source Map

### Local references
- `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-workflow-bridge-eval/references/Boundary-of-Responsibility-2026-03-15-03-56.md`

### Official / primary references
- `https://www.anthropic.com/research/building-effective-agents`
- `https://www.anthropic.com/engineering/built-multi-agent-research-system`
- `https://platform.openai.com/docs/guides/agent-evals`
- `https://platform.openai.com/docs/guides/trace-grading`
- `https://platform.openai.com/docs/guides/graders/`
- `https://platform.openai.com/docs/guides/evaluation-best-practices`
- `https://inspect.aisi.org.uk/tracing.html`
- `https://inspect.aisi.org.uk/scorers.html`
- `https://inspect.aisi.org.uk/log-viewer.html`
- `https://www.promptfoo.dev/docs/providers/simulated-user/`
- `https://github.com/awslabs/agent-evaluation`
- `https://github.com/confident-ai/deepeval`
- `https://docs.mcp-agent.com/patterns/workflows/overview`
- `https://docs.mcp-agent.com/patterns/workflows/evaluator_optimizer`
- `https://arxiv.org/abs/2308.03688`
- `https://arxiv.org/abs/2401.13178`
- `https://arxiv.org/abs/2406.12045`
- `https://arxiv.org/abs/2406.13352`
