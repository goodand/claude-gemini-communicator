# Claude-Gemini Communicator 사용자 매뉴얼

이 문서는 현재 코드베이스(`src/`, `skills/`, `config/`) 기준으로 작성된 사용자용 안내서입니다.  
기존 `README.md`는 구버전으로 간주하고 제외했습니다.

## 1) 이 서비스가 하는 일

이 서비스는 Claude/Codex 작업 흐름에 Hook을 붙여, 파일 변경/응답 종료 시 Gemini(CLI/SDK) 평가를 자동 수행하고 결과를 기록합니다.

핵심 자동 동작:
- `PreToolUse Hook`: 위험한 Bash 명령을 사전 차단 또는 경고
- `PostToolUse Hook`: `Write/Edit` 후 대상 파일(`watch_extensions`) 자동 평가
- `Stop Hook`: 응답 완료 시
  - 개발 계획 문서(Plan)로 판단되면 평가
  - transcript에서 반복 에러를 감지하면 에러 분석

기록 파일:
- Markdown 피드백: `plans/gemini/gemini_feedback.md`
- JSONL 이벤트 버스: `plans/gemini/a2a_events.jsonl` (설정 시)
- 상태 파일:
  - 쿨다운: `.cooldown_state.json`
  - 에러 이력: `.error_history.json`
  - 비동기 작업: `.scheduler_jobs.json`

피드백 경로 오버라이드/분리:
- `GEMINI_FEEDBACK_DIR` 환경변수를 지정하면 피드백 저장 경로가 `<GEMINI_FEEDBACK_DIR>/gemini_feedback.md`로 바뀝니다.
- `install --target` 시 PostToolUse/Stop Hook 명령에 `GEMINI_FEEDBACK_DIR=<target>/plans/gemini`가 자동 주입되어, 대상 프로젝트별로 피드백 파일이 분리됩니다.

## 2) 주요 기능 (사용자 관점)

### A. 운영/진단 CLI (`src/cli.py`)

실행 예시:
```bash
python3 src/cli.py <command>
# 또는 환경에 따라 python3.13 src/cli.py <command>
```

명령:
- `doctor`: 설정/환경/Hook/JSONL 상태 진단
- `status`: 현재 설정값 + 상태 파일 요약
- `stats [--jsonl]`: 피드백 또는 JSONL 통계
- `search <keyword> [--source --date]` 또는 `search --jsonl ...`: 검색
- `chain <id>` 또는 `chain --list`: request/message 체인 추적
- `test`: 내장 자동 테스트 실행
- `clear [--jsonl]`: 상태 파일 초기화
- `install --target <dir>`: 다른 프로젝트에 Hook+Skill 설치
- `uninstall --target <dir>`: 설치 제거

### B. Hook 기반 자동화

#### 1) PreToolUse (`src/hooks/hook_pre_tool.py`)
- Bash 명령만 검사
- 차단(`block`) 예시:
  - `rm -rf`
  - `git push --force` / `git push -f`
  - `git reset --hard`
  - `git clean -f`
  - DB 파괴 명령(`DROP`, `TRUNCATE`) 컨텍스트 매칭 시
- 경고(`warn`) 예시:
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
- 응답 텍스트가 Plan으로 분류되면 평가
- transcript 에러를 스캔해 임계치 도달 시 Lazy Analysis 실행
- 글로벌 쿨다운(`error_detection.global_cooldown_seconds`) 적용

### C. Skill 도구 (수동 실행형)

#### 1) Cross-Agent Bridge (`skills/cross-agent-bridge/scripts/bridge.py`)
통합 CLI:
```bash
python3 skills/cross-agent-bridge/scripts/bridge.py review --file <file>
python3 skills/cross-agent-bridge/scripts/bridge.py codex-review --file <file> --model gpt-5
python3 skills/cross-agent-bridge/scripts/bridge.py parse --file <output.jsonl> --agent auto
python3 skills/cross-agent-bridge/scripts/bridge.py doctor
python3 skills/cross-agent-bridge/scripts/bridge.py setup
```

지원 기능:
- Gemini 리뷰 (`review`)
- Codex 리뷰 (`codex-review`, `codex exec` 사용)
- Codex/Gemini/Claude 출력 파싱 (`parse`)
- 환경 점검 (`doctor`)
- 초기 설정 파일 생성 (`setup`)

#### 2) Agent Parser (`skills/agent-parser/scripts/parse.py`)
- Codex/Gemini/Claude 출력 자동 감지 파싱
- `--format summary|json`, `--agent auto|codex|gemini|claude`

#### 3) Gemini Reviewer (`skills/gemini-reviewer/scripts/evaluate.py`)
- 독립형 코드/문서 리뷰
- CLI 우선, 실패 시 SDK 폴백
- `--save`로 피드백 파일 저장

#### 4) 설치 스크립트 (`skills/install/scripts/run_install.sh`)
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
- Gemini CLI 인증만 사용할 경우 API 키 없이도 일부 경로 동작 가능
- SDK 폴백까지 안정적으로 쓰려면 API 키 권장

### 3단계. 설정 확인
기본 설정 파일:
- `config/config.json`

중요 항목:
- `watch_extensions`, `exclude_files`
- `cooldown_seconds_per_file`
- `async_mode`
- `jsonl_bus.enabled/path`
- `error_detection.*`

### 4단계. Hook 설치
현재 프로젝트 또는 타 프로젝트에 설치:
```bash
python3 src/cli.py install --target <프로젝트_경로>
# 또는
zsh skills/install/scripts/run_install.sh --target <프로젝트_경로>
```

설치 시 동작:
- `PreToolUse`, `PostToolUse`, `Stop` Hook이 대상 프로젝트 `.claude/settings.local.json`에 등록됩니다.
- 피드백 기록 Hook(`PostToolUse`, `Stop`)에는 `GEMINI_FEEDBACK_DIR=<target>/plans/gemini`가 자동 주입됩니다.
- 따라서 피드백이 communicator 루트가 아니라 대상 프로젝트 `plans/gemini/gemini_feedback.md`로 분리 저장됩니다.

제거:
```bash
python3 src/cli.py uninstall --target <프로젝트_경로>
# 또는
zsh skills/install/scripts/run_install.sh --uninstall --target <프로젝트_경로>
```

### 5단계. 동작 점검
```bash
python3 src/cli.py doctor
python3 src/cli.py status
python3 src/cli.py test
```

## 4) 반드시 알아야 할 주의사항

- `README.md`가 아니라 실제 동작은 `src/`와 `config/config.json` 기준입니다.
- 자동 평가는 파일 저장 직후가 아니라, Hook 입력 조건 + 확장자 + 제외/쿨다운을 모두 통과해야 실행됩니다.
- 동일 파일은 쿨다운 내 재평가되지 않습니다.
- `exclude_files` 경로에 걸리면 어떤 변경이어도 평가되지 않습니다.
- 위험 명령은 PreTool Hook에서 실제로 차단될 수 있습니다.
- `async_mode=true`면 즉시 결과가 아닌 지연 기록입니다.
- JSONL 이벤트를 켜면 이력 분석(`stats --jsonl`, `search --jsonl`, `chain`)이 가능하지만 파일이 커질 수 있습니다.
- `clear --jsonl` 실행 시 이벤트 로그까지 삭제됩니다.

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
5. Gemini CLI 경로(`gemini_cmd`)와 SDK 설치 여부 확인  
6. 필요 시 `python3 src/cli.py clear` 후 재시도
