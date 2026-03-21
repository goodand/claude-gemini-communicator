# Graphviz Notes

## Target
- KB: `knowledge_bases/codebase-analysis-3layer-production-kb-at2026-03-20-17-21.md`
- checklist: `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-20-17-21.md`

## Graph Intent
- show the 3-layer model
- show the procedural agent flow
- show artifact gates between steps
- show class policy and lint/static enforcement as cross-cutting rules
- show backtrack paths explicitly

## Source File
- `references/graphviz/codebase-analysis-3layer-kb-at2026-03-20-17-32.dot`

## Rendering Example
```bash
cd /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis

dot -Tsvg references/graphviz/codebase-analysis-3layer-kb-at2026-03-20-17-32.dot \
  -o references/graphviz/codebase-analysis-3layer-kb-at2026-03-20-17-32.svg
```
