# Implementation Checklist - claude-session-poison-recovery

1. Run `python3 scripts/resume_precheck.py <session.jsonl>` before editing any session file.
2. If `Selected N lines from ... in Visual Studio Code` repeats, clear selection and close the relevant editor tab before JSONL repair.
3. If precheck passes, retry with minimal input first (`continue`, `/context`, or direct resume).
4. If precheck fails, write a fixed copy with `python3 scripts/fix_jsonl.py <session.jsonl>` and inspect before `--apply`.
5. If root cause is still unclear, capture the next failing request with `python3 scripts/claude_sniffer.py` and `ANTHROPIC_BASE_URL=http://127.0.0.1:7735 claude`.
6. Move long batch output behind `bash scripts/safe_batch_run.sh <log> -- <command...>`.
7. Apply `sanitize_utils.py` for model/API inputs and artifact writes in long-running evaluation scripts.
8. Only edit `~/.claude/settings.json` with valid JSON merge after verifying the key is supported in the actual runtime.

## Context Loss Recovery (added 2026-03-26)

9. If Claude forgets the plan after compaction or resume, run `python3 scripts/context_restore.py --project-root <project>` first.
10. If `difficulty=easy` (HANDOFF exists), read the most recent HANDOFF document to restore plan state.
11. If `difficulty=medium` (no HANDOFF), reconstruct from `git log --oneline -20` + MEMORY.md + active plans.
12. If `difficulty=hard` (no HANDOFF, no MEMORY), use `agent-parser` skill on session JSONL to extract compaction summary.
13. After restoration, report understood state to user and get explicit confirmation before proceeding.
14. If no HANDOFF existed, create one with `python3 scripts/context_restore.py --project-root <project> --create-handoff`.
15. At session end, always write a HANDOFF document to anchor plan state for next session.
