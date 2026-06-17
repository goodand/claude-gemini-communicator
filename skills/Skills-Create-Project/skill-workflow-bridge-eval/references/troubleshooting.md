# Troubleshooting — skill-workflow-bridge-eval

> 케이스 형식: CASE-XXX (증상 → 원인 → 해결 → 교훈)

## CASE-001: JSON 파일 입력 시 classify_output AttributeError

- **증상**: `classify --raw file.json` 실행 시 `AttributeError: 'dict' object has no attribute 'strip'`
- **원인**: `_load()`가 `.json` 확장자이면 `json.load()`로 파싱하여 dict 반환. `classify_output()`은 문자열만 기대.
- **해결**: `classify_output()` 상단에 `isinstance(raw_text, (dict, list))` 체크 추가. `build_bridge_eval()` 내부에서도 dict인 경우 `json.loads()` 대신 직접 사용.
- **교훈**: `_load()`의 반환 타입이 문자열/dict 두 가지인 점을 모든 호출부에서 고려해야 한다. 타입 힌트나 일관된 반환 타입으로 예방 가능.
