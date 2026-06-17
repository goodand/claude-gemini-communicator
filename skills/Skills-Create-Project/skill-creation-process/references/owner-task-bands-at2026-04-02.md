# Owner Task Bands

- generated_at: `2026-04-02`
- scope: `top-level skill routing / owner-specialist taxonomy / YAML description`

## Purpose

top-level skill들의 공통 Task를 owner band 기준으로 고정한다.  
이 문서는 body보다 먼저 읽히는 YAML `description` 라우팅을 정렬하기 위한 canonical reference다.

## Owner Bands

### 1. Verification / Consistency Decision

- owner: `verification-decision-gate`
- owner verbs:
  - `verify`
  - `judge`
  - `gate`
  - `route`
- direct-call specialists:
  - `claim-verifier`
  - `doc-code-sync-checker`
  - `codebase-doc-alignment`
  - `skill-workflow-bridge-eval`
  - `evidence-trace-auditor`
  - `cross-repo-product-review`
  - `async-migration-verify`
- use owner when:
  - claim/rule/alignment/workflow judgment와 execution evidence audit가 함께 얽힌 multi-concern verification이 필요할 때
- direct-call specialist notes:
  - `cross-repo-product-review`: 외부 repo milestone quality review + bounded Codex handoff + convergence closure. Band 3/Band 2 보조 인접성.
  - `async-migration-verify`: sync→async 전환 구조적 closure 검증 (6-checkpoint). 순수 Band 1.

### 2. Artifact Production / Validation / Promotion

- owner: `workspace-artifact-production-process`
- owner verbs:
  - `produce`
  - `sequence`
  - `validate`
  - `promote`
- direct-call specialists:
  - `kb-checklist-pipeline`
  - `slice-experiment-lab`
  - `evidence-to-knowledge-promoter`
  - `edge-case-generator`
- use owner when:
  - reusable artifact set을 production order로 닫아야 할 때

### 3. Delegation / Orchestration

- owner: `worktree-parallel`
- owner verbs:
  - `orchestrate`
  - `coordinate`
  - `parallelize`
  - `merge`
- direct-call specialists:
  - `agent-task-packet`
  - `codex-delegation-protocol`
  - `codex-worktree-dispatch`
  - `codex-tmux-orchestrator`
  - `codex-subagent-setup`
- use owner when:
  - 여러 agent/runtime/handoff를 함께 조율해야 할 때

### 4. Codebase Evidence Collection / Structuring

- owner: `codebase-analysis`
- owner verbs:
  - `analyze`
  - `gather`
  - `structure`
  - `prepare`
- direct-call specialists:
  - `codebase-progress`
  - `github-deep-research`
- use owner when:
  - later modeling/review/planning을 위한 multi-concern codebase evidence가 필요할 때

### 5. Design / Planning

- owner: `design-planning-orchestrator`
- owner verbs:
  - `plan`
  - `design`
  - `map`
  - `compose`
- direct-call specialists:
  - `semantic-slice-mapper`
  - `execution-contract-mapper`
  - `contract-to-concept-mapper`
  - `dependency-slice-planner`
  - `agent-graph-ir`
- use owner when:
  - concept, contract, slice, flow design이 함께 얽힌 multi-concern planning이 필요할 때

### 6. Lifecycle / Backup / Migration

- owner: `artifact-lifecycle-manager`
- owner verbs:
  - `migrate`
  - `backup`
  - `rename`
  - `clean`
- direct-call specialists:
  - none (standalone owner adapted closure — family closure 7-item 중 item 1, 2, 7은 N/A)
- use owner when:
  - directory structure change, backup, delete/replace, stale cleanup이 같이 움직일 때

### 7. Measurement / Evaluation

- owner: `measurement-evaluation-orchestrator`
- owner verbs:
  - `measure`
  - `benchmark`
  - `compare`
  - `evaluate`
- direct-call specialists:
  - `baseline-diff-lab`
  - `agent-tool-benchmark`
- use owner when:
  - metric formula, baseline diff, score interpretation이 함께 필요할 때

### 8. Multimodal Interpretation / Externalization

- owner: `multimodal-evidence-refinement-loop`
- owner verbs:
  - `reinject`
  - `refine`
  - `close`
  - `derive`
- direct-call specialists:
  - `image-text-cot-review`
- use owner when:
  - multimodal evidence를 반복적으로 이해하고 pending/closure를 관리해야 할 때

## Verb Taxonomy

- owner-first verbs:
  - `orchestrate`
  - `route`
  - `verify`
  - `judge`
  - `plan`
  - `refine`
  - `normalize`
  - `measure`
  - `migrate`
- specialist-first verbs:
  - `run`
  - `extract`
  - `export`
  - `build`
  - `render`
  - `dispatch`
  - `launch`
  - `audit`
  - `generate`
  - `promote`

## Standalone Skills (no family)

어떤 band에도 속하지 않는 독립 실행 skill. family closure 대상이 아님.

- `python-static-diagnostic-fixer` — Python IDE static diagnostics fix (fix)
- `langfuse-codex-prompt` — Langfuse SDK integration for Codex (fetch, record)
- `claude-session-poison-recovery` — Claude session corruption recovery (recover, restore)
- `mermaid-authoring-strategy` — Mermaid diagram authoring strategy (author, debug)
- `tmux-controller` — user-facing app tmux control (run, stop, restart) ⚠ watchlist

adjacency risk (verified standalone이지 permanent standalone은 아님):
- `tmux-controller` ↔ `codex-tmux-orchestrator` (Band 3): 같은 tmux, 다른 audience — Band 3 specialist 편입 후보로 watch
- `langfuse-codex-prompt` ↔ `agent-tool-benchmark` (Band 7): eval score 접점, 다른 scope

## Notes

- 명사는 body/reference link로 보강할 수 있지만, 동사는 YAML `description`에서 이미 라우팅을 결정한다.
- owner skill은 broad task context를 소유하고, specialist는 direct-call narrow context만 남긴다.
