# research URL Knowledge Base
- ver: `v0.1.0`
- generated_at: `2026-03-16`
- updated_at: `2026-03-16` (v0.1.0: initial KB for kb_to_consistency_check.py)
- canonical_role: `knowledge_base -> consistency checklist 변환 평가 기준을 고정하는 설계 KB`
- canonical_slice: `traceability-based coverage / unsupported item / boundary preservation / scope inflation`
- format: `- [한 줄 설명](URL)`
- generation_method: `GitHub/Paper search 후 traceability·coverage·checklist derivation 관점만 추려 정리`
- total_urls: `10`
- paper_like_urls: `4`
- other_urls: `6`

## Document Map

| 문서 | 역할 |
|------|------|
| [SKILL.md](../SKILL.md) | skill 목적 · 워크플로우 |
| `kb-to-consistency-check-knowledge_base-at2026-03-16-15-44.md` (이 파일) | kb_to_consistency_check 설계용 URL KB |
| [kb-to-consistency-check-github-search-at2026-03-16-15-44.md](../references/kb-to-consistency-check-github-search-at2026-03-16-15-44.md) | GitHub shortlist 및 선택 근거 |
| [kb-to-consistency-check-paper-search-at2026-03-16-15-44.md](../references/kb-to-consistency-check-paper-search-at2026-03-16-15-44.md) | 논문 shortlist 및 선택 근거 |
| [kb-to-consistency-check-evaluation-criteria-at2026-03-16-15-44.md](../references/kb-to-consistency-check-evaluation-criteria-at2026-03-16-15-44.md) | 현재 채택할 평가 기준 메모 |
| [contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md](./contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md) | broader contract-to-concept general KB |

## Table of Contents
- [Canonical Design Takeaways](#canonical-design-takeaways)
- [Current Implementation Target](#current-implementation-target)
- [Paper-like URLs](#paper-like-urls)
- [Other research References URLs](#other-research-references-urls)

## Canonical Design Takeaways

- `kb_to_consistency_check.py`는 완전 자동 semantic judge가 아니라 **candidate traceability gap detector**로 시작하는 편이 맞다.
- 비교 단위는 `knowledge_base 전체`와 `checklist 전체`가 아니라 아래 두 층이다.
  - `KB canonical unit`
  - `consistency checklist item`
- 이 대상은 `구현용 checklist 동기화 검사`와 혼동하지 않는다.
- 이 대상은 `codebase 구현 검증기`와 직접 동일시하지 않는다.
- 최소 비교 방향은 아래 두 개다.
  - `forward`: KB unit이 checklist에 반영되었는가
  - `backward`: checklist item이 KB 근거를 갖는가
- 최소 판정 유형은 아래 5개다.
  - `covered`
  - `missing_from_checklist`
  - `unsupported_in_checklist`
  - `scope_inflation`
  - `boundary_loss`
- 최소 측정 지표는 아래 네 개다.
  - `coverage_ratio`
  - `unsupported_item_ratio`
  - `traceability_ratio`
  - `boundary_preservation_ratio`
- 출력은 단일 score보다 아래 두 층이 더 적합하다.
  - machine-readable JSON
  - human-readable markdown report

## Current Implementation Target

- v0.1은 `anchor/keyword + section-level comparison + human review queue` 방식으로 시작한다.
- 현재 checklist 포맷에는 항목별 `derived_from` / `evidence` 필드가 없으므로, 완전한 traceability matrix는 아직 어렵다.
- 따라서 이 KB에서 만든 `consistency checklist`는 다음 단계 `implementation checklist`의 source of truth로 사용한다.
- v0.1 metric 정의는 아래처럼 둔다.
  - `traceability_ratio`: KB 근거를 역참조 가능한 checklist items / total checklist items
  - `boundary_preservation_ratio`: preserved guardrails / total guardrails
- 따라서 v0.1의 핵심은 아래다.
  - KB canonical unit 추출
  - checklist item 추출
  - heuristic mapping
  - missing / unsupported / inflation 후보 보고

## Paper-like URLs

- [Automated Requirements Traceability: The Study of Human Analysts](https://digitalcommons.calpoly.edu/theses/317/)
  - sources: `kb-to-consistency-check-paper-search-at2026-03-16-15-44.md`
  - agent: `A00`
  - taxonomy: `[[requirements_traceability]] · human_vetting`
  - key_idea: 자동 traceability는 최종 판정기가 아니라 사람이 검토할 후보 집합을 잘 만드는 쪽이 더 현실적이다.
  - execution_conditions: heuristic mapping 결과를 human review queue로 남길 출력 계층 필요
  - pseudocode_3lines:
    - 1) KB unit과 checklist item 후보 매핑을 만든다.
    - 2) 점수가 낮거나 ambiguous한 항목을 분리한다.
    - 3) 사람이 검토할 큐로 출력한다.

- [Automating Requirements Traceability: Two Decades of Learning from KDD](https://ieeexplore.ieee.org/document/8595127)
  - sources: `kb-to-consistency-check-paper-search-at2026-03-16-15-44.md`
  - agent: `A00`
  - taxonomy: `[[requirements_traceability]] · coverage_precision`
  - key_idea: traceability는 coverage와 noise 사이의 균형 문제로 볼 수 있다.
  - execution_conditions: `coverage_ratio`와 `unsupported_item_ratio`를 함께 계산해야 함
  - pseudocode_3lines:
    - 1) KB unit coverage를 계산한다.
    - 2) 근거 없는 checklist item 비율을 계산한다.
    - 3) 둘을 함께 보고한다.

- [Traceability Matrix in Requirements Gathering: A Systematic Review of the Literature](https://perspectivas.espoch.edu.ec/RCP_ESPOCH/en/article/view/221)
  - sources: `kb-to-consistency-check-paper-search-at2026-03-16-15-44.md`
  - agent: `A00`
  - taxonomy: `[[traceability_matrix]] · standardization`
  - key_idea: traceability matrix가 표준화되어 있지 않으면 completeness와 consistency 평가가 흔들린다.
  - execution_conditions: KB unit id / checklist item id / relation type 같은 고정 필드 필요
  - pseudocode_3lines:
    - 1) KB unit과 checklist item에 id를 부여한다.
    - 2) relation type을 기록한다.
    - 3) matrix를 기반으로 누락과 불일치를 계산한다.

- [Blockchain Technology for Requirement Traceability in Systems Engineering](https://www.sciencedirect.com/science/article/abs/pii/S0306437924000425)
  - sources: `kb-to-consistency-check-paper-search-at2026-03-16-15-44.md`
  - agent: `A00`
  - taxonomy: `[[dual_level_traceability]] · artifact_vs_object`
  - key_idea: artifact-level과 object-level traceability를 구분해야 평가가 덜 혼동된다.
  - execution_conditions: KB 문서 전체와 KB canonical unit을 분리하는 계층 설계 필요
  - pseudocode_3lines:
    - 1) 문서 레벨과 항목 레벨을 구분한다.
    - 2) 항목 레벨에서 먼저 매핑한다.
    - 3) 문서 레벨 summary를 나중에 계산한다.

## Other research References URLs

- [StrictDoc](https://github.com/strictdoc-project/strictdoc)
  - sources: `kb-to-consistency-check-github-search-at2026-03-16-15-44.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) requirement unit을 구조화한다.
    - 2) traceability matrix를 만든다.
    - 3) uncovered item을 보고한다.

- [StrictDoc Deep Traceability 문서](https://strictdoc.readthedocs.io/en/stable/stable/docs/strictdoc_21_L2_StrictDoc_Requirements-DEEP-TRACE.html)
  - sources: `kb-to-consistency-check-github-search-at2026-03-16-15-44.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) forward/backward traceability를 분리한다.
    - 2) uncovered requirement view를 제공한다.
    - 3) trace gap을 항목 단위로 출력한다.

- [Sphinx-Needs](https://github.com/useblocks/sphinx-needs)
  - sources: `kb-to-consistency-check-github-search-at2026-03-16-15-44.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) need-like unit을 만든다.
    - 2) unit 간 링크를 기록한다.
    - 3) filtered view로 gap을 본다.

- [Coral RepoDocConsistencyChecker Agent](https://github.com/Coral-Protocol/Coral-RepoDocConsistencyChecker-Agent)
  - sources: `kb-to-consistency-check-github-search-at2026-03-16-15-44.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 비교 대상 문서를 입력받는다.
    - 2) itemized inconsistency를 생성한다.
    - 3) 분류형 보고서로 출력한다.

- [OpenAPI-diff](https://github.com/OpenAPITools/openapi-diff)
  - sources: `kb-to-consistency-check-github-search-at2026-03-16-15-44.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 두 artifact를 읽는다.
    - 2) structured diff를 계산한다.
    - 3) diff 타입별 결과를 분리한다.

- [pydoclint](https://github.com/jsh9/pydoclint)
  - sources: `kb-to-consistency-check-github-search-at2026-03-16-15-44.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 문서와 대상 구조를 읽는다.
    - 2) 항목별 규칙 위반을 찾는다.
    - 3) lint 메시지로 출력한다.
