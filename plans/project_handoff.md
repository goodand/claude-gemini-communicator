# Project Handoff — Claude-Gemini Communicator

> 새로운 세션의 LLM이 이 프로젝트를 이어받을 때 읽는 문서입니다.

## 1. 프로젝트 한 줄 요약

AI 코딩 에이전트(Claude Code, Codex CLI, Gemini CLI)가 코드/문서를 작성하면 **Gemini가 자동으로 평가**하고, 각 에이전트의 출력을 **구조화된 JSON으로 파싱**하여 크로스-에이전트 협업을 가능하게 하는 시스템.

## 2. 현재 완성된 기능

### Phase 1-4 (Claude Code Hooks 기반)
| Phase | 핵심 기능 | 상태 |
|---|---|---|
| 1 | Gemini CLI subprocess 평가 (PostToolUse + Stop Hook) | ✅ |
| 2 | google-genai SDK 직접 호출, Dual Mode, 비동기, Rate Limit 자동 순회 | ✅ |
| 3 | A2A 구조화 JSON 메시지 프로토콜 | ✅ |
| 4 | 에러 감지 (transcript 스캔 → Lazy Analysis → Gemini 분석) | ✅ |

### Phase 5 (크로스 플랫폼 확장) — 이번 세션에서 완성
| 기능 | 파일 | 상태 |
|---|---|---|
| PreToolUse Hook (위험 명령 차단) | `scripts/hook_pre_tool.py` | ✅ |
| CLI 관리 도구 (doctor/status/stats/search/test/clear) | `scripts/cli.py` | ✅ |
| Agent Skill (gemini-reviewer) | `skills/gemini-reviewer/` | ✅ |
| Codex CLI 연동 (AGENTS.md + notify hook) | `AGENTS.md`, `codex.toml` | ✅ |
| Codex sandbox 분석 + notify hook 검증 | notify = sandbox 밖 실행 확인 | ✅ |
| Codex JSONL 스트림 파서 | `scripts/codex_json_parser.py` | ✅ |
| Gemini JSON 파서 | `scripts/gemini_json_parser.py` | ✅ |
| Claude Transcript 파서 | `scripts/transcript_parser.py` | ✅ |
| `--output-schema` 구조화 출력 스키마 | `schemas/codex_review_result.json`, `schemas/codex_task_result.json` | ✅ |
| codex-status CLI 서브커맨드 | `scripts/cli.py` | ✅ |
| 커밋 템플릿 (Good/Bad Case) | `.gitmessage` | ✅ |
| Gemini Code Assist 연동 | `.gemini/review.md` | ✅ |

## 3. 아키텍처

```
┌──────────────────────────────────────────────────┐
│                  Orchestrator (User/CI)           │
│                                                    │
│  Claude Code          Codex CLI         Gemini CLI │
│  ┌──────────┐    ┌──────────────┐    ┌───────────┐│
│  │Hooks:    │    │notify hook   │    │headless   ││
│  │ Pre/Post │    │(sandbox 밖)  │    │--output-  ││
│  │ /Stop    │    │              │    │format json││
│  └────┬─────┘    └──────┬───────┘    └─────┬─────┘│
│       │                 │                   │      │
│       ▼                 ▼                   ▼      │
│  ┌─────────────────────────────────────────────┐  │
│  │          Output Parsers (scripts/)          │  │
│  │  codex_json_parser  gemini_json_parser     │  │
│  │  transcript_parser                          │  │
│  └──────────────────┬──────────────────────────┘  │
│                     ▼                              │
│  ┌─────────────────────────────────────────────┐  │
│  │  a2a_bridge.py (Gemini SDK/CLI 이중화)      │  │
│  │  → call_gemini() → gemini_feedback.md       │  │
│  └─────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 4. 핵심 파일 맵

```
claude-gemini-communicator/
├── CLAUDE.md                    # Claude Code용 지침 (상세)
├── AGENTS.md                    # Codex CLI용 지침
├── codex.toml                   # Codex 프로젝트 설정 (notify hook)
├── .gitmessage                  # 커밋 템플릿 (Good/Bad Case)
├── .gemini/review.md            # Gemini Code Assist PR 리뷰 규칙
│
├── scripts/
│   ├── a2a_bridge.py            # 핵심 오케스트레이터 (SDK/CLI, 비동기, 에러감지, A2A)
│   ├── config.json              # 전체 설정
│   ├── hook_auto_task.py        # PostToolUse Hook
│   ├── hook_stop.py             # Stop Hook (Plan + Error)
│   ├── hook_pre_tool.py         # PreToolUse Hook (위험 명령 차단)
│   ├── async_runner.py          # 비동기 실행기
│   ├── cli.py                   # CLI 관리 도구 (7개 서브커맨드)
│   ├── codex_json_parser.py     # Codex JSONL 파서
│   ├── gemini_json_parser.py    # Gemini JSON 파서
│   └── transcript_parser.py     # Claude Transcript 파서
│
├── schemas/
│   ├── codex_review_result.json # Codex 코드 리뷰 출력 스키마
│   └── codex_task_result.json   # Codex 태스크 결과 출력 스키마
│
├── skills/gemini-reviewer/      # 크로스 플랫폼 Agent Skill
│   ├── SKILL.md
│   ├── scripts/evaluate.py      # Standalone Gemini 리뷰 (a2a_bridge 독립)
│   ├── scripts/codex_notify.py  # Codex notify hook
│   └── references/
│
├── plans/
│   ├── claude/                  # Claude가 만든 계획 문서들
│   ├── codex/                   # Codex가 만든 계획 문서들
│   └── project_handoff.md       # 이 문서
│
└── gemini_feedback.md           # Gemini 평가 로그 (append-only)
```

## 5. 개발 워크플로우 (검증됨)

### Claude Code → Gemini 자동 평가
```
Claude가 .md/.py 파일 Write/Edit
→ hook_auto_task.py (PostToolUse Hook) 자동 실행
→ a2a_bridge.py → Gemini SDK 호출
→ gemini_feedback.md에 결과 append
→ Claude에 피드백 주입
```

### Codex CLI → Gemini 자동 평가
```
Codex가 턴 완료 (agent-turn-complete)
→ codex_notify.py (notify hook, sandbox 밖에서 실행)
→ Plan 감지 시 Gemini SDK 호출
→ gemini_feedback.md에 결과 append
```

### Codex를 부하 개발자로 사용
```bash
# 코딩 지시 (workspace-write, 파일 수정 가능)
codex exec --full-auto "작업 내용"

# 구조화 출력 (스키마 강제)
codex exec --output-schema schemas/codex_review_result.json "리뷰할 내용"

# JSONL 스트림 파싱
codex exec --json "작업" 2>/dev/null | python3 scripts/codex_json_parser.py

# 주의: git commit/push는 --sandbox danger-full-access 필요
# 주의: 외부 API 호출은 sandbox가 차단 (notify hook은 sandbox 밖이라 가능)
```

### Gemini CLI headless
```bash
echo "프롬프트" | gemini --output-format json | python3 scripts/gemini_json_parser.py
```

## 6. 검증된 기술적 사실 (중요)

### Codex CLI Sandbox 정책
- `(deny default)` + `(allow network-outbound (remote ip "localhost:*"))` — 외부 네트워크 차단
- `read-only`: 파일 읽기만 허용
- `workspace-write`: workdir 쓰기 허용, `.git/` 쓰기 불가, 네트워크 차단
- `danger-full-access`: 모든 제한 해제
- **notify hook은 sandbox 밖 (launchd 직속 자식)** → 네트워크 자유 → Gemini API 호출 가능

### Codex config 경로
- 글로벌: `~/.codex/config.toml`
- 프로젝트: `codex.toml` (프로젝트 루트)
- notify는 글로벌 config의 project 섹션에 등록해야 동작 (`codex.toml` 단독으로는 인식 안 됨)

### OpenAI Structured Output 규칙
- `--output-schema`의 JSON Schema에서 **모든 properties가 required에 포함**되어야 함
- optional 필드는 `"type": ["string", "null"]`로 처리

## 7. 미완성 / 다음 단계

### 단기 (바로 구현 가능)
- [ ] 3개 파서 (codex/gemini/transcript)를 통합하는 래퍼 스크립트
- [ ] `codex exec --json` 파싱 결과를 Gemini에 자동 전달하는 파이프라인
- [ ] transcript_parser를 TeammateIdle 훅에 등록 (`.claude/settings.local.json`)
- [ ] CLI `test` 서브커맨드에 새 파서들 테스트 추가 (현재 36건 → 확장)

### 중기
- [ ] Agent Teams 통합 (`claude --teammate-mode tmux`)
  - 팀 리더가 Codex/Gemini를 팀원으로 spawn
  - `~/.claude/teams/`, `~/.claude/tasks/` 기반 작업 조율
- [ ] Gemini Extension 개발
- [ ] CI/CD 파이프라인 (GitHub Actions + codex exec)

### 장기 비전
- [ ] Reference Architecture 기반 리팩토링 (Scheduler/Router/Memory 분리)
  - 참고: `plans/claude/reference_communicator.md`
- [ ] MCP 기반 원격 연동 (로컬 초과 시)
- [ ] 멀티 머신/원격 협업 확장

## 8. 환경 설정 체크리스트

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. API Key 설정
cp .env.example .env
# .env에 GEMINI_API_KEY 입력

# 3. Claude Code Hooks 확인
cat .claude/settings.local.json

# 4. Codex CLI notify hook 확인
grep -A2 "claude-gemini-communicator" ~/.codex/config.toml

# 5. 전체 시스템 진단
python3 scripts/cli.py doctor

# 6. Codex 연동 상태 확인
python3 scripts/cli.py codex-status

# 7. 전체 자동 테스트 (36건)
python3 scripts/cli.py test
```

## 9. 커밋 컨벤션

`.gitmessage` 참조:
- **Good Case** (feat/refactor/perf): pseudo-code 블록으로 핵심 로직 기술
- **Bad Case** (fix): 소크라테스식 5 Whys (Problem → Why-1 → Why-2 → Why-3 → Fix)
- **Footer**: Impact/Risk/Review-focus (Gemini Code Assist용)

## 10. 주의사항

- `gemini_feedback.md`는 자동 생성 파일 — 수동 편집 주의
- `.env`는 절대 커밋 금지 (API Key 포함)
- Hook 스크립트는 모두 `exit(0)` 보장 → 에이전트 정상 동작에 영향 없음
- Codex sandbox 내에서는 외부 API 호출 불가 → notify hook 또는 danger-full-access 사용
- 무료 티어 API key는 모델별 일일 한도 존재 → 자동 순회로 대응
