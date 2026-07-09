---
name: slice-experiment-lab
description: >-
  Use this skill when a contract-oriented implementation slice must be closed
  with smoke evidence, quick_validate status, contract/valid/invalid artifacts,
  and a next-slice decision for follow-up work.
---

# Slice Experiment Lab

contract slice 실험을 `smoke -> evidence -> next-slice gate`까지 반복 가능한 형식으로 묶는 skill.

## When to use

- contract/validator 조각을 하나씩 구현하며 `references/`에 실험 증거를 남기고 싶을 때
- `contract / valid / invalid` artifact와 `quick_validate` 결과를 함께 판단해야 할 때
- 현재 조각을 닫고 다음 조각으로 넘어갈지 기계적으로 점검하고 싶을 때
- 공용 process와 별도로 skill 내부 실험 루프를 재사용 가능한 형식으로 만들고 싶을 때

## Workflow

1. source of truth는 [knowledge_bases/slice-experiment-lab-knowledge_base-at2026-03-19-00-45.md](knowledge_bases/slice-experiment-lab-knowledge_base-at2026-03-19-00-45.md) 하나로 고정한다.
2. `Canonical Design Takeaways`를 읽고 이 skill이 실험 evaluator이지 smoke runner가 아니라는 경계를 먼저 고정한다.
3. [checklist-forconsistency-evaluation/consistency-checklist-at2026-03-19-00-45.md](checklist-forconsistency-evaluation/consistency-checklist-at2026-03-19-00-45.md) 로 입력 triad와 next-slice gate 규칙을 확인한다.
4. [checklist-forimplementation/implementation-checklist-at2026-03-19-00-45.md](checklist-forimplementation/implementation-checklist-at2026-03-19-00-45.md) 를 읽고 현재 실험 조각과 follow-up 후보를 확인한다.
5. `scripts/slice_experiment_lab.py --help`로 triad 이름 제안, quick_validate capture, smoke capture, bridge layers, strict warning gate, experiment bundle 평가를 수행한다.

## Scripts

- [scripts/slice_experiment_lab.py](scripts/slice_experiment_lab.py) — triad naming helper + quick_validate/smoke capture + bridge layers + strict warning gate + next-slice evaluation
- [scripts/test_slice_experiment_lab.py](scripts/test_slice_experiment_lab.py) — 첫 실험 slice TDD

## References

- [references/vertical-slice-experiment-bundle-at2026-03-19-00-45.md](references/vertical-slice-experiment-bundle-at2026-03-19-00-45.md) — 현재 구현한 실험 slice
- [references/vertical-slice-input-adapters-at2026-03-19-00-57.md](references/vertical-slice-input-adapters-at2026-03-19-00-57.md) — helper 3개를 붙인 입력 정규화 slice
- [references/vertical-slice-quick-validate-artifact-bridge-at2026-03-19-01-07.md](references/vertical-slice-quick-validate-artifact-bridge-at2026-03-19-01-07.md) — quick_validate capture artifact를 canonical bundle로 잇는 bridge slice
- [references/vertical-slice-captured-smoke-to-bundle-at2026-03-19-13-16.md](references/vertical-slice-captured-smoke-to-bundle-at2026-03-19-13-16.md) — captured smoke artifact를 canonical bundle로 잇는 bridge slice
- [references/vertical-slice-strict-warning-policy-gate-at2026-03-19-13-21.md](references/vertical-slice-strict-warning-policy-gate-at2026-03-19-13-21.md) — quick_validate warnings를 strict gate로 판정하는 slice
- [references/troubleshooting.md](references/troubleshooting.md) — 반복 실수와 artifact naming 주의사항

## Notes

- 이 skill은 smoke나 quick_validate를 직접 실행하는 tool runner가 아니라, 그 결과 artifact를 읽고 `ready / hold`를 판정하는 실험 evaluator다.
- helper 3개는 evaluator 앞단의 입력 정규화 layer다.
- `quick_validate_artifact_bundle_bridge`는 capture artifact를 evaluator 입력 bundle로 잇는 bridge layer다.
- `captured_smoke_to_bundle_adapter`는 smoke capture artifact를 evaluator 입력 bundle로 잇는 bridge layer다.
- `strict_warning_policy_gate`는 `quick_validate_capture` artifact의 warnings/errors를 strict 정책으로 한 번 더 해석한다.
- `contract / valid / invalid` triad와 `quick_validate_status`가 같이 있어야 next-slice 판정을 강하게 할 수 있다.
- next-slice 후보는 공용 process가 아니라 각 skill의 implementation checklist를 따른다.
