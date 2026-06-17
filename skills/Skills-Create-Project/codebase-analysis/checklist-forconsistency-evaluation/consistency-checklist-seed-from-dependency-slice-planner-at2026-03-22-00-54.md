# codebase-analysis slice stage 정합성 평가 체크리스트 seed

> 목적: `codebase-analysis`의 slice stage가 coarse tree split이 아니라 dependency-aware slice decision + handoff artifact producer 역할로 유지되는지 점검하기 위한 seed다.
> source of truth: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`의 `Problem Framing`, `Role Boundary`, `Canonical Input Signals`, `Recommended Slice Stage Sequence`, `Canonical Output Contract`

## A. Identity

- [ ] 이 skill의 핵심 목적이 `repository structure + dependency evidence -> parallel-safe slices + handoff artifacts`로 고정돼 있다
- [ ] 이 skill의 slice stage가 단순 디렉토리 분할기가 아니라 `tree-based seed + dependency-aware refinement` 구조로 정의돼 있다
- [ ] 이 skill의 직접 책임이 `slice decision + handoff artifact producer`로 고정돼 있다

## B. Boundary

- [ ] graph extraction은 `depsolve-analyzer` 같은 upstream extractor 책임으로 분리돼 있다
- [ ] final fan-out launch는 slice stage의 직접 책임이 아님이 명시돼 있다
- [ ] direct code edits와 destructive action은 기본 비목표로 분리돼 있다
- [ ] `context-links`는 task-local appendix이고 canonical KB보다 먼저 source of truth처럼 읽지 않는다

## C. Source Of Truth Order

- [ ] source of truth 순서가 `canonical synthesis KB -> consistency checklist -> implementation checklist -> scripts`로 고정돼 있다
- [ ] thin KB는 redirect note일 뿐 별도 source of truth가 아님이 명시돼 있다
- [ ] KB만 읽어도 slice stage input/output contract가 닫혀 있어야 한다는 self-contained rule이 유지된다

## D. Input Signals

- [ ] final slice 결정 전에 최소 required input으로 `directory tree`, `file count`, `total bytes`, `file extension buckets`, `manifest locations`, `static dependency overlay`를 본다고 명시돼 있다
- [ ] `known entrypoints`, `wrapper/path-mutation register`, `shared hub summary`, `cross-region edge summary`, `cycle/diamond/phantom anomaly ledger`가 strongly recommended signal로 분리돼 있다
- [ ] `tree`만으로 시작할 수는 있어도 `static dependency overlay` 없이 final slice를 확정하지 않는다고 명시돼 있다

## E. Slice Stage Sequence

- [ ] slice stage가 `inventory -> coarse slice seed -> static dependency overlay -> refinement -> runtime overlay -> stop rules -> final slice proposal` 순서로 고정돼 있다
- [ ] refinement가 `merge`와 `re-cut`을 모두 허용한다고 명시돼 있다
- [ ] refinement scoring 신호에 `size_score`, `internal_cohesion_score`, `cross_edge_ratio`, `shared_hub_penalty`, `runtime_condition_penalty`, `ownership_conflict_penalty`가 포함돼 있다

## F. Stop Rules

- [ ] `single large hub file`, `wrapper indirection`, `high cross-edge density`, `path-order/runtime condition dependence`, `coordination cost increase`가 stop rule로 고정돼 있다
- [ ] `analysis_only`와 `write_safe`를 구분한다고 명시돼 있다

## G. Output Contract

- [ ] global outputs에 `inventory_snapshot.json`, `slice_seed_candidates.json`, `static_dependency_overlay.json`, `slice_refinement_report.md`, `slice_manifest.json`, `parallel_slices.json`, `write_safe_slices.json` 또는 `analysis_only_slices.json`, `do_not_split_regions.json`이 포함돼 있다
- [ ] optional outputs에 `runtime_overlay.json`, `unobserved_path_register.json`이 분리돼 있다
- [ ] per-slice outputs에 `slices/<slice_id>/context-links.md`, `slices/<slice_id>/handoff_packet.json`이 포함돼 있다
- [ ] minimal `slice_manifest.json`과 minimal `handoff_packet.json` shape가 canonical contract로 고정돼 있다
