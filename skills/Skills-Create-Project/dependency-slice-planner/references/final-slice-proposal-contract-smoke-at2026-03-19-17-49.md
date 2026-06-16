# dependency-slice-planner final_slice_proposal contract

- generated_at: `2026-03-19T17:50:10+09:00`
- contract_family: `final_slice_proposal_contract`
- version: `v0.1.0`

## Required Top-Level Fields

- `status`
- `generated_at`
- `algorithm_family`
- `version`
- `input_artifacts`
- `parallel_slice_count`
- `write_safe_slice_count`
- `analysis_only_slice_count`
- `do_not_split_count`
- `parallel_slices`
- `write_safe_slices`
- `analysis_only_slices`
- `do_not_split_regions`
- `slice_manifest`
- `handoff_packet_count`
- `handoff_packets`
- `next_candidate`

## Slice Required Fields

- `slice_id`
- `root_dirs`
- `files`
- `entrypoints`
- `classification`
- `source_candidate_id`
- `reason`

## Do-Not-Split Required Fields

- `candidate_id`
- `root_dir`
- `triggered_stop_rules`
- `reason`
