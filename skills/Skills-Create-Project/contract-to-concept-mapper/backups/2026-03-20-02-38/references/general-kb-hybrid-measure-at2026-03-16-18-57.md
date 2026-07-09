# KB-To-Consistency Coverage Report

- kb: `contract-to-concept-mapper/knowledge_bases/contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md`
- checklist: `contract-to-concept-mapper/checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-14-03.md`
- kb_profile: `hybrid_kb`

## Metrics

- coverage_ratio: `0.5926`
- unsupported_item_ratio: `0.0333`
- traceability_ratio: `0.9667`
- boundary_preservation_ratio: `0.4`

## Support KB Units

- support: `31`

## Ignored KB Units

- metadata: `8`
- reference_inventory: `98`
- toc: `6`

## missing_from_checklist

- source_research_files: `contract-to-concept-mapper-github-search-at2026-03-16.md`, `contract-to-concept-mapper-paper-search-at2026-03-16.md`
- 이 문서는 `research_index_kb`만이 아니라 `hybrid_kb`다.
- URL inventory와 사례 모음을 유지하되, direct compare용 기준은 `Canonical Design Takeaways`에 둔다.
- metric은 `fixed point -> interpretation -> execution` 3층으로 본다.
- fixed point 원칙은 [measurement-strategy-from-eval-runner-rag-bench-at2026-03-16-18-47.md](../references/measurement-strategy-from-eval-runner-rag-bench-at2026-03-16-18-47.md)를 따른다.
- `coverage_ratio`
- `unsupported_item_ratio`
- `traceability_ratio`
- `boundary_preservation_ratio`
- 위 4개는 현재 strict metric보다는 heuristic/candidate metric에 가깝다.
- 따라서 report에서는 단일 점수보다 mapping table과 human review queue를 함께 본다.

## unsupported_in_checklist

- `semantic-slice-mapper`, `execution-contract-mapper`, `evidence-trace-auditor`와 책임이 구분된다

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
- low-confidence mapping: `kb_to_consistency_check.py` 같은 checker는 이 문서 전체가 아니라 canonical slice를 우선 읽는 것이 맞다.
- low-confidence mapping: 이 skill의 핵심 목적은 `실행 계약 공간 -> 개념 공간` 복원이다.
- low-confidence mapping: 단순 summarizer보다 `설명 가능한 lifting system`으로 보는 편이 맞다.
