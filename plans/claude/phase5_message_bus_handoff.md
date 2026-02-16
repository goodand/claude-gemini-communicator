# Phase 5 — 메시지 버스 통합 + 아키텍처 재구조화 준비

> 작성: CTO(Claude) | 2026-02-16
> 목적: 다음 세션/에이전트가 이어받을 수 있는 핸드오프 문서

---

## 1. 현재까지 완료된 작업 요약

### Phase 1-4 (기능 구현)
| Phase | 내용 | 상태 |
|---|---|---|
| 1 | Gemini CLI 평가 파이프라인 + Hook | ✅ 완료 |
| 2 | google-genai SDK, 비동기, 복수 API key/모델 | ✅ 완료 |
| 3 | A2A 구조화 JSON 메시지 프로토콜 | ✅ 완료 |
| 4 | 에러 감지 (transcript 스캔, Lazy Analysis) | ✅ 완료 |

### Phase 5-7 (구조 정리)
| Phase | 내용 | 상태 |
|---|---|---|
| 5 | 크로스 플랫폼 확장 (Codex/Gemini 파서, 핸드오프) | ✅ 완료 |
| 6 | 3-Skill 패키징 (gemini-reviewer, agent-parser, cross-agent-bridge) | ✅ 완료 |
| 7 | `scripts/a2a_bridge.py` God Object 분해 → `src/` 3-레이어 DAG | ✅ 완료 |

### 이번 세션에서 완료한 추가 작업
| 작업 | 상세 |
|---|---|
| A2A 8필드 엔벨로프 | `build_a2a_request()`에 `message_id`, `target_agent`, `status` 추가 |
| request_id 전 경로 전파 | 모든 Hook → `save_feedback(request_id=)` |
| `parse_error_status()` | 문자열 에러 → 구조화 dict |
| 001 Framework 최종 개정 | Gemini 비판 3건 반영 (§6-11 전면 개정) |
| scripts/ 레거시 제거 | **-3,269줄** 삭제, `config.json` 루트 이동, 디렉토리 완전 제거 |
| 테스트 47건 | test_core 14, test_hooks 15, test_shared 18 (전체 통과) |

---

## 2. 현재 프로젝트 구조 (scripts/ 제거 후)

```
claude-gemini-communicator/
├── config.json                  ← 전체 설정 (루트, 유일본)
├── src/                         ← 실행 코드 (12 모듈, ~1,963줄)
│   ├── shared/                  ← 레이어 3: config, feedback, hook_io
│   ├── core/                    ← 레이어 2: gemini_service, a2a_protocol, error_analyzer, cooldown
│   ├── hooks/                   ← 레이어 1: hook_auto_task, hook_stop, hook_pre_tool
│   ├── async_runner.py
│   └── cli.py
├── skills/                      ← 자립형 (cp -r 설치)
│   ├── gemini-reviewer/
│   ├── agent-parser/
│   ├── cross-agent-bridge/
│   └── codex-user-context/
├── plans/                       ← 메시지 버스 (de facto)
│   ├── claude/                  ← Claude 작업 공간
│   ├── codex/                   ← Codex 작업 공간
│   ├── gemini/
│   │   └── gemini_feedback.md   ← 전 에이전트 수렴점 (in-degree 6)
│   └── project_handoff.md
├── architecture/                ← 의존성 분석 + 설계 문서
└── tests/                       ← pytest 47건
```

### 의존성 규칙 (DAG, 순환 없음)
```
hooks/ → core/ → shared/   (정방향만)
hooks/ → shared/            (건너뛰기 허용)
shared/ → (외부 없음)       (독립)
skills/ → (src/ import 금지, 자체 _common.py)
```

---

## 3. 다음에 해야 할 작업: JSONL 메시지 버스

### 왜 아키텍처 재구조화 전에 해야 하는가

현재 `plans/gemini/gemini_feedback.md`가 de facto 메시지 버스인데, **Markdown은 기계 파싱에 부적합**:
- 구조화된 검색/필터링 불가
- 통계/분석에 파싱 비용이 높음
- 멀티홉 체인 추적 불가 (request_id는 Markdown 헤더에 텍스트로만 존재)

**Reference Architecture**(Scheduler/Router/Memory 분리)를 구현하려면 **기계가 읽을 수 있는 메시지 형식**이 먼저 필요.

### 구현 계획

#### Phase 5-A: JSONL 버스 도입
- 파일: `plans/gemini/a2a_events.jsonl`
- 형식: 1라인 1 JSON, UTF-8, `\n` 종결
- **기존 Markdown과 병행 기록** (tee 패턴) — 호환성 유지
- fcntl 파일 lock 동일 적용

**수정 대상:**
```python
# src/shared/feedback.py — save_feedback() 확장
def save_feedback(feedback_text, *, file_path=None, request_id=None):
    # 기존: Markdown append
    # 추가: JSONL append (동일 데이터를 JSON으로)
```

**JSONL 레코드 스키마:**
```json
{
  "message_id": "msg-uuid",
  "request_id": "req-uuid",
  "timestamp": "2026-02-16T20:00:00+09:00",
  "source_agent": "claude",
  "target_agent": "gemini",
  "message_type": "evaluation_request",
  "status": {"code": "success"},
  "payload": { ... },
  "file_path": "plans/test.md",
  "hook_source": "post_tool_use"
}
```

#### Phase 5-B: parent_message_id (멀티홉 체인 추적)
- `build_a2a_request()`에 선택 필드 `parent_message_id` 추가
- 단일 홉에서는 생략 (현재 대부분)
- 멀티 에이전트 체인 시 필수

**멀티홉 시나리오:**
```
Claude Hook → Gemini 분석 요청 (M1)
  └→ Gemini 응답 (M2, parent: M1)
      └→ Codex 통지 (M3, parent: M2)
```

#### Phase 5-C: CLI 검색 확장
- `src/cli.py`의 `search` 명령이 JSONL을 직접 쿼리
- `--agent`, `--status`, `--since`, `--request-id` 필터

---

## 4. 그 다음: Reference Architecture (장기 비전)

> 상세: `plans/claude/reference_communicator.md`

JSONL 버스가 확립된 후에 검토할 항목:

| 컴포넌트 | 현재 | 미래 |
|---|---|---|
| Scheduler | Hook 스크립트가 직접 처리 | 독립 스케줄러 모듈 |
| Router | `gemini_service.py`가 하드코딩 | 설정 기반 에이전트 라우팅 |
| Memory | `.error_history.json` (Layer 1만) | Message Store + Summary Memory |
| Agent Registry | 없음 (하드코딩) | `agents.json` 선언적 등록 |

**Gemini가 Phase 4에서 비판한 과설계 항목** (의도적 비채택):
- `sequence_number` — 파일 라인 번호가 자연 순서
- `causal_depth` — `parent_message_id` 체인으로 대체
- `targets` 배열/DSL — 현재 1:1, `target_agent` 문자열 충분
- `root_message_id` — `request_id`가 동일 역할
- Memory 4계층 — Layer 1만으로 충분 (에러 이력 JSON)
- debate/relay 모드 — 단일 평가 모드만 사용 중

---

## 5. 3-Agent 역할 분담 가이드

| 역할 | 에이전트 | 적합한 작업 |
|---|---|---|
| **CTO** | Claude | 의존성 분석, 코드 리뷰, 실행 계획, Gemini API 호출 |
| **Developer** | Codex | 코딩 (테스트 → 구현), 파일 생성/수정 (gpt-5 모델) |
| **CSO** | Gemini | 설계 비판, 과설계 경고, 리스크 평가 |

### Codex CLI 사용법
```bash
# 기본 실행
./plans/codex/run_codex_user_context.sh "테스트 코드를 작성해줘"

# 파일 쓰기 가능 모드
./plans/codex/run_codex_user_context.sh --full-auto "parse.py 함수 구현해줘"

# 모델 지정
./plans/codex/run_codex_user_context.sh --model gpt-5 "코드 리뷰"
```

**Codex 주의사항:**
- ChatGPT 계정 → `gpt-5` 모델만 사용 가능 (gpt-5.3-codex, o3, gpt-4.1 불가)
- `--full-auto` 없으면 read-only sandbox → 파일 쓰기 불가
- 기존 로직을 무시하고 새 변수명으로 짜는 경향 → Claude가 리뷰 필수

---

## 6. 핵심 파일 참조 맵

### 구현할 때 읽어야 할 파일
| 목적 | 파일 |
|---|---|
| A2A 메시지 빌드/파싱 | `src/core/a2a_protocol.py` |
| Gemini 호출 | `src/core/gemini_service.py` |
| 피드백 저장 (JSONL 추가 지점) | `src/shared/feedback.py` |
| 설정 로드 | `src/shared/config.py` → `config.json` |
| Hook 진입점 | `src/hooks/hook_auto_task.py`, `hook_stop.py` |
| 에러 감지 | `src/core/error_analyzer.py` |

### 아키텍처 결정 근거
| 목적 | 파일 |
|---|---|
| 의사결정 프레임워크 | `architecture/001_decision_framework.md` |
| 현재 DAG 분석 | `architecture/04_new_architecture_analysis.md` |
| CTO 최종 아키텍처 | `architecture/03_cto_final_architecture.md` |
| 장기 비전 | `plans/claude/reference_communicator.md` |
| Phase 4 축소 경위 | `plans/claude/phase4_architecture.md` |

### 세션 transcript (대화 맥락)
| 세션 | 경로 |
|---|---|
| 현재 (scripts/ 정리, 8필드 구현) | `~/.claude/projects/-Users-jaehyuntak-Desktop-Project-------------claude-gemini-communicator/b5d53b40-d48f-44ef-bfa4-c1f1945fadaf.jsonl` |
| 이전 (God Object 분해, Skill 패키징) | `~/.claude/projects/-Users-jaehyuntak-Desktop-Project-------------claude-gemini-communicator/4a89731a-a50d-4004-a934-32a879aaaab0.jsonl` |

---

## 7. 즉시 실행 가능한 작업 체크리스트

### Phase 5-A: JSONL 버스 (예상 ~200줄)
- [ ] `src/shared/feedback.py`에 `_append_jsonl()` 함수 추가
- [ ] `save_feedback()` 내에서 Markdown + JSONL 동시 기록
- [ ] `config.json`에 `"jsonl_bus": {"enabled": true, "path": "plans/gemini/a2a_events.jsonl"}` 추가
- [ ] fcntl lock으로 동시 쓰기 보호
- [ ] `tests/test_shared.py`에 JSONL 기록 테스트 추가
- [ ] `.gitignore`에 `a2a_events.jsonl` 추가 (선택: 로그성 파일)

### Phase 5-B: parent_message_id (예상 ~50줄)
- [ ] `src/core/a2a_protocol.py`의 `build_a2a_request()`에 `parent_message_id` 선택 파라미터 추가
- [ ] Hook에서 응답의 `message_id`를 다음 요청의 `parent_message_id`로 전달
- [ ] `tests/test_core.py`에 parent_message_id 테스트 추가

### Phase 5-C: CLI 검색 확장 (예상 ~100줄)
- [ ] `src/cli.py`의 `cmd_search()`에 JSONL 쿼리 모드 추가
- [ ] `--format jsonl` 출력 옵션
- [ ] `--agent`, `--status`, `--since` 필터

### 문서 업데이트
- [ ] `CLAUDE.md` Phase 8 섹션 추가
- [ ] `architecture/04_new_architecture_analysis.md` JSONL 버스 반영

---

## 8. 검증 계획

```bash
# 1. 기존 테스트 통과 확인
python3 -m pytest tests/ -v

# 2. JSONL 기록 확인
echo '{"tool_name":"Write","tool_input":{"file_path":"plans/test.md"}}' | python3 src/hooks/hook_auto_task.py
cat plans/gemini/a2a_events.jsonl | python3 -m json.tool --no-ensure-ascii

# 3. JSONL 검색
python3 src/cli.py search --format jsonl --agent gemini --since 2026-02-16

# 4. parent_message_id 체인 확인
python3 -c "
from src.core.a2a_protocol import build_a2a_request
r1 = build_a2a_request('evaluation_request', {}, 'post_tool_use')
r2 = build_a2a_request('evaluation_response', {}, 'gemini_sdk', parent_message_id=r1['message_id'])
print(f'M1: {r1[\"message_id\"]}')
print(f'M2: {r2[\"message_id\"]}, parent: {r2[\"parent_message_id\"]}')
"
```
