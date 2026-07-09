# Doc Code Sync Path Ready-For-Diff Execution Evidence Plan

## Scope

- skill: `doc-code-sync-checker`
- target: `doc-code-sync path rule`
- stage: `ready_for_diff`

## Inputs

- implementation checklist:
  - `doc-code-sync-checker/checklist-forimplementation/mismatch-semantics-implementation-checklist-at2026-03-16-22-36.md`
- contract diff basis:
  - `execution-contract-mapper/references/contract-diff-basis-smoke-at2026-03-17-01-40.json`
- pre-fix artifact:
  - `doc-code-sync-checker/references/typed-mismatch-path-rule-smoke-report-at2026-03-17-00-08.json`
- post-fix artifact:
  - `doc-code-sync-checker/references/typed-mismatch-path-rule-post-fix-smoke-report-at2026-03-17-00-08.json`

## Handoffs

1. `evidence-trace-auditor`
   - when: `now`
   - purpose: raw smoke를 evidence ledger와 support audit로 정규화
2. `baseline-diff-lab`
   - when: `now`
   - purpose: before/after diff와 reduction metric 계산
   - adapter: `baseline-diff-lab/scripts/metricize_smoke_report.py`

## Next Actions

1. pre/post artifact가 같은 execution target을 가리키는지 확인
2. 필요하면 raw smoke artifact를 metric artifact로 정규화
3. `baseline-diff-lab` planner로 diff artifact 이름을 고정
4. `baseline-diff-lab` compute로 before/after diff 계산

## JSON Artifact

- `doc-code-sync-path-ready-for-diff-execution-evidence-plan-at2026-03-17-08-51.json`
