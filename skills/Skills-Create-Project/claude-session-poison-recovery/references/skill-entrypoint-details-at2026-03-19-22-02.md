# Claude Session Poison Recovery Details

## Scripts

- [resume_precheck.py](../scripts/resume_precheck.py) - session JSONL 존재, full parse, tail parse, surrogate scan, sessions-index 상태를 점검
- [fix_jsonl.py](../scripts/fix_jsonl.py) - surrogate/NUL 제거 copy 생성, 필요 시 `.bak` 백업 후 `--apply`
- [claude_sniffer.py](../scripts/claude_sniffer.py) - Claude API request/response를 JSONL로 캡처해 invalid JSON request body를 확인
- [sanitize_stream.py](../scripts/sanitize_stream.py) - ANSI, CR, NUL, invalid UTF-8를 제거하는 stream sanitizer
- [safe_batch_run.sh](../scripts/safe_batch_run.sh) - 장시간 batch 출력 전체를 로그 파일로 격리하고 요약만 터미널에 노출
- [sanitize_utils.py](../scripts/sanitize_utils.py) - model/API 입력 및 artifact 저장 직전 surrogate/NUL 제거 유틸
- [context_restore.py](../scripts/context_restore.py) - git + HANDOFF + MEMORY.md 기반 컨텍스트 복원 (context loss 전용, 2026-03-26 추가)

## References

- [claude-session-poison-recovery-knowledge_base-at2026-03-19-21-17.md](../knowledge_bases/claude-session-poison-recovery-knowledge_base-at2026-03-19-21-17.md) - canonical KB
- [consistency-checklist-at2026-03-19-21-17.md](../checklist-forconsistency-evaluation/consistency-checklist-at2026-03-19-21-17.md) - source of truth와 recovery 분기 정합성 점검
- [implementation-checklist-at2026-03-19-21-17.md](../checklist-forimplementation/implementation-checklist-at2026-03-19-21-17.md) - 실제 적용 순서
- [symptom-matrix-at2026-03-19-21-17.md](symptom-matrix-at2026-03-19-21-17.md) - symptom to likely cause matrix
- [recovery-runbook-at2026-03-19-21-17.md](recovery-runbook-at2026-03-19-21-17.md) - direct resume, IDE selection 차단, JSONL fix 순서
- [ide-selection-and-settings-notes-at2026-03-19-21-17.md](ide-selection-and-settings-notes-at2026-03-19-21-17.md) - VS Code selection auto-context, settings 수정 주의사항
- [official-github-corroboration-at2026-03-19-21-34.md](official-github-corroboration-at2026-03-19-21-34.md) - official Anthropic GitHub issue corroboration
- [prevention-patterns-at2026-03-19-21-17.md](prevention-patterns-at2026-03-19-21-17.md) - batch 격리, sanitize, sniffer 운용
- [local-tooling-map-at2026-03-19-21-17.md](local-tooling-map-at2026-03-19-21-17.md) - 현재 project-local verified tooling map
- [troubleshooting.md](troubleshooting.md) - local troubleshooting edge cases
- [context-loss-patterns-at2026-03-26.md](context-loss-patterns-at2026-03-26.md) - compaction 특화 5가지 패턴 + 복원 소스 우선순위 (2026-03-26 추가)

## Notes

- `parse 가능`과 `surrogate 없음`은 같은 조건이 아니다. 둘 다 따로 확인한다.
- `full parse ok`여도 `tail parse fail`이면 resume 직후 문맥이 깨질 수 있다.
- `echo '{...}' >> ~/.claude/settings.json` 같은 raw append는 금지한다. settings는 항상 valid JSON merge로 수정한다.
- exact settings key는 runtime version dependent다. 실제 실행 환경에서 key 지원을 확인하기 전에는 확정 해결책으로 가정하지 않는다.
- direct resume과 picker resume은 분리해서 판단한다. picker 이슈가 있어도 `claude --resume <session-id>`는 통과할 수 있다.
