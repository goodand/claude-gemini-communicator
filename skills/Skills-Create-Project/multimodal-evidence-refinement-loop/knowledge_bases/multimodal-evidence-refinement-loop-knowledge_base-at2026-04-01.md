# hybrid research Knowledge Base
- ver: `v0.1.0`
- generated_at: `2026-04-01`
- canonical_role: `multimodal-evidence-refinement-loop를 위한 hybrid_kb`
- canonical_slice: `Canonical Design Takeaways는 이 skill의 source of truth`
- source_research_files: `image-pipeline repeated task and repeated issue patterns generalized on 2026-04-01`
- generation_method: `repeated pattern extraction -> generic multimodal refinement-loop rule synthesis`

## Profile

- 이 skill은 이미지 증거와 텍스트 판단을 반복 재주입하며 이해도를 높이는 multimodal loop owner다.
- source recurrence는 실제 이미지 파이프라인에서 반복된 image-text drift, baseline confusion, pending leakage에서 나왔다.
- 핵심 질문은 `이미지 이해를 어떻게 반복적으로 정제하고, 어떤 시점에 machine truth로 고정할 것인가`다.

## Canonical Design Takeaways

- 이미지는 evidence layer다.
- 텍스트는 normalized judgment layer다.
- baseline은 comparison anchor layer다.
- manifest는 machine-truth layer다.
- one-shot caption이나 one-shot summary를 final understanding으로 취급하면 drift가 커진다.
- refinement loop는 현재 judgment를 다시 image evidence에 재주입해 delta를 확인해야 한다.
- closure가 충분하지 않으면 explicit pending marker를 유지해야 한다.
- review surface와 manifest split은 downstream 정규화 레이어인 `image-text-cot-review`가 맡는다.

## Repeated Source Patterns

- evidence to normalized review surface layering
- human-facing markdown versus machine-truth manifest split
- baseline-winner-default decision card repetition
- image evidence and text judgment drift apart
- comparison outcome and policy decision collapse into one field
- human reading order and machine schema order diverge
- ambiguous multimodal state hidden without explicit pending marker

## Current Implementation Target

- v0.1은 multimodal refinement loop rule과 layered state model을 canonicalize한다.
- output-only review surface generation은 하위 skill로 분리하고, 상위 loop owner를 먼저 고정하는 것이 첫 목표다.
- 후속 slice가 필요하면 loop-state manifest helper나 bounded reinjection runner contract로 내려갈 수 있다.
