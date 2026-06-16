# Troubleshooting — agent-task-packet

## CASE-001: validate가 빈 why를 통과시킴

**증상**: `why` 필드가 비어있는 packet이 `validate` 통과 (exit 0)
**원인**: `validate_packet()`에서 `goal` 길이 검증은 있었으나 `why` 검증 누락
**해결**: `why` 최소 5자 검증 추가 (`len(str(data.get("why","")).strip()) < 5`)
**교훈**: 필수 필드가 REQUIRED_FIELDS에 있어도 "존재"만 확인하고 "의미 있는 값" 검증이 빠질 수 있다. 새 필수 필드 추가 시 빈 값/짧은 값 검증도 함께 넣을 것.

## CASE-002: show에서 created_by 비면 "by" dangling

**증상**: `created_by`가 빈 문자열일 때 `show` 출력이 `Created: 2026-03-15 by ` — "by " 뒤에 아무것도 없음
**원인**: f-string에서 `data.get('created_by', '?')` 사용 — 빈 문자열은 falsy지만 `get()`의 기본값 '?'는 키가 없을 때만 작동
**해결**: `created_by.strip()` 후 truthy 분기 — 값이 있으면 "by {name}" 포함, 없으면 생략
**교훈**: `dict.get(key, default)`는 키가 **없을 때**만 default를 반환한다. 빈 문자열(`""`)은 키가 **있는** 상태이므로 default가 적용되지 않는다. 출력 포맷에서 조건부 텍스트는 항상 truthy 분기 처리.

## CASE-003: validate가 빈 task_id를 통과시킴

**증상**: `task_id`가 `""` 또는 공백 문자열인 packet이 `validate`를 통과
**원인**: `validate_packet()`에서 `task_id` 타입만 검사하고, 비어있는 문자열은 막지 않음
**해결**: `task_id`가 문자열인 경우에도 `strip()` 결과가 비면 `task_id가 비어있다` 오류 추가
**교훈**: 식별자 필드는 타입 검증만으로 충분하지 않다. 문자열 식별자는 항상 빈 문자열과 공백-only 입력을 별도 차단해야 한다.
