# Troubleshooting — codex-subagent-setup

## CASE-001: Runtime nickname exists but file-backed profile does not

**증상**: subagent는 생성됐지만, 이후 재사용 가능한 agent guide 파일이 없다.
**원인**: 런타임 생성 상태와 file-backed role definition을 분리하지 않았기 때문이다.
**해결**: `agents/<role>/AGENT.md`를 canonical role guide로 둔다.
**교훈**: nickname은 identity가 아니라 표시 이름이다.

## CASE-002: All workers receive too much context

**증상**: worker들이 전체 문맥을 중복으로 읽고 역할이 흐려진다.
**원인**: `fork_context=true`를 broad하게 사용했다.
**해결**: `context-broker` 하나에만 full context를 집중시키고 worker는 compact packet만 받는다.
**교훈**: full context는 예외 경로여야 한다.

## CASE-003: Flat agent markdown stopped scaling

**증상**: role 정의, tool 정책, context 링크, handoff 규약이 한 파일에 섞여 읽기와 유지보수가 나빠졌다.
**원인**: flat `agents/*.md` 구조가 커지는 subagent 운영을 감당하지 못했다.
**해결**: `agents/<role>/AGENT.md` + `knowledge_bases/` + `references/` + `bridges/` + `scripts/` 구조로 분리했다.
**교훈**: subagent도 package 단위로 다루는 편이 확장성이 높다.
