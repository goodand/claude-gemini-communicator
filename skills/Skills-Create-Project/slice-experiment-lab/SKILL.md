---
name: slice-experiment-lab
description: >-
  workspace-artifact-production-process family의 contract-slice closure
  specialist. Use this skill when a contract-oriented implementation slice
  must be closed with smoke evidence, quick_validate status, contract/valid/invalid
  artifacts, and a reusable readiness evaluation. broader artifact production
  order는 workspace-artifact-production-process를 사용하라.
---

# Slice Experiment Lab

contract slice 실험을 `smoke -> evidence -> readiness evaluation`까지 반복 가능한 형식으로 묶는 skill.

## When to use

- contract/validator 조각을 하나씩 구현하며 `references/`에 실험 증거를 남기고 싶을 때
- `contract / valid / invalid` artifact와 `quick_validate` 결과를 함께 판단해야 할 때
- 현재 조각이 `ready`인지 `hold`인지 기계적으로 점검하고 싶을 때
- 공용 process와 별도로 skill 내부 실험 루프를 재사용 가능한 형식으로 만들고 싶을 때

## Workflow

1. source of truth는 [knowledge_bases/slice-experiment-lab-knowledge_base-at2026-03-19-00-45.md](knowledge_bases/slice-experiment-lab-knowledge_base-at2026-03-19-00-45.md) 하나로 고정한다.
2. `Canonical Design Takeaways`를 읽고 이 skill이 실험 evaluator이지 smoke runner가 아니라는 경계를 먼저 고정한다.
3. [checklist-forconsistency-evaluation/consistency-checklist-at2026-03-19-00-45.md](checklist-forconsistency-evaluation/consistency-checklist-at2026-03-19-00-45.md) 로 triad 입력과 readiness 판정 규칙을 확인한다.
4. `scripts/slice_experiment_lab.py --help`로 triad 이름 제안, quick_validate capture, smoke capture, strict warning gate, experiment bundle 평가를 수행한다.

## Scripts

- [scripts/slice_experiment_lab.py](scripts/slice_experiment_lab.py) — triad naming helper + quick_validate/smoke capture + strict warning gate + readiness evaluation
- [scripts/test_slice_experiment_lab.py](scripts/test_slice_experiment_lab.py) — 첫 실험 slice TDD

## References

- [references/vertical-slice-experiment-bundle-at2026-03-19-00-45.md](references/vertical-slice-experiment-bundle-at2026-03-19-00-45.md) — 현재 구현한 실험 slice
- [references/vertical-slice-input-adapters-at2026-03-19-00-57.md](references/vertical-slice-input-adapters-at2026-03-19-00-57.md) — helper 3개를 붙인 입력 정규화 slice
- [references/vertical-slice-strict-warning-policy-gate-at2026-03-19-13-21.md](references/vertical-slice-strict-warning-policy-gate-at2026-03-19-13-21.md) — quick_validate warnings를 strict gate로 판정하는 slice
- [references/troubleshooting.md](references/troubleshooting.md) — 반복 실수와 artifact naming 주의사항

## Notes

- 이 skill은 smoke나 quick_validate를 직접 실행하는 tool runner이기도 하지만, 핵심은 그 결과를 `ready / hold`로 읽는 실험 evaluator에 있다.
- retained helper는 triad naming, quick_validate capture, smoke command capture다.
- `strict_warning_policy_gate`는 `quick_validate_capture` artifact의 warnings/errors를 strict 정책으로 한 번 더 해석한다.
- `contract / valid / invalid` triad와 `quick_validate_status`가 같이 있어야 readiness 판정을 강하게 할 수 있다.
