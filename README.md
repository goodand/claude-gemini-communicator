# Claude-Gemini Communicator

Claude Code가 문서를 작성하면 Gemini가 자동으로 평가하는 AI 협업 시스템.

## 작동 방식

```
Claude (Write .md) → Hook 트리거 → Gemini CLI 평가 → 피드백 주입
```

1. Claude Code에서 `.md` 파일을 작성/수정하면 PostToolUse Hook이 트리거됩니다.
2. Hook 스크립트가 Gemini CLI를 호출하여 문서를 평가합니다.
3. 평가 결과가 `gemini_feedback.md`에 기록되고, Claude에 `additionalContext`로 주입됩니다.
4. Claude의 응답이 소프트웨어 개발 계획인 경우, Stop Hook이 추가 평가를 트리거합니다.

## 빠른 시작

### 필수 요구사항
- Gemini CLI (`/usr/local/bin/gemini`)
- Python 3
- Claude Code (hooks 지원)

### 설정

이 프로젝트 디렉토리에서 Claude Code를 시작하면 `.claude/settings.local.json`의 Hook 설정이 자동으로 적용됩니다.

```bash
cd ~/Desktop/Project_____현재_진행중인/claude-gemini-communicator
claude
```

### 모니터링

```bash
# 다른 터미널에서 피드백 실시간 확인
tail -f gemini_feedback.md
```

## 설정 커스터마이징

`scripts/config.json`에서 수정:

- **타임아웃**: `gemini_timeout` (기본 90초)
- **쿨다운**: `cooldown_seconds_per_file` (기본 300초, 동일 파일 재평가 방지)
- **감시 확장자**: `watch_extensions` (기본 `.md`)
- **평가 프롬프트**: `evaluation_prompt` (Gemini에 보내는 평가 지시)

## 프로젝트 구조

```
scripts/
├── config.json          # 설정
├── a2a_bridge.py        # Gemini CLI 호출 + 쿨다운 + 피드백 저장
├── hook_auto_task.py    # PostToolUse Hook (Write/Edit 감지)
└── hook_stop.py         # Stop Hook (Plan 감지)
```

자세한 내용은 [CLAUDE.md](./CLAUDE.md)를 참조하세요.
