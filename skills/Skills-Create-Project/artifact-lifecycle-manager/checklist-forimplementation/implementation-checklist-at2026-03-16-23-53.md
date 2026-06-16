# artifact-lifecycle-manager 구현용 체크리스트

> 역할: lifecycle 규칙을 실제 audit script와 운용 절차로 내린다.
> source of truth: `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-23-53.md`

## A. Guard Script

- [ ] order audit subcommand를 만든다
- [ ] duplicate scan subcommand를 만든다
- [ ] combined audit subcommand를 만든다
- [ ] JSON payload로 결과를 출력한다

## B. Detection Rules

- [ ] minute-level timestamp 누락을 잡는다
- [ ] metadata order 위반을 잡는다
- [ ] active markdown duplicate hash group을 잡는다
- [ ] legacy 포함 여부를 옵션으로 분리한다

## C. TDD

- [ ] order success fixture를 만든다
- [ ] duplicate detection fixture를 만든다
- [ ] audit failure fixture를 만든다
