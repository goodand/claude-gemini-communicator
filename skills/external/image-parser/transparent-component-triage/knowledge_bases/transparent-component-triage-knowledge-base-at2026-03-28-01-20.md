# Transparent Component Triage Knowledge Base

## Purpose

This skill exists to keep the preprocessing baseline conservative while still identifying a small deterministic subset worth human review.

## Repo-Specific Rationale

- Automatic object isolation is not batch-ready in this workspace.
- Alpha-connected components can still provide a useful deterministic prefilter.
- The right output is a reviewed candidate subset, not an automatic branch activation.

## Operating Principles

1. Triage the full batch, but promote nothing automatically.
2. Treat `alpha_split_sufficient` as a mechanical signal only.
3. Keep the default baseline on full-image plus standalone OCR.
4. Use the batch report to decide where one-image review should happen next.

## Boundary Reminder

This skill should stop at:

- candidate subset discovery
- report generation
- summary JSON
- manifest JSONL

It should not expand into:

- semantic scoring
- OCR review per component
- image correction
- caption reruns
