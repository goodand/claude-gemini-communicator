---
name: install
description: 현재 프로젝트에 claude-gemini-communicator 3-Agent 협업 시스템을 설치하거나 제거한다. Hook 3개 등록 + Skills 5개 심링크. 중복 설치 방지, 안전한 제거 지원.
---

# Install

현재 프로젝트에 claude-gemini-communicator 시스템을 설치한다.
Hook 3개(가드/리뷰/에러분석) + Skills 5개(심링크)를 한 번에 설정.

## Workflow

1. `scripts/run_install.sh`로 현재 프로젝트에 설치한다.
2. 이미 설치된 항목은 건너뛴다 (중복 방지).
3. `--uninstall`로 communicator 항목만 안전하게 제거한다.
4. 기존 사용자 Hook/Skills는 보존된다.

## Commands

```bash
# 현재 프로젝트에 설치
zsh skills/install/scripts/run_install.sh

# 특정 디렉토리에 설치
zsh skills/install/scripts/run_install.sh --target /path/to/project

# 제거
zsh skills/install/scripts/run_install.sh --uninstall

# 특정 디렉토리에서 제거
zsh skills/install/scripts/run_install.sh --uninstall --target /path/to/project

# 실행 전 확인
zsh skills/install/scripts/run_install.sh --dry-run
```

## 설치 내용

**Hook 3개** (`.claude/settings.local.json`):
- `PreToolUse` — Bash 위험 명령 가드
- `PostToolUse` — Write/Edit 시 Gemini 자동 리뷰
- `Stop` — 에러 분석 + Plan 감지

**Skills 5개** (`.claude/skills/` 심링크):
- `agent-parser` — 에이전트 출력 파싱
- `codex-user-context` — Codex CLI 비대화형 호출
- `cross-agent-bridge` — 에이전트 오케스트레이션
- `gemini-cli-context` — Gemini CLI 비대화형 호출
- `gemini-reviewer` — Gemini 코드/문서 리뷰
