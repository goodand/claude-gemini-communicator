---
name: measurement-evaluation-orchestrator
description: >-
  Use this skill when metric design, baseline comparison, benchmark formula
  selection, and score interpretation must be coordinated together across
  experiments or agent evaluations. before/after diff는 baseline-diff-lab,
  metric formula registry와 validation logic은 agent-tool-benchmark를
  사용하라.
---

# Measurement Evaluation Orchestrator

측정 band의 workflow owner.

## When to use

- baseline diff와 benchmark formula를 같이 설계하거나 해석해야 할 때
- 어떤 측정 specialist를 먼저 써야 할지 불확실할 때
- 외부 tool/API 결과를 metric과 verdict로 함께 연결해야 할 때

## Do not use

- before/after baseline diff만 필요할 때
- benchmark metric formula와 validation logic만 필요할 때

## Family Roles

- owner:
  - `measurement-evaluation-orchestrator`
- direct-call specialists:
  - `baseline-diff-lab`
  - `agent-tool-benchmark`

## Workflow

1. baseline measurement, formula selection, score interpretation concern을 분리한다.
2. direct-call specialist 하나로 충분한지 먼저 판단한다.
3. multi-concern measurement면 owner가 metric order와 comparison surface를 정한다.
4. 결과를 downstream verification, optimization, product decision으로 넘긴다.

## References

- owner band taxonomy는 [../skill-creation-process/references/owner-task-bands-at2026-04-02.md](../skill-creation-process/references/owner-task-bands-at2026-04-02.md)
- troubleshooting note는 [references/troubleshooting.md](references/troubleshooting.md)
