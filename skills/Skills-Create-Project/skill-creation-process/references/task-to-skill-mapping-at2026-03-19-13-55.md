# Task To Skill Mapping

- generated_at: `2026-03-19-13-55`
- purpose: `repeated task를 stable key로 보고 관련 skill과 page linker를 바로 찾기 위한 lookup page`

## Usage

- `TASK-01` 같은 key로 반복 Task를 찾는다
- `Primary Skills`는 먼저 직접 쓰는 skill
- `Support Skills`는 bridge/handoff 또는 후속 단계에서 따라가는 skill
- `Page Linker`는 먼저 열어볼 reference 또는 skill entrypoint

## Mapping Table

### TASK-01 — Reference Acquisition Mode 결정

- label: `reference_acquisition_mode_selection`
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - [claim-verifier](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/claim-verifier/SKILL.md)
- Page Linker:
  - [phase-guide.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/phase-guide.md)
  - [reference-acquisition-modes-at2026-03-17-09-35.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/reference-acquisition-modes-at2026-03-17-09-35.md)

### TASK-02 — KB Profile 분기

- label: `kb_profile_branching`
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
  - [kb-checklist-pipeline](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/kb-checklist-pipeline/SKILL.md)
- Support Skills:
  - [contract-to-concept-mapper](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/contract-to-concept-mapper/SKILL.md)
- Page Linker:
  - [phase-guide.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/phase-guide.md)
  - [progressive-context-skill-strategy-template.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/templates/progressive-context-skill-strategy-template.md)

### TASK-03 — KB -> Consistency -> Implementation

- label: `kb_to_checklists`
- Primary Skills:
  - [kb-checklist-pipeline](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/kb-checklist-pipeline/SKILL.md)
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - [execution-contract-mapper](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/SKILL.md)
- Page Linker:
  - [phase-guide.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/phase-guide.md)

### TASK-04 — Contract-First Vertical Slice

- label: `contract_first_vertical_slice`
- Primary Skills:
  - [execution-contract-mapper](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/SKILL.md)
  - [slice-experiment-lab](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/slice-experiment-lab/SKILL.md)
- Support Skills:
  - [doc-code-sync-checker](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/doc-code-sync-checker/SKILL.md)
  - [dependency-slice-planner](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/dependency-slice-planner/SKILL.md)
- Page Linker:
  - [execution-contract-mapper/SKILL.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/SKILL.md)
  - [slice-experiment-lab/SKILL.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/slice-experiment-lab/SKILL.md)

### TASK-05 — TDD -> Implementation -> Smoke -> Evidence -> quick_validate

- label: `execution_evidence_loop`
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
  - [slice-experiment-lab](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/slice-experiment-lab/SKILL.md)
- Support Skills:
  - [evidence-trace-auditor](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/SKILL.md)
  - [baseline-diff-lab](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/baseline-diff-lab/SKILL.md)
- Page Linker:
  - [execution-evidence-pattern-at2026-03-17-04-03.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/execution-evidence-pattern-at2026-03-17-04-03.md)
  - [slice-experiment-lab/SKILL.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/slice-experiment-lab/SKILL.md)

### TASK-06 — references/ Artifact Triad 남기기

- label: `artifact_triad_recording`
- Primary Skills:
  - [slice-experiment-lab](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/slice-experiment-lab/SKILL.md)
- Support Skills:
  - [evidence-trace-auditor](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/SKILL.md)
- Page Linker:
  - [vertical-slice-experiment-bundle-at2026-03-19-00-45.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/slice-experiment-lab/references/vertical-slice-experiment-bundle-at2026-03-19-00-45.md)

### TASK-07 — Capture Artifact Bridge

- label: `capture_artifact_bridge`
- Primary Skills:
  - [slice-experiment-lab](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/slice-experiment-lab/SKILL.md)
- Support Skills:
  - [evidence-trace-auditor](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/SKILL.md)
- Page Linker:
  - [vertical-slice-quick-validate-artifact-bridge-at2026-03-19-01-07.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/slice-experiment-lab/references/vertical-slice-quick-validate-artifact-bridge-at2026-03-19-01-07.md)
  - [vertical-slice-captured-smoke-to-bundle-at2026-03-19-13-16.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/slice-experiment-lab/references/vertical-slice-captured-smoke-to-bundle-at2026-03-19-13-16.md)

### TASK-08 — Next-Slice Gate 판단

- label: `next_slice_gate`
- Primary Skills:
  - [slice-experiment-lab](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/slice-experiment-lab/SKILL.md)
- Support Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Page Linker:
  - [vertical-slice-strict-warning-policy-gate-at2026-03-19-13-21.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/slice-experiment-lab/references/vertical-slice-strict-warning-policy-gate-at2026-03-19-13-21.md)
  - [implementation-checklist-at2026-03-19-00-45.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/slice-experiment-lab/checklist-forimplementation/implementation-checklist-at2026-03-19-00-45.md)

### TASK-09 — Evidence To KB Promotion

- label: `evidence_to_kb_promotion`
- Primary Skills:
  - [evidence-to-knowledge-promoter](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-to-knowledge-promoter/SKILL.md)
- Support Skills:
  - [evidence-trace-auditor](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/SKILL.md)
  - [baseline-diff-lab](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/baseline-diff-lab/SKILL.md)
- Page Linker:
  - [evidence-promotion-pattern-at2026-03-17-03-45.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/evidence-promotion-pattern-at2026-03-17-03-45.md)

### TASK-10 — Portability / Install-Readiness Audit

- label: `portable_install_audit`
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - [artifact-lifecycle-manager](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/artifact-lifecycle-manager/SKILL.md)
- Page Linker:
  - [portable-skill-hierarchy-rules-at2026-03-17-09-22.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/portable-skill-hierarchy-rules-at2026-03-17-09-22.md)
  - [core-skill-portability-audit-at2026-03-17-09-22.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/core-skill-portability-audit-at2026-03-17-09-22.md)

### TASK-11 — SKILL.md Line-Count Warning 대응

- label: `skill_entrypoint_split`
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - [artifact-lifecycle-manager](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/artifact-lifecycle-manager/SKILL.md)
- Page Linker:
  - [skill-entrypoint-details-at2026-03-18-23-32.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/skill-entrypoint-details-at2026-03-18-23-32.md)

### TASK-12 — Bounded Subagent Delegation

- label: `bounded_subagent_delegation`
- Primary Skills:
  - [agent-task-packet](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/agent-task-packet/SKILL.md)
- Support Skills:
  - [codex-worktree-dispatch](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-worktree-dispatch/SKILL.md)
  - [codex-tmux-orchestrator](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-tmux-orchestrator/SKILL.md)
  - [worktree-parallel](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/worktree-parallel/SKILL.md)
- Page Linker:
  - [agent-task-packet/SKILL.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/agent-task-packet/SKILL.md)
  - [worktree-parallel/SKILL.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/worktree-parallel/SKILL.md)

### TASK-13 — Semantic Owner / Execution Specialist Split

- label: `semantic_owner_specialist_split`
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
  - [multimodal-evidence-refinement-loop](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/multimodal-evidence-refinement-loop/SKILL.md)
  - [image-text-cot-review](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/image-text-cot-review/SKILL.md)
- Support Skills:
  - [evidence-trace-auditor](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/SKILL.md)
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-14 — YAML Description Verb Alignment Before Body Edits

- label: `yaml_verb_alignment`
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - [multimodal-evidence-refinement-loop](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/multimodal-evidence-refinement-loop/SKILL.md)
  - [image-text-cot-review](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/image-text-cot-review/SKILL.md)
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-15 — Cross-Workspace Canonical Skill Exposure

- label: `cross_workspace_skill_exposure`
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - [artifact-lifecycle-manager](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/artifact-lifecycle-manager/SKILL.md)
- Page Linker:
  - [portable-skill-hierarchy-rules-at2026-03-17-09-22.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/portable-skill-hierarchy-rules-at2026-03-17-09-22.md)

### TASK-16 — Routing Mirror Update After Family Addition

- label: `routing_mirror_family_update`
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - [multimodal-evidence-refinement-loop](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/multimodal-evidence-refinement-loop/SKILL.md)
  - [image-text-cot-review](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/image-text-cot-review/SKILL.md)
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-17 — Iterative Multi-Round YAML Description Verb Narrowing

- label: `iterative_yaml_verb_narrowing`
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - [multimodal-evidence-refinement-loop](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/multimodal-evidence-refinement-loop/SKILL.md)
  - [image-text-cot-review](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/image-text-cot-review/SKILL.md)
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-18 — Bidirectional Ecosystem Routing Closure

- label: `bidirectional_ecosystem_closure`
- Primary Skills:
  - [multimodal-evidence-refinement-loop](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/multimodal-evidence-refinement-loop/SKILL.md)
  - [image-text-cot-review](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/image-text-cot-review/SKILL.md)
- Support Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-19 — Family Closure Audit Protocol (3-Step) — `protocol`

- label: `family_closure_audit_protocol`
- classification: protocol (substep 19a body guardrail backfill, 19b batch sync 포함)
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - [verification-decision-gate](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/verification-decision-gate/SKILL.md)
- Page Linker:
  - [family-closure-audit-checklist-at2026-04-02.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/family-closure-audit-checklist-at2026-04-02.md)
  - [owner-task-bands-at2026-04-02.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/owner-task-bands-at2026-04-02.md)

### TASK-20 — Specialist-Less Owner Band Adapted Closure — `standalone-task`

- label: `specialist_less_owner_adapted_closure`
- classification: standalone-task
- Primary Skills:
  - [artifact-lifecycle-manager](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/artifact-lifecycle-manager/SKILL.md)
- Support Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Page Linker:
  - [family-closure-audit-checklist-at2026-04-02.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/family-closure-audit-checklist-at2026-04-02.md)

### TASK-21 — Standalone Skill Band-Membership Triage — `standalone-task`

- label: `standalone_skill_band_membership_triage`
- classification: standalone-task
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - none
- Page Linker:
  - [owner-task-bands-at2026-04-02.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/owner-task-bands-at2026-04-02.md)

### TASK-22 — Cross-Workspace Mirror Provenance Tagging — `standalone-task`

- label: `cross_workspace_mirror_provenance_tagging`
- classification: standalone-task
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - none
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-23 — Freeze State Normalization With Watch Separation — `standalone-task`

- label: `freeze_state_normalization_with_watch_separation`
- classification: standalone-task
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - [owner-task-bands-at2026-04-02.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/owner-task-bands-at2026-04-02.md)
  - [family-closure-audit-checklist-at2026-04-02.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/family-closure-audit-checklist-at2026-04-02.md)
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-24 — Closure Patch Adjacent-Band Vocabulary Detection — `loop`

- label: `closure_patch_adjacent_band_vocabulary_detection`
- classification: loop
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - [owner-task-bands-at2026-04-02.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/owner-task-bands-at2026-04-02.md)
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-25 — Taxonomy Retrofit (Sidecar) — `repair-step`

- label: `taxonomy_retrofit`
- classification: repair-step (1회성이지만 label 누락 반복 시 재발)
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - none
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-26 — Substep Inflation Prevention — `repair-step`

- label: `substep_inflation_prevention`
- classification: repair-step
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - none
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-27 — Mirror Provenance 3-Field Completion — `repair-step`

- label: `mirror_provenance_3_field_completion`
- classification: repair-step
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - none
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-28 — Two-Axis Taxonomy Separation — `repair-step`

- label: `two_axis_taxonomy_separation`
- classification: repair-step
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - [family-closure-audit-checklist-at2026-04-02.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/family-closure-audit-checklist-at2026-04-02.md)
  - [owner-task-bands-at2026-04-02.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/owner-task-bands-at2026-04-02.md)
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-29 — Stable Key First Append-Only Numbering Discipline — `repair-step`

- label: `stable_key_first_append_only_numbering`
- classification: repair-step
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - none
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-30 — Truth-Source-First Pipeline Preflight — `standalone-task`

- label: `truth_source_first_pipeline_preflight`
- classification: standalone-task
- Primary Skills:
  - [claim-verifier](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/claim-verifier/SKILL.md)
- Support Skills:
  - [doc-code-sync-checker](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/doc-code-sync-checker/SKILL.md)
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-31 — Programmatic QA To Visual Export Readback — `loop`

- label: `programmatic_qa_to_visual_export_readback`
- classification: loop
- Primary Skills:
  - [baseline-diff-lab](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/baseline-diff-lab/SKILL.md)
- Support Skills:
  - [evidence-trace-auditor](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/SKILL.md)
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-32 — Structured Data Truth Source / Screenshot Evidence Split — `standalone-task`

- label: `structured_data_truth_source_screenshot_evidence_split`
- classification: standalone-task
- Primary Skills:
  - [claim-verifier](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/claim-verifier/SKILL.md)
- Support Skills:
  - [doc-code-sync-checker](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/doc-code-sync-checker/SKILL.md)
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-33 — Presentation-Surface Missing-Value Normalization — `repair-step`

- label: `presentation_surface_missing_value_normalization`
- classification: repair-step
- Primary Skills:
  - [execution-contract-mapper](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/SKILL.md)
- Support Skills:
  - [claim-verifier](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/claim-verifier/SKILL.md)
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-34 — Visual Patch Fail-Fast Layout Rerun — `loop`

- label: `visual_patch_fail_fast_layout_rerun`
- classification: loop
- Primary Skills:
  - [baseline-diff-lab](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/baseline-diff-lab/SKILL.md)
- Support Skills:
  - [evidence-trace-auditor](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/SKILL.md)
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-35 — Workspace Roots / Reference / Live Generator Confirmation — `standalone-task`

- label: `workspace_roots_reference_live_generator_confirmation`
- classification: standalone-task
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - [claim-verifier](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/claim-verifier/SKILL.md)
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-36 — File-System Manifest Scan Before Spec Binding — `standalone-task`

- label: `file_system_manifest_scan_before_spec_binding`
- classification: standalone-task
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - [claim-verifier](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/claim-verifier/SKILL.md)
  - [doc-code-sync-checker](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/doc-code-sync-checker/SKILL.md)
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

### TASK-37 — Interpreter Lineage Verification Before Generator Rerun — `loop`

- label: `interpreter_lineage_verification_before_generator_rerun`
- classification: loop
- Primary Skills:
  - [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)
- Support Skills:
  - [claim-verifier](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/claim-verifier/SKILL.md)
- Page Linker:
  - [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)

## Notes

- `TASK-xx` key는 stable lookup key로 쓴다.
- repeated-pattern 문서의 사람이 읽는 번호는 historical append-only로 보고, stable lookup은 `TASK-xx`를 우선한다.
- issue에서 task로 갈 때는 [repeated-task-and-issue-patterns-at2026-03-19-13-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)를 먼저 본다.
- repeated-pattern 문서의 `Issue To Task Mapping`은 join/index view이며, 새 canonical task/issue를 먼저 append하는 surface가 아니다.
- task에서 바로 skill을 찾고 싶으면 이 문서를 lookup page로 쓴다.
- machine-readable lookup은 `references/catalog/tasks.json`, `references/catalog/skills.json`, `references/catalog/joins.json`, `scripts/catalog_lookup.py`를 사용한다.
- issue에서 `TASK -> SKILL` join을 바로 보고 싶으면 `python3 skill-creation-process/scripts/catalog_lookup.py show --key JOIN-ISSUE-07` 같은 형식으로 조회한다.
