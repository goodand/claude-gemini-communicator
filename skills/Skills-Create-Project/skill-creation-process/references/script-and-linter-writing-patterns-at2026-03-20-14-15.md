# Script And Linter Writing Patterns

- scope: `workspace-artifact-production-process`에서 재사용 가능한 script 작성 규칙과 static/linter handling 노하우
- source notes: `phase-guide.md` 4-2, `practical-lessons.md`, `python-static-diagnostic-fixer`

## Script Writing Goals

- 반복 작업을 CLI로 묶는다.
- validator와 builder의 입력/출력을 안정화한다.
- 실행 결과를 추적 가능한 artifact로 남긴다.
- 사람이 아니라 agent가 읽기 좋은 `stdout/stderr/exit_code` 계약을 만든다.

## CLI Shape

- `--help`는 필수다.
- subcommand 구조를 선호한다.
- stdout은 결과 데이터만, stderr는 진행 상황과 경고만 보낸다.
- exit code 계약을 먼저 정하고 구현한다.
  - `0`: 성공
  - `0 + stderr`: 경고 포함 성공
  - `1`: 실패

## Script Implementation Heuristics

- `from __future__ import annotations`를 기본으로 둔다.
- `_load_text()`와 `_load_json()`를 분리해서 반환 타입을 섞지 않는다.
- 존재 확인은 범용 래퍼 대신 return code를 직접 본다.
- validation을 mutation보다 먼저 한다.
- 경로 검증은 `..`, 절대경로, symlink를 같이 본다.
- 문서에 규칙을 썼다면 validate에도 구현한다.

## Test And Runtime Gate

- script를 만들면 대응 TDD도 함께 만든다.
- 먼저 `py_compile`과 기존 테스트로 런타임이 정상인지 확인한다.
- smoke는 구현 결과를 실제 artifact로 남기는 최소 시나리오만 둔다.
- 정적 검증만으로 완료 선언하지 않는다.

## Linter And Static Diagnostic Rules

- static/linter 수습은 런타임 안정성 뒤에 온다.
- 먼저 runtime gate를 잠근다.
  - `py_compile`
  - 기존 테스트
  - 필요한 최소 smoke
- 그 다음에만 Pylance/Pyright/linter 수정으로 내려간다.

## Safe Static Fixes

- unused import / unused variable 제거
- `from __future__ import annotations` 추가
- type hint 보강
- `Optional` guard 추가
- loader/object가 `None`일 수 있는 경우 guard 추가

## Unsafe Static Fixes

- 런타임 경로를 바꾸는 대규모 refactor를 정적 진단 수습으로 포장
- 테스트 없이 import graph를 크게 바꾸기
- warning을 없애려고 의미 있는 분기나 side effect를 제거
- type checker를 만족시키려다 실제 동작을 가리는 no-op code 추가

## Practical Sequence

1. runtime이 깨졌는지 먼저 확인
2. static issue를 taxonomy로 분류
3. safe-fix만 먼저 적용
4. `py_compile`과 테스트 재실행
5. 남는 항목만 별도 follow-up으로 분리

## Validator Separation: Runtime vs Sync

validator를 하나로 합치면 "테스트 통과 = 정렬 완료"처럼 보이는 문제가 발생한다.
두 가지 validator를 분리한다.

### Runtime Validator
- **목적**: 실행 시점에 입력이 유효한지 확인
- **실행 시점**: builder, CLI, script 실행 시 자동
- **엄격도**: 호환성 유지 — unknown field 허용, deprecated field 경고
- **exit code**: 실패 시 1, 경고 시 0+stderr
- **예시**: `packet_builder.py validate`, `dispatch_manager.py validate`
- **규칙**: 기존 데이터가 깨지지 않도록 느슨하게 유지

### Sync Validator (Audit)
- **목적**: canonical registry와 consumer(template/builder/test)의 동기화 확인
- **실행 시점**: 수정 후 수동, CI에서 주기적
- **엄격도**: strict — unknown field 에러, enum mismatch 에러, 누락 필드 에러
- **exit code**: drift 발견 시 1
- **예시**: `audit_contract_sync.py`
- **규칙**: canonical registry를 source of truth로 삼고 consumer의 재정의를 거부

### 분리하지 않으면 생기는 문제:
1. runtime validator가 느슨해서 canonical에 없는 필드가 template에 들어가도 통과
2. "63 tests passed" → 정렬 완료로 착각 → 다음 라운드에서 drift 재발견
3. enum 정의가 registry와 template에서 다른데 둘 다 "valid"로 판정

### 도입 순서:
1. 먼저 machine registry를 만든다 (Phase 4.2A)
2. sync audit script를 만든다
3. runtime validator는 기존 것을 유지한다
4. 두 validator의 scope를 명시적으로 문서화한다

---

## When To Split

- script 설계 원칙은 이 문서에 둔다.
- 특정 tool의 개별 진단 taxonomy는 해당 skill KB나 troubleshooting으로 내린다.
- 공용 규칙이 반복되면 여기로 승격한다.
