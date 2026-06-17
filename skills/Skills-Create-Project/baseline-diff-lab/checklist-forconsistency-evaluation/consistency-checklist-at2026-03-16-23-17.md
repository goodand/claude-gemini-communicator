# baseline-diff-lab 정합성 평가 체크리스트

> 목적: baseline diff 단계가 pre/post artifact와 diff report를 같은 계약으로 다루는지 점검한다.
> source of truth: `knowledge_bases/baseline-diff-lab-canonical-design-at2026-03-16-23-17.md`

## A. Order

- [ ] `pre-fix -> debug -> post-fix -> diff` 순서가 고정돼 있다
- [ ] pre-fix artifact 없이 diff 단계로 건너뛰지 않는다

## B. Artifact Contract

- [ ] pre-fix와 post-fix가 같은 metric set을 쓴다
- [ ] raw smoke report는 diff 전에 `metrics` dict artifact로 정규화할 수 있다
- [ ] JSON artifact와 MD report가 함께 남는다
- [ ] delta와 reduction metric이 함께 남는다

## C. Handoff

- [ ] 다른 skill의 implementation branch 후속 단계로 handoff 가능하다
- [ ] bridge 문서에서 baseline-diff-lab로 넘어가는 타이밍이 명시돼 있다
