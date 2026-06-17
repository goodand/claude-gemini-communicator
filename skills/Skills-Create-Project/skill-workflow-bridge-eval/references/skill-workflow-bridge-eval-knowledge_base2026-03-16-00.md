# research URL Knowledge Base
- ver: `v0.1.0`
- generated_at: `2026-03-16`
- updated_at: `2026-03-16` (v0.1.0: workflow-bridge-eval reference corpus and detailed mapping added)
- format: `- [한 줄 설명](URL)`
- generation_method: `manual curation based on primary papers, official documentation, GitHub repositories, and internal skill references for workflow bridge/evaluation design`
- total_urls: `21`
- paper_like_urls: `6`
- other_urls: `15`

## Document Map

| 문서 | 역할 |
|------|------|
| [Boundary-of-Responsibility-2026-03-15-03-56.md](./Boundary-of-Responsibility-2026-03-15-03-56.md) | `skill-workflow-bridge-eval`의 canonical 책임 경계 문서 |
| [skill-workflow-bridge-eval-reference-2026-03-16-01.md](./skill-workflow-bridge-eval-reference-2026-03-16-01.md) | 장문 설계 reference · workflow mode / retry / handoff packet / decision model |
| `skill-workflow-bridge-eval-knokledge_base2026-03-16-00.md` (이 파일) | 외부 논문·공식 문서·GitHub reference 21개 인덱스 |
| [skill-workflow-bridge-eval-checklist-2026-03-16-02.md](./skill-workflow-bridge-eval-checklist-2026-03-16-02.md) | 구현 정합성 평가 체크리스트 |
| [../../../../my-second-identity/template/knowledge_base.md](../../../../my-second-identity/template/knowledge_base.md) | knowledge base 작성 템플릿 원본 |

## Table of Contents
- [Paper-like URLs](#paper-like-urls)
- [Other research References URLs](#other-research-references-urls)
- [How To Use This Knowledge Base](#how-to-use-this-knowledge-base)
- [Workflow-Bridge Evaluation Dimensions](#workflow-bridge-evaluation-dimensions)
- [Coverage Matrix](#coverage-matrix)
- [Direct Mapping To Planned Skill Artifacts](#direct-mapping-to-planned-skill-artifacts)
- [Recommended Reading Order](#recommended-reading-order)
- [Common Failure Modes This KB Is Trying To Prevent](#common-failure-modes-this-kb-is-trying-to-prevent)
- [Suggested Minimal Reference Stack For v01](#suggested-minimal-reference-stack-for-v01)
- [Suggested Next Files To Create In references](#suggested-next-files-to-create-in-references)
- [Suggested Next Scripts To Create In scripts](#suggested-next-scripts-to-create-in-scripts)
- [Suggested Minimal Acceptance Plan](#suggested-minimal-acceptance-plan)

## Paper-like URLs

- [AgentBench는 LLM을 환경 속 agent로 평가하며 task success만이 아니라 multi-environment action performance를 보는 초기 대표 benchmark다](https://arxiv.org/abs/2308.03688)
  - sources: `manual_reading_2026-03-16`
  - agent: `A00`
  - cross_ref: 책임 경계 [Boundary-of-Responsibility-2026-03-15-03-56.md](./Boundary-of-Responsibility-2026-03-15-03-56.md) · 장문 설계 [skill-workflow-bridge-eval-reference-2026-03-16-01.md](./skill-workflow-bridge-eval-reference-2026-03-16-01.md) · 관련 논문 [#02-agentboard-analytical-evaluation](#02-agentboard-analytical-evaluation)
  - anchor_note: `#01-agentbench-evaluating-llms-as-agents`
  - taxonomy: [[agent-benchmark, environment-based, workflow-evaluation]] · Axis W
  - key_idea: AgentBench는 agent를 단발 응답 모델이 아니라 환경 내 행동 주체로 보고, 다양한 environment에서 과업 수행과 상호작용 능력을 평가한다.
  - execution_conditions: step-level success와 environment feedback를 기록하는 harness가 필요하며, intermediate trajectory를 분석할 수 있어야 한다.
  - pseudocode_3lines:
    - 1) Agent를 environment에 배치하고 task 수행 trajectory를 기록한다.
    - 2) 최종 성공뿐 아니라 intermediate interaction quality와 failure points를 분석한다.
    - 3) 여러 task/domain에서 agent capability를 비교한다.

- [AgentBoard는 multi-turn LLM agent를 analytical evaluation board 방식으로 평가하며 final score보다 progress와 trajectory 분석을 강조한다](https://arxiv.org/abs/2401.13178)
  - sources: `manual_reading_2026-03-16`
  - agent: `A00`
  - cross_ref: 책임 경계 [Boundary-of-Responsibility-2026-03-15-03-56.md](./Boundary-of-Responsibility-2026-03-15-03-56.md) · 장문 설계 [skill-workflow-bridge-eval-reference-2026-03-16-01.md](./skill-workflow-bridge-eval-reference-2026-03-16-01.md) · 관련 논문 [#01-agentbench-evaluating-llms-as-agents](#01-agentbench-evaluating-llms-as-agents)
  - anchor_note: `#02-agentboard-analytical-evaluation`
  - taxonomy: [[trajectory-analysis, progress-eval, multi-turn-agent]] · Axis W
  - key_idea: AgentBoard는 에이전트 평가에서 단순 정답률 대신 intermediate step과 progress를 분석 가능한 board 형태로 구조화한다.
  - execution_conditions: run-level trace, step-level event log, failure taxonomy, progress metric이 필요하다.
  - pseudocode_3lines:
    - 1) multi-turn agent run의 intermediate events와 progress indicators를 기록한다.
    - 2) final success 외에 어떤 단계에서 막혔는지 analytical하게 분해한다.
    - 3) agent별 trajectory quality를 비교한다.

- [τ-bench는 tool-agent-user interaction을 실제 도메인과 policy constraints 안에서 평가하는 benchmark로 handoff quality를 interaction 품질로 보게 해준다](https://arxiv.org/abs/2406.12045)
  - sources: `manual_reading_2026-03-16`
  - agent: `A00`
  - cross_ref: 장문 설계 [skill-workflow-bridge-eval-reference-2026-03-16-01.md](./skill-workflow-bridge-eval-reference-2026-03-16-01.md) · 관련 문서 `FANIN_POLICY.md` 예정 · 관련 논문 [#04-agentdojo-robustness](#04-agentdojo-robustness)
  - anchor_note: `#03-tau-bench-tool-agent-user`
  - taxonomy: [[tool-interaction, policy-adherence, simulated-user]] · Axis W
  - key_idea: tool agent의 성능은 내부 reasoning뿐 아니라 user/tool/policy와의 상호작용 품질로도 평가되어야 한다.
  - execution_conditions: simulated user 또는 downstream consumer를 명시적으로 두고 interaction log를 저장해야 한다.
  - pseudocode_3lines:
    - 1) user request, tool actions, policy constraints를 함께 설정한다.
    - 2) agent의 intermediate actions와 consumer-facing outputs를 기록한다.
    - 3) task success와 policy adherence를 동시에 평가한다.

- [AgentDojo는 agent robustness와 adversarial failure를 평가하는 benchmark로 natural-language output과 misleading completion claim을 그대로 신뢰하면 안 된다는 근거를 준다](https://arxiv.org/abs/2406.13352)
  - sources: `manual_reading_2026-03-16`
  - agent: `A00`
  - cross_ref: 책임 경계 [Boundary-of-Responsibility-2026-03-15-03-56.md](./Boundary-of-Responsibility-2026-03-15-03-56.md) · 장문 설계 [skill-workflow-bridge-eval-reference-2026-03-16-01.md](./skill-workflow-bridge-eval-reference-2026-03-16-01.md) · 관련 논문 [#03-tau-bench-tool-agent-user](#03-tau-bench-tool-agent-user)
  - anchor_note: `#04-agentdojo-robustness`
  - taxonomy: [[robustness, adversarial-eval, misleading-output]] · Axis W
  - key_idea: agent output은 completion claim만으로 신뢰하면 안 되며, adversarial or malformed outputs를 견디는 evaluation layer가 필요하다.
  - execution_conditions: unsafe, ambiguous, misleading, malformed output에 대한 failure taxonomy와 evaluator가 필요하다.
  - pseudocode_3lines:
    - 1) adversarial 또는 misleading output case를 준비한다.
    - 2) raw output을 그대로 통과시키지 않고 robust grading을 수행한다.
    - 3) unsafe or ambiguous decision은 stop/escalate로 분리한다.

- [SWE-bench는 real-world GitHub issue 해결력을 평가하며 executable verification과 issue-to-patch trace가 중요하다는 기준을 준다](https://arxiv.org/abs/2310.06770)
  - sources: `manual_reading_2026-03-16`
  - agent: `A00`
  - cross_ref: 장문 설계 [skill-workflow-bridge-eval-reference-2026-03-16-01.md](./skill-workflow-bridge-eval-reference-2026-03-16-01.md) · 관련 문서 `ARTIFACT_SCHEMA.md` 예정 · 관련 논문 [#02-agentboard-analytical-evaluation](#02-agentboard-analytical-evaluation)
  - anchor_note: `#05-swe-bench-executable-verification`
  - taxonomy: [[coding-agent, executable-verification, patch-trace]] · Axis W
  - key_idea: coding workflow에서는 설명보다 executable artifact와 traceable verification이 더 강한 성공 증거가 된다.
  - execution_conditions: output artifact existence, tests, patch provenance, run logs를 함께 봐야 한다.
  - pseudocode_3lines:
    - 1) issue 또는 task를 concrete artifact task로 내린다.
    - 2) patch/output을 실행 가능한 검증 기준으로 확인한다.
    - 3) 성공 claim이 아니라 executable evidence로 pass/fail을 결정한다.

- [iAgentBench는 정보 탐색형 agent의 sensemaking을 고트래픽·현실성 있는 주제로 평가해, multi-step bridge quality를 정보 정제 관점에서 보게 한다](https://arxiv.org/abs/2603.04656)
  - sources: `manual_reading_2026-03-16`
  - agent: `A00`
  - cross_ref: 장문 설계 [skill-workflow-bridge-eval-reference-2026-03-16-01.md](./skill-workflow-bridge-eval-reference-2026-03-16-01.md) · 관련 논문 [#01-agentbench-evaluating-llms-as-agents](#01-agentbench-evaluating-llms-as-agents)
  - anchor_note: `#06-iagentbench-sensemaking`
  - taxonomy: [[information-seeking, sensemaking, multi-step-eval]] · Axis W
  - key_idea: 정보 탐색형 agent는 단순 retrieval이 아니라 탐색 결과를 정제하고 다음 step에 쓸 수 있게 구조화하는 능력까지 평가돼야 한다.
  - execution_conditions: evidence trace, intermediate notes, synthesis quality, next-step utility를 기록해야 한다.
  - pseudocode_3lines:
    - 1) 여러 정보 source에서 evidence를 수집한다.
    - 2) evidence를 정리해 sensemaking artifact를 만든다.
    - 3) 이 artifact가 다음 step의 입력으로 실제로 유용한지 평가한다.

## Other research References URLs

- [Anthropic의 Building Effective Agents는 sequential, parallel, evaluator-optimizer workflow를 실제 agent pattern으로 구분해 이 skill의 모드 정의에 가장 직접적인 공식 기준을 제공한다](https://www.anthropic.com/research/building-effective-agents)
  - sources: `official_article_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: workflow mode taxonomy의 1차 기준.
  - pseudocode_3lines:
    - 1) 문제 유형에 따라 sequential, parallel, evaluator-optimizer 중 적절한 workflow를 선택한다.
    - 2) 각 workflow의 장단점과 비용 구조를 고려해 orchestration policy를 정한다.
    - 3) 복잡한 multi-agent로 가기 전에 단일 agent baseline을 확보한다.

- [Anthropic의 multi-agent research system 구축 글은 agent 간 handoff와 역할 분리가 raw output dump가 아니라 구조화된 workflow artifact여야 함을 보여준다](https://www.anthropic.com/engineering/built-multi-agent-research-system)
  - sources: `official_article_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: handoff packet과 role-based decomposition 설계의 상위 reference.
  - pseudocode_3lines:
    - 1) 연구/계획/작성/검증 역할을 분리한다.
    - 2) 각 역할의 산출물을 다음 역할이 소비 가능한 형태로 구조화한다.
    - 3) 최종적으로 role outputs를 synthesis한다.

- [OpenAI Agent Evals 가이드는 agent run을 task-level과 trajectory-level로 평가하는 기본 틀을 제공해 bridge_eval과 run trace 설계의 기준이 된다](https://platform.openai.com/docs/guides/agent-evals)
  - sources: `official_docs_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: workflow_run / step_run / artifact lineage 설계 기준.
  - pseudocode_3lines:
    - 1) agent run 단위를 명확히 정의한다.
    - 2) intermediate trajectory와 artifacts를 기록한다.
    - 3) run 결과를 pass/fail 이상으로 구조화한다.

- [OpenAI Trace Grading은 intermediate trace를 평가 대상으로 삼아, step-to-step handoff quality를 최종 응답과 분리해 볼 수 있게 한다](https://platform.openai.com/docs/guides/trace-grading)
  - sources: `official_docs_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: handoff trace grading 및 decision trace 저장 기준.
  - pseudocode_3lines:
    - 1) intermediate trace를 별도 평가 대상으로 정의한다.
    - 2) 각 단계의 trace에 대해 grading 기준을 적용한다.
    - 3) final output과 trace quality를 분리해 분석한다.

- [OpenAI Graders는 자연어 출력과 구조화 출력을 score 또는 pass/fail로 바꾸는 grader 설계의 기본 reference다](https://platform.openai.com/docs/guides/graders/)
  - sources: `official_docs_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: extractor grader, decision grader, evidence grader 분리 설계 참고.
  - pseudocode_3lines:
    - 1) 출력에서 평가 기준을 추출한다.
    - 2) grader를 통해 structured score/pass-fail로 변환한다.
    - 3) grading 결과를 다음 decision 로직에 연결한다.

- [OpenAI Evaluation Best Practices는 failure taxonomy와 test design을 미리 고정하라고 권장하며 retry/reroute 기준을 ad-hoc로 두지 않게 해준다](https://platform.openai.com/docs/guides/evaluation-best-practices)
  - sources: `official_docs_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: recoverable/irrecoverable/no-progress 같은 failure taxonomy 설계 기준.
  - pseudocode_3lines:
    - 1) 평가 기준과 실패 유형을 미리 분류한다.
    - 2) representative failure cases를 설계한다.
    - 3) 평가 결과를 개선 가능한 feedback loop로 연결한다.

- [Inspect AI GitHub 저장소는 multi-step eval, scorer abstraction, trace-based analysis를 지원하는 framework reference다](https://github.com/UKGovernmentBEIS/inspect_ai)
  - sources: `github_readme_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: scorer abstraction과 trace-oriented evaluation framework reference.
  - pseudocode_3lines:
    - 1) evaluation task와 scorer를 분리한다.
    - 2) trace와 log를 남겨 run 분석이 가능하게 한다.
    - 3) 동일 평가 harness를 여러 workflow에 재사용한다.

- [Inspect Tracing 문서는 intermediate execution trace를 저장하고 분석하는 방식이 bridge decision trace와 잘 맞는다는 점을 보여준다](https://inspect.aisi.org.uk/tracing.html)
  - sources: `official_docs_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: step event log와 decision trace 설계 reference.
  - pseudocode_3lines:
    - 1) run과 trace를 함께 저장한다.
    - 2) trace 안에서 intermediate actions를 분석한다.
    - 3) trace를 기준으로 failure point를 분해한다.

- [Inspect Scorers 문서는 different output modality를 공통 scorer interface로 평가하는 방식이 output_type별 bridge_eval 설계와 잘 맞는다](https://inspect.aisi.org.uk/scorers.html)
  - sources: `official_docs_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: `script_result`, `structured_json`, `natural_language`, `mixed`를 통합 평가하는 scorer abstraction 참고.
  - pseudocode_3lines:
    - 1) 출력 타입별 평가 함수를 공통 interface 아래 둔다.
    - 2) 각 scorer가 pass/score/evidence를 만든다.
    - 3) scorer 결과를 공통 decision engine으로 연결한다.

- [Inspect Log Viewer는 run/trace/log를 한 번에 보는 운영 감각을 제공해 workflow_run과 step_run을 구분한 기록 설계에 도움을 준다](https://inspect.aisi.org.uk/log-viewer.html)
  - sources: `official_docs_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: human-reviewable run record UX 참고.
  - pseudocode_3lines:
    - 1) run, trace, score를 함께 볼 수 있게 한다.
    - 2) 어느 step에서 실패했는지 즉시 찾을 수 있게 한다.
    - 3) 분석 결과를 다음 개선 루프로 연결한다.

- [Promptfoo의 simulated user 기능은 downstream skill 또는 consumer를 simulated evaluator처럼 취급하는 multi-turn handoff evaluation reference다](https://www.promptfoo.dev/docs/providers/simulated-user/)
  - sources: `official_docs_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: downstream consumer simulation과 multi-turn evaluator loop reference.
  - pseudocode_3lines:
    - 1) simulated user나 consumer를 준비한다.
    - 2) agent output이 consumer 요구를 만족하는지 대화적으로 평가한다.
    - 3) 불충분하면 feedback을 생성해 다음 loop에 반영한다.

- [AWS Agent Evaluation은 target agent와 evaluator agent를 분리해 multi-turn evaluation을 수행하는 구조를 보여준다](https://github.com/awslabs/agent-evaluation)
  - sources: `github_readme_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: producer skill과 bridge evaluator를 분리하는 구조 reference.
  - pseudocode_3lines:
    - 1) target agent와 evaluator agent를 분리한다.
    - 2) evaluator가 intermediate outputs를 평가한다.
    - 3) 평가 결과를 기준으로 다음 action을 결정한다.

- [DeepEval은 LLM application과 agent output의 component-level 평가를 지원해 handoff readiness나 repairability 같은 custom metric 설계에 유용하다](https://github.com/confident-ai/deepeval)
  - sources: `github_readme_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: custom bridge metrics 설계 reference.
  - pseudocode_3lines:
    - 1) 필요한 evaluation metric을 custom하게 정의한다.
    - 2) component-level로 output quality를 측정한다.
    - 3) metric 결과를 개선 루프에 연결한다.

- [MCP Agent Workflows Overview는 sequential, parallel, evaluator-optimizer 같은 workflow pattern을 실제 agent system 설계에 매핑한다](https://docs.mcp-agent.com/patterns/workflows/overview)
  - sources: `official_docs_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: workflow mode abstraction의 구현 reference.
  - pseudocode_3lines:
    - 1) workflow pattern을 모드 단위로 분리한다.
    - 2) 각 모드의 실행/평가/종료 규칙을 정한다.
    - 3) task 특성에 맞게 workflow를 선택한다.

- [MCP Agent Evaluator-Optimizer 문서는 evaluator feedback을 structured retry input으로 바꾸는 loop 설계의 직접 reference다](https://docs.mcp-agent.com/patterns/workflows/evaluator_optimizer)
  - sources: `official_docs_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: `retry_spec`와 `loop_state` 설계의 1차 reference.
  - pseudocode_3lines:
    - 1) generator가 candidate output을 생성한다.
    - 2) evaluator가 candidate를 점검하고 feedback을 만든다.
    - 3) feedback을 structured retry input으로 사용해 loop를 반복한다.

- [OpenAI Agents Python은 handoff, tracing, sessions 개념을 framework 수준에서 제공해 skill 간 handoff packet과 run lineage 설계에 참고가 된다](https://github.com/openai/openai-agents-python)
  - sources: `github_readme_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: handoff semantics와 session/trace vocabulary reference.
  - pseudocode_3lines:
    - 1) agent 간 handoff object를 정의한다.
    - 2) session과 trace를 함께 추적한다.
    - 3) handoff 결과를 다음 agent가 소비 가능한 contract로 만든다.

- [LangGraph는 stateful multi-agent workflow를 graph 형태로 모델링해, reroute와 branch/fan-in을 장기적으로 graph-based control로 확장할 수 있음을 보여준다](https://github.com/langchain-ai/langgraph)
  - sources: `github_readme_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: v0.1 이후 router/hybrid mode 확장 reference.
  - pseudocode_3lines:
    - 1) workflow 상태를 graph state로 모델링한다.
    - 2) branch와 loop, reroute를 graph transition으로 표현한다.
    - 3) state에 따라 다음 node를 결정한다.

- [CrewAI는 role-based multi-agent orchestration을 통해 specialist agent 조합과 sequential/parallel task 배치를 직관적으로 보여준다](https://github.com/crewAIInc/crewAI)
  - sources: `github_readme_manual_review_2026-03-16`
  - agent: `A00`
  - role_in_skill: specialist skill fan-out과 role-based branch 설계 참고.
  - pseudocode_3lines:
    - 1) 각 역할별 specialist agent를 정의한다.
    - 2) task를 sequential 또는 parallel하게 배치한다.
    - 3) specialist output을 다시 합쳐 최종 결론을 만든다.

## How To Use This Knowledge Base

이 knowledge base는 단순 URL 목록이 아니라, `skill-workflow-bridge-eval`을 설계할 때 어떤 축을 어떤 reference에서 가져와야 하는지 빠르게 찾기 위한 작업용 인덱스다.

권장 사용 순서:

1. 먼저 [Boundary-of-Responsibility-2026-03-15-03-56.md](./Boundary-of-Responsibility-2026-03-15-03-56.md)를 읽는다.
- 이 Skill이 무엇을 소유하고 무엇을 소유하지 않는지 먼저 고정한다.

2. 그 다음 [skill-workflow-bridge-eval-reference-2026-03-16-01.md](./skill-workflow-bridge-eval-reference-2026-03-16-01.md)를 읽는다.
- workflow mode, decision set, retry loop, natural-language normalization을 이해한다.

3. 그 다음 이 knowledge base의 `Coverage Matrix`를 본다.
- 어떤 reference가 어떤 설계 축을 덮는지 확인한다.

4. 필요한 문서를 골라 읽는다.
- `retry_spec` 설계가 필요하면 `Anthropic`, `MCP evaluator_optimizer`, `OpenAI graders`를 우선 본다.
- `trace/run lineage`가 필요하면 `AgentBoard`, `AgentBench`, `OpenAI trace grading`, `Inspect tracing`을 우선 본다.
- `fan-in policy`가 필요하면 `Anthropic`, `CrewAI`, `LangGraph`, `τ-bench`를 우선 본다.

5. 마지막으로 checklist로 되돌아간다.
- 구현 전에 기준을 문서화하고, 구현 후 checklist로 정합성 평가를 한다.

## Workflow-Bridge Evaluation Dimensions

### D1. Workflow Mode Awareness
- sequential
- parallel
- evaluator-optimizer
- hybrid/router future

### D2. Output Type Awareness
- script_result
- structured_json
- natural_language
- mixed

### D3. Handoff Readiness
- downstream contract satisfied?
- next_step_ready?
- missing items?
- evidence sufficient?

### D4. Retry Quality
- blind retry 금지
- repair retry 필요
- retry_spec schema 필요
- no-progress signal 필요

### D5. Decision Algebra
- pass
- retry
- reroute
- loop
- stop
- escalate
- fanout
- fanin_hold

### D6. Trace / Lineage
- workflow_run_id
- step_run_id
- raw_output
- bridge_eval
- retry_spec
- handoff_packet
- event log

### D7. Fan-in / Aggregation
- branch normalization
- branch conflict handling
- weighting or expert-first policy
- fanin_hold decision

### D8. Robustness Against Misleading Output
- completion claim 신뢰 금지
- malformed output
- ambiguous output
- misleading natural language
- unsafe or external-blocked taxonomy

## Coverage Matrix

| Reference | D1 Workflow Mode | D2 Output Type | D3 Handoff Readiness | D4 Retry Quality | D5 Decision Algebra | D6 Trace / Lineage | D7 Fan-in | D8 Robustness |
|---|---|---|---|---|---|---|---|---|
| `Anthropic effective agents` | Y | partial | partial | Y | Y | low | Y | partial |
| `Anthropic multi-agent system` | Y | partial | Y | partial | partial | partial | Y | partial |
| `OpenAI agent evals` | partial | partial | partial | partial | partial | Y | low | partial |
| `OpenAI trace grading` | low | partial | Y | partial | partial | Y | low | partial |
| `OpenAI graders` | low | Y | Y | Y | partial | partial | low | partial |
| `Eval best practices` | low | partial | partial | Y | Y | partial | low | Y |
| `Inspect AI` | partial | Y | partial | partial | partial | Y | partial | partial |
| `Inspect tracing` | low | partial | partial | partial | low | Y | low | partial |
| `Inspect scorers` | low | Y | Y | Y | partial | partial | low | partial |
| `Promptfoo simulated user` | partial | partial | Y | partial | partial | partial | partial | partial |
| `AWS agent-evaluation` | partial | partial | Y | Y | partial | partial | low | partial |
| `DeepEval` | low | Y | Y | Y | partial | partial | low | partial |
| `MCP workflows overview` | Y | low | partial | partial | partial | low | Y | low |
| `MCP evaluator_optimizer` | partial | partial | Y | Y | Y | partial | low | partial |
| `AgentBench` | partial | low | partial | low | low | Y | low | partial |
| `AgentBoard` | partial | low | partial | low | low | Y | low | partial |
| `τ-bench` | partial | partial | Y | partial | partial | Y | partial | partial |
| `AgentDojo` | low | partial | partial | low | partial | partial | low | Y |
| `SWE-bench` | low | partial | Y | partial | low | Y | low | partial |
| `OpenAI agents python` | partial | partial | Y | partial | partial | Y | low | partial |
| `LangGraph` | Y | low | partial | partial | Y | Y | Y | partial |
| `CrewAI` | Y | low | partial | low | partial | partial | Y | low |

핵심 해석:
- workflow mode는 `Anthropic`, `MCP`, `LangGraph`, `CrewAI`가 강하다.
- 자연어/구조화 output 평가와 retry quality는 `OpenAI graders`, `DeepEval`, `Inspect scorers`, `MCP evaluator_optimizer`가 강하다.
- trace/lineage는 `OpenAI trace grading`, `Inspect tracing`, `AgentBoard`, `AgentBench`가 강하다.
- robustness는 `AgentDojo`, `Eval best practices`, `τ-bench`가 보강한다.

## Direct Mapping To Planned Skill Artifacts

### 1. `WORKFLOW_MODES.md`
주요 reference:
- `Anthropic effective agents`
- `MCP workflows overview`
- `CrewAI`
- `LangGraph`

설명:
- sequential / parallel / evaluator-optimizer의 계약과 적용 조건을 분리한다.

### 2. `DECISION_ALGEBRA.md`
주요 reference:
- `Anthropic effective agents`
- `OpenAI eval best practices`
- `MCP evaluator_optimizer`
- `LangGraph`

설명:
- `pass`, `retry`, `reroute`, `loop`, `stop`, `escalate`, `fanout`, `fanin_hold`를 정의한다.

### 3. `NATURAL_LANGUAGE_OUTPUT_POLICY.md`
주요 reference:
- `OpenAI graders`
- `OpenAI trace grading`
- `DeepEval`
- `AgentDojo`

설명:
- 자연어 출력을 claim으로 취급하고, extract->grade->decide->handoff로 정규화하는 규칙을 정의한다.

### 4. `ARTIFACT_SCHEMA.md`
주요 reference:
- `OpenAI agent evals`
- `Inspect tracing`
- `Inspect scorers`
- `OpenAI agents python`

설명:
- `raw_output.md`, `bridge_eval.json`, `retry_spec.json`, `handoff_packet.json`, `event_log.jsonl` 구조를 정의한다.

### 5. `FAILURE_TAXONOMY.md`
주요 reference:
- `Eval best practices`
- `AgentDojo`
- `τ-bench`

설명:
- `recoverable`, `irrecoverable`, `ambiguous`, `external_blocked`, `no_progress`, `unsafe` taxonomy를 정의한다.

### 6. `LOOP_POLICY.md`
주요 reference:
- `Anthropic effective agents`
- `MCP evaluator_optimizer`
- `AWS agent-evaluation`

설명:
- max retries, max iterations, score threshold, no-progress 판정을 정의한다.

### 7. `FANIN_POLICY.md`
주요 reference:
- `Anthropic effective agents`
- `CrewAI`
- `LangGraph`
- `τ-bench`

설명:
- branch conflict, weighted merge, expert-first, safety veto, fanin_hold 조건을 정의한다.

### 8. `bridge_eval_runner.py`
주요 reference:
- `OpenAI agent evals`
- `Inspect AI`
- `OpenAI graders`

설명:
- 하나의 step output을 읽어 `bridge_eval.json`을 생성한다.

### 9. `decision_engine.py`
주요 reference:
- `MCP evaluator_optimizer`
- `Eval best practices`
- `LangGraph`

설명:
- `bridge_eval`을 받아 retry/reroute/loop/pass/stop을 결정한다.

### 10. `fanin_aggregator.py`
주요 reference:
- `Anthropic effective agents`
- `CrewAI`
- `LangGraph`

설명:
- parallel branch 결과를 정규화하고 fan-in 가능 여부를 판단한다.

## Recommended Reading Order

### Stage 1. Skill identity와 workflow mode 고정
1. `Anthropic effective agents`
2. `MCP workflows overview`
3. `Boundary-of-Responsibility-2026-03-15-03-56.md`
4. `skill-workflow-bridge-eval-reference-2026-03-16-01.md`

목표:
- 이 skill의 역할과 workflow 모드를 먼저 고정한다.

### Stage 2. Retry / handoff / natural-language handling 고정
5. `MCP evaluator_optimizer`
6. `OpenAI graders`
7. `OpenAI trace grading`
8. `DeepEval`
9. `AgentDojo`

목표:
- 자연어 출력 정규화, retry_spec, robustness 기준을 고정한다.

### Stage 3. Trace / run lineage / evaluation harness 고정
10. `OpenAI agent evals`
11. `Inspect AI`
12. `Inspect tracing`
13. `Inspect scorers`
14. `OpenAI agents python`
15. `AgentBoard`
16. `AgentBench`

목표:
- workflow_run, step_run, event log, artifact lineage를 고정한다.

### Stage 4. Fan-in / multi-branch / hybrid future 고정
17. `CrewAI`
18. `LangGraph`
19. `τ-bench`
20. `Anthropic multi-agent research system`
21. `SWE-bench`
22. `iAgentBench`

목표:
- fan-in policy, hybrid routing, evidence utility, executable evidence 관점을 추가한다.

## Common Failure Modes This KB Is Trying To Prevent

### 1. completion claim을 곧바로 성공으로 오판
예:
- "완료했습니다"
- "분석 끝났습니다"
- "파일 만들었습니다"

대응 reference:
- `AgentDojo`
- `OpenAI graders`
- `OpenAI trace grading`

### 2. 자연어 출력이 downstream 입력 계약을 만족하지 않는데 그대로 handoff
대응 reference:
- `OpenAI graders`
- `DeepEval`
- `MCP evaluator_optimizer`

### 3. blind retry 반복
대응 reference:
- `Anthropic effective agents`
- `MCP evaluator_optimizer`
- `Eval best practices`

### 4. parallel branch 결과를 정규화 없이 단순 concat
대응 reference:
- `Anthropic effective agents`
- `CrewAI`
- `LangGraph`

### 5. run은 남았지만 왜 retry/reroute/stop 했는지 trace가 없음
대응 reference:
- `OpenAI trace grading`
- `Inspect tracing`
- `AgentBoard`

### 6. downstream skill readiness와 quality 평가가 뒤섞임
대응 reference:
- `OpenAI agent evals`
- `Inspect scorers`
- `DeepEval`

### 7. no-progress loop를 감지하지 못함
대응 reference:
- `MCP evaluator_optimizer`
- `Anthropic effective agents`

### 8. executable evidence가 필요한 task인데 natural-language self-report만 봄
대응 reference:
- `SWE-bench`
- `OpenAI agent evals`

## Suggested Minimal Reference Stack For v01

### Must Read
- `Anthropic effective agents`
- `OpenAI graders`
- `OpenAI trace grading`
- `OpenAI agent evals`
- `MCP workflows overview`
- `MCP evaluator_optimizer`
- `Inspect tracing`
- `DeepEval`
- local `Boundary-of-Responsibility`
- local `skill-workflow-bridge-eval-reference`

### Read If Needed
- `AgentDojo`
- `Promptfoo simulated user`
- `AWS agent-evaluation`
- `CrewAI`
- `LangGraph`

### Later / Expansion
- `AgentBench`
- `AgentBoard`
- `τ-bench`
- `iAgentBench`
- `SWE-bench`
- `Anthropic multi-agent research system`
- `OpenAI agents python`

## Suggested Next Files To Create In references

1. `WORKFLOW_MODES.md`
2. `DECISION_ALGEBRA.md`
3. `NATURAL_LANGUAGE_OUTPUT_POLICY.md`
4. `ARTIFACT_SCHEMA.md`
5. `FAILURE_TAXONOMY.md`
6. `LOOP_POLICY.md`
7. `FANIN_POLICY.md`
8. `RUN_TRACE_SCHEMA.md`

## Suggested Next Scripts To Create In scripts

1. `bridge_eval_runner.py`
2. `output_type_classifier.py`
3. `nl_output_extractor.py`
4. `decision_engine.py`
5. `retry_spec_builder.py`
6. `handoff_packet_builder.py`
7. `fanin_aggregator.py`
8. `loop_controller.py`
9. `event_log_writer.py`

## Suggested Minimal Acceptance Plan

### Step 1. output type classification
- `script_result`
- `structured_json`
- `natural_language`
- `mixed`

### Step 2. natural-language normalization
- raw output 저장
- extraction JSON 생성
- bridge_eval 생성
- next_step_ready 판단

### Step 3. decision engine
- pass
- retry
- reroute
- stop
- loop

### Step 4. retry quality
- blind retry 금지
- retry_spec 기반 repair retry
- no-progress signal

### Step 5. fan-in
- branch normalization
- branch conflict detection
- fanin_hold 조건 판정

### Step 6. traceability
- workflow_run_id
- step_run_id
- artifacts lineage
- event log

최소 acceptance 기준:
- 자연어 출력이 raw 그대로 downstream으로 가지 않는다.
- retry는 repair instructions 없이 발생하지 않는다.
- decision은 모두 artifact와 함께 trace된다.
- downstream skill은 handoff_packet을 canonical input으로 사용할 수 있다.
- parallel 결과는 fan-in 전에 branch별 정규화가 된다.
