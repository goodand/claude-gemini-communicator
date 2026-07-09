# KB-To-Consistency Coverage Report

- kb: `contract-to-concept-mapper/knowledge_bases/kb-to-consistency-check-knowledge_base-at2026-03-16-15-44.md`
- checklist: `contract-to-concept-mapper/checklist-forconsistency-evaluation/kb-to-consistency-consistency-checklist-at2026-03-16-15-55.md`

## Metrics

- coverage_ratio: `0.75`
- unsupported_item_ratio: `0.6216`
- traceability_ratio: `0.3784`
- boundary_preservation_ratio: `0.75`

## Ignored KB Units

- metadata: `10`
- reference_inventory: `10`
- toc: `4`

## missing_from_checklist

- 최소 비교 방향은 아래 두 개다.
- 따라서 v0.1의 핵심은 아래다.

## unsupported_in_checklist

- **A-03**: 구현용 checklist 동기화 문제와 혼동되지 않는다
- **A-04**: codebase 구현 검증기와 직접 동일시되지 않는다
- **B-01**: `forward` 비교가 정의돼 있다
- **B-02**: `backward` 비교가 정의돼 있다
- **B-03**: forward만 있고 backward가 빠지지 않는다
- **B-04**: backward만 있고 coverage 관점이 빠지지 않는다
- **C-01**: KB를 canonical unit으로 나눌 필요가 반영돼 있다
- **C-02**: checklist item도 별도 비교 단위로 다뤄진다
- **C-03**: artifact-level과 object-level을 구분한다
- **E-01**: `coverage_ratio`를 계산하거나 동등 지표가 있다
- **E-02**: `unsupported_item_ratio`를 계산하거나 동등 지표가 있다
- **E-03**: `traceability_ratio`를 계산하거나 동등 지표가 있다
- **E-04**: `boundary_preservation_ratio`를 계산하거나 동등 지표가 있다
- **F-01**: checklist 판정에 KB 근거를 연결할 수 있어야 한다
- **F-03**: ambiguity가 높은 항목은 human review queue로 보낸다
- **G-01**: machine-readable JSON 출력이 있다
- **G-02**: human-readable markdown report 출력이 있다
- **G-03**: missing / unsupported / inflation / boundary loss를 분리해 보여준다
- **G-04**: human review needed 항목을 별도 출력할 수 있다
- **H-04**: heuristic mapping 결과를 최종 truth로 단정하지 않는다
- **I-01**: 이 checklist는 KB의 canonical slice를 충분히 operationalize한다
- **I-02**: 구현 전 단계에서 봐야 할 주요 risk가 coverage / unsupported / boundary / inflation으로 정리된다
- **I-03**: 다음 단계 구현용 checklist는 이 문서를 source of truth로 삼아야 한다

## scope_inflation

- 없음

## boundary_loss

- 없음

## Human Review Queue

- low-confidence mapping: v0.1은 `anchor/keyword + section-level comparison + human review queue` 방식으로 시작한다.
- low-confidence mapping: 최소 판정 유형은 아래 5개다.
- low-confidence mapping: 최소 판정 유형은 아래 5개다.
- low-confidence mapping: 최소 판정 유형은 아래 5개다.
- low-confidence mapping: 최소 판정 유형은 아래 5개다.
- low-confidence mapping: 최소 판정 유형은 아래 5개다.
- low-confidence mapping: 출력은 단일 score보다 아래 두 층이 더 적합하다.
- low-confidence mapping: 현재 checklist 포맷에는 항목별 `derived_from` / `evidence` 필드가 없으므로, 완전한 traceability matrix는 아직 어렵다.
- low-confidence mapping: `kb_to_consistency_check.py`는 완전 자동 semantic judge가 아니라 **candidate traceability gap detector**로 시작하는 편이 맞다.
