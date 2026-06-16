# Reference Acquisition Modes

- generated_at: `2026-03-17-09-35`
- scope: `skill-creation-process Phase 0`

## Purpose

KB를 만들 때 항상 외부 웹 조사부터 가는 것이 아니라,
사용자 요청에 따라 `외부 조사 포함`과 `내부 코드베이스만 사용` 두 모드를 분기한다.

## Modes

### Default: external_research

- 기본 모드
- GitHub, 논문, 기술 문서, 블로그, 기존 local codebase를 함께 사용한다
- `research_index_kb`를 넓게 만드는 데 적합하다

활성 조건:
- 사용자가 별도 제한을 주지 않음
- 최신 사례나 외부 설계 선택지가 가치 있다고 판단됨

### Opt-In: internal_codebase_only

- 사용자가 명시적으로 요청했을 때만 활성화한다
- 외부 웹 검색 없이 현재 workspace와 이미 존재하는 local artifact만 사용한다

활성 조건:
- 사용자가 `웹 검색 없이`
- `외부 자료 없이`
- `내부 코드베이스만`
- `현재 workspace만으로`
  같은 표현으로 명시

## Allowed Sources In `internal_codebase_only`

- 현재 workspace의 codebase
- 현재 workspace의 `references/`, `knowledge_bases/`, `checklist-*`, `scripts/`
- 기존 smoke/evidence/diff artifact
- 현재 workspace 안의 다른 skill 문서와 script

## Disallowed Sources In `internal_codebase_only`

- 웹 검색
- GitHub deep research
- 논문/블로그/외부 공식 문서 신규 조사
- 현재 workspace 밖의 새로운 reference 유입

## KB Guidance

- `internal_codebase_only`여도 KB는 만들 수 있다
- 다만 성격은 보통 아래 둘 중 하나다
  - local-reference `research_index_kb`
  - local-source `hybrid_kb`
- checklist source of truth가 필요하면 결국 `Canonical Design Takeaways`를 넣어 `hybrid_kb` 이상으로 올린다

## Good Fits

- 기존 codebase와 정합적인 MD 작성
- 기존 checklist/contract와 정합적인 script 작성
- 외부 best practice보다 현재 local source of truth를 우선해야 하는 수정
- portable install 문맥처럼 외부 링크를 늘리지 않는 작업

## Output Marking

이 모드를 썼다면 KB나 note에 아래를 남긴다.

- `reference_acquisition_mode: internal_codebase_only`
- `source_scope: local_workspace_only`

## Decision Rule

1. 기본은 `external_research`
2. 사용자 명시 요청이 있을 때만 `internal_codebase_only`
3. `internal_codebase_only`에서는 외부 best practice보다 local contract 정합성을 우선한다
