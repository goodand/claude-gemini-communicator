# Dependency Slice Planner Entrypoint Details

`dependency-slice-planner` entrypoint에서 분리한 상세 자료.

## Scripts

- [scripts/dependency_slice_planner.py](../scripts/dependency_slice_planner.py) — `slice_manifest`, `handoff_packet`, `inventory_snapshot`, `slice_seed_candidates`, `static_dependency_overlay`, `runtime_overlay`, `wrapper_path_mutation_register`, `unobserved_path_register`, `inventory_path_index` contract emit/validate + `seed_to_refinement_report`, `stop_rule_evaluator`, `final_slice_proposal_generator`
- [scripts/test_dependency_slice_planner.py](../scripts/test_dependency_slice_planner.py) — contract slice TDD

## Extended References

- [../knowledge_bases/dependency-slice-planner-knowledge_base-at2026-03-18-22-47.md](../knowledge_bases/dependency-slice-planner-knowledge_base-at2026-03-18-22-47.md) — merged redirect note
- [vertical-slice-static-dependency-overlay-contract-at2026-03-19-14-14.md](vertical-slice-static-dependency-overlay-contract-at2026-03-19-14-14.md) — static dependency overlay contract slice
- [vertical-slice-runtime-overlay-contract-at2026-03-19-14-14.md](vertical-slice-runtime-overlay-contract-at2026-03-19-14-14.md) — runtime overlay contract slice
- [vertical-slice-wrapper-path-mutation-register-at2026-03-20-01-20.md](vertical-slice-wrapper-path-mutation-register-at2026-03-20-01-20.md) — wrapper/path-mutation signal artifact slice
- [vertical-slice-unobserved-path-register-at2026-03-19-22-10.md](vertical-slice-unobserved-path-register-at2026-03-19-22-10.md) — runtime follow-up artifact slice
- [vertical-slice-inventory-path-index-language-metadata-join-at2026-03-19-21-54.md](vertical-slice-inventory-path-index-language-metadata-join-at2026-03-19-21-54.md) — per-slice language bucket and byte-count materialization
- [canonical-output-naming-alignment-at2026-03-20-00-53.md](canonical-output-naming-alignment-at2026-03-20-00-53.md) — KB canonical naming과 current implementation output family 매핑
- [tool-capability-policy-at2026-03-18-22-47.md](tool-capability-policy-at2026-03-18-22-47.md) — allowed/disallowed capability
- [context-links-at2026-03-18-22-47.md](context-links-at2026-03-18-22-47.md) — task-local artifact links
- [troubleshooting.md](troubleshooting.md) — 반복 실패와 형식 주의사항

## Notes

- 이 skill은 extractor나 final launcher가 아니라 `slice decision + handoff artifact producer`다.
- tree/size/depth는 coarse seed일 뿐이고, final slice는 static dependency refinement와 stop rule을 거쳐야 한다.
- runtime overlay가 있으면 `unobserved_path_register`를 follow-up artifact로 별도 분리할 수 있다.
- wrapper/path-mutation evidence는 `wrapper_path_mutation_register`로 먼저 정규화한 뒤 static overlay에 반영할 수 있다.
- `context-links`는 task-local appendix다. source of truth는 canonical KB다.
- direct code edits나 destructive action은 기본 비목표다.
