# Claude-Gemini Communicator

Claude Code, Codex CLI, Gemini CLI 3-Agent 협업 시스템.

## 작동 방식

```
Claude Code (오케스트레이터)
├── Gemini CLI (계정 로그인) → 코드 리뷰, 문서 평가, 아키텍처 비판
├── Codex CLI (계정 로그인) → 코딩, 분석, 리뷰
└── Hook 시스템 → 자동 평가, 에러 분석, 위험 명령 차단
```

1. Claude Code에서 파일을 작성/수정하면 PostToolUse Hook이 Gemini 평가를 트리거합니다.
2. Gemini CLI(계정 로그인 우선) 또는 SDK(API key 폴백)로 평가합니다.
3. 결과가 `plans/gemini/gemini_feedback.md`에 기록됩니다.
4. Codex CLI 결과는 `plans/codex/codex_feedback.md`에 기록됩니다.

## 빠른 시작

### 필수 요구사항
- Gemini CLI (Google 계정 로그인)
- Codex CLI (OpenAI 계정 로그인)
- Python 3.10+
- Claude Code (hooks 지원)

### 다른 프로젝트에 설치

```bash
# 설치 (Hook 3개 + Skills 6개 심링크)
zsh skills/install/scripts/run_install.sh --target /path/to/project

# 제거
zsh skills/install/scripts/run_install.sh --uninstall --target /path/to/project
```

### 모니터링

```bash
# Gemini 피드백 실시간 확인
tail -f plans/gemini/gemini_feedback.md

# Codex 피드백 실시간 확인
tail -f plans/codex/codex_feedback.md
```

## 설정

`config/config.json`에서 수정:

- **타임아웃**: `gemini_timeout` (기본 120초)
- **쿨다운**: `cooldown_seconds_per_file` (기본 300초)
- **감시 확장자**: `watch_extensions` (기본 `.md`, `.py`)
- **라우팅 규칙**: `routing_rules` (메시지 타입별 대상 에이전트)
- **SDK 설정**: `sdk` (모델, 폴백, API key 환경변수)

## 프로젝트 구조

```
config/
├── config.json              # 메인 설정
└── .env.example             # 환경변수 템플릿
src/
├── hooks/                   # Hook 스크립트 (PreToolUse, PostToolUse, Stop)
├── core/                    # 핵심 로직 (Gemini 서비스, 라우터, 쿨다운)
└── shared/                  # 공유 유틸 (설정 로딩, 피드백 저장)
skills/
├── install/                 # 다른 프로젝트에 설치/제거
├── gemini-cli-context/      # Gemini CLI 비대화형 호출
├── codex-user-context/      # Codex CLI 비대화형 호출
├── cross-agent-bridge/      # 에이전트 오케스트레이션
├── agent-parser/            # 에이전트 출력 파싱
└── gemini-reviewer/         # Gemini 코드/문서 리뷰
```
