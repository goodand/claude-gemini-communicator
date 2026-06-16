# KB Checklist Pipeline Canonical Design

- ver: `v0.1.0`
- generated_at: `2026-03-16-23-11`
- canonical_role: `KB -> checklist -> implementation branch를 고정하는 canonical KB`
- source_of_truth_for: `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-23-11.md`

## Canonical Design Takeaways

- 파이프라인의 기본 순서는 `references -> knowledge_base -> consistency checklist -> implementation checklist`다.
- branch 결정은 implementation checklist 작성 전에 끝낸다.
- `document_output` branch와 `implementation_output` branch를 섞지 않는다.
- `document_output`은 `md`, `txt`, `image` 산출물만 다룬다.
- `script_output`은 `implementation_output`의 하위 특수 branch다.
- `implementation_output`은 script와 기타 비문서 구현물을 포함한다.
- script 또는 비문서 구현물 branch에서는 TDD가 선행한다.
- script branch의 최소 순서는 `implementation checklist -> TDD file -> implementation -> smoke/evidence -> debug -> before/after diff`다.
- script/비문서 branch가 raw smoke report를 만들면 diff 전 `metrics` dict artifact로 먼저 정규화한다.
- 문서 branch는 TDD가 필수는 아니다.
- script/비문서 branch에서 debug는 optional note가 아니라 후속 단계다.
- 수정 효과를 증명해야 하면 before/after diff를 남긴다.
- progressive context injection은 `router -> branch index -> branch family -> canonical KB -> checklists -> execution/evidence`다.
- source of truth는 항상 canonical KB다.
- research 메모나 후보 아이디어는 branch source가 아니다.
- evidence는 troubleshooting과 smoke report로 다시 reference에 남긴다.

## Current Implementation Target

- 현재는 라우터형 skill과 branch routing script를 먼저 고정하는 단계다.
- branch routing은 `document_output`, `script_output`, `implementation_output` 세 가지를 지원한다.
- consistency checklist는 이 canonical KB를 기준으로 판정한다.
- implementation checklist는 branch별 후속 작업과 TDD 여부를 고정한다.
