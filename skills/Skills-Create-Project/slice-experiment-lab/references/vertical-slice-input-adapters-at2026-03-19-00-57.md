# input adapter slice

- timestamp: `2026-03-19-00-57`
- source_of_truth: [../knowledge_bases/slice-experiment-lab-knowledge_base-at2026-03-19-00-45.md](../knowledge_bases/slice-experiment-lab-knowledge_base-at2026-03-19-00-45.md)
- consistency_checklist: [../checklist-forconsistency-evaluation/consistency-checklist-at2026-03-19-00-45.md](../checklist-forconsistency-evaluation/consistency-checklist-at2026-03-19-00-45.md)

## Goal

evaluator 앞단의 입력 정규화 layer를 붙여 triad naming, quick_validate capture, smoke command capture를 재사용 가능한 subcommand로 고정한다.

## Implemented Commands

- `suggest-triad-names`
- `capture-quick-validate`
- `capture-smoke-command`

## Adapter Scope

- triad naming helper는 `contract / valid / invalid` 파일명 규칙을 제안한다
- quick_validate adapter는 `stdout/stderr/exit code`를 `passed|failed` artifact로 정규화한다
- smoke command adapter는 smoke command 결과를 `valid|invalid|capture_failed` artifact로 정규화한다
