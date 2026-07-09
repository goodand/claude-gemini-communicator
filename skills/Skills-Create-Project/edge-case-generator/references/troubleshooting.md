# Troubleshooting — edge-case-generator

## CASE-001: CLI 핸들러를 validate 함수로 잘못 선택

- **증상**: `run` 실행 시 모든 케이스가 `EXCEPTION`으로 떨어지며 `'dict' object has no attribute 'file'` 또는 `'files'` 오류가 반복됨
- **원인**: 함수 탐색이 `cmd_validate()` 같은 CLI 핸들러를 먼저 집어와서, JSON dict를 argparse 객체처럼 넘김
- **해결법**: 함수 선택 시 `validate_*`만 대상으로 제한하고, `cmd_*`는 제외. 파라미터 1개짜리 순수 validate 함수만 선택
- **교훈**: 스크립트 안에 `validate` 문자열이 들어간다고 전부 검증 함수는 아니다. CLI 레이어와 순수 로직을 구분해야 한다

## CASE-002: 스크립트 전체를 스캔해서 helper 규칙까지 오탐

- **증상**: `analyze`가 실제 `validate_*`에 없는 규칙까지 추출함. 예: helper 함수의 `overlap` 문자열 때문에 cross-field 규칙이 생김
- **원인**: 정규식/문자열 검색 대상을 파일 전체 source로 잡아서 validate 외부 문맥까지 포함
- **해결법**: AST로 `validate_*` 함수 본문만 추출한 뒤, 그 텍스트에 대해서만 규칙 패턴 검색
- **교훈**: "이 skill은 validate 함수만 분석한다"는 SKILL.md 문구가 실제 코드에 반영돼야 한다

## CASE-003: 단일 필드 조각 케이스라서 의미 없는 실패가 대량 발생

- **증상**: `generate`로 만든 케이스를 `run`에 넣으면, 의도한 규칙 때문이 아니라 다른 필수 필드 누락 때문에 대부분 실패
- **원인**: 케이스 입력이 `{field: value}` 같은 partial object 형태라 baseline 유효 입력이 없음
- **해결법**: REQUIRED_FIELDS와 enum 규칙을 이용해 baseline valid object를 먼저 만들고, 규칙별 케이스는 baseline 위에 override
- **교훈**: edge case는 "필드 하나만 바꾼 실험"이어야 한다. baseline이 없으면 노이즈가 결과를 덮는다

## CASE-004: target validate의 실제 빈틈이 report에 잡힘

- **증상**: `agent-task-packet/scripts/packet_builder.py` 대상 실행에서 `task_id_type_invalid_3`이 `fail` 기대였는데 `pass`로 보고됨
- **원인**: target validate가 `task_id`에 대해 문자열 타입만 검사하고, 빈 문자열/공백 문자열은 막지 않음
- **해결법**: target skill의 validate에서 `not tid.strip()` 같은 빈 문자열 검사를 추가
- **교훈**: baseline 기반 케이스에서 나온 unexpected pass는 generator 노이즈가 아니라 실제 validate 누락일 가능성이 높다

## CASE-005: symlink 케이스가 placeholder 경로라서 거짓 양성 발생

- **증상**: `codex-worktree-dispatch/scripts/dispatch_manager.py` 대상 실행에서 `symlink_path`가 `fail` 기대였는데 `pass`로 보고됨
- **원인**: generator가 `"SYMLINK_TARGET"` 같은 placeholder만 넣고 실제 symlink를 만들지 않았고, target validate는 현재 작업 디렉토리가 아니라 repo root 기준으로 경로를 해석했음
- **해결법**: `run` 단계에서 실제 symlink fixture를 생성하고, target validate의 경로 해석 기준(`cwd` 또는 `repo_root`)에 맞는 상대경로로 주입
- **교훈**: 파일시스템 검증 케이스는 문자열만 바꿔서는 부족하다. symlink, 파일 존재, repo root 해석처럼 환경 의존 검증은 setup fixture와 path-base 추정이 함께 가야 한다

---

## 케이스 추가 템플릿

```markdown
## CASE-XXX: [짧은 제목]

- **증상**: [에러 메시지 또는 관찰된 동작]
- **원인**: [근본 원인]
- **해결법**: [구체적 해결 방법]
- **교훈**: [재발 방지 또는 설계 원칙]
```
