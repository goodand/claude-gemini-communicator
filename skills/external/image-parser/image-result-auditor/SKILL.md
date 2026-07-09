---
name: image-result-auditor
description: Audit completed image jobs and export frozen comparison bundles from evidence-backed records. Use when you need approval candidates, retry candidates, comparison summaries, or auto-eval outputs without mutating upstream artifacts.
---

# Image Result Auditor

## Overview

Use this skill after worker completion or bundle freeze to turn evidence-backed records into review-ready queues, comparison summaries, and auto-eval outputs.
It owns audit and consumer preparation only. It does not mutate files, regenerate upstream arms, or approve items without evidence.

## Use This Skill When

- worker records already exist
- a human review queue must be prepared
- rename or metadata conflicts must be detected before commit
- frozen per-image comparison bundles already exist
- a downstream consumer must compare arms or run proxy auto-eval without regenerating ledgers

## Required MCPs

- `agent-task-manager`
- `conport`

## Optional MCPs

- `filesystem`
- `exiftool`

## Not Owned Here

- worker execution
- file rename or metadata commit
- human approval
- cross-tool speculative repair
- arm regeneration
- context package mutation
- semantic judge implementation
- iterative reinjection, baseline comparison, pending closure → `multimodal-evidence-refinement-loop`
- review surface layout, machine-truth manifest split → `image-text-cot-review`

## References

- `references/runtime.md`
- `references/troubleshooting.md`
- `references/review-queue-contract.md`
- `references/comparison-consumer-runtime.md`
- `references/frozen-bundle-contract.md`
- `references/semantic-judge-waiver.md`
- `checklists/audit-preflight.md`
- `checklists/four-mode-consumer-readiness.md`
- `knowledge_bases/image-result-auditor-knowledge-base-at2026-03-28-11-20.md`
- `knowledge_bases/image-result-auditor-comparison-consumer-knowledge-base-at2026-03-29-00-30.md`
- `evals/evals.json`
