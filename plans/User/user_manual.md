# Claude-Gemini Communicator 사용자 매뉴얼

이 문서는 현재 코드베이스(`src/`, `skills/`, `config/`) 기준으로 작성된 사용자용 안내서입니다.

## 1) 이 서비스가 하는 일

Claude Code를 중심으로 Gemini와 Codex를 연결하는 **멀티 에이전트 통합 시스템**입니다.
파일 변경, 응답 완료, 명령 실행 등의 이벤트에 반응하여 외부 에이전트에 리뷰/분석을 요청하고, 결과를 프로젝트별로 기록합니다.

### 에이전트 역할

| 에이전트 | 역할 | 인증 방식 |
|----------|------|-----------|
| **Claude Code** | 오케스트레이터 — 코드 작성, 에이전트 호출, 결과 종합 | Claude Code 자체 |
| **Gemini** | 코드 리뷰, 문서 평가, 아키텍처 비판 | Google OAuth 또는 API key |
| **Codex** | 코딩, 코드 리뷰, 분석 (샌드박스 코드 실행 가능) | OpenAI 계정 로그인 |

### 자동 동작 (Hook 시스템)

- **PreToolUse Hook**: 위험한 Bash 명령을 사전 차단 또는 경고
- **PostToolUse Hook**: `Write/Edit` 후 대상 파일을 Gemini에 자동 평가 요청
- **Stop Hook**: 응답 완료 시 Plan 문서 평가 + 반복 에러 분석

### 수동 호출 (Skill 시스템)

Claude가 Skill을 통해 Gemini 또는 Codex를 직접 호출할 수 있습니다.
사용자 입장에서 두 에이전트의 호출 방식은 거의 동일합니다:

```bash
# Gemini에 리뷰 요청
zsh skills/gemini-cli-context/scripts/run_gemini_cli.sh "리뷰해줘" --file src/app.py

# Codex에 리뷰 요청
zsh skills/codex-user-context/scripts/run_codex_user_context.sh "리뷰해줘" --file src/app.py
```

### Gemini vs Codex 차이점

| | Gemini | Codex |
|---|---|---|
| **자동 실행** | Hook이 자동 트리거 | 자동 실행 없음 (Skill로 수동 호출) |
| **코드 실행** | 불가 | 샌드박스 내 실행 가능 |
| **샌드박스 모드** | 없음 | `read-only` / `workspace-write` / `danger-full-access` |
| **SDK 폴백** | CLI 실패 시 SDK(API key) 자동 폴백 | 모델 자동 폴백 (`gpt-5.3-codex` → `gpt-5`) |
| **피드백 저장** | `plans/gemini/gemini_feedback.md` | `plans/codex/codex_feedback.md` |

### 피드백 기록

각 에이전트의 피드백은 프로젝트의 `plans/` 디렉토리에 분리 저장됩니다:

```
<프로젝트>/
└── plans/
    ├── gemini/
    │   ├── gemini_feedback.md     # Gemini 피드백 (Markdown)
    │   └── a2a_events.jsonl       # JSONL 이벤트 버스 (설정 시)
    └── codex/
        └── codex_feedback.md      # Codex 피드백 (Markdown)
```

상태 파일 (communicator 루트):
- 쿨다운: `.cooldown_state.json`
- 에러 이력: `.error_history.json`
- 비동기 작업: `.scheduler_jobs.json`

피드백 경로 오버라이드:
- `GEMINI_FEEDBACK_DIR` 환경변수로 Gemini 피드백 경로를 변경할 수 있습니다.
- `CODEX_FEEDBACK_DIR` 환경변수로 Codex 피드백 경로를 변경할 수 있습니다.
- `install --target` 시 Hook에 `GEMINI_FEEDBACK_DIR`이 자동 주입되어 프로젝트별로 분리됩니다.

## 2) 주요 기능 (사용자 관점)

### A. 운영/진단 CLI (`src/cli.py`)

```bash
python3 src/cli.py <command>
```

| 명령 | 설명 |
|------|------|
| `doctor` | 설정/환경/Hook/JSONL 상태 진단 |
| `status` | 현재 설정값 + 상태 파일 요약 |
| `stats [--jsonl]` | 피드백 또는 JSONL 통계 |
| `search <keyword> [--source --date]` | 피드백 검색 (`--jsonl` 지원) |
| `chain <id>` / `chain --list` | request/message 체인 추적 |
| `test` | 내장 자동 테스트 실행 |
| `clear [--jsonl]` | 상태 파일 초기화 |
| `install --target <dir>` | 다른 프로젝트에 Hook+Skill 설치 |
| `uninstall --target <dir>` | 설치 제거 |

### B. Hook 기반 자동화

#### 1) PreToolUse (`src/hooks/hook_pre_tool.py`)
- Bash 명령만 검사
- 차단(`block`):
  - `rm -rf`
  - `git push --force` / `git push -f`
  - `git reset --hard`
  - `git clean -f`
  - DB 파괴 명령(`DROP`, `TRUNCATE`) 컨텍스트 매칭 시
- 경고(`warn`):
  - `git branch -D`
  - `git restore .`
  - `chmod 777`
  - `kill -9`
  - `pip install <패키지>` (requirements 파일 기반이 아닌 단일 패키지 설치)

#### 2) PostToolUse (`src/hooks/hook_auto_task.py`)
- `Write`/`Edit` 도구 이후만 동작
- 감시 확장자(`watch_extensions`)만 대상
- `exclude_files`는 제외
- 파일별 쿨다운(`cooldown_seconds_per_file`) 적용
- 코드 확장자면 `code_evaluation_prompt`, 아니면 `evaluation_prompt` 사용
- `async_mode=true`면 백그라운드 비동기 실행

#### 3) Stop Hook (`src/hooks/hook_stop.py`)
- 응답 텍스트가 Plan으로 분류되면 Gemini 평가 요청
- transcript 에러를 스캔해 임계치 도달 시 Gemini 에러 분석 실행
- 글로벌 쿨다운(`error_detection.global_cooldown_seconds`) 적용

### C. Skill 도구

#### 1) Gemini CLI (`skills/gemini-cli-context/`)
```bash
zsh scripts/run_gemini_cli.sh "리뷰해줘" --file src/app.py
zsh scripts/run_gemini_cli.sh --model gemini-2.5-pro "심층 분석해줘" --file src/cli.py
zsh scripts/run_gemini_cli.sh --save "리뷰해줘" --file src/app.py
cat src/app.py | zsh scripts/run_gemini_cli.sh "리뷰해줘"
```

옵션: `--model`, `--file`, `--save`, `--dry-run`, `--yolo`

#### 2) Codex CLI (`skills/codex-user-context/`)
```bash
zsh scripts/run_codex_user_context.sh "리뷰해줘" --file src/app.py
zsh scripts/run_codex_user_context.sh --sandbox danger-full-access "외부 API 조사해줘"
zsh scripts/run_codex_user_context.sh --full-auto --save "설계안 작성해줘"
zsh scripts/run_codex_user_context.sh --model gpt-5 "코드 리뷰해줘"
```

옵션: `--model`, `--file`, `--save`, `--dry-run`, `--full-auto`, `--sandbox`, `--project`

샌드박스 모드:
- `read-only` — 기본값, 네트워크 차단, 파일 읽기만
- `workspace-write` — 작업 디렉토리 쓰기 허용
- `danger-full-access` — 네트워크 포함 전체 접근

#### 3) Cross-Agent Bridge (`skills/cross-agent-bridge/scripts/bridge.py`)
```bash
python3 bridge.py review --file <file>           # Gemini 리뷰
python3 bridge.py codex-review --file <file>      # Codex 리뷰
python3 bridge.py parse --file <output> --agent auto  # 출력 파싱
python3 bridge.py doctor                          # 환경 점검
python3 bridge.py setup                           # 설정 파일 생성
```

#### 4) Agent Parser (`skills/agent-parser/scripts/parse.py`)
- Codex/Gemini/Claude 출력 자동 감지 파싱
- `--format summary|json`, `--agent auto|codex|gemini|claude`

#### 5) Gemini Reviewer (`skills/gemini-reviewer/scripts/evaluate.py`)
- 독립형 코드/문서 리뷰
- CLI 우선, 실패 시 SDK 폴백
- `--save`로 피드백 파일 저장

#### 6) 설치 스크립트 (`skills/install/scripts/run_install.sh`)
- 현재/대상 프로젝트에 Hook+Skill 설치/제거

## 3) 설치 방법

### 1단계. 의존성 설치
```bash
pip install -r requirements.txt
```

`requirements.txt`:
- `google-genai>=1.0.0`
- `google-auth>=2.20.0`
- `httpx>=0.24.0`

### 2단계. 환경변수 설정
`.env` 생성:
```env
GEMINI_API_KEY=your-api-key-here
GEMINI_OAUTH_CLIENT_ID=...
GEMINI_OAUTH_CLIENT_SECRET=...
```

주의:
- Gemini CLI 인증만 사용할 경우 API 키 없이도 동작 가능
- SDK 폴백까지 안정적으로 쓰려면 API 키 권장
- Codex는 OpenAI 계정 로그인만 필요 (별도 API 키 불필요)

### 3단계. 설정 확인
기본 설정 파일: `config/config.json`

중요 항목:
- `watch_extensions`, `exclude_files`
- `cooldown_seconds_per_file`
- `async_mode`
- `jsonl_bus.enabled/path`
- `error_detection.*`

### 4단계. Hook 설치
```bash
python3 src/cli.py install --target <프로젝트_경로>
```

설치 시 동작:
- `PreToolUse`, `PostToolUse`, `Stop` Hook이 대상 프로젝트 `.claude/settings.local.json`에 등록됩니다.
- 피드백 기록 Hook(`PostToolUse`, `Stop`)에는 `GEMINI_FEEDBACK_DIR=<target>/plans/gemini`가 자동 주입됩니다.
- Skills 6개가 심링크로 연결됩니다 (Gemini/Codex 모두 포함).

제거:
```bash
python3 src/cli.py uninstall --target <프로젝트_경로>
```

### 5단계. 동작 점검
```bash
python3 src/cli.py doctor
python3 src/cli.py status
python3 src/cli.py test
```

## 4) 반드시 알아야 할 주의사항

- 실제 동작은 `src/`와 `config/config.json` 기준입니다.
- Hook 자동 평가는 Gemini만 트리거합니다. Codex는 Skill로 수동 호출해야 합니다.
- 자동 평가는 Hook 입력 조건 + 확장자 + 제외/쿨다운을 모두 통과해야 실행됩니다.
- 동일 파일은 쿨다운 내 재평가되지 않습니다.
- `exclude_files` 경로에 걸리면 어떤 변경이어도 평가되지 않습니다.
- 위험 명령은 PreTool Hook에서 실제로 차단될 수 있습니다.
- `async_mode=true`면 즉시 결과가 아닌 지연 기록입니다.
- JSONL 이벤트를 켜면 이력 분석(`stats --jsonl`, `search --jsonl`, `chain`)이 가능하지만 파일이 커질 수 있습니다.
- `clear --jsonl` 실행 시 이벤트 로그까지 삭제됩니다.
- Codex 샌드박스 기본값은 `read-only`이며 네트워크가 차단됩니다. 네트워크가 필요하면 `--sandbox danger-full-access`를 명시해야 합니다.

## 5) 자주 쓰는 운영 명령

```bash
# 전체 상태 진단
python3 src/cli.py doctor

# 현재 설정/상태 보기
python3 src/cli.py status

# JSONL 통계
python3 src/cli.py stats --jsonl

# JSONL 검색
python3 src/cli.py search timeout --jsonl --agent gemini

# 체인 추적
python3 src/cli.py chain --list
python3 src/cli.py chain <request_id_prefix>

# 상태 초기화
python3 src/cli.py clear
python3 src/cli.py clear --jsonl
```

## 6) 문제 발생 시 빠른 체크리스트

1. `python3 src/cli.py doctor`에서 에러/경고 확인
2. `.env`와 `config/config.json`의 경로/키/모델 확인
3. 대상 프로젝트 `.claude/settings.local.json`에 Hook 등록 여부 확인
4. `watch_extensions`, `exclude_files`, 쿨다운 때문에 스킵된 것은 아닌지 확인
5. Gemini: CLI 경로(`gemini_cmd`)와 SDK 설치 여부 확인
6. Codex: OpenAI 계정 로그인 상태와 모델 접근 권한 확인
7. 필요 시 `python3 src/cli.py clear` 후 재시도
