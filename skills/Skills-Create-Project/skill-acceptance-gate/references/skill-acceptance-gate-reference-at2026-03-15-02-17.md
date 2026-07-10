기준은 “Skill이 작동하는가”를 trigger, boundary, schema, runtime trace, regression, failure 관점에서 판단할 수 있느
  냐이다.

  핵심 추천 세트

  1. 평가 프레임워크

  - OpenAI Evals (https://github.com/openai/evals)
  - Inspect AI (https://github.com/UKGovernmentBEIS/inspect_ai)
  - Promptfoo (https://github.com/promptfoo/promptfoo)
  - DeepEval (https://github.com/confident-ai/deepeval)
  - AWS Agent Evaluation (https://github.com/awslabs/agent-evaluation)

  2. 에이전트 벤치마크 / 논문

  - AgentBench (https://arxiv.org/abs/2308.03688)
  - AgentBoard (https://arxiv.org/abs/2401.13178)
  - τ-bench (https://arxiv.org/abs/2406.12045)
  - AgentDojo (https://arxiv.org/abs/2406.13352)
  - SWE-bench (https://arxiv.org/abs/2310.06770)
  - iAgentBench (https://arxiv.org/abs/2603.04656)

  3. 구현/운영 문서

  - OpenAI Agent evals (https://platform.openai.com/docs/guides/agent-evals)
  - OpenAI Trace grading (https://platform.openai.com/docs/guides/trace-grading)
  - OpenAI Graders (https://platform.openai.com/docs/guides/graders/)
  - OpenAI Evaluation best practices (https://platform.openai.com/docs/guides/evaluation-best-practices)
  - Inspect Scorers (https://inspect.aisi.org.uk/scorers.html)
  - Inspect Tracing (https://inspect.aisi.org.uk/tracing.html)
  - Inspect Log Viewer (https://inspect.aisi.org.uk/log-viewer.html)
  - Inspect Tool Use Tutorial (https://inspect.aisi.org.uk/tutorial.html)
  - Promptfoo Simulated User (https://www.promptfoo.dev/docs/providers/simulated-user/)

  ———

  ## 1. GitHub Reference 수집 목록

  ### A. 평가 프레임워크 계열

  - openai/evals (https://github.com/openai/evals)
      - 이유: dataset + grader + eval run 구조의 가장 기본 reference
      - skill-acceptance-gate에 필요한 것:
          - eval dataset 구조
          - grader 구성
          - regression test 개념
  - UKGovernmentBEIS/inspect_ai (https://github.com/UKGovernmentBEIS/inspect_ai)
      - 이유: tool use, multi-turn, scorer, trace, log가 가장 잘 정리된 실전형 framework
      - 필요한 것:
          - scorer abstraction
          - runtime trace / log 구조
          - no-score -> later score 개발 루프
  - promptfoo/promptfoo (https://github.com/promptfoo/promptfoo)
      - 이유: declarative config + CI/CD + regression gate가 강함
      - 필요한 것:
          - acceptance criteria를 config로 표현하는 방식
          - assert 기반 판정
          - security / red-team case
  - confident-ai/deepeval (https://github.com/confident-ai/deepeval)
      - 이유: component-level + agentic metrics + tracing이 있음
      - 필요한 것:
          - custom metric 설계
          - tool correctness / task completion 같은 agent metric 참고
  - awslabs/agent-evaluation (https://github.com/awslabs/agent-evaluation)
      - 이유: evaluator agent가 target agent와 대화하며 multi-turn 평가하는 구조
      - 필요한 것:
          - hooks
          - concurrent evaluation
          - CI integration

  ### B. 벤치마크 구현 계열

  - hkust-nlp/AgentBoard (https://github.com/hkust-nlp/AgentBoard)
      - 이유: final success rate 말고 fine-grained analytical evaluation을 강조
      - 필요한 것:
          - progress-rate류 세분화 평가 철학
          - panel/visualization 아이디어
  - microsoft/ToolTalk (https://github.com/microsoft/ToolTalk)
      - 이유: conversational tool-use benchmark
      - 필요한 것:
          - tool sequence correctness
          - multi-turn tool call ground truth
  - sierra-research/tau-bench (https://github.com/sierra-research/tau-bench)
      - 이유: user-agent-tool 상호작용과 policy adherence를 평가
      - 필요한 것:
          - simulated user
          - domain rules adherence
          - tool-use acceptance cases
  - sierra-research/tau2-bench (https://github.com/sierra-research/tau2-bench)
      - 이유: 최신 확장판
      - 필요한 것:
          - dual-control environment
          - train/test split 운영 방식
  - ethz-spylab/agentdojo (https://github.com/ethz-spylab/agentdojo)
      - 이유: 공격/방어/robustness 평가
      - 필요한 것:
          - prompt injection failure case
          - adversarial acceptance gate
  - SWE-bench/SWE-bench (https://github.com/SWE-bench/SWE-bench)
      - 이유: coding agent acceptance gate의 최종 검증 reference
      - 필요한 것:
          - issue -> patch -> test pass harness
          - reproducible evaluation containerization

  ———

  ## 2. 논문 Reference 수집 목록

  - AgentBench: Evaluating LLMs as Agents (https://arxiv.org/abs/2308.03688)
      - 포인트: agent 평가를 multi-environment benchmark로 본다
  - AgentBoard: An Analytical Evaluation Board of Multi-turn LLM Agents (https://arxiv.org/abs/2401.13178)
      - 포인트: final accuracy만 보지 않고 sub-skill / trajectory / progress를 본다
  - τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains (https://arxiv.org/abs/2406.12045)
      - 포인트: simulated user + domain policy + tool use를 함께 본다
  - AgentDojo: A Dynamic Environment to Evaluate Attacks and Defenses for LLM Agents
    (https://arxiv.org/abs/2406.13352)
      - 포인트: prompt injection/robustness를 acceptance gate에 넣어야 함을 보여준다
  - SWE-bench: Can Language Models Resolve Real-World GitHub Issues? (https://arxiv.org/abs/2310.06770)
      - 포인트: coding agent acceptance는 결국 executable verification이 필요하다는 기준
  - iAgentBench: Benchmarking Sensemaking Capabilities of Information-Seeking Agents on High-Traffic Topics
    (https://arxiv.org/abs/2603.04656)
      - 포인트: dynamic/real-world information-seeking agent 평가에 유용

  ———

  ## 3. 구현 Reference 수집 목록

  ### OpenAI 쪽

  - Agent evals (https://platform.openai.com/docs/guides/agent-evals)
      - workflow-level 평가 기준
  - Trace grading (https://platform.openai.com/docs/guides/trace-grading)
      - trace 기반 skill acceptance 평가에 직접적
  - Graders (https://platform.openai.com/docs/guides/graders/)
      - string / similarity / score-model / python grader 구조 참고
  - Evaluation best practices (https://platform.openai.com/docs/guides/evaluation-best-practices)
      - eval 설계 원칙 reference

  ### Inspect 쪽

  - Inspect Scorers (https://inspect.aisi.org.uk/scorers.html)
      - scorer abstraction 설계 reference
  - Inspect Tracing (https://inspect.aisi.org.uk/tracing.html)
      - runtime failure / timeout / action trace 구조 reference
  - Inspect Log Viewer (https://inspect.aisi.org.uk/log-viewer.html)
      - in-progress evaluation 관찰 방식 reference
  - Inspect Tutorial - Tool Use (https://inspect.aisi.org.uk/tutorial.html)
      - tool-use eval starter reference

  ### Promptfoo 쪽

  - Simulated User (https://www.promptfoo.dev/docs/providers/simulated-user/)
      - tau-bench 스타일 multi-turn simulated user testing에 바로 대응

  ———

  ## 4. skill-acceptance-gate 설계에 어떻게 매핑할지

  ### Trigger / Boundary

  - 주 reference:
      - OpenAI Evaluation best practices
      - Inspect Scorers
      - Promptfoo config/assert
  - 목적:
      - 이 Skill이 언제 호출되어야 하는지
      - 어떤 필드를 소유/금지하는지
      - 어떤 결과를 pass/fail로 볼지

  ### Runtime / Trace

  - 주 reference:
      - OpenAI Trace grading
      - Inspect Tracing
      - Inspect Log Viewer
  - 목적:
      - Skill 실행 trace를 보고 어디서 실패했는지 분리
      - black-box 평가가 아니라 step-level 판정

  ### Multi-turn / Tool-use / Simulated User

  - 주 reference:
      - τ-bench
      - ToolTalk
      - AWS Agent Evaluation
      - Promptfoo Simulated User
  - 목적:
      - “Skill이 실제 agent loop 안에서 작동하는가” 검증

  ### Adversarial / Failure Cases

  - 주 reference:
      - AgentDojo
      - Promptfoo red-team
  - 목적:
      - boundary break, injection, misuse 대응 여부 검증

  ### Coding-agent Acceptance

  - 주 reference:
      - SWE-bench
  - 목적:
      - 최종적으로는 file diff + tests + issue resolution까지 가야 함을 기준화

  ———

  ## 5. 우선 수집 순서

  ### 반드시 먼저 읽을 것

  1. inspect_ai
  2. OpenAI trace grading / graders / eval best practices
  3. promptfoo
  4. τ-bench
  5. AgentBoard

  ### 두 번째 묶음

  6. deepeval
  7. agent-evaluation
  8. ToolTalk
  9. AgentDojo

  ### 세 번째 묶음

  10. SWE-bench
  11. iAgentBench

  ———