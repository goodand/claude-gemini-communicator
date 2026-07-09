---
name: claude-session-poison-recovery
description: >-
  Use this skill when (A) Claude Code fails with invalid JSON surrogate errors,
  IDE selection auto-context issues, or session JSONL corruption, OR (B) Claude
  loses plan context after compaction/resume — forgetting agreed plans, confusing
  roles, or suggesting wrong next steps.
---

# Claude Session Poison Recovery

두 가지 failure class를 다룬다:

1. **Session Corruption**: JSON surrogate error, IDE selection auto-context, JSONL corruption, prevention hardening
2. **Context Loss**: compaction/resume 후 계획 망각, 역할 혼동, 문서 drift — git/HANDOFF 기반 복원

## When to use

### Session Corruption (증상 §1-5)
- `The request body is not valid JSON: no low surrogate in string`가 반복될 때
- `continue`, `/compact`, `--resume` 이후 같은 400이 계속 날 때
- `Selected N lines from ... in Visual Studio Code`가 매 요청에 붙을 때
- 세션 JSONL이 깨졌는지, live IDE context가 문제인지 분리해야 할 때

### Context Loss (증상 §6-7)
- `/compact` 또는 auto-compaction 후 Claude가 합의된 계획을 잊었을 때
- `--resume` 후 Claude가 이전 세션의 결정사항을 모를 때
- 역할 경계가 혼동될 때 (CTO가 코드 구현 시도, Codex↔Claude subagent 혼동)
- metric naming이 비공식 명칭으로 회귀했을 때

## Workflow A: Session Corruption

1. [KB](knowledge_bases/claude-session-poison-recovery-knowledge_base-at2026-03-19-21-17.md)의 `Canonical design takeaways`와 `Recovery order`를 읽는다.
2. [symptom-matrix](references/symptom-matrix-at2026-03-19-21-17.md)로 증상을 분류한다 (§1-5).
3. 세션 JSONL이 의심되면 `scripts/resume_precheck.py`를 먼저 돌린다.
4. [recovery-runbook](references/recovery-runbook-at2026-03-19-21-17.md) Step 0-6 순서대로 진행한다.
5. JSONL fix가 필요하면 `scripts/fix_jsonl.py`로 copy → diff → `--apply`.
6. 원인 불명이면 `scripts/claude_sniffer.py`로 failing request body를 캡처한다.
7. 재발 방지: `scripts/safe_batch_run.sh`, `scripts/sanitize_stream.py`, `scripts/sanitize_utils.py`.

## Workflow B: Context Loss

1. [symptom-matrix](references/symptom-matrix-at2026-03-19-21-17.md)로 증상을 분류한다 (§6-7).
2. `scripts/context_restore.py --project-root .` 를 실행한다.
3. difficulty 판정에 따라 [recovery-runbook](references/recovery-runbook-at2026-03-19-21-17.md) Step 7-11을 따른다:
   - `easy` → Step 8: HANDOFF 문서에서 복원
   - `medium` → Step 9: git + MEMORY.md에서 재구성
   - `hard` → Step 10: session transcript에서 추출
4. 복원 후 사용자에게 "현재 이해한 상태"를 보고하고 확인받는다.
5. Step 11: HANDOFF 작성, 외부 앵커 확보로 재발 방지.

패턴 상세: [context-loss-patterns](references/context-loss-patterns-at2026-03-26.md)

## Details

- [skill-entrypoint-details](references/skill-entrypoint-details-at2026-03-19-22-02.md) — scripts, references, local notes, official GitHub corroboration
- [context-loss-patterns](references/context-loss-patterns-at2026-03-26.md) — compaction 특화 5가지 패턴 + 복원 소스 우선순위
- [prevention-patterns](references/prevention-patterns-at2026-03-19-21-17.md) — batch 격리, sanitize, sniffer 운용
