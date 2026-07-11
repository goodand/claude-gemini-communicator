# 새 Mac 마이그레이션 — 심링크 토폴로지 복원

이 PC의 skill 발견 구조는 **정본 1곳(Desktop git repo) + 나머지는 전부 심링크 뷰**
(`~/.codex/skills`, `~/.claude/skills`, `~/control`, `~/agent`)다
([DATA_MANAGEMENT_PHILOSOPHY.md](../skills/DATA_MANAGEMENT_PHILOSOPHY.md)). 심링크
자체는 git 밖이라 `git clone`으로 안 옮겨진다. 이 키트가 그 심링크와, clone으로 안
돌아오는 소수의 비-git 콘텐츠를 재생성한다.

캡처 시점(2026-07-11) 실측: **심링크 95개**(.codex/skills 33 · .claude/skills 11 ·
.claude/agents 45 · control 4 · agent 2), 깨진 링크 0. (.claude/agents = 에이전트 팀
리소스 뷰 — owners/specialists/codex_agents 등, 대부분 이 repo를 가리킴.)

## 복원 순서 (신 Mac에서)

### 0. 전제
- Desktop 경로를 동일하게 유지: `~/Desktop/Project_____현재_진행중인/`.
  (한글 폴더명은 macOS에서 NFD로 분해될 수 있음 — resolver/audit은 NFC 정규화로 처리하나,
  clone 위치 폴더명은 구 Mac과 동일 바이트로 두는 게 안전.)
- 사용자명이 달라도 스크립트는 `$HOME` 기반이라 동작한다.

### 1. 정본 git repo clone
```bash
mkdir -p ~/Desktop/Project_____현재_진행중인
cd ~/Desktop/Project_____현재_진행중인
git clone <origin>/claude-gemini-communicator
git clone <origin>/my-image-parser
git clone <origin>/narrative-ai
git clone <origin>/my-second-identity
git clone <origin>/vscode-markdown-review-surface
```
`git clone`은 각 repo의 **기본 브랜치**만 가져온다. 이번 마이그레이션에서 보존한
작업 브랜치는 원격에 있으니 필요 시 별도 체크아웃:
- communicator `wip/auto-hooks-flag-and-family-routing` (Desktop 전용 유일본 봉인본),
  `feat/skill-runtime-portability-mac`, tag `archive/skill-v0-import-baseline`.

### 2. 비-git 콘텐츠 복원
```bash
bash ~/Desktop/Project_____현재_진행중인/claude-gemini-communicator/migration/restore-content.sh
```
- `~/skills/{destructive-cleanup-preflight, workspace-control-recovery}` ← communicator `external/home` 미러 (캡처 시 diff 0)
- `~/.codex/skills/pptx` ← communicator `external/codex/pptx` 미러 (diff 0)
- `~/agent/skills/taste-skill` ← `github.com/Leonxlnx/taste-skill` clone
  (구 Mac의 미커밋 2건은 복원 안 됨 — 필요하면 구 Mac에서 먼저 커밋/스태시 백업)

### 3. 심링크 재생성
```bash
bash ~/Desktop/Project_____현재_진행중인/claude-gemini-communicator/migration/restore-global-symlinks.sh
```
95개 심링크를 의존 순서(정본을 직접 가리키는 `~/.codex` → 그것을 가리키는 `~/.claude`/`agent`)로
재생성한다. idempotent(재실행 안전), 타겟이 없으면 해당 링크만 SKIP.

### 4. 검증
```bash
cd ~/Desktop/Project_____현재_진행중인/claude-gemini-communicator
python3 skills/resolve_skill.py list          # 발견 인벤토리(이름·루트)
python3 skills/resolve_skill.py conflicts      # 이름 충돌 클래스
python3 skills/catalog_resolver_audit.py       # 층2↔층3 drift 0 확인
python3 skills/integration-gate/run_integration_gate.py   # PASS_WITH_WARNING 기대
```
`resolve_skill.py`는 절대경로가 아니라 repo-상대 구조로 발견하므로, clone 위치가
같으면 구 Mac과 동일 결과가 나와야 한다.

한 방에 검증:
```bash
bash migration/check.sh   # 가정 원장의 자동 probe 전부 (리허설·gate·drift·이식성)
```

## 가정 원장 (지속 검증)

무엇을 "당연하다"고 두고 진행하는지와 그 확인 명령을 [ASSUMPTIONS.md](ASSUMPTIONS.md)에
표로 둔다. probe 없는 줄이 곧 다음 unknown이다. 자동 probe는 `check.sh`가 집계하고,
'언제 도나'(트리거)만 새 머신에서 로컬 cron/launchd 한 줄로 등록한다(ASSUMPTIONS.md 하단).
`rehearse.sh`는 합성 `$HOME`으로 복원을 미리 돌려 사용자명/경로 독립을 이사 전에 확인한다.

## 심링크 목록 갱신 (구 Mac에서, 선택)
심링크 구성이 바뀌었으면 **구 Mac에서** 재캡처해 스크립트를 갱신한다:
```bash
python3 migration/gen_restore_symlinks.py   # restore-global-symlinks.sh 재생성
```
(신 Mac에는 캡처할 심링크가 없으므로 이 제너레이터는 반드시 구 Mac에서 실행.)

## 무결성 가드 (path_integrity_guard.py)

심링크 훼손 패턴("이름=계약으로 개명하는데 참조는 절대경로로 고정")을 예방·진단하는
읽기 전용 도구. 마이그레이션 전후 검증에 쓴다.

```bash
G=migration/path_integrity_guard.py
python3 $G broken                # 끊긴 심링크 전수 (CI 가드: 있으면 exit 1)
python3 $G candidates            # 끊긴 링크별 복구가능성 REPAIRABLE/AMBIGUOUS/ORPHAN
python3 $G external <경계>        # <경계> 밖 의존 = 이식 시 함께 옮길 것 (freeze)
python3 $G rel-candidates        # abs→rel 변환 후보: FULL_WIN(개명내성 획득) 등 분류
python3 $G inbound <폴더>         # <폴더> 개명/이동 전 폭발 반경 (그 안 가리키는 링크)
python3 $G verbose-risk          # '_____' 서술형 폴더 의존 링크 (개명 시 대량 훼손)
# 옵션: --json (서브커맨드 앞에)
```

**개명/이동 전에는 반드시** `inbound <그 폴더>`로 폭발 반경을 먼저 본다 — 이게 이
PC의 1위 훼손 원인(폴더 개명)을 막는 가드다. 2026-07-09 실측: 살아있는 링크 다수가
`Project_____현재_진행중인` 한 폴더에 의존 → 이 폴더 개명은 대량 훼손을 부른다.

reference 도구 subflow와의 대응: `broken`+`candidates` = fixMyRefs(broken→후보검색→
판정), `external` = obsidian-export freeze(외부 resource 이식), `rel-candidates` =
brandt/symlinks(abs→rel 변환성), `inbound`/`verbose-risk` = 개명 전 예방(기존 도구엔
드문, 이 PC 특유의 가드).

`rel-candidates` 판정 뜻: **FULL_WIN**은 공통 조상이 서술형 폴더보다 깊어 상대화하면
상위 폴더 개명에도 안 깨지는 링크(진짜 실익). **USERNAME_ONLY**는 상대화해도 HOME까지
등반하거나 서술형 폴더가 남아 실익이 사용자명 독립뿐 — 이건 이미 `$HOME` 치환이 하므로
변환 불필요. 2026-07-10 실측(.cache 등 휘발성 prune 후): FULL_WIN 125(대부분 Desktop
트리 내부 상호참조로, `Project_____현재_진행중인` 개명 폭탄을 실제로 해제; intra-repo만
안전 대상), USERNAME_ONLY 105.

## git 밖이라 이 키트가 커버하지 '않는' 것
아래는 별도로 옮겨야 한다(이 repo에 없음):
- `~/.claude/projects/*/memory/` — 세션 메모리(MEMORY.md + 개별 파일)
- `~/HANDOFF_*.md` — 핸드오프 문서
- `~/.claude/settings.json`, `~/.codex/config.toml` 등 에이전트 설정
- API 키·`.env` (미러에서 제외됨)
