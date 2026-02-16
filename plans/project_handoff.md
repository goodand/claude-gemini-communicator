# Project Handoff — Claude-Gemini Communicator

> 새로운 세션의 LLM이 이 프로젝트를 이어받을 때 읽는 문서입니다.

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
| 8 | A2A 엔벨로프 확장 (`message_id`, `target_agent`, 구조화 `status`) | ✅ |
| 9 | feedback.md 엔트리에 request_id 포함 (추적 가능성) | ✅ |
| 10 | 실패 상태 구조화 (`[SDK_ERROR]` → `{"status":"error","error_type":"sdk"}`) | ✅ |

## 3. 아키텍처 (Phase 7: src/ 3-레이어 DAG)

```
hooks/ (진입점)           → core/ (비즈니스 로직)    → shared/ (인프라)

hook_auto_task.py ──→ gemini_service.py ──→ config.py
hook_stop.py ─────→ error_analyzer.py ──→ feedback.py
hook_pre_tool.py ─→ a2a_protocol.py ───→ hook_io.py
                    cooldown.py
```

### 메시지 버스: plans/
```
plans/
├── claude/                  ← Claude 전용 작업 공간
├── codex/                   ← Codex 전용 작업 공간
├── gemini/
│   └── gemini_feedback.md   ← 전 에이전트 피드백 수렴점 (in-degree 6)
└── project_handoff.md       ← 에이전트 간 컨텍스트 전달 (이 문서)
```

## 4. 핵심 파일 맵

```
claude-gemini-communicator/
├── CLAUDE.md / AGENTS.md        # Claude / Codex 지침
│
├── src/                         # Phase 7: 모듈 아키텍처 (실행 코드)
│   ├── shared/ (config, feedback, hook_io)
│   ├── core/ (gemini_service, a2a_protocol, error_analyzer, cooldown)
│   ├── hooks/ (hook_auto_task, hook_stop, hook_pre_tool)
│   ├── async_runner.py
│   └── cli.py (doctor/status/stats/search/test/clear)
│
│
├── skills/                      # Phase 6: 자립형 Skill (cp -r 설치)
│   ├── gemini-reviewer/         # Gemini 코드/문서 리뷰 (Exp. Backoff)
│   ├── agent-parser/            # Codex/Gemini/Claude 통합 파서
│   ├── cross-agent-bridge/      # 통합 오케스트레이터 (review/parse/doctor/setup)
│   └── codex-user-context/      # Codex 사용자 컨텍스트 실행
│
├── architecture/                # 아키텍처 분석 (001 Framework, 의존성 분석)
├── plans/                       # 메시지 버스 (에이전트 허브)
└── schemas/                     # Codex 구조화 출력 스키마
```

## 5. 개발 워크플로우

### Claude Code → Gemini 자동 평가
```
Claude가 .md/.py 파일 Write/Edit
→ src/hooks/hook_auto_task.py (PostToolUse Hook) 자동 실행
→ src/core/gemini_service.py → Gemini SDK 호출
→ plans/gemini/gemini_feedback.md에 결과 append
→ Claude에 피드백 주입
```

### Codex CLI → Gemini 자동 평가
```
Codex가 턴 완료 (agent-turn-complete)
→ skills/gemini-reviewer/scripts/codex_notify.py (notify hook, sandbox 밖)
→ Plan 감지 시 Gemini SDK 호출
→ plans/gemini/gemini_feedback.md에 결과 append
```

## 6. 검증된 기술적 사실

- **PostToolUse Hook은 Bash 실패(exit code != 0) 시 발동하지 않음** → 에러 감지는 Stop Hook transcript 스캔
- **google-genai SDK는 OAuth를 Developer API에서 지원하지 않음** → API key만 사용
- **Codex notify hook은 sandbox 밖** → 네트워크 자유 → Gemini API 호출 가능
- **src/ 의존성 그래프**: DAG, 12노드, 26엣지, 순환 없음 (graph-structure-classifier 검증)
- **plans/ = 메시지 버스**: `gemini_feedback.md`가 전체 프로젝트 최고 in-degree (6)

## 7. 다음 단계

### 단기 (현재 주요 작업)
- [ ] JSONL 버스 도입 (`plans/gemini/a2a_events.jsonl` 병행 기록)
- [ ] `parent_message_id` (멀티홉 체인 추적)
- [ ] CLI 검색 확장 (JSONL 쿼리, 필터 추가)

### 중기
- [ ] Agent Teams 통합 (`claude --teammate-mode tmux`)
- [ ] CI/CD 파이프라인 (GitHub Actions)
### 장기
- [ ] Reference Architecture (Scheduler/Router/Memory 분리)

## 8. 환경 설정 체크리스트

```bash
pip install -r requirements.txt     # google-genai, google-auth, httpx
cp .env.example .env                # .env에 GEMINI_API_KEY 입력
python3 src/cli.py doctor           # 시스템 진단
python3 src/cli.py test             # 자동 테스트 (16건)
```

## 9. 주의사항

- Hook 스크립트는 `exit(0)` 보장 → 에이전트 동작에 영향 없음
- `.env` 절대 커밋 금지
- `plans/gemini/gemini_feedback.md`는 자동 생성 — 수동 편집 주의
- skills/는 자립형 (src/ import 없음, cp -r로 설치)
- scripts/는 레거시 (config.json 호스트, 점진적 축소 대상)
