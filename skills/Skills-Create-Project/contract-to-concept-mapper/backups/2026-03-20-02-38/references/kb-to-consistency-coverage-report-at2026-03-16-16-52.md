# KB-To-Consistency Coverage Report

- kb: `contract-to-concept-mapper/knowledge_bases/kb-to-consistency-check-knowledge_base-at2026-03-16-15-44.md`
- checklist: `contract-to-concept-mapper/checklist-forconsistency-evaluation/kb-to-consistency-consistency-checklist-at2026-03-16-15-55.md`

## Metrics

- coverage_ratio: `0.6765`
- unsupported_item_ratio: `0.0`
- traceability_ratio: `1.0`
- boundary_preservation_ratio: `0.5`

## Support KB Units

- support: `14`

## Ignored KB Units

- metadata: `8`
- reference_inventory: `70`
- toc: `4`

## missing_from_checklist

- 비교 단위는 `knowledge_base 전체`와 `checklist 전체`가 아니라 아래 두 층이다.
- 최소 비교 방향은 아래 두 개다.
- 최소 판정 유형은 아래 5개다.
- 최소 측정 지표는 아래 네 개다.
- 출력은 단일 score보다 아래 두 층이 더 적합하다.
- v0.1 metric 정의는 아래처럼 둔다.
- `traceability_ratio`: KB 근거를 역참조 가능한 checklist items / total checklist items
- `boundary_preservation_ratio`: preserved guardrails / total guardrails
- 따라서 v0.1의 핵심은 아래다.
- KB canonical unit 추출
- checklist item 추출

## unsupported_in_checklist

- 없음

## scope_inflation

- 없음

## boundary_loss

- 없음

## Human Review Queue

- low-confidence mapping: 이 대상은 `구현용 checklist 동기화 검사`와 혼동하지 않는다.
- low-confidence mapping: 이 대상은 `구현용 checklist 동기화 검사`와 혼동하지 않는다.
- low-confidence mapping: `consistency checklist item`
- low-confidence mapping: v0.1은 `anchor/keyword + section-level comparison + human review queue` 방식으로 시작한다.
- low-confidence mapping: 이 대상은 `구현용 checklist 동기화 검사`와 혼동하지 않는다.
- low-confidence mapping: `backward`: checklist item이 KB 근거를 갖는가
- low-confidence mapping: `kb_to_consistency_check.py`는 완전 자동 semantic judge가 아니라 **candidate traceability gap detector**로 시작하는 편이 맞다.
- low-confidence mapping: `KB canonical unit`
