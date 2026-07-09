# evidence-to-knowledge-promoter 구현용 체크리스트

> 목적: 정합성 평가용 checklist를 기준으로 `evidence-to-knowledge-promoter`의 첫 구현 slice를 `support_audit + baseline diff -> promotion candidate summary`로 내린다.
> 선행조건: `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-17-03-00.md`

## A. Input Lock

- [ ] `knowledge_bases/evidence-to-knowledge-promoter-knowledge_base-at2026-03-17-02-48.md`의 `Canonical Design Takeaways`를 source of truth로 읽는다
- [ ] `evidence_ledger` 또는 `support_audit`를 첫 evidence 입력으로 고정한다
- [ ] `baseline-diff-lab`의 before/after diff artifact를 delta 입력으로 고정한다

## B. First Vertical Slice

- [ ] 첫 vertical slice를 `promotion candidate summary` 생성으로 고정한다
- [ ] 입력 evidence를 `finding`, `delta`, `lesson_candidate`, `residual_uncertainty`로 분류하는 최소 스키마를 고정한다
- [ ] output summary는 machine-readable JSON과 human-readable Markdown 둘 다 남긴다
- [ ] summary entry는 최소 `kind`, `name`, `source`, `value`, `evidence`, `promotion_decision`, `reason`을 가진다

## C. Promotion Rules

- [ ] 단일 관측 사실은 기본값으로 `finding`으로 남긴다
- [ ] before/after delta가 있는 경우 `delta` 후보를 우선 생성한다
- [ ] 동일 유형 evidence 반복과 provenance 안정성이 충족되면 `lesson_candidate`로 올린다
- [ ] residual uncertainty가 있으면 `promotion_decision=hold`로 남긴다

## D. Script + TDD

- [ ] `scripts/`에 첫 promoter script를 만든다
- [ ] 대응 TDD 파일을 먼저 고정한다
- [ ] `--help`, exit code, stdout/stderr 계약을 먼저 설계한다

## E. Smoke + Evidence

- [ ] 실제 `support_audit` 1개와 `baseline diff` 1개를 smoke input으로 고정한다
- [ ] promotion summary JSON/MD를 `references/`에 남긴다
- [ ] 승격 보류/과승격 케이스가 생기면 `references/troubleshooting.md`에 추가한다

## F. Follow-up Slices

- [ ] 두 번째 slice는 `promotion trigger evaluator`로 잡는다
- [ ] 세 번째 slice는 `lesson-to-hybrid-kb patch plan`으로 잡는다
- [ ] 반복 검증된 lesson만 `canonical_design_kb` 후보로 승격하는 후속 규칙을 별도 slice로 남긴다

## G. Current Progress

- [x] 첫 slice `promotion candidate summary`를 구현했다
- [x] 두 번째 slice `promotion trigger evaluator`를 구현했다
- [x] 세 번째 slice `lesson-to-hybrid-kb patch plan`을 구현했다
- [x] 네 번째 slice `apply-hybrid-kb-patch`를 구현했다
- [x] 다섯 번째 slice `canonical candidate evaluator`를 구현했다
- [x] 여섯 번째 slice `canonical_kb_patch_plan`을 구현했다
- [x] 일곱 번째 slice `apply-canonical-kb-patch`를 구현했다
