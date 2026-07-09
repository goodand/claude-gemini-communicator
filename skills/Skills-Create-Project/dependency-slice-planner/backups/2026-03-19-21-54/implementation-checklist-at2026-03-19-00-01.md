# dependency-slice-planner 구현용 체크리스트

> 목적: canonical synthesis KB를 기준으로 `dependency-slice-planner`의 contract phase를 닫고, 그 다음 algorithm/refinement phase로 안전하게 내려간다.
> 선행조건: `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-19-00-01.md`

## A. Source Lock

- [ ] `knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md`를 단일 source of truth로 읽는다
- [ ] thin KB는 redirect note로만 취급한다
- [x] first implementation target은 planner 전체가 아니라 canonical output contract를 machine-readable shape로 내리는 것으로 고정한다

## B. First Vertical Slice

- [ ] 첫 vertical slice를 `slice_manifest_contract`로 고정한다
- [ ] `slice_manifest.json` minimal shape를 JSON schema 또는 validator contract로 먼저 고정한다
- [ ] `slice_count`, `slices[]`, `slice_id`, `root_dirs`, `files`, `entrypoints`, `classification`, `reason` 필드를 최소 required contract로 고정한다
- [ ] `classification`은 최소 `write_safe`와 `analysis_only`를 허용해야 한다

## C. Second Contract Slice

- [ ] 두 번째 slice를 `handoff_packet_contract`로 둔다
- [ ] `handoff_packet.json` minimal shape를 JSON schema 또는 validator contract로 고정한다
- [ ] `slice_id`, `root_dirs`, `files`, `entrypoints`, `allowed_paths`, `non_goals`, `upstream_artifacts`를 최소 required contract로 고정한다

## D. Script + TDD

- [ ] `scripts/`에 첫 contract script를 만든다
- [ ] 대응 TDD 파일을 먼저 만든다
- [ ] `--help`, exit code, stdout/stderr 계약을 먼저 고정한다
- [ ] 첫 script는 `emit-slice-manifest-contract` 또는 `validate-slice-manifest` 계열 중 하나로 시작한다

## E. Smoke + Evidence

- [ ] `slice_manifest` positive sample 1개와 invalid sample 1개를 만든다
- [ ] `handoff_packet` positive sample 1개와 invalid sample 1개를 만든다
- [ ] JSON artifact와 Markdown summary를 `references/`에 남긴다
- [ ] 실패 케이스가 생기면 `references/troubleshooting.md`에 누적한다

## F. Follow-up Slices

- [ ] `handoff_packet_contract` 다음에는 `inventory_snapshot_contract`를 고려한다
- [ ] 그 다음 `slice_seed_candidates_contract`, `static_dependency_overlay_contract`로 내려간다
- [ ] output contract가 닫힌 뒤에만 planner algorithm implementation으로 간다

## G. Algorithm Phase

- [x] 첫 algorithm slice는 `seed_to_refinement_report`로 둔다
- [x] 입력은 최소 `inventory_snapshot.json`, `slice_seed_candidates.json`, `static_dependency_overlay.json`을 받고 `runtime_overlay.json`은 optional overlay로 받는다
- [x] refinement는 `merge`와 `re-cut`을 둘 다 허용한다
- [x] scoring 신호는 최소 `size_score`, `internal_cohesion_score`, `cross_edge_ratio`, `shared_hub_penalty`, `runtime_condition_penalty`, `ownership_conflict_penalty`를 반영한다
- [x] 첫 algorithm 산출물은 `slice_refinement_report.md` 또는 동등한 machine-readable refinement artifact로 남긴다
- [x] 그 다음 `stop_rule_evaluator`로 내려간다
- [x] 그 다음 `final_slice_proposal_generator`로 내려간다

## H. Non-Goals

- [ ] 첫 구현에서 graph extractor 자체는 만들지 않는다
- [ ] 첫 구현에서 final fan-out launcher는 만들지 않는다
- [ ] 첫 구현에서 runtime overlay probe executor는 만들지 않는다

## I. Current Progress

- [x] `consistency checklist`를 canonical synthesis KB 기준으로 만들었다
- [x] `implementation checklist`를 만들고 첫 slice를 `slice_manifest_contract`로 고정했다
- [x] `emit-slice-manifest-contract`를 구현했다
- [x] `validate-slice-manifest`를 구현했다
- [x] `emit-handoff-packet-contract`를 구현했다
- [x] `validate-handoff-packet`를 구현했다
- [x] `emit-inventory-snapshot-contract`를 구현했다
- [x] `validate-inventory-snapshot`를 구현했다
- [x] `emit-slice-seed-candidates-contract`를 구현했다
- [x] `validate-slice-seed-candidates`를 구현했다
- [x] `emit-static-dependency-overlay-contract`를 구현했다
- [x] `validate-static-dependency-overlay`를 구현했다
- [x] `emit-runtime-overlay-contract`를 구현했다
- [x] `validate-runtime-overlay`를 구현했다
- [x] `runtime_overlay_contract`를 구현했다
- [x] contract phase는 `runtime_overlay_contract`까지 닫혔다
- [x] `emit-seed-refinement-report-contract`를 구현했다
- [x] `build-seed-refinement-report`를 구현했다
- [x] `seed_to_refinement_report` algorithm slice를 구현했다
- [x] `emit-stop-rule-evaluation-contract`를 구현했다
- [x] `evaluate-stop-rules`를 구현했다
- [x] `stop_rule_evaluator` algorithm slice를 구현했다
- [x] `emit-final-slice-proposal-contract`를 구현했다
- [x] `build-final-slice-proposal`를 구현했다
- [x] `final_slice_proposal_generator` algorithm slice를 구현했다
- [x] v0.1 planner algorithm phase는 `final_slice_proposal_generator`까지 닫혔다
