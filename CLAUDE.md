# CLAUDE.md — Claude-Gemini Communicator

## 프로젝트 개요

Claude Code가 계획/문서를 작성하면 Gemini가 자동으로 평가하는 협업 시스템.
Claude Code Hooks를 통해 Write/Edit 도구 사용 시 자동 트리거됩니다.

## 현재 상태: Phase 2 구현 완료

### Phase 1 (MVP) — 완료
- Gemini CLI subprocess 기반 평가 파이프라인
- PostToolUse Hook + Stop Hook
- 쿨다운 메커니즘, 피드백 로그

### Phase 2 — 구현 완료
- **google-genai SDK 직접 호출** (subprocess 대비 속도 향상)
- **Dual Mode**: SDK 우선 → CLI fallback (SDK 실패 시 자동 전환)
- **비동기 모드**: fire-and-forget 백그라운드 평가 (config 스위치)
- **복수 API key 지원**: `.env`에서 로드
- **OAuth 인증 인프라**: Gemini CLI 토큰 재사용 준비 (스코프 제한으로 현재 API key 사용)

## 핵심 파일

| 파일 | 역할 |
|---|---|
| `scripts/a2a_bridge.py` | 핵심 오케스트레이터 (SDK/CLI 이중화, 비동기, 쿨다운, 피드백) |
| `scripts/config.json` | 전체 설정 (SDK, 타임아웃, 쿨다운, 프롬프트 등) |
| `scripts/hook_auto_task.py` | PostToolUse Hook (.md Write/Edit → Gemini 평가) |
| `scripts/hook_stop.py` | Stop Hook (Plan 감지 → Gemini 평가) |
| `scripts/async_runner.py` | 비동기 백그라운드 Gemini 호출 실행기 |
| `scripts/setup.sh` | 의존성 설치 스크립트 |
| `.claude/settings.local.json` | Hook 등록 설정 |
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
├── scripts/
│   ├── config.json          ← 전체 설정
│   ├── a2a_bridge.py        ← 핵심 오케스트레이터
│   ├── hook_auto_task.py    ← PostToolUse Hook
│   ├── hook_stop.py         ← Stop Hook
│   ├── async_runner.py      ← 비동기 실행기
│   ├── setup.sh             ← 의존성 설치
│   └── .cooldown_state.json ← 런타임 생성
├── plans/
│   ├── test.md              ← 테스트용 문서
│   └── phase2_implementation_plan.md ← Phase 2 계획서
└── gemini_feedback.md       ← Gemini 피드백 로그
```

## 아키텍처

```
Hook Scripts (hook_auto_task.py, hook_stop.py)
    │
    ▼
a2a_bridge.py → call_gemini() 오케스트레이터
    │
    ├─ SDK 경로: _call_gemini_sdk() → google-genai (API key)
    │     └─ 실패 시 → CLI fallback
    │
    ├─ CLI 경로: _call_gemini_cli() → subprocess (Phase 1)
    │
    └─ Async 경로: call_gemini_async() → async_runner.py (백그라운드)
```

**인증 우선순위:** `.env` API key → OAuth credentials → CLI fallback

## 동작 흐름

### PostToolUse Hook (Write/Edit → .md 파일)
1. Claude가 `.md` 파일을 Write/Edit
2. `hook_auto_task.py`가 stdin으로 Hook JSON 수신
3. 확장자 확인 → 제외 파일 확인 → 쿨다운 확인 (동일 파일 5분 내 재호출 방지)
4. async_mode 확인:
   - **동기 (기본)**: `call_gemini()` → SDK 우선, 실패 시 CLI fallback → 피드백 저장 + Claude에 주입
   - **비동기**: `call_gemini_async()` → 즉시 리턴 + 백그라운드에서 평가 → `gemini_feedback.md`에 기록

### Stop Hook (Plan 감지)
1. Claude 응답 완료 시 `hook_stop.py`가 stdin으로 Stop JSON 수신
2. 마지막 assistant 텍스트 추출
3. 길이 < 300자 → 즉시 패스 (빠른 필터)
4. Gemini에 Plan 여부 분류 요청 ("예"/"아니오") — 항상 동기
5. "예" → async_mode에 따라 동기/비동기 전체 평가

## 핵심 설정 (`scripts/config.json`)

### 기본 설정 (Phase 1)
| 키 | 기본값 | 설명 |
|---|---|---|
| `gemini_cmd` | `/usr/local/bin/gemini` | Gemini CLI 절대 경로 |
| `gemini_timeout` | `90` | 호출 타임아웃 (초) |
| `cooldown_seconds_per_file` | `300` | 파일별 재호출 방지 쿨다운 (초) |
| `min_content_length` | `300` | Stop Hook 최소 텍스트 길이 |
| `watch_extensions` | `[".md"]` | 감시 대상 확장자 |
| `exclude_files` | `["gemini_feedback.md"]` | 제외 파일명 |

### SDK 설정 (Phase 2)
| 키 | 기본값 | 설명 |
|---|---|---|
| `sdk.enabled` | `true` | SDK 모드 활성화 |
| `sdk.model` | `gemini-2.5-flash` | 사용 모델 |
| `sdk.fallback_to_cli` | `true` | SDK 실패 시 CLI 폴백 |
| `sdk.api_key_env` | `GEMINI_API_KEY` | API key 환경변수명 |
| `sdk.max_output_tokens` | `2048` | 최대 출력 토큰 |
| `sdk.temperature` | `0.3` | 생성 온도 |
| `async_mode` | `false` | 비동기 모드 (fire-and-forget) |
| `async_timeout` | `120` | 비동기 프로세스 타임아웃 (초) |

## 의존성

- Python 3.13+ (3.13.6 검증됨)
- `google-genai` >= 1.0.0 (SDK 모드)
- `google-auth` >= 2.20.0 (OAuth 인프라)
- Gemini CLI (`/usr/local/bin/gemini`, CLI fallback용)
- Claude Code (hooks 기능 필요)

설치: `bash scripts/setup.sh` 또는 `pip install -r requirements.txt`

## 테스트 방법

```bash
# 1. SDK 설치 확인
python3 -c "from google import genai; print('OK')"

# 2. SDK 직접 호출 테스트
python3 -c "import sys; sys.path.insert(0,'scripts'); from a2a_bridge import load_config, _call_gemini_sdk; print(_call_gemini_sdk('Hello','Say OK.',load_config()))"

# 3. Dual Mode 테스트 (call_gemini 오케스트레이터)
python3 -c "import sys; sys.path.insert(0,'scripts'); from a2a_bridge import load_config, call_gemini; r=call_gemini('Hi','Say OK.',load_config()); print('SDK' if '[FALLBACK]' not in r else 'CLI', r[:100])"

# 4. Hook 통합 테스트 (쿨다운 초기화 후)
rm -f scripts/.cooldown_state.json
echo '{"tool_name":"Write","tool_input":{"file_path":"plans/test.md"}}' | python3 scripts/hook_auto_task.py

# 5. 피드백 실시간 확인
tail -f gemini_feedback.md

# 6. 폴백 테스트 (SDK 비활성화)
python3 -c "import sys; sys.path.insert(0,'scripts'); from a2a_bridge import load_config, call_gemini; c=load_config(); c['sdk']={'enabled':False}; print(call_gemini('Hi','Say OK.',c)[:100])"
```

## 롤백

`config.json`에서 `"sdk": {"enabled": false}` 설정만으로 Phase 1 동작으로 즉시 복귀 가능.

## Phase 3 확장 계획 (미구현)

- A2A 메시지 스키마 완전 구현
- Agent Teams 완전 통합 (`claude --teammate-mode tmux`)
- Gemini Extension 개발
- Rate Limit 자동 감지 + 모델/키 자동 전환

## 주의사항

- `gemini_feedback.md`는 자동으로 수정되는 파일이므로 수동 편집 시 주의
- `.cooldown_state.json`은 런타임에 자동 생성/갱신됨 (.gitignore에 포함)
- Hook 스크립트는 항상 `exit(0)`을 보장하여 Claude 정상 동작에 영향 없음
- 무료 티어 API key는 모델별 일일 한도 존재 (`gemini-2.0-flash` 한도 소진 시 `gemini-2.5-flash` 사용)
- `.env` 파일은 절대 커밋하지 않을 것 (.gitignore 포함)
