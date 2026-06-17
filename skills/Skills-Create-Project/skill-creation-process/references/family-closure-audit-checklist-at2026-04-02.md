# Family Closure Audit Checklist

- generated_at: `2026-04-02`
- scope: `owner-family band closure / reusable audit protocol`
- gold sample: Band 1 (verification-decision-gate), Band 5 (design-planning-orchestrator), Band 7 (measurement-evaluation-orchestrator)

## Purpose

owner family를 닫을 때 매번 같은 7개 항목을 빠짐없이 확인하기 위한 canonical checklist.
이 문서가 closure 판정의 single source of truth다.

## 3-Step Audit Protocol

순서를 깨면 재감사한다.

### Step 1. Existence Audit

- glob으로 대상 SKILL.md 존재 확인
- "목록에 없다 ≠ 파일이 없다" — 반드시 filesystem read 증거로 판정
- owner SKILL.md + 모든 specialist SKILL.md 존재를 확인해야 Step 2로 넘어감

### Step 2. YAML-only Band Classification

- 판단 순서: **Task > Action Item > Verb > Noun** (noun만으로 band 결정 금지)
- owner verb와 specialist verb가 섞였는지 확인
- 같은 task + 같은 action을 가진 다른 skill이 있으면 conflict로 기록

### Step 3. Family Closure Checklist (7-item)

| # | 항목 | 확인 대상 | pass 조건 |
|---|---|---|---|
| 1 | specialist YAML family 선언 | 각 specialist `SKILL.md` frontmatter | `{owner-name} family의 ... specialist` 형식 |
| 2 | owner YAML specialist routing | owner `SKILL.md` frontmatter | 모든 specialist가 direct-call로 나열됨 |
| 3 | owner Family Roles 섹션 | owner `SKILL.md` body | owner + specialist 목록이 명시적으로 존재 |
| 4 | canonical band reference — specialist 목록 | `owner-task-bands-at2026-04-02.md` | 모든 specialist가 나열됨 |
| 5 | canonical band reference — use owner when | `owner-task-bands-at2026-04-02.md` | owner trigger 문장이 현재 specialist 범위를 반영 |
| 6 | owner body guardrail | owner `SKILL.md` body | When to use ✓, Do not use ✓, Workflow ✓ |
| 7 | specialist body specificity | 각 specialist `SKILL.md` body | 인접 band/skill과 겹치는 broad 표현 없음 |

## Source of Truth Rule

family closure 시 최소 3곳이 함께 바뀐다:

1. owner SKILL.md (description + Family Roles + Do not use)
2. specialist SKILL.md (description family 선언)
3. `owner-task-bands-at2026-04-02.md` (specialist 목록 + use owner when)

이 3곳이 어긋나면 source of truth가 갈라진 것으로 취급한다.

4. cross-workspace mirror가 있으면 provenance 3필드(`canonical source` / `imported from` / `last synced`) completeness를 함께 확인. 하나라도 빠지면 `incomplete provenance`.

## Known Risk Patterns

- **entrypoint 과적재**: owner SKILL.md가 70줄을 넘기면 reference로 내려야 함. 현재 watch: `worktree-parallel` (71줄), `skill-creation-process` (61줄)
- **band label drift**: owner YAML의 family name과 canonical band reference의 band name이 다르면 다음 라운드에서 통일
- **specialist 추가 시 3곳 동시 수정**: specialist를 추가하면 위 3곳을 한 pass에서 닫아야 함
- **ecosystem section 비대화**: owner에 Ecosystem routing note가 쌓이면 YAML + Family Roles + Ecosystem + owner-task-bands로 source of truth가 4곳 분산. 현재 watch: `multimodal-evidence-refinement-loop` (Ecosystem 8항목)

## Frozen Gold Samples

- Band 1: verification-decision-gate (5 specialists) — 2026-04-02
- Band 2: workspace-artifact-production-process (4 specialists) — 2026-04-02
- Band 3: worktree-parallel (5 specialists) — 2026-04-02
- Band 4: codebase-analysis (2 specialists) — 2026-04-02
- Band 5: design-planning-orchestrator (5 specialists) — 2026-04-02
- Band 6: artifact-lifecycle-manager (standalone owner adapted closure, 0 specialists) — 2026-04-02
- Band 7: measurement-evaluation-orchestrator (2 specialists) — 2026-04-02
- Band 8: multimodal-evidence-refinement-loop (1 specialist) — 2026-04-02

## Standalone Skills (verified 2026-04-02)

- python-static-diagnostic-fixer
- langfuse-codex-prompt
- claude-session-poison-recovery
- mermaid-authoring-strategy
- tmux-controller
