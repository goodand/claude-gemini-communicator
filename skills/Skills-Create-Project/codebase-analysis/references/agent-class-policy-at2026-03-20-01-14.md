# Agent Class Policy

## Purpose

Split agents by context reusability and interpretation risk.

## Class 1: Persistent Structural Agent

Definition:
- high context reusability
- low semantic drift
- large structural workload
- should retain context across repeated structure-analysis tasks

Examples:
- `dependency-graph-analyst`

Allowed:
- import / wrapper / runpy / `sys.path` / manifest collection
- graph updates
- node / edge / boundary artifact refresh

Disallowed:
- final synthesis
- broad policy judgment
- narrative-heavy interpretation
- unrelated task types outside the fixed structural remit

Rule:
- keep alive when the codebase structure is still the same working target
- enforce narrow task whitelist

## Class 2: Run-Scoped Interpretive Agent

Definition:
- meaning can drift across runs
- interpretation-heavy
- should accumulate context only for one analysis run

Examples:
- `dependency-risk-auditor`
- `reviewer`

Allowed:
- risk interpretation
- issue classification
- review findings
- repeated task / repeated issue documentation

Rule:
- write artifacts, then terminate
- do not carry broad prior-run memory into the next run

## Class 3: Artifact-Backed Synthesizer

Definition:
- reusable through artifact registries, not through long-lived codebase memory
- contradiction handling depends on evidence maps and finding registries

Examples:
- `synthesizer`

Allowed:
- merge worker summaries
- deduplicate findings
- resolve contradictions using artifact-backed evidence
- maintain canonical finding map and residual gap register

Rule:
- reuse contradiction/finding artifacts when available
- avoid becoming a second full-context structural explorer

## Linter / Static Handling Policy

- warning-heavy enforcement is useful for subagent discipline
- prefer enabling lint/static guard before subagent execution and disabling it after the coordinated run ends
- if runtime-only toggling is unavailable, the lead agent should enable the guard before dispatch and disable it after fan-in / synthesis completes
- persistent structural agents and interpretive agents may use different lint profiles
