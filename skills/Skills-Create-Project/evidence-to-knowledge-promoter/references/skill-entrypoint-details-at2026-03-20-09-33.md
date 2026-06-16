# Evidence To Knowledge Promoter Entrypoint Details

## Scripts

- `scripts/evidence_to_knowledge_promoter.py` — `build-promotion-summary`
- `scripts/evidence_to_knowledge_promoter.py` — `evaluate-promotion-trigger`
- `scripts/evidence_to_knowledge_promoter.py` — `build-hybrid-kb-patch-plan`
- `scripts/evidence_to_knowledge_promoter.py` — `evaluate-canonical-candidate`
- `scripts/evidence_to_knowledge_promoter.py` — `build-canonical-kb-patch-plan`
- `scripts/test_evidence_to_knowledge_promoter.py` — first-slice TDD

## Reference Map

- `knowledge_bases/evidence-to-knowledge-promoter-knowledge_base-at2026-03-17-02-48.md` — hybrid_kb + canonical takeaways
- `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-17-03-00.md` — 승격 규칙 정합성 판단 기준
- `references/evidence-promotion-handoff-at2026-03-17-08-57.md` — `support_audit + baseline_diff -> promotion summary` 입력 스키마
- `references/vertical-slice-promotion-summary-at2026-03-17-03-08.md` — 첫 promotion summary slice 정의
- `references/vertical-slice-promotion-trigger-evaluator-at2026-03-17-03-14.md` — 승격 판정 slice 정의
- `references/vertical-slice-hybrid-kb-patch-plan-at2026-03-17-03-20.md` — hybrid KB patch plan slice 정의
- `references/vertical-slice-canonical-candidate-evaluator-at2026-03-17-03-36.md` — canonical KB 후보 판정 slice 정의
- `references/vertical-slice-canonical-kb-patch-plan-at2026-03-17-09-03.md` — canonical KB patch plan slice 정의
- `references/troubleshooting.md` — 승격 실패/과승격 방지 메모

## Current Status

- 현재 단계는 `hybrid_kb`다.
- upstream handoff는 `references/evidence-promotion-handoff-at2026-03-17-08-57.md`의 payload mapping을 따른다.
- 현재는 `build-canonical-kb-patch-plan`까지 구현됐고, 실제 KB apply/mutation은 이 skill의 범위에서 제거했다.
