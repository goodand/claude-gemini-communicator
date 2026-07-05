---
name: skill-path-resolver
description: >-
  Use this skill when skills fail due to path errors ("No such file",
  "ModuleNotFoundError"), when migrating between environments (Claude
  Container, Gemini CLI, local), or when setting up $SKILLS_ROOT.
  스킬 경로 해석 + 하드코딩 경로 수정 — 다른 스킬의 기반 인프라.
---

# Skill Path Resolver

스킬 간 경로 문제를 해결하는 기반 인프라. 다른 스킬에서 import하여 사용한다.

## When to use

- 스킬 실행 시 "No such file or directory" 경로 에러가 날 때
- 새 환경(Claude Container, Gemini CLI, 로컬)에서 스킬을 처음 설정할 때
- 다른 스킬에서 스킬 간 경로를 동적으로 해석해야 할 때
- 하드코딩된 절대경로를 일괄 수정해야 할 때

## Workflow

1. **환경 감지** — `scripts/resolver.py detect`로 현재 환경과 SKILLS_ROOT를 자동 탐지. 5단계 우선순위: $SKILLS_ROOT → Claude Container → Gemini global → 프로젝트 로컬 → CWD (→ ref supported_patterns 환경별 경로 루트)
2. **경로 수정** — `scripts/resolver.py fix-all --dry-run`으로 하드코딩 경로 미리보기 후 적용. Python/Bash/Markdown 패턴 자동 감지 (→ ref supported_patterns 수정 대상 패턴)
3. **스킬 간 연동** — 다른 스킬에서 `skill_paths.py`를 import하여 경로 해석. `SkillPaths.get_script()`, `get_reference()` API 사용 (→ ref examples Example 9)
4. **환경변수 내보내기** — `scripts/resolver.py export --shell bash`로 셸 설정 생성. bash/fish/powershell 지원

## Scripts

- `scripts/skill_paths.py` — **핵심 모듈**. 다른 스킬에서 `from skill_paths import SkillPaths`로 import. 환경 자동 탐지 + LRU 캐싱
- `scripts/resolver.py` — **CLI 도구**. `detect`, `fix`, `fix-all`, `export`, `resolve` 서브커맨드. `python3 scripts/resolver.py --help`
- `scripts/workspace_manager.py` — 중간 파일 정리. `cleanup` 서브커맨드 + `--keep` 패턴

## References

- `references/examples.md` — 10개 사용 예시 (환경 설정, 경로 수정, CI/CD, 셸별 설정)
- `references/supported_patterns.md` — 감지/수정 대상 패턴 (Python/Bash/Markdown), 환경별 경로 루트, 수정 제외 규칙

## Notes

- 시스템 경로(`/usr/bin`), URL, 이미 상대경로인 것은 수정하지 않음
- `fix-all` 전 반드시 `--dry-run`으로 미리보기 — 의도하지 않은 수정 방지
- 다른 스킬의 `sys.path.insert`는 `SkillPaths.get_script()` 호출로 대체하는 것을 권장
- Python 3.9 호환 필수 (`from __future__ import annotations`)
