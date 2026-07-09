# Profile Generalization Experiment

- generated_at: `2026-03-16-19-35`
- checker: `contract-to-concept-mapper/scripts/kb_to_consistency_check.py`
- purpose: `research_index_kb / hybrid_kb / canonical_design_kb` profile이 `contract-to-concept-mapper` 특수 케이스인지, 아니면 다른 skill에도 같은 패턴이 보이는지 확인

## Inputs

| skill | kb | checklist |
|---|---|---|
| contract-to-concept-mapper | [legacy original KB](../legacy/2026-03-16-18-56-pre-hybrid-promotion/contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md) | [consistency checklist](../checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-14-03.md) |
| contract-to-concept-mapper | [current hybrid KB](../knowledge_bases/contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md) | [consistency checklist](../checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-14-03.md) |
| contract-to-concept-mapper | [canonical KB](../knowledge_bases/contract-to-concept-canonical-design-at2026-03-16-18-06.md) | [consistency checklist](../checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-14-03.md) |
| doc-code-sync-checker | [doc hybrid KB](../../doc-code-sync-checker/knowledge_bases/doc-code-sync-checker-knowledge_base-at2026-03-16.md) | [doc consistency checklist](../../doc-code-sync-checker/checklist-forconsistency-evaluation/consistency-checklist.md) |
| doc-code-sync-checker | [doc canonical KB](../../doc-code-sync-checker/knowledge_bases/doc-code-sync-canonical-design-at2026-03-16-18-18.md) | [doc consistency checklist](../../doc-code-sync-checker/checklist-forconsistency-evaluation/consistency-checklist.md) |

## Matrix

| case | detected profile | coverage_ratio | unsupported_item_ratio | traceability_ratio | boundary_preservation_ratio | warnings |
|---|---|---:|---:|---:|---:|---|
| contract research original | `research_index_kb` | `n/a` | `0.3` | `0.7` | `1.0` | `2` |
| contract hybrid current | `hybrid_kb` | `1.0` | `0.0` | `1.0` | `1.0` | `0` |
| contract canonical | `canonical_design_kb` | `1.0` | `0.0` | `1.0` | `1.0` | `0` |
| doc hybrid current | `hybrid_kb` | `0.36` | `0.2` | `0.8` | `1.0` | `0` |
| doc canonical | `canonical_design_kb` | `0.8` | `0.1333` | `0.8667` | `0.6667` | `0` |

## Profile-Level Averages

| profile | cases | coverage_ratio | unsupported_item_ratio | traceability_ratio | boundary_preservation_ratio |
|---|---:|---:|---:|---:|---:|
| `research_index_kb` | 1 | `n/a` | `0.3` | `0.7` | `1.0` |
| `hybrid_kb` | 2 | `0.68` | `0.1` | `0.9` | `1.0` |
| `canonical_design_kb` | 2 | `0.9` | `0.0667` | `0.9334` | `0.8334` |

## Findings

1. `research_index_kb`는 cross-skill 이전에 구조적으로 직접 비교 대상이 아니다.
   - canonical unit이 없어서 `coverage_ratio`가 `n/a`로 나온다.
   - warning도 항상 같이 뜬다.
   - 즉 이 profile은 checklist direct source of truth로 쓰기 어렵다.

2. profile 효과는 `contract-to-concept-mapper` 특수 케이스가 아니다.
   - `doc-code-sync-checker`에서도 `hybrid_kb`, `canonical_design_kb`가 실제 측정 가능한 상태로 잡혔다.
   - 즉 `research -> hybrid/canonical`로 갈수록 측정 가능성이 높아지는 패턴 자체는 일반화된다.

3. 다만 profile만으로 모든 variance가 설명되지는 않는다.
   - `contract-to-concept-mapper`는 `hybrid`와 `canonical` 둘 다 `1.0 / 0.0 / 1.0 / 1.0`이다.
   - `doc-code-sync-checker`는 같은 profile이어도 `hybrid`가 `0.36 / 0.2 / 0.8 / 1.0`, `canonical`이 `0.8 / 0.1333 / 0.8667 / 0.6667`이다.
   - 따라서 profile은 1차 원인이고, 실제 canonical completeness와 checklist wording alignment가 2차 원인이다.

4. 이번 실험 중 checker 분류 기준도 보정했다.
   - 이전에는 support metadata가 있으면 canonical 문서도 `hybrid_kb`로 접혔다.
   - 지금은 `reference inventory` 존재 여부를 기준으로 `hybrid_kb`와 `canonical_design_kb`를 구분한다.
   - `source_research_kb`도 support metadata로 승격해서 canonical unit 오탐을 줄였다.

## Cause Analysis

### First-Order Cause

- `research_index_kb`는 reference inventory 중심이라 checklist와 직접 비교할 canonical unit이 없다.
- 그래서 이 profile에서는 metric이 의미를 잃거나, unsupported만 높게 보이기 쉽다.

### Second-Order Cause

- `hybrid_kb`와 `canonical_design_kb`는 비교가 가능하지만, 결과는 skill마다 다르다.
- 핵심 차이는 `Canonical Design Takeaways`의 완성도와 checklist의 문장 정렬 정도다.

### Third-Order Cause

- checker의 typing/mapping heuristic도 잔여 variance를 만든다.
- 이번 수정으로 `source_research_kb` 오탐은 줄였지만, `doc-code-sync-checker`에는 아직 아래 같은 잔여 mismatch가 남는다.
  - KB에 있는 rule-type/guardrail 문장이 checklist에서 더 넓거나 다른 문장으로 표현됨
  - checklist의 `intent`, `runtime smoke test`, `구현 깊이 부족 vs scope inflation 분류` 같은 항목이 canonical KB에 직접 쓰여 있지 않음

## Representative Residuals

### doc-code-sync-checker hybrid missing examples

- `최소 결과 분류는 아래 3개다.`
- ``missing_in_doc``
- `우선 비교할 규칙 유형은 아래 4개다.`
- `필드/필수값`

### doc-code-sync-checker canonical missing examples

- `우선 지원할 규칙 유형은 필수 필드, enum/상수, 상태 전이표, 경로 규칙이다.`
- `이 skill은 repo-wide crawler가 아니라 명시적으로 지정한 문서/스크립트 쌍을 검사하는 로컬 도구다.`
- `scaffold 단계와 실제 구현 단계를 혼동하지 않는다.`

### doc-code-sync-checker unsupported examples

- ``intent`는 참고용이고 구현 기준이 아님이 분리돼 있다`
- `runtime smoke test용 도구인지, 대규모 semantic diff 엔진인지 경계가 명확하다`
- `code 변경 없이 smoke test/검증 보고만 만드는 사용 시나리오가 가능하다`
- `현재 불일치는 구현 깊이 부족인지, scope inflation인지 분류 가능하다`

## Conclusion

- 원인 분석 기준으로 보면, 이번 패턴은 `contract-to-concept-mapper` 특수 케이스가 아니다.
- `profile mismatch`가 1차 원인이라는 점은 다른 skill에서도 재현된다.
- 하지만 `hybrid -> canonical` 승격만으로 자동으로 `1.0`이 되지는 않는다.
- 그 다음 단계의 실제 원인은 `canonical KB completeness + checklist wording alignment + checker mapping heuristic`의 결합이다.

## Next Actions

1. `doc-code-sync-checker` canonical KB에 guardrail / scope / local-tool wording을 더 직접적으로 추가
2. 또는 `doc-code-sync-checker` consistency checklist를 canonical KB 표현에 맞게 정리
3. 그 뒤 같은 실험을 다시 돌려 `doc canonical` 수치가 `contract canonical`에 얼마나 가까워지는지 비교
