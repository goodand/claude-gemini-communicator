#!/usr/bin/env python3
"""Path Integrity Guard — 심링크 훼손 패턴을 예방/진단한다.

배경: 이 PC는 "이름=계약(개명으로 뜻을 다듬음)" + "정본 1곳, 나머지는 절대경로
심링크 뷰"라는 두 원칙을 함께 쓴다(DATA_MANAGEMENT_PHILOSOPHY.md). 살아있는
이름 ↔ 고정을 가정하는 참조가 충돌해, 개명·이동·재구성·정리 때마다 옛 이름을
가리키던 심링크가 조용히 끊긴다. 이 도구는 그 세 국면을 커버한다:

  broken       현재 끊긴(dangling) 심링크 전수 — 사후 진단/CI 가드
  candidates   끊긴 링크마다 같은 basename의 후보를 검색해 복구가능성 판정
               (fixMyRefs subflow: REPAIRABLE/AMBIGUOUS/ORPHAN)
  external     <경계> 밖을 가리키는 링크 = 이식 시 함께 옮겨야 할 외부 의존
               (obsidian-export freeze subflow: 자기완결성 검증)
  rel-candidates 절대경로 링크의 상대경로 변환 후보 판정 — 변환이 어떤 위험을
               제거하는지로 분류 (brandt/symlinks subflow: FULL_WIN/USERNAME_ONLY/
               KEEP_ABSOLUTE/ALREADY_REL). 읽기 전용(변환은 하지 않음).
  inbound      <폴더>를 개명/이동하기 '전에' 그 안을 가리키는 링크 목록(폭발 반경)
  verbose-risk '_____' 서술형 폴더에 의존하는 살아있는 링크(미래 개명 시 대량 훼손)

전부 읽기 전용. stdlib만.

사용:
  python3 migration/path_integrity_guard.py broken [ROOT ...]
  python3 migration/path_integrity_guard.py inbound <FOLDER> [ROOT ...]
  python3 migration/path_integrity_guard.py verbose-risk [ROOT ...]
  옵션: --json
종료코드: broken/verbose-risk는 항목 있으면 1(가드용), inbound는 항상 0.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

HOME = Path.home()

# 기본 스캔 루트: 정본 트리 + git-외부 뷰 계층. (필요시 인자로 덮어씀)
DEFAULT_ROOTS = [
    HOME / "Desktop" / "Project_____현재_진행중인",
    HOME / ".codex", HOME / ".claude", HOME / "control",
    HOME / "agent", HOME / "skills",
]
# 스캔에서 건너뛸 디렉토리 이름(노이즈/속도). .git은 내부에 우리가 볼 심링크가
# 없고 loose object가 많아 반드시 prune(안 하면 repo마다 수만 파일 walk).
PRUNE = {".git", "node_modules", ".venv", "venv", "__pycache__",
         ".mypy_cache", ".pytest_cache", ".ruff_cache",
         # 휘발성 빌드/툴 캐시 — 여기 심링크는 재생성물이라 분석 노이즈
         # (uv environments-v2/builds-v0가 .cache/uv 아래에 있음)
         ".cache", ".history"}


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def iter_symlinks(roots):
    """roots 아래 모든 심링크를 (link, raw_target, abs_target)로 산출.

    abs_target: 상대 링크는 링크 위치 기준으로 정규화한 절대경로(존재 여부 무관).
    """
    for root in roots:
        root = Path(root)
        if not root.exists() and not root.is_symlink():
            continue
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            dirnames[:] = [d for d in dirnames if d not in PRUNE]
            for name in list(dirnames) + filenames:
                p = os.path.join(dirpath, name)
                if os.path.islink(p):
                    raw = os.readlink(p)
                    ab = raw if os.path.isabs(raw) else os.path.normpath(
                        os.path.join(os.path.dirname(p), raw))
                    yield p, raw, ab


def homeify(s: str) -> str:
    h = str(HOME)
    return s.replace(h, "~", 1) if s.startswith(h) else s


def cmd_broken(roots, as_json):
    rows = []
    for link, raw, ab in iter_symlinks(roots):
        if not os.path.exists(link):  # dangling
            rows.append({"link": link, "target": raw, "abs_target": ab})
    if as_json:
        print(json.dumps({"count": len(rows), "broken": rows},
                         ensure_ascii=False, indent=2))
    else:
        for r in rows:
            print(f"BROKEN  {homeify(r['link'])}  ->  {homeify(r['target'])}")
        print(f"\n끊긴 심링크: {len(rows)}개")
    return 1 if rows else 0


def cmd_candidates(roots, as_json):
    """fixMyRefs subflow: 끊긴 링크의 target basename을 스캔 루트에서 검색해
    복구 후보 유무로 복구가능성을 판정한다. 한 번의 walk로 (끊긴 링크 수집 +
    basename 인덱스 구축)을 동시에 한다.
    """
    index = defaultdict(list)   # nfc(basename) -> [실존 경로]
    broken = []
    for root in roots:
        root = Path(root)
        if not root.exists() and not root.is_symlink():
            continue
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            dirnames[:] = [d for d in dirnames if d not in PRUNE]
            for name in list(dirnames) + filenames:
                p = os.path.join(dirpath, name)
                if os.path.islink(p):
                    raw = os.readlink(p)
                    ab = raw if os.path.isabs(raw) else os.path.normpath(
                        os.path.join(os.path.dirname(p), raw))
                    if not os.path.exists(p):
                        broken.append((p, raw, ab))
                    continue  # 심링크 자신은 후보 인덱스에 넣지 않음
                index[nfc(name)].append(p)

    rows = []
    for link, raw, ab in broken:
        bn = nfc(os.path.basename(ab.rstrip("/")))
        cands = [c for c in index.get(bn, []) if c != link]
        cls = "ORPHAN" if not cands else ("REPAIRABLE" if len(cands) == 1
                                          else "AMBIGUOUS")
        rows.append({"link": link, "target": raw, "basename": bn,
                     "verdict": cls, "candidates": cands})
    order = {"REPAIRABLE": 0, "AMBIGUOUS": 1, "ORPHAN": 2}
    rows.sort(key=lambda r: order[r["verdict"]])
    counts = {k: sum(1 for r in rows if r["verdict"] == k)
              for k in ("REPAIRABLE", "AMBIGUOUS", "ORPHAN")}

    if as_json:
        print(json.dumps({"broken": len(rows), "counts": counts,
                          "rows": rows}, ensure_ascii=False, indent=2))
    else:
        for r in rows:
            print(f"{r['verdict']:<11}{homeify(r['link'])}")
            if r["verdict"] == "REPAIRABLE":
                print(f"            └→ {homeify(r['candidates'][0])}")
            elif r["verdict"] == "AMBIGUOUS":
                print(f"            └→ 후보 {len(r['candidates'])}개 "
                      f"(예: {homeify(r['candidates'][0])})")
        print(f"\n끊김 {len(rows)}개 → 복구가능 {counts['REPAIRABLE']} / "
              f"모호 {counts['AMBIGUOUS']} / 고아 {counts['ORPHAN']}")
    return 1 if rows else 0


def cmd_rel_candidates(roots, as_json):
    """abs→rel 변환 후보를 '변환이 제거하는 위험'으로 분류(brandt/symlinks subflow).

    핵심 뉘앙스: 상대화는 공통 조상 '위쪽' 의존만 없앤다. 공통 조상이 서술형
    폴더('_____') 아래면 그 폴더명이 상대경로에서 사라져 개명내성이 생기지만(FULL_WIN),
    공통 조상이 그 위(HOME 등)면 상대경로에 서술형 폴더명이 남아 사용자명만
    떨어진다(USERNAME_ONLY — 이건 이미 키트의 $HOME 치환이 하는 일이라 실익 낮음).
    """
    rows = []
    for link, raw, ab in iter_symlinks(roots):
        if not os.path.exists(link):
            continue  # 깨진 링크는 변환 대상 아님
        if not os.path.isabs(raw):
            rows.append({"link": link, "target": raw, "rel": raw,
                         "verdict": "ALREADY_REL"}); continue
        ld = os.path.dirname(link)
        rel = os.path.relpath(ab, ld)
        try:
            common = os.path.commonpath([os.path.abspath(link), ab])
        except ValueError:
            common = os.sep
        hs = str(HOME)
        if common == os.sep or not (common == hs or common.startswith(hs + os.sep)):
            verdict = "KEEP_ABSOLUTE"          # 루트/HOME 밖까지 올라감 → 절대 유지가 나음
        elif common == hs or "_____" in nfc(rel):
            # 공통 조상이 HOME(상대화해도 HOME까지 등반 = $HOME 치환과 동급) 이거나
            # 상대경로에 서술형 폴더가 남아 개명 위험이 그대로면 실익은 사용자명뿐.
            verdict = "USERNAME_ONLY"
        else:
            # 공통 조상이 HOME보다 깊고 서술형 폴더도 안 거침 → 짧고 안정적,
            # 상위 폴더 개명에도 안 깨짐(진짜 실익).
            verdict = "FULL_WIN"
        rows.append({"link": link, "target": raw, "rel": rel,
                     "verdict": verdict, "common": common})

    order = {"FULL_WIN": 0, "USERNAME_ONLY": 1, "KEEP_ABSOLUTE": 2, "ALREADY_REL": 3}
    rows.sort(key=lambda r: order[r["verdict"]])
    counts = {k: sum(1 for r in rows if r["verdict"] == k) for k in order}

    if as_json:
        print(json.dumps({"total": len(rows), "counts": counts, "rows": rows},
                         ensure_ascii=False, indent=2))
    else:
        for r in rows:
            if r["verdict"] == "FULL_WIN":
                print(f"FULL_WIN      {homeify(r['link'])}")
                print(f"              └→ {r['rel']}")
        print()
        for k in ("FULL_WIN", "USERNAME_ONLY", "KEEP_ABSOLUTE", "ALREADY_REL"):
            print(f"  {k:<14} {counts[k]}")
        print(f"\n변환 실익 큰 것(FULL_WIN, 개명내성 획득): {counts['FULL_WIN']}개. "
              "USERNAME_ONLY는 $HOME 치환이 이미 커버.")
    return 0


def cmd_external(boundary, roots, as_json):
    """freeze subflow: <경계> 안의 링크 중 경계 밖을 가리키는 것 = 외부 의존.
    이식/아카이브 시 함께 옮기지 않으면 깨진다."""
    b = nfc(os.path.abspath(os.path.expanduser(boundary))).rstrip(os.sep)
    scan = roots if roots else [Path(b)]
    hits = []
    for link, raw, ab in iter_symlinks(scan):
        abn = nfc(ab).rstrip(os.sep)
        inside_boundary = nfc(link).startswith(b + os.sep)
        if inside_boundary and abn != b and not abn.startswith(b + os.sep):
            hits.append({"link": link, "target": raw, "abs_target": ab,
                         "alive": os.path.exists(link)})
    # 경계 밖 어디로 새는지 접두어별 집계
    buckets = defaultdict(int)
    for h in hits:
        t = nfc(h["abs_target"])
        key = "/".join(t.split(os.sep)[:5]) or t
        buckets[homeify(key)] += 1
    if as_json:
        print(json.dumps({"boundary": b, "count": len(hits),
                          "escape_buckets": dict(buckets), "external": hits},
                         ensure_ascii=False, indent=2))
    else:
        print(f"# '{homeify(b)}' 밖을 가리키는 링크 (이식 시 함께 옮겨야 함)\n")
        for k, n in sorted(buckets.items(), key=lambda kv: -kv[1]):
            print(f"{n:4d}  → {k}...")
        print(f"\n외부 의존 링크: {len(hits)}개"
              + ("" if hits else " — 자기완결적(이식 안전)"))
    return 1 if hits else 0


def cmd_inbound(folder, roots, as_json):
    tgt = nfc(os.path.abspath(os.path.expanduser(folder)))
    hits = []
    for link, raw, ab in iter_symlinks(roots):
        abn = nfc(ab)
        if abn == tgt or abn.startswith(tgt + os.sep):
            hits.append({"link": link, "target": raw, "abs_target": ab,
                         "alive": os.path.exists(link)})
    if as_json:
        print(json.dumps({"folder": tgt, "count": len(hits), "inbound": hits},
                         ensure_ascii=False, indent=2))
    else:
        print(f"# '{homeify(tgt)}' 안을 가리키는 심링크 (개명/이동 시 깨질 것들)\n")
        for h in hits:
            mark = "" if h["alive"] else "  [이미 깨짐]"
            print(f"{homeify(h['link'])}{mark}")
        print(f"\n폭발 반경: {len(hits)}개 링크"
              + ("" if hits else " — 안전하게 개명/이동 가능"))
    return 0


def cmd_verbose_risk(roots, as_json):
    """'_____' 서술형 폴더명에 의존하는 살아있는 링크를, 의존 폴더별로 집계."""
    by_folder = defaultdict(list)
    for link, raw, ab in iter_symlinks(roots):
        if not os.path.exists(link):
            continue
        for comp in nfc(ab).split(os.sep):
            if "_____" in comp:
                by_folder[comp].append(link)
    groups = sorted(by_folder.items(), key=lambda kv: -len(kv[1]))
    total = sum(len(v) for v in by_folder.values())
    if as_json:
        print(json.dumps(
            {"total": total,
             "folders": [{"folder": k, "dependent_links": len(v),
                          "links": v} for k, v in groups]},
            ensure_ascii=False, indent=2))
    else:
        print("# 서술형('_____') 폴더에 의존하는 살아있는 링크 "
              "(그 폴더 개명 시 한꺼번에 깨짐)\n")
        for folder, links in groups:
            print(f"{len(links):4d}  {folder}")
        print(f"\n합계 {total}개 링크가 서술형 폴더명에 매여 있음. "
              "개명 전 반드시 `inbound <폴더>`로 반경 확인.")
    return 1 if total else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="path integrity guard")
    ap.add_argument("--json", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("broken").add_argument("roots", nargs="*")
    sub.add_parser("candidates").add_argument("roots", nargs="*")
    sub.add_parser("rel-candidates").add_argument("roots", nargs="*")
    pe = sub.add_parser("external")
    pe.add_argument("boundary")
    pe.add_argument("roots", nargs="*")
    pi = sub.add_parser("inbound")
    pi.add_argument("folder")
    pi.add_argument("roots", nargs="*")
    sub.add_parser("verbose-risk").add_argument("roots", nargs="*")
    args = ap.parse_args(argv)

    roots = [Path(r) for r in args.roots] if args.roots else DEFAULT_ROOTS
    if args.cmd == "broken":
        return cmd_broken(roots, args.json)
    if args.cmd == "candidates":
        return cmd_candidates(roots, args.json)
    if args.cmd == "rel-candidates":
        return cmd_rel_candidates(roots, args.json)
    if args.cmd == "external":
        return cmd_external(args.boundary, [Path(r) for r in args.roots]
                            if args.roots else None, args.json)
    if args.cmd == "inbound":
        return cmd_inbound(args.folder, roots, args.json)
    if args.cmd == "verbose-risk":
        return cmd_verbose_risk(roots, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
