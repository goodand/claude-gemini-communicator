# skill-acceptance-gate 정합성 판단 체크리스트

- version: `v0.1.0`
- created_at: `2026-03-15`
- updated_at: `2026-03-15`
- purpose: `skill-acceptance-gate 구현이 reference corpus와 기능적으로 정합한지 판단하기 위한 상세 체크리스트`
- primary_source: `skill-acceptance-gate-knowledge_base-at-2026-03-15-02-19.md`

## 문서 목적

이 체크리스트는 `skill-acceptance-gate`가 단순 문서/아이디어 수준이 아니라, 실제 코드베이스에서 **작동 가능한 acceptance gate skill**로 구현되었는지 판정하기 위한 기준이다.

이 문서의 판정 기준은 아래 reference 축을 따른다.

- 평가 프레임워크 축: `OpenAI Evals`, `Inspect AI`, `Promptfoo`, `DeepEval`, `AWS Agent Evaluation`
- 분석형 benchmark 축: `AgentBench`, `AgentBoard`, `τ-bench`, `AgentDojo`, `SWE-bench`, `iAgentBench`
- 운영 문서 축: `OpenAI Agent evals`, `Trace grading`, `Graders`, `Evaluation best practices`, `Inspect Scorers`, `Inspect Tracing`, `Inspect Log Viewer`, `Promptfoo Simulated User`

이 체크리스트의 핵심 질문은 아래 하나다.

`이 Skill은 다른 Skill들의 작동 여부를 trigger, boundary, schema, runtime trace, regression, adversarial, executable gate 관점에서 실제로 판정할 수 있는가?`

## 판정 원칙

- [ ] `skill-acceptance-gate`는 단순 smoke test 모음이 아니다.
- [ ] `skill-acceptance-gate`는 최소한 `trigger correctness`, `boundary correctness`, `schema validity`, `runtime traceability`, `multi-turn/tool-use correctness`, `adversarial robustness`, `regression stability`, `executable acceptance`를 다뤄야 한다.
- [ ] `pass/fail`만 출력하는 구현은 부분 정합으로 본다.
- [ ] reference corpus에 있는 `trace`, `scorer`, `simulated user`, `adversarial`, `release gate` 개념 중 2개 이상이 빠지면 정합성이 낮다고 본다.
- [ ] 구현은 `문서 + script + eval + output artifact`의 네 층 중 최소 세 층을 가져야 한다.
- [ ] 특정 reference를 그대로 복제할 필요는 없지만, 핵심 설계 의도가 구현에 반영되어야 한다.

## 정합성 레벨 정의

### Level 0. Note
- [ ] 링크/메모만 존재하고 실행 가능한 script가 없다.
- [ ] acceptance 기준이 자연어로만 있고 machine-checkable form이 없다.

### Level 1. Testable
- [ ] 최소 schema validator와 happy-path script가 있다.
- [ ] 최소 `evals/evals.json` 또는 동등한 테스트 입력이 있다.
- [ ] failure 시 exit code가 일관적이다.

### Level 2. Operational
- [ ] trigger/boundary/schema/trace/regression gate가 모두 구현되어 있다.
- [ ] 로그/trace/artifact가 저장된다.
- [ ] negative case와 adversarial case가 있다.
- [ ] 다른 Skill에 적용 가능한 공통 인터페이스가 있다.

### Level 3. Trusted
- [ ] tmux/Codex 실험에서 실제로 검증되었다.
- [ ] regression과 release gate가 운영 중이다.
- [ ] bug/trouble 패턴이 references에 축적되어 있다.
- [ ] false positive / false negative 사례가 정리되어 있다.

## 1. Skill 정체성 / 책임 경계

Reference basis:
- `OpenAI Evaluation best practices`
- `AgentBoard`
- `AgentDojo`
- `Inspect Scorers`

- [ ] 이 Skill의 목적이 `다른 Skill을 평가하는 meta-skill`로 명확히 정의되어 있다.
- [ ] 이 Skill은 production task 수행 skill이 아니라 `acceptance gate`라는 점이 문서에 명시되어 있다.
- [ ] 이 Skill이 직접 구현/수정/실행하는 것이 아니라, 평가·판정·검증하는 역할이라는 점이 분명하다.
- [ ] 이 Skill이 판정하는 최소 단위가 무엇인지 정의되어 있다. 예: `SKILL.md`, `scripts/`, `evals/`, `references/`, runtime outputs.
- [ ] 이 Skill이 소유하는 산출물이 정의되어 있다. 예: `gate report`, `grade JSON`, `trace summary`, `failure taxonomy`.
- [ ] 이 Skill이 수정하면 안 되는 대상이 정의되어 있다. 예: target skill의 핵심 구현 파일 자체를 평가 중 수정하지 않는다.
- [ ] target skill과 `skill-acceptance-gate`의 경계가 문서로 명확하다.
- [ ] acceptance gate가 실제 workflow에서 언제 호출되는지 정의돼 있다. 예: 초안 직후, script 추가 후, tmux 실험 후, release 전.
- [ ] `note`, `draft`, `operational`, `trusted` 상태 구분이 있다.
- [ ] `skill-acceptance-gate`가 target skill의 소유권 필드까지 재정의하지 않도록 boundary가 정리돼 있다.

## 2. Reference Coverage 정합성

Reference basis:
- knowledge base 전체

- [ ] `OpenAI Evals` 계열 reference가 반영돼 있다.
- [ ] `Inspect AI` 계열 reference가 반영돼 있다.
- [ ] `Promptfoo` 계열 reference가 반영돼 있다.
- [ ] `DeepEval` 계열 reference가 반영돼 있다.
- [ ] `AWS Agent Evaluation` 계열 reference가 반영돼 있다.
- [ ] `AgentBoard`의 fine-grained evaluation 철학이 반영돼 있다.
- [ ] `τ-bench`의 multi-turn/tool-user-agent 관점이 반영돼 있다.
- [ ] `AgentDojo`의 adversarial/robustness 관점이 반영돼 있다.
- [ ] `SWE-bench`의 executable acceptance 관점이 반영돼 있다.
- [ ] `OpenAI Trace grading`의 step-level grading 개념이 반영돼 있다.
- [ ] `Inspect Tracing`의 runtime trace 구조가 반영돼 있다.
- [ ] `Promptfoo Simulated User`의 multi-turn acceptance 테스트 아이디어가 반영돼 있다.
- [ ] reference마다 `왜 필요한지`와 `어떤 artifact로 구현에 들어오는지`가 설명돼 있다.
- [ ] reference를 단순 인용이 아니라 구현 항목과 연결했다.
- [ ] 어떤 reference가 `필수`, `권장`, `확장`인지 구분돼 있다.

## 3. Trigger Correctness Gate

Reference basis:
- `OpenAI Evaluation best practices`
- `Promptfoo`
- `Promptfoo Simulated User`

- [ ] target skill이 언제 발동해야 하는지 positive trigger case가 정의돼 있다.
- [ ] target skill이 발동하면 안 되는 negative trigger case가 정의돼 있다.
- [ ] ambiguous prompt에 대한 disambiguation case가 있다.
- [ ] multi-skill 환경에서 잘못된 skill이 선택되는 경우를 잡는 케이스가 있다.
- [ ] trigger case는 단일 예시가 아니라 여러 representative prompt로 구성된다.
- [ ] trigger 판정 기준이 문자열 포함 수준을 넘어, 최종 선택된 skill name 또는 call decision까지 검증한다.
- [ ] trigger 결과를 저장하는 machine-readable output이 있다.
- [ ] trigger false positive를 잡는 케이스가 있다.
- [ ] trigger false negative를 잡는 케이스가 있다.
- [ ] trigger 판정 로직이 hard-coded keyword match에만 의존하지 않는지 검토되었다.
- [ ] trigger test는 regression suite에 포함된다.
- [ ] trigger 실패 시 원인이 `prompt ambiguity`, `metadata weakness`, `routing bug` 중 어느 쪽인지 분리할 수 있다.

## 4. Boundary Correctness Gate

Reference basis:
- `AgentDojo`
- `τ-bench`
- `OpenAI Graders`

- [ ] target skill이 소유해야 하는 필드/상태/파일을 명시한 `BOUNDARY_RULES`가 있다.
- [ ] target skill이 읽기만 해야 하는 필드를 명시했다.
- [ ] target skill이 절대 수정하면 안 되는 필드를 명시했다.
- [ ] forbidden mutation test case가 있다.
- [ ] path boundary break 사례가 있다.
- [ ] prompt injection 형태의 boundary break 사례가 있다.
- [ ] tool return hijack 또는 indirect instruction injection 사례가 있다.
- [ ] boundary audit script가 실제로 forbidden field mutation을 감지한다.
- [ ] boundary breach가 감지되면 exit code가 실패로 떨어진다.
- [ ] boundary breach report가 생성된다.
- [ ] target skill이 다른 skill의 ownership 영역을 침범했을 때 failure taxonomy에 분류된다.
- [ ] allowed path/forbidden path 검사가 normalize된 path 기준으로 동작한다.
- [ ] relative path, symlink, `..` traversal, prefix overlap에 대한 방어가 있다.
- [ ] boundary 규칙이 문서와 스크립트에서 일치한다.

## 5. Schema Validity Gate

Reference basis:
- `OpenAI Evals`
- `Inspect Scorers`
- `OpenAI Graders`

- [ ] target skill input schema가 정의되어 있다.
- [ ] target skill output schema가 정의되어 있다.
- [ ] schema validator script가 있다.
- [ ] 필수 필드 누락 테스트가 있다.
- [ ] 금지 필드 포함 테스트가 있다.
- [ ] 잘못된 enum/status 값 테스트가 있다.
- [ ] invalid path format 테스트가 있다.
- [ ] empty array / empty string / null 처리 규칙이 있다.
- [ ] schema validation 결과가 machine-readable JSON으로도 나온다.
- [ ] validation success/failure가 deterministic하다.
- [ ] validator는 human-readable summary도 제공한다.
- [ ] schema version field가 있다.
- [ ] version mismatch 처리 규칙이 있다.
- [ ] backward compatibility 정책이 있다.
- [ ] schema validation은 runtime 이전에 반드시 실행된다.

## 6. Runtime Traceability Gate

Reference basis:
- `OpenAI Trace grading`
- `Inspect Tracing`
- `Inspect Log Viewer`
- `DeepEval`

- [ ] target skill 실행 시 trace를 남길 수 있다.
- [ ] trace에는 최소 `start`, `step`, `result`, `error`, `end` 수준의 이벤트가 있다.
- [ ] trace에는 timestamp가 있다.
- [ ] trace에는 task/case identifier가 있다.
- [ ] trace에는 input snapshot 또는 input reference가 있다.
- [ ] trace에는 output snapshot 또는 output reference가 있다.
- [ ] trace에는 intermediate decision이 남는다.
- [ ] trace grade를 계산하는 별도 script가 있다.
- [ ] trace만 보고 어느 단계에서 실패했는지 분리 가능하다.
- [ ] timeout이 trace에 명시된다.
- [ ] exception class / stderr 요약이 trace에 남는다.
- [ ] trace artifact 경로가 표준화돼 있다.
- [ ] 여러 run의 trace를 비교할 수 있다.
- [ ] trace report가 사람이 읽기 좋은 summary를 제공한다.
- [ ] trace log viewer 또는 viewer-friendly JSON 구조를 염두에 둔 포맷이다.

## 7. Scoring / Grading Gate

Reference basis:
- `OpenAI Graders`
- `Inspect Scorers`
- `OpenAI Agent evals`

- [ ] 어떤 gate를 rule-based로 채점할지 정의돼 있다.
- [ ] 어떤 gate를 model-based로 채점할지 정의돼 있다.
- [ ] 어떤 gate를 python/custom grader로 채점할지 정의돼 있다.
- [ ] score와 pass/fail의 관계가 문서화돼 있다.
- [ ] binary gate와 scalar score를 혼용할 때 기준이 있다.
- [ ] threshold가 hard-coded되었더라도 문서화돼 있다.
- [ ] threshold selection rationale이 있다.
- [ ] score output schema가 있다.
- [ ] grader failure와 target skill failure를 구분할 수 있다.
- [ ] grader nondeterminism이 허용되는 영역과 허용되지 않는 영역이 구분돼 있다.
- [ ] model grader를 deterministic gate 대체 용도로 남용하지 않는다.
- [ ] grader 자체 smoke test가 있다.
- [ ] grader regression test가 있다.

## 8. Multi-turn / Tool-use Gate

Reference basis:
- `τ-bench`
- `ToolTalk`
- `AWS Agent Evaluation`
- `Promptfoo Simulated User`
- `AgentBench`

- [ ] single-turn eval만이 아니라 multi-turn eval이 있다.
- [ ] simulated user 또는 evaluator agent 기반 케이스가 있다.
- [ ] target skill이 agent loop 안에서 호출되는 실제 시나리오가 있다.
- [ ] tool-use sequence correctness를 검증하는 case가 있다.
- [ ] tool call order를 검증하는 case가 있다.
- [ ] tool output handling correctness case가 있다.
- [ ] retry/replan 상황에서 target skill이 올바르게 다시 호출되는지 검증한다.
- [ ] multi-turn transcript가 artifact로 저장된다.
- [ ] multi-turn transcript를 점수화하는 규칙이 있다.
- [ ] policy adherence 또는 constraint adherence를 보는 case가 있다.
- [ ] interaction loop가 너무 길어졌을 때 timeout/abort 기준이 있다.
- [ ] tool unavailable / malformed tool result 케이스가 있다.
- [ ] multi-turn gate 결과가 단일 성공률만이 아니라 failure type으로도 집계된다.

## 9. Adversarial / Robustness Gate

Reference basis:
- `AgentDojo`
- `Promptfoo`
- `τ-bench`

- [ ] adversarial suite가 있다.
- [ ] prompt injection case가 있다.
- [ ] hidden instruction / indirect instruction case가 있다.
- [ ] boundary escape case가 있다.
- [ ] malformed schema but plausible input case가 있다.
- [ ] high-noise context case가 있다.
- [ ] contradictory instruction case가 있다.
- [ ] fake success artifact case가 있다.
- [ ] stale state / stale metadata case가 있다.
- [ ] permission escalation misuse case가 있다.
- [ ] adversarial case failure 시 어떤 rule을 어겼는지 라벨링된다.
- [ ] adversarial suite는 regression에 포함된다.
- [ ] release 전에만 돌리는 게 아니라 개발 단계에서도 돌릴 수 있다.
- [ ] adversarial 케이스는 references에서 독립 문서로 관리된다.

## 10. Regression Stability Gate

Reference basis:
- `OpenAI Evals`
- `Promptfoo`
- `OpenAI Evaluation best practices`
- `Inspect AI`

- [ ] golden cases가 있다.
- [ ] baseline outputs 또는 baseline scores가 있다.
- [ ] 변경 후 재실행 시 delta를 계산한다.
- [ ] regression suite는 최소 happy-path와 negative-path를 모두 포함한다.
- [ ] regression suite는 trigger, boundary, schema, trace 중 최소 4축 이상을 포함한다.
- [ ] regression 결과를 파일로 저장한다.
- [ ] regression summary report가 있다.
- [ ] known flaky case를 분리한다.
- [ ] flaky case 정책이 있다.
- [ ] regression failure가 발생했을 때 원인 분류가 가능하다.
- [ ] regression 결과가 CI 또는 local automation에서 재현 가능하다.
- [ ] regression 대상 데이터셋이 실제 failure pattern을 반영한다.
- [ ] trivial easy cases만으로 구성되지 않는다.

## 11. Executable Acceptance / Release Gate

Reference basis:
- `SWE-bench`
- `OpenAI Agent evals`
- `Inspect AI`

- [ ] 최종 release gate가 있다.
- [ ] release gate는 문서만이 아니라 script로 존재한다.
- [ ] required artifact 존재 여부를 검사한다.
- [ ] required script exit code를 검사한다.
- [ ] malformed but present artifact를 걸러낼 수 있다.
- [ ] release gate가 target skill의 최소 운영 readiness를 판정한다.
- [ ] `all green` 조건이 문서화돼 있다.
- [ ] partial success를 release success로 오인하지 않는다.
- [ ] release gate는 regression gate와 별개로 존재한다.
- [ ] release gate 결과를 저장한다.
- [ ] release gate는 target skill의 `trusted` 승격 조건과 연결된다.

## 12. Failure Taxonomy / 보고 체계

Reference basis:
- `AgentBoard`
- `AgentBench`
- `Inspect Log Viewer`

- [ ] failure taxonomy 문서가 있다.
- [ ] failure를 최소 아래 수준으로 분류한다.
- [ ] `trigger_failure`
- [ ] `boundary_failure`
- [ ] `schema_failure`
- [ ] `trace_failure`
- [ ] `tool_loop_failure`
- [ ] `adversarial_failure`
- [ ] `regression_failure`
- [ ] `release_gate_failure`
- [ ] 각 실패 유형마다 대표 사례가 있다.
- [ ] 각 실패 유형마다 재현 방법이 있다.
- [ ] 각 실패 유형마다 recommended next action이 있다.
- [ ] report가 pass/fail뿐 아니라 failure taxonomy breakdown을 포함한다.
- [ ] run summary에 top failure reasons가 포함된다.

## 13. Artifact / 디렉토리 구조 정합성

Reference basis:
- knowledge base의 planned artifacts mapping

- [ ] `SKILL.md`가 있다.
- [ ] `references/`에 운영 기준 문서가 있다.
- [ ] `evals/evals.json`이 있다.
- [ ] `scripts/`에 validator / grader / runner가 있다.
- [ ] `references/OPERATING_CRITERIA.md`가 있다.
- [ ] `references/BOUNDARY_RULES.md`가 있다.
- [ ] `references/TRACE_GRADING.md`가 있다.
- [ ] `references/FAILURE_TAXONOMY.md`가 있다.
- [ ] `references/REGRESSION_POLICY.md`가 있다.
- [ ] `references/ADVERSARIAL_TESTS.md` 또는 동등 문서가 있다.
- [ ] `references/RELEASE_GATE.md` 또는 동등 문서가 있다.
- [ ] `scripts/gate_validate_schema.py`가 있다.
- [ ] `scripts/gate_trigger_matrix.py`가 있다.
- [ ] `scripts/gate_boundary_audit.py`가 있다.
- [ ] `scripts/gate_trace_grade.py`가 있다.
- [ ] `scripts/gate_simulated_user.py`가 있다.
- [ ] `scripts/gate_regression_suite.py`가 있다.
- [ ] `scripts/gate_release_check.py`가 있다.
- [ ] artifact 저장 경로 규칙이 문서화돼 있다.
- [ ] run logs, traces, reports의 파일명 규칙이 있다.

## 14. Evals 설계 정합성

Reference basis:
- `OpenAI Evals`
- `Promptfoo`
- `Inspect AI`

- [ ] `evals/evals.json` 또는 동등한 eval spec 파일이 있다.
- [ ] eval case마다 `id`가 있다.
- [ ] eval case마다 `prompt/input`이 있다.
- [ ] eval case마다 `expected behavior`가 있다.
- [ ] eval case마다 `grading method`가 있다.
- [ ] eval case마다 `positive/negative/adversarial` 분류가 있다.
- [ ] eval case마다 `required artifacts`가 있다.
- [ ] eval case마다 `failure class`가 연결된다.
- [ ] multi-turn case는 transcript expectation을 포함한다.
- [ ] eval spec이 machine-runnable 하다.
- [ ] eval spec이 script interface와 맞는다.
- [ ] eval result schema가 별도로 정의돼 있다.

## 15. 문서-코드 일치성

Reference basis:
- 전체 reference corpus

- [ ] `SKILL.md`의 약속과 실제 script가 일치한다.
- [ ] references 문서의 file name이 실제 파일과 일치한다.
- [ ] 문서에 존재한다고 적은 subcommand가 실제 구현돼 있다.
- [ ] 문서에 없는 위험한 기능이 script에 숨어 있지 않다.
- [ ] 예시 명령이 실제 실행 가능하다.
- [ ] outdated field name이나 deprecated option이 없는지 검토했다.
- [ ] eval spec과 grader script의 expected keys가 일치한다.
- [ ] report 문서와 run output schema가 일치한다.
- [ ] 문서 수정 후 script signature mismatch를 확인하는 절차가 있다.

## 16. 운영 자동화 / CI 적합성

Reference basis:
- `Promptfoo`
- `OpenAI Evals`
- `AWS Agent Evaluation`

- [ ] non-interactive CLI 실행이 가능하다.
- [ ] exit code 정책이 있다.
- [ ] JSON output 옵션이 있다.
- [ ] CI에서 돌릴 수 있는 quick mode가 있다.
- [ ] 더 느리지만 comprehensive한 full mode가 있다.
- [ ] flaky 또는 expensive tests를 분리했다.
- [ ] trace/log/report를 CI artifact로 저장할 수 있다.
- [ ] CI failure message가 actionable 하다.
- [ ] local run과 CI run의 차이를 문서화했다.
- [ ] network-required test와 offline test를 구분한다.

## 17. tmux / Codex 실험 연계 준비도

Reference basis:
- 현재 프로젝트 운영 흐름
- 향후 `codex-tmux-orchestrator`, `codex-session-monitor`

- [ ] `skill-acceptance-gate`가 tmux에서 non-interactive로 실행 가능하다.
- [ ] Codex worker가 만든 output artifact를 읽어 평가할 수 있다.
- [ ] long-running eval에서도 trace/log가 누적된다.
- [ ] stale run과 정상 run을 구분할 수 있다.
- [ ] session 외부에서도 결과만으로 grading이 가능하다.
- [ ] tmux capture log와 gate trace를 연결할 수 있는 식별자가 있다.
- [ ] multi-session 병렬 실행 시 output collision이 없다.
- [ ] run directory naming이 deterministic하다.
- [ ] future `skill-bug/trouble` logging과 연결될 수 있다.

## 18. 최소 합격선

### v0.1 필수
- [ ] trigger matrix
- [ ] boundary audit
- [ ] schema validation
- [ ] simple trace capture
- [ ] regression suite
- [ ] run summary report

### v0.2 권장
- [ ] simulated user multi-turn eval
- [ ] adversarial suite
- [ ] trace grading labels
- [ ] failure taxonomy breakdown
- [ ] CI quick/full modes

### v0.3 강정합
- [ ] executable release gate
- [ ] richer tool-loop scoring
- [ ] trust 승격 절차
- [ ] bug/trouble pattern archive 연동
- [ ] viewer-friendly log/trace integration

## 19. 최종 판정 질문

아래 질문에 모두 `예`라고 답할 수 있어야 정합성이 높다고 본다.

- [ ] 이 Skill은 다른 Skill이 언제 발동해야 하는지 판정할 수 있는가?
- [ ] 이 Skill은 다른 Skill이 경계를 넘었는지 판정할 수 있는가?
- [ ] 이 Skill은 입력/출력 스키마 위반을 판정할 수 있는가?
- [ ] 이 Skill은 최종 실패뿐 아니라 중간 실패 위치를 판정할 수 있는가?
- [ ] 이 Skill은 multi-turn agent loop에서도 작동 여부를 판정할 수 있는가?
- [ ] 이 Skill은 adversarial misuse를 판정할 수 있는가?
- [ ] 이 Skill은 수정 후 회귀를 판정할 수 있는가?
- [ ] 이 Skill은 release 가능한 상태인지 판정할 수 있는가?

## 20. 구현 전 반드시 결정할 12가지

- [ ] acceptance result의 canonical schema는 무엇인가?
- [ ] trace artifact 형식은 무엇인가?
- [ ] failure taxonomy는 몇 단계까지 나눌 것인가?
- [ ] trigger grade는 rule-based인가 model-based인가?
- [ ] boundary grade는 어떤 입력을 기반으로 판정할 것인가?
- [ ] adversarial suite의 최소 범위는 어디까지인가?
- [ ] regression suite의 gold set은 어디에 보관할 것인가?
- [ ] expensive eval과 cheap eval을 어떻게 분리할 것인가?
- [ ] release gate는 어떤 script를 최종 source of truth로 볼 것인가?
- [ ] tmux/Codex 실험 로그와 gate 결과를 어떻게 연결할 것인가?
- [ ] trusted 승격 기준은 무엇인가?
- [ ] false positive / false negative를 어떻게 기록하고 줄일 것인가?

## 사용한 reference 기준

- `skill-acceptance-gate-knowledge_base-at-2026-03-15-02-19.md`
- `OpenAI Evals`
- `Inspect AI`
- `Promptfoo`
- `DeepEval`
- `AWS Agent Evaluation`
- `AgentBench`
- `AgentBoard`
- `τ-bench`
- `AgentDojo`
- `SWE-bench`
- `iAgentBench`
- `OpenAI Agent evals`
- `OpenAI Trace grading`
- `OpenAI Graders`
- `OpenAI Evaluation best practices`
- `Inspect Scorers`
- `Inspect Tracing`
- `Inspect Log Viewer`
- `Promptfoo Simulated User`
