#!/usr/bin/env bash
# 비-git 실제 콘텐츠 복원 — 심링크 복원 '전에' 실행.
# 심링크가 가리킬 대상 중 git clone으로 안 돌아오는 것들을 준비한다.
# 대부분은 communicator repo의 external 미러에서 복사(캡처 시점 diff 0 확인).
# taste-skill만 별도 origin에서 clone.
set -euo pipefail

REPO="$HOME/Desktop/Project_____현재_진행중인/claude-gemini-communicator"
EXT="$REPO/skills/external"

copy_from_mirror() {  # copy_from_mirror <mirror-subpath> <dest>
  local src="$EXT/$1" dst="$2"
  if [ ! -d "$src" ]; then echo "SKIP(미러없음) $1"; return; fi
  # -L 병행: dst가 '깨진 심링크'면 -e가 false라 cp가 그 위에 실행되는 것을 방지
  if [ -e "$dst" ] || [ -L "$dst" ]; then echo "이미 존재 $dst"; return; fi
  mkdir -p "$(dirname "$dst")"
  cp -R "$src" "$dst"
  echo "OK   $dst  ← 미러 $1"
}

# 1) ~/skills home-global 정본 2개 (external/home 미러와 동일)
copy_from_mirror "home/destructive-cleanup-preflight" "$HOME/skills/destructive-cleanup-preflight"
copy_from_mirror "home/workspace-control-recovery"    "$HOME/skills/workspace-control-recovery"

# 2) ~/.codex/skills/pptx 실체 (external/codex/pptx 미러와 동일)
copy_from_mirror "codex/pptx" "$HOME/.codex/skills/pptx"

# 3) taste-skill — vendored 외부 repo (남의 repo, 미러 안 함). origin에서 clone.
TASTE="$HOME/agent/skills/taste-skill"
if [ -d "$TASTE/.git" ]; then
  echo "이미 존재 $TASTE"
elif [ -e "$TASTE" ] || [ -L "$TASTE" ]; then
  # 이전 실행 실패 잔재 등 — 비어있지 않으면 clone이 fatal로 죽으므로 건너뛰고 알림
  echo "경고: $TASTE 경로가 존재하나 git repo가 아님 — 확인 후 정리하고 재실행"
else
  mkdir -p "$(dirname "$TASTE")"
  git clone https://github.com/Leonxlnx/taste-skill.git "$TASTE"
  echo "OK   $TASTE  ← github.com/Leonxlnx/taste-skill (구 Mac의 미커밋 2건은 복원 안 됨)"
fi

echo "콘텐츠 복원 완료. 이제 restore-global-symlinks.sh 실행."
