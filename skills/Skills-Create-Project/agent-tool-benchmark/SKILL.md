---
name: agent-tool-benchmark
description: >-
  measurement-evaluation-orchestrator family의 metric-formula specialist. Use
  this skill when benchmark metric formulas and validation logic are needed for
  agent tool-use quality, orchestration evaluation, or Langfuse custom scores.
  multi-concern measurement orchestration은
  measurement-evaluation-orchestrator를 사용하라.
---

# Agent Tool-Use Benchmark

agent tool 사용 품질의 정량 측정 수식 레지스트리. 8개 벤치마크, 9개 메트릭.

## When to use

- agent tool calling 정확도를 정량 측정할 때
- 오케스트레이션 파이프라인의 step별 실패 진단이 필요할 때
- canonical graph 구조 유사도를 F1/GED 계열로 평가할 때
- Langfuse에 custom score를 등록할 메트릭 정의가 필요할 때

상세 메트릭 표와 사용법은 [entrypoint 상세 안내](references/agent-tool-benchmark-entrypoint-details-at2026-03-24.md)를 따른다.

## Scripts

- `scripts/metric_formulas.py` — `report` / `validate` / `export` (`--help` 지원)
- `scripts/test_metric_formulas.py` — unittest 분리 테스트 (36 tests)

## Knowledge Bases

- [knowledge_bases/agent-tool-benchmark-kb-at2026-03-24.md](knowledge_bases/agent-tool-benchmark-kb-at2026-03-24.md)

## References

- [references/agent-tool-benchmark-paper-search-at2026-03-24.md](references/agent-tool-benchmark-paper-search-at2026-03-24.md)
- [references/agent-tool-benchmark-entrypoint-details-at2026-03-24.md](references/agent-tool-benchmark-entrypoint-details-at2026-03-24.md)
- [references/troubleshooting.md](references/troubleshooting.md)
