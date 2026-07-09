# Troubleshooting — doc-code-sync-checker

## CASE-001: 다이어그램과 테이블을 다른 계약으로 오해

- **증상**: 같은 상태 머신을 표현한 다이어그램과 전이 테이블을 별개 규칙으로 취급하여 false mismatch 발생
- **원인**: 시각 표현과 구조화 표현의 동등성 판단이 없음
- **해결법**: 비교 전에 규칙을 정규화하여 공통 transition tuple로 변환
- **교훈**: doc-code-sync-checker의 핵심은 문자열 비교가 아니라 계약 정규화다
