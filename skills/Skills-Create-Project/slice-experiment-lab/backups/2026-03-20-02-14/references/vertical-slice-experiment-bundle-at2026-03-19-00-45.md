# experiment_bundle vertical slice

- timestamp: `2026-03-19-00-45`
- source_of_truth: [../knowledge_bases/slice-experiment-lab-knowledge_base-at2026-03-19-00-45.md](../knowledge_bases/slice-experiment-lab-knowledge_base-at2026-03-19-00-45.md)
- checklist: [../checklist-forimplementation/implementation-checklist-at2026-03-19-00-45.md](../checklist-forimplementation/implementation-checklist-at2026-03-19-00-45.md)

## Goal

contract slice 실험 bundle과 next-slice gate를 reusable evaluator로 고정한다.

## Implemented Commands

- `emit-experiment-bundle-contract`
- `evaluate-experiment-bundle`
- `suggest-triad-names`
- `capture-quick-validate`
- `capture-smoke-command`

## Decision Gate

- contract artifact 존재
- valid artifact status = `valid`
- invalid artifact status = `invalid`
- `quick_validate_status = passed`
- `next_slice_candidate` 존재

위가 모두 맞으면 `ready_for_next_slice`, 아니면 `hold_current_slice`.
