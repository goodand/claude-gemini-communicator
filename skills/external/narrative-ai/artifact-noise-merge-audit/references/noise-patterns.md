# Noise Patterns

## Common keep candidates

- runtime-core files
- canonical Maestro flows
- tracked CI/docs files that are already part of the repo contract

## Common remove candidates

- temporary screenshots
- `/tmp`-style artifacts
- `test_log/**` churn unless the user explicitly wants it tracked
- local skill locks, user state files, and branch-only experiment output

## Repo lesson

This repo often benefits from:
- keeping code changes
- excluding experiment noise
- opening a slim PR instead of forcing a giant branch through review
