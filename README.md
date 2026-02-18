# Claude-Gemini Communicator

Claude Code, Codex CLI, Gemini CLI 3-Agent 협업 시스템.

## 작동 방식

```
Claude Code (오케스트레이터)
├── Gemini CLI (계정 로그인) → 코드 리뷰, 문서 평가, 아키텍처 비판
├── Codex CLI (계정 로그인) → 코딩, 분석, 리뷰
└── Hook 시스템 → 자동 평가, 에러 분석, 위험 명령 차단
```

1. Claude Code에서 파일을 작성/수정하면 **PostToolUse Hook**이 Gemini 평가를 트리거합니다.
2. Gemini CLI(계정 로그인 우선) 또는 SDK(API key 폴백)로 평가합니다.
3. 결과가 `plans/gemini/gemini_feedback.md`에 기록됩니다.
4. Codex CLI 결과는 `plans/codex/codex_feedback.md`에 기록됩니다.

## 빠른 시작

### 필수 요구사항
- Gemini CLI (Google 계정 로그인)
- Codex CLI (OpenAI 계정 로그인)
- Python 3.10+
- Claude Code (hooks 지원)

### 1단계. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2단계. 환경변수 설정

```bash
cp config/.env.example .env
# .env 파일을 열어 API 키 설정
```

- Gemini CLI 인증만 사용할 경우 API 키 없이도 동작 가능
- SDK 폴백까지 안정적으로 쓰려면 `GEMINI_API_KEY` 권장

### 3단계. 다른 프로젝트에 설치

```bash
# 설치 (Hook 3개 + Skills 6개 심링크)
python3 src/cli.py install --target /path/to/project

# 제거
python3 src/cli.py uninstall --target /path/to/project
```

설치 시 PostToolUse/Stop Hook에 `GEMINI_FEEDBACK_DIR`이 자동 주입되어, 대상 프로젝트의 `plans/gemini/`에 피드백이 분리 저장됩니다.

### 4단계. 동작 점검

```bash
python3 src/cli.py doctor    # 시스템 진단
python3 src/cli.py status    # 현재 상태
python3 src/cli.py test      # 자동 테스트 (68건)
```

## Hook 시스템

| Hook | 트리거 | 동작 |
|------|--------|------|
| **PreToolUse** | Bash 명령 실행 전 | `rm -rf`, `git push --force` 등 위험 명령 차단/경고 |
| **PostToolUse** | Write/Edit 후 | 감시 확장자 파일 자동 Gemini 평가 (쿨다운 적용) |
| **Stop** | 응답 완료 시 | Plan 문서 평가 + 반복 에러 분석 |

## CLI 명령어

```bash
python3 src/cli.py doctor              # 설정/환경/Hook/JSONL 진단
python3 src/cli.py status              # 현재 설정값 + 상태 요약
python3 src/cli.py stats [--jsonl]     # 피드백 또는 JSONL 통계
python3 src/cli.py search <keyword>    # 피드백 검색 (--jsonl 지원)
python3 src/cli.py chain <id>          # 메시지 체인 추적 (--list)
python3 src/cli.py test                # 내장 자동 테스트
python3 src/cli.py clear [--jsonl]     # 상태 파일 초기화
python3 src/cli.py install --target <dir>    # Hook+Skill 설치
python3 src/cli.py uninstall --target <dir>  # 설치 제거
```

## 설정

`config/config.json`에서 수정:

- **감시 확장자**: `watch_extensions` (기본 `.md`, `.py`)
- **제외 파일**: `exclude_files`
- **쿨다운**: `cooldown_seconds_per_file` (기본 300초)
- **타임아웃**: `gemini_timeout` (기본 120초)
- **비동기 모드**: `async_mode`
- **JSONL 버스**: `jsonl_bus.enabled/path`
- **에러 감지**: `error_detection.*`
- **라우팅 규칙**: `routing_rules` (메시지 타입별 대상 에이전트)
- **SDK 설정**: `sdk` (모델, 폴백, API key 환경변수)

## 프로젝트 구조

```
config/
├── config.json              # 메인 설정
└── .env.example             # 환경변수 템플릿
src/
├── hooks/                   # Hook 스크립트 (PreToolUse, PostToolUse, Stop)
├── core/                    # 핵심 로직 (Gemini 서비스, 라우터, 쿨다운, 스케줄러)
├── shared/                  # 공유 유틸 (설정 로딩, 피드백 저장, 파일 락)
├── cli.py                   # CLI 관리 도구
└── async_runner.py          # 비동기 Gemini 호출
skills/
├── install/                 # 다른 프로젝트에 설치/제거
├── gemini-cli-context/      # Gemini CLI 비대화형 호출
├── codex-user-context/      # Codex CLI 비대화형 호출
├── cross-agent-bridge/      # 에이전트 오케스트레이션
├── agent-parser/            # 에이전트 출력 파싱
└── gemini-reviewer/         # Gemini 코드/문서 리뷰
```

## 상세 문서

- **사용자 매뉴얼**: [`plans/User/user_manual.md`](plans/User/user_manual.md)
- **프로젝트 가이드**: [`plans/claude/claude_project_guide.md`](plans/claude/claude_project_guide.md)
- **아키텍처**: [`architecture/`](architecture/)
