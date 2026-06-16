# Optional Fixture Bundle Manifest

- generated_at: `2026-03-17-09-39`
- scope: `core reusable skill set for another workspace Codex CLI`
- source audit:
  - [core-skill-portability-audit-at2026-03-17-09-22.md](./core-skill-portability-audit-at2026-03-17-09-22.md)
  - [install-readiness-dependency-map-at2026-03-17-09-28.md](../../doc-code-sync-checker/references/install-readiness-dependency-map-at2026-03-17-09-28.md)

## Purpose

주축 skill을 다른 workspace에 설치할 때,
core engine과 sample reproduction fixture를 분리해서 배포 범위를 명확히 한다.

## Decision

현재 core reusable skill set 기준으로 확정된 optional fixture bundle은 아래 두 개다.

- [agent-task-packet](../../agent-task-packet/SKILL.md)
- [codex-worktree-dispatch](../../codex-worktree-dispatch/SKILL.md)

그 외 core nine 기준 추가 optional fixture bundle은 현재 없다.

## Why These Two

### `agent-task-packet`

- 연결 skill: [doc-code-sync-checker](../../doc-code-sync-checker/SKILL.md)
- 용도: `required_field` sample pair 재현
- 연결 문서:
  - [vertical-slice-required-field-at2026-03-16-20-03.md](../../doc-code-sync-checker/references/vertical-slice-required-field-at2026-03-16-20-03.md)

### `codex-worktree-dispatch`

- 연결 skill: [doc-code-sync-checker](../../doc-code-sync-checker/SKILL.md)
- 용도:
  - `path_safety` sample pair 재현
  - `transition_rule` sample pair 재현
  - `enum_value` sample pair 재현
- 연결 문서:
  - [vertical-slice-path-safety-at2026-03-16-20-44.md](../../doc-code-sync-checker/references/vertical-slice-path-safety-at2026-03-16-20-44.md)
  - [vertical-slice-transition-rule-at2026-03-16-21-48.md](../../doc-code-sync-checker/references/vertical-slice-transition-rule-at2026-03-16-21-48.md)
  - [vertical-slice-enum-value-at2026-03-16-22-13.md](../../doc-code-sync-checker/references/vertical-slice-enum-value-at2026-03-16-22-13.md)

## Excluded From Optional Fixture Pack

- `github-deep-research`
- `_shared/reference-inbox`

이 둘은 sample reproduction fixture가 아니라 research provenance 성격이라 기본 배포 묶음에 넣지 않는다.

## Install Profiles

### Core Portable Pack

- 주축 9개 skill만 설치
- 목적:
  - core process 사용
  - own input 기반 실행
  - sample pair 원본 재현은 생략

### Sample Reproduction Pack

- 주축 9개 skill
- `agent-task-packet`
- `codex-worktree-dispatch`

목적:
- `doc-code-sync-checker`의 문서화된 sample pair 재현

### Provenance-Extended Pack

- `Sample Reproduction Pack`
- 추가 provenance source를 별도 선택 설치

목적:
- research provenance 원본 링크까지 추적
- 기본 설치 기준으로는 과하다

## Result

다른 workspace Codex CLI에 주축 skill을 배포할 때,
sample reproduction이 필요하면 현재는 아래 둘만 추가로 가져가면 된다.

1. `agent-task-packet`
2. `codex-worktree-dispatch`
