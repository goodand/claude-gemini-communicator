# [Framework] 의사결정 및 설계 정의서 — 메시지 버스 우선(001)

> 작성: Codex | 코드베이스 전수 스캔 기반 | 날짜: 2026-02-16
> 개정: CTO(Claude) | Gemini 비판 반영 + 구현 실측 반영 | rev.2: 2026-02-16

## 1. 배경 (Background)

- **Needs (본질적 필요)**
  - `Before`: 현재 시스템은 Hook, Skill, Parser, Bridge가 각각 동작하지만, 에이전트 간 메시지 포맷과 전달 경로가 단일 기준으로 고정되어 있지 않다. A2A 포맷은 일부 경로에만 적용되고(`a2a_schema_enabled`), 나머지 경로는 에이전트별 고유 포맷을 병행한다.
  - 결과적으로 "기능은 존재하지만 협업 메시지 레이어가 분절된 상태"이며, 이 상태에서는 멀티 에이전트 협업이 재현 가능한 시스템으로 수렴하기 어렵다.

- **Wants (구체적 요구)**
  - `After`: 멀티 에이전트 협업의 1차 목표를 **메시지 버스 확립(에이전트 간 메시지 공유 체계)**으로 명시하고, 모든 구조 개편은 이 목표를 지원하는 수단으로 재정렬한다.
  - `Task`: `00_decision_framework.md`의 리팩토링 축(정본화/중복제거/분해)을 메시지 버스 목적에 종속시키고, 평가 기준을 "구조 미화"가 아니라 "메시지 전달 일관성"으로 전환한다.

## 2. 문제 (Problem)

- **Painpoint (고통의 지점)**
  - 에이전트별 메시지 해석 규칙이 다르다.
    - Hook 입력(JSON), Codex notify 이벤트, Gemini headless JSON, Claude transcript JSONL, A2A JSON이 병행된다.
  - 공통 스키마가 전역 강제가 아니라 선택 경로다.
    - A2A가 기본 경로가 아니라 옵션 경로로 남아 있어 end-to-end 일관성이 약하다.
  - 메시지 전달보다 코드 구조가 앞서 평가된다.
    - 리팩토링 완료 여부는 측정하지만, "A→B→C 전달 무결성"은 1급 KPI로 관리되지 않는다.

- **Problem Causes (원인 분석)**
  - `Causal Relationship`
    - Phase별 기능을 빠르게 추가하면서 진입점별 로컬 포맷이 증가
    - 이후 구조 분해(`scripts`/`src`/`skills`)를 진행했지만 메시지 규약 통일은 단계적 옵션으로 남음
    - 결과적으로 코드 모듈은 분리되었으나 메시지 계층은 단일 버스로 수렴하지 못함
  - `Vicious Circle`
    - 포맷 불일치
    - 어댑터/파서 보강으로 임시 연결
    - 경로별 예외 처리 증가
    - 공통 스키마 도입 비용 상승
    - 다시 로컬 포맷을 유지

## 3. 해결책 (Solution)

- **문제 해결 상태 (State or Type)**
  - `State (상태)`
    - 시스템의 최상위 목적을 "리팩토링"이 아니라 "메시지 버스 운영"으로 고정한다.
    - 즉, 어떤 구조 변경이든 "메시지 공유 일관성"을 먼저 통과해야 채택한다.
  - `Type (유형)`
    - **Message Bus First 아키텍처 원칙**
      - Entry 계층(Hook/CLI/Notify/Bridge)은 공통 메시지 엔벨로프로 변환 후 전달
      - Core 계층은 메시지 타입 기반으로 처리(평가/분류/에러분석)
      - Parser 계층은 모든 에이전트 출력을 공통 엔벨로프로 정규화
    - **최소 공통 필드 고정 (8필드, 구현 완료)**
      - `message_id`, `request_id`, `source_agent`, `target_agent`, `message_type`, `payload`, `timestamp`, `status`
      - 선택 확장: `parent_message_id` (멀티홉 체인용, §7 참조)
    - **수단 재정렬**
      - `src` 정본화, 중복 제거, God Object 분해는 모두 "버스 일관성 강화"를 위한 수단으로만 추진

- **Type + Performance (성능 지표)**
  - `KPI`
    - 경로 일관성: Hook/Skill/Parser/Bridge 전 경로에서 공통 필드 충족률 100%
    - 전달 무결성: 에이전트 간 메시지 유실/파싱실패 미기록 건수 0
    - 추적 가능성: 모든 메시지에 `request_id` 연결 가능 비율 100%
    - 복구 가능성: 실패 메시지에 `status`/재시도 근거 기록 비율 100%
  - `Criteria`
    - 임의의 협업 시나리오에서 "누가 누구에게 무엇을 보냈고 어떻게 처리됐는지"를 단일 스키마로 재구성 가능하면 해결
    - 구조 리팩토링 여부와 무관하게 메시지 버스 품질 지표가 우선 통과되면 해결

## 4. 비목표 (Non-goals)

> **핵심 개념**: 비목표는 우선순위 회피가 아니라, 메시지 버스 1단계를 보호하기 위한 경계다.

- **비목표 설정 가이드 (What is NOT a Non-goal)**
  - ❌ "모든 파일 리팩토링 완료" 자체를 성공으로 보지 않는다.
  - ❌ DRY 극대화를 위해 skill 자립성(cp -r)을 훼손하지 않는다.
  - ⚠️ 버스 정합성을 해치는 대규모 구조 실험은 1단계에서 제외한다.

- **비목표 분류 및 케이스**
  - `Case: State`
    - `scripts/` 완전 제거를 이번 단계에서 보장하지 않음
    - Agent Teams/장기 Memory 아키텍처 구현을 이번 단계에서 보장하지 않음
  - `Case: Type`
    - Redis/Kafka 같은 외부 브로커 도입은 1단계 범위 밖
    - 신규 UI/대시보드 개발은 범위 밖
  - `Case: Performance`
    - **Null**: 모델 응답 품질 자체 튜닝은 별도 태스크
    - **Over**: 초기부터 분산 이벤트 플랫폼으로 확장하지 않음
    - **Under**: 로컬 파일 기반 메시지 전달(JSON/JSONL)은 1단계에서 허용

## 5. 제약 (Constraints)

- 기술적 제약
  - 현재 운영 Hook 경로는 `.claude/settings.local.json`의 `scripts/hook_*.py`이며, 운영 경로를 깨지 않는 점진 이행이 필요하다.
  - 스크립트들은 호출자 보호를 위해 `exit(0)` 정책을 유지해야 한다.
  - `skills/*`는 독립 배포 단위이므로 외부 내부모듈 의존 최소화 원칙을 유지해야 한다.
  - 로그/피드백 파일은 동시성 보호(fcntl) 패턴을 유지해야 한다.

- 비용/환경 제약
  - Codex sandbox 네트워크 제한으로 실API 검증 경로가 분리된다.
  - Gemini quota/rate limit 및 CLI 환경 제약(디렉토리 mismatch)이 존재하므로 실패 상태 기록과 재시도 전략이 필수다.

- 시간 제약
  - 빅뱅 전환 대신 메시지 버스 기준으로 단계적 정렬이 필요하다.
  - 1단계는 "공통 스키마 정렬 + 경로 추적 가능성" 확보를 우선하고, 이후 구조 최적화를 진행한다.

---

## 요약: 의사결정 한 줄

> **이 프로젝트의 상위 목적은 리팩토링이 아니라 멀티 에이전트 메시지 버스 확립이며, 정본화·중복제거·모듈분해는 모두 그 목적을 달성하기 위한 수단으로만 집행한다.**

---

## 6. 물리적 메시지 버스 (Physical Bus)

> **Gemini 비판 반영**: "메시지 버스의 물리적 실체가 모호" → 실측 기반으로 구체화

- 현재 구현 (1단계, 실측)
  - **주 경로**: `plans/gemini/gemini_feedback.md` — Markdown append-only 로그
    - DAG 분석 기준 in-degree 6 (프로젝트 내 최다 연결 노드)
    - 모든 Hook, 에러분석, 비동기 실행기가 이 파일에 기록
    - `fcntl.LOCK_EX` 파일 잠금으로 동시 쓰기 보호
  - **보조 경로**: `scripts/.error_history.json` — 에러 이력/중복 방지
  - **전달 방식**: `stdout → stdin` (Hook JSON 파이프) + 파일 append

- 2단계 확장 (선택, 필요 시)
  - JSONL 버스 파일 도입: `plans/gemini/a2a_events.jsonl`
    - 1라인 1 JSON, UTF-8, `\n` 종결
    - 기존 Markdown 로그와 병행 기록 (tee 패턴)
  - 이유: 기계 소비(파싱/검색/통계)에 Markdown보다 JSONL이 적합
  - `.bus/` 별도 디렉토리는 불필요 — `plans/gemini/` 안에 통합

- 동시성/잠금 전략 (구현 완료)
  - Writer: `fcntl.LOCK_EX` 배타 잠금 (`src/shared/feedback.py`)
  - Reader: `tail -f` 또는 직접 읽기 (잠금 불필요)
  - Rotation: 현재 미구현, 필요 시 날짜 기반 분리 (`gemini_feedback.2026-02.md`)

## 7. 메시지 엔벨로프 (Common Envelope)

> **Gemini 비판 반영**: "parent_message_id / sequence_number 부재" → 선택 확장으로 정의

- 필수 필드 (8개, `src/core/a2a_protocol.py`에 구현 완료)
  - `message_id`: UUIDv4 — 메시지 고유 식별
  - `request_id`: UUIDv4 — 요청-응답 쌍 추적 (피드백 로그에도 기록)
  - `source_agent`: 발신 에이전트 (`"claude"`)
  - `target_agent`: 수신 에이전트 (`"gemini"`, `"codex"`)
  - `message_type`: `"evaluation_request"` | `"evaluation_response"` | `"error_analysis"` 등
  - `payload`: 본문 (자유 구조)
  - `timestamp`: ISO 8601 UTC
  - `status`: `"pending"` | `"success"` | `{"code": "error", "error_type": "sdk", "detail": "..."}` | `"fallback"`

- 선택 확장 필드 (2단계, 멀티홉 체인용)
  - `parent_message_id`: 직접 상위 메시지 ID (단일 홉에선 생략)
  - `a2a_version`: 스키마 버전 (`"1.0"`)

- 구현 상태
  - `build_a2a_request()`: 8필드 생성 + 하위 호환 `source` 필드 유지
  - `parse_a2a_response()`: 응답에서 8필드 복원 + `parse_error_status()` 자동 적용
  - `parse_error_status()`: 문자열 prefix (`[SDK_ERROR]`, `[ERROR]`, `[FALLBACK]`) → 구조화 status

- 샘플 (실측 기반)

```json
{
  "a2a_version": "1.0",
  "message_id": "7fb1c3a9-...",
  "request_id": "d4e5-...",
  "timestamp": "2026-02-16T06:25:31+00:00",
  "source_agent": "claude",
  "target_agent": "gemini",
  "message_type": "evaluation_request",
  "status": "pending",
  "payload": {"file": "architecture/001_decision_framework.md"}
}
```

- 의도적 비채택 (과설계 방지)
  - `sequence_number`: 파일 기반 시스템에서 라인 번호가 자연 순서 → 별도 필드 불필요
  - `causal_depth`: 현재 1-hop (Claude→Gemini) 구조에서 불필요, 멀티홉 시 `parent_message_id` 체인으로 대체
  - `targets` 배열/DSL: 현재 1:1 통신만 존재, `target_agent` 문자열로 충분
  - `root_message_id`: `request_id`가 동일 역할 수행

## 8. 순서/인과성 (Ordering & Causality)

- 순서 보장 (현재)
  - Markdown append-only: 타임스탬프 헤더가 자연 순서 (`## [2026-02-16 06:25:31]`)
  - JSONL 전환 시: 파일 라인 번호 = 자연 순서 (별도 `sequence_number` 불필요)

- 인과 추적 (구현 완료)
  - `request_id`: 요청-응답 쌍 연결 (Hook → Gemini 호출 → 피드백 기록까지 동일 ID)
  - 에러 해시(`hash_error`): 동일 에러 재발 추적 (`src/core/error_analyzer.py`)
  - 향후: `parent_message_id`로 멀티홉 체인 추적 (현재는 1-hop만 존재)

- 전달 의미론
  - Best-effort: Hook 실패 시 `exit(0)` → Claude 정상 동작 보호 우선
  - 중복 방지: 에러 해시 + `analyzed` 플래그로 동일 에러 재분석 차단
  - 쿨다운: 파일별 300초, 에러 분석 전역 60초

## 9. KPI와 외부 요인 분리 (Metrics Isolation)

> **Gemini 비판 반영**: "100% 충족률은 외부 요인(Gemini quota 등) 분리 없이 의미 없다"

- 내부 KPI (버스 품질, 100% 목표 가능)
  - `schema_conformance`: 8 필수 필드 충족률 — 내부 코드로 보장 가능
  - `request_id_coverage`: 모든 피드백 기록에 request_id 포함 비율
  - `error_hash_dedup`: 동일 에러 재분석 방지율

- 외부 KPI (환경 의존, 100% 불가 → SLO 기반)
  - `gemini_call_success_rate`: Gemini API 호출 성공률 (quota, 네트워크 영향)
  - `end_to_end_delivery`: Hook 트리거 → 피드백 기록 완료율

- 외부 요인 분류 (구현 완료: `parse_error_status()`)
  - `error_type: "sdk"` → Gemini SDK 오류 (quota, 인증, 네트워크)
  - `error_type: "general"` → CLI 실패, 파싱 오류
  - `code: "fallback"` → SDK 실패 후 CLI 전환 (부분 성공)
  - 이 분류가 `status` 필드에 구조화되어 내부/외부 실패 자동 구분 가능

- 측정 원칙
  - 내부 KPI 미달 → 코드 버그, 즉시 수정
  - 외부 KPI 미달 → 환경 문제, 대응 전략 조정 (키 순회, 모델 전환, CLI fallback)

## 10. 마이그레이션 전략 (Phased Migration)

- Phase 0 (완료): God Object 분해
  - `scripts/a2a_bridge.py` (836줄) → `src/` 3계층 DAG (shared/ → core/ → hooks/)
  - 12노드 26엣지, 순환 의존 0 (graph-structure-classifier 검증)

- Phase 1 (완료): 8필드 엔벨로프 + request_id 추적
  - `build_a2a_request()`: 8필드 생성
  - `parse_error_status()`: 에러 구조화
  - 전 Hook에서 `request_id` 생성/전파

- Phase 2 (현재): Skills 자립화 + 크로스 에이전트
  - 3개 Skill 패키지 완성 (gemini-reviewer, agent-parser, cross-agent-bridge)
  - `cp -r` 독립 배포 가능

- Phase 3 (다음): JSONL 버스 도입 (선택)
  - Markdown과 병행 기록 → 기계 소비 경로 확보
  - `parent_message_id` 필수화로 멀티홉 체인 추적

## 11. 리스크 및 대응 (Risks & Mitigations)

- 파일 잠금 경합
  - 현황: `fcntl.LOCK_EX`로 해결 완료 (`src/shared/feedback.py`)
  - 잔여 리스크: 비동기 모드에서 다수 프로세스 동시 쓰기 시 지연 가능 → 쿨다운으로 완화

- 피드백 파일 크기 증가
  - 현황: `gemini_feedback.md` 무제한 append
  - 대응: 날짜 기반 분리 또는 오래된 엔트리 아카이브 (수동)

- 외부 API 실패 전파
  - 현황: `parse_error_status()`로 분류 + CLI fallback + 키/모델 순회
  - 잔여 리스크: 모든 키/모델 소진 시 → `[ERROR]` 로그 후 `exit(0)` (Claude 보호)

- KPI "영구 미달" 리스크
  - 대응: §9에서 내부/외부 KPI 분리 → 내부 KPI만 100% 목표, 외부는 SLO 기반
