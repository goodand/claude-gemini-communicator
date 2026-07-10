# 이어서 하기 (Continuation) — git repo만 보고 작업을 잇는 진입점

> 세션 메모리·`~/HANDOFF_*.md`·`~/.claude`는 이 머신에만 있고 clone에 안 딸려온다.
> **이 문서가 repo 안의 유일한 정본 기록**이다. 새 세션은 여기부터 읽으면 된다.
> 최종 갱신: 2026-07-11.

## 0. 한눈에

- **main** — skill catalog 통합 + 마이그레이션 키트 + **§3-A WIP 선별 재적용**까지 반영된 안정 기준.
- **열린 작업** — 없음. 남은 건 아래 §3 백로그(§3-A는 완료, §3-D에 결정 기록).
- **검증 한 방** — `bash migration/check.sh` → `ALL GREEN`이어야 정상.

## 1. 완료된 것 (main에 반영됨)

- **skill catalog 통합** (PR #2): PC 전역 skill 미러 + 발견/분류 3층 체계
  (`skills/SKILL_DISCOVERY.md`, `SKILL_TAXONOMY.md`, `resolve_skill.py`,
  `catalog_resolver_audit.py`, `verification-router/`) + `_stale` 격리.
- **integration gate** (PR #2): `skills/integration-gate/` 4-subflow, CI-gateable.
- **Gemini 리뷰 수정** (PR #3): depsolve/mapper analyzer 정확도 7건 + 재리뷰 2건.
- **마이그레이션 키트 + 무결성 가드 + 지속검증** (PR #4): 아래 §2 파일들.
- **resolver 이식성**: `resolve_skill.py`의 사용자명 하드코딩 3곳 → `$HOME` 기반.
- **§3-A WIP 선별 재적용** (merge `eeef2f1` → push `c54575f`, 2026-07-10): kill-switch +
  SKILL.md 라우팅 6종 + 신규 skill(semantic-slice-mapper, design-planning-orchestrator) +
  acceptance-gate refs + template + `.codex/agents` = 35파일. rescue-7 심링크 7/7 green.
  main 나중수정본은 merge-base 3-way 판정으로 보존(회귀 0).

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

### A. WIP 재적용 — ✅ 완료 (2026-07-10, merge `eeef2f1` → push `c54575f`)
선별 35파일 반영: kill-switch(config+hooks), SKILL.md 라우팅 6종, `.codex/agents` 5종+config,
`--help-routing.md`, 신규 skill. "신규 skill 5종"은 실체 확인 결과 로드가능 2종만
(semantic-slice-mapper, design-planning-orchestrator — 반영); skill-acceptance-gate=references만·
template=조각 1파일(둘 다 반영); dependency-graph-analyzer=DEPRECATED+legacy뿐(제외, depsolve로 대체).
방법론: wip이 main보다 2 behind → M파일을 merge-base 3-way 분류(WIP_ONLY/MAIN_ONLY/BOTH),
BOTH 8개(resolve_skill.py, depsolve-analyzer/* 등 PR#3/#4 수정본)는 불변 유지 → 회귀 0.
`auto_hooks_enabled`는 repo 본연 동작 위해 별도 커밋(`c54575f`)으로 `true`.

### B. "아직 probe 없는" unknown 3개 (전략 = triage: 싸고 물릴 것부터)
1. **#3 남은 하드코딩** — *지금, 값쌈.* 실행코드는 이미 clean. `check.sh`에 5번째
   probe 추가: `git grep -nE "/Users/[^/]+/(Desktop|control|agent)" -- '*.py' '*.sh'`
   가 비어야 함(현재 통과).
2. **#2 rescue-7 심링크** — ✅ 해소(2026-07-10, §3-A 반영으로 7/7 OK). 아래는 회귀 감지 probe로 유지:
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

### D. 결정 기록 (2026-07-11)
- **taste-skill 미러 정책 = vendored 유지·미러 제외**: `~/agent/skills/taste-skill`은 타인
  repo clone(`github.com/Leonxlnx/taste-skill`)이라 무단 미러 대신 출처 링크만 남김 —
  `skills/SKILL_DISCOVERY.md` §2에 기록. "external=미러, 출처가 정본" 원칙.
- **wip의 rename 90건(`external/_stale/…`→`external/…`) = 폐기**: 전부 R100(내용 동일),
  wip 미러 커밋 7분 뒤 main이 `_stale` 격리 도입(`aae8fdb`) — 격리 직전 옛 배치의 잔상이지
  제안이 아님. 적용 시 정본 중복 8종 부활·policy_sync 위반이라 미적용.
- 이 두 결정("미러=출처가 정본", "_stale=격리 유지")은 향후 **skills/ 독립 repo 분리** 시
  `external/` 취급의 선례가 된다.
- 남은 외부-repo 백로그(이 repo 밖): msi 로컬 skill 2종(repair-rag-artifact-contract,
  trace-claude-session-memory)을 my-second-identity main에 커밋 — HANDOFF §3-B 참조.

## 4. 브랜치·태그 지도

| ref | 뜻 | 상태 |
|---|---|---|
| `main` | 안정 기준(모든 통합 반영) — **유일한 브랜치** | 정본 |
| `archive/wip-desktop-snapshot` (tag) | Desktop 전용 스냅샷 `3f802b6` 봉인. §3-A 선별분은 main에 반영됐고, 잔여=legacy/backups/아티팩트/옛 미러배치(§3-D 폐기 결정) | 아카이브(wip 브랜치는 2026-07-11 tag 봉인 후 삭제) |
| `archive/skill-v0-import-baseline` (tag) | v0 baseline 보존 | 아카이브 |

## 5. git 밖이라 여기 없는 것 (새 머신에서 따로 챙길 것)

- **세션 메모리** `~/.claude/projects/*/memory/` — Claude 로컬. 필요하면 수동 복사.
- **`~/HANDOFF_skill-branch-integration_at2026-07-09.md`** — 이 문서의 더 상세한 원본.
- **전역 심링크 50개 + 비-git 콘텐츠** — `migration/restore-*.sh`로 복원(§2).
- **rescue-7 타겟 콘텐츠** — main에 반영됨(§3-A 완료). 과거 전체 스냅샷은 `archive/wip-desktop-snapshot` tag.
