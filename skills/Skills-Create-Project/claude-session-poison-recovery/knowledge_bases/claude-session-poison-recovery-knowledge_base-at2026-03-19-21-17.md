# claude-session-poison-recovery Knowledge Base

- created_at: `2026-03-19-21-17`
- reference_acquisition_mode: `hybrid_user_issue_reports_plus_local_evidence`
- source_scope: `github_issue_reports_user_supplied_plus_local_runtime_diagnostics`
- purpose: `Claude session poison, invalid JSON surrogate error, IDE selection auto-context, JSONL resume repair, and prevention hardening을 재사용 가능한 절차로 정리`

## Canonical Design Takeaways

1. `The request body is not valid JSON: no low surrogate in string`는 모델 품질 문제가 아니라 request serialization failure다.
2. 원인을 먼저 `stored session corruption`과 `live context injection`으로 분리해야 한다.
3. 같은 column에서 400이 반복되고 `Selected N lines from ... in Visual Studio Code`가 같이 보이면, JSONL fix보다 IDE selection auto-context 차단을 먼저 의심한다.
4. `resume_precheck`가 pass면 fix를 바로 적용하지 말고, live IDE context와 현재 선택 버퍼를 먼저 끊는다.
5. JSONL fix는 copy-first, backup-first가 원칙이다. parse fail, tail fail, surrogate hit가 있을 때만 적용 우선순위가 올라간다.
6. batch 출력과 tool output은 Claude 대화 컨텍스트에 그대로 들어가면 session poison을 재발시킬 수 있다. long-running output은 파일로 격리하고 요약만 노출한다.
7. model/API 입력과 artifact 저장 모두 surrogate/NUL sanitize가 필요하다. stdout sanitize만으로는 충분하지 않다.
8. settings 수정은 valid JSON merge로만 해야 한다. raw append는 별도 JSON object를 덧붙여 파일을 깨뜨린다.
9. `includeIdeSelection` 같은 설정 키는 이슈에 보고된 값일 수 있지만, 실제 runtime 구현과 버전에서 확인하기 전까지는 `version-dependent hint`로 취급한다.
10. sniffer는 과거 요청 복구가 아니라 다음 재현 요청 캡처용이다. 이미 끝난 400의 raw body는 보통 로컬에 남지 않는다.
11. official GitHub issue는 symptom corroboration 용도로 쓰고, exact banner string이나 exact settings key는 local-only/runtime-verified 규칙으로 분리한다.

## Failure classes

- IDE selection auto-context: VS Code/Cursor에서 선택된 텍스트가 매 요청에 자동 포함
- Bash/tool output invalid unicode: progress bar, ANSI, binary-like output, broken surrogate가 다음 요청에 오염 전파
- Session JSONL corruption: truncated tail, parse failure, surrogate codepoints, broken resume chain
- Picker/runtime friction: huge session, stale index, picker stall, direct resume only path
- Unsafe settings mutation: `>> ~/.claude/settings.json` 같은 append로 config 자체를 파손
- Context compaction loss: auto-compaction이 plan/role/decision context를 요약에서 누락시켜 Claude가 합의된 계획을 잊음
- HANDOFF absence on resume: resume 시 복원 앵커(HANDOFF 문서)가 없어 이전 세션의 결정사항·진행상태를 재구성할 수 없음

## Canonical Design Takeaways — Context Loss (12-17)

12. Compaction 후 컨텍스트 유실은 JSON corruption이 아니라 **semantic loss**다. 세션은 정상인데 Claude가 계획을 모른다.
13. 복원의 1차 소스는 **git** (log, diff, blame)이다. 코드 변경 이력이 가장 신뢰도 높은 ground truth.
14. 복원의 2차 소스는 **HANDOFF 문서**다. 세션 종료 시 작성된 인수인계 문서가 plan state를 기록한다.
15. 복원의 3차 소스는 **MEMORY.md**다. 프로젝트 수준의 장기 기억이지만, 세션 단위 진행상황은 없다.
16. 복원의 4차 소스는 **session JSONL transcript**다. compaction summary 구간을 직접 읽을 수 있지만 비용이 높다.
17. 예방의 핵심은 **세션 종료 전 HANDOFF 문서 작성**이다. HANDOFF가 있으면 resume 시 `context_restore.py`가 자동으로 plan state를 재구성한다.

## Recovery order — Context Loss (별도 경로)

Context loss는 JSON corruption recovery와 독립된 경로다.

1. 증상을 matrix §6, §7로 분류한다.
2. `context_restore.py --project-root .` 를 실행해 복원 요약을 생성한다.
3. 복원 요약에서 가장 최근 HANDOFF 문서를 찾아 직접 읽는다.
4. HANDOFF가 없으면 `git log --oneline -20` + `git diff HEAD~5..HEAD --stat` 으로 최근 변경을 파악한다.
5. MEMORY.md에서 프로젝트 수준 맥락 (팀 구조, 현재 phase, 실험 상태)을 확인한다.
6. 위 소스들로 plan state를 재구성한 뒤, 사용자에게 "현재 이해한 상태"를 명시적으로 보고하고 확인받는다.
7. 확인 후 HANDOFF가 없었다면 `context_restore.py --create-handoff` 로 복원 문서를 생성해 다음 유실에 대비한다.

## Recovery order

1. symptom을 matrix로 분류한다.
2. 가능한 경우 editor selection을 먼저 제거하고 관련 탭을 닫는다.
3. session JSONL에 대해 `scripts/resume_precheck.py`를 돌린다.
4. precheck가 pass면 direct resume 또는 continue를 최소 입력으로 재시도한다.
5. precheck가 fail이면 `scripts/fix_jsonl.py`로 copy를 만든 뒤 diff를 보고 필요 시 `--apply` 한다.
6. 여전히 원인 불명 또는 request body 위치 확인이 필요하면 `scripts/claude_sniffer.py`를 켜고 재현한다.
7. 복구 후에는 `scripts/safe_batch_run.sh`와 `scripts/sanitize_utils.py`를 적용해 재발을 막는다.

## Verified local signals

- session JSONL이 full parse, tail parse, surrogate scan 모두 통과하면 stored-session corruption 가설은 약해진다.
- referenced markdown file가 strict UTF-8 decode와 surrogate scan을 통과하면 디스크 파일 자체보다는 editor buffer/live context 경로가 더 유력하다.
- 같은 column 위치가 반복되면 요청 body 길이와 포함 컨텍스트가 거의 고정되어 있다는 뜻이다.
- `Selected N lines from ...` 배너는 IDE selection auto-context에 대한 강한 local 단서다.

## Recommended tool bundle

- `resume_precheck.py`
- `fix_jsonl.py`
- `claude_sniffer.py`
- `safe_batch_run.sh`
- `sanitize_stream.py`
- `sanitize_utils.py`
- `context_restore.py` — git + HANDOFF + MEMORY 기반 컨텍스트 복원 (context loss 전용)

## References used

- [official-github-corroboration-at2026-03-19-21-34.md](../references/official-github-corroboration-at2026-03-19-21-34.md)
  - verified official issue set: `#1709`, `#1832`, `#3995`, `#9561`
- local verified scripts and artifacts from the current project workspace
- local Claude session JSONL precheck and referenced markdown UTF-8/surrogate checks
