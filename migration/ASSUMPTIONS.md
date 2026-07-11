# 가정 원장 (Assumption Ledger)

"우리가 참이라 치고 진행하는 것" + 각각을 확인하는 **probe(명령)** + 기대값 + 마지막 확인일.

> **규칙**: probe 없는 줄이 곧 다음 unknown이다. 무언가를 "당연히 그렇다"고 두면
> 여기 한 줄로 적고 probe를 붙인다. probe를 못 붙이면, 그게 아직 못 보는 곳이다.

**왜 repo에 두나 (세션·에이전트·머신 독립)**: 세션 메모리·`~/.claude`·이 대화는
새 Mac으로 안 따라온다. 정본은 push되는 이 repo뿐이다. probe는 순수 shell/stdlib라
Claude·Codex·Gemini·사람·CI 누구나, 어느 머신에서든 실행된다. 경로는 `$HOME`/repo-상대라
사용자명이 달라도 동작한다.

자동화 가능한 probe는 한 번에: `bash migration/check.sh` (하나라도 실패 시 exit 1).

| # | 가정 | probe | 기대 | 마지막 확인 | check.sh |
|---|---|---|---|---|---|
| 1 | 복원 키트가 다른 `$HOME`(=다른 사용자명)에서 이식 가능 | `bash migration/rehearse.sh` | PASS (50/50, 누수 0) | 2026-07-10 | ✓ |
| 2 | skills-catalog repo probe 일괄 (drift·gate·하드코딩 — 2026-07-11 분리로 catalog repo 이관) | `bash ../skills-catalog/check.sh` | ALL GREEN, exit 0 | 2026-07-11 | ✓ |
| 5 | 비-git 콘텐츠가 catalog 미러와 동일(clone으로 복원 가능) | `diff -rq ~/skills/destructive-cleanup-preflight ../skills-catalog/skills/external/home/destructive-cleanup-preflight` | 차이 0 | 2026-07-10 (구 Mac) | 수동 |
| 6 | 끊긴 심링크 수 (관찰 — gate 아님) | `python3 migration/path_integrity_guard.py broken` | 베이스라인 44; 증가하면 조사 | 2026-07-10 | 관찰 |
| 7 | 외부 의존(freeze) 반경 (관찰) | `python3 migration/path_integrity_guard.py external ~/Desktop/Project_____현재_진행중인` | 베이스라인 12; 증가하면 조사 | 2026-07-10 | 관찰 |

## 아직 probe 없는 줄 = 알려진 unknown (probe를 붙이는 게 다음 할 일)

- 새 Mac에서 Obsidian vault 내부/외부 링크가 실제로 무결한가? — vault 전용 probe 필요
- resolve_skill.py 외에 실행경로에 남은 하드코딩이 더 있는가? — repo 전역 `/Users/` 코드 스캔 probe

### 해소됨
- ~~`~/.claude/agents/_resources`의 rescue-깨진 7건~~ — **해소(2026-07-11)**: (a) 타겟은
  §3-A 재적용으로 존재하게 됨, (b) 심링크 자체도 `~/.claude/agents`(+`_resources`)를
  `gen_restore_symlinks.py` SCAN에 추가해 `restore-global-symlinks.sh`가 재생성(agents 45개
  포함, 총 95개, broken 0). 새 Mac에서도 키트만으로 복원됨.

## 트리거(언제 도나) — 머신마다 로컬 등록

로직(`check.sh`)은 git으로 이동, **트리거만** 새 Mac에서 한 줄 등록한다(로컬 launchd/cron 택1).

cron (매일 09:00):
```cron
0 9 * * * cd "$HOME/Desktop/Project_____현재_진행중인/claude-gemini-communicator" && bash migration/check.sh >> "$HOME/.cache/skill-check.log" 2>&1
```

launchd (`~/Library/LaunchAgents/com.jaehyuntak.skillcheck.plist`, 매일 09:00):
`ProgramArguments = [/bin/bash, -lc, cd ~/Desktop/.../claude-gemini-communicator && bash migration/check.sh]`,
`StartCalendarInterval = {Hour:9, Minute:0}` 후 `launchctl load`.
