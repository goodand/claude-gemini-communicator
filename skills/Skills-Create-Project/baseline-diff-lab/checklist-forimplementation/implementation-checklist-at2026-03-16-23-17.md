# baseline-diff-lab 구현용 체크리스트

> 역할: baseline diff 실험을 실제 artifact 단위로 내린다.
> source of truth: `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-23-17.md`

## A. Inputs

- [ ] planner script로 handoff 입력을 먼저 정리한다
- [ ] pre-fix baseline artifact를 만든다
- [ ] debug evidence를 저장한다
- [ ] post-fix baseline artifact를 만든다
- [ ] upstream이 raw smoke report만 만들면 metricize script로 `metrics` dict artifact를 먼저 만든다

## B. Outputs

- [ ] compute script로 같은 metric set의 before/after delta를 계산한다
- [ ] before/after diff JSON을 만든다
- [ ] before/after diff MD를 만든다
- [ ] reduction metric을 계산한다

## C. Handoff

- [ ] upstream skill이 baseline-diff-lab로 handoff하는 bridge를 남긴다
- [ ] bridge에서 metric set과 artifact 경로를 넘긴다
- [ ] planner output이 diff artifact 이름과 다음 액션을 제안한다
