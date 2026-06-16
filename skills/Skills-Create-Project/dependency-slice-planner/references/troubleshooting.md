# dependency-slice-planner troubleshooting

## Current Notes

- source of truth는 `knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md` 하나로 고정한다.
- thin KB는 redirect note일 뿐, 별도 canonical source로 다시 읽지 않는다.
- `context-links`는 task-local artifact appendix라서 canonical KB보다 먼저 읽지 않는다.
- planner는 graph extractor나 final launcher가 아니다.
