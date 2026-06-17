# Bridge: skill-creation-process -> artifact-lifecycle-manager

## Use This Bridge When

- active artifact를 rename, replace, delete 하려 한다
- legacy backup 필요 여부를 먼저 판단해야 한다
- `knowledge_base -> consistency -> implementation` 생성 순서를 다시 검증해야 한다
- 같은 내용의 예전 active artifact를 정리해야 한다

## Handoff Condition

- 변경 대상이 이미 active tree에 있다
- naming, metadata order, duplicate 여부를 같이 확인해야 한다
- cleanup이 단순 편집이 아니라 lifecycle decision에 가깝다

## Handoff Payload

- target skill: `artifact-lifecycle-manager`
- 필요한 입력:
  - target skill directory
  - 바꾸려는 active artifact 경로
  - legacy 포함 여부
  - lifecycle 작업 종류 (`backup`, `rename`, `delete`, `duplicate cleanup`)

## Recommended Sequence

1. `artifact-lifecycle-manager/scripts/artifact_lifecycle_guard.py audit --skill-dir <skill-dir>`
2. 필요하면 duplicate scan 결과 확인
3. legacy backup 필요 여부 결정
4. rename/delete/cleanup 실행

## Next Read

1. [artifact-lifecycle-manager/SKILL.md](../../artifact-lifecycle-manager/SKILL.md)
2. [artifact-lifecycle-manager-canonical-design-at2026-03-16-23-53.md](../../artifact-lifecycle-manager/knowledge_bases/artifact-lifecycle-manager-canonical-design-at2026-03-16-23-53.md)
3. [artifact_lifecycle_guard.py](../../artifact-lifecycle-manager/scripts/artifact_lifecycle_guard.py)
