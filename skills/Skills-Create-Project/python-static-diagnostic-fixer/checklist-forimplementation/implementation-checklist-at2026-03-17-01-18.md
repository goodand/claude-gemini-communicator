# python-static-diagnostic-fixer 구현용 체크리스트

> 목적: 반복된 Pylance/linter 정리 패턴을 안전한 작업 순서로 내린다.
> 선행조건: `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-17-01-18.md`

## A. Diagnose

- [ ] 먼저 진단 메시지, 파일 경로, 줄 번호를 기록한다
- [ ] `py_compile`과 기존 테스트로 런타임 정상 여부를 확인한다

## B. Safe Fix Order

- [ ] `unused import` 제거 또는 정리
- [ ] `unused variable` 제거 또는 `_`로 명시
- [ ] 동적 import 계열이면 `spec.loader is None` 같은 optional guard 추가
- [ ] 필요하면 `ModuleType`, return annotation, `from __future__ import annotations` 같은 typing 보강

## C. Verification

- [ ] 수정 후 다시 `py_compile` 실행
- [ ] 관련 테스트 재실행
- [ ] 에디터 진단이 줄었는지 확인

## D. Follow-up

- [ ] 반복 패턴이면 `references/troubleshooting.md`에 케이스를 남긴다
- [ ] 빈도가 높아지면 보조 script 후보로 올린다
