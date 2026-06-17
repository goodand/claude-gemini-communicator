# Packet Measurement Fields

- recorded_at: `2026-03-25`

agent-task-packet 실행 결과를 벤치마크 메트릭으로 평가할 때 사용하는 필드와 함수 정의.

오케스트레이션(packet_builder.py)과 분리되어 `agent-task-packet/evals/`에 구현되어 있다.

## 측정용 필드

| 필드 | 위치 | 대응 메트릭 | 설명 |
|------|------|-------------|------|
| `required_checks[].category` | eval 전용 | Resolve Rate (SWE-bench) | `f2p`, `p2p`, `new`, `smoke`, `regression` |
| `required_checks[].done_index` | packet core | Response Milestone (ToolSandbox) | done_definition[i]와의 연결 |
| `timeout_minutes` | packet core | SR@k (MINT) | 시간 기반 turn budget |
| `stop_conditions` | packet core | SR@k (MINT) | 범위 기반 중단 기준 |

> `done_index`, `timeout_minutes`, `stop_conditions`는 오케스트레이션 필드이면서 동시에 측정의 입력이 된다.
> `category`는 측정 전용이므로 오케스트레이션 템플릿에는 포함하지 않는다.

## 측정 함수 (agent-task-packet/evals/packet_eval_metrics.py)

| 함수 | 대응 메트릭 | 반환 |
|------|-------------|------|
| `response_coverage(data)` | Response Milestone | 0.0~1.0 (done_index 커버리지) |
| `turn_budget_score(data)` | SR@k | 0.0~1.0 (timeout +0.5, stop_conditions +0.5) |
| `safety_audit(data)` | SR@k | warnings[] (null timeout, 빈 stop_conditions) |
| `resolve_readiness(data)` | Resolve Rate | 0.0~1.0 (category 채택 비율) |

## category 분류

| category | 의미 |
|----------|------|
| `f2p` | Fail-to-Pass — 이번 태스크에서 새로 통과시키는 테스트 |
| `p2p` | Pass-to-Pass — 기존에 통과하던 테스트 (회귀 방지) |
| `new` | 새로 작성한 테스트 |
| `smoke` | 기본 동작 확인 |
| `regression` | 회귀 테스트 |

## 측정용 템플릿

`agent-task-packet/evals/packet_eval_template.json` — category + done_index가 포함된 평가 전용 packet.

## 관련 파일

- `agent-tool-benchmark/scripts/metric_formulas.py` — 범용 메트릭 수식 (9개)
- `agent-task-packet/evals/packet_eval_metrics.py` — packet 특화 측정 함수
- `agent-task-packet/evals/packet_eval_template.json` — 측정용 템플릿
