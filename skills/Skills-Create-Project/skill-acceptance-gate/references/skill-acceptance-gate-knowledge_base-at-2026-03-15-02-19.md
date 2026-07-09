# research URL Knowledge Base
- ver: `v0.1.0`
- generated_at: `2026-03-15`
- updated_at: `2026-03-15` (v0.1.0: explanatory sections, coverage matrix, implementation mapping, and detailed relevance notes added)
- format: `- [한 줄 설명](URL)`
- generation_method: `manual curation based on GitHub repositories, arXiv papers, and official implementation/evaluation docs for skill-acceptance-gate design`
- total_urls: `26`
- paper_like_urls: `6`
- other_urls: `20`

## Document Map

| 문서 | 역할 |
|------|------|
| `skill-acceptance-gate-reference-at2026-03-15-02-17.md` | raw note · 수집한 GitHub/논문/구현 레퍼런스 메모 |
| `skill-acceptance-gate-knowledge_base-at-2026-03-15-02-19.md` (이 파일) | 구조화된 reference 인덱스 |

## Table of Contents
- [Paper-like URLs](#paper-like-urls)
- [Other research References URLs](#other-research-references-urls)

## Paper-like URLs

- [AgentBench는 LLM agent를 다중 환경에서 평가하는 범용 벤치마크를 제안하며 최종 정답뿐 아니라 환경별 수행 능력을 비교한다](https://arxiv.org/abs/2308.03688)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - cross_ref: 관련 구현 OpenAI Evals · Inspect AI · 관련 논문 [#02 AgentBoard](#02-agentboard-240113178)
  - anchor_note: `01-agentbench-230803688`
  - taxonomy: [[agent-benchmark, multi-environment, evaluation]] · Axis A
  - key_idea: AgentBench는 다양한 환경에서 LLM agent의 성공률과 행동 성능을 비교해 범용 agent 평가의 기준점을 제공한다.
  - execution_conditions: 다중 환경 실행기, 표준화된 task interface, environment-specific scoring이 필요하다.
  - pseudocode_3lines:
    - 1) 환경별 task와 interaction protocol을 정의한다.
    - 2) agent를 실행해 trajectory와 최종 결과를 수집한다.
    - 3) environment별 success/failure를 집계해 cross-agent 비교를 수행한다.

- [AgentBoard는 multi-turn LLM agent를 final accuracy뿐 아니라 세부 trajectory와 progress까지 포함해 분석적으로 평가한다](https://arxiv.org/abs/2401.13178)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - cross_ref: 관련 구현 AgentBoard repo · 관련 논문 [#01 AgentBench](#01-agentbench-230803688)
  - anchor_note: `02-agentboard-240113178`
  - taxonomy: [[agent-benchmark, analytical-evaluation, trajectory]] · Axis A
  - key_idea: AgentBoard는 최종 성공률만이 아니라 중간 진행도와 세부 sub-skill을 분해해 평가하는 보드를 제공한다.
  - execution_conditions: trajectory logging, fine-grained metric schema, multi-turn interaction record가 필요하다.
  - pseudocode_3lines:
    - 1) agent 실행 중 intermediate action과 state transition을 기록한다.
    - 2) final score 외에 progress 및 sub-skill 지표를 계산한다.
    - 3) mode별/benchmark별 비교 보드로 진단 결과를 시각화한다.

- [τ-bench는 사용자-agent-tool 상호작용을 현실 도메인과 정책 제약 안에서 평가하는 tool-use 벤치마크다](https://arxiv.org/abs/2406.12045)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - cross_ref: 관련 구현 tau-bench repo · Promptfoo simulated user · 관련 논문 [#04 AgentDojo](#04-agentdojo-240613352)
  - anchor_note: `03-tau-bench-240612045`
  - taxonomy: [[tool-use, multi-turn, simulated-user, policy-adherence]] · Axis A
  - key_idea: τ-bench는 사용자의 질의와 도구 호출, 도메인 규칙 준수 여부를 함께 평가해 실사용 agent 평가를 강화한다.
  - execution_conditions: simulated user, executable tools, domain policy checker, multi-turn evaluator가 필요하다.
  - pseudocode_3lines:
    - 1) 사용자-에이전트-도구 상호작용 시나리오를 준비한다.
    - 2) agent의 도구 호출과 응답 trajectory를 실행한다.
    - 3) 정책 준수와 task completion을 함께 점수화한다.

- [AgentDojo는 공격과 방어가 모두 가능한 동적 환경에서 LLM agent의 robustness를 평가한다](https://arxiv.org/abs/2406.13352)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - cross_ref: 관련 구현 agentdojo repo · 관련 논문 [#03 τ-bench](#03-tau-bench-240612045)
  - anchor_note: `04-agentdojo-240613352`
  - taxonomy: [[agent-security, adversarial-evaluation, prompt-injection]] · Axis A
  - key_idea: AgentDojo는 prompt injection과 같은 공격 상황에서 agent가 경계 조건을 지키는지 동적으로 검증한다.
  - execution_conditions: 공격 시나리오, 방어 정책, environment sandbox, trace-level failure labeling이 필요하다.
  - pseudocode_3lines:
    - 1) 공격/방어 시나리오와 규칙을 정의한다.
    - 2) agent를 해당 환경에서 실행하며 공격 입력을 주입한다.
    - 3) 경계 위반 여부와 방어 성공 여부를 평가한다.

- [SWE-bench는 실제 GitHub 이슈 해결을 통해 coding agent의 최종 executable acceptance를 평가한다](https://arxiv.org/abs/2310.06770)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - cross_ref: 관련 구현 SWE-bench repo · 관련 구현 OpenAI Agent evals
  - anchor_note: `05-swe-bench-231006770`
  - taxonomy: [[coding-agent, executable-verification, issue-resolution]] · Axis A
  - key_idea: SWE-bench는 실제 저장소 이슈를 수정하고 테스트를 통과시키는지로 coding agent의 진짜 완료 여부를 판정한다.
  - execution_conditions: issue-to-patch task set, reproducible environment, test harness, patch application workflow가 필요하다.
  - pseudocode_3lines:
    - 1) issue와 대응 코드베이스를 로드한다.
    - 2) agent가 patch를 생성하고 적용한다.
    - 3) 테스트 실행 결과로 수정 성공 여부를 검증한다.

- [iAgentBench는 정보 탐색 에이전트의 sensemaking 능력을 동적이고 고트래픽한 주제에서 평가한다](https://arxiv.org/abs/2603.04656)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - cross_ref: 관련 논문 [#01 AgentBench](#01-agentbench-230803688) · [#02 AgentBoard](#02-agentboard-240113178)
  - anchor_note: `06-iagentbench-260304656`
  - taxonomy: [[information-seeking, dynamic-evaluation, sensemaking]] · Axis A
  - key_idea: iAgentBench는 빠르게 변하는 주제에서 정보 수집뿐 아니라 정리와 판단 능력까지 포함해 agent를 평가한다.
  - execution_conditions: dynamic corpus, temporal task set, reasoning trace capture, answer grounding이 필요하다.
  - pseudocode_3lines:
    - 1) 시간 민감성이 있는 정보 탐색 task를 정의한다.
    - 2) agent가 자료를 수집하고 정리하는 과정을 기록한다.
    - 3) 사실성·구성력·근거성 기준으로 결과를 평가한다.

## Other research References URLs

- [OpenAI Evals는 dataset, grader, eval-run 구조를 제공하는 가장 기본적인 agent/model evaluation framework다](https://github.com/openai/evals)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 평가할 샘플과 기대 동작을 dataset으로 정의한다.
    - 2) grader 또는 scoring logic을 연결한다.
    - 3) eval run을 실행해 결과를 기록하고 회귀를 비교한다.

- [Inspect AI는 tool-use, scorer, trace, log를 포함한 실전형 eval framework다](https://github.com/UKGovernmentBEIS/inspect_ai)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) task, solver, scorer를 조합해 평가 파이프라인을 정의한다.
    - 2) runtime trace와 intermediate state를 로깅한다.
    - 3) scorer로 multi-turn/task-level pass-fail을 계산한다.

- [Promptfoo는 선언형 config와 assert 기반 평가를 지원하는 LLM/agent regression framework다](https://github.com/promptfoo/promptfoo)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) prompts, providers, assertions를 config에 정의한다.
    - 2) eval run을 실행해 assertion 결과를 수집한다.
    - 3) regression gate와 report로 기준 충족 여부를 판정한다.

- [DeepEval은 custom metric과 tracing을 포함한 component-level 및 agentic evaluation framework다](https://github.com/confident-ai/deepeval)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 평가 대상 component나 agent task를 정의한다.
    - 2) custom metric 또는 built-in metric을 연결한다.
    - 3) trace와 metric 결과로 pass-fail 및 품질 편차를 분석한다.

- [AWS Agent Evaluation은 evaluator agent가 target agent와 대화하며 multi-turn 성능을 평가하는 프레임워크다](https://github.com/awslabs/agent-evaluation)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) target agent와 evaluator agent를 설정한다.
    - 2) multi-turn interaction을 실행하며 결과를 관찰한다.
    - 3) evaluator가 task completion과 행동 품질을 판정한다.

- [AgentBoard GitHub 구현체는 analytical evaluation board 개념을 실제 benchmark orchestration과 visualization으로 연결한다](https://github.com/hkust-nlp/AgentBoard)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) benchmark 실행 결과와 trajectory 메타데이터를 수집한다.
    - 2) 세분화된 metric을 집계한다.
    - 3) board 형식으로 모델과 agent를 비교한다.

- [ToolTalk는 대화형 tool-use benchmark 구현체로 도구 호출 순서와 정답성을 검증한다](https://github.com/microsoft/ToolTalk)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) tool-use dialogue task와 gold action을 준비한다.
    - 2) agent가 대화 중 어떤 도구를 호출하는지 기록한다.
    - 3) 호출 순서와 결과를 gold와 비교해 평가한다.

- [tau-bench GitHub 구현체는 user-agent-tool 상호작용을 실제 runnable benchmark로 제공한다](https://github.com/sierra-research/tau-bench)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 도메인별 task와 policy를 로드한다.
    - 2) user-agent-tool loop를 실행한다.
    - 3) completion과 policy adherence를 평가한다.

- [tau2-bench는 tau-bench의 확장형 구현으로 더 복잡한 control과 evaluation split을 지원한다](https://github.com/sierra-research/tau2-bench)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 확장된 task/control 설정을 적용한다.
    - 2) agent trajectory를 더 복합적인 환경에서 실행한다.
    - 3) split별 결과를 비교해 일반화 성능을 본다.

- [AgentDojo GitHub 구현체는 공격/방어 실험 환경을 runnable benchmark 형태로 제공한다](https://github.com/ethz-spylab/agentdojo)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 공격 시나리오와 방어 설정을 로드한다.
    - 2) agent를 공격 환경에서 실행한다.
    - 3) 경계 위반과 방어 성공률을 집계한다.

- [SWE-bench GitHub 구현체는 issue-to-patch-to-test 흐름을 재현 가능한 coding benchmark로 제공한다](https://github.com/SWE-bench/SWE-bench)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 이슈와 대응 저장소 환경을 준비한다.
    - 2) patch를 적용하고 빌드/테스트를 실행한다.
    - 3) 테스트 성공 여부로 acceptance를 판정한다.

- [OpenAI Agent evals 문서는 workflow-level agent evaluation 설계 원칙을 설명한다](https://platform.openai.com/docs/guides/agent-evals)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 평가하려는 workflow와 성공 조건을 정의한다.
    - 2) representative tasks와 grader를 준비한다.
    - 3) 반복 평가로 회귀와 품질 변화를 측정한다.

- [OpenAI Trace grading 문서는 agent trace를 기반으로 단계별 평가를 수행하는 방법을 설명한다](https://platform.openai.com/docs/guides/trace-grading)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) agent 실행 trace를 수집한다.
    - 2) 단계별 행동이나 intermediate state를 grader로 평가한다.
    - 3) black-box 최종 점수 외에 step-level failure를 분리한다.

- [OpenAI Graders 문서는 string, similarity, model, python grader를 설계하는 방법을 설명한다](https://platform.openai.com/docs/guides/graders/)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 평가 기준에 맞는 grader 타입을 선택한다.
    - 2) 입력과 기대 출력 구조를 정의한다.
    - 3) grader 결과를 pass-fail 또는 score로 환산한다.

- [OpenAI Evaluation best practices 문서는 eval 설계 시 representative dataset과 stable scoring을 강조한다](https://platform.openai.com/docs/guides/evaluation-best-practices)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 실제 사용 사례를 대표하는 eval set을 만든다.
    - 2) 변동이 낮은 scoring rule을 설계한다.
    - 3) 작은 변화도 회귀로 감지할 수 있게 반복 실행한다.

- [Inspect Scorers 문서는 scorer abstraction과 custom scoring 설계 방식을 설명한다](https://inspect.aisi.org.uk/scorers.html)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) task output에 맞는 scorer 인터페이스를 정의한다.
    - 2) rule-based 또는 model-based scoring을 구현한다.
    - 3) scorer 결과를 experiment log에 기록한다.

- [Inspect Tracing 문서는 agent run의 trace와 intermediate execution record를 분석하는 방법을 설명한다](https://inspect.aisi.org.uk/tracing.html)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 실행 중 action, tool call, state를 tracing한다.
    - 2) failure point와 latency를 분석한다.
    - 3) trace 기반 디버깅과 score 해석을 수행한다.

- [Inspect Log Viewer 문서는 in-progress evaluation과 run log를 시각적으로 관찰하는 방법을 제공한다](https://inspect.aisi.org.uk/log-viewer.html)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) eval run log를 viewer-friendly 형식으로 저장한다.
    - 2) step별 실행 상태를 시각적으로 확인한다.
    - 3) failure 사례를 빠르게 분류한다.

- [Inspect Tutorial은 tool-use task를 포함한 Inspect AI 시작 절차를 제공한다](https://inspect.aisi.org.uk/tutorial.html)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 기본 task와 solver를 설정한다.
    - 2) tool-use 또는 multi-turn 예제를 실행한다.
    - 3) scorer와 log 결과를 해석한다.

- [Promptfoo Simulated User 문서는 simulated user를 활용한 multi-turn agent testing 패턴을 제공한다](https://www.promptfoo.dev/docs/providers/simulated-user/)
  - sources: `skill-acceptance-gate-reference-at2026-03-15-02-17.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) user simulator의 persona와 목표를 정의한다.
    - 2) target agent와 multi-turn conversation을 실행한다.
    - 3) assertion과 transcript를 바탕으로 acceptance를 판정한다.

## How To Use This Knowledge Base

이 문서는 단순 URL 인덱스가 아니라 `skill-acceptance-gate` 설계를 위한 **선별 reference map**이다. 읽는 순서는 논문 발표 순서가 아니라 **구현 의사결정 순서**를 따라야 한다.

### 읽는 순서

1. **평가 프레임워크**를 먼저 읽는다.
   - 이유: 어떤 구조로 eval dataset, scorer, trace, report를 구성할지 먼저 고정해야 이후 benchmark reference를 어디에 매핑할지 결정할 수 있다.
   - 추천 시작점: `Inspect AI` → `OpenAI Agent evals / Trace grading / Graders / Evaluation best practices` → `Promptfoo`

2. **agent benchmark / 논문**을 두 번째로 읽는다.
   - 이유: 어떤 평가 축이 빠지면 안 되는지, 즉 `success-only` 평가를 넘어 어떤 dimensions가 필요한지 배울 수 있다.
   - 추천 시작점: `AgentBoard` → `τ-bench` → `AgentDojo` → `SWE-bench`

3. **공식 문서/운영 문서**를 세 번째로 읽는다.
   - 이유: 실제 구현할 scorer, trace, simulated user, Python grader가 어떤 인터페이스를 가져야 하는지 코드 수준으로 떨어뜨릴 수 있다.

### 이 문서에서 뽑아야 하는 것

- `trigger correctness`를 판정하는 기준
- `boundary ownership`를 판정하는 기준
- `schema validity`를 강제하는 방식
- `runtime trace`를 저장하고 채점하는 방식
- `simulated user / tool loop` 평가 방식
- `adversarial / robustness` 평가 방식
- `regression gate`를 유지하는 방법
- `executable acceptance`를 최종 게이트로 삼는 방법

### 이 문서만으로 결정하지 말아야 하는 것

- 특정 모델의 절대 성능 비교
- 특정 프레임워크 하나만을 절대 표준으로 삼는 결정
- 현재 프로젝트의 최종 file layout
- 현재 프로젝트에 바로 필요한 모든 script signature

이 문서는 **reference 해석과 요구사항 추출**까지를 담당한다. 실제 file format, CLI signature, state machine은 이 문서를 바탕으로 별도 `references/` 문서에서 고정해야 한다.

## Acceptance-Gate Evaluation Dimensions

`skill-acceptance-gate`는 아래 8개 평가 축을 모두 다뤄야 한다. 이 8개 중 1~2개만 있으면 스킬 검증이 아니라 단순 smoke test가 된다.

| 축 | 질문 | 실패 예시 | 필요한 산출물 |
|---|---|---|---|
| Trigger Correctness | 이 요청에서 이 Skill이 발동해야 하는가 | 불필요한 Skill 오발동 / 필요한데 미발동 | trigger matrix |
| Boundary Correctness | 이 Skill이 소유하지 않은 필드를 수정하지 않는가 | packet이 dispatch 상태를 덮어씀 | boundary rules |
| Schema Validity | 입력/출력이 계약된 schema를 만족하는가 | 필수 필드 누락, 금지 필드 유입 | schema validator |
| Runtime Traceability | 중간 행동과 실패 위치를 추적 가능한가 | 최종 실패만 있고 이유를 모름 | trace log / trace grader |
| Tool / Multi-turn Correctness | 실제 agent loop와 tool 호출 맥락에서 맞게 작동하는가 | 단일 턴에선 통과하지만 실제 loop에선 실패 | simulated user / tool-use eval |
| Adversarial Robustness | 경계 위반, prompt injection, misuse에 버티는가 | 허용 경로 밖 수정, injected instruction 수용 | adversarial suite |
| Regression Stability | 수정 후에도 기존 기능이 유지되는가 | 예전 통과 케이스 재실패 | regression suite |
| Executable Acceptance | 최종 산출물이 실제로 통합 가능한가 | schema는 맞지만 merge-check 불가 | release gate / executable check |

### 이 8개 축을 Skill 구현에 대응시키는 방법

- `trigger correctness` → `evals/evals.json`의 positive/negative trigger cases
- `boundary correctness` → ownership field matrix + forbidden mutation tests
- `schema validity` → JSON schema validator + malformed sample tests
- `runtime traceability` → trace log JSONL + run summary + anomaly detector
- `tool / multi-turn correctness` → simulated user conversations + orchestrated agent loop replay
- `adversarial robustness` → malicious packet / prompt injection / path escape samples
- `regression stability` → fixed golden cases + snapshot outputs + CI run
- `executable acceptance` → merge-check / release-check / artifact presence gate

## Coverage Matrix

아래 매트릭스는 어떤 reference가 어떤 acceptance dimension을 강하게 커버하는지 요약한 것이다.

Legend:
- `H` = 핵심 reference
- `M` = 보조 reference
- `L` = 간접 reference

| Reference | Trigger | Boundary | Schema | Trace | Multi-turn | Adversarial | Regression | Executable |
|---|---|---|---|---|---|---|---|---|
| OpenAI Evals | M | L | H | L | M | L | H | L |
| Inspect AI | M | M | H | H | H | M | H | M |
| Promptfoo | H | M | H | M | H | H | H | L |
| DeepEval | M | M | M | H | M | M | M | L |
| AWS Agent Evaluation | M | L | M | M | H | L | M | L |
| AgentBench | L | L | L | M | H | L | M | L |
| AgentBoard | M | M | L | H | H | L | M | L |
| τ-bench | M | M | L | M | H | M | M | L |
| AgentDojo | M | H | L | H | H | H | M | L |
| SWE-bench | L | M | M | M | L | L | M | H |
| iAgentBench | L | L | L | M | H | L | M | M |
| OpenAI Trace grading | L | M | L | H | M | L | M | L |
| OpenAI Graders | M | M | H | M | L | L | H | L |
| Eval best practices | H | M | H | M | M | M | H | M |
| Inspect Scorers | M | M | H | M | L | L | H | L |
| Inspect Tracing | L | M | L | H | M | M | M | L |
| Inspect Log Viewer | L | L | L | H | M | L | M | L |
| Promptfoo Simulated User | M | M | M | M | H | M | M | L |

### Matrix 해석 규칙

- `OpenAI Evals`만 읽고 끝내면 `trace`와 `boundary`가 약해진다.
- `Inspect AI`만 읽고 끝내면 framework는 강해지지만 adversarial/CI gate 설계가 약해질 수 있다.
- `Promptfoo`만 읽고 끝내면 assertion 중심 regression은 강하지만 deeper trace analysis가 부족할 수 있다.
- `SWE-bench`를 너무 일찍 가져오면 executable gate만 과대평가하고 trigger/boundary 설계가 빈약해질 수 있다.
- `AgentDojo`를 넣지 않으면 boundary break와 injection 사례를 acceptance gate에 넣지 못할 가능성이 높다.

## Detailed Reference Notes

아래 메모는 단순 요약이 아니라, 각 reference에서 `skill-acceptance-gate`가 실제로 무엇을 뽑아와야 하는지에 초점을 맞춘다.

### 1. Inspect AI
- 왜 중요한가:
  - `Task + solver + scorer + log/trace` 구조가 가장 직접적으로 `skill-acceptance-gate`의 실행 단위를 닮아 있다.
- skill에 주는 설계 시사점:
  - Skill acceptance는 단일 문자열 비교가 아니라 `task definition`, `intermediate run`, `scorer`, `metadata`를 함께 봐야 한다.
- 꼭 추출할 것:
  - built-in scorer와 custom scorer 분리 방식
  - trace anomaly 처리 방식
  - eval log를 나중에 사람이 읽고 디버깅하는 viewer workflow
- 구현에 반영할 artefact:
  - `gate_trace_grade.py`
  - `gate_log_bundle.py`
  - `gate_score_schema.json`
- 놓치기 쉬운 위험:
  - trace는 저장하지만 점수와 연결하지 못하는 설계
  - scorer를 너무 자유형으로 두어 결과 비교가 불안정해지는 문제

### 2. OpenAI Trace grading
- 왜 중요한가:
  - black-box 결과만 보는 평가를 벗어나, agent의 trace를 structured score로 바꾸는 아이디어를 명확히 준다.
- skill에 주는 설계 시사점:
  - `skill-acceptance-gate`는 최종 성공/실패 외에도 `어느 단계에서 어긋났는지`를 라벨링해야 한다.
- 꼭 추출할 것:
  - trace 단위의 label/score schema
  - workflow-level error identification
- 구현에 반영할 artefact:
  - `trace_grading_rules.md`
  - `gate_trace_labels.json`
- 놓치기 쉬운 위험:
  - trace를 남기기만 하고 grade로 구조화하지 않으면 디버깅 기록이 축적되지 않는다.

### 3. OpenAI Graders
- 왜 중요한가:
  - `string`, `similarity`, `model`, `python` grader를 상황별로 고르는 설계 원칙을 준다.
- skill에 주는 설계 시사점:
  - 하나의 score 방식으로 모든 Skill을 평가하면 안 된다.
  - trigger/boundary는 rule-based, trajectory 품질은 model/python grader가 맞다.
- 꼭 추출할 것:
  - Python grader 인터페이스
  - invalid result handling rule
- 구현에 반영할 artefact:
  - `graders/trigger_grade.py`
  - `graders/boundary_grade.py`
  - `graders/trace_grade.py`
- 놓치기 쉬운 위험:
  - model grader를 남용해 deterministic하게 판정해야 할 case까지 불안정하게 만드는 것

### 4. OpenAI Evaluation best practices
- 왜 중요한가:
  - “대표성 있는 dataset”, “안정적 scoring”, “반복 가능한 regression”이 왜 중요한지 가장 직접적으로 말해준다.
- skill에 주는 설계 시사점:
  - Skill acceptance dataset은 synthetic showcase만으로 구성하면 안 되고 실제 failure pattern을 포함해야 한다.
- 꼭 추출할 것:
  - representative eval set 설계 원칙
  - eval iteration loop
- 구현에 반영할 artefact:
  - `gate_dataset_design.md`
  - `golden_cases/`
- 놓치기 쉬운 위험:
  - easy case 위주의 dataset으로 gate를 만들고 실제 현업 failure를 놓치는 것

### 5. Promptfoo
- 왜 중요한가:
  - declarative config, assertions, CI integration, red-team까지 한 흐름 안에 있다.
- skill에 주는 설계 시사점:
  - `skill-acceptance-gate`도 eventually config-driven eval spec를 가져야 한다.
- 꼭 추출할 것:
  - assertion schema
  - CI/CLI ergonomics
  - red-team extensions
- 구현에 반영할 artefact:
  - `gate_cases.yaml`
  - `gate_assertions.md`
  - `gate_ci_contract.md`
- 놓치기 쉬운 위험:
  - assertion은 많지만 trace/metadata와 연결이 안 되는 구조

### 6. Promptfoo Simulated User
- 왜 중요한가:
  - multi-turn simulated user testing이 `실제 agent loop에서 Skill이 작동하는가`를 보는 최소 레퍼런스다.
- skill에 주는 설계 시사점:
  - trigger correctness는 단일 turn prompt만으로 테스트하면 부족하다.
- 꼭 추출할 것:
  - session state 유지
  - function-calling agent 테스트 방식
  - debugging logs
- 구현에 반영할 artefact:
  - `gate_simulated_user.py`
  - `sim-users/basic.yaml`
  - `sim-users/adversarial.yaml`
- 놓치기 쉬운 위험:
  - single-turn unit eval만 통과하고 real multi-turn orchestration에서 무너지는 것

### 7. AgentBoard
- 왜 중요한가:
  - final accuracy만 보지 않고 progress / sub-skill / intermediate failures를 봐야 한다는 점을 강하게 제시한다.
- skill에 주는 설계 시사점:
  - `skill-acceptance-gate`는 `pass/fail`만으로 끝나면 안 되고 failure taxonomy를 가져야 한다.
- 꼭 추출할 것:
  - fine-grained evaluation axis
  - partial progress 개념
- 구현에 반영할 artefact:
  - `failure_taxonomy.md`
  - `gate_breakdown_report.py`
- 놓치기 쉬운 위험:
  - pass/fail binary만 남고 왜 실패했는지 카테고리화가 안 되는 것

### 8. τ-bench
- 왜 중요한가:
  - simulated user + domain rules + API tools를 동시에 본다.
- skill에 주는 설계 시사점:
  - boundary correctness는 static schema validation만으로 충분하지 않다. 실제 tool loop에서 policy adherence를 봐야 한다.
- 꼭 추출할 것:
  - policy adherence 개념
  - realistic tool-user-agent interaction
- 구현에 반영할 artefact:
  - `gate_policy_cases.yaml`
  - `gate_tool_loop_eval.py`
- 놓치기 쉬운 위험:
  - tool 호출 자체는 성공해도 domain rule 위반을 놓치는 것

### 9. AgentDojo
- 왜 중요한가:
  - acceptance gate에 adversarial robustness를 넣어야 한다는 가장 직접적인 근거다.
- skill에 주는 설계 시사점:
  - `forbidden_paths`, `boundary break`, `prompt injection`, `tool-return hijack`를 정식 negative suite로 넣어야 한다.
- 꼭 추출할 것:
  - extensible attack/defense environment 아이디어
  - security test case corpus 사고방식
- 구현에 반영할 artefact:
  - `gate_adversarial_suite.py`
  - `attack-cases/`
  - `boundary-break-cases/`
- 놓치기 쉬운 위험:
  - security/injection tests를 release 직전에만 붙이는 것

### 10. SWE-bench
- 왜 중요한가:
  - 최종 acceptance는 결국 실행 가능한 산출물 여부까지 봐야 한다는 기준을 준다.
- skill에 주는 설계 시사점:
  - `skill-acceptance-gate`도 마지막에는 script exit code, artifact existence, merge readiness까지 체크해야 한다.
- 꼭 추출할 것:
  - issue-to-patch-to-test 구조
  - reproducible execution environment 사고방식
- 구현에 반영할 artefact:
  - `gate_release_check.py`
  - `gate_artifact_contract.json`
- 놓치기 쉬운 위험:
  - LLM judge나 metadata validation만 통과하고 실제 실행 불가 상태를 놓치는 것

## Direct Mapping To Planned Skill Artifacts

아래 표는 현재 reference corpus를 `skill-acceptance-gate` 구현 산출물에 직접 연결한 것이다.

| planned artifact | primary references | 목적 |
|---|---|---|
| `references/OPERATING_CRITERIA.md` | Eval best practices, AgentBoard, Inspect AI | Skill acceptance 축과 판정 원칙 고정 |
| `references/BOUNDARY_RULES.md` | AgentDojo, τ-bench, OpenAI Graders | ownership / forbidden mutation 규칙 고정 |
| `references/TRACE_GRADING.md` | OpenAI Trace grading, Inspect Tracing | trace label과 anomaly 판정 규칙 정의 |
| `references/FAILURE_TAXONOMY.md` | AgentBoard, AgentBench, AgentDojo | failure category 체계화 |
| `references/REGRESSION_POLICY.md` | OpenAI Evals, Promptfoo, Eval best practices | regression suite와 golden cases 관리 |
| `scripts/gate_validate_schema.py` | OpenAI Graders, Inspect Scorers | schema + deterministic checks |
| `scripts/gate_trigger_matrix.py` | Promptfoo, Eval best practices | positive/negative trigger eval |
| `scripts/gate_boundary_audit.py` | AgentDojo, τ-bench | forbidden mutation / boundary break 탐지 |
| `scripts/gate_trace_grade.py` | Trace grading, Inspect Tracing | trace 기반 구조화 판정 |
| `scripts/gate_simulated_user.py` | Promptfoo Simulated User, τ-bench, AWS Agent Evaluation | multi-turn acceptance |
| `scripts/gate_regression_suite.py` | OpenAI Evals, Promptfoo | stable regression check |
| `scripts/gate_release_check.py` | SWE-bench | executable acceptance gate |

## Recommended Reading Plan For Implementation

### Tier 1: 바로 구현에 쓰는 문서
1. Inspect AI
2. OpenAI Evaluation best practices
3. OpenAI Trace grading
4. OpenAI Graders
5. Promptfoo

이 다섯 개로 아래를 먼저 고정할 수 있어야 한다.
- eval case file format
- scorer interface
- trace log format
- pass/fail gate structure
- regression 실행 루프

### Tier 2: 평가 범위 확장에 쓰는 문서
6. AgentBoard
7. τ-bench
8. Promptfoo Simulated User
9. AWS Agent Evaluation
10. DeepEval

이 묶음은 아래를 확장할 때 사용한다.
- multi-turn acceptance
- intermediate failure labeling
- tool-use policy gate
- evaluator agent or simulated user loop

### Tier 3: hard gate와 security에 쓰는 문서
11. AgentDojo
12. SWE-bench
13. iAgentBench

이 묶음은 아래를 확장할 때 사용한다.
- adversarial boundary tests
- executable release gate
- dynamic information-seeking evaluation

## What The Future Skill Should Probably Validate

`skill-acceptance-gate`가 최종적으로 검증해야 하는 것은 아래 4계층이다.

### Layer 1. Static Contract Layer
- schema valid
- required fields present
- forbidden fields absent
- ownership boundary respected
- relative path normalization valid

### Layer 2. Controlled Runtime Layer
- happy-path script success
- negative-path rejection
- trace captured
- score produced
- deterministic summary generated

### Layer 3. Agent Loop Layer
- multi-turn trigger correctness
- tool loop correctness
- simulated user interaction stability
- timeout / retry / anomaly labeling

### Layer 4. Release Gate Layer
- regression suite pass
- adversarial suite pass
- required artifact generated
- merge/release/executable checks pass

## Common Failure Modes This KB Is Trying To Prevent

- final success rate만 보고 intermediate failure를 놓치는 것
- `trace` 없이 pass/fail만 남기는 것
- `boundary` 위반을 schema 검증만으로 충분하다고 착각하는 것
- single-turn eval만 통과시키고 multi-turn loop를 검증하지 않는 것
- adversarial 케이스를 release 직전에야 붙이는 것
- LLM-judge 결과를 executable acceptance보다 앞에 두는 것
- regression set에 real failure pattern이 반영되지 않는 것
- docs는 많은데 scorer/script contract가 없는 것

## Suggested Next Files To Create In references/

- `OPERATING_CRITERIA.md`
- `BOUNDARY_RULES.md`
- `TRACE_GRADING.md`
- `FAILURE_TAXONOMY.md`
- `REGRESSION_POLICY.md`
- `ADVERSARIAL_TESTS.md`
- `RELEASE_GATE.md`

## Suggested Next Scripts To Create In scripts/

- `gate_validate_schema.py`
- `gate_trigger_matrix.py`
- `gate_boundary_audit.py`
- `gate_trace_grade.py`
- `gate_simulated_user.py`
- `gate_regression_suite.py`
- `gate_release_check.py`

## Suggested Minimal Acceptance Plan

### v0.1
- static schema validation
- trigger matrix
- boundary audit
- simple trace capture
- basic regression suite

### v0.2
- multi-turn simulated user eval
- trace grading labels
- failure taxonomy report
- adversarial negative suite

### v0.3
- executable release gate
- richer tool-loop scoring
- published log bundle / inspect-style viewer integration
- CI integration with red/green acceptance policy
