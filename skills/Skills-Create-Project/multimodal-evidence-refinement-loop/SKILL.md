---
name: multimodal-evidence-refinement-loop
description: >-
  Multimodal Interpretation family의 workflow owner. Use this skill when a
  multimodal agent must iteratively reinject image evidence, prior text
  judgment, and baseline context to improve understanding before closing state
  or deriving review artifacts. output normalization direct call은
  image-text-cot-review를 사용하라.
---

# Multimodal Evidence Refinement Loop

이미지를 증거로 읽고, 텍스트 판단을 정규화해 다시 이미지에 재주입하면서 이해도를 높이는 상위 loop owner.

## When to use

- one-shot caption보다 반복적 multimodal understanding loop가 필요할 때
- image evidence, text judgment, baseline, machine truth를 별도 층으로 유지해야 할 때
- 이전 pass의 판단과 현재 image reading을 다시 결합해 refinement해야 할 때
- semantic closure가 아직 불완전해 explicit pending state를 유지해야 할 때
- human review surface를 만들기 전에 machine-truth loop state를 먼저 닫아야 할 때

## Do not use

- human-facing markdown review card만 만들면 될 때
- machine-truth manifest shape만 정규화하면 될 때
- OCR extraction, component split, caption execution 자체가 현재 작업일 때
- 최종 approval promotion이나 metadata commit이 현재 작업일 때

## Family Roles

- owner:
  - `multimodal-evidence-refinement-loop`
- direct-call specialists:
  - `image-text-cot-review`

## Workflow

1. bounded item set과 현재 baseline anchor를 먼저 고정한다.
2. image evidence를 읽고 첫 text judgment를 만든다.
3. 현재 judgment와 필요한 context를 다시 image reading input에 재주입한다.
4. baseline과 이전 pass 대비 무엇이 유지되고 무엇이 바뀌었는지 분리해 기록한다.
5. closure가 충분하지 않으면 `pending` 상태와 unresolved 이유를 남기고 다음 refinement focus를 정한다.
6. closure가 충분하면 machine-truth loop state를 고정한다.
7. human-facing review surface와 stable manifest split이 필요하면 `image-text-cot-review`로 handoff한다.

## Canonical Loop Layers

- image evidence
- normalized text judgment
- baseline comparison anchor
- machine-truth manifest

## Canonical Outputs

- refinement-loop manifest
- per-item baseline comparison note
- explicit pending marker when semantic closure is incomplete
- handoff-ready normalized state for downstream review surface generation

## Not owned here

- final markdown review card layout
- output-only manifest field formatting
- OCR execution
- caption runner execution
- final approval or metadata mutation

## Ecosystem

- upstream evidence normalization이 먼저 필요하면 `evidence-trace-auditor`
- review surface와 machine-truth output split을 만들려면 `image-text-cot-review`
- claim-heavy assertion verification이 필요하면 `claim-verifier`
- loop 결과를 reusable KB insight로 올리려면 `evidence-to-knowledge-promoter`
- caption run execution은 `openai-image-caption-validation`
- component/OCR evidence export는 `component-split-ocr-review`
- OCR evidence extraction은 `macos-ocr-evidence`
- markdown review surface build는 `obsidian-caption-review-builder`

## References

- `references/runtime.md`
- `references/troubleshooting.md`
- `knowledge_bases/multimodal-evidence-refinement-loop-knowledge_base-at2026-04-01.md`
- `evals/evals.json`
