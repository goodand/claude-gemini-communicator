# kb-checklist-pipeline 정합성 평가 체크리스트

> 목적: canonical KB가 branch 규칙과 checklist 순서에 제대로 내려왔는지 점검한다.
> source of truth: `knowledge_bases/kb-checklist-pipeline-canonical-design-at2026-03-16-23-11.md`

## A. Pipeline Order

- [ ] `references -> knowledge_base -> consistency checklist -> implementation checklist` 순서가 고정돼 있다
- [ ] branch 결정이 implementation checklist 전에 이뤄진다
- [ ] source of truth가 canonical KB로 고정돼 있다

## B. Branch Separation

- [ ] `document_output`과 `implementation_output`이 구분돼 있다
- [ ] `script_output`이 `implementation_output`의 하위 특수 branch로 구분돼 있다
- [ ] branch별 후속 자료 읽기 순서가 다르다는 점이 문서화돼 있다

## C. TDD Guardrail

- [ ] `document_output`에는 TDD 필수 규칙을 강제하지 않는다
- [ ] `script_output`에는 TDD 선행 규칙이 있다
- [ ] `md/txt/image`가 아닌 구현물에도 TDD 또는 검증 파일 선행 규칙이 있다
- [ ] `script_output`과 `implementation_output`에는 smoke 이후 debug와 before/after diff 단계가 있다

## D. Progressive Context Injection

- [ ] router -> index -> family -> canonical KB -> checklists -> execution/evidence 순서가 보인다
- [ ] implementation branch에서는 execution/evidence 다음에 debug와 diff가 이어진다
- [ ] branch family 문서가 후속 자료 읽기 체인을 설명한다
- [ ] script branch에서 TDD 이후 evidence까지 이어지는 흐름이 있다

## E. Final Check

- [ ] 이 skill만 읽어도 branch별 다음 문서를 결정할 수 있다
- [ ] branch 혼동 없이 checklist를 생성할 수 있다
