---
name: async-migration-verify
description: >-
  Use this skill when sync-to-async migrations must be verified beyond "tests
  pass" for structural residue, UX regressions, and failure-path completeness.
---

# Async Migration Verify

sync→async 전환이 구조적으로 닫혔는지 검증하는 reusable verification skill.

## Use This Skill When

- file I/O 또는 save/load API가 async 경로로 전환됐을 때
- tests는 green이지만 migration completeness를 별도로 판단해야 할 때
- dead import, duplication, concurrency UX, TOCTOU, error path를 점검해야 할 때

## Do Not Use This Skill When

- async 전환이 없는 일반 버그 수정일 때
- business rule 자체를 검토하는 task일 때

## Read Order

1. `references/runtime.md`
2. `knowledge_bases/async-migration-verify-knowledge_base-at2026-04-08-00-15.md`
3. `checklist-forconsistency-evaluation/async-migration-consistency-checklist-at2026-04-08-00-16.md`
4. `checklist-forimplementation/async-migration-implementation-checklist-at2026-04-08-00-17.md`
5. `references/troubleshooting.md`
6. `scripts/scan_dead_imports.sh`
7. `scripts/scan_sync_async_duplication.sh`

## Scripts

- `scripts/scan_dead_imports.sh` — dead import와 alias form residue 수집
- `scripts/scan_sync_async_duplication.sh` — sync/async duplication drift 후보 수집

## Outputs

- 6-checkpoint verification verdict
- scanner findings
- follow-up implementation checklist

## Notes

- green tests는 충분조건이 아니다.
- concurrency guard는 visible feedback이 없으면 still-open이다.
- contract-heavy migration이면 absorbed rule lane까지 같이 점검한다.
