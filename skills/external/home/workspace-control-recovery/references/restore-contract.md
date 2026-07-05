# Restore Contract

## Owned Outcome

Recover the approved subtree to a usable state while preserving any newer current files unless overwrite is explicitly requested.

## Invariants

- workspace provenance must be verified before reusing any recovery source
- backup target path must be inspected before restore
- current files are not overwritten by default
- exact-content evidence outranks structure-only and name-only evidence
- excluded noise should not distort recovery counts

## Recovery Targets

Common targets include:

- `control/`
- `kb/`
- `knowledge_base/`
- `knowledge_bases/`
- `team/`
- `user_decisions/`

## Routing Boundary

- If the question is "what is safe to delete?" or "which paths are protected before cleanup?", route to [Destructive Cleanup Preflight](../../destructive-cleanup-preflight/SKILL.md).
- If the question is "what disappeared and how do we restore it safely?", stay here.

## Escalate Instead Of Guessing

- the snapshot path exists but access mode is blocked
- the backup target subtree is absent
- donor workspace and current workspace evidence disagree
- current files seem newer but provenance is unclear
- the user asks for destructive overwrite
