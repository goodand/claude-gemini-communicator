# Troubleshooting

## Snapshot Listed But Target Looks Missing

- Check the exact dated snapshot path, not only the visible mounted volume root.
- Validate the target subtree directly before concluding the backup is unusable.

## Recent Backup Still Does Not Contain The File

- A backup completion time does not prove a specific path was captured.
- Inspect the target path inside the snapshot and report absence explicitly.

## Recovery Evidence Exists Only As Filenames

- Treat file lists, `rg --files`, and similar outputs as `name-only` or `structure-only`.
- Do not claim content recovery until a file body is directly read.

## Donor Workspace Has Similar Files

- Confirm the full workspace root for every source file.
- Do not substitute donor content for current-workspace content without explicit approval.

## Restore Would Clobber Newer Current Files

- Stop and switch to missing-only merge restore.
- Measure `extra` first so preserved current files are explicit in the report.

## Counts Look Wrong

- Exclude `.DS_Store` and similar noise from recovery counts unless they matter to the user.
- Recompute counts from normalized relative paths on both sides.

## You Are Still In Pre-Delete Mode

- If nothing has been deleted yet, stop recovery planning.
- Route to [Destructive Cleanup Preflight](../../destructive-cleanup-preflight/SKILL.md) for scope classification and protected-path review first.
