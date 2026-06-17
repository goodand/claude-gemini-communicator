# python-static-diagnostic-fixer 정합성 평가 체크리스트

> 목적: 정적 진단 수정이 런타임 회귀보다 앞서지 않도록 순서를 고정한다.
> source of truth: `knowledge_bases/python-static-diagnostic-fixer-knowledge_base-at2026-03-17-01-18.md`의 `Canonical Design Takeaways`

## A. Order

- [ ] `py_compile` 또는 기존 테스트로 런타임 정상 여부를 먼저 확인한다
- [ ] 정적 진단 수정은 런타임 정상 확인 뒤에만 적용한다

## B. Safe Fix Taxonomy

- [ ] `unused_cleanup`, `optional_loader_guard`, `typing_support`를 우선 taxonomy로 둔다
- [ ] 큰 로직 재구성은 v0.1 비목표로 유지한다

## C. Behavior Guardrail

- [ ] 수정 목적이 정적 진단 감소인지, 기능 변경인지 구분한다
- [ ] 수정 후 다시 `py_compile`과 관련 테스트를 돌린다

## D. Evidence

- [ ] 진단 메시지 또는 줄 번호를 남길 수 있다
- [ ] 어떤 패턴으로 고쳤는지 기록할 수 있다
