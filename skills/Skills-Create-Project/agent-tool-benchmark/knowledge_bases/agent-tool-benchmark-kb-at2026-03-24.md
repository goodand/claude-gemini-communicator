---
name: agent-tool-benchmark-kb
kb_profile: canonical_design_kb
role: agent tool-use benchmark metric design
ver: 1
created_at: 2026-03-24
updated_at: 2026-03-24
reference_acquisition_mode: external_research
source_scope: agent-tool-benchmark skill
purpose: agent tool-use 측정 메트릭의 설계 결정과 경계를 canonical design으로 고정한다
---

# Agent Tool-Use Benchmark KB

## Canonical design takeaways

1. metric registry는 **8개 벤치마크에서 추출한 9개 메트릭**으로 구성한다. AgentBench는 환경별 normalized score라 범용 수식화에 부적합하여 조사만 수행, registry에서 제외.
2. 각 메트릭은 **수도코드 / LaTeX / Python** 3중 표현으로 관리하며, Python 구현을 ground truth로 교차 검증한다.
3. 교차 검증은 **고정 테스트 벡터** (경계값 포함)로 수행하며, 수도코드와 LaTeX를 손으로 추적한 expected 값과 Python 결과를 비교한다.
4. GED Score는 **symmetric difference 근사**다. 정확한 Graph Edit Distance는 NP-hard이므로 v0에서는 간소화한다.
5. ToolSandbox의 Action Score와 3-Milestone AND는 별개 메트릭이다. Action은 tool call 매칭 비율, 3-Milestone은 Action × State × Response의 AND 논리.
6. Langfuse 연동은 `langfuse-codex-prompt` skill의 evaluation KB가 담당한다. 이 skill은 **메트릭 계산까지만** 소유한다.

## Metric family

| Family | 메트릭 | 출처 | 핵심 수식 패턴 |
|--------|--------|------|---------------|
| Accuracy | AST Accuracy | BFCL | `(1/N) Σ 𝟙[match]` |
| Accuracy | API-Bank L1 | API-Bank | `(1/N) Σ 𝟙[name ∧ args]` |
| Judge-based | Pass Rate | ToolEval | `(1/N) Σ score_map[judge]` |
| Set-based | F1 Score | T-Eval/TaskBench | `2PR/(P+R)` |
| Graph-based | GED Score | TaskBench | `1 - GED/max_edges` |
| Stateful | Action Score | ToolSandbox | `|matched|/max(|pred|,|gt|)` |
| Stateful | 3-Milestone AND | ToolSandbox | `A × S × R` |
| Regression | Resolve Rate | SWE-bench | `𝟙[F2P ∧ P2P]` |
| Efficiency | SR@k | MINT | `(1/N) Σ 𝟙[correct ∧ t≤k]` |

## Source-of-truth rule

- **수식의 source of truth**: `scripts/metric_formulas.py` 안의 `METRIC_REGISTRY` + Python 함수
- **검증의 source of truth**: `scripts/test_metric_formulas.py`
- **논문 조사의 source of truth**: `references/agent-tool-benchmark-paper-search-at2026-03-24.md`
- 이 KB는 설계 결정을 기록하며, 구현 코드를 복사하지 않는다

## Simplification boundary

| 항목 | 현재 상태 | 정확 구현이 필요해지는 조건 |
|------|----------|--------------------------|
| GED → symmetric difference | 간소화 | 실제 graph editing operation이 필요한 경우 |
| AgentBench normalized score | 미구현 | 8개 환경 중 하나를 실제로 사용하는 경우 |
| ToolEval unsure = 0.5 | 고정 가중치 | 실제 judge calibration을 수행하는 경우 |
| AST match | boolean input | 실제 AST parser를 통합하는 경우 |

## Langfuse / custom-score boundary

- 이 skill: 메트릭 값을 **계산**한다 (`ast_accuracy()` → `float`)
- `langfuse-codex-prompt` skill: 계산된 값을 Langfuse에 **push**한다 (`create_score()`)
- 이 경계를 넘지 않는다. metric_formulas.py에 langfuse import를 추가하지 않는다.

## Not part of this skill

- Langfuse SDK 연동 (→ langfuse-codex-prompt)
- 개별 벤치마크의 full dataset 재현 (→ 각 벤치마크 repo)
- codebase graph 구조 평가 (→ codebase-analysis)
- agent orchestration 성능 측정 (→ 향후 orchestration skill)
