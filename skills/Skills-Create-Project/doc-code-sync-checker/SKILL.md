---
name: doc-code-sync-checker
description: >-
  verification-decision-gate family의 documented-rule sync specialist. Use this
  skill when reference documents define rules, fields, transitions, or
  constraints that must exist in code and pairwise document-code drift must be
  reported. broader consistency routing과 next-step gate는
  verification-decision-gate를 사용하라.
---

# Doc-Code Sync Checker

reference 문서의 규칙을 추출하고 validate/상수/전이표 구현과 대조하여 pairwise drift를 찾는다.

## Read Order

1. `references/indexes/doc-code-sync-family-index-at2026-03-16-18-18.md`
2. 필요한 family 문서 1개 이상
3. `knowledge_bases/doc-code-sync-canonical-design-at2026-03-16-18-18.md`
4. `references/vertical-slice-required-field-at2026-03-16-20-03.md`
5. `references/vertical-slice-path-safety-at2026-03-16-20-44.md`
6. `references/vertical-slice-transition-rule-at2026-03-16-21-48.md`
7. `references/vertical-slice-enum-value-at2026-03-16-22-13.md`
8. `checklist-forconsistency-evaluation/consistency-checklist.md`
9. `checklist-forimplementation/implementation-checklist.md`
10. `scripts/doc_code_sync.py`

## Use When

- field reference와 validate 함수가 일치하는지 확인할 때
- 상태 전이표, enum, 경로 규칙이 코드에 반영됐는지 검사할 때
- "문서에 썼지만 코드에 없음" 유형의 버그를 사전 차단할 때
- troubleshooting의 정합성 패턴을 재검증할 때
- `artifact-lifecycle-manager`가 stale candidate로 올린 rule-bearing reference를 2차 semantic recheck할 때

## Layers

- `references/families/pairwise-sync-family-at2026-03-16-18-18.md` — pairwise workflow와 scope
- `references/families/rule-taxonomy-family-at2026-03-16-18-18.md` — 우선 지원할 규칙 유형
- `references/families/drift-report-family-at2026-03-16-18-18.md` — compare/report 출력 계약
- `knowledge_bases/doc-code-sync-canonical-design-at2026-03-16-18-18.md` — checklist와 codebase의 직접 source of truth
- `knowledge_bases/doc-code-sync-checker-knowledge_base-at2026-03-16.md` — research/hybrid KB, 사례와 대안 탐색용

## Scripts and Evidence

- `scripts/doc_code_sync.py` — `required_field`, `path_safety`, `transition_rule`, `enum_value` pairwise slice 구현. `python3 scripts/doc_code_sync.py --help`
- `references/install-readiness-dependency-map-at2026-03-17-09-28.md` — 다른 workspace 설치 시 `install-required / optional fixture / internalize` 분류
- `references/vertical-slice-required-field-at2026-03-16-20-03.md` — 첫 구현 대상 pair와 `required_field` vertical slice 정의
- `references/vertical-slice-path-safety-at2026-03-16-20-44.md` — `dispatch-fields.md <-> dispatch_manager.py` path safety slice 정의
- `references/vertical-slice-transition-rule-at2026-03-16-21-48.md` — 전이표 ↔ `VALID_TRANSITIONS` slice 정의
- `references/vertical-slice-enum-value-at2026-03-16-22-13.md` — status enum ↔ `VALID_STATUSES` slice 정의
- `references/sync-targets.md` — 비교 대상 유형
- `references/sync-checklist.md` — 문서-코드 정합성 체크리스트
- `references/troubleshooting.md` — drift 실전 사례

## Notes

- 시작점은 항상 **reference 문서 규칙** 또는 **validate 구현 규칙** 둘 중 하나를 명시한다
- research/hybrid KB를 checklist source로 바로 쓰지 말고 canonical KB를 먼저 본다
- 다이어그램, 표, 상수 dict는 서로 다른 표현이지만 같은 계약일 수 있다
- claim-verifier와 달리 시작점은 자연어 주장보다 **규칙 집합(rule set)** 이다
- `normalize`는 v0.1에서 compare 내부 단계다
- 현재 구현 slice는 `required_field`, `path_safety`, `transition_rule`, `enum_value` 네 종류다
- core engine은 이 skill 폴더만으로 닫히지만, bundled sample pair를 그대로 재현하려면 `references/install-readiness-dependency-map-at2026-03-17-09-28.md`의 optional fixture 분류를 먼저 확인한다
- `reference freshness audit`의 1차 stale candidate 탐지는 `artifact-lifecycle-manager`가 맡고, 이 skill은 rule-bearing reference의 2차 semantic recheck를 맡는다
