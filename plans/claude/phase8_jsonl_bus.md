# Phase 8: JSONL 메시지 버스 + parent_message_id + CLI 확장

## 구현 완료 요약

### Phase 8-A: JSONL 메시지 버스
- `config.json`에 `jsonl_bus` 설정 블록 추가 (`enabled: true`, `path: plans/gemini/a2a_events.jsonl`)
- `src/shared/config.py`: `validate_config()`에 `jsonl_bus` 검증 추가
- `src/shared/feedback.py`: `_append_jsonl()` 신규 함수 + `save_feedback()` 확장 (Dependency Injection으로 DAG 위반 없음)
- `src/hooks/hook_auto_task.py`: JSONL 파라미터 전달
- `src/hooks/hook_stop.py`: JSONL 파라미터 전달

### Phase 8-B: parent_message_id
- `src/core/a2a_protocol.py`: `build_a2a_request()`에 `parent_message_id` 선택 파라미터 추가
- Hook에서 요청 엔벨로프 `message_id` → 응답 `parent_message_id`로 전파

### Phase 8-C: CLI 검색 확장
- `src/cli.py`: `parse_jsonl_events()`, `_search_jsonl()` 신규 + `cmd_search()` JSONL 모드 분기
- `--jsonl`, `--agent`, `--request-id`, `--since` argparse 옵션 추가
- `cmd_status()`에 JSONL 버스 상태 표시 추가

### 버그 수정
- 기존 `test_a2a_parse_valid()` 테스트 수정: `status`가 dict인데 문자열 비교하던 버그 해결

## 테스트 결과
- 22/22 ALL PASSED (Phase 8 신규 6건 포함)

## 롤백
- `config.json`에서 `"jsonl_bus": {"enabled": false}` 설정하면 JSONL 기록 비활성화
- parent_message_id는 호출 시 파라미터 생략하면 됨
- CLI는 `--jsonl` 안 쓰면 기존 Markdown 검색 동작
