# CI Docs Checks

## Repo-specific drift patterns

- README lags behind product repositioning
- checklist state can claim repo-readiness before files are tracked
- local-only auth files can look like repo changes if not explicitly called out

## Review questions

- Are the workflow files actually tracked and runnable?
- Does README match the current product definition?
- Are `.env.example` and `.gitignore` consistent with real local-only files?
- Is a local helper being presented as a repo-level requirement?

## Preferred verdicts

- `merge-now` for coherent tracked CI/docs updates
- `split-before-merge` when docs/CI are good but mixed with runtime or local noise
