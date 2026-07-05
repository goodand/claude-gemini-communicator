# Image Result Auditor Knowledge Base

- recorded_at: `2026-03-28`

## Purpose

`image-result-auditor` translates worker evidence into human-reviewable queue decisions without crossing into file mutation or human approval.

## Why This Skill Exists

- worker completion does not automatically mean review readiness
- approval and retry boundaries depend on evidence quality, not just row status
- rename and metadata conflicts should be surfaced before commit time, not during commit time

## Proven Invariants

- approval-ready requires evidence-backed completion
- retry and hold must remain separate
- audit decisions should be reconstructible from canonical artifacts

## Benchmark Relevance

This skill participates in orchestration quality because it decides whether evidence is sufficient to advance the pipeline. Its eval layer should stay compatible with benchmark metrics used for tool-use and packetized workflows.
