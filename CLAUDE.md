# CLAUDE.md — Claude-Gemini Communicator

## 프로젝트 개요

Claude Code가 계획/문서를 작성하면 Gemini가 자동으로 평가하는 협업 시스템.
Claude Code Hooks를 통해 Write/Edit 도구 사용 시 자동 트리거됩니다.

# 최근 사용 했던 LLM 정보
- 세션 id : "session ID: 8aafa760-be1e-4993-a1f9-780453b2c88e"
- 세션 디렉토리 및 작업 경로 : /Users/jaehyuntak/.gemini/skills/skill_evaluator/plans

## 현재 상태: Phase 7 구현 완료

### Phase 1 (MVP) — 완료
- Gemini CLI subprocess 기반 평가 파이프라인
- PostToolUse Hook + Stop Hook, 쿨다운, 피드백 로그

### Phase 2 — 완료
- google-genai SDK (Dual Mode: SDK 우선, CLI fallback)
- 비동기 모드, 복수 API key/모델 자동 순회, `.env` 관리

### Phase 3 — 완료
- A2A 구조화 JSON 메시지 프로토콜

### Phase 4 — 완료
- 에러 감지 (transcript 스캔 → Lazy Analysis), 에러 해시 정규화, fcntl file lock

### Phase 5 — 완료
- 크로스 플랫폼 확장: Codex/Gemini 파서, 구조화 스키마, 프로젝트 핸드오프

### Phase 6 — 완료 (3-Skill 패키징)
- **3개 자립형 Skill**: `cp -r`로 다른 프로젝트에 설치 가능
- **gemini-reviewer**: Exponential Backoff, `--format json`, `_common.py`
- **agent-parser**: Codex/Gemini/Claude 통합 파서 + 자동 포맷 감지
- **cross-agent-bridge**: 통합 오케스트레이터 (review/parse/doctor/setup)

### Phase 7 — 완료 (src/ 모듈 아키텍처 마이그레이션)
- `scripts/a2a_bridge.py` (836줄, God Object) → `src/` 3-레이어 DAG 구조로 분해
- **shared/** (config, feedback, hook_io) — 설정/저장/IO 유틸리티
- **core/** (gemini_service, a2a_protocol, error_analyzer, cooldown) — 비즈니스 로직
- **hooks/** (hook_auto_task, hook_stop, hook_pre_tool) — Claude Code Hook 진입점
- DAG 의존성 보장: hooks/ → core/ → shared/ (역방향 금지, 순환 없음)
- Hook 경로 `.claude/settings.local.json`에서 `src/hooks/`로 변경 완료
- 의존성 분석: depsolve-analyzer + graph-structure-classifier 검증

### 3-Agent 역할 분담 (검증 완료)
- **Codex**: 설계 + 코딩 (샌드박스, 네트워크 차단)
- **Claude**: 의존성 분석, 병렬 실행, Code Review, Gemini API 호출
- **Gemini**: 계획/설계 비판 (Claude Hook 또는 사용자 터미널에서 호출)

### 미구현 (장기 비전)
- JSONL 버스 도입: `plans/gemini/a2a_events.jsonl` 병행 기록
- `parent_message_id`: 멀티홉 체인 추적
- Agent Teams 통합 (`claude --teammate-mode tmux`)
- Reference Architecture (Scheduler/Router/Memory 분리)

## 핵심 파일

### src/ 모듈 (Phase 7, 실행 경로)

| 모듈 | 역할 | 줄 수 |
|---|---|---|
| `src/shared/config.py` | 설정 로더 (load_config, load_env, validate) | ~85 |
| `src/shared/feedback.py` | 피드백 저장 (fcntl file lock) | ~30 |
| `src/shared/hook_io.py` | Hook I/O (format_hook_output, read_file_content) | ~35 |
| `src/core/gemini_service.py` | Gemini SDK/CLI 호출 (rate limit 순회, fallback) | ~230 |
| `src/core/a2a_protocol.py` | A2A JSON 메시지 빌드/파싱/렌더링 | ~150 |
| `src/core/error_analyzer.py` | 에러 감지 (transcript 스캔, Lazy Analysis) | ~170 |
| `src/core/cooldown.py` | 쿨다운 (파일별/전역) | ~50 |
| `src/hooks/hook_auto_task.py` | PostToolUse Hook (.md Write/Edit → Gemini 평가) | ~90 |
| `src/hooks/hook_stop.py` | Stop Hook (Plan 감지 + 에러 감지) | ~140 |
| `src/hooks/hook_pre_tool.py` | PreToolUse Hook (위험 명령 차단/경고) | ~160 |
| `src/async_runner.py` | 비동기 백그라운드 Gemini 호출 실행기 | ~60 |
| `src/cli.py` | CLI 관리 도구 (doctor/status/stats/search/test/clear) | ~420 |

### 설정 + 환경

| 파일 | 역할 |
|---|---|
| `config.json` | 전체 설정 (SDK, 에러 감지, 프롬프트 등) |
| `.claude/settings.local.json` | Hook 등록 설정 (→ src/hooks/) |
| `.gemini/review.md` | Gemini Code Assist PR 리뷰 규칙 |
| `.env` | API key 저장 (gitignore) |
| `plans/gemini/gemini_feedback.md` | Gemini 평가 결과 로그 (append-only) |

### Skills (Phase 6, 자립형)

| Skill | 진입점 | 역할 |
|---|---|---|
| `skills/gemini-reviewer/` | `scripts/evaluate.py` | Gemini 코드/문서 리뷰 (Exp. Backoff, JSON 출력) |
| `skills/agent-parser/` | `scripts/parse.py` | Codex/Gemini/Claude 통합 파서 (자동 감지) |
| `skills/cross-agent-bridge/` | `scripts/bridge.py` | 통합 오케스트레이터 (review/parse/doctor/setup) |

## 디렉토리 구조

```
claude-gemini-communicator/
├── CLAUDE.md                    ← 이 파일
├── AGENTS.md                    ← Codex CLI용 지침
├── requirements.txt
├── .claude/
│   └── settings.local.json      ← Hook 설정 (→ src/hooks/)
├── .gemini/
│   └── review.md                ← Gemini Code Assist PR 리뷰 규칙
│
├── src/                         ← Phase 7: 모듈 아키텍처 (실행 코드)
│   ├── shared/                  ← 레이어 3: 설정/저장/IO
│   │   ├── config.py
│   │   ├── feedback.py
│   │   └── hook_io.py
│   ├── core/                    ← 레이어 2: 비즈니스 로직
│   │   ├── gemini_service.py
│   │   ├── a2a_protocol.py
│   │   ├── error_analyzer.py
│   │   └── cooldown.py
│   ├── hooks/                   ← 레이어 1: Hook 진입점
│   │   ├── hook_auto_task.py
│   │   ├── hook_stop.py
│   │   └── hook_pre_tool.py
│   ├── async_runner.py
│   └── cli.py
│
├── config.json                  ← 전체 설정 (SDK, 에러 감지, 프롬프트 등)
│
├── skills/                      ← Phase 6: 자립형 Skill (cp -r 설치)
│   ├── gemini-reviewer/         ← Gemini 코드/문서 리뷰
│   ├── agent-parser/            ← Codex/Gemini/Claude 통합 파서
│   ├── cross-agent-bridge/      ← 통합 오케스트레이터
│   └── codex-user-context/      ← Codex 사용자 컨텍스트 실행
│
├── architecture/                ← 아키텍처 분석 문서
│   ├── 001_decision_framework.md
│   ├── 001_decision_framework_checklist.md
│   └── 04_new_architecture_analysis.md
│
├── plans/                       ← 메시지 버스 (에이전트 허브)
│   ├── claude/                  ← Claude 전용 작업 공간
│   ├── codex/                   ← Codex 전용 작업 공간
│   ├── gemini/
│   │   └── gemini_feedback.md   ← 전 에이전트 피드백 수렴점 (in-degree 6)
│   └── project_handoff.md       ← 에이전트 간 컨텍스트 전달
│
└── schemas/                     ← Codex 구조화 출력 스키마
```

## 아키텍처 (Phase 7: src/ 3-레이어 DAG)

```
hooks/ (진입점)           → core/ (비즈니스 로직)    → shared/ (인프라)
                              ↓
hook_auto_task.py ──→ gemini_service.py ──→ config.py
hook_stop.py ─────→ error_analyzer.py ──→ feedback.py
hook_pre_tool.py ─→ a2a_protocol.py ───→ hook_io.py
                    cooldown.py
```

### 의존성 그래프 (순환 없음, DAG 검증 완료)
- 허브 #1: `shared.config` (in-degree 6, ~85줄) — 작고 안정적
- 이전 허브: `a2a_bridge.py` (5 dependents, 836줄, God Object) → 분해됨
- 레이어 규칙: hooks/ → core/ → shared/ (역방향 없음)

### 메시지 버스: plans/
- `plans/gemini/gemini_feedback.md`가 전체 프로젝트 최고 in-degree (6)
- 모든 에이전트(Claude, Codex, Gemini, User)가 접근하는 수렴점
- 상세: `architecture/04_new_architecture_analysis.md`

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

## 핵심 설정 (`config.json`)

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

설치: `pip install -r requirements.txt`

## 테스트 방법

```bash
# 1. CLI 전체 자동 테스트 (16건 — config, 에러감지, A2A, PreToolUse 등)
python3 src/cli.py test

# 2. SDK 호출 테스트
python3 -c "from src.core.gemini_service import call_gemini; from src.shared.config import load_config; print(call_gemini('Hi','Say OK.',load_config())[:100])"

# 3. PostToolUse Hook 테스트
rm -f .cooldown_state.json
echo '{"tool_name":"Write","tool_input":{"file_path":"plans/test.md"}}' | python3 src/hooks/hook_auto_task.py

# 4. PreToolUse Hook 테스트
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | python3 src/hooks/hook_pre_tool.py

# 5. 시스템 진단
python3 src/cli.py doctor

# 6. Skill 자립성 테스트
cp -r skills/agent-parser /tmp/test-parser && cd /tmp/test-parser && python3 scripts/parse.py --help
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
