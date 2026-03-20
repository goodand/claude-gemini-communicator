---
name: workspace-artifact-production-process
description: >-
  Use this skill when producing reusable workspace artifacts such as
  markdown docs, scripts, checklists, knowledge bases, references,
  smoke outputs, and bounded code through a standardized process.
  문서, 스크립트, 체크리스트, KB, 레퍼런스, smoke 산출물, 제한된 코드까지
  포함하는 workspace artifact 생산 절차에 사용한다.
---

# Workspace Artifact Production Process

반복되는 문제에서 출발하여, workspace 전반의 재사용 가능한 artifact를 생산하는 정형화된 절차.

## When to use

- 새 skill, agent artifact, 문서 세트, reference bundle을 처음부터 만들 때
- 기존 workspace artifact의 구조가 표준 production order에 맞는지 검증할 때
- MD, KB, checklist, reference, script, smoke artifact를 함께 정리해야 할 때
- Codex 실전 테스트 후 결과를 재사용 가능한 artifact로 남길 때

## Workflow

1. **의도 파악 + HITL (Phase -2~-1)** — 사용자 의도 확인 → human-in-the-loop 포인트 → 목표/비목표/의존성 고정 (→ `references/phase-guide.md` Phase -2~-1)
2. **자료 조사 + Reference 저장 (Phase 0)** — 기본은 외부 조사, 명시 요청 시 `internal_codebase_only`로 분기 후 `references/`에 원자료 저장 (→ `references/phase-guide.md` Phase 0)
3. **Knowledge Base 저장 (Phase 1)** — `references/`를 구조화·정리해 `knowledge_bases/`에 저장 (→ `references/phase-guide.md` Phase 1)
4. **KB 분석 + 정합성 checklist (Phase 2)** — `knowledge_bases/` 기반 정합성 평가용 checklist 작성 (→ `references/phase-guide.md` Phase 2)
5. **구현용 checklist + TDD (Phase 3)** — consistency checklist를 구현 항목과 테스트 계획으로 내림 (→ `references/phase-guide.md` Phase 3)
6. **Codebase 작성 (Phase 4)** — SKILL.md, scripts, evals 작성. 구현 파일을 만들면 TDD 파일도 같이 만든다 (→ `references/phase-guide.md` Phase 4)
7. **Smoke Test + Reference 갱신 (Phase 5)** — 정적 검증 → 실전 smoke test → 실험 결과 기반 `references/` 보강 (→ `references/phase-guide.md` Phase 5)
8. **계획·린터 (Phase 6)** — 계획 버전화 + 구조적 제약 기계 강제 (→ `references/phase-guide.md` Phase 6)

## Details

- `Scripts`, `References`, `Notes` 상세는 [references/skill-entrypoint-details-at2026-03-18-23-32.md](references/skill-entrypoint-details-at2026-03-18-23-32.md)
- MD 작성 규칙과 재사용 노하우는 [references/markdown-artifact-writing-patterns-at2026-03-20-14-13.md](references/markdown-artifact-writing-patterns-at2026-03-20-14-13.md)
- split 기준은 entrypoint 경량화만이며, 상세 내용은 그대로 분리했다
- subagent 작업은 [references/subagent-preservation-rule-at2026-03-19-21-34.md](references/subagent-preservation-rule-at2026-03-19-21-34.md) 의 preservation-first rule을 기본 계약으로 쓴다
- canonical skill name은 `workspace-artifact-production-process`로 보되, 디렉토리 경로 `skill-creation-process/`는 호환성을 위해 유지한다
