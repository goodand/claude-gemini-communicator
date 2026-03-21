# Issue Evidence Storage Rule

- scope: `workspace-artifact-production-process`에서 smoke/test 중 발생한 issue, evidence, summary pointer의 저장 경계를 고정한다.
- purpose: raw evidence, human-readable issue narrative, entrypoint summary를 섞지 않고 반복 가능한 저장 구조로 유지한다.

## Layer 1: Execution Evidence

Store:
- `references/*-smoke-*.json`
- raw logs
- raw artifact files
- evidence ledger
- support audit

Rule:
- 실행 중 관측된 사실과 원본 산출물은 먼저 이 층에 남긴다.
- issue 해석 전에 raw evidence를 덮어쓰거나 요약만 남기지 않는다.

## Layer 2: Issue Narrative

Store:
- `references/troubleshooting.md`

Format:
- `CASE-XXX`
- `증상 -> 원인 -> 해결 -> 교훈`

Rule:
- 사람이 읽는 issue explanation과 lesson은 `troubleshooting.md`에 남긴다.
- raw evidence 경로나 smoke artifact 이름을 함께 적어 traceability를 유지한다.

## Layer 3: Entrypoint Surface

Store:
- `SKILL.md` `Notes`

Rule:
- entrypoint에는 해결된 규칙을 1줄만 올린다.
- 상세 설명은 `(→ references/troubleshooting.md CASE-XXX)` 포인터로 보낸다.

## Boundary

- `references/fixtures/`는 sample input/output bundle 계층이다.
- `references/fixtures/`는 per-run smoke issue, troubleshooting case, evidence ledger 저장소가 아니다.
- `knowledge_bases/`는 채택된 설계와 takeaways를 두는 층이며 per-run issue를 직접 저장하지 않는다.
- `checklist`는 판정 항목 층이며 raw evidence를 저장하지 않는다.

## Escalation

- 같은 issue pattern이 반복되면 validator/code rule로 승격한다.
- cross-skill 반복 이슈면 `references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md`에 묶는다.
- reusable lesson을 KB insight로 올릴 때는 `references/evidence-promotion-pattern-at2026-03-17-03-45.md` 경로를 따른다.
