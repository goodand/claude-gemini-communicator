# Image Result Auditor Comparison Consumer Knowledge Base

## Purpose

Capture why the auditor skill now also owns frozen-bundle comparison consumption and proxy auto-eval, instead of creating a separate narrow skill tied to one experiment name.

## Core Lessons

- downstream comparison is still an audit problem when it consumes completed evidence rather than generating new artifacts
- aggregate bundle freshness can drift behind per-image truth, so the consumer must support direct per-image fallback
- comparison winners and default baselines are different outputs and should never be collapsed into one field
- semantic judge absence should produce a waiver, not a fake execution claim

## Proven Example

`phase1` four-mode small-batch auto-eval was regenerated from `image11`, `image7`, and `image9` using per-image bundles while the consumer also gained aggregate-bundle input support.
