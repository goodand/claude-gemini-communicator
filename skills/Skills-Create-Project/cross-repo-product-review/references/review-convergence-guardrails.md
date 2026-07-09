# Review Convergence Guardrails

## Guardrails

### 1. Intent Lock First

- product definition must be confirmed before reading modules in detail
- a wrong product framing invalidates the review

### 2. Structural-Class Completeness

- if Codex fixes one field or branch in a structural class, check sibling fields in the same class
- do not close a finding only because the named line changed

### 3. Round Closure Means Re-Reading

- every Codex fix is re-read from current code-state
- green tests alone do not close product-review findings

### 4. Direct Closure Threshold

- when residual issues drop to 1-2 bounded items, prefer direct expert patch over another round-trip handoff

### 5. API-Surface Change Trigger

- if the fix introduces async migration, bundler migration, or another API-surface rewrite, route the changed area through an additional specialist review
