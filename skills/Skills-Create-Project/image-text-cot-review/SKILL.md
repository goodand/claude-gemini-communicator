---
name: image-text-cot-review
description: >-
  multimodal-evidence-refinement-loop family의 output-normalization specialist.
  Use this skill when outputs from a multimodal evidence refinement loop must
  be normalized into a human-facing review surface and a machine-truth manifest
  without collapsing comparison outcome, policy decision, pending state, or
  default-baseline status. loop owner는 multimodal-evidence-refinement-loop를
  사용하라.
---

# Image Text CoT Review

멀티모달 refinement loop의 결과를 human-facing review surface와 machine-truth manifest로 분리 정규화하는 skill.

## When to use

- 이미지 evidence와 텍스트 judgment의 review surface field split을 설계하거나 정규화할 때
- `multimodal-evidence-refinement-loop` 결과를 downstream review artifact로 정리할 때
- human-facing markdown와 machine-truth manifest를 같이 유지해야 할 때
- comparison outcome과 policy decision을 분리해야 할 때
- qualitative winner와 current default baseline을 분리해 기록해야 할 때
- 멀티모달 상태가 아직 닫히지 않아 explicit pending marker가 필요할 때

## Do not use

- OCR 추출이나 component split 자체가 현재 작업일 때
- 이미지 재주입, hypothesis refinement, baseline comparison loop 자체가 현재 작업일 때
- 이미지 caption generation이나 rerun execution이 현재 작업일 때
- 최종 rename/metadata commit이 현재 작업일 때
- 코드나 문서 claim을 repo evidence로 검증하는 일반 claim verification이 필요할 때

## Workflow

1. bounded input set을 먼저 고정한다.
2. image evidence와 text judgment를 별도 층으로 수집한다.
3. machine-truth manifest에 같은 item id로 정규화한다.
4. human-facing markdown review card는 manifest에서 파생한다.
5. comparison outcome, policy decision, review state를 별도 필드로 유지한다.
6. pending state가 남아 있으면 명시적으로 드러내고, winner/default promotion은 후속 gate로 넘긴다.

## Canonical Outputs

- human-facing markdown review surface
- machine-truth manifest
- explicit pending marker when closure is incomplete
- winner/default separation note when comparison exists

## Not owned here

- OCR execution
- object isolation
- caption generation or rerun execution
- final approval promotion
- file commit or metadata mutation

## Ecosystem

- upstream evidence normalization이 먼저 필요하면 `evidence-trace-auditor`
- iterative image reinjection과 understanding refinement 자체는 `multimodal-evidence-refinement-loop`
- claim-heavy assertion verification이 필요하면 `claim-verifier`
- review 결과를 reusable KB insight로 올리려면 `evidence-to-knowledge-promoter`
- markdown review surface build는 `obsidian-caption-review-builder`
- VS Code-native review workspace operation은 `vscode-fabriqa-foam-workflow`
- audit/consumer preparation은 `image-result-auditor`

## References

- `references/runtime.md`
- `references/troubleshooting.md`
- `knowledge_bases/image-text-cot-review-knowledge_base-at2026-04-01.md`
- `evals/evals.json`
