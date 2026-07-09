---
name: python-static-diagnostic-fixer
description: >-
  Use this skill when Python files show editor diagnostics such as Pylance,
  Pyright, or linter warnings and you must fix static issues without masking
  runtime behavior. Python 정적 진단을 런타임과 분리해 안전하게 정리한다.
---

# Python Static Diagnostic Fixer

Python red squiggle, Pylance, lint 경고를 런타임 오류와 분리해서 정리하는 스캐폴드.

## When to use

- VS Code/Pylance에 빨간 줄이 뜨는데 실제 런타임 오류인지 먼저 구분해야 할 때
- `unused import`, `unused variable`, `spec.loader is None` 같은 정적 경고를 안전하게 정리할 때
- 타입 힌트나 `from __future__ import annotations` 추가가 필요한지 판단할 때

## Workflow

1. `knowledge_bases/python-static-diagnostic-fixer-knowledge_base-at2026-03-17-01-18.md`의 `Canonical Design Takeaways`를 읽는다
2. `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-17-01-18.md`로 정적 진단 처리 순서를 먼저 고정한다
3. `checklist-forimplementation/implementation-checklist-at2026-03-17-01-18.md`로 첫 작업 단위를 정한다
4. 먼저 `py_compile`과 기존 테스트로 런타임 정상 여부를 확인한다
5. 그 다음 unused/typing/optional-guard 계열 수정만 적용한다

## Knowledge Bases

- `knowledge_bases/python-static-diagnostic-fixer-knowledge_base-at2026-03-17-01-18.md` — 반복된 정적 진단 수정 패턴의 hybrid KB

## Checklists

- `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-17-01-18.md`
- `checklist-forimplementation/implementation-checklist-at2026-03-17-01-18.md`

## References

- `references/troubleshooting.md`

## Scripts

- `scripts/diagnostic_audit.py` — 한 Python 파일을 대상으로 runtime gate와 safe-fix 후보를 구조화해 출력
- `scripts/test_diagnostic_audit.py` — `diagnostic_audit.py` TDD

## Notes

- 정적 진단 정리는 런타임 회귀를 만들지 않는 범위에서만 한다
- `py_compile`과 테스트가 먼저고, 에디터 경고 수습은 그 다음이다
