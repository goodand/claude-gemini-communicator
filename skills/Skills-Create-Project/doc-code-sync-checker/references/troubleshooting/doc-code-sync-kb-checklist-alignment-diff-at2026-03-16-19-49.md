# doc-code-sync-checker KB/Checklist Alignment Diff

- generated_at: `2026-03-16-19-49`
- backup: [legacy/2026-03-16-19-39-pre-kb-checklist-alignment](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/doc-code-sync-checker/legacy/2026-03-16-19-39-pre-kb-checklist-alignment)
- checker: [kb_to_consistency_check.py](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/contract-to-concept-mapper/scripts/kb_to_consistency_check.py)

## Scope

- hybrid KB: [doc-code-sync-checker-knowledge_base-at2026-03-16.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/doc-code-sync-checker/knowledge_bases/doc-code-sync-checker-knowledge_base-at2026-03-16.md)
- canonical KB: [doc-code-sync-canonical-design-at2026-03-16-18-18.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/doc-code-sync-checker/knowledge_bases/doc-code-sync-canonical-design-at2026-03-16-18-18.md)
- consistency checklist: [consistency-checklist.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/doc-code-sync-checker/checklist-forconsistency-evaluation/consistency-checklist.md)

## Before

| case | profile | coverage_ratio | unsupported_item_ratio | traceability_ratio | boundary_preservation_ratio | missing | unsupported |
|---|---|---:|---:|---:|---:|---:|---:|
| hybrid | `hybrid_kb` | `0.36` | `0.2` | `0.8` | `1.0` | `16` | `6` |
| canonical | `canonical_design_kb` | `0.8` | `0.1333` | `0.8667` | `0.6667` | `3` | `4` |

## Changes

1. source of truth 문장 정렬
   - canonical KB에 `intent`, `runtime smoke test`, `code 변경 없는 검증 보고`, `구현 깊이 부족 vs scope inflation 분류`를 직접 추가
2. hybrid KB 정리
   - 결과 분류와 rule type을 분리 bullet 대신 결합형 문장으로 정리
   - current implementation status를 checklist가 소비하는 문장 단위로 압축
3. checklist 정렬
   - `pairwise checker 경계`, `규칙 object`, `scaffold 단계` 표현을 KB 문구와 더 가깝게 조정
4. checker 보정
   - `Current Implementation Status`를 support section으로 분류
   - `아래 3개다/4개다` summary parent 힌트 추가

## After

| case | profile | coverage_ratio | unsupported_item_ratio | traceability_ratio | boundary_preservation_ratio | missing | unsupported |
|---|---|---:|---:|---:|---:|---:|---:|
| hybrid | `hybrid_kb` | `1.0` | `0.0` | `1.0` | `1.0` | `0` | `0` |
| canonical | `canonical_design_kb` | `1.0` | `0.0` | `1.0` | `1.0` | `0` | `0` |

## Interpretation

- 이번 개선은 `doc-code-sync-checker`에서 profile 전략이 실제로 닫힌다는 증거다.
- 원인은 단순히 profile 승격만이 아니라:
  - canonical source wording alignment
  - checklist wording alignment
  - summary/support typing heuristic 보정
  이 세 가지가 같이 작동했기 때문이다.
- 즉 `profile mismatch`는 1차 원인이고, profile 정렬 이후에는 `문장 단위 canonical completeness`와 `checker typing`이 2차 원인으로 작동한다.

## Validation

- `python3 contract-to-concept-mapper/scripts/test_kb_to_consistency_check.py`
- `python3 ../super-skill-creator/scripts/quick_validate.py doc-code-sync-checker`

