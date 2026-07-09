# KB Profile Generalization Note

## Summary

- `kb-to-consistency` pair는 `hybrid_kb`로 판정되며 현재 규칙에서 안정적으로 동작한다.
- `contract-to-concept-mapper` general pair는 `research_index_kb`로 판정되며, canonical KB 없이 바로 checklist와 비교하면 coverage 해석이 왜곡된다.

## Evidence

- stable pair report:
  `references/kb-to-consistency-coverage-report-at2026-03-16-16-59.md`
- canonical contract-to-concept pair report:
  `references/contract-to-concept-canonical-pair-report-at2026-03-16-18-08.md`
- general pair report:
  `references/general-pair-profile-report-at2026-03-16-17-34.md`

## Interpretation

- `kb_to_consistency_check.py`는 현재 모든 KB에 보편적으로 쓰는 도구가 아니다.
- 현재 버전은 최소한 아래 두 profile을 구분해야 한다.
  - `hybrid_kb`: canonical takeaway + support/reference inventory가 함께 있는 KB
  - `research_index_kb`: URL inventory / paper note 중심 KB
- `contract-to-concept-canonical-design-at2026-03-16-18-06.md` 같은 canonical KB를 만들면
  general skill도 `hybrid_kb`로 승격되어 checker를 안정적으로 적용할 수 있다.

## Practical Rule

1. `research_index_kb`이면 먼저 canonical takeaway를 만든다.
2. 그 다음 `consistency checklist`와 비교한다.
3. `coverage_ratio`는 canonical unit이 없으면 해석하지 않는다.
