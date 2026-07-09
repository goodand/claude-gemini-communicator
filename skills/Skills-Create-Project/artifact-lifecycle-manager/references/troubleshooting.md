# Troubleshooting — artifact-lifecycle-manager

## CASE-001: 파일명 timestamp는 맞는데 순서 검증이 실패함

**증상**: artifact order audit가 실패한다.
**원인**: 실제 생성/수정 metadata가 checklist보다 KB보다 더 앞선 순서를 따르지 않는다.
**해결**: 어떤 artifact가 나중에 만들어졌는지 metadata로 다시 확인하고 active file을 재정리한다.
**교훈**: 파일명 timestamp는 보조 신호고 최종 순서는 metadata가 결정한다.

## CASE-002: 내용이 같은 파일이 active tree에 둘 있음

**증상**: duplicate scan이 같은 hash group을 보고한다.
**원인**: rename 후 원본 active file을 남겨둔 채 새 파일도 유지했다.
**해결**: 새 파일을 유지하고, 같은 내용의 예전 active file은 삭제한다.
**교훈**: same-content duplicate는 legacy가 아니라 active cleanup 대상으로 본다.
