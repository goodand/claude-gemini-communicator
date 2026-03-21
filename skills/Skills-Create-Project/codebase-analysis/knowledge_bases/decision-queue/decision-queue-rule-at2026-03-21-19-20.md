# Decision Queue Rule

## Purpose

Hold decision-needed items for `codebase-analysis` while implementation and smoke work are still evolving.

## Scope

Use this queue for:
- promotion vs defer decisions
- rule hardening decisions
- warning policy decisions
- archive/layout decisions
- wrapper generalization decisions
- other cross-artifact choices that are not yet stable enough for KB or validator promotion

Do not use this queue for:
- raw smoke evidence
- troubleshooting case logs
- sample fixtures
- finalized canonical rules already promoted into KB, contract, or checklist

## Storage Boundary

- location: `knowledge_bases/decision-queue/`
- this directory is a decision backlog layer inside `codebase-analysis`
- it is not a source-of-truth KB layer
- it is not a raw evidence archive layer

## Recommended File Shape

Use minute-level filenames:
- `decision-<topic>-atYYYY-MM-DD-HH-MM.md`

Recommended sections:
- `Context`
- `Decision Needed`
- `Options`
- `Advantages`
- `Side Effects`
- `Current Recommendation`
- `Status`
- `Promotion Target`

## Status Values

- `pending`
- `promote`
- `defer`
- `reject`

## Exit Rule

Once a decision is resolved:
- promote it into KB / contract / checklist / troubleshooting / validator rule as appropriate
- then either leave the decision file as trace history or mark it resolved explicitly
