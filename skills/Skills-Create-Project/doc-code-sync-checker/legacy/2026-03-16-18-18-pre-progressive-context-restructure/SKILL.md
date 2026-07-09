---
name: doc-code-sync-checker
description: >-
  Use this skill when reference documents define rules, fields, transitions, or
  constraints that must exist in code — extracts documented rules, compares them
  with validate logic, and reports document-code drift.
  문서에 적힌 규칙과 코드 구현의 정합성을 검사하고 drift를 보고한다.
---

# Doc-Code Sync Checker

reference 문서의 규칙을 추출하고 validate/상수/테이블 구현과 대조하여 drift를 찾는다.

## When to use

- field reference와 validate 함수가 일치하는지 확인할 때
- 상태 전이표, enum, 경로 규칙이 코드에 반영됐는지 검사할 때
- "문서에 썼지만 코드에 없음" 유형의 버그를 사전 차단할 때
- troubleshooting의 정합성 패턴을 재검증할 때

## Workflow

1. **문서 규칙 추출** — `scripts/doc_code_sync.py extract-doc --doc <file>` → 규칙/제약/전이 목록 추출
2. **코드 규칙 추출** — `scripts/doc_code_sync.py extract-code --script <file>` → validate/상수 기반 규칙 추출
3. **비교** — `scripts/doc_code_sync.py compare --doc-rules <json> --code-rules <json>` → missing/extra/mismatch 분류
4. **보고** — `scripts/doc_code_sync.py report --results <results.json>` → drift와 수정 권고 출력

## Scripts

- `scripts/doc_code_sync.py` — extract-doc/extract-code/compare/report 스캐폴드. `python3 scripts/doc_code_sync.py --help`

## References

- `references/sync-targets.md` — 비교 대상 유형
- `references/sync-checklist.md` — 문서-코드 정합성 체크리스트
- `references/troubleshooting.md` — drift 실전 사례

## Knowledge Bases

- `knowledge_bases/doc-code-sync-checker-knowledge_base-at2026-03-16.md` — GitHub 조사 URL KB

## Notes

- 시작점은 항상 **reference 문서 규칙** 또는 **validate 구현 규칙** 둘 중 하나를 명시한다
- 다이어그램, 표, 상수 dict는 서로 다른 표현이지만 같은 계약일 수 있다
- claim-verifier와 달리 시작점은 자연어 주장보다 **규칙 집합(rule set)** 이다
- mismatch와 unverifiable을 분리해서 보고한다
