# Agent Tool-Use Benchmark — 논문 조사 보고서

- recorded_at: `2026-03-24`
- scope: `agent-tool-benchmark`
- reference_acquisition_mode: `external_research`

## 사용자 의도 파악

코드베이스 분석 목적의 오케스트레이션 Skills 개발을 위해,
agent의 tool 사용 품질을 수치로 측정하는 방법론을 조사한다.

## Shortlist

### 1. BFCL (Berkeley Function Calling Leaderboard)
- URL: https://gorilla.cs.berkeley.edu/leaderboard.html
- GitHub: https://github.com/ShishirPatil/gorilla
- Paper: "Gorilla: Large Language Model Connected with Massive APIs" (Patil et al., 2023)
- 선택 이유:
  - AST 기반 function call 정확도 측정의 de facto standard
  - simple/parallel/multiple/exec 4가지 카테고리로 세분화
  - 코드베이스 분석 agent의 tool selection 정확도 측정에 직접 적용 가능

### 2. ToolEval / ToolBench
- URL: https://openbmb.github.io/ToolBench/
- GitHub: https://github.com/OpenBMB/ToolBench
- Paper: "ToolLLM: Facilitating Large Language Models to Master 16000+ Real-World APIs" (Qin et al., ICLR 2024 Spotlight)
- 선택 이유:
  - Pass Rate + Win Rate의 LLM-as-judge 평가 패턴
  - SoPR/SoWR로 solvable subset 분리 → 공정 비교
  - 코드베이스 분석 결과의 품질 판정에 judge 패턴 재사용 가능

### 3. T-Eval
- URL: https://open-compass.github.io/T-Eval/
- GitHub: https://github.com/open-compass/T-Eval
- Paper: "T-Eval: Evaluating Tool Utilization Capability Step by Step" (Chen et al., ACL 2024)
- 선택 이유:
  - 6단계 sub-capability 분리 (instruct, plan, tool select, argument, content, reasoning)
  - step-by-step 평가 → 오케스트레이션의 어느 단계에서 실패하는지 진단 가능

### 4. TaskBench
- GitHub: https://github.com/microsoft/JARVIS
- Paper: "TaskBench: Benchmarking Large Language Models for Task Automation" (Shen et al., NeurIPS 2023)
- 선택 이유:
  - Node-F1, Edge-F1, GED 기반 그래프 구조 평가
  - 코드베이스 분석 canonical graph의 구조적 정확도 측정에 직접 대응

### 5. ToolSandbox (Apple)
- GitHub: https://github.com/apple/ToolSandbox
- Paper: "ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark" (Lu et al., 2024)
- 선택 이유:
  - stateful 환경에서 3-milestone AND 평가 (Action × State × Response)
  - 코드베이스 분석은 파일 시스템 상태에 의존 → stateful 평가 패턴 필요

### 6. SWE-bench
- GitHub: https://github.com/princeton-nlp/SWE-bench
- Paper: "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" (Jimenez et al., ICLR 2024)
- 선택 이유:
  - fail-to-pass ∧ pass-to-pass 이중 검증 → regression 방지
  - 코드베이스 분석 구현의 테스트 기반 검증에 동일 패턴 적용 가능

### 7. MINT
- GitHub: https://github.com/xingyaoww/mint-bench
- Paper: "MINT: Evaluating LLMs in Multi-Turn Interaction with Tools and Language Feedback" (Wang et al., ICLR 2024)
- 선택 이유:
  - SR@k (k턴 이내 성공률) → multi-turn 오케스트레이션 효율성 측정

### 8. API-Bank
- GitHub: https://github.com/AlibabaResearchDMLNLP/API-Bank
- Paper: "API-Bank: A Comprehensive Benchmark for Tool-Augmented LLMs" (Li et al., ACL 2023)
- 선택 이유:
  - 3-level 난이도 (call → retrieve+call → plan+retrieve+call)
  - 오케스트레이션 복잡도 단계별 평가에 참조

### 9. AgentBench
- GitHub: https://github.com/THUDM/AgentBench
- Paper: "AgentBench: Evaluating LLMs as Agents" (Liu et al., ICLR 2024)
- 선택 이유:
  - 8개 환경별 normalized overall → 다양한 task 유형의 통합 점수

## Design Takeaways

1. **AST 매칭은 tool call 정확도의 기본 단위**다. BFCL이 증명함.
2. **LLM-as-judge**는 open-ended 품질 판정에 유효하다 (ToolEval 87% human agreement).
3. **Step-by-step 분해**로 실패 지점을 진단해야 한다 (T-Eval 6단계).
4. **그래프 구조 비교**는 Node-F1 + Edge-F1 + GED로 정량화 가능하다 (TaskBench).
5. **Stateful 평가**는 AND 논리 (모든 milestone 통과)가 현실적이다 (ToolSandbox).
6. **Regression 방지**는 F2P ∧ P2P 이중 게이트로 보장한다 (SWE-bench).
7. **Multi-turn 효율성**은 SR@k로 턴 수 기준 측정한다 (MINT).

## Reject/Hold

- **Gorilla API 호출 생성** — BFCL로 흡수됨, 별도 분석 불필요
- **StableToolBench** — ToolBench의 안정성 개선이지 새 메트릭 아님, hold
- **GTA (General Tool Agents)** — 2024 후반 출시, 아직 채택률 낮음, hold
