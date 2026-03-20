# Workspace Artifact Production Process Entry Details

- entrypoint page: [../SKILL.md](../SKILL.md)
- 이 문서는 `SKILL.md`에서 분리한 `Scripts`, `References`, `Notes` 상세 페이지다.
- canonical skill name은 `workspace-artifact-production-process`이며, 디렉토리 경로는 `skill-creation-process/`를 유지한다.

## Scripts

- `quick_validate.py` — skill 구조 린트 (`python3 super-skill-creator/scripts/quick_validate.py <skill-dir>`)
- `skill_smoke_test.py` — evals 스모크 테스트 (`python3 super-skill-creator/scripts/skill_smoke_test.py <skill-dir>`)
- `scripts/verify_artifact_order.py` — `knowledge_base -> consistency -> implementation` 생성 순서/분 단위 파일명 검증
- `scripts/execution_evidence_planner.py` — execution contract를 smoke/evidence/diff 단계로 넘기는 handoff plan 생성
- `scripts/execution_handoff_validator.py` — planner payload가 downstream handoff contract와 맞는지 검증
- `scripts/skill_portability_audit.py` — 다른 workspace 설치 전 `internal / bridge / external_dependency` 계층 audit
- `scripts/catalog_lookup.py` — `TASK-*`, `ISSUE-*`, `SKILL-*`, `LINK-*`, `JOIN-*` JSON catalog lookup/search

## References

- `references/progressive-context-injection.md` — 3-Layer 설계 원리, 링크 규칙, 왜 이렇게 하는가
- `references/markdown-artifact-writing-patterns-at2026-03-20-14-13.md` — MD, KB, checklist, reference 문서를 쓸 때 재사용할 writing rules 집약본
- `references/phase-guide.md` — Phase -1~7 전체 상세 절차 + 산출물
- `references/reference-acquisition-modes-at2026-03-17-09-35.md` — `external_research`와 `internal_codebase_only` 분기 규칙
- `references/portable-skill-hierarchy-rules-at2026-03-17-09-22.md` — portable install을 위한 link/bridge 계층 규칙
- `references/execution-evidence-pattern-at2026-03-17-04-03.md` — 실행 계약을 smoke/evidence/audit/diff로 내리는 공용 패턴
- `references/vertical-slice-execution-handoff-validator-at2026-03-18-22-52.md` — planner payload handoff schema validator slice
- `references/evidence-promotion-pattern-at2026-03-17-03-45.md` — 실험 결과를 KB insight로 승격하는 공용 파이프라인
- `references/vertical-slice-static-dependency-overlay-contract-at2026-03-19-14-14.md` — static dependency overlay contract slice
- `references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md` — 최근 반복 작업/이슈와 공용 process vs 개별 skill 경계 정리
- `references/subagent-task-and-trouble-patterns-at2026-03-20-02-48.md` — subagent handoff에서 반복된 bounded task / trouble pattern 정리
- `references/task-to-skill-mapping-at2026-03-19-13-55.md` — repeated task key로 관련 skill과 page linker를 찾는 lookup page
- `references/catalog/` — machine-searchable JSON catalogs (`tasks`, `issues`, `skills`, `links`, `joins`, `manifest`)
- `references/artifact-lifecycle-bridge-at2026-03-16-23-58.md` — rename/delete/cleanup이 나오면 `artifact-lifecycle-manager`로 넘기는 handoff
- `references/intent-and-reference-analysis-details.md` — 의도 파악/Reference 분석의 세부 기준 보존
- `references/skill-directory-structure.md` — 필수 디렉토리 구조 + troubleshooting 필수 규칙
- `references/anti-patterns.md` — 하지 말 것 목록 (절차/SKILL.md/Scripts/문서-코드 정합성)
- `references/practical-lessons.md` — 11개 스킬 구현에서 배운 실전 노하우 11가지
- `references/troubleshooting.md` — skill 제작 중 발견된 공통 버그·오류

## Notes

- **핵심 원리**: Progressive Context Injection — SKILL.md(~45줄) → scripts/(--help) → references/(깊은 컨텍스트) (→ `references/progressive-context-injection.md`)
- `quick_validate`에서 SKILL.md line-count warning이 나오면 내용을 억지로 줄이기보다 자연스러운 split point를 찾아 별도 파일로 옮기고, entrypoint에는 링크만 남긴다
- `references/`는 가장 넓은 문서 층 — 조사 원자료, task 문서, 실험 후 보강 문서까지 포함
- `knowledge_bases/`는 `references/`를 구조화·정리한 중간 지식층
- 모든 skill에 `references/troubleshooting.md` 필수 — 린터가 검사 (→ `references/skill-directory-structure.md`)
- Phase -1(동기 정의) 없이 착수 금지 — 반복 문제에서 출발 (→ `references/anti-patterns.md`)
- 정적 검증만으로 완료 선언 금지 — Phase 5-2 tmux+Codex 실전 필수 (→ `references/phase-guide.md` Phase 5)
- 외부 조사 없이 local 정합성 기반으로 MD/코드를 써야 하면 `references/reference-acquisition-modes-at2026-03-17-09-35.md`의 `internal_codebase_only`를 명시적으로 활성화한다
- 다른 workspace 배포 전에는 `references/portable-skill-hierarchy-rules-at2026-03-17-09-22.md` 기준으로 portability audit를 먼저 남긴다
- active artifact rename/delete/cleanup은 직접 처리하지 말고 lifecycle 판단이 필요하면 `references/artifact-lifecycle-bridge-at2026-03-16-23-58.md`를 따라 `artifact-lifecycle-manager`로 넘긴다
