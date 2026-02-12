# Phase 2 구현 계획: Claude-Gemini Communicator

## Context

Phase 1(MVP)은 완료 및 검증됨. Claude Code Hooks → Gemini CLI subprocess 호출 → 피드백 저장/주입 파이프라인이 정상 동작 중.
Phase 2에서는 (1) SDK 직접 호출로 성능 개선, (2) 비동기 모드로 블로킹 해소, (3) A2A 스키마 확장을 목표로 한다.

**사용자 결정 사항:**
- 인증: Gemini CLI OAuth 인증 재사용 (`~/.gemini/oauth_creds.json`)
- 호환: Dual Mode (SDK 우선, CLI fallback)
- 비동기: SDK 속도 개선 + fire-and-forget 백그라운드 모드 모두 구현

---

## 아키텍처 변경

```
Hook Scripts (변경 최소화)
    │
    ▼
a2a_bridge.py (오케스트레이터)
    │
    ├─ SDK 경로: _call_gemini_sdk() → google-generativeai
    │     └─ 인증: API KEY > OAuth(CLI 재사용) > 실패 시 CLI fallback
    │
    ├─ CLI 경로: _call_gemini_cli() → subprocess (기존 Phase 1)
    │
    └─ Async 경로: call_gemini_async() → async_runner.py (백그라운드 프로세스)
```

**핵심 원칙:** `call_gemini()` 함수 시그니처 유지 → Hook 스크립트 변경 최소화

---

## 수정 대상 파일 (5개)

### 1. `scripts/a2a_bridge.py` — 핵심 변경

**추가할 함수들:**
- `_sdk_available()` — SDK 설치 여부 확인 (lazy import)
- `_read_file_content(file_path)` — SDK용 파일 내용 읽기 (CLI는 경로만 전달했지만 SDK는 내용 필요)
- `_load_oauth_credentials(sdk_config)` — `~/.gemini/oauth_creds.json`에서 Gemini CLI OAuth 토큰 로드 → `google.oauth2.credentials.Credentials` 객체 생성 → 만료 시 자동 갱신
- `_call_gemini_sdk(content, prompt, config, file_path)` — SDK 직접 호출
- `_call_gemini_cli(content, prompt, config, file_path)` — 기존 subprocess 로직 (이름만 변경)
- `call_gemini_async(content, prompt, config, file_path, source)` — 백그라운드 프로세스 spawn

**수정할 함수:**
- `call_gemini()` — 오케스트레이터로 리팩토링: SDK 시도 → 실패 시 CLI fallback

**OAuth 인증 방식:**
```
인증 우선순위:
1. GEMINI_API_KEY 환경변수 → genai.configure(api_key=...)
2. ~/.gemini/oauth_creds.json → Credentials 객체 → genai.configure(credentials=...)
3. 둘 다 실패 → CLI subprocess fallback
```

Gemini CLI의 OAuth 클라이언트 정보는 `.env` 환경변수로 관리:
- `GEMINI_OAUTH_CLIENT_ID` — Gemini CLI의 OAuth Client ID
- `GEMINI_OAUTH_CLIENT_SECRET` — Gemini CLI의 OAuth Client Secret

### 2. `scripts/config.json` — 설정 확장

기존 필드 유지 + 새 필드 추가:

```json
{
  "gemini_cmd": "/usr/local/bin/gemini",
  "gemini_timeout": 90,
  "cooldown_seconds_per_file": 300,
  "min_content_length": 300,
  "watch_extensions": [".md"],
  "exclude_files": ["gemini_feedback.md"],
  "evaluation_prompt": "...",
  "plan_detection_prompt": "...",

  "sdk": {
    "enabled": true,
    "model": "gemini-2.0-flash",
    "fallback_to_cli": true,
    "oauth_creds_path": "~/.gemini/oauth_creds.json",
    "api_key_env": "GEMINI_API_KEY",
    "max_output_tokens": 2048,
    "temperature": 0.3
  },

  "async_mode": false,
  "async_timeout": 120
}
```

새 필드는 모두 optional (기본값이 있어서 Phase 1 config 그대로 동작).

### 3. `scripts/hook_auto_task.py` — 비동기 분기 추가 (~5줄)

`call_gemini()` 호출 직전에 async 분기:
```python
if config.get("async_mode", False):
    from a2a_bridge import call_gemini_async
    pending_msg = call_gemini_async(content="", prompt=prompt, config=config,
                                     file_path=file_path, source="PostToolUse Hook")
    print(format_hook_output(pending_msg))
    sys.exit(0)
```

### 4. `scripts/hook_stop.py` — 비동기 분기 추가 (~5줄)

Plan 감지("예") 후 전체 평가 시 async 분기 (Plan 분류 자체는 항상 동기):
```python
if config.get("async_mode", False):
    from a2a_bridge import call_gemini_async
    pending_msg = call_gemini_async(content=text, prompt=eval_prompt, config=config,
                                     source="Stop Hook (Plan 감지)")
    print(format_hook_output(pending_msg))
    sys.exit(0)
```

### 5. `.gitignore` — 패턴 추가

`*.egg-info/` 추가

---

## 신규 생성 파일 (3개)

### 1. `requirements.txt`
```
google-generativeai>=0.8.0
google-auth>=2.20.0
```

### 2. `scripts/async_runner.py`

독립 실행 스크립트. `call_gemini_async()`가 `subprocess.Popen`으로 spawn.
- JSON 임시 파일에서 인자 읽기
- `a2a_bridge.call_gemini()` 동기 호출 (이 프로세스 자체가 비동기 핸들러)
- `gemini_feedback.md`에 결과 저장 (소스에 "(비동기)" 표시)
- 임시 파일 자동 삭제
- `exit(0)` 보장 (안전 패턴)

### 3. `scripts/setup.sh`

의존성 설치 편의 스크립트:
```bash
#!/bin/bash
cd "$(dirname "$0")/.."
python3 -m pip install -r requirements.txt
```

---

## 변경 없는 파일

| 파일 | 이유 |
|---|---|
| `.claude/settings.local.json` | Hook 등록 변경 불필요 (동일 스크립트, 동일 타임아웃) |
| `gemini_feedback.md` | append-only 형식 유지 |

---

## 구현 순서

1. `requirements.txt` 생성 + `pip install`
2. `scripts/a2a_bridge.py` 리팩토링 (SDK 함수들 추가, call_gemini 오케스트레이터화)
3. `scripts/config.json` 확장
4. SDK 단독 테스트 (credential 로딩 → API 호출)
5. Dual mode 테스트 (SDK 성공 / SDK 실패→CLI fallback)
6. `scripts/async_runner.py` 생성
7. Hook 스크립트에 async 분기 추가
8. 비동기 모드 테스트
9. `.gitignore` 업데이트
10. CLAUDE.md 업데이트 (Phase 2 반영)

---

## 검증 방법

```bash
# 1. SDK credential 로딩
python3 -c "import sys; sys.path.insert(0,'scripts'); from a2a_bridge import _load_oauth_credentials; print(_load_oauth_credentials({}))"

# 2. SDK 직접 호출
python3 -c "import sys; sys.path.insert(0,'scripts'); from a2a_bridge import load_config, _call_gemini_sdk; print(_call_gemini_sdk('Hello', 'Say OK.', load_config()))"

# 3. Dual mode (call_gemini 오케스트레이터)
python3 -c "import sys; sys.path.insert(0,'scripts'); from a2a_bridge import load_config, call_gemini; r=call_gemini('Hello','Say OK.',load_config()); print('SDK' if '[FALLBACK]' not in r else 'CLI', r[:100])"

# 4. Hook 통합 테스트 (쿨다운 초기화 후)
rm -f scripts/.cooldown_state.json
echo '{"tool_name":"Write","tool_input":{"file_path":"plans/test.md"}}' | python3 scripts/hook_auto_task.py

# 5. 비동기 모드 테스트 (config에서 async_mode: true 설정 후)
echo '{"tool_name":"Write","tool_input":{"file_path":"plans/test.md"}}' | python3 scripts/hook_auto_task.py
sleep 5 && tail -3 gemini_feedback.md

# 6. 폴백 테스트 (SDK 비활성화)
python3 -c "import sys; sys.path.insert(0,'scripts'); from a2a_bridge import load_config, call_gemini; c=load_config(); c['sdk']={'enabled':False}; print(call_gemini('Hello','Say OK.',c)[:100])"
```

## 롤백 전략

`config.json`에서 `"sdk": {"enabled": false}` 설정만으로 Phase 1 동작으로 즉시 복귀 가능. 코드 롤백 불필요.
