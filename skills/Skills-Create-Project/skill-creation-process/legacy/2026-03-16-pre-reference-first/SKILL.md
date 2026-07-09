---
name: skill-creation-process
description: >-
  Use this skill when creating a new Agent Skill from scratch or verifying
  an existing skill's structure against the standardized process.
  새 Agent Skill을 제작하거나 기존 skill의 구조 정합성을 검증할 때 사용한다.
---

# Skill Creation Process

반복되는 문제에서 출발하여, 표준 구조의 Agent Skill을 제작하는 정형화된 절차.

## When to use

- 새 Agent Skill을 처음부터 만들 때
- 기존 skill의 구조가 표준에 맞는지 검증할 때
- skill 제작 중 "다음에 뭘 해야 하지?" 싶을 때
- Codex 실전 테스트 후 결과를 정리할 때

## Workflow

1. **동기 정의 (Phase -1)** — 반복 문제 식별 → 목표 1문장 + 비목표 + 의존성 확정 (→ `references/phase-guide.md` Phase -1)
2. **자료 조사 (Phase 0)** — github-deep-research + 논문 탐색 → `knowledge_bases/`에 저장 (→ `references/phase-guide.md` Phase 0)
3. **Reference 분석 (Phase 1)** — `knowledge_bases/`를 읽어 task용 `references/`와 체크리스트로 정제 (→ `references/phase-guide.md` Phase 1)
4. **SKILL.md 작성 (Phase 2)** — ~45줄 lean 구조, Progressive Context Injection 적용 (→ `references/progressive-context-injection.md`)
5. **Scripts 작성 (Phase 3)** — 자동화 + 검증 + 추적, `--help` 필수 (→ `references/phase-guide.md` Phase 3)
6. **Evals 작성 (Phase 4)** — 4개 이상, mainline + edge case (→ `references/phase-guide.md` Phase 4)
7. **검증 (Phase 5)** — 정적 검증 → tmux+Codex 실전 → troubleshooting 기록 (→ `references/phase-guide.md` Phase 5)
8. **계획·린터 (Phase 6-7)** — 계획 버전화 + 구조적 제약 기계 강제 (→ `references/phase-guide.md` Phase 6-7)

## Scripts

- `quick_validate.py` — skill 구조 린트 (`python3 super-skill-creator/scripts/quick_validate.py <skill-dir>`)
- `skill_smoke_test.py` — evals 스모크 테스트 (`python3 super-skill-creator/scripts/skill_smoke_test.py <skill-dir>`)

## References

- `references/progressive-context-injection.md` — 3-Layer 설계 원리, 링크 규칙, 왜 이렇게 하는가
- `references/phase-guide.md` — Phase -1~7 전체 상세 절차 + 산출물
- `references/skill-directory-structure.md` — 필수 디렉토리 구조 + troubleshooting 필수 규칙
- `references/anti-patterns.md` — 하지 말 것 목록 (절차/SKILL.md/Scripts/문서-코드 정합성)
- `references/practical-lessons.md` — 11개 스킬 구현에서 배운 실전 노하우 11가지
- `references/troubleshooting.md` — skill 제작 중 발견된 공통 버그·오류

## Notes

- **핵심 원리**: Progressive Context Injection — SKILL.md(~45줄) → scripts/(--help) → references/(깊은 컨텍스트) (→ `references/progressive-context-injection.md`)
- `knowledge_bases/`는 skill 제작·구체화용 조사 자산, `references/`는 skill 사용 시 task 수행용 문서
- 모든 skill에 `references/troubleshooting.md` 필수 — 린터가 검사 (→ `references/skill-directory-structure.md`)
- Phase -1(동기 정의) 없이 착수 금지 — 반복 문제에서 출발 (→ `references/anti-patterns.md`)
- 정적 검증만으로 완료 선언 금지 — Phase 5-2 tmux+Codex 실전 필수 (→ `references/phase-guide.md` Phase 5)
