# Review Convergence Implementation Checklist

1. Capture a one-paragraph product intent statement.
2. Classify touched files into the six canonical review categories.
3. Produce a severity-ranked findings list with file anchors.
4. Generate a bounded Codex handoff prompt from the findings.
5. Re-read each changed file after Codex patch.
6. Reclassify residual items into resolved / residual / newly introduced.
7. If residual count is 1-2, close directly instead of dispatching another full round.
8. Record promoted repeated tasks/issues after closure evidence exists.
