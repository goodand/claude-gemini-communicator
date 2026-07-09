# Skill Portability Audit

- workspace_root: `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project`

## Summary

- `internal`: `83`
- `bridge`: `20`
- `external_dependency`: `10`
- `outside_workspace`: `0`
- `absolute_path`: `59`
- `missing`: `0`

## Skills

### skill-creation-process

- `internal`: `0`
- `bridge`: `3`
- `external_dependency`: `0`
- `outside_workspace`: `0`
- `absolute_path`: `6`
- `missing`: `0`
- notable findings:
  - `bridge`: `references/artifact-lifecycle-bridge-at2026-03-16-23-58.md` -> `../../artifact-lifecycle-manager/SKILL.md` (artifact-lifecycle-manager)
  - `bridge`: `references/artifact-lifecycle-bridge-at2026-03-16-23-58.md` -> `../../artifact-lifecycle-manager/knowledge_bases/artifact-lifecycle-manager-canonical-design-at2026-03-16-23-53.md` (artifact-lifecycle-manager)
  - `bridge`: `references/artifact-lifecycle-bridge-at2026-03-16-23-58.md` -> `../../artifact-lifecycle-manager/scripts/artifact_lifecycle_guard.py` (artifact-lifecycle-manager)
  - `absolute_path`: `references/evidence-promotion-pattern-at2026-03-17-03-45.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-to-knowledge-promoter/SKILL.md` (absolute_path)
  - `absolute_path`: `references/evidence-promotion-pattern-at2026-03-17-03-45.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-to-knowledge-promoter/references/vertical-slice-apply-hybrid-kb-patch-at2026-03-17-03-27.md` (absolute_path)
  - `absolute_path`: `references/evidence-promotion-pattern-at2026-03-17-03-45.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-to-knowledge-promoter/references/vertical-slice-canonical-candidate-evaluator-at2026-03-17-03-36.md` (absolute_path)
  - `absolute_path`: `references/evidence-promotion-pattern-at2026-03-17-03-45.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-to-knowledge-promoter/references/vertical-slice-hybrid-kb-patch-plan-at2026-03-17-03-20.md` (absolute_path)
  - `absolute_path`: `references/evidence-promotion-pattern-at2026-03-17-03-45.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-to-knowledge-promoter/references/vertical-slice-promotion-summary-at2026-03-17-03-08.md` (absolute_path)

### kb-checklist-pipeline

- `internal`: `4`
- `bridge`: `4`
- `external_dependency`: `0`
- `outside_workspace`: `0`
- `absolute_path`: `0`
- `missing`: `0`
- notable findings:
  - `bridge`: `references/families/baseline-diff-bridge-at2026-03-16-23-17.md` -> `../../../baseline-diff-lab/SKILL.md` (baseline-diff-lab)
  - `bridge`: `references/families/baseline-diff-bridge-at2026-03-16-23-17.md` -> `../../../baseline-diff-lab/knowledge_bases/baseline-diff-lab-canonical-design-at2026-03-16-23-17.md` (baseline-diff-lab)
  - `bridge`: `references/families/baseline-diff-bridge-at2026-03-16-23-17.md` -> `../../../baseline-diff-lab/references/indexes/baseline-diff-index-at2026-03-16-23-17.md` (baseline-diff-lab)
  - `bridge`: `references/families/implementation-output-branch-at2026-03-16-23-11.md` -> `../../../skill-creation-process/references/execution-evidence-pattern-at2026-03-17-04-03.md` (skill-creation-process)
  - `internal`: `references/families/implementation-output-branch-at2026-03-16-23-11.md` -> `./baseline-diff-bridge-at2026-03-16-23-17.md` (kb-checklist-pipeline)
  - `internal`: `references/indexes/kb-checklist-pipeline-branch-index-at2026-03-16-23-11.md` -> `../../knowledge_bases/kb-checklist-pipeline-canonical-design-at2026-03-16-23-11.md` (kb-checklist-pipeline)
  - `internal`: `references/indexes/kb-checklist-pipeline-branch-index-at2026-03-16-23-11.md` -> `../families/document-output-branch-at2026-03-16-23-11.md` (kb-checklist-pipeline)
  - `internal`: `references/indexes/kb-checklist-pipeline-branch-index-at2026-03-16-23-11.md` -> `../families/implementation-output-branch-at2026-03-16-23-11.md` (kb-checklist-pipeline)

### execution-contract-mapper

- `internal`: `2`
- `bridge`: `6`
- `external_dependency`: `0`
- `outside_workspace`: `0`
- `absolute_path`: `17`
- `missing`: `0`
- notable findings:
  - `internal`: `knowledge_bases/execution-contract-mapper-knowledge_base-at2026-03-17-00-44.md` -> `../SKILL.md` (execution-contract-mapper)
  - `internal`: `knowledge_bases/execution-contract-mapper-knowledge_base-at2026-03-17-00-44.md` -> `./execution-contract-mapper-issues-at2026-03-16.md` (execution-contract-mapper)
  - `absolute_path`: `references/execution-contract-mapper-metrics-evaluation-at2026-03-17-01-35.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/checklist-forconsistency-evaluation/consistency-checklist-at2026-03-17-01-00.md` (absolute_path)
  - `absolute_path`: `references/execution-contract-mapper-metrics-evaluation-at2026-03-17-01-35.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/knowledge_bases/execution-contract-mapper-knowledge_base-at2026-03-17-00-44.md` (absolute_path)
  - `absolute_path`: `references/execution-contract-mapper-metrics-evaluation-at2026-03-17-01-35.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/references/cli-contract-smoke-at2026-03-17-01-29.json` (absolute_path)
  - `absolute_path`: `references/execution-contract-mapper-metrics-evaluation-at2026-03-17-01-35.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/references/rule-schema-smoke-at2026-03-17-01-06.json` (absolute_path)
  - `absolute_path`: `references/execution-contract-mapper-metrics-evaluation-at2026-03-17-01-35.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/references/schema-contract-smoke-at2026-03-17-01-11.json` (absolute_path)
  - `absolute_path`: `references/execution-contract-mapper-metrics-evaluation-at2026-03-17-01-41.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/checklist-forconsistency-evaluation/consistency-checklist-at2026-03-17-01-00.md` (absolute_path)

### doc-code-sync-checker

- `internal`: `30`
- `bridge`: `0`
- `external_dependency`: `10`
- `outside_workspace`: `0`
- `absolute_path`: `5`
- `missing`: `0`
- notable findings:
  - `internal`: `checklist-forconsistency-evaluation/applied-kb-code-review-at2026-03-16.md` -> `./consistency-checklist.md` (doc-code-sync-checker)
  - `internal`: `knowledge_bases/doc-code-sync-canonical-design-at2026-03-16-18-18.md` -> `../SKILL.md` (doc-code-sync-checker)
  - `internal`: `knowledge_bases/doc-code-sync-canonical-design-at2026-03-16-18-18.md` -> `../checklist-forconsistency-evaluation/consistency-checklist.md` (doc-code-sync-checker)
  - `internal`: `knowledge_bases/doc-code-sync-canonical-design-at2026-03-16-18-18.md` -> `../checklist-forimplementation/implementation-checklist.md` (doc-code-sync-checker)
  - `internal`: `knowledge_bases/doc-code-sync-canonical-design-at2026-03-16-18-18.md` -> `../references/indexes/doc-code-sync-family-index-at2026-03-16-18-18.md` (doc-code-sync-checker)
  - `internal`: `knowledge_bases/doc-code-sync-canonical-design-at2026-03-16-18-18.md` -> `../scripts/doc_code_sync.py` (doc-code-sync-checker)
  - `external_dependency`: `knowledge_bases/doc-code-sync-checker-knowledge_base-at2026-03-16.md` -> `../../_shared/reference-inbox/claim-doc-sync-intent-from-jsonl-at2026-03-16.md` (external_dependency)
  - `external_dependency`: `knowledge_bases/doc-code-sync-checker-knowledge_base-at2026-03-16.md` -> `../../github-deep-research/references/doc-code-sync-checker-github-search-at2026-03-16.md` (external_dependency)

### evidence-trace-auditor

- `internal`: `2`
- `bridge`: `1`
- `external_dependency`: `0`
- `outside_workspace`: `0`
- `absolute_path`: `29`
- `missing`: `0`
- notable findings:
  - `internal`: `knowledge_bases/evidence-trace-auditor-knowledge_base-at2026-03-17-01-52.md` -> `../SKILL.md` (evidence-trace-auditor)
  - `internal`: `knowledge_bases/evidence-trace-auditor-knowledge_base-at2026-03-17-01-52.md` -> `./evidence-trace-auditor-issues-at2026-03-16.md` (evidence-trace-auditor)
  - `absolute_path`: `knowledge_bases/evidence-trace-auditor-knowledge_base-at2026-03-17-01-52.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/doc-code-sync-checker/references/typed-mismatch-enum-value-smoke-report-at2026-03-16-22-43.json` (absolute_path)
  - `absolute_path`: `knowledge_bases/evidence-trace-auditor-knowledge_base-at2026-03-17-01-52.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/references/contract-diff-basis-smoke-at2026-03-17-01-40.json` (absolute_path)
  - `bridge`: `references/evidence-promotion-bridge-at2026-03-17-03-52.md` -> `../../evidence-to-knowledge-promoter/references/evidence-promotion-handoff-at2026-03-17-08-57.md` (evidence-to-knowledge-promoter)
  - `absolute_path`: `references/evidence-promotion-bridge-at2026-03-17-03-52.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-to-knowledge-promoter/SKILL.md` (absolute_path)
  - `absolute_path`: `references/evidence-status-rules-at2026-03-17-02-36.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/SKILL.md` (absolute_path)
  - `absolute_path`: `references/vertical-slice-artifact-path-evidence-at2026-03-17-02-20.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/knowledge_bases/evidence-trace-auditor-knowledge_base-at2026-03-17-01-52.md` (absolute_path)

### baseline-diff-lab

- `internal`: `1`
- `bridge`: `3`
- `external_dependency`: `0`
- `outside_workspace`: `0`
- `absolute_path`: `1`
- `missing`: `0`
- notable findings:
  - `bridge`: `references/evidence-promotion-bridge-at2026-03-17-03-52.md` -> `../../evidence-to-knowledge-promoter/references/evidence-promotion-handoff-at2026-03-17-08-57.md` (evidence-to-knowledge-promoter)
  - `absolute_path`: `references/evidence-promotion-bridge-at2026-03-17-03-52.md` -> `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-to-knowledge-promoter/SKILL.md` (absolute_path)
  - `bridge`: `references/general-kb-fix-diff-at2026-03-16-23-41.md` -> `../../contract-to-concept-mapper/references/general-kb-baseline-measure-at2026-03-16-18-55.json` (contract-to-concept-mapper)
  - `bridge`: `references/general-kb-fix-diff-at2026-03-16-23-41.md` -> `../../contract-to-concept-mapper/references/general-kb-hybrid-final-at2026-03-16-18-59.json` (contract-to-concept-mapper)
  - `internal`: `references/indexes/baseline-diff-index-at2026-03-16-23-17.md` -> `../families/fix-diff-family-at2026-03-16-23-17.md` (baseline-diff-lab)

### evidence-to-knowledge-promoter

- `internal`: `18`
- `bridge`: `0`
- `external_dependency`: `0`
- `outside_workspace`: `0`
- `absolute_path`: `0`
- `missing`: `0`
- notable findings:
  - `internal`: `knowledge_bases/evidence-to-knowledge-promoter-knowledge_base-at2026-03-17-02-48.md` -> `../SKILL.md` (evidence-to-knowledge-promoter)
  - `internal`: `knowledge_bases/evidence-to-knowledge-promoter-knowledge_base-at2026-03-17-02-48.md` -> `../references/troubleshooting.md` (evidence-to-knowledge-promoter)
  - `internal`: `references/evidence-to-knowledge-promoter-hybrid-kb-hold-copy-at2026-03-17-03-27.md` -> `../SKILL.md` (evidence-to-knowledge-promoter)
  - `internal`: `references/evidence-to-knowledge-promoter-hybrid-kb-hold-copy-at2026-03-17-03-27.md` -> `../references/troubleshooting.md` (evidence-to-knowledge-promoter)
  - `internal`: `references/evidence-to-knowledge-promoter-hybrid-kb-patched-copy-at2026-03-17-03-27.md` -> `../SKILL.md` (evidence-to-knowledge-promoter)
  - `internal`: `references/evidence-to-knowledge-promoter-hybrid-kb-patched-copy-at2026-03-17-03-27.md` -> `../references/troubleshooting.md` (evidence-to-knowledge-promoter)
  - `internal`: `references/vertical-slice-apply-hybrid-kb-patch-at2026-03-17-03-27.md` -> `./evidence-to-knowledge-promoter-hybrid-kb-hold-copy-at2026-03-17-03-27.md` (evidence-to-knowledge-promoter)
  - `internal`: `references/vertical-slice-apply-hybrid-kb-patch-at2026-03-17-03-27.md` -> `./evidence-to-knowledge-promoter-hybrid-kb-patched-copy-at2026-03-17-03-27.md` (evidence-to-knowledge-promoter)

### contract-to-concept-mapper

- `internal`: `24`
- `bridge`: `3`
- `external_dependency`: `0`
- `outside_workspace`: `0`
- `absolute_path`: `1`
- `missing`: `0`
- notable findings:
  - `internal`: `knowledge_bases/contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md` -> `../SKILL.md` (contract-to-concept-mapper)
  - `internal`: `knowledge_bases/contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md` -> `../references/contract-to-concept-mapper-github-search-at2026-03-16.md` (contract-to-concept-mapper)
  - `internal`: `knowledge_bases/contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md` -> `../references/contract-to-concept-mapper-paper-search-at2026-03-16.md` (contract-to-concept-mapper)
  - `internal`: `knowledge_bases/contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md` -> `../references/measurement-strategy-from-eval-runner-rag-bench-at2026-03-16-18-47.md` (contract-to-concept-mapper)
  - `internal`: `knowledge_bases/contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md` -> `./contract-to-concept-canonical-design-at2026-03-16-18-06.md` (contract-to-concept-mapper)
  - `internal`: `knowledge_bases/contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md` -> `./contract-to-concept-mapper-issues-at2026-03-16.md` (contract-to-concept-mapper)
  - `internal`: `knowledge_bases/kb-to-consistency-check-knowledge_base-at2026-03-16-15-44.md` -> `../SKILL.md` (contract-to-concept-mapper)
  - `internal`: `knowledge_bases/kb-to-consistency-check-knowledge_base-at2026-03-16-15-44.md` -> `../references/kb-to-consistency-check-evaluation-criteria-at2026-03-16-15-44.md` (contract-to-concept-mapper)

### artifact-lifecycle-manager

- `internal`: `2`
- `bridge`: `0`
- `external_dependency`: `0`
- `outside_workspace`: `0`
- `absolute_path`: `0`
- `missing`: `0`
- notable findings:
  - `internal`: `references/indexes/artifact-lifecycle-index-at2026-03-16-23-53.md` -> `../families/backup-and-naming-family-at2026-03-16-23-53.md` (artifact-lifecycle-manager)
  - `internal`: `references/indexes/artifact-lifecycle-index-at2026-03-16-23-53.md` -> `../families/order-and-duplicate-family-at2026-03-16-23-53.md` (artifact-lifecycle-manager)
