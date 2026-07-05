# Protected Path Review

- Mark `control/` trees as protected until proven otherwise.
- Mark active workspace roots as protected until runtime dependence is reviewed.
- Mark `.codex/` runtime and session state as protected while sessions may still be active.
- Treat `knowledge_base`, `knowledge_bases`, `team/`, and `user_decisions/` as source-of-truth candidates by default.
- Require an explicit reviewed delete-ready list before any `rm`.
- If a deletion incident already happened, stop and route to [Workspace Control Recovery](../../workspace-control-recovery/SKILL.md).
