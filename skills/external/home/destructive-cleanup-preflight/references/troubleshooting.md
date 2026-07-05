# Troubleshooting

## A Candidate Path Looks Disposable But Is Still In Use

- Treat the path as protected until runtime dependence is reviewed.
- Do not downgrade active-runtime uncertainty into delete-ready status.

## A Directory Contains Both Generated And Canonical Files

- Reclassify it as `mixed-content`.
- Keep it out of the delete-ready list until narrower child paths are reviewed.

## The User Wants To Delete First And Sort It Out Later

- Stop and require an explicit reviewed path list.
- If loss already happened, route to [Workspace Control Recovery](../../workspace-control-recovery/SKILL.md).

## Cleanup Scope Starts Expanding Mid-Conversation

- Re-freeze the candidate path set.
- Re-run protected-path review instead of continuing with stale assumptions.
