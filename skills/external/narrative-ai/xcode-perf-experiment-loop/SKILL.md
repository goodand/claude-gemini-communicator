---
name: xcode-perf-experiment-loop
description: Use when running repeated iOS/Xcode performance experiments for this repo, especially 5-run launch measurements, Xcode simulator timing, idb-based permission automation, cumulative delay analysis, amplified delay analysis, or minute-stamped perf notes. Triggers on requests like "Xcode speed test", "5회 측정", "launch_to_carousel_ms", "누적 지연", "증폭 지연", "idb tap", "simulator permission automation", and "perf experiment loop".
---

# Xcode Perf Experiment Loop

Use this skill for repeated simulator performance experiments in this repo.

## When to use

Use it when the user wants to:
- measure `launch_to_carousel_ms` or similar launch KPIs
- repeat the same Xcode simulator experiment 3 to 5 times
- automate simulator permission popups with `idb`
- compare before/after latency on an experiment branch
- analyze cumulative delay or amplified delay from `summary.tsv`
- write a minute-stamped note under `test_log/`

Do not use it for:
- architecture-only reviews with no runtime measurement
- backend-only latency analysis without iOS simulator runs
- one-off UI bug fixes unrelated to timing

## Default workflow

1. Work from an isolated branch or worktree. Prefer a stable base branch for new experiments.
2. Instrument only the critical path. Keep launch-path metrics explicit in JS and native logs.
3. Reuse existing measurement scripts if the branch already contains them. For the current repo, look for `test_log/scripts/run_perf_trace_measurements.sh` before creating new automation.
4. Use Xcode/iOS runtime as the source of truth. Browser tools are only for secondary breakdowns.
5. If simulator permission popups block the run, prefer `idb` screenshot + AX tree + tap automation rather than manual clicking.
6. Collect at least 5 runs unless the user explicitly asks for fewer.
7. Analyze `summary.tsv` with `scripts/analyze_summary_tsv.py` in this skill.
8. Write a minute-stamped result note in `test_log/` with:
   - branch/worktree
   - exact command path
   - p50/p95/max
   - dominant cumulative delay
   - amplified delay source
   - pass/fail against target KPI
9. Do not commit local helper artifacts unless the user asks. Usually exclude:
   - `Podfile` or `Podfile.lock` path rewrites
   - `node_modules` symlinks
   - raw run directories under `test_log/`

## Files to read when needed

- `references/workflow.md`
  - Read when preparing a new experiment branch, choosing tools, or deciding what to commit.
- `references/metrics.md`
  - Read when interpreting `summary.tsv`, calculating p50/p95/max, or classifying cumulative vs amplified delay.

## Scripts

- `scripts/analyze_summary_tsv.py`
  - Use this to turn a `summary.tsv` file into a concise metric report.
  - Example:
    - `python scripts/analyze_summary_tsv.py path/to/summary.tsv`
    - `python scripts/analyze_summary_tsv.py path/to/summary.tsv --json`

## Output checklist

Every experiment summary should state:
- branch and worktree
- experiment goal
- run count
- p50, p95, max
- whether target KPI passed
- dominant critical-path spans
- cumulative delay finding
- amplified delay finding
- recommended next change

