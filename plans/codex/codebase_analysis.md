# Codebase Analysis (2026-02-17)

## 0) 분석 전제/입력
- 지시 파일: `plans/codex/codebase_analysis_task.md`
- 실제 확인 파일:
  - `src/` 전체 (`18`개 Python 파일)
  - `config.json`
  - `.env`, `.env.example`
- 참고:
  - 루트 `CLAUDE.md`는 현재 워크스페이스에 **없음**
  - 대체 가이드로 `plans/claude/claude_project_guide.md`를 확인

---

## 1) 디렉토리 구조 파악

### `src/` 파일 목록 + 역할(1줄)
- `src/__init__.py`: 패키지 마커(내용 없음)
- `src/async_runner.py`: 비동기 Gemini 호출용 백그라운드 실행기
- `src/cli.py`: 운영/진단/검색/테스트/체인 추적 CLI
- `src/core/__init__.py`: 패키지 마커(내용 없음)
- `src/core/a2a_protocol.py`: A2A 엔벨로프 생성/응답 파싱/마크다운 변환
- `src/core/cooldown.py`: 파일별 쿨다운 상태 저장/검사
- `src/core/error_analyzer.py`: transcript 에러 스캔 + Lazy Analysis 트리거
- `src/core/gemini_service.py`: Gemini SDK/REST/CLI 호출 및 fallback
- `src/core/memory.py`: JSONL 이벤트 로드/필터/요약 API
- `src/core/router.py`: message_type/확장자 기반 대상 에이전트 라우팅
- `src/core/scheduler.py`: 비동기 작업 등록/완료/실패/정리 상태 저장
- `src/hooks/__init__.py`: 패키지 마커(내용 없음)
- `src/hooks/hook_auto_task.py`: PostToolUse(Write/Edit) 자동 평가 훅
- `src/hooks/hook_pre_tool.py`: PreToolUse(Bash) 위험 명령 차단/경고 훅
- `src/hooks/hook_stop.py`: Stop 훅(Plan 감지 + 에러 감지)
- `src/shared/__init__.py`: 패키지 마커(내용 없음)
- `src/shared/config.py`: `.env`/`config.json` 로딩 및 config 검증
- `src/shared/feedback.py`: Markdown/JSONL 피드백 이벤트 저장
- `src/shared/hook_io.py`: Hook stdout 포맷 및 파일 읽기 유틸

### 3-레이어 구조(`shared/`, `core/`, `hooks/`)
- `shared/`: 입출력/설정/저장 인프라 유틸
- `core/`: 도메인 로직(호출, 라우팅, 분석, 상태)
- `hooks/`: Claude Hook 진입점(입력 해석 + core orchestration)

---

## 2) 의존성 그래프

### 모듈 간 import 요약
- `hooks/hook_auto_task.py` -> `shared.config`, `shared.feedback`, `shared.hook_io`, `core.cooldown`, `core.gemini_service`, `core.a2a_protocol`, `core.router`
- `hooks/hook_stop.py` -> `shared.config`, `shared.feedback`, `shared.hook_io`, `core.gemini_service`, `core.a2a_protocol`, `core.error_analyzer`, `core.router`
- `hooks/hook_pre_tool.py` -> `shared.config`
- `core/gemini_service.py` -> `shared.config`, `shared.hook_io` (지연 import로 `shared.feedback`)
- `core/error_analyzer.py` -> (지연 import) `core.gemini_service`, `shared.feedback`
- `core/memory.py` -> `shared.config`
- `core/scheduler.py` -> `shared.config`
- `cli.py` -> `shared.*`, `core.*`, `hooks.hook_pre_tool` (테스트용)
- `async_runner.py` -> `shared.config`, `core.gemini_service`

### DAG 규칙 검증 (`hooks/ -> core/ -> shared/`)
- 자동 점검 결과:
  - `shared -> core` 역의존: 없음
  - `shared -> hooks` 역의존: 없음
  - `core -> hooks` 역의존: 없음
- 결론: 레이어 DAG 규칙은 `src` 내부에서 유지됨

### 텍스트 그래프
- `hooks/*` -> `core/*` -> `shared/*`
- `cli.py`, `async_runner.py`는 레이어 외곽 orchestrator/entrypoint 역할

---

## 3) 핵심 데이터 흐름

### A) Hook 진입 -> 비즈니스 로직 -> 저장/출력
- 공통:
  1. Hook JSON stdin 파싱
  2. `load_env()` + `load_config()`
  3. 조건 필터/판정
  4. `call_gemini()` 또는 내부 분석 로직
  5. `save_feedback()`/`log_jsonl_event()`로 저장
  6. `format_hook_output()`으로 Claude context 주입

### B) `hook_auto_task.py` 호출 순서
1. stdin JSON 파싱, `tool_name`이 `Write|Edit`인지 검사
2. `tool_input.file_path` 확보
3. `watch_extensions`, `exclude_files` 필터
4. `check_cooldown(file_path, config)`
5. 코드/문서 프롬프트 선택(`code_extensions`)
6. `build_a2a_evaluation_prompt()` 적용
7. `async_mode=true`면 `call_gemini_async()` 후 즉시 반환
8. 동기 모드면 `resolve_target("evaluation_request", file_path)`
9. `build_a2a_request()` 생성 -> request JSONL 기록
10. `call_gemini()` 실행
11. `a2a_schema_enabled`면 `parse_a2a_response()` -> `a2a_response_to_markdown()`
12. `save_feedback()`로 Markdown + (옵션)JSONL 응답 기록
13. `format_hook_output()` 출력

### C) `hook_stop.py` 흐름

#### Plan 감지 흐름
1. `extract_last_assistant_text()`로 마지막 assistant 텍스트 추출(transcript 우선)
2. `min_content_length` 미만이면 종료
3. `plan_detection_prompt`로 `call_gemini()` 분류 호출
4. A2A 모드면 JSON 파싱으로 `is_plan`, 아니면 문자열 "예" 포함 검사
5. plan이 아니면 종료
6. 평가 프롬프트(`evaluation_prompt`) 구성 + A2A 확장
7. 비동기면 `call_gemini_async()`
8. 동기면 `resolve_target("evaluation_request")` -> 요청 JSONL 기록
9. `call_gemini()` -> (옵션)A2A 파싱/렌더링 -> `save_feedback()`

#### 에러 감지 흐름
1. `error_detection.enabled` 확인
2. `transcript_path` 확인
3. `scan_transcript_for_errors(tail_lines)`로 최근 로그 스캔
4. 에러 없으면 종료
5. `check_error_and_analyze(errors, config)`:
   - 에러 정규화/해시/심각도 분류
   - threshold + global cooldown 만족 시만 분석
   - 요청 JSONL 기록
   - Gemini 분석 호출
   - 이력 업데이트(`analyzed=true`, `last_analysis_time`)
   - `save_feedback()`로 결과 저장

---

## 4) 설정 구조

## `config.json` 키 + 소비처
- `gemini_cmd`: `core/gemini_service.py`(CLI 호출), `cli.py`(doctor 상태 점검)
- `gemini_timeout`: `core/gemini_service.py`
- `cooldown_seconds_per_file`: `core/cooldown.py`, `cli.py`(status 출력)
- `min_content_length`: `hooks/hook_stop.py`
- `watch_extensions`: `hooks/hook_auto_task.py`, `cli.py`(status 출력)
- `exclude_files`: `hooks/hook_auto_task.py`
- `evaluation_prompt`: `hooks/hook_auto_task.py`, `hooks/hook_stop.py`, `shared/config.py`(필수 필드 검증)
- `code_evaluation_prompt`: `hooks/hook_auto_task.py`
- `code_extensions`: `hooks/hook_auto_task.py`
- `plan_detection_prompt`: `hooks/hook_stop.py`
- `sdk.enabled`: `core/gemini_service.py`, `cli.py`
- `sdk.model`: `core/gemini_service.py`, `cli.py`, `shared/config.py`(warn 검증)
- `sdk.fallback_models`: `core/gemini_service.py`
- `sdk.fallback_to_cli`: `core/gemini_service.py`, `cli.py`
- `sdk.oauth_creds_path`: `core/gemini_service.py`
- `sdk.api_key_env`: `core/gemini_service.py`
- `sdk.max_output_tokens`: `core/gemini_service.py`
- `sdk.temperature`: `core/gemini_service.py`, `shared/config.py`(범위 검증)
- `sdk.oauth_client_id_env`: `core/gemini_service.py`
- `sdk.oauth_client_secret_env`: `core/gemini_service.py`
- `async_mode`: `hooks/hook_auto_task.py`, `hooks/hook_stop.py`, `cli.py`
- `async_timeout`: 현재 `src/` 내 직접 소비처 없음
- `a2a_schema_enabled`: `hooks/hook_auto_task.py`, `hooks/hook_stop.py`, `core/a2a_protocol.py`, `cli.py`
- `pre_tool_guard.enabled`: `hooks/hook_pre_tool.py`, `cli.py`
- `pre_tool_guard.custom_block_patterns`: `hooks/hook_pre_tool.py`, `shared/config.py`(정규식 검증)
- `jsonl_bus.enabled`: `shared/feedback.py`, `cli.py`
- `jsonl_bus.path`: `shared/feedback.py`, `core/memory.py`, `cli.py`, `shared/config.py`(검증)
- `routing_rules`: `core/router.py`
- `error_detection.enabled`: `hooks/hook_stop.py`, `cli.py`
- `error_detection.tail_lines`: `hooks/hook_stop.py`
- `error_detection.global_cooldown_seconds`: `core/error_analyzer.py`
- `error_detection.thresholds`: `core/error_analyzer.py`, `shared/config.py`(검증)
- `error_detection.error_prompt`: `core/error_analyzer.py`
- `error_detection.feedback_prefix`: `core/error_analyzer.py`

### `.env` 환경변수 목록
- 코드/샘플 기준 사용 변수명:
  - `GEMINI_API_KEY` (기본)
  - `GEMINI_API_KEY_*` prefix 키들(복수 API key 순회)
  - `GEMINI_OAUTH_CLIENT_ID`
  - `GEMINI_OAUTH_CLIENT_SECRET`
- `load_env()`는 `.env`의 `KEY=VALUE`를 환경에 주입(이미 존재하면 덮어쓰지 않음)

---

## 5) Phase 8+ 신규 모듈 분석 (`router`, `memory`, `scheduler`)

### `src/core/router.py`
- 기능: `routing_rules`를 순서대로 평가해 `target` 결정(`match_type`, `match_ext`, `*`)
- 통합 상태:
  - 런타임 통합됨: `hook_auto_task.py`, `hook_stop.py`
  - 테스트 통합됨: `cli.py test` 그룹 8
- 관찰:
  - 룰 스키마 검증(필드 타입/누락)은 별도 없음

### `src/core/memory.py`
- 기능: JSONL 이벤트 로드 + 최근/에이전트/타입/request_id/since 필터 + 요약
- 통합 상태:
  - 런타임 훅/CLI 명령 경로에는 직접 미사용
  - `cli.py test`에서만 함수 호출
- 결론: **미통합(테스트 전용 상태)**

### `src/core/scheduler.py`
- 기능: `.scheduler_jobs.json` 기반 작업 등록/완료/실패/조회/정리
- 통합 상태:
  - `call_gemini_async()`/`async_runner.py`와 연결 없음
  - `cli.py test`에서 lifecycle 검증만 수행
- 결론: **미통합(테스트 전용 상태)**

### 기존 코드와의 통합 요약
- 완전 통합: `router`
- 부분/미통합: `memory`, `scheduler`
- 특히 scheduler는 문서상 "비동기 작업 추적"을 표방하지만 실제 async 경로에서 호출되지 않음

---

## 6) 테스트 현황 (`src/cli.py test`)

### 그룹별 항목
1. Config 검증
- config 로드
- 필수 필드 존재

2. 에러 감지 함수
- normalize_error_text
- hash_error
- classify_error_severity

3. A2A 프로토콜
- 요청 생성
- 정상 JSON 파싱
- raw text 폴백
- markdown 변환

4. PreToolUse Guard
- block 패턴들
- allow 케이스
- 문자열 내부 오탐 방지

5. Config validate
- 현재 config 유효성
- 필수 필드 누락 감지

6. Phase 8 JSONL + parent_message_id
- JSONL append
- JSONL disabled(실질 검증 약함)
- parent_message_id 전파/부재
- jsonl_bus 검증
- JSONL 파싱

7. 멀티홉 체인
- parent_message_id 체인
- prefix 매칭
- 미존재 ID
- 요청→응답 pair
- log_jsonl_event

8. Reference Architecture
- Router 4종
- Memory 3종
- Scheduler 2종

### 커버리지 부족 영역
- 실제 Hook 엔트리 통합 테스트 부재(`hook_auto_task.main`, `hook_stop.main` end-to-end)
- `gemini_service` 실호출 경로(API key/OAuth/CLI fallback) 단위/통합 테스트 부재
- `async_runner.py` 테스트 부재
- `hook_stop`의 Plan 판정 분기(A2A on/off, JSON 파싱 실패 fallback) 테스트 부재
- `error_analyzer.check_error_and_analyze()`의 cooldown/threshold 경계값 테스트 부족
- `test_jsonl_disabled()`는 assertion 없는 사실상 noop

---

## 7) 개선 기회 식별

### A) 미통합/사실상 dead code
- `core/memory.py`: 런타임 경로 미사용(테스트 전용)
- `core/scheduler.py`: async 파이프라인과 미연결(테스트 전용)
- `config.async_timeout`: 소비처 없음

### B) 중복 로직
- JSONL 읽기 로직이 `cli.py:parse_jsonl_events`와 `core/memory.load_events`로 중복
- JSONL 경로 계산이 `cli.py/_get_jsonl_path`, `core/memory`, `shared/feedback`에 분산

### C) 타입/에러 처리/신뢰성 리스크
- 여러 entrypoint에서 broad `except Exception: sys.exit(0)` 사용 -> 장애 원인 은닉
- `hook_auto_task.py`의 `exclude_files`는 basename 비교만 수행
  - `config.json`에 경로형 항목(`plans/gemini/gemini_feedback.md`)이 있어도 basename 매칭에는 반영되지 않음
  - 현재는 `gemini_feedback.md` 항목이 함께 있어 실제 차단은 동작하지만, 설정 표현이 일관적이지 않음
- `hook_stop.py` plan 분류 결과 판정이 "예" substring 기반 fallback이라 오검출 가능
- `scheduler.py` 파일 쓰기 락 없음(동시 접근 시 경쟁 위험)
- `core/router.py` 규칙 구조 validation 부재

### D) 보안/운영 관점 메모
- 현재 `.env`에 실제 API key 값이 존재(로컬 파일 기준). 저장소 유출 방지 정책 점검 필요

---

## 부록) 핵심 결론
- 3-레이어 DAG(`hooks -> core -> shared`)는 현재 코드에서 잘 지켜짐.
- Phase 8+ 중 `router`는 운영 경로에 붙었지만, `memory/scheduler`는 테스트 코드 중심으로 남아 있음.
- 다음 구현 태스크에서는 `scheduler`를 `call_gemini_async`/`async_runner`에 연결하고, JSONL 조회는 `core/memory`로 일원화하는 것이 가장 큰 구조 개선 포인트.
