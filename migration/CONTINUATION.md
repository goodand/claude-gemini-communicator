# 이어서 하기 (Continuation) — git repo만 보고 작업을 잇는 진입점

> 세션 메모리·`~/HANDOFF_*.md`·`~/.claude`는 이 머신에만 있고 clone에 안 딸려온다.
> **이 문서가 repo 안의 유일한 정본 기록**이다. 새 세션은 여기부터 읽으면 된다.
> 최종 갱신: 2026-07-10.

## 0. 한눈에

- **main** — skill catalog 통합 완료 + 마이그레이션 키트까지 반영된 안정 기준.
- **열린 작업** — 없음(이 문서가 main에 올라오면서 PR #4까지 닫힘). 남은 건 아래 §3 백로그.
- **검증 한 방** — `bash migration/check.sh` → `ALL GREEN`이어야 정상.

## 1. 완료된 것 (main에 반영됨)

- **skill catalog 통합** (PR #2): PC 전역 skill 미러 + 발견/분류 3층 체계
  (`skills/SKILL_DISCOVERY.md`, `SKILL_TAXONOMY.md`, `resolve_skill.py`,
  `catalog_resolver_audit.py`, `verification-router/`) + `_stale` 격리.
- **integration gate** (PR #2): `skills/integration-gate/` 4-subflow, CI-gateable.
- **Gemini 리뷰 수정** (PR #3): depsolve/mapper analyzer 정확도 7건 + 재리뷰 2건.
- **마이그레이션 키트 + 무결성 가드 + 지속검증** (PR #4): 아래 §2 파일들.
- **resolver 이식성**: `resolve_skill.py`의 사용자명 하드코딩 3곳 → `$HOME` 기반.

## 2. 마이그레이션 키트 (`migration/`)

| 파일 | 용도 | 실행 위치 |
|---|---|---|
| `MIGRATION.md` | 새 Mac 복원 전체 절차(clone→콘텐츠→심링크→검증) | 참조 |
| `gen_restore_symlinks.py` | 살아있는 심링크 캡처→복원 스크립트 생성 | **구 Mac** |
| `restore-global-symlinks.sh` | 심링크 50개 재생성($HOME 기반) | 새 Mac |
| `restore-content.sh` | 비-git 콘텐츠 복원(미러 copy + taste-skill clone) | 새 Mac |
| `path_integrity_guard.py` | 6-subflow 무결성 진단(아래) | 상시 |
| `ASSUMPTIONS.md` | 가정 원장(믿음+probe+기대). probe 없는 줄=다음 unknown | 상시 |
| `check.sh` | 자동 probe 집계, 실패 시 exit 1 | 상시(로컬 cron 등록) |
| `rehearse.sh` | 합성 `$HOME`으로 이식성 사전 검증 | 이사 전 |

가드 6-subflow: `broken`(끊긴 링크) · `candidates`(복구가능성) · `external`(freeze 외부의존)
· `rel-candidates`(abs→rel 변환성) · `inbound <폴더>`(개명 전 폭발반경) · `verbose-risk`.

## 3. 백로그 (우선순위 · 구체 명령)

### A. WIP 재적용 (다음 큰 작업)
`wip/auto-hooks-flag-and-family-routing` 브랜치(`3f802b6`, origin에 push됨)에 Desktop
전용 유일본이 봉인돼 있다. 여기서 **선별해서** main으로 정식 반영한다(전량 아님 —
legacy/backups/캐시는 제외):
- `auto_hooks_enabled` kill-switch (config.json + hook_auto_task.py + hook_stop.py)
- SKILL.md 6종의 owner-family/specialist 라우팅 섹션(agent-parser, codex-user-context,
  cross-agent-bridge, gemini-cli-context, gemini-reviewer, skill-creation-process)
- 신규 skill 5종(semantic-slice-mapper, dependency-graph-analyzer, skill-acceptance-gate,
  design-planning-orchestrator, template)
- `.codex/agents/*.toml`, `skills/--help-routing.md`
```bash
git log --stat wip/auto-hooks-flag-and-family-routing -1   # 봉인 내용 확인
git checkout wip/auto-hooks-flag-and-family-routing -- <선별 경로>   # 필요분만 꺼내기
```
> 이 작업이 끝나면 아래 #2 unknown(rescue-7 심링크)도 함께 초록이 된다.

### B. "아직 probe 없는" unknown 3개 (전략 = triage: 싸고 물릴 것부터)
1. **#3 남은 하드코딩** — *지금, 값쌈.* 실행코드는 이미 clean. `check.sh`에 5번째
   probe 추가: `git grep -nE "/Users/[^/]+/(Desktop|control|agent)" -- '*.py' '*.sh'`
   가 비어야 함(현재 통과).
2. **#2 rescue-7 심링크** — *red 추적.* `~/.claude/agents/_resources`의 7개가 지금
   BROKEN(wip에만 콘텐츠 존재). A(WIP 재적용)의 done-definition으로 쓴다:
   ```bash
   for p in ~/.claude/agents/_resources/codex_agents/*.toml \
            ~/.claude/agents/_resources/guides/help-routing-template.md \
            ~/.claude/agents/_resources/owners/architect/design-planning-orchestrator; do
     [ -e "$p" ] && echo OK || echo BROKEN $p; done
   ```
3. **#1 Obsidian vault 무결성** — *보류(비쌈·불확실).* 심링크층은 `external <vault>`로
   재사용 가능하나, 마크다운 wikilink/embed(`[[note]]`/`![[img]]`)는 파서 신규 필요.
   vault 이사가 실제 안건이 될 때 scope부터.

### C. 상시 검증 트리거 등록 (새 머신 1회)
로직은 git으로 왔으니 트리거만: `ASSUMPTIONS.md` 하단의 cron/launchd 한 줄 등록.

## 4. 브랜치·태그 지도

| ref | 뜻 | 상태 |
|---|---|---|
| `main` | 안정 기준(모든 통합 반영) | 정본 |
| `wip/auto-hooks-flag-and-family-routing` | Desktop 전용 유일본 봉인(§3-A 재적용 대기) | 보존, **삭제 금지** |
| `archive/skill-v0-import-baseline` (tag) | v0 baseline 보존 | 아카이브 |

## 5. git 밖이라 여기 없는 것 (새 머신에서 따로 챙길 것)

- **세션 메모리** `~/.claude/projects/*/memory/` — Claude 로컬. 필요하면 수동 복사.
- **`~/HANDOFF_skill-branch-integration_at2026-07-09.md`** — 이 문서의 더 상세한 원본.
- **전역 심링크 50개 + 비-git 콘텐츠** — `migration/restore-*.sh`로 복원(§2).
- **rescue-7 타겟 콘텐츠** — `wip/...` 브랜치에 있음(§3-A로 반영).
