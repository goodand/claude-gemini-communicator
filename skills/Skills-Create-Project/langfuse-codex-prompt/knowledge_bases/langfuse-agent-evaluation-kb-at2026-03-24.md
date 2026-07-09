---
name: langfuse-agent-evaluation-kb
kb_profile: canonical_design_kb
role: langfuse agent tool-use evaluation strategy
ver: 1
created_at: 2026-03-24
updated_at: 2026-03-24
reference_acquisition_mode: external_research
source_scope: langfuse-codex-prompt + agent-tool-benchmark
purpose: Langfuse를 활용한 agent tool-use 품질 측정의 canonical design을 정리한다
---

# Langfuse Agent Evaluation KB

## Canonical design takeaways

1. `Trace`는 하나의 agent task 실행 단위다. tool call은 `Span`으로, LLM reasoning은 `Generation`으로 기록한다.
2. `Score`는 Trace/Span/Session/DatasetRun에 부착 가능하며, `NUMERIC`/`BOOLEAN`/`CATEGORICAL` 3가지 타입을 지원한다.
3. `Dataset`은 test case 모음이며, `Dataset Run`은 하나의 evaluation pass다. A/B 비교는 동일 Dataset에 서로 다른 Run을 만들어 수행한다.
4. tool-use 평가는 **selection → argument → efficiency → completion** 4단계 score taxonomy를 따른다.
5. LLM-as-judge는 Langfuse의 built-in evaluator template으로 설정하거나, 외부 pipeline에서 score를 SDK로 push한다.
6. 벤치마크 메트릭(AST Accuracy, F1, Pass Rate 등)은 외부에서 계산 후 `create_score()`로 Langfuse에 기록한다.
7. idempotency key(`score_id`)로 중복 score를 방지하거나 갱신한다.

## Score Taxonomy for Tool Use

### Tier 1: Per-call (Span 단위)

| Score Name | Type | 설명 |
|---|---|---|
| `tool_selection_correct` | BOOLEAN | 올바른 tool을 선택했는가 |
| `tool_argument_correct` | BOOLEAN | parameter가 정확한가 |
| `tool_call_latency_ms` | NUMERIC | 개별 tool call 지연시간 |

### Tier 2: Per-task (Trace 단위)

| Score Name | Type | 설명 |
|---|---|---|
| `tool_selection_accuracy` | NUMERIC | 올바른 tool 선택 비율 (0.0~1.0) |
| `tool_argument_accuracy` | NUMERIC | 올바른 argument 비율 |
| `tool_call_efficiency` | NUMERIC | 유효 호출 / 전체 호출 |
| `task_completion` | BOOLEAN | 최종 목표 달성 여부 |
| `hallucination_in_tool_args` | BOOLEAN | 존재하지 않는 tool/arg 호출 여부 |

### Tier 3: Per-experiment (Dataset Run 단위)

| Score Name | Type | 설명 |
|---|---|---|
| `ast_accuracy` | NUMERIC | BFCL 방식 AST 매칭 정확도 |
| `pass_rate` | NUMERIC | ToolEval 방식 pass/unsure/fail 가중 평균 |
| `f1_tool_selection` | NUMERIC | T-Eval 방식 tool selection F1 |
| `resolve_rate` | NUMERIC | SWE-bench 방식 F2P ∧ P2P |
| `sr_at_k` | NUMERIC | MINT 방식 k턴 이내 성공률 |

## Evaluation Pipeline Pattern

### 1. Dataset 생성

```python
langfuse = Langfuse()
langfuse.create_dataset(
    name="agent-tool-use-benchmark",
    metadata={"version": "v1", "type": "tool_use"}
)
```

### 2. Test case 등록

```python
langfuse.create_dataset_item(
    dataset_name="agent-tool-use-benchmark",
    input={"task": "Find all Python files importing torch"},
    expected_output={
        "ideal_tools": ["Grep"],
        "ideal_args": {"pattern": "import torch|from torch"},
    }
)
```

### 3. Experiment 실행 + Score 기록

```python
dataset = langfuse.get_dataset("agent-tool-use-benchmark")
for item in dataset.items:
    trace = langfuse.trace(name="eval-run")
    result = run_agent(item.input["task"], trace=trace)

    # link trace to dataset item
    item.link(trace=trace, run_name="v2-experiment")

    # compute & record metric
    accuracy = compute_ast_accuracy(result.tool_calls, item.expected_output)
    trace.score(name="ast_accuracy", value=accuracy, data_type="NUMERIC")

langfuse.flush()
```

### 4. Score 직접 push (외부 pipeline)

```python
langfuse.create_score(
    trace_id="tr-xxx",
    name="f1_tool_selection",
    value=0.85,
    data_type="NUMERIC",
    score_id="unique-idempotency-key",
    comment="pred={Grep,Read}, gt={Grep,Read,Glob}"
)
```

## Integration with agent-tool-benchmark skill

`agent-tool-benchmark/scripts/metric_formulas.py`의 Python 함수들을 직접 import하여 Langfuse score value를 계산한다.

```python
from metric_formulas import ast_accuracy, f1_score, pass_rate

# 계산 후 Langfuse에 push
value = ast_accuracy(predictions)
langfuse.create_score(trace_id=tid, name="ast_accuracy", value=value)
```

## Context-based Scoring (span 내부)

```python
with langfuse.start_as_current_observation(as_type="span", name="tool:Grep") as span:
    result = execute_grep(pattern, path)
    span.update(output=result)
    span.score(name="tool_selection_correct", value=1, data_type="BOOLEAN")
    span.score_trace(name="task_progress", value=0.5, data_type="NUMERIC")
```

## Not part of this KB

- Langfuse 프롬프트 템플릿 관리 (→ SKILL.md 본체)
- Codex CLI 실행 연동 (→ SKILL.md workflow)
- 개별 벤치마크 수식의 수도코드/LaTeX 표현 (→ agent-tool-benchmark skill)
- Neo4j/Graphviz 등 graph export (→ codebase-analysis skill)

## Why this KB exists

agent의 tool 사용 품질을 정량 측정하려면 trace → score → dataset run의 3단계가 필요하다. 이 KB는 Langfuse SDK의 scoring API와 벤치마크 메트릭의 연결점을 canonical design으로 고정하여, 매번 API 문서를 다시 찾지 않도록 한다.
