# hybrid research Knowledge Base
- ver: `v0.1.0`
- generated_at: `2026-04-01`
- canonical_role: `image-text-cot-review를 위한 hybrid_kb`
- canonical_slice: `Canonical Design Takeaways는 이 skill의 source of truth`
- source_research_files: `image-pipeline repeated task and repeated issue patterns generalized on 2026-04-01`
- generation_method: `repeated pattern extraction -> generic review-surface rule synthesis`

## Profile

- 이 skill은 multimodal refinement loop 결과를 review artifact로 정규화하는 output-layer owner다.
- source recurrence는 실제 이미지 파이프라인에서 반복된 review-surface drift에서 나왔다.
- 핵심 질문은 `human-facing review`와 `machine-truth state`를 어떻게 함께 유지할 것인가다.

## Canonical Design Takeaways

- image evidence와 text judgment는 같은 카드에 보여도 machine field로는 분리해야 한다.
- human-facing markdown와 machine-truth manifest는 둘 다 필요하지만, source of truth는 manifest다.
- comparison outcome과 policy decision은 같은 field가 아니다.
- qualitative winner와 current default baseline은 같은 field가 아니다.
- multimodal closure가 끝나지 않았으면 explicit pending marker를 유지해야 한다.
- markdown reading order와 machine schema order는 다를 수 있으므로, markdown는 derived surface로 취급해야 한다.
- iterative reinjection/refinement 자체는 `multimodal-evidence-refinement-loop`가 소유하고, 이 skill은 review artifact structuring을 소유한다.

## Repeated Source Patterns

- evidence to normalized review surface layering
- human-facing markdown versus machine-truth manifest split
- baseline-winner-default decision card repetition
- image evidence and text judgment drift apart
- comparison outcome and policy decision collapse into one field
- human reading order and machine schema order diverge
- ambiguous multimodal state hidden without explicit pending marker

## Current Implementation Target

- v0.1은 workflow rule과 output split을 canonicalize한다.
- script나 schema generator 없이도 사람이 반복해서 같은 구조를 유지할 수 있게 만드는 것이 첫 목표다.
- 후속 slice가 필요하면 manifest schema helper나 review-card builder로 내려갈 수 있다.
