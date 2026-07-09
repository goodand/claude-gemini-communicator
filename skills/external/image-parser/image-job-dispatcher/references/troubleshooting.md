# Troubleshooting

## CASE-001: Two workers write into the same ledger family

**Symptom**:
- two workers target the same ledger JSON or `_responses/` directory
- later aggregation cannot tell which rows belong to which worker

**Cause**:
- shard materialization or packet ownership drift

**Action**:
- stop the batch
- regenerate shards and issued packets
- confirm one shard JSONL, one ledger, and one `_responses/` directory per worker

## CASE-002: Worker text says success but MCP state does not

**Symptom**:
- the subagent says it completed
- task state or registry evidence does not show a finished row

**Cause**:
- free-form worker text was treated as truth

**Action**:
- trust MCP state and worker-owned artifacts only
- rerun or retry that row if the ledger is incomplete

## CASE-003: Parallel batch looks complete but overlap checks are weak

**Symptom**:
- all workers produced ledgers
- later review reveals duplicate `image_id` coverage or reused output paths

**Cause**:
- the dispatcher skipped shard overlap verification

**Action**:
- treat the batch as invalid until overlap is rechecked
- re-read the shard manifest and the issued task packets
- do not aggregate into shared review surfaces until the overlap check is explicit

## CASE-004: The current session thread cap prevents intended fanout

**Symptom**:
- the plan expects `10` workers
- the active Codex session only launches fewer workers at once

**Cause**:
- the live session inherited an older thread cap before the repo-local `.codex/config.toml` change

**Action**:
- record the actual wave behavior in feedback
- keep the packets and shard manifest unchanged
- restart the Codex session before claiming a true 10-way fanout run

## CASE-005: A worker edits shared docs instead of only owned shard surfaces

**Symptom**:
- a worker touches plans, registries, or shared markdown outputs
- merge review becomes ambiguous

**Cause**:
- packet scope was not explicit enough

**Action**:
- reissue the task packet with concrete owned paths
- keep shared summaries and registries under main-agent ownership only
