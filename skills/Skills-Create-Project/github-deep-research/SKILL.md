---
name: github-deep-research
description: >-
  codebase-analysis family의 GitHub research specialist. Use this skill when
  GitHub repositories, code patterns, issues, or PRs must be explored with
  structured repo → module → execution validation and shallow search is not
  enough. broader multi-concern codebase evidence collection은
  codebase-analysis를 사용하라.
---

# GitHub Deep Research

짧은 검색 요청을 구조화된 탐색-검증 워크플로우로 확장한다.

## When to use

- 특정 SDK/라이브러리의 실제 사용 패턴을 코드에서 찾을 때
- 에러 메시지의 해결법을 이슈/PR에서 찾을 때
- 유사 오픈소스 프로젝트를 비교 분석할 때
- repo 추천 시 README가 아닌 코드/테스트 증거가 필요할 때

## Workflow

1. **의도 정규화** — 사용자 요청에서 검색 scope(code/issues/prs/repos), 필수/선택 요구사항, 제외 조건을 분리한다
2. **후보 수집** — `scripts/deep_search.py`로 scope별 검색 실행. 넓은 검색과 정밀 검색을 병행한다
3. **repo 검증** — 후보를 코드 수준에서 확인한다 (`gh api repos/.../contents/...`). README만으로 판단하지 않는다. repo가 부적합하면 같은 repo 내 다른 module을 먼저 확인한 뒤 다음 repo로 이동한다 (→ agent-prompt-reference R4 fallback 규칙)
4. **구조화 보고서** — 검증 결과를 정리한다: 추천 repo/module, 검증 근거, 불일치 로그, 탈락 사유 (→ agent-output-reference 템플릿)

심층 조사 시 Task/Router/Loop/Exit 제어 흐름을 적용한다 (→ agent-prompt-reference).

## Scripts

- `scripts/deep_search-at2026-03-13-18-00.py` — `gh search code/issues/prs/repos` 통합 래퍼. `python3 scripts/deep_search-at2026-03-13-18-00.py --help`
- `scripts/repo_inspect-at2026-03-13.py` — repo 검증 증거 일괄 수집 (기본정보/파일트리/README/이슈/커밋). `python3 scripts/repo_inspect-at2026-03-13.py owner/repo`

## References

- `references/gh-search-cheatsheet-at2026-03-13-18-00.md` — gh search 커맨드, 검색 전략 테이블, `--` 구분자
- `references/github-deep-research-reference-at2026-03-13-17-45.md` — 오픈 스킬 6개 사례 조사
- `references/github-deep-research-agent-prompt-reference-at2026-03-13-17-47.md` — T/R/L/E 제어 흐름 + 3단계 검증(repo→module→실행) 전체 템플릿
- `references/github-deep-research-agent-output-reference-at2026-03-13-17-47` — 구조화 보고서 출력 템플릿

## Notes

- `gh auth status`로 인증 확인 필수 (rate limit 5,000 req/hr)
- 제외 조건(negation qualifier) 사용 시 `--` 구분자 필수: `gh search code -- "query -qualifier:value"`
- 스타 수나 README 문구를 기능 정합성보다 우선하지 않는다 — 코드/테스트가 더 강한 증거
- repo 부적합 판정 전 같은 repo 내 대안 module을 먼저 확인한다
