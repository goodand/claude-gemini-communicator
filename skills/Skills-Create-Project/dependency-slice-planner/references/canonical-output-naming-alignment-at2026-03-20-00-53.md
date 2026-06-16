# dependency-slice-planner canonical output naming alignment

- created_at: `2026-03-20-00-53`
- purpose: KB의 canonical output naming과 현재 script implementation의 output family를 한 곳에서 매핑

## Alignment Table

| KB canonical name | Current implementation family | Status | Notes |
|---|---|---|---|
| `inventory_snapshot.json` | `inventory_snapshot` contract + validation + input artifact | aligned | canonical name 그대로 유지 |
| `slice_seed_candidates.json` | `slice_seed_candidates` contract + validation + input artifact | aligned | canonical name 그대로 유지 |
| `static_dependency_overlay.json` | `static_dependency_overlay` contract + validation + input artifact | aligned | canonical name 그대로 유지 |
| `slice_refinement_report.md` | `seed_refinement_report` algorithm output | machine-readable equivalent | 구현은 JSON 중심이고 command에서 markdown summary도 함께 남길 수 있다 |
| `runtime_overlay.json` | `runtime_overlay` contract + validation + input artifact | aligned | canonical name 그대로 유지 |
| `unobserved_path_register.json` | `unobserved_path_register` contract + validation + build output | aligned | canonical optional output |
| `slice_manifest.json` | `slice_manifest` contract + final proposal embedded `slice_manifest` | aligned | canonical name 그대로 유지 |
| `parallel_slices.json` | final proposal embedded `parallel_slices` | aligned | 현재는 final proposal payload 내부 family |
| `write_safe_slices.json` | final proposal embedded `write_safe_slices` | aligned | 현재는 final proposal payload 내부 family |
| `analysis_only_slices.json` | final proposal embedded `analysis_only_slices` | aligned | 현재는 final proposal payload 내부 family |
| `do_not_split_regions.json` | final proposal embedded `do_not_split_regions` | aligned | 현재는 final proposal payload 내부 family |
| `slices/<slice_id>/context-links.md` | not materialized by planner script | pending | task-local appendix는 upstream/upper agent materialization 영역으로 남아 있다 |
| `slices/<slice_id>/handoff_packet.json` | final proposal embedded `handoff_packets[]` | partially aligned | semantic shape는 맞지만 per-slice path emit은 아직 직접 쓰지 않는다 |

## Interpretation Rule

- KB 이름이 `.json` 또는 `.md`로 적혀 있어도, 현재 구현에서는 일부 산출물이 `final proposal payload` 내부 field family로 먼저 닫혀 있다.
- `slice_refinement_report.md`는 현재 `seed_refinement_report` JSON이 canonical machine-readable equivalent이고, optional markdown summary를 함께 남기는 것으로 해석한다.
- per-slice path materialization은 planner core의 필수 책임이 아니라 upper layer가 file emission을 결정하는 단계로 남겨둔다.

## Follow-Up Boundary

- output family semantic이 이미 맞는 경우:
  - script output key를 유지하고 이 문서를 naming bridge로 사용
- 실제 file materialization이 필요한 경우:
  - `emit-final-slice-proposal-files` 같은 follow-up command를 별도 slice로 추가
- KB wording을 구현 쪽으로 더 맞추고 싶다면:
  - `slice_refinement_report.md` 항목에 `or equivalent machine-readable artifact`를 명시
