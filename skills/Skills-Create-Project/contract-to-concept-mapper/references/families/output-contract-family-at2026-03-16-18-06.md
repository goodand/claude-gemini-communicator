# Output Contract Family

## Tags

- `concept_summary`
- `boundary_map`
- `semantic_relation_map`
- `mermaid`
- `pseudocode`
- `vector_secondary`

## Family Focus

- concept-space 출력은 사람이 읽을 수 있어야 한다
- Mermaid / pseudocode는 render target이다
- 벡터 값이나 vector DB는 보조 출력이다
- 출력은 traceability 없이 자연어만 남기지 않는다

## Script / Output Mapping

- current scripts:
  - `scripts/kb_to_consistency_check.py` — output contract가 KB/checklist에 반영되는지 간접 검사
- target outputs:
  - `concept summary`
  - `boundary description`
  - `semantic relation map`
  - optional `semantic index / vector manifest`

## Canonical Handoff

- 실제 출력 계약은 `knowledge_bases/contract-to-concept-canonical-design-at2026-03-16-18-06.md`를 기준으로 고정한다
