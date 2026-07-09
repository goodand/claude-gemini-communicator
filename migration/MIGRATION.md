# 새 Mac 마이그레이션 — 심링크 토폴로지 복원

이 PC의 skill 발견 구조는 **정본 1곳(Desktop git repo) + 나머지는 전부 심링크 뷰**
(`~/.codex/skills`, `~/.claude/skills`, `~/control`, `~/agent`)다
([DATA_MANAGEMENT_PHILOSOPHY.md](../skills/DATA_MANAGEMENT_PHILOSOPHY.md)). 심링크
자체는 git 밖이라 `git clone`으로 안 옮겨진다. 이 키트가 그 심링크와, clone으로 안
돌아오는 소수의 비-git 콘텐츠를 재생성한다.

캡처 시점(2026-07-09) 실측: **심링크 50개**(.codex 33 · .claude 11 · control 4 · agent 2),
깨진 링크 0.

## 복원 순서 (신 Mac에서)

### 0. 전제
- Desktop 경로를 동일하게 유지: `~/Desktop/Project_____현재_진행중인/`.
  (한글 폴더명은 macOS에서 NFD로 분해될 수 있음 — resolver/audit은 NFC 정규화로 처리하나,
  clone 위치 폴더명은 구 Mac과 동일 바이트로 두는 게 안전.)
- 사용자명이 달라도 스크립트는 `$HOME` 기반이라 동작한다.

### 1. 정본 git repo clone
```bash
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
50개 심링크를 의존 순서(정본을 직접 가리키는 `~/.codex` → 그것을 가리키는 `~/.claude`/`agent`)로
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

## 심링크 목록 갱신 (구 Mac에서, 선택)
심링크 구성이 바뀌었으면 **구 Mac에서** 재캡처해 스크립트를 갱신한다:
```bash
python3 migration/gen_restore_symlinks.py   # restore-global-symlinks.sh 재생성
```
(신 Mac에는 캡처할 심링크가 없으므로 이 제너레이터는 반드시 구 Mac에서 실행.)

## git 밖이라 이 키트가 커버하지 '않는' 것
아래는 별도로 옮겨야 한다(이 repo에 없음):
- `~/.claude/projects/*/memory/` — 세션 메모리(MEMORY.md + 개별 파일)
- `~/HANDOFF_*.md` — 핸드오프 문서
- `~/.claude/settings.json`, `~/.codex/config.toml` 등 에이전트 설정
- API 키·`.env` (미러에서 제외됨)
