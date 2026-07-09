# Troubleshooting — kb-checklist-pipeline

## CASE-001: branch를 늦게 결정해서 checklist가 섞임

**증상**: document branch와 implementation branch 항목이 한 checklist에 섞인다.
**원인**: artifact type을 KB 이후에 분기하지 않고 구현 단계에서 늦게 분기했다.
**해결**: branch index에서 먼저 `document_output` vs `implementation_output`을 고른다.
**교훈**: branch 결정은 implementation checklist 작성 전에 끝내야 한다.
