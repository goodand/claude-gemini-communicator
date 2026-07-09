---
name: doc-code-sync-checker
description: >-
  Use this skill when reference documents define rules, fields, transitions, or
  constraints that must exist in code — extracts documented rules, compares them
  with validate logic, and reports document-code drift.
  문서에 적힌 규칙과 코드 구현의 정합성을 검사하고 drift를 보고한다.
---

# Doc-Code Sync Checker

reference 문서의 규칙을 추출하고 validate/상수/전이표 구현과 대조하여 pairwise drift를 찾는다.

## Read Order

1. `references/indexes/doc-code-sync-family-index-at2026-03-16-18-18.md`
2. 필요한 family 문서 1개 이상
3. `knowledge_bases/doc-code-sync-canonical-design-at2026-03-16-18-18.md`
4. `checklist-forconsistency-evaluation/consistency-checklist.md`
5. `scripts/doc_code_sync.py`

## Use When

- field reference와 validate 함수가 일치하는지 확인할 때
- 상태 전이표, enum, 경로 규칙이 코드에 반영됐는지 검사할 때
- "문서에 썼지만 코드에 없음" 유형의 버그를 사전 차단할 때
- troubleshooting의 정합성 패턴을 재검증할 때

## Layers

- `references/families/pairwise-sync-family-at2026-03-16-18-18.md` — pairwise workflow와 scope
- `references/families/rule-taxonomy-family-at2026-03-16-18-18.md` — 우선 지원할 규칙 유형
- `references/families/drift-report-family-at2026-03-16-18-18.md` — compare/report 출력 계약
- `knowledge_bases/doc-code-sync-canonical-design-at2026-03-16-18-18.md` — checklist와 codebase의 직접 source of truth
- `knowledge_bases/doc-code-sync-checker-knowledge_base-at2026-03-16.md` — research/hybrid KB, 사례와 대안 탐색용

## Scripts and Evidence

- `scripts/doc_code_sync.py` — extract-doc/extract-code/compare/report 스캐폴드. `python3 scripts/doc_code_sync.py --help`
- `references/sync-targets.md` — 비교 대상 유형
- `references/sync-checklist.md` — 문서-코드 정합성 체크리스트
- `references/troubleshooting.md` — drift 실전 사례

## Notes

- 시작점은 항상 **reference 문서 규칙** 또는 **validate 구현 규칙** 둘 중 하나를 명시한다
- research/hybrid KB를 checklist source로 바로 쓰지 말고 canonical KB를 먼저 본다
- 다이어그램, 표, 상수 dict는 서로 다른 표현이지만 같은 계약일 수 있다
- claim-verifier와 달리 시작점은 자연어 주장보다 **규칙 집합(rule set)** 이다
- `normalize`는 v0.1에서 compare 내부 단계다
