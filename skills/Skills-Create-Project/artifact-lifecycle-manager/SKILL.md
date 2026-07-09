---
name: artifact-lifecycle-manager
description: >-
  Lifecycle Migration family의 workflow owner. Use this skill when artifact
  backup, minute-level timestamp naming, metadata order validation,
  rename/move/delete/replace changes, or duplicate-content cleanup must be
  managed together — especially when directory structure migration and stale
  reference cleanup move in the same change.
---

# Artifact Lifecycle Manager

`legacy backup -> timestamp naming -> metadata order -> duplicate cleanup`를 고정한다.

## Do not use

- rule-bearing reference의 semantic recheck만 하면 될 때 → `doc-code-sync-checker`
- claim-heavy reference의 semantic recheck만 하면 될 때 → `claim-verifier`
- 새 artifact를 production order로 처음부터 만들 때 → `workspace-artifact-production-process`

## Family Roles

- owner:
  - `artifact-lifecycle-manager`
- direct-call specialists:
  - none (standalone owner)

## Workflow

1. **stale candidate 탐지** — `scripts/artifact_lifecycle_guard.py scan-stale-candidates`로 1차 후보 추출
2. **duplicate 정리** — `scan-duplicates`로 내용 동일 중복 식별 → 예전 active artifact 삭제
3. **naming/order 검증** — `check-order`로 생성 순서 확인, timestamp naming 규칙 감사
4. **backup + destructive 변경** — 내용이 달라지는 변경 전에만 legacy backup 생성 후 rename/move/delete 실행
5. **handoff** — semantic recheck가 필요한 건 doc-code-sync-checker 또는 claim-verifier로 넘김

## Read Order

1. `references/indexes/artifact-lifecycle-index-at2026-03-16-23-53.md`
2. `references/families/backup-and-naming-family-at2026-03-16-23-53.md`
3. `references/families/order-and-duplicate-family-at2026-03-16-23-53.md`
4. `knowledge_bases/artifact-lifecycle-manager-canonical-design-at2026-03-16-23-53.md`
5. `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-23-53.md`
6. `checklist-forimplementation/implementation-checklist-at2026-03-16-23-53.md`
7. 필요하면 `scripts/artifact_lifecycle_guard.py --help`

## Use When

- 파일명만 바뀐 중복 artifact를 정리할 때
- 삭제/rename 전에 legacy backup 기준을 확인해야 할 때
- `knowledge_base -> consistency -> implementation` 생성 순서를 검증해야 할 때
- 분 단위 timestamp naming을 강제하거나 audit해야 할 때
- 코드 변경 뒤 reference/knowledge_base/checklist가 stale candidate인지 1차 탐지할 때

## Notes

- source of truth는 canonical KB다
- active artifact는 `*-atYYYY-MM-DD-HH-MM.md`를 따른다
- 생성 순서는 파일명보다 metadata를 우선한다
- 내용이 같은 예전 active artifact는 삭제하고 legacy 중복은 줄인다
- 내용이 달라지는 destructive 변경 전에만 legacy backup을 만든다
- `scripts/artifact_lifecycle_guard.py`는 order, duplicate, stale candidate를 검사한다 (`check-order` / `scan-duplicates` / `scan-stale-candidates` / `audit`)
- `reference freshness audit`의 1차 owner는 이 skill이다
- 이 skill은 timestamp, active artifact, lifecycle 기준으로 `candidate stale`만 올린다
- rule-bearing reference의 semantic recheck는 `doc-code-sync-checker`로 handoff한다
- claim-heavy reference의 semantic recheck는 `claim-verifier`로 handoff한다
