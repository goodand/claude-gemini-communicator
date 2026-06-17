# Artifact Lifecycle Family: backup-and-naming

## Backup Rule

- destructive rename/delete 전에만 legacy backup을 만든다
- 새 파일이 기존 파일과 내용이 같으면 legacy backup 대신 active duplicate를 정리한다
- legacy folder는 작업 시점 timestamp로 만든다

## Naming Rule

- active markdown artifact는 `*-atYYYY-MM-DD-HH-MM.md`
- timestamp는 생성 순서를 읽는 보조 수단이고, 최종 판정은 metadata다
- issue memo나 임시 초안도 active artifact면 같은 규칙을 따른다
