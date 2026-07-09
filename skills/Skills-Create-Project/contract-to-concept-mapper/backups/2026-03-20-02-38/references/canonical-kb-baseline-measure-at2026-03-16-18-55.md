# KB-To-Consistency Coverage Report

- kb: `contract-to-concept-mapper/knowledge_bases/contract-to-concept-canonical-design-at2026-03-16-18-06.md`
- checklist: `contract-to-concept-mapper/checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-14-03.md`
- kb_profile: `hybrid_kb`

## Metrics

- coverage_ratio: `1.0`
- unsupported_item_ratio: `0.0`
- traceability_ratio: `1.0`
- boundary_preservation_ratio: `1.0`

## Support KB Units

- support: `6`

## Ignored KB Units

- metadata: `2`

## missing_from_checklist

- 없음

## unsupported_in_checklist

- 없음

## scope_inflation

- 없음

## boundary_loss

- 없음

## Human Review Queue

- low-confidence mapping: 단순 summarizer가 아니라 `설명 가능한 lifting system`으로 본다.
- low-confidence mapping: traceability 없는 자연어 요약만 남기는 출력은 실패 사례로 본다.
- low-confidence mapping: 최소 출력은 `concept summary`, `boundary description`, `semantic relation map`이다.
- low-confidence mapping: 현재는 scaffold 단계다.
- low-confidence mapping: canonical_role: `contract-to-concept-mapper의 현재 채택 설계를 고정하는 canonical KB`
- low-confidence mapping: codebase 정합성 평가 도구와 직접 동일시하지 않는다.
- low-confidence mapping: 이 skill의 핵심 목적은 `실행 계약 공간 -> 개념 공간` 복원이다.
- low-confidence mapping: 현재는 traceable lifting 구조를 먼저 고정하는 단계다.

## Metric Metadata

- fixed point: [kb-to-consistency-metric-formula-contract-at2026-03-16-19-02.md](../knowledge_bases/kb-to-consistency-metric-formula-contract-at2026-03-16-19-02.md)
- `coverage_ratio`
  - class: `proxy-profile`
  - formula: `matched_canonical_kb_units / total_canonical_kb_units`
- `unsupported_item_ratio`
  - class: `project-custom`
  - formula: `unsupported_checklist_items / total_checklist_items`
- `traceability_ratio`
  - class: `proxy-profile`
  - interpretation: strict proof가 아니라 heuristic mapping 존재 기준
- `boundary_preservation_ratio`
  - class: `proxy-profile`
  - interpretation: 현재는 heuristic guardrail unit 기준
