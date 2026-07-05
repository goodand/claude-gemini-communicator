# Image Worker Knowledge Base

- recorded_at: `2026-03-28`

## Purpose

`image-worker` exists to keep single-image execution isolated even when the surrounding pipeline is packetized and parallelized.

## Why This Skill Must Stay Narrow

- caption quality and evidence tracking become unreliable when one worker owns multiple rows
- dispatcher truthfulness depends on one worker owning one bounded ledger family
- later audit and commit stages need exact provenance for each image row

## Proven Invariants

- one worker should own one image row at a time
- MCP-backed state is the completion source of truth
- raw response JSON and execution records are first-class evidence, not optional side artifacts

## Benchmark Relevance

This skill is local and narrow, but it still participates in orchestration quality. Its eval layer should remain compatible with the benchmark scoring vocabulary used by dispatcher and other packetized skills.
