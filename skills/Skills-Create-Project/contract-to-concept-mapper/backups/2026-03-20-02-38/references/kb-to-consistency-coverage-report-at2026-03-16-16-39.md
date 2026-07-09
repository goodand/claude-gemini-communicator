# KB-To-Consistency Coverage Report

- kb: `contract-to-concept-mapper/knowledge_bases/kb-to-consistency-check-knowledge_base-at2026-03-16-15-44.md`
- checklist: `contract-to-concept-mapper/checklist-forconsistency-evaluation/kb-to-consistency-consistency-checklist-at2026-03-16-15-55.md`

## Metrics

- coverage_ratio: `0.7391`
- unsupported_item_ratio: `0.2973`
- traceability_ratio: `0.7027`
- boundary_preservation_ratio: `0.8`

## Ignored KB Units

- metadata: `10`
- reference_inventory: `82`
- toc: `4`

## missing_from_checklist

- `consistency checklist item`
- 최소 비교 방향은 아래 두 개다.
- 최소 판정 유형은 아래 5개다.
- 따라서 v0.1의 핵심은 아래다.
- KB canonical unit 추출
- checklist item 추출

## unsupported_in_checklist

- 구현용 checklist 동기화 문제와 혼동되지 않는다
- codebase 구현 검증기와 직접 동일시되지 않는다
- checklist item도 별도 비교 단위로 다뤄진다
- artifact-level과 object-level을 구분한다
- `coverage_ratio`를 계산하거나 동등 지표가 있다
- `unsupported_item_ratio`를 계산하거나 동등 지표가 있다
- `traceability_ratio`를 계산하거나 동등 지표가 있다
- `boundary_preservation_ratio`를 계산하거나 동등 지표가 있다
- ambiguity가 높은 항목은 human review queue로 보낸다
- human review needed 항목을 별도 출력할 수 있다
- 다음 단계 구현용 checklist는 이 문서를 source of truth로 삼아야 한다

## scope_inflation

- 없음

## boundary_loss

- 없음

## Human Review Queue

- low-confidence mapping: `forward`: KB unit이 checklist에 반영되었는가
- low-confidence mapping: `backward`: checklist item이 KB 근거를 갖는가
- low-confidence mapping: `KB canonical unit`
- low-confidence mapping: v0.1은 `anchor/keyword + section-level comparison + human review queue` 방식으로 시작한다.
- low-confidence mapping: 출력은 단일 score보다 아래 두 층이 더 적합하다.
- low-confidence mapping: `backward`: checklist item이 KB 근거를 갖는가
- low-confidence mapping: 현재 checklist 포맷에는 항목별 `derived_from` / `evidence` 필드가 없으므로, 완전한 traceability matrix는 아직 어렵다.
- low-confidence mapping: `kb_to_consistency_check.py`는 완전 자동 semantic judge가 아니라 **candidate traceability gap detector**로 시작하는 편이 맞다.
- low-confidence mapping: `KB canonical unit`
- low-confidence mapping: missing / unsupported / inflation 후보 보고
