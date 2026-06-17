# dependency-slice-planner 정합성 실평가

- evaluated_at: `2026-03-20-00-53`
- checklist: [consistency-checklist-at2026-03-19-00-01.md](consistency-checklist-at2026-03-19-00-01.md)
- source of truth: [../knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md](../knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md)
- overall_status: `strong_partial`

## Verdict

현재 구현은 `identity`, `boundary`, `source of truth order`, `contract-first + planner algorithm v0.1`까지는 정합성이 높다.
반면 KB가 의도한 richer signal ingestion과 canonical global output naming은 아직 일부가 문서/계약 중심에 머물러 있다.

## A. Identity

- status: `pass`
- evidence:
  - [../SKILL.md](../SKILL.md)
  - [../knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md](../knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md)
- assessment:
  - skill 목적이 `repository structure + dependency evidence -> parallel-safe slices + handoff artifacts`로 고정돼 있다.
  - `slice decision + handoff artifact producer`라는 역할 경계도 entrypoint에 직접 올라와 있다.

## B. Boundary

- status: `pass`
- evidence:
  - [../SKILL.md](../SKILL.md)
  - [../references/skill-entrypoint-details-at2026-03-19-22-51.md](../references/skill-entrypoint-details-at2026-03-19-22-51.md)
  - [../knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md](../knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md)
- assessment:
  - graph extraction과 final launcher를 planner 책임에서 분리했다.
  - `context-links`를 task-local appendix로 낮추고 canonical KB를 우선 source of truth로 고정했다.
  - destructive action이 기본 비목표라는 점도 남아 있다.

## C. Source Of Truth Order

- status: `pass`
- evidence:
  - [../SKILL.md](../SKILL.md)
  - [implementation-checklist-at2026-03-19-00-01.md](../checklist-forimplementation/implementation-checklist-at2026-03-19-00-01.md)
  - [../knowledge_bases/dependency-slice-planner-knowledge_base-at2026-03-18-22-47.md](../knowledge_bases/dependency-slice-planner-knowledge_base-at2026-03-18-22-47.md)
- assessment:
  - canonical synthesis KB -> consistency checklist -> implementation checklist -> scripts 순서가 유지된다.
  - thin KB는 redirect note로 강등돼 있고, source of truth가 둘로 갈라지지 않는다.

## D. Input Signals

- status: `partial`
- evidence:
  - [../scripts/dependency_slice_planner.py](../scripts/dependency_slice_planner.py)
  - [../references/vertical-slice-inventory-path-index-materialization-at2026-03-19-21-13.md](../references/vertical-slice-inventory-path-index-materialization-at2026-03-19-21-13.md)
  - [../references/vertical-slice-wrapper-path-mutation-register-at2026-03-20-01-20.md](../references/vertical-slice-wrapper-path-mutation-register-at2026-03-20-01-20.md)
  - [../references/vertical-slice-unobserved-path-register-at2026-03-19-22-10.md](../references/vertical-slice-unobserved-path-register-at2026-03-19-22-10.md)
- assessment:
  - required input 계층인 `inventory_snapshot`, `slice_seed_candidates`, `static_dependency_overlay`, optional `runtime_overlay`, optional `inventory_path_index`는 구현돼 있다.
  - `total bytes`, `language buckets`, `entrypoints`, `unobserved_path_register` follow-up도 일부 반영됐다.
  - `wrapper/path-mutation register`도 독립 artifact family로 분리됐다.
  - 하지만 KB가 strongly recommended로 분리한 `shared hub summary`, `cross-region edge summary`, `cycle/diamond/phantom anomaly ledger`는 아직 독립 artifact로 닫히지 않았다.
- follow_up:
  - richer signal artifact를 `shared hub`와 `anomaly ledger` 위주로 더 분리하거나 upstream extractor bridge를 더 명시할 것

## E. Planner Algorithm

- status: `partial`
- evidence:
  - [../scripts/dependency_slice_planner.py](../scripts/dependency_slice_planner.py)
  - [../references/vertical-slice-seed-to-refinement-report-at2026-03-19-17-29.md](../references/vertical-slice-seed-to-refinement-report-at2026-03-19-17-29.md)
  - [../references/vertical-slice-stop-rule-evaluator-at2026-03-19-17-41.md](../references/vertical-slice-stop-rule-evaluator-at2026-03-19-17-41.md)
  - [../references/vertical-slice-final-slice-proposal-generator-at2026-03-19-17-49.md](../references/vertical-slice-final-slice-proposal-generator-at2026-03-19-17-49.md)
- assessment:
  - `inventory -> coarse slice seed -> static dependency overlay -> refinement -> runtime overlay -> stop rules -> final slice proposal` 순서의 뼈대는 구현돼 있다.
  - refinement scoring에 `size_score`, `internal_cohesion_score`, `cross_edge_ratio`, `shared_hub_penalty`, `runtime_condition_penalty`, `ownership_conflict_penalty`가 반영된다.
  - `merge_with_neighbor`와 `re_cut_with_dependency_overlay`도 recommendation으로 나온다.
  - 다만 KB가 암시하는 richer multilevel refinement나 upstream graph detail을 적극 소비하는 단계는 아직 v0.1 heuristic 수준이다.
- follow_up:
  - refinement input richness와 merge/re-cut target policy를 더 고도화할 것

## F. Stop Rules

- status: `pass`
- evidence:
  - [../scripts/dependency_slice_planner.py](../scripts/dependency_slice_planner.py)
  - [../references/vertical-slice-stop-rule-evaluator-at2026-03-19-17-41.md](../references/vertical-slice-stop-rule-evaluator-at2026-03-19-17-41.md)
- assessment:
  - `shared hub`, `cross-edge density`, `runtime condition`, `wrapper/path edge`, `coordination cost increase` 계열 stop signal이 구현돼 있다.
  - `write_safe`, `analysis_only`, `do_not_split` 분기도 실제 코드와 contract에 닫혀 있다.

## G. Output Contract

- status: `partial`
- evidence:
  - [../scripts/dependency_slice_planner.py](../scripts/dependency_slice_planner.py)
  - [../references/vertical-slice-inventory-path-index-materialization-at2026-03-19-21-13.md](../references/vertical-slice-inventory-path-index-materialization-at2026-03-19-21-13.md)
  - [../references/vertical-slice-inventory-path-index-language-metadata-join-at2026-03-19-21-54.md](../references/vertical-slice-inventory-path-index-language-metadata-join-at2026-03-19-21-54.md)
  - [../references/vertical-slice-unobserved-path-register-at2026-03-19-22-10.md](../references/vertical-slice-unobserved-path-register-at2026-03-19-22-10.md)
- assessment:
  - `slice_manifest`, `handoff_packet`, `parallel_slices`, `write_safe_slices`, `analysis_only_slices`, `do_not_split_regions`, optional `unobserved_path_register`는 구현돼 있다.
  - `inventory_path_index`를 넣으면 `files`, `entrypoints`, `language_buckets`, `total_bytes` materialization도 된다.
  - 다만 KB 문구 그대로의 global output naming 중 `slice_refinement_report.md`는 현재 machine-readable refinement artifact 중심이라 완전히 같은 표면은 아니다.
  - per-slice `slices/<slice_id>/...` 디렉토리 materialization은 아직 planner script가 직접 쓰지 않고 contract 수준에 머문다.
- follow_up:
  - canonical naming을 KB와 더 맞추거나, KB에서 machine-readable equivalent를 명시적으로 허용할 것

## H. Adapter Boundary

- status: `pass`
- evidence:
  - [../SKILL.md](../SKILL.md)
  - [../knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md](../knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md)
- assessment:
  - parser/extractor는 외부 adapter 후보로 두고, normalized graph schema / refinement / stop rules / handoff generation은 내부에 둔다는 경계가 유지된다.
  - 현재 구현도 외부 repo를 직접 끌어오지 않고 로컬 planner core를 유지한다.

## Next Follow-Ups

1. richer input signal artifact를 `wrapper/path-mutation`, `shared hub summary`, `anomaly ledger` 단위로 분리할지 결정한다.
   - `wrapper/path-mutation`은 구현됨
2. canonical output naming과 실제 output naming의 차이를 KB 또는 script 쪽 한곳에서 정리한다.
3. per-slice directory materialization이 필요하면 `slices/<slice_id>/context-links.md`, `handoff_packet.json` emit path를 실제 출력 단계까지 내린다.
