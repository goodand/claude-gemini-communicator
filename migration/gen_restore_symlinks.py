#!/usr/bin/env python3
"""현재 Mac의 git-외부 심링크를 캡처해 새 Mac용 복원 스크립트를 생성한다.

**구 Mac에서 실행**한다(살아있는 심링크를 읽어야 하므로). 결과물
`restore-global-symlinks.sh`가 신 Mac에서 심링크를 재생성한다.

원리(DATA_MANAGEMENT_PHILOSOPHY.md): 정본은 Desktop git repo 하나, 나머지
위치(~/.codex, ~/.claude, ~/control, ~/agent)는 전부 심링크 뷰. 심링크 자체는
git 밖이라 clone으로 안 옮겨지므로 여기서 캡처해 재생성한다.

- link/target의 홈 접두어를 $HOME으로 치환 → 신 Mac 사용자명이 달라도 동작.
- 경로/타겟은 NFC로 정규화 → macOS가 NFD로 돌려주는 한글 경로와의 혼재 방지.
- 의존 순서(정본을 직접 가리키는 ~/.codex 먼저)로 정렬.
- 캡처 시점 깨진 링크는 제외하고 주석으로 기록.
"""
import os
import unicodedata
from pathlib import Path

HOME = Path.home()
ME = str(HOME)
HERE = Path(__file__).resolve().parent
# ~/.claude/agents(에이전트 팀 리소스 뷰)는 owners/specialists 등 depth-4 링크가
# 있어 두 루트로 스캔한다: walk가 각 루트에서 3단계까지만 보므로 _resources를
# 별도 루트로도 넣어 depth-4를 포착. 두 루트가 겹치는 링크는 collect()가 dedup.
SCAN = [HOME / ".codex" / "skills", HOME / ".claude" / "skills",
        HOME / ".claude" / "agents", HOME / ".claude" / "agents" / "_resources",
        HOME / "control", HOME / "agent"]


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def homeify(p: str) -> str:
    return p.replace(ME, "$HOME", 1) if p.startswith(ME) else p


def order_key(link: str) -> int:
    if "/.codex/skills/" in link:
        return 0        # 정본 repo/~skills를 직접 가리킴 → 먼저
    if "/control/" in link:
        return 1
    if "/.claude/skills/" in link:
        return 2        # ~/.codex를 가리킴 → 뒤
    if "/.claude/agents/" in link:
        return 3        # 대부분 repo 직접(git, 항상 존재), m5만 ~/.codex/skills 의존 → 0 이후
    return 4            # ~/agent → control/.codex 의존


def collect():
    links, broken, seen = [], [], set()
    for root in SCAN:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            for name in list(dirnames) + filenames:
                p = Path(dirpath) / name
                if p.is_symlink():
                    # os.walk/readlink가 돌려주는 한글 경로는 NFD일 수 있어
                    # 스크립트 안에서 NFC/NFD가 섞이지 않게 정규화한다.
                    key = nfc(str(p))
                    if key in seen:      # 겹치는 SCAN 루트(agents/_resources)가 만드는 중복 제거
                        continue
                    seen.add(key)
                    tgt = nfc(os.readlink(p))
                    (links if os.path.exists(p) else broken).append((key, tgt))
            if Path(dirpath) != root and Path(dirpath).parent != root:
                dirnames[:] = []
    links.sort(key=lambda lt: (order_key(lt[0]), lt[0]))
    return links, broken


def render(links, broken) -> str:
    out = [
        "#!/usr/bin/env bash",
        "# 전역 skill 심링크 복원 — 새 Mac 마이그레이션용. (gen_restore_symlinks.py 생성물)",
        "# 선행조건: MIGRATION.md의 1~2단계(repo clone + 비-git 콘텐츠 복원)를 먼저 끝낼 것.",
        "# $HOME 기반이라 사용자명이 달라도 동작. idempotent(재실행 안전).",
        "set -euo pipefail",
        "",
        "link() {  # link <target> <linkpath>",
        '  local target="$1" linkpath="$2" check="$1"',
        "  # 상대 타겟은 링크가 놓일 디렉토리 기준으로 실존 확인 (CWD 무관)",
        '  if [[ "$target" != /* ]]; then check="$(dirname "$linkpath")/$target"; fi',
        '  if [ ! -e "$check" ]; then echo "SKIP(타겟없음) $linkpath -> $target"; return; fi',
        '  mkdir -p "$(dirname "$linkpath")"',
        '  rm -rf "$linkpath"',
        '  ln -s "$target" "$linkpath"',
        '  echo "OK   $linkpath"',
        "}",
        "",
    ]
    titles = {0: "~/.codex/skills → 정본 repo(Desktop) / ~/skills",
              1: "~/control/patterns → communicator",
              2: "~/.claude/skills → ~/.codex/skills",
              3: "~/.claude/agents/_resources → communicator repo (+ m5는 ~/.codex/skills)",
              4: "~/agent → ~/control, ~/.codex"}
    cur = None
    for link, tgt in links:
        grp = order_key(link)
        if grp != cur:
            out.append(f"# ── {titles[grp]} ──")
            cur = grp
        out.append(f'link "{homeify(tgt)}" "{homeify(link)}"')
    out += ["", f'echo "복원 완료: {len(links)}개 심링크"']
    if broken:
        out += ["", "# 캡처 시점에 이미 깨져 있던 링크(복원 제외):"]
        out += [f"#   {homeify(l)} -> {homeify(t)}" for l, t in broken]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    links, broken = collect()
    dst = HERE / "restore-global-symlinks.sh"
    dst.write_text(render(links, broken), encoding="utf-8")
    dst.chmod(0o755)
    print(f"생성: {dst}")
    print(f"심링크 {len(links)}개, 깨진 것 {len(broken)}개")
