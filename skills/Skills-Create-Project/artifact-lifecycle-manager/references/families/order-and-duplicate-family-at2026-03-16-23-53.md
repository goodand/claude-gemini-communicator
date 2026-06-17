# Artifact Lifecycle Family: order-and-duplicate

## Order Rule

- 기본 chain은 `knowledge_base -> consistency checklist -> implementation checklist`
- sequence 판정은 `created`, 없으면 `modified` metadata를 쓴다
- 파일명 timestamp가 맞아도 metadata order가 틀리면 실패다

## Duplicate Rule

- active tree에 같은 내용의 markdown artifact가 둘 이상 있으면 정리 대상이다
- 같은 내용이고 파일명만 다른 예전 artifact는 active tree에서 삭제한다
- legacy는 보존층이라 duplicate scan에서 기본 제외할 수 있다

## Recommended Check

1. order audit
2. duplicate scan
3. 필요하면 legacy backup
4. rename/delete 실행
