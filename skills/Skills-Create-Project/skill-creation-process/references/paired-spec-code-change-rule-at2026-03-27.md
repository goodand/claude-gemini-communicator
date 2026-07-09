# Paired Spec-Code Change Rule

- scope: SPEC(reference/registry)과 code(template/builder/test)가 동시에 바뀔 때의 양방향 재확인 규칙
- source: 2026-03-26~27 세션에서 한쪽만 고치고 다른 쪽을 놓치는 문제 반복

## 문제 정의

SPEC도 수정, 구현도 수정된 경우가 가장 위험하다.
- SPEC만 바뀌면: consumer 갱신 누락 → sync audit가 잡음
- code만 바뀌면: SPEC과 불일치 → sync audit가 잡음
- **둘 다 바뀌면**: 양쪽 다 "수정됨"이라 drift가 숨어버림

## 규칙

### SPEC → Code 방향
SPEC 변경이 code에 반영됐는가:
1. registry의 enum/field가 바뀌면 → builder constant, template $schema_notes, test assertion 갱신 확인
2. reference의 정책 문구가 바뀌면 → builder 동작, template 기본값 확인

### Code → SPEC 방향
code 변경이 SPEC/reference에 반영됐는가:
1. builder에 새 constant/로직이 추가되면 → registry, reference에 등록 확인
2. template에 새 필드가 추가되면 → registry fields에 등록 확인
3. test에 새 assertion이 추가되면 → 대응하는 규칙이 registry/reference에 있는지 확인

## 적용 시점

- Phase 4.2A (Contract Owner Map + Sync Audit)의 4번째 절차로 실행
- Phase 5로 넘어가기 전 필수 gate
- 단순 bugfix(SPEC 변경 없음)에는 불필요

## 검증 방법

1. `git diff --name-only`로 변경된 파일 목록 추출
2. reference/registry 파일과 template/builder/test 파일이 모두 포함되면 → paired-change
3. paired-change이면 양방향 재확인 필수
4. audit_contract_sync.py 실행으로 기계적 parity 확인
5. 정책 문구 drift 분기:
   - rule-bearing drift (enum/field/transition 규칙 문구) → doc-code-sync-checker 또는 sync audit
   - claim-heavy narrative drift (설계 주장, 비교 서술) → claim-verifier consistency claim

## 체크리스트

- [ ] SPEC 변경 목록 작성
- [ ] 각 SPEC 변경에 대응하는 code 변경 확인
- [ ] 각 code 변경에 대응하는 SPEC 반영 확인
- [ ] sync audit 실행 → all in_sync
- [ ] 정책 문구 변경 분기: rule-bearing → doc-code-sync-checker, claim-heavy → claim-verifier
