# Runtime — cross-repo-product-review

## Input Contract

- target repo root
- product intent summary
- non-goals
- review depth expectation

## Canonical Review Categories

1. Host / Entry
2. Data Contract
3. Feature Seams
4. Webview / Render / Runtime
5. Host State / Persistence
6. Tests / Evidence

## Convergence Rule

- round 1: broad finding discovery
- round 2+: verify closure, not just diff
- residual 1-2 actionable items: prefer direct expert fix over another full handoff

## Evidence Rule

- findings must include file path and why it matters
- re-verification must include current code-state, not old session assumptions
- repeated task and repeated issue promotion happens only after closure evidence exists
