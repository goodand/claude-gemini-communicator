---
name: execution-contract-mapper
description: >-
  design-planning-orchestrator family의 execution-contract specialist. Use
  this skill when concept-space outputs must be converted into stable execution
  contracts such as checklists, JSON schema, CLI contracts, function
  signatures, or rule schemas. broader multi-concern planning은
  design-planning-orchestrator를 사용하라.
---

# Execution Contract Mapper

개념 공간을 agent가 따를 수 있는 실행 계약으로 낮추는 스캐폴드.

## When to use

- knowledge_base를 checklist, schema, CLI contract로 내릴 때
- codebase가 따라야 할 최소 계약을 고정할 때
- rule schema와 출력 계약을 먼저 정의할 때

## Workflow

1. `knowledge_bases/execution-contract-mapper-knowledge_base-at2026-03-17-00-44.md`의 `Canonical Design Takeaways`를 source of truth로 읽는다
2. `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-17-01-00.md`로 무엇이 맞아야 하는지 먼저 고정한다
3. `checklist-forimplementation/implementation-checklist-at2026-03-17-01-00.md`로 첫 slice를 `rule_schema`로 내린다
4. 이후 script/TDD/smoke는 그 contract를 codebase와 대조 가능한 형태로 출력한다

## Knowledge Bases

- `knowledge_bases/execution-contract-mapper-knowledge_base-at2026-03-17-00-44.md` — 공식 spec/doc 조사 자산과 canonical slice를 함께 담는 hybrid_kb
- `knowledge_bases/execution-contract-mapper-issues-at2026-03-16.md` — 현재 이슈와 필요성

## Checklists

- `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-17-01-00.md` — 정합성 평가 기준
- `checklist-forimplementation/implementation-checklist-at2026-03-17-01-00.md` — 첫 구현 slice를 `rule_schema`로 내리는 작업 기준

## Scripts

- `scripts/execution_contract_mapper.py` — consistency checklist를 `rule_schema` artifact로 변환
- `scripts/execution_contract_mapper.py emit-schema-contract` — `rule_schema` artifact의 JSON Schema 계약을 생성
- `scripts/execution_contract_mapper.py emit-cli-contract` — mapper script의 CLI surface를 machine-readable contract로 생성
- `scripts/execution_contract_mapper.py emit-contract-diff-basis` — stable contract artifact 묶음을 future diff consumer가 읽을 diff basis로 정규화
- `scripts/test_execution_contract_mapper.py` — 첫 vertical slice TDD

## References

- `references/troubleshooting.md` — 구현/실험 중 나온 반복 버그 기록
- `references/execution-evidence-bridge-at2026-03-17-04-03.md` — contract artifact를 구현/evidence loop로 넘기는 handoff

## Notes

- v0.1 slice `rule_schema`, `schema_contract`, `cli_contract`, `contract_diff_basis`까지 구현됐다
- semantic-slice-mapper와 evidence-trace-auditor의 중간층이며, 구현 단계 handoff는 `references/execution-evidence-bridge-at2026-03-17-04-03.md`를 따른다
