#!/usr/bin/env python3
"""Catalog ↔ Resolver 정합성 감사 (SKILL_TAXONOMY.md 층2↔층3 드리프트 감지).

catalog(skills.json, SKILL-* namespace)의 각 항목이 resolver의 발견 결과와
같은 정본을 가리키는지 검사한다. macOS 한글 NFC/NFD 정규화를 처리한다.

드리프트 분류:
  PATH_MISSING     catalog path가 디스크에 없음
  NOT_DISCOVERED   resolver가 그 이름(디렉토리명·catalog name 모두)으로 발견 못함
  NOT_WINNER       발견은 됐지만 우선순위 승자가 catalog path와 다른 실체
  NAME_MISMATCH    catalog name ≠ SKILL.md frontmatter name (개명 드리프트)
  OK               정합

사용 (repo 루트에서):
    python3 skills/catalog_resolver_audit.py            # 사람용 표
    python3 skills/catalog_resolver_audit.py --json     # 기계용
    종료코드: 드리프트 있으면 1 (CI 게이트용)

stdlib만.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent           # <repo>/skills
DEFAULT_CATALOG = (HERE / "Skills-Create-Project" / "skill-creation-process"
                   / "references" / "catalog" / "skills.json")


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def skills_suffix(path: str) -> str | None:
    """경로에서 'skills' 컴포넌트 이후의 상대 suffix.

    catalog는 절대경로를 저장하므로 다른 clone/worktree에서 감사하면 절대경로가
    달라진다. 'skills/...' suffix가 같으면 같은 repo-상대 실체로 인정한다.
    """
    parts = Path(path).parts
    for i, p in enumerate(parts):
        if p == "skills":
            return "/".join(parts[i:])
    return None


def frontmatter_name(skill_md: Path) -> str | None:
    try:
        text = skill_md.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    m = re.match(r"\s*---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return None
    nm = re.search(r"(?m)^name:\s*(.+)$", m.group(1))
    return nfc(nm.group(1).strip()) if nm else None


def audit(catalog_path: Path):
    sys.path.insert(0, str(HERE))
    from resolve_skill import discover  # noqa: E402
    winners, _ = discover()

    cat = json.loads(catalog_path.read_text(encoding="utf-8"))
    rows = []
    for item in cat.get("items", []):
        key, name = item.get("key", "?"), nfc(item.get("name", ""))
        raw = item.get("path", "")
        d = Path(raw).parent if raw.endswith("SKILL.md") else Path(raw)
        row = {"key": key, "name": name, "dir": str(d)}

        if not d.exists():
            # catalog는 절대경로를 저장하므로 다른 clone/worktree/머신(CI 등)에서는
            # 그 경로가 없다. 곧바로 PATH_MISSING으로 단정하지 말고 'skills/' 이후
            # 상대 suffix를 현재 repo 루트 기준으로 재해석해 실존을 먼저 확인한다.
            suffix = skills_suffix(str(d))
            if suffix and (HERE.parent / suffix).exists():
                d = HERE.parent / suffix
            else:
                row["status"] = "PATH_MISSING"
                rows.append(row); continue

        real = nfc(os.path.realpath(d))
        dirname = nfc(d.name)
        fm = frontmatter_name(d / "SKILL.md")

        w = winners.get(name) or winners.get(dirname) or (winners.get(fm) if fm else None)
        same = False
        if w:
            same = nfc(w["real"]) == real
            if not same:
                # 다른 clone/worktree에서 실행된 경우: repo-상대 suffix로 재판정
                a, b = skills_suffix(real), skills_suffix(nfc(w["real"]))
                same = a is not None and a == b
        if not w:
            row["status"] = "NOT_DISCOVERED"
        elif not same:
            row["status"] = "NOT_WINNER"
            row["winner"] = w["path"]; row["winner_root"] = w["root"]
        elif fm and fm != name:
            row["status"] = "NAME_MISMATCH"
            row["frontmatter_name"] = fm
        else:
            row["status"] = "OK"
        rows.append(row)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="catalog<->resolver drift audit")
    ap.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    rows = audit(args.catalog)
    drift = [r for r in rows if r["status"] != "OK"]

    if args.json:
        print(json.dumps({"total": len(rows), "drift": len(drift),
                          "rows": rows}, ensure_ascii=False, indent=2))
    else:
        w = max((len(r["name"]) for r in rows), default=4)
        for r in rows:
            extra = r.get("winner") or r.get("frontmatter_name") or ""
            print(f"{r['status']:<16}{r['name']:<{w}}  {extra}")
        print(f"\nOK {len(rows)-len(drift)} / drift {len(drift)} (총 {len(rows)})")
    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
