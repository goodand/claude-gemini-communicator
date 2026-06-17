---
name: dependency-slice-planner
description: >-
  design-planning-orchestrator family의 dependency-based slice planning
  specialist. Use this skill when repository structure and dependency-graph
  evidence must be turned into parallel-safe slices, write-safe boundaries,
  and handoff artifacts for downstream agents. broader multi-concern planning은
  design-planning-orchestrator를 사용하라.
---

# Dependency Slice Planner

repository tree와 dependency evidence를 이용해 `analysis_only` 또는 `write_safe` slice를 계획하는 skill.

## When to use

- coarse tree split만으로는 안전한 병렬 경계를 정하기 어려울 때
- dependency graph, wrapper, manifest crossing을 반영해 slice를 다시 잘라야 할 때
- `slice_manifest.json`과 per-slice handoff artifact를 만들고 싶을 때

## Workflow

1. source of truth는 [knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md](knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md) 하나로 고정한다.
2. KB의 `Role Boundary`, `Canonical Input Signals`, `Recommended Planner Algorithm`, `Canonical Output Contract`, `Canonical Design Takeaways`를 먼저 읽는다.
3. capability 제한은 [references/tool-capability-policy-at2026-03-18-22-47.md](references/tool-capability-policy-at2026-03-18-22-47.md)에서 확인한다.
4. 실제 task-local graph artifact가 있으면 [bridges/dependency-slice-planner-handoff-contract-at2026-03-18-22-47.md](bridges/dependency-slice-planner-handoff-contract-at2026-03-18-22-47.md)와 [references/context-links-at2026-03-18-22-47.md](references/context-links-at2026-03-18-22-47.md)를 읽고 입력 범위를 닫는다.
5. runtime evidence가 있으면 `runtime_overlay.json`을 검증하고 필요 시 `unobserved_path_register.json`을 먼저 만든다.
6. 출력은 KB의 canonical contract에 맞춰 `slice_manifest.json`, `parallel_slices.json`, `write_safe_slices.json` 또는 `analysis_only_slices.json`, `do_not_split_regions.json`, per-slice `context-links.md`, `handoff_packet.json`으로 정리한다.

## References

- [knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md](knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md) — canonical synthesis KB
- [checklist-forconsistency-evaluation/consistency-checklist-at2026-03-19-00-01.md](checklist-forconsistency-evaluation/consistency-checklist-at2026-03-19-00-01.md) — planner identity, boundary, input/output contract 정합성 기준
- [checklist-forimplementation/implementation-checklist-at2026-03-19-00-01.md](checklist-forimplementation/implementation-checklist-at2026-03-19-00-01.md) — 구현 진행과 follow-up slice 기준
- [bridges/dependency-slice-planner-handoff-contract-at2026-03-18-22-47.md](bridges/dependency-slice-planner-handoff-contract-at2026-03-18-22-47.md) — planner input/output handoff contract
- [references/skill-entrypoint-details-at2026-03-19-22-51.md](references/skill-entrypoint-details-at2026-03-19-22-51.md) — scripts, slice notes, troubleshooting, extended references

## Notes

- 이 skill은 extractor나 final launcher가 아니라 `slice decision + handoff artifact producer`다.
- detailed notes는 [references/skill-entrypoint-details-at2026-03-19-22-51.md](references/skill-entrypoint-details-at2026-03-19-22-51.md)에 둔다.
