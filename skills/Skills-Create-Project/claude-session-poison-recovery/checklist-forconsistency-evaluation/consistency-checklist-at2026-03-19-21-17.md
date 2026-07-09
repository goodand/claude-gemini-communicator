# Consistency Checklist - claude-session-poison-recovery

- [ ] SKILL.md distinguishes `stored session corruption` from `live context injection`
- [ ] workflow puts `resume_precheck.py` before `fix_jsonl.py --apply`
- [ ] workflow explicitly checks both `full parse` and `tail parse`
- [ ] workflow treats `parse ok` and `surrogate free` as separate checks
- [ ] workflow documents IDE selection auto-context as a first-class branch
- [ ] workflow warns against `>> ~/.claude/settings.json`
- [ ] settings guidance is marked version-dependent unless locally verified
- [ ] direct resume and picker resume are treated as separate success paths
- [ ] prevention includes batch output isolation, API-input sanitize, and artifact-write sanitize
- [ ] bundled scripts map to the troubleshooting steps described in the references

## Context Loss consistency (added 2026-03-26)
- [ ] SKILL.md distinguishes `session corruption` from `context loss` as separate failure classes
- [ ] symptom matrix covers compaction context loss (§6) and HANDOFF absence (§7)
- [ ] KB lists `context compaction loss` and `HANDOFF absence on resume` as failure classes
- [ ] KB includes design takeaways 12-17 for context loss
- [ ] KB includes separate recovery order for context loss
- [ ] recovery runbook covers Step 7-11 (context restore, HANDOFF restore, git+MEMORY reconstruct, transcript, prevention)
- [ ] `context_restore.py` is listed in the recommended tool bundle
- [ ] `context_restore.py` supports `--json`, `--create-handoff`, `--project-root` flags
- [ ] restoration difficulty levels (easy/medium/hard) map to specific runbook steps (8/9/10)
- [ ] context-loss-patterns reference documents at least 3 real-world patterns from observed sessions
- [ ] prevention includes HANDOFF creation as a first-class recommendation
