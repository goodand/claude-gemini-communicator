---
name: codebase-progress
description: >-
  codebase-analysis family의 progress-scanning specialist. Use this skill when
  project progress must be assessed from code by scanning TODOs/FIXMEs, git
  activity, plan-vs-implementation drift, or agent session continuity.
  broader multi-concern codebase evidence collection은 codebase-analysis를
  사용하라.
---

# Codebase Progress

코드베이스를 직접 분석하여 프로젝트 진행 상황을 파악하고, drift를 감지한다.

## When to use

- TODO/FIXME 현황과 git 활동으로 진행률을 파악할 때
- 계획(마일스톤) 대비 실제 구현 drift를 감지할 때
- 이전 스캔 대비 변경(delta)을 확인할 때
- 에이전트 세션 기록에서 작업 진행 컨텍스트를 추출할 때

## Workflow

1. **스캔 실행** — `scripts/scan_progress.py`로 코드 상태 수집. mode별 분리: `todos`, `git-stats`, `milestone`, `delta`, `full` (→ ref1 repo-map + drift-detect 패턴)
2. **drift 감지** — 마일스톤 파일 대비 실제 구현을 대조. 키워드/파일 존재 검사로 완료 여부 판정. README가 아닌 코드 증거 기반 (→ ref1 drift-detect deterministic collectors)
3. **세션 컨텍스트 연계** — 에이전트 대화 세션에서 최근 작업 내역 추출. 여러 CLI 도구(Claude/Codex/Gemini)의 세션 디렉토리 탐색 (→ ref2 cli-continues 세션 인덱싱 패턴)
4. **보고서 생성** — 스캔 결과를 구조화된 markdown으로 출력. `--output`으로 파일 저장, 이전 결과와 diff 가능

## Scripts

- `scripts/scan_progress.py` — TODO/git/milestone/delta 통합 스캐너. `python3 scripts/scan_progress.py --help`

## References

- `references/codebase-기반-Progress-Management-Skills-search-at2026-08-15.md` — agentsys repo-map + drift-detect + workflow-state 분석, 3 repo 비교
- `references/Search-for-CLI-conversational-progress-management-skills-at-2026-03-13-20-17.md` — cli-continues 세션 인덱싱 + cross-tool handoff 분석

## Notes

- drift 감지는 키워드 매칭이므로 false positive 가능 — 코드 실제 확인 병행 권장
- git log 파싱은 `--no-walk` 없이 `--oneline` 사용, 대형 repo에서 `--since` 필수
- 에이전트 세션 경로는 OS/도구별로 다름 — `~/.claude/`, `~/.codex/` 등 (→ ref2 14개 도구 경로)
- 마일스톤 파일은 `- [ ]`/`- [x]` 체크리스트 또는 `## 항목명` 형식 지원
