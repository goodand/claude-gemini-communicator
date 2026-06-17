# Symptom Matrix

## 1. Same 400, same column, plus `Selected N lines from ...`

- likely cause: `live IDE selection auto-context`
- first check: deselect editor text, close the selected tab, retry with minimal input
- next check: if available, disable or verify IDE-selection auto-inclusion behavior for the actual runtime version

## 2. `continue` or `/compact` keeps failing after heavy Bash/tool output

- likely cause: `invalid Unicode from tool output`
- first check: isolate batch output with `safe_batch_run.sh`
- next check: use `claude_sniffer.py` to capture the next request body and locate surrogate hits

## 3. `claude --resume <session-id>` fails or restored context is obviously truncated

- likely cause: `session JSONL corruption or truncated tail`
- first check: `resume_precheck.py`
- next check: `fix_jsonl.py` copy mode, then `--apply` if needed

## 4. Picker stalls or CPU spikes, but direct resume may still work

- likely cause: `picker/index/runtime issue`
- action: treat picker and direct resume separately; prefer `claude --resume <session-id>`

## 5. Referenced file on disk looks fine, but request still fails only when IDE is open

- likely cause: `editor buffer or extension-injected live context`
- action: close the file tab, then close the IDE window entirely if needed, then retry

## 6. After `/compact` or auto-compaction, Claude suggests wrong next steps or forgets the plan

- likely cause: `context compaction loss — semantic context dropped during summarization`
- symptoms:
  - Claude proposes actions that contradict the agreed plan
  - Role boundaries are confused (e.g., CTO attempts implementation, confuses Codex with Claude subagent)
  - Metric names revert to informal variants (e.g., DocHit@10 instead of HitRate@10)
  - "다음에 뭐 해야 하지?" 질문에 엉뚱한 단계를 제안
- first check: `context_restore.py --project-root .` — git log + HANDOFF docs + MEMORY.md 기반 복원 요약 생성
- next check: 가장 최근 HANDOFF 문서를 직접 읽고 plan state 재확인
- escalation: 복원 요약이 현재 상태와 불일치하면, session JSONL transcript에서 compaction summary 구간을 직접 확인

## 7. `claude --resume` succeeds but restored context has no plan awareness

- likely cause: `HANDOFF document absent or stale — no restoration anchor`
- symptoms:
  - resume 후 Claude가 "무엇을 하고 있었는지" 모름
  - 이전 세션의 결정사항을 기억하지 못함
  - git diff는 변경이 있는데 Claude가 그 변경의 맥락을 설명하지 못함
- first check: `git log --oneline -20` + `ls plans/**/HANDOFF*` — 최근 변경과 인수인계 문서 존재 확인
- next check: HANDOFF가 없으면 `context_restore.py --create-handoff` 로 현재 상태에서 복원 문서 생성
- prevention: 매 세션 종료 전 HANDOFF 문서 작성을 습관화 (또는 hook으로 강제)
