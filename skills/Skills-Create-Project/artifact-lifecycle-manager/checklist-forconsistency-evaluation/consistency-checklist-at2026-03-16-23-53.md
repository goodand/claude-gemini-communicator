# artifact-lifecycle-manager 정합성 평가 체크리스트

> 목적: artifact lifecycle 규칙이 naming, order, duplicate cleanup까지 일관되게 정의됐는지 점검한다.
> source of truth: `knowledge_bases/artifact-lifecycle-manager-canonical-design-at2026-03-16-23-53.md`

## A. Naming

- [ ] active artifact naming이 `*-atYYYY-MM-DD-HH-MM.md`로 정의돼 있다
- [ ] timestamp naming과 metadata order의 관계가 분리돼 있다

## B. Order

- [ ] 기본 chain이 `knowledge_base -> consistency checklist -> implementation checklist`로 고정돼 있다
- [ ] 순서 판정에 metadata를 우선 사용한다

## C. Lifecycle Decision

- [ ] destructive 변경 전에만 legacy backup을 만든다
- [ ] same-content duplicate는 active cleanup 대상으로 정의돼 있다
- [ ] order와 duplicate를 script로 검증할 수 있다
