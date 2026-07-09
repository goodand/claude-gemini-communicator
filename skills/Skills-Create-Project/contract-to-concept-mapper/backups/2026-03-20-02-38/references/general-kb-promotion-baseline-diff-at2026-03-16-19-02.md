# General KB Promotion Baseline Diff

- date: `2026-03-16-19-02`
- target KB: [contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md](../knowledge_bases/contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md)
- checklist: [consistency-checklist-at2026-03-16-14-03.md](../checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-14-03.md)
- before: [general-kb-baseline-measure-at2026-03-16-18-55.md](./general-kb-baseline-measure-at2026-03-16-18-55.md)
- after: [general-kb-hybrid-final-at2026-03-16-18-59.md](./general-kb-hybrid-final-at2026-03-16-18-59.md)

## Summary

`research_index_kb`였던 일반 KB에 `Canonical Design Takeaways`와 measurement alignment를 추가해 `hybrid_kb`로 승격한 뒤,
같은 checklist 기준으로 baseline을 재측정했다.

핵심 변화는 `reference inventory 중심 KB`에서 `direct-compare 가능한 canonical slice 포함 KB`로 바뀌었다는 점이다.

## Metric Diff

| metric | before | after | interpretation |
|---|---:|---:|---|
| `coverage_ratio` | `n/a` | `1.0` | canonical unit이 생겨 해석 가능해졌고, checklist와 전부 매핑됨 |
| `unsupported_item_ratio` | `0.3` | `0.0` | KB 근거가 없던 checklist item이 canonical slice 보강으로 해소됨 |
| `traceability_ratio` | `0.7` | `1.0` | checklist item 전부가 KB 근거를 갖게 됨 |
| `boundary_preservation_ratio` | `1.0` | `1.0` | guardrail 보존 상태는 승격 전후 유지됨 |

## Artifact/Profile Diff

| 항목 | before | after |
|---|---|---|
| `kb_profile` | `research_index_kb` | `hybrid_kb` |
| canonical unit 수 | `0` | `16` |
| covered checklist item 수 | `21` | `30` |
| unsupported checklist item 수 | `9` | `0` |
| warnings | `coverage_ratio 해석 불가`, `canonical KB 먼저 필요` | 없음 |

## Why The Metrics Changed

1. broad research note에 있던 의미를 `Canonical Design Takeaways`로 올렸다.
2. comparison target이 문서 전체가 아니라 canonical slice가 되었다.
3. metric interpretation layer를 broad reference inventory와 분리했다.
4. 책임 경계 문장과 scaffold/current-stage 문장을 canonical layer에 포함했다.

## What This Proves

- baseline 개선의 핵심은 semantic matcher 강화보다 `KB profile 정렬`이었다.
- `research/index KB -> canonical/hybrid KB -> consistency checklist` 순서가 실제로 유효하다.
- 같은 checker라도 source artifact profile이 맞지 않으면 metric이 왜곡될 수 있다.

## Metric Metadata Summary

- fixed point: [kb-to-consistency-metric-formula-contract-at2026-03-16-19-02.md](../knowledge_bases/kb-to-consistency-metric-formula-contract-at2026-03-16-19-02.md)
- `coverage_ratio`
  - class: `proxy-profile`
  - formula: `matched_canonical_kb_units / total_canonical_kb_units`
  - note: canonical unit이 없으면 `n/a`
- `unsupported_item_ratio`
  - class: `project-custom`
  - formula: `unsupported_checklist_items / total_checklist_items`
- `traceability_ratio`
  - class: `proxy-profile`
  - note: strict proof가 아니라 heuristic mapping 존재 기준
- `boundary_preservation_ratio`
  - class: `proxy-profile`
  - note: heuristic guardrail unit 기준

## Next Use

- 다른 skill에서도 broad KB가 checklist source of truth가 되려면 먼저 canonical slice를 추가한다.
- 현재 4개 metric의 이름/수식/strict-vs-proxy 해석은 local contract 문서에서 고정한다.
