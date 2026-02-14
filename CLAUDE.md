# CLAUDE.md — Claude-Gemini Communicator

## 프로젝트 개요

Claude Code가 계획/문서를 작성하면 Gemini가 자동으로 평가하는 협업 시스템.
Claude Code Hooks를 통해 Write/Edit 도구 사용 시 자동 트리거됩니다.

# 최근 사용 했던 LLM 정보
- 세션 id : "session ID: 8aafa760-be1e-4993-a1f9-780453b2c88e"
- 세션 디렉토리 및 작업 경로 : /Users/jaehyuntak/.gemini/skills/skill_evaluator/plans

## 현재 상태: Phase 4 구현 완료

### Phase 1 (MVP) — 완료
- Gemini CLI subprocess 기반 평가 파이프라인
- PostToolUse Hook + Stop Hook
- 쿨다운 메커니즘, 피드백 로그

### Phase 2 — 완료
- google-genai SDK 직접 호출 (Dual Mode: SDK 우선, CLI fallback)
- 비동기 모드 (fire-and-forget 백그라운드)
- 복수 API key + 복수 모델 자동 순회 (429 Rate Limit 대응)
- `.env` 기반 환경변수 관리

### Phase 3 — 완료
- A2A 구조화된 JSON 메시지 프로토콜
- 평가 요청/응답 JSON 스키마 강제 + 잘린 JSON 자동 복구
- `a2a_schema_enabled` 설정으로 활성화 (기본 비활성, 하위 호환)

### Phase 4 — 완료
- **에러 감지**: Stop Hook에서 transcript 스캔 → 에러 패턴 매칭
- **Lazy Analysis**: 심각도별 가중치 (Critical 1회, High 1회, Medium 2회, Low 3회)
- **에러 해시 정규화**: 경로/라인/시간 마스킹으로 동일 에러 인식
- **file lock**: fcntl로 gemini_feedback.md 동시 쓰기 보호
- **Gemini Code Assist**: `.gemini/review.md`로 PR 리뷰 규칙 설정

### 미구현 (장기 비전)
- Agent Teams 통합 (`claude --teammate-mode tmux`)
- Gemini Extension 개발
- Reference Architecture 기반 리팩토링 (Scheduler/Router/Memory 분리)
  - 참고: `plans/reference_communicator.md`

## 핵심 파일

| 파일 | 역할 |
|---|---|
| `scripts/a2a_bridge.py` | 핵심 오케스트레이터 (SDK/CLI 이중화, 비동기, 에러 감지, A2A) |
| `scripts/config.json` | 전체 설정 (SDK, 에러 감지, 프롬프트 등) |
| `scripts/hook_auto_task.py` | PostToolUse Hook (.md Write/Edit → Gemini 평가) |
| `scripts/hook_stop.py` | Stop Hook (Plan 감지 + 에러 감지) |
| `scripts/async_runner.py` | 비동기 백그라운드 Gemini 호출 실행기 |
| `scripts/setup.sh` | 의존성 설치 스크립트 |
| `.claude/settings.local.json` | Hook 등록 설정 |
| `.gemini/review.md` | Gemini Code Assist PR 리뷰 규칙 |
| `.env` | API key 저장 (gitignore) |
| `gemini_feedback.md` | Gemini 평가 결과 로그 (append-only) |

## 디렉토리 구조

```
claude-gemini-communicator/
├── CLAUDE.md                ← 이 파일
├── README.md                ← 프로젝트 소개 + 사용법
├── requirements.txt         ← Python 패키지 의존성
├── .gitignore
├── .env                     ← API key (gitignore)
├── .env.example             ← API key 템플릿
├── .claude/
│   └── settings.local.json  ← Hook 설정 (PostToolUse, Stop)
├── .gemini/
│   └── review.md            ← Gemini Code Assist PR 리뷰 규칙
├── scripts/
│   ├── config.json          ← 전체 설정
│   ├── a2a_bridge.py        ← 핵심 오케스트레이터
│   ├── hook_auto_task.py    ← PostToolUse Hook
│   ├── hook_stop.py         ← Stop Hook (Plan + Error)
│   ├── async_runner.py      ← 비동기 실행기
│   ├── setup.sh             ← 의존성 설치
│   ├── .cooldown_state.json ← 런타임 생성 (gitignore)
│   └── .error_history.json  ← 런타임 생성 (gitignore)
├── plans/
│   ├── test.md              ← 테스트용 문서
│   ├── phase2_implementation_plan.md
│   ├── a2a_message_schema.md
│   ├── phase4_architecture.md
│   ├── error_auto_injection.md
│   └── reference_communicator.md  ← 장기 비전 아키텍처
└── gemini_feedback.md       ← Gemini 피드백 로그
```

## 아키텍처

```
Hook Scripts (hook_auto_task.py, hook_stop.py)
    │
    ▼
a2a_bridge.py → call_gemini() 오케스트레이터
    │
    ├─ SDK: _call_gemini_with_api_key() → google-genai
    │     └─ 429 → 다음 API key/모델 자동 전환
    │     └─ 실패 → CLI fallback
    │
    ├─ CLI: _call_gemini_cli() → subprocess (Phase 1)
    │
    ├─ Async: call_gemini_async() → async_runner.py (백그라운드)
    │
    └─ Error: scan_transcript_for_errors() → check_error_and_analyze()
              → Lazy Analysis (심각도별 임계값)
              → Gemini 분석 → "[SYSTEM ADVISORY]" prefix로 Claude에 주입
```

## 동작 흐름

### PostToolUse Hook (Write/Edit → .md 파일)
1. Claude가 `.md` 파일을 Write/Edit
2. `hook_auto_task.py`가 stdin으로 Hook JSON 수신
3. 확장자 확인 → 제외 파일 확인 → 쿨다운 확인 (5분)
4. `call_gemini()` → SDK/CLI → 피드백 저장 + Claude에 주입

### Stop Hook (Plan 감지 + 에러 감지)
1. Claude 응답 완료 시 `hook_stop.py`가 stdin 수신
2. **Plan 감지**: 텍스트 300자 이상 → Gemini 분류 → "예" → 평가
3. **에러 감지**: transcript 마지막 50줄 스캔 → 에러 패턴 매칭
   - 에러 해시 정규화 (경로/시간 마스킹)
   - Lazy Analysis: 심각도별 임계값 (Critical 1회, Medium 2회 등)
   - 이미 분석된 에러 재트리거 방지
   - 전역 쿨다운 60초

### PostToolUse Hook JSON 구조 (실험 확인)
```json
{
  "tool_name": "Bash",
  "tool_input": {"command": "...", "description": "..."},
  "tool_response": {
    "stdout": "...",
    "stderr": "...",
    "interrupted": false
  }
}
```
**주의: PostToolUse Hook은 Bash 실패(exit code != 0) 시 발동하지 않음!**
→ 에러 감지는 Stop Hook의 transcript 스캔으로 해결.

## 핵심 설정 (`scripts/config.json`)

### 기본 설정
| 키 | 기본값 | 설명 |
|---|---|---|
| `gemini_cmd` | `/usr/local/bin/gemini` | Gemini CLI 경로 |
| `gemini_timeout` | `90` | 호출 타임아웃 (초) |
| `cooldown_seconds_per_file` | `300` | 파일별 쿨다운 (초) |
| `min_content_length` | `300` | Stop Hook 최소 길이 |
| `watch_extensions` | `[".md"]` | 감시 확장자 |
| `exclude_files` | `["gemini_feedback.md"]` | 제외 파일 |

### SDK 설정
| 키 | 기본값 | 설명 |
|---|---|---|
| `sdk.enabled` | `true` | SDK 모드 |
| `sdk.model` | `gemini-2.5-flash` | 기본 모델 |
| `sdk.fallback_models` | `["gemini-2.0-flash", "gemini-1.5-flash"]` | 폴백 모델 |
| `sdk.fallback_to_cli` | `true` | CLI 폴백 |
| `async_mode` | `false` | 비동기 모드 |

### 에러 감지 설정 (Phase 4)
| 키 | 기본값 | 설명 |
|---|---|---|
| `error_detection.enabled` | `true` | 에러 감지 활성화 |
| `error_detection.tail_lines` | `50` | transcript 스캔 줄 수 |
| `error_detection.global_cooldown_seconds` | `60` | 분석 간 최소 간격 |
| `error_detection.thresholds` | `{"critical":1,"high":1,"medium":2,"low":3}` | 심각도별 트리거 횟수 |

### A2A 설정 (Phase 3)
| 키 | 기본값 | 설명 |
|---|---|---|
| `a2a_schema_enabled` | `false` | 구조화 JSON 모드 |

## 의존성

- Python 3.13+ (3.13.6 검증됨)
- `google-genai` >= 1.0.0
- `google-auth` >= 2.20.0
- Gemini CLI (`/usr/local/bin/gemini`, CLI fallback용)
- Claude Code (hooks 기능)

설치: `bash scripts/setup.sh` 또는 `pip install -r requirements.txt`

## 테스트 방법

```bash
# 1. SDK 호출 테스트
python3 -c "import sys; sys.path.insert(0,'scripts'); from a2a_bridge import load_config, call_gemini; print(call_gemini('Hi','Say OK.',load_config())[:100])"

# 2. PostToolUse Hook 테스트
rm -f scripts/.cooldown_state.json
echo '{"tool_name":"Write","tool_input":{"file_path":"plans/test.md"}}' | python3 scripts/hook_auto_task.py

# 3. 에러 감지 테스트 (단위)
python3 -c "import sys; sys.path.insert(0,'scripts'); from a2a_bridge import normalize_error_text, hash_error, classify_error_severity; print(hash_error('TypeError: foo')); print(classify_error_severity('ModuleNotFoundError: bar'))"

# 4. CLI 폴백 테스트
python3 -c "import sys; sys.path.insert(0,'scripts'); from a2a_bridge import load_config, call_gemini; c=load_config(); c['sdk']={'enabled':False}; print(call_gemini('Hi','Say OK.',c)[:100])"

# 5. 피드백 실시간 확인
tail -f gemini_feedback.md

# 6. 상태 파일 초기화 (재테스트 시)
rm -f scripts/.cooldown_state.json scripts/.error_history.json
```

## 롤백

| 기능 | 롤백 방법 |
|---|---|
| SDK → CLI | `config.json`에서 `"sdk": {"enabled": false}` |
| 에러 감지 끄기 | `"error_detection": {"enabled": false}` |
| A2A 스키마 끄기 | `"a2a_schema_enabled": false` |
| 비동기 끄기 | `"async_mode": false` |
| 전체 Phase 1 복귀 | SDK + 에러감지 + A2A 모두 비활성화 |

## Git 정보

- 리포: https://github.com/goodand/claude-gemini-communicator.git
- 브랜치: main (단독 개발)
- Push Protection: OAuth 클라이언트 정보는 `.env` 환경변수로 관리 (코드에 하드코딩 금지)

## 주의사항

- `gemini_feedback.md`는 자동으로 수정되는 파일이므로 수동 편집 시 주의
- `.cooldown_state.json`, `.error_history.json`은 런타임 자동 생성 (.gitignore)
- Hook 스크립트는 항상 `exit(0)` 보장 → Claude 정상 동작에 영향 없음
- **PostToolUse Hook은 Bash 실패 시 발동하지 않음** — 에러 감지는 Stop Hook에서 처리
- 무료 티어 API key는 모델별 일일 한도 존재 (자동 순회로 대응)
- `.env` 파일 절대 커밋 금지 (.gitignore 포함)
