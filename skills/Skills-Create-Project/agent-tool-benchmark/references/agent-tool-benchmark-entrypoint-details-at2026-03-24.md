# Agent Tool-Use Benchmark — Entrypoint Details

- recorded_at: `2026-03-24`

## 메트릭 목록 (8개 벤치마크, 9개 메트릭)

| # | 메트릭 | 출처 | 용도 |
|---|--------|------|------|
| 1 | AST Accuracy | BFCL | tool call 구조 정확도 |
| 2 | Pass Rate | ToolEval | LLM-as-judge 성공률 |
| 3 | F1 Score (Set) | T-Eval/TaskBench | tool selection 정밀도 |
| 4 | 3-Milestone AND | ToolSandbox | stateful 종합 판정 |
| 5 | Resolve Rate | SWE-bench | regression 방지 이중 게이트 |
| 6 | GED Score | TaskBench | 그래프 구조 유사도 |
| 7 | SR@k | MINT | multi-turn 효율성 |
| 8 | Action Score | ToolSandbox | tool call 매칭 비율 |
| 9 | API-Bank L1 | API-Bank | API name+args exact match |

AgentBench (THU, ICLR 2024)는 조사만 수행, metric registry에서 제외 (8개 환경별 normalized score, 범용 수식화 부적합).

## CLI 사용법

```bash
# 전체 보고서 + 교차 검증 (기본값)
python3 scripts/metric_formulas.py

# 교차 검증만
python3 scripts/metric_formulas.py validate

# JSON 내보내기
python3 scripts/metric_formulas.py export metrics.json

# 도움말
python3 scripts/metric_formulas.py --help

# 분리 테스트
python3 scripts/test_metric_formulas.py
```

## Notes

- 각 메트릭은 수도코드/LaTeX/Python 3가지로 표현되며, Python 구현을 ground truth로 교차 검증한다
- GED Score는 symmetric difference로 근사한 간소화 구현이다 (→ KB simplification boundary 참조)
- 메트릭 **계산**만 이 skill이 소유하며, Langfuse **push**는 `langfuse-codex-prompt` skill이 담당한다
