# Install Readiness Dependency Map

- generated_at: `2026-03-17-09-28`
- target skill: `doc-code-sync-checker`
- purpose: `portable install 관점에서 external sibling 의존성을 분류`

## Summary

`doc-code-sync-checker`의 core engine 자체는 이 skill 폴더만으로 작동한다.
다만 현재 문서에 포함된 vertical-slice 예시 pair는 외부 sibling fixture를 참조한다.

## Classification

### Install-Required

- 없음

설명:
- `scripts/doc_code_sync.py`
- canonical KB
- consistency checklist
- implementation checklist

이 조합만으로 rule engine과 compare/report 흐름 자체는 닫힌다.

### Optional Fixture

- [agent-task-packet](../../agent-task-packet/SKILL.md)
  - 이유: `required_field` sample pair 재현용
  - 연결 문서:
    - [vertical-slice-required-field-at2026-03-16-20-03.md](./vertical-slice-required-field-at2026-03-16-20-03.md)

- [codex-worktree-dispatch](../../codex-worktree-dispatch/SKILL.md)
  - 이유: `path_safety`, `transition_rule`, `enum_value` sample pair 재현용
  - 연결 문서:
    - [vertical-slice-path-safety-at2026-03-16-20-44.md](./vertical-slice-path-safety-at2026-03-16-20-44.md)
    - [vertical-slice-transition-rule-at2026-03-16-21-48.md](./vertical-slice-transition-rule-at2026-03-16-21-48.md)
    - [vertical-slice-enum-value-at2026-03-16-22-13.md](./vertical-slice-enum-value-at2026-03-16-22-13.md)

설명:
- 이 둘은 `first-run required dependency`가 아니라 `documented sample reproduction dependency`다.
- 다른 workspace에 최소 설치만 할 경우 제외 가능하다.

### Internalize

- `github-deep-research` search note
- `_shared/reference-inbox` intent memo

설명:
- 이 둘은 runtime pair나 source of truth가 아니라 research provenance다.
- first-run context를 막지 않도록 external link를 직접 따라가게 만들지 말고, 현재 KB 안에 요약만 남기는 쪽이 맞다.

## Recommended Install Modes

### Minimal Portable Install

- `doc-code-sync-checker`만 설치

용도:
- engine 구조 이해
- own pair 입력으로 drift 검사
- sample pair 재현은 하지 않음

### Sample-Complete Install

- `doc-code-sync-checker`
- `agent-task-packet`
- `codex-worktree-dispatch`

용도:
- 현재 references에 적힌 vertical-slice 예시를 그대로 재현

### Provenance-Complete Install

- `doc-code-sync-checker`
- `agent-task-packet`
- `codex-worktree-dispatch`
- `github-deep-research`
- `_shared/reference-inbox`

용도:
- research provenance까지 원본 경로 수준으로 추적
- 보통은 과하다

## Decision

- 기본 배포 기준은 `Minimal Portable Install`
- 예시 재현까지 원하면 `Sample-Complete Install`
- provenance 원본 추적은 optional이며 기본 배포 범위에 넣지 않는다
