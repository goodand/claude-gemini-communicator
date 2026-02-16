# CSO(Gemini) 아키텍처 재구조화 전략

> 작성: CSO(Gemini 2.5 Flash) | 날짜: 2026-02-16
> 입력: CTO(Claude)의 01_dependency_analysis.md

---

## A) scripts/ vs skills/ 통합 방안

- **살릴 것**: `skills/` 디렉토리 구조 → 모듈화된 핵심 로직의 주된 위치
- **버릴 것**: `scripts/` 중복 파서 3종 삭제, `a2a_bridge.py` 완전 분해 후 삭제
- **통합**: hooks가 새 `core/`/`shared/` 모듈을 직접 호출하도록 변경

## B) a2a_bridge.py 분해 → 6개 도메인

| 새 모듈 | 위치 | 함수 |
|---|---|---|
| `cooldown_manager.py` | `src/core/` | check_cooldown, load/save_cooldown_state |
| `gemini_service.py` | `src/core/` | call_gemini, _call_gemini_sdk/cli/api_key/oauth, call_gemini_async |
| `a2a_protocol.py` | `src/core/` | build_a2a_request, parse_a2a_response, a2a_response_to_markdown |
| `error_analyzer.py` | `src/core/` | scan_transcript_for_errors, check_error_and_analyze, hash_error 등 |
| `config_manager.py` | `src/shared/` | load_config, load_env |
| `feedback_manager.py` | `src/shared/` | save_feedback (7곳 → 1곳 통합) |
| `hook_utils.py` | `src/shared/` | format_hook_output, read_file_content |

## C) 새 디렉토리 트리

```
claude-gemini-communicator/
├── src/
│   ├── cli.py                  ← Main Entry Point (간소화)
│   ├── async_runner.py
│   ├── hooks/
│   │   ├── hook_auto_task.py
│   │   ├── hook_stop.py
│   │   └── hook_pre_tool.py
│   ├── core/
│   │   ├── cooldown_manager.py
│   │   ├── gemini_service.py
│   │   ├── a2a_protocol.py
│   │   └── error_analyzer.py
│   └── shared/
│       ├── config_manager.py
│       ├── feedback_manager.py
│       └── hook_utils.py
├── skills/
│   ├── gemini-reviewer/        ← core/gemini_service 활용
│   ├── agent-parser/           ← 파서 정본
│   └── cross-agent-bridge/     ← core/ 모듈 활용
├── architecture/
├── plans/
├── schemas/
└── [config files]
```

## D) 마이그레이션 5단계

| 단계 | 내용 | 위험도 | 롤백 |
|---|---|---|---|
| 1 | `src/shared/` 생성 — 중복 유틸 통합 | 낮음 | git revert |
| 2 | `src/core/` 생성 — a2a_bridge.py 분해 | **중간** | a2a_bridge.py를 프록시로 유지 |
| 3 | 파서 단일화 — scripts/ 파서 삭제 | 낮음 | git revert |
| 4 | hooks/cli.py 의존성 업데이트 | **중간** | 파일별 독립 커밋 |
| 5 | 잔여 코드 정리 — a2a_bridge.py/scripts/ 삭제 | 낮음 | git revert |

## E) 함정 경고

1. **숨겨진 내부 상태 의존성** — a2a_bridge.py 내 전역/모듈 수준 상태 변수의 암묵적 의존
2. **테스트 커버리지 부족** — 파일 I/O, Gemini API 호출 등 모킹 어려운 부분
3. **cli.py/hooks의 과도한 오케스트레이션** — 또 다른 God Object 생성 위험
