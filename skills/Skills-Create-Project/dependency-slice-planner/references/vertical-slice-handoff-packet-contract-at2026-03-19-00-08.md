# Vertical Slice: handoff_packet_contract

## Goal

- canonical `handoff_packet.json` contract를 machine-readable artifact로 고정한다.

## Input

- canonical synthesis KB의 `Canonical Output Contract`
- minimal `handoff_packet.json` example

## Output

- `handoff_packet_contract` JSON/MD
- `handoff_packet_validation` JSON/MD

## Rules

- required fields는 `slice_id`, `root_dirs`, `files`, `entrypoints`, `allowed_paths`, `non_goals`, `upstream_artifacts`
- 모든 path-like collection은 `list[str]`이어야 한다
- packet은 launch instruction이 아니라 per-slice handoff artifact다
