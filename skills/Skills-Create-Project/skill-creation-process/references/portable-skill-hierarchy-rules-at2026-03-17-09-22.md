# Portable Skill Hierarchy Rules

- generated_at: `2026-03-17-09-22`
- target: `skills intended for reuse in another workspace Codex CLI`

## Purpose

다른 workspace의 Codex CLI가 skill context를 안정적으로 따라가게 하려면,
핵심 컨텍스트 계층을 `skill 내부 -> bridge -> 명시적 외부 의존성` 순서로 고정해야 한다.

## Classification

- `internal`
  - 참조 대상이 같은 skill 디렉토리 안에 있다.
  - first-run context는 가능한 한 이 계층에서 닫는다.

- `bridge`
  - 참조 대상이 다른 설치 대상 skill 디렉토리 안에 있다.
  - cross-skill 연결은 가능하지만, handoff/bridge 문서 또는 downstream SKILL 포인터 수준으로 유지한다.

- `external_dependency`
  - 참조 대상이 현재 설치 대상 skill 묶음 밖, 같은 workspace의 다른 sibling 폴더에 있다.
  - portable pack에서는 가장 먼저 검토해야 하는 위험이다.
  - 해결 방향:
    - 내부 sample로 복제
    - optional fixture로 명시
    - install set에 추가

- `outside_workspace`
  - 참조 대상이 현재 workspace root 밖에 있다.
  - portable 관점에서 기본적으로 비권장이다.

- `absolute_path`
  - `/Users/...` 같은 절대경로다.
  - 다른 workspace 재사용 관점에서 비이식적이다.

- `missing`
  - 문서가 존재하지 않거나 상대경로가 끊겼다.
  - 가장 먼저 수정해야 한다.

## Rules

1. `SKILL.md`에서 직접 요구하는 핵심 문서는 가능한 한 `internal`이어야 한다.
2. 다른 skill을 따라가게 해야 하면 raw sibling path 대신 `bridge` 문서를 둔다.
3. `vertical-slice`나 `sample pair`가 외부 프로젝트를 가리키면 `external_dependency`로 보고 설치 세트에 포함할지, internal sample로 복제할지 결정한다.
4. `knowledge_base`의 연구 provenance 링크는 남길 수 있지만, first-run source of truth는 외부 sibling에 의존하지 않게 한다.
5. 다른 workspace에 배포하기 전에는 `scripts/skill_portability_audit.py`로 audit 결과를 남긴다.
6. `external_dependency`가 나오면 raw count로 끝내지 말고 optional fixture bundle manifest를 만들어 `install-required / optional fixture / provenance-only`를 확정한다.

## Current Bundle Baseline

- 현재 core reusable skill set의 optional fixture bundle baseline은
  [optional-fixture-bundle-manifest-at2026-03-17-09-39.md](./optional-fixture-bundle-manifest-at2026-03-17-09-39.md)
  를 따른다.
