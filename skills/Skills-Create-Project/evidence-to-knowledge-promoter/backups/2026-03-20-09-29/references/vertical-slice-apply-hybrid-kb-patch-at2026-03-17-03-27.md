# Vertical Slice: apply-hybrid-kb-patch

## Purpose

`hybrid_kb_patch_plan`을 실제 KB copy에 적용해, 승격 규칙이 문서 패치까지 이어지는지 확인한다.

## Input

- `hybrid_kb_patch_plan`
- target `hybrid_kb`

## Output

- patched KB copy
- machine-readable `hybrid_kb_patch_apply_result`
- human-readable Markdown apply summary

## Current Rule

- source KB 원본은 직접 덮어쓰지 않는다
- `output-kb` copy에만 patch를 적용한다
- `patch_decision = hold`면 문서 변경 없이 hold result만 남긴다
- `patch_decision = promote`면
  - `lesson_candidate`는 `Canonical Design Takeaways`
  - candidate `delta`는 `Current Implementation Target`
  - `finding`은 `Research Focus`
  섹션으로 append 한다

## Smoke Artifacts

- Hold case:
  - [hybrid-kb-patch-apply-hold-smoke-at2026-03-17-03-27.json](./hybrid-kb-patch-apply-hold-smoke-at2026-03-17-03-27.json)
  - [evidence-to-knowledge-promoter-hybrid-kb-hold-copy-at2026-03-17-03-27.md](./evidence-to-knowledge-promoter-hybrid-kb-hold-copy-at2026-03-17-03-27.md)
- Promote case:
  - [hybrid-kb-patch-apply-positive-smoke-at2026-03-17-03-27.json](./hybrid-kb-patch-apply-positive-smoke-at2026-03-17-03-27.json)
  - [evidence-to-knowledge-promoter-hybrid-kb-patched-copy-at2026-03-17-03-27.md](./evidence-to-knowledge-promoter-hybrid-kb-patched-copy-at2026-03-17-03-27.md)
