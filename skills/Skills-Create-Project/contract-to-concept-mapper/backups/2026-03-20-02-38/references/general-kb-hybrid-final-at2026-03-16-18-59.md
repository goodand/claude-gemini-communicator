# KB-To-Consistency Coverage Report

- kb: `contract-to-concept-mapper/knowledge_bases/contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md`
- checklist: `contract-to-concept-mapper/checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-14-03.md`
- kb_profile: `hybrid_kb`

## Metrics

- coverage_ratio: `1.0`
- unsupported_item_ratio: `0.0`
- traceability_ratio: `1.0`
- boundary_preservation_ratio: `1.0`

## Support KB Units

- support: `43`

## Ignored KB Units

- metadata: `8`
- reference_inventory: `98`
- toc: `6`

## missing_from_checklist

- 없음

## unsupported_in_checklist

- 없음

## scope_inflation

- 없음

## boundary_loss

- 없음

## Human Review Queue

- low-confidence mapping: execution_conditions: diff나 변경된 contract unit을 입력으로 취급할 수 있어야 함
- low-confidence mapping: Mermaid / pseudocode는 주요 render target이고, vector output은 보조 층이다.
- low-confidence mapping: traceability 없는 자연어 요약만 남기는 출력은 실패 사례로 본다.
- low-confidence mapping: 최소 출력은 `concept summary`, `boundary description`, `semantic relation map`이다.
- low-confidence mapping: 이 skill의 핵심 목적은 `실행 계약 공간 -> 개념 공간` 복원이다.
- low-confidence mapping: 이 skill의 핵심 목적은 `실행 계약 공간 -> 개념 공간` 복원이다.
- low-confidence mapping: canonical_role: `외부 사례와 현재 채택 설계 slice를 함께 담는 hybrid KB`
- low-confidence mapping: 현재는 scaffold 단계다.
- low-confidence mapping: 이 skill의 v0.1 비교 단위는 broad research document가 아니라 canonical slice다.
- low-confidence mapping: codebase 정합성 평가기나 실행 로그 수집기와 직접 동일시하지 않는다.
- low-confidence mapping: 이 skill의 핵심 목적은 `실행 계약 공간 -> 개념 공간` 복원이다.
- low-confidence mapping: 단순 summarizer보다 `설명 가능한 lifting system`으로 보는 편이 맞다.

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
