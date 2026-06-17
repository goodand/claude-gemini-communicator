# Recovery Runbook

## Step 0. Do not mutate evidence first

- do not overwrite the session JSONL immediately
- do not append raw JSON to `~/.claude/settings.json`

## Step 1. Identify the live context signal

If the failure banner contains `Selected N lines from ... in Visual Studio Code`, treat that as a primary clue. Clear selection and close the referenced tab before anything else.

## Step 2. Precheck the stored session

```bash
python3 scripts/resume_precheck.py /path/to/session.jsonl
```

Interpretation:
- `status=pass` means the stored JSONL is not the first suspect
- `status=fail` means fix/copy path moves up in priority

## Step 3. Retry with minimal context

- same session: `continue` or `/context`
- direct resume: `claude --resume <session-id>`
- avoid long pasted context during this step

## Step 4. Fix only when the file actually fails precheck

```bash
python3 scripts/fix_jsonl.py /path/to/session.jsonl
python3 scripts/fix_jsonl.py /path/to/session.jsonl --apply
```

Rules:
- inspect the written copy first
- `--apply` is allowed only after the copy looks correct
- `--apply` creates `.bak`

## Step 5. Capture the next bad request if the source is still unclear

```bash
python3 scripts/claude_sniffer.py
ANTHROPIC_BASE_URL=http://127.0.0.1:7735 claude
```

Use this when you need the exact failing request body, not when you only need to repair a known bad JSONL.

## Step 6. Prevent recurrence

- route long batch commands through `safe_batch_run.sh`
- sanitize long text streams with `sanitize_stream.py`
- sanitize model/API input and artifact writes with `sanitize_utils.py`

---

# Context Loss Recovery (separate path from JSON corruption)

Symptom matrix §6, §7에 해당. 세션은 정상이지만 Claude가 계획/역할/결정사항을 잊은 경우.

## Step 7. Run context restore

```bash
python3 scripts/context_restore.py --project-root /path/to/project
```

Interpretation:
- `difficulty=easy` → HANDOFF 존재. Step 8로.
- `difficulty=medium` → HANDOFF 없음, MEMORY.md + git 있음. Step 9로.
- `difficulty=hard` → 둘 다 없음. Step 10으로.

## Step 8. Restore from HANDOFF

1. `context_restore.py` 출력에서 most recent HANDOFF 경로를 확인한다.
2. HANDOFF 문서를 읽고 plan state를 재구성한다.
3. 사용자에게 "현재 이해한 상태"를 명시적으로 보고하고 확인받는다.
4. 확인 후 작업을 재개한다.

## Step 9. Reconstruct from git + MEMORY.md

HANDOFF가 없는 경우:

1. `git log --oneline -20` 으로 최근 작업 파악.
2. `git diff HEAD~5..HEAD --stat` 으로 변경된 파일 범위 확인.
3. MEMORY.md에서 프로젝트 수준 맥락 (팀 구조, phase, 실험 상태) 확인.
4. active plans/checklists 중 가장 최근 수정된 문서를 읽는다.
5. 사용자에게 보고 후 확인받는다.
6. 확인 후 `context_restore.py --create-handoff` 로 복원 문서를 생성한다.

## Step 10. Last resort — session transcript

git과 MEMORY.md도 충분하지 않은 경우:

1. `context_restore.py --json` 출력의 `session_transcript.path` 확인.
2. `agent-parser` skill로 compaction summary 구간을 추출한다.
3. 또는 session JSONL의 마지막 N줄을 직접 읽는다:
   ```bash
   tail -50 /path/to/session.jsonl | python3 -m json.tool
   ```
4. 추출된 맥락으로 plan state를 재구성하고 사용자 확인을 받는다.

## Step 11. Prevent context loss recurrence

- 매 세션 종료 전 HANDOFF 문서를 작성한다 (수동 또는 hook).
- compaction 전에 핵심 plan state를 외부 파일에 앵커한다 (HANDOFF, MEMORY.md).
- 장기 결정사항은 MEMORY.md에 기록하되, 세션 단위 진행상황은 HANDOFF에 기록한다.
- metric naming, 역할 경계 같은 규칙은 contract 문서에 기계 참조 가능한 형태로 유지한다.
