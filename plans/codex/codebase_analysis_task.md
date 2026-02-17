# Codex 코드베이스 분석 태스크

## 목적

이 프로젝트의 현재 코드베이스를 분석하여 `plans/codex/codebase_analysis.md`에 결과를 작성하라.
이후 코딩 태스크의 컨텍스트로 활용할 분석 문서다.

## 분석 범위

### 1. 디렉토리 구조 파악
- `src/` 전체 파일 목록과 각 파일의 역할 (1줄 요약)
- `src/shared/`, `src/core/`, `src/hooks/` 3-레이어 구조 이해

### 2. 의존성 그래프
- 각 모듈이 import하는 대상 정리 (모듈 간 의존)
- DAG 규칙 확인: `hooks/ → core/ → shared/` 방향만 허용, 역방향 없는지 검증

### 3. 핵심 데이터 흐름
- Hook 진입 → 비즈니스 로직 → 저장/출력 경로 추적
- `hook_auto_task.py`: 어떤 순서로 함수가 호출되는가
- `hook_stop.py`: Plan 감지 + 에러 감지 각각의 흐름

### 4. 설정 구조
- `config.json`의 모든 설정 키와 소비처 (어떤 모듈에서 사용되는가)
- `.env` 환경변수 목록

### 5. 최근 추가된 모듈 분석 (Phase 8+)
- `src/core/router.py`: 라우팅 규칙 매칭 로직
- `src/core/memory.py`: JSONL 이벤트 조회 인터페이스
- `src/core/scheduler.py`: 작업 등록/추적 라이프사이클
- 이 3개 모듈이 기존 코드에 어떻게 통합되어 있는지, 아직 연결 안 된 부분은 무엇인지

### 6. 테스트 현황
- `src/cli.py test` 내 테스트 그룹별 항목 정리
- 테스트 커버리지가 부족한 영역 식별

### 7. 개선 기회 식별
- 아직 연결되지 않은 코드 (dead code, 미통합 모듈)
- 중복 로직
- 타입 힌트/에러 처리 누락

## 출력

분석 결과를 `plans/codex/codebase_analysis.md`에 작성하라.

## 실행 방법

```bash
# 프로젝트 루트에서 Codex CLI 실행
codex -m gpt-5.3-codex "plans/codex/codebase_analysis_task.md 파일의 지시에 따라 코드베이스를 분석하고 plans/codex/codebase_analysis.md에 결과를 작성해줘"
```

## 참고 파일

- `CLAUDE.md` (프로젝트 루트) — 전체 프로젝트 가이드 (Phase 8+ 반영)
- `config.json` — 전체 설정
- `src/cli.py` — CLI 도구 + 테스트 스위트
