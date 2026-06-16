# evidence-to-knowledge-promoter 정합성 평가 체크리스트

> 목적: `evidence-to-knowledge-promoter`가 증거 공간의 결과를 재사용 가능한 insight KB 규칙으로 승격하는 기준을 올바르게 고정하는지 점검한다.
> source of truth: `knowledge_bases/evidence-to-knowledge-promoter-knowledge_base-at2026-03-17-02-48.md`의 `Canonical Design Takeaways`

## A. Identity

- [ ] 이 skill의 핵심 목적이 `evidence -> finding/delta -> lesson -> KB insight` 승격 규칙을 정하는 것으로 고정돼 있다
- [ ] 이 skill이 evidence 수집이 아니라 이미 수집된 evidence를 insight KB 규칙으로 승격하는 중간층으로 정의돼 있다

## B. Boundary

- [ ] evidence 수집/정규화는 `evidence-trace-auditor`의 선행 책임으로 분리돼 있다
- [ ] before/after delta 계산은 `baseline-diff-lab`의 선행 책임으로 분리돼 있다
- [ ] 이 skill이 code 수정 자동화나 raw evidence 생성 책임을 갖지 않는다고 명시돼 있다

## C. Source Of Truth Order

- [ ] source of truth 순서가 `Canonical Design Takeaways 또는 더 좁은 canonical KB -> consistency checklist -> implementation checklist -> scripts`로 고정돼 있다
- [ ] `evidence_ledger`, `support_audit`, `baseline diff`가 이 skill의 선행 입력이라고 명시돼 있다

## D. Promotion Unit Semantics

- [ ] 최소 promotion 단위가 `finding`, `delta`, `lesson`, `promotion_trigger`, `residual_uncertainty`로 고정돼 있다
- [ ] 단일 관측 사실은 우선 `finding`으로 남긴다고 명시돼 있다
- [ ] before/after diff가 있고 개선 방향이 수치로 닫히면 `delta`를 reusable insight로 올릴 수 있다고 명시돼 있다
- [ ] 반복 가능한 수정/해석 규칙만 `lesson`으로 승격한다고 명시돼 있다
- [ ] residual uncertainty가 남아 있으면 lesson이나 adoption rule로 승격하지 않는다고 명시돼 있다

## E. Promotion Trigger

- [ ] 같은 유형의 evidence가 2회 이상 반복되고 해석이 안정적일 때 `lesson` 후보로 승격할 수 있다고 명시돼 있다
- [ ] evidence provenance가 분명하고 raw artifact로 역추적 가능해야 `hybrid_kb` source of truth slice로 승격할 수 있다고 명시돼 있다
- [ ] `hybrid_kb`는 조사 자산과 canonical takeaways를 함께 유지하고, 반복 검증된 adoption rule만 `canonical_design_kb`로 분리한다고 명시돼 있다

## F. First Vertical Slice

- [ ] v0.1 첫 vertical slice가 `support_audit + baseline diff -> promotion candidate summary`로 고정돼 있다
- [ ] 첫 promotion 대상 분류가 `finding`, `delta`, `lesson`, `residual_uncertainty`라고 명시돼 있다
