# Bridge: execution-contract-mapper -> implementation/evidence loop

## Use This Bridge When

- `rule_schema`, `schema_contract`, `cli_contract`, `contract_diff_basis`가 준비됐다
- 이제 contract-aware 구현/TDD/smoke/evidence 단계로 넘어가야 한다

## Handoff Payload

- implementation checklist path
- `rule_schema` artifact path
- `schema_contract` artifact path
- `cli_contract` artifact path
- `contract_diff_basis` artifact path
- target fixture 또는 pair

## Recommended Order

1. implementation checklist에 따라 TDD를 먼저 작성
2. 구현 후 raw smoke artifact를 남긴다
3. `evidence-trace-auditor`로 smoke를 ledger/audit로 정규화한다
4. fix 효과를 주장해야 하면 `baseline-diff-lab`으로 before/after diff를 계산한다
5. reusable lesson이면 `evidence-to-knowledge-promoter`로 넘긴다

## Next Read

1. [execution_evidence_planner.py](../../skill-creation-process/scripts/execution_evidence_planner.py)
2. [KB Checklist Pipeline](../../kb-checklist-pipeline/SKILL.md)
3. [implementation_output branch](../../kb-checklist-pipeline/references/families/implementation-output-branch-at2026-03-16-23-11.md)
4. [Evidence Trace Auditor](../../evidence-trace-auditor/SKILL.md)
5. [Baseline Diff Lab](../../baseline-diff-lab/SKILL.md)
6. [Execution Contract To Evidence Pattern](../../skill-creation-process/references/execution-evidence-pattern-at2026-03-17-04-03.md)
