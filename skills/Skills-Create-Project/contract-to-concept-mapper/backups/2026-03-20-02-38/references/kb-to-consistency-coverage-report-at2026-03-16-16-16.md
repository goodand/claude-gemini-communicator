# KB-To-Consistency Coverage Report

- kb: `contract-to-concept-mapper/knowledge_bases/kb-to-consistency-check-knowledge_base-at2026-03-16-15-44.md`
- checklist: `contract-to-concept-mapper/checklist-forconsistency-evaluation/kb-to-consistency-consistency-checklist-at2026-03-16-15-55.md`

## Metrics

- coverage_ratio: `0.3125`
- unsupported_item_ratio: `0.4324`
- traceability_ratio: `0.5676`
- boundary_preservation_ratio: `0.5`

## missing_from_checklist

- ver: `v0.1.0`
- generated_at: `2026-03-16`
- format: `- [한 줄 설명](URL)`
- total_urls: `10`
- paper_like_urls: `4`
- other_urls: `6`
- [Canonical Design Takeaways](#canonical-design-takeaways)
- [Current Implementation Target](#current-implementation-target)
- [Paper-like URLs](#paper-like-urls)
- [Other research References URLs](#other-research-references-urls)
- 비교 단위는 `knowledge_base 전체`와 `checklist 전체`가 아니라 아래 두 층이다.
- 최소 비교 방향은 아래 두 개다.
- 따라서 v0.1의 핵심은 아래다.
- [Automating Requirements Traceability: Two Decades of Learning from KDD](https://ieeexplore.ieee.org/document/8595127)
- [Traceability Matrix in Requirements Gathering: A Systematic Review of the Literature](https://perspectivas.espoch.edu.ec/RCP_ESPOCH/en/article/view/221)
- [Blockchain Technology for Requirement Traceability in Systems Engineering](https://www.sciencedirect.com/science/article/abs/pii/S0306437924000425)
- [StrictDoc](https://github.com/strictdoc-project/strictdoc)
- [StrictDoc Deep Traceability 문서](https://strictdoc.readthedocs.io/en/stable/stable/docs/strictdoc_21_L2_StrictDoc_Requirements-DEEP-TRACE.html)
- [Sphinx-Needs](https://github.com/useblocks/sphinx-needs)
- [Coral RepoDocConsistencyChecker Agent](https://github.com/Coral-Protocol/Coral-RepoDocConsistencyChecker-Agent)
- [OpenAPI-diff](https://github.com/OpenAPITools/openapi-diff)
- [pydoclint](https://github.com/jsh9/pydoclint)

## unsupported_in_checklist

- **A-03**: 구현용 checklist 동기화 문제와 혼동되지 않는다
- **A-04**: codebase 구현 검증기와 직접 동일시되지 않는다
- **B-01**: `forward` 비교가 정의돼 있다
- **B-02**: `backward` 비교가 정의돼 있다
- **B-03**: forward만 있고 backward가 빠지지 않는다
- **C-02**: checklist item도 별도 비교 단위로 다뤄진다
- **C-03**: artifact-level과 object-level을 구분한다
- **E-01**: `coverage_ratio`를 계산하거나 동등 지표가 있다
- **E-02**: `unsupported_item_ratio`를 계산하거나 동등 지표가 있다
- **E-03**: `traceability_ratio`를 계산하거나 동등 지표가 있다
- **E-04**: `boundary_preservation_ratio`를 계산하거나 동등 지표가 있다
- **F-03**: ambiguity가 높은 항목은 human review queue로 보낸다
- **G-01**: machine-readable JSON 출력이 있다
- **G-02**: human-readable markdown report 출력이 있다
- **G-04**: human review needed 항목을 별도 출력할 수 있다
- **H-04**: heuristic mapping 결과를 최종 truth로 단정하지 않는다

## scope_inflation

- 없음

## boundary_loss

- 없음

## Human Review Queue

- low-confidence mapping: canonical_slice: `traceability-based coverage / unsupported item / boundary preservation / scope inflation`
- low-confidence mapping: updated_at: `2026-03-16` (v0.1.0: initial KB for kb_to_consistency_check.py)
- low-confidence mapping: v0.1은 `anchor/keyword + section-level comparison + human review queue` 방식으로 시작한다.
- low-confidence mapping: 최소 판정 유형은 아래 5개다.
- low-confidence mapping: 최소 판정 유형은 아래 5개다.
- low-confidence mapping: 최소 판정 유형은 아래 5개다.
- low-confidence mapping: 최소 판정 유형은 아래 5개다.
- low-confidence mapping: 최소 판정 유형은 아래 5개다.
- low-confidence mapping: 출력은 단일 score보다 아래 두 층이 더 적합하다.
- low-confidence mapping: updated_at: `2026-03-16` (v0.1.0: initial KB for kb_to_consistency_check.py)
- low-confidence mapping: 현재 checklist 포맷에는 항목별 `derived_from` / `evidence` 필드가 없으므로, 완전한 traceability matrix는 아직 어렵다.
- low-confidence mapping: generation_method: `GitHub/Paper search 후 traceability·coverage·checklist derivation 관점만 추려 정리`
- low-confidence mapping: updated_at: `2026-03-16` (v0.1.0: initial KB for kb_to_consistency_check.py)
- low-confidence mapping: [Automated Requirements Traceability: The Study of Human Analysts](https://digitalcommons.calpoly.edu/theses/317/)
