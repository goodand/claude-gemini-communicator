# Project Handoff — Claude-Gemini Communicator

> 새로운 세션의 LLM/에이전트가 이 프로젝트를 이어받을 때 읽는 문서입니다.
> 최종 갱신: 2026-02-17

## 1. 프로젝트 한 줄 요약

AI 코딩 에이전트(Claude Code, Codex CLI, Gemini CLI)가 코드/문서를 작성하면 **Gemini가 자동으로 평가**하고, `plans/` 디렉토리가 **에이전트 간 메시지 버스** 역할을 하여 크로스-에이전트 협업을 가능하게 하는 시스템.

## 2. 현재 완성된 기능

| Phase | 핵심 기능 | 상태 |
|---|---|---|
| 1 | Gemini CLI subprocess 평가 (PostToolUse + Stop Hook) | ✅ |
| 2 | google-genai SDK, Dual Mode, 비동기, Rate Limit 순회 | ✅ |
| 3 | A2A 구조화 JSON 메시지 프로토콜 | ✅ |
| 4 | 에러 감지 (transcript 스캔 → Lazy Analysis → Gemini 분석) | ✅ |
| 5 | 크로스 플랫폼 확장: Codex/Gemini 파서, 구조화 스키마 | ✅ |
| 6 | 3-Skill 패키징 (gemini-reviewer, agent-parser, cross-agent-bridge) | ✅ |
| 7 | src/ 모듈 아키텍처 마이그레이션 (836줄 God Object → 3-레이어 DAG) | ✅ |
| 8 | JSONL 메시지 버스 + parent_message_id + CLI 확장 | ✅ |
| 8+ | Reference Architecture (Router/Memory/Scheduler) + Codex Review 버그 수정 | ✅ |
| 9 | LLM 추상화 (Provider 패턴) + 피드백 루프 자동화 + 이식성 강화 | ✅ |
| 9+ | CSO 안정성 강화 (스케줄러 락, exclude 오류, 라우터 검증) | ✅ |
| 10 | 모듈 통합 (JSONL 일원화, Scheduler↔AsyncRunner, async_timeout 제거) | ✅ |

## 3. 아키텍처 (Phase 8+: src/ 3-레이어 DAG + Reference Architecture)

```
hooks/ (진입점)           → core/ (비즈니스 로직)    → shared/ (인프라)

hook_auto_task.py ──→ gemini_service.py ──→ config.py
hook_stop.py ─────→ error_analyzer.py ──→ feedback.py
hook_pre_tool.py ─→ a2a_protocol.py ───→ hook_io.py
                    cooldown.py
                    router.py      ← NEW (Phase 8+)
                    memory.py      ← NEW (Phase 8+, 테스트 전용)
                    scheduler.py   ← NEW (Phase 8+, 테스트 전용)
```

### 메시지 버스
```
plans/
├── claude/                  ← Claude 전용 작업 공간
├── codex/                   ← Codex 전용 작업 공간 (codebase_analysis.md 포함)
├── User/                    ← 사용자 지침 (system_prompt.md)
├── gemini/
│   ├── gemini_feedback.md   ← 전 에이전트 피드백 수렴점 (Markdown)
│   ├── a2a_events.jsonl     ← JSONL 이벤트 버스 (기계 파싱용)
│   └── cso_review_request.md ← Gemini CSO 아키텍처 비판 요청 (미실행)
└── project_handoff.md       ← 에이전트 간 컨텍스트 전달 (이 문서)
```

## 4. 핵심 파일 맵

```
claude-gemini-communicator/
├── CLAUDE.md                       # Claude 지침 (프로젝트 루트)
├── config/
│   ├── config.json                 # 전체 설정 (SDK, routing_rules, error_detection 등)
│   └── .env.example                # 환경변수 템플릿
│
├── src/                            # 실행 코드 (3-레이어 DAG)
│   ├── shared/ (config, feedback, hook_io)
│   ├── core/ (gemini_service, a2a_protocol, error_analyzer, cooldown, router, memory, scheduler)
│   ├── hooks/ (hook_auto_task, hook_stop, hook_pre_tool)
│   ├── async_runner.py
│   └── cli.py (doctor/status/stats/search/chain/test/clear — 68건 테스트)
│
├── skills/                         # 자립형 Skill (cp -r 설치)
│   ├── gemini-reviewer/            # Gemini 코드/문서 리뷰
│   ├── agent-parser/               # Codex/Gemini/Claude 통합 파서
│   ├── cross-agent-bridge/         # 통합 오케스트레이터
│   └── codex-user-context/         # Claude에서 Codex CLI 호출
│
├── template/                       # 커밋 메시지, 의사결정 프레임워크 템플릿
├── plans/                          # 메시지 버스 (에이전트 허브)
└── schemas/                        # Codex 구조화 출력 스키마
```

## 5. 다음 세션 작업 대상 (우선순위순)

### 미통합 모듈 연결 (Codex codebase_analysis.md 참조)
- [x] `memory.py` — CLI 중복 제거, `parse_jsonl_file()` + `load_events()` 2단 구조
- [x] `scheduler.py` — `async_runner.py`에서 `register_job`/`complete_job`/`fail_job` 호출
- [x] JSONL 경로 → `shared/config.get_jsonl_path()` 단일 출처 (5곳 통합)
- [x] `config.async_timeout` — 소비처 없어 제거 (`gemini_timeout`으로 충분)

### Gemini CSO 아키텍처 비판
- [x] `plans/gemini/cso_architecture_review.md` 완료 (16/25점, 5축 평가)
- [x] CSO 최시급 이슈 (`PROJECT_ROOT` 단일 출처화) → A-3에서 해결
- [x] CSO 이식성 비판 (fcntl) → A-3 + B-1에서 skills 포함 전면 해결
- [x] CSO 재사용성 비판 (LLM 추상화) → B-1 Provider 패턴으로 해결
- [x] CSO 피드백 루프 비판 (단방향 통신) → B-2 feedback_context.py로 해결

### 구조 개선 (Codex Review + CSO Review에서 식별)
- [x] `exclude_files` basename vs 경로 비교 불일치 정리
- [x] `scheduler.py` 파일 쓰기 락 추가 (filelock)
- [x] `router.py` 규칙 스키마 검증 추가 + config validate_config() 연동
- [x] Hook e2e 통합 테스트 추가 (11건: PostToolUse 5, PreToolUse 4, Stop 2)
- [x] `cli.py` → `hooks/` 역방향 import — 이미 해결 (`check_command`는 `shared/command_guard.py`에 위치)

### 장기
- [ ] Agent Teams 통합 (`claude --teammate-mode tmux`)
- [ ] CI/CD 파이프라인 (GitHub Actions)

## 6. 3-Agent 역할 분담

| 에이전트 | 역할 | 제약 |
|---|---|---|
| **Claude** | 오케스트레이션, API 호출, Code Review | Gemini API 직접 호출 가능 |
| **Codex** | 로컬 코딩, 분석, 리뷰 (gpt-5.3-codex) | 샌드박스 네트워크 차단 → API 호출 불가 |
| **Gemini** | 계획/설계 비판 (CSO 역할) | CLI 쿼터 제한 있음, SDK로 우회 가능 |

### Codex CLI 호출 방법 (Claude에서)
```bash
# 코드 생성 (full-auto)
zsh skills/codex-user-context/scripts/run_codex_user_context.sh --full-auto "태스크 설명"

# 코드 리뷰
codex review --base origin/main

# dry-run (컨텍스트 확인)
zsh skills/codex-user-context/scripts/run_codex_user_context.sh --dry-run "test"
```

## 7. 검증 방법

```bash
python3.13 src/cli.py test           # 자동 테스트 57건
python3.13 src/cli.py doctor         # 시스템 진단
python3.13 src/cli.py chain --list   # JSONL 메시지 체인 목록
python3.13 src/cli.py stats --jsonl  # JSONL 이벤트 통계
```

## 8. 환경 설정 체크리스트

```bash
pip install -r requirements.txt     # google-genai, google-auth, httpx
cp .env.example .env                # .env에 GEMINI_API_KEY 입력
python3.13 src/cli.py doctor        # 시스템 진단
python3.13 src/cli.py test          # 자동 테스트 (57건)
```

## 9. 주의사항

- **Python 3.13**: Hook은 `python3.13` (Homebrew)으로 실행 (`.claude/settings.local.json`)
- Hook 스크립트는 `exit(0)` 보장 → 에이전트 동작에 영향 없음
- `.env` 절대 커밋 금지
- `plans/gemini/gemini_feedback.md`는 자동 생성 — 수동 편집 주의
- `plans/gemini/a2a_events.jsonl`은 런타임 자동 생성 (.gitignore 대상)
- skills/는 자립형 (src/ import 없음, cp -r로 설치)
- scripts/는 Phase 7에서 삭제됨 (레거시)
- 커밋 시 `template/.gitmessage` 형식 참조
- Git: 단독 개발자, main branch 직접 push, force push 필요 (Co-Authored-By 제거로 히스토리 재작성됨)

## 10. 참조 문서

| 문서 | 위치 | 용도 |
|---|---|---|
| Claude 프로젝트 가이드 | `plans/claude/claude_project_guide.md` | Claude 전용 상세 가이드 |
| Codex 프로젝트 가이드 | `plans/codex/codex_project_guide.md` | Codex 전용 가이드 |
| Codex 코드베이스 분석 | `plans/codex/codebase_analysis.md` | Codex가 작성한 의존성/구조 분석 |
| 아키텍처 분석 | `architecture/04_new_architecture_analysis.md` | DAG 의존성 상세 분석 |
| Gemini CSO 리뷰 요청 | `plans/gemini/cso_review_request.md` | 아키텍처 비판 요청 (미실행) |
| 사용자 지침 | `plans/User/system_prompt.md` | 개발 프로세스 가이드 |
