---
name: super-skill-creator
description: >-
  Meta-skill for creating, improving, evaluating, and packaging Agent Skills.
  Use when the user wants to build a new skill, refactor an existing skill,
  add scripts/references/assets, create evals, compare baseline vs with-skill
  behavior, improve triggering descriptions, or package skills for reuse.
license: MIT
---

# Super Skill Creator

## Purpose

This skill exists to help create other skills well.

Use it when the user wants to:

- create a new Agent Skill
- improve an existing Agent Skill
- turn a repeated workflow into a reusable skill
- move a long prompt into a skill package
- add scripts, references, assets, or evals to a skill
- benchmark a skill against baseline behavior
- improve skill triggering / routing
- package a skill into a reusable folder or archive

## Core principles

### 1. Keep SKILL.md lean

The context window is shared. Do not stuff large examples, schemas, or detailed docs
into `SKILL.md` unless they are truly core instructions.

Use:

- `scripts/` for deterministic or repeated operations
- `references/` for detailed documentation, schemas, long examples
- `assets/` for templates or files used in output

### 2. Prefer progressive disclosure

Structure skills so the model can load only what is needed:

1. metadata in YAML frontmatter
2. core workflow in `SKILL.md`
3. detailed docs in `references/`
4. repeatable logic in `scripts/`

### 3. Design for triggering

The `description` field is extremely important. It should clearly say:

- what the skill does
- when it should be used
- what kinds of user requests should trigger it

If a skill is under-triggering, make the description more explicit and concrete.

### 4. Evaluate, do not guess

Do not assume a skill works because it “looks good”.
Create realistic eval prompts and compare:

- with-skill
- without-skill baseline
- old-skill vs new-skill when improving

### 5. Scripts are infrastructure, not optional

Scripts는 단순 자동화가 아니라 **스킬 작동 결과를 추적·검증하는 인프라**다.
3가지 역할: (1) 작업 자동화, (2) 검증 로직 (exit code 계약), (3) 결과 추적 (`--output`).

### 6. Verify with scripts, not eyes

`quick_validate.py`로 구조 검증, `skill_smoke_test.py`로 스크립트 실행·evals 구조·섹션 존재를 자동 확인.
Smoke test 없이 완료 선언하지 않는다.

### 7. Prefer reusable structure over one-off cleverness

A good skill is reusable, composable, and easy to maintain.

## Workflow

## Step 1 — Identify the job to be done

Figure out which of these applies:

- **new skill**: nothing exists yet
- **refactor skill**: a prompt or process exists but is messy
- **improve skill**: a skill exists but performs poorly
- **package skill**: files exist but need proper skill structure
- **benchmark skill**: compare variants and gather evidence
- **routing optimization**: improve the skill description / AGENTS hints

Ask focused questions only when necessary:

- what task should the skill handle?
- what should trigger it?
- what outputs matter?
- what inputs/files are involved?
- what edge cases matter?
- what counts as success?

## Step 2 — Decide the right freedom level

Choose the right level of instruction:

- **high freedom**: heuristic workflow, many valid paths
- **medium freedom**: a preferred structure with some variation
- **low freedom**: deterministic sequence, exact script, fragile process

Use scripts when correctness or repeatability matters.

## Step 3 — Scaffold the skill

When creating a new skill, generate:

- `SKILL.md`
- `scripts/` if deterministic logic is needed
- `references/` if long docs or schemas are needed
- `assets/` if templates or output resources are needed
- `evals/` if the user wants testing and benchmarking

Use `scripts/init_skill.py` when possible.

## Step 4 — Write the skill

When writing `SKILL.md`:

- make the title and purpose obvious
- say when to use the skill
- explain the workflow in imperative steps
- explicitly point to `scripts/` and `references/`
- avoid duplicated documentation
- avoid filler prose

Include examples only if they genuinely help.

## Step 5 — Create eval prompts

Create 2–5 realistic prompts that a real user would actually say.

Good eval prompts:

- resemble normal user requests
- cover mainline behavior
- include at least one edge case when relevant
- are specific enough to grade

Save them in a structured form if benchmarking is planned.

## Step 6 — Compare variants

When evaluating:

- launch with-skill and baseline comparisons from the same prompt set
- save outputs separately
- write assertions for objective checks
- keep qualitative review for style or judgment-heavy tasks

Use:

- `scripts/init_iteration.py`
- `scripts/aggregate_benchmark.py`
- `scripts/generate_static_review.py`

## Step 7 — Analyze and improve

Use benchmark results and human feedback to improve:

- triggering quality
- workflow clarity
- script usefulness
- token/time cost
- reliability across prompts

Use `agents/analyzer.md`, `agents/grader.md`, and `agents/comparator.md`.

## Step 8 — Improve routing

If a skill is not triggering reliably:

- tighten the YAML description
- add routing hints to `AGENTS.md` / `CLAUDE.md`
- reduce overlap with similar skills
- avoid having too many near-duplicate skills

Use:

- `references/triggering-and-routing.md`
- `scripts/make_routing_doc.py`

## Step 9 — Package for reuse

Once the skill is stable:

- validate structure
- remove junk files
- ensure references are intentional
- package into zip/tar if needed

Use `scripts/quick_validate.py`, `scripts/skill_smoke_test.py`, and `scripts/package_skill.py`.

## What not to do

Do not:

- create unnecessary README files inside the skill
- duplicate docs across SKILL.md and references
- write huge walls of text in SKILL.md
- assume the description is “good enough” without trigger review
- benchmark with unrealistic prompts
- compare variants using different prompt sets

## Output conventions

When creating or improving a skill, output in this order:

1. summary of the job
2. proposed skill structure
3. `SKILL.md`
4. scripts / references / assets as needed
5. eval prompts
6. benchmark plan if relevant
7. packaging notes if relevant

## Common use cases

### Case A — User says:
“Make me a skill for X.”

Do:
- clarify scope
- scaffold a new skill
- write SKILL.md
- add references/scripts only if needed
- propose eval prompts

### Case B — User says:
“Improve this skill.”

Do:
- inspect existing structure
- identify problems
- preserve a baseline snapshot if benchmarking
- improve SKILL.md / scripts / routing
- run comparison plan

### Case C — User says:
“Turn this repeated prompt/process into a reusable skill.”

Do:
- identify repeated decisions and deterministic steps
- split instructions into workflow + scripts + references
- write a triggerable description
- produce packaging-ready structure

### Case D — User says:
“The skill doesn’t trigger reliably.”

Do:
- inspect description
- inspect overlap with similar skills
- generate routing hints
- produce positive and negative trigger examples

## Quick checklist

Before finalizing a skill, check:

- Is the description explicit?
- Is SKILL.md concise?
- Are large docs moved to references?
- Are deterministic steps moved to scripts?
- Are eval prompts realistic?
- Is there a clear benchmark plan?
- Is routing guidance documented?