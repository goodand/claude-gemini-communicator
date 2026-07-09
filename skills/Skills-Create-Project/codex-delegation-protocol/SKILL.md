---
name: codex-delegation-protocol
description: >-
  worktree-parallel family의 delegation-message specialist. Use this skill
  when a Codex delegation prompt must be assembled from task-packet + context
  files + constraints and emitted as a ready-to-execute command string.
  broader multi-agent orchestration은 worktree-parallel을 사용하라.
---

# Codex Delegation Protocol

task-packet(계약서)을 Codex가 이해할 수 있는 위임 메시지로 변환하는 프로토콜.

## When to use

- task-packet을 Codex 실행 프롬프트로 변환할 때
- 위임 메시지의 완전성(goal/scope/done/constraints)을 검증할 때
- worktree 경로를 포함한 실행 커맨드 문자열을 생성할 때
- 과거 위임 메시지를 템플릿으로 재활용할 때

## Workflow

1. **패킷 로드** — `scripts/delegation_builder.py compose --packet <packet.json>` → 패킷에서 필수 필드 추출
2. **컨텍스트 수집** — context_files 읽기 + 관련 reference 자동 탐지 (→ `references/prompt-anatomy.md`)
3. **프롬프트 조립** — 5-section 구조: Mission / Scope / Context / Constraints / Done-Definition
4. **검증** — `scripts/delegation_builder.py validate --message <msg.md>` → 누락 섹션·금지 패턴 검사
5. **커맨드 생성** — `scripts/delegation_builder.py command --packet <packet.json> [--worktree <path>]` → 실행 가능한 codex exec 문자열 출력

## Scripts

- `scripts/delegation_builder.py` — compose/validate/command/preview 통합 래퍼. `python3 scripts/delegation_builder.py --help`

## References

- `references/prompt-anatomy.md` — 5-section 프롬프트 구조, 각 섹션 규칙, 좋은/나쁜 예시
- `references/delegation-checklist.md` — 위임 전 검증 체크리스트 (10항목)
- `references/troubleshooting.md` — 실전 테스트 버그 케이스

## Notes

- **프롬프트에 코드를 직접 붙여넣지 않는다** — context_files 경로만 전달, Codex가 직접 읽음
- **done_definition은 검증 가능해야 한다** — "잘 작성하라"는 done이 아니다
- **sandbox 기본값은 workspace-write** — network 필요 시 packet.constraints에 명시
- **한국어 경로 주의** — worktree_path에 한국어 포함 시 tmux send-keys 인코딩 문제 가능 (→ `references/troubleshooting.md`)
