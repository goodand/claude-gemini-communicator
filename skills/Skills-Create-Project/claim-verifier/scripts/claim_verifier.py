#!/usr/bin/env python3
"""claim-verifier — 자연어 claim을 원자화하고 코드/파일 증거로 판정한다.

Usage:
    python3 claim_verifier.py extract --input <file>
    python3 claim_verifier.py verify --claims <claims.json> --repo <path>
    python3 claim_verifier.py report --results <results.json>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))

# ---------------------------------------------------------------------------
# Claim Types (references/claim-types.md 대응)
# ---------------------------------------------------------------------------

CLAIM_TYPES = {
    "boundary": ["하지 않", "않는다", "포함하지", "금지", "제외", "not", "forbidden", "exclude"],
    "implementation": ["구현", "지원", "implement", "support"],
    "consistency": ["일치", "맞다", "동기화", "sync", "match", "consistent"],
    "artifact": ["존재", "생성", "파일", "exist", "file", "create", "generate"],
    "state": ["완료", "실행", "동작", "통과", "pass", "complete", "run"],
}

VERDICTS = {"true", "false", "partial", "unverifiable"}


def _now_iso():
    return datetime.now(KST).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Extract: 텍스트 → claim 목록
# ---------------------------------------------------------------------------

def _classify_claim(text):
    """claim 텍스트에서 type을 추론한다."""
    lower = text.lower()
    for ctype, keywords in CLAIM_TYPES.items():
        if any(kw in lower for kw in keywords):
            return ctype
    return "state"


def _split_compound(text):
    """복합 claim을 원자 단위로 분리한다.

    "A하고 B한다", "A + B + C" 같은 패턴을 분리.
    """
    # 한국어 나열 패턴
    parts = re.split(r"[,;]\s*(?:그리고|또한|및|and)\s*|[,;]\s+", text)
    if len(parts) > 1:
        return [p.strip() for p in parts if p.strip()]
    return [text]


def extract_claims(text, source_path=None):
    """텍스트에서 검증 가능한 claim 목록을 추출한다.

    - markdown list item (- / * / [ ])에서 추출
    - 빈 줄, 헤더(#), 코드블록(```) 무시
    - 복합 문장은 원자 단위로 분리
    """
    claims = []
    claim_id = 0
    in_code_block = False

    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()

        # 코드블록 토글
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # 무시: 빈 줄, 헤더, 구분선, 표 구분자
        if not stripped or stripped.startswith("#") or stripped.startswith("---"):
            continue
        if re.match(r"^\|[-:| ]+\|$", stripped):
            continue

        # claim 후보: list item 또는 일반 문장
        claim_text = stripped
        # list item prefix 제거
        claim_text = re.sub(r"^[-*]\s+(\[.\]\s+)?", "", claim_text)
        # 표 행에서 추출
        if claim_text.startswith("|") and claim_text.endswith("|"):
            cells = [c.strip() for c in claim_text.strip("|").split("|")]
            claim_text = " ".join(c for c in cells if c and not re.match(r"^[-:]+$", c))

        if not claim_text or len(claim_text) < 5:
            continue

        # 복합 claim 분리
        atoms = _split_compound(claim_text)
        for atom in atoms:
            claims.append({
                "id": f"CLM-{claim_id:03d}",
                "text": atom,
                "type": _classify_claim(atom),
                "source_file": source_path or "",
                "source_line": line_no,
            })
            claim_id += 1

    return claims


def cmd_extract(args):
    """파일에서 claim을 추출한다."""
    path = Path(args.input)
    if not path.exists():
        print(json.dumps({"error": f"파일 없음: {path}"}, ensure_ascii=False))
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    claims = extract_claims(text, source_path=str(path))

    output = {
        "command": "extract",
        "input": str(path),
        "claim_count": len(claims),
        "claims": claims,
        "extracted_at": _now_iso(),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))



# ---------------------------------------------------------------------------
# Verify: claim + repo → verdict + evidence
# ---------------------------------------------------------------------------

def _extract_paths(text):
    """claim 텍스트에서 파일 경로 후보를 추출한다."""
    # path/to/file.ext 패턴 (확장자는 ASCII만, 한국어 접미사 제거)
    paths = re.findall(r"[\w./\-]+\.[a-zA-Z0-9]{1,5}(?=[\s가-힣,;.\)\]\"']|$)", text)
    # 디렉토리 패턴 (path/to/dir/)
    paths += re.findall(r"[\w./\-]+/", text)
    return [p for p in paths if "/" in p or "." in p]


def _grep_file(file_path, pattern, max_results=5):
    """파일에서 패턴을 검색하여 line evidence를 반환한다."""
    evidence = []
    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            for line_no, line in enumerate(f, start=1):
                if pattern.lower() in line.lower():
                    evidence.append({
                        "file": str(file_path),
                        "line": line_no,
                        "content": line.rstrip()[:200],
                    })
                    if len(evidence) >= max_results:
                        break
    except (OSError, UnicodeDecodeError):
        pass
    return evidence


def _extract_keywords(text):
    """claim 텍스트에서 검색용 키워드를 추출한다."""
    # 따옴표 안 문자열
    quoted = re.findall(r"['\"`]([^'\"`]+)['\"`]", text)
    if quoted:
        return quoted
    # 주요 단어 (한국어 제외, 영문 identifier)
    words = re.findall(r"[a-zA-Z_]\w{2,}", text)
    return words[:3] if words else []


def verify_claim(claim, repo_root):
    """단일 claim을 repo 대비 검증한다.

    Returns: {"claim_id", "verdict", "evidence", "reason", "follow_up"}
    """
    text = claim.get("text", "")
    ctype = claim.get("type", "state")
    evidence = []
    verdict = "unverifiable"
    reason = ""
    follow_up = ""

    repo = Path(repo_root)

    # 1. 경로 기반 증거 수집
    paths = _extract_paths(text)
    for p in paths:
        full_path = repo / p
        if full_path.is_file():
            evidence.append({
                "file": str(p),
                "line": None,
                "content": f"파일 존재 확인: {p}",
                "type": "file_exists",
            })
        elif full_path.is_dir() or any(repo.glob(p + "*")):
            evidence.append({
                "file": str(p),
                "line": None,
                "content": f"디렉토리/패턴 존재: {p}",
                "type": "dir_exists",
            })

    # 2. 키워드 기반 증거 수집
    keywords = _extract_keywords(text)
    for kw in keywords:
        # repo 내 Python/MD/JSON 파일 검색
        for ext in ("*.py", "*.md", "*.json"):
            for f in repo.rglob(ext):
                # 너무 깊은 경로, node_modules 등 제외
                rel = str(f.relative_to(repo))
                if any(skip in rel for skip in ("node_modules", ".git", "__pycache__", ".venv")):
                    continue
                hits = _grep_file(f, kw, max_results=2)
                for h in hits:
                    h["file"] = rel
                    h["type"] = "keyword_match"
                evidence.extend(hits)
                if len(evidence) >= 10:
                    break
            if len(evidence) >= 10:
                break
        if len(evidence) >= 10:
            break

    # 3. 판정
    if not evidence:
        verdict = "unverifiable"
        reason = "관련 파일/키워드 증거를 찾지 못함"
        follow_up = "수동 탐색 필요: " + text[:80]
    elif ctype == "artifact":
        file_exists = any(e.get("type") == "file_exists" for e in evidence)
        verdict = "true" if file_exists else "false"
        reason = "파일 존재 확인" if file_exists else "파일 미존재"
        if verdict == "false":
            follow_up = f"파일 생성 필요: {paths}"
    elif ctype == "boundary":
        keyword_hits = [e for e in evidence if e.get("type") == "keyword_match"]
        if keyword_hits:
            verdict = "false"
            reason = f"금지 대상이 발견됨 ({len(keyword_hits)}건)"
            follow_up = "해당 코드를 제거하거나 claim을 수정"
        else:
            verdict = "true"
            reason = "금지 대상 미발견"
    elif ctype == "consistency":
        # consistency claim은 keyword grep으로 부분 판정만 가능.
        # pairwise doc↔code 비교는 doc-code-sync-checker를 사용할 것.
        keyword_hits = [e for e in evidence if e.get("type") == "keyword_match"]
        file_hits = [e for e in evidence if e.get("type") in ("file_exists", "dir_exists")]
        if keyword_hits and file_hits:
            verdict = "partial"
            reason = "keyword + 파일 존재 확인됨. pairwise 비교는 doc-code-sync-checker 필요"
            follow_up = "doc-code-sync-checker로 정밀 비교 필요"
        elif keyword_hits or file_hits:
            verdict = "partial"
            reason = "일부 증거만 확인됨"
            follow_up = "doc-code-sync-checker로 정밀 비교 필요"
        else:
            verdict = "unverifiable"
            reason = "구조적 증거 부족"
            follow_up = "doc-code-sync-checker로 정밀 비교 필요"
    else:
        # implementation, state: 증거 양으로 판정
        keyword_hits = [e for e in evidence if e.get("type") == "keyword_match"]
        file_hits = [e for e in evidence if e.get("type") in ("file_exists", "dir_exists")]

        if keyword_hits and file_hits:
            verdict = "true"
            reason = f"파일 존재 + 키워드 {len(keyword_hits)}건 매칭"
        elif keyword_hits or file_hits:
            verdict = "partial"
            reason = "일부 증거만 확인됨"
            follow_up = "추가 확인 필요: 코드 실행 또는 수동 검증"
        else:
            verdict = "unverifiable"
            reason = "구조적 증거 부족"
            follow_up = "수동 탐색 필요"

    return {
        "claim_id": claim.get("id", "?"),
        "claim_text": text,
        "claim_type": ctype,
        "verdict": verdict,
        "evidence": evidence[:5],  # 최대 5건
        "reason": reason,
        "follow_up": follow_up,
    }


def cmd_verify(args):
    """claim 목록을 repo 대비 검증한다."""
    claims_path = Path(args.claims)
    if not claims_path.exists():
        print(json.dumps({"error": f"파일 없음: {claims_path}"}, ensure_ascii=False))
        sys.exit(1)

    data = json.loads(claims_path.read_text(encoding="utf-8"))
    claims = data.get("claims", data) if isinstance(data, dict) else data

    results = []
    for claim in claims:
        result = verify_claim(claim, args.repo)
        results.append(result)

    output = {
        "command": "verify",
        "repo": args.repo,
        "total": len(results),
        "summary": {
            v: sum(1 for r in results if r["verdict"] == v)
            for v in VERDICTS
        },
        "results": results,
        "verified_at": _now_iso(),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Report: 결과 → 보고서
# ---------------------------------------------------------------------------

def format_report(data):
    """검증 결과를 markdown 보고서로 변환한다."""
    lines = []
    lines.append("# Claim Verification Report")
    lines.append("")
    lines.append(f"- verified_at: `{data.get('verified_at', '?')}`")
    lines.append(f"- repo: `{data.get('repo', '?')}`")
    lines.append(f"- total claims: {data.get('total', 0)}")
    lines.append("")

    # Summary
    summary = data.get("summary", {})
    lines.append("## Summary")
    lines.append("")
    lines.append("| Verdict | Count |")
    lines.append("|---------|-------|")
    for v in ["true", "false", "partial", "unverifiable"]:
        lines.append(f"| {v} | {summary.get(v, 0)} |")
    lines.append("")

    # Details
    lines.append("## Details")
    lines.append("")
    for r in data.get("results", []):
        verdict_mark = {"true": "O", "false": "X", "partial": "△", "unverifiable": "?"}
        mark = verdict_mark.get(r["verdict"], "?")
        lines.append(f"### [{mark}] {r['claim_id']}: {r['claim_text'][:80]}")
        lines.append("")
        lines.append(f"- **verdict**: {r['verdict']}")
        lines.append(f"- **type**: {r.get('claim_type', '?')}")
        lines.append(f"- **reason**: {r.get('reason', '')}")
        if r.get("follow_up"):
            lines.append(f"- **follow_up**: {r['follow_up']}")

        evidence = r.get("evidence", [])
        if evidence:
            lines.append("- **evidence**:")
            for e in evidence:
                loc = f"{e['file']}:{e['line']}" if e.get("line") else e.get("file", "?")
                lines.append(f"  - `{loc}` — {e.get('content', '')[:120]}")
        lines.append("")

    return "\n".join(lines)


def cmd_report(args):
    """검증 결과를 보고서로 출력한다."""
    results_path = Path(args.results)
    if not results_path.exists():
        print(json.dumps({"error": f"파일 없음: {results_path}"}, ensure_ascii=False))
        sys.exit(1)

    data = json.loads(results_path.read_text(encoding="utf-8"))
    report = format_report(data)
    print(report)


def format_verdict_table(data):
    """results → 5열 markdown 표 (claim_id | verdict | evidence | reason | follow_up)."""
    lines = [
        "| claim_id | verdict | evidence | reason | follow_up |",
        "|----------|---------|----------|--------|-----------|",
    ]
    for r in data.get("results", []):
        cid = r.get("claim_id", "?")
        verdict = r.get("verdict", "?")

        ev_parts = []
        for e in r.get("evidence", [])[:3]:
            if e.get("line"):
                ev_parts.append(f"`{e['file']}:{e['line']}`")
            elif e.get("file"):
                ev_parts.append(f"`{e['file']}`")
        ev_str = ", ".join(ev_parts) if ev_parts else "—"

        reason = r.get("reason", "").replace("|", "/")[:60]
        follow_up = r.get("follow_up", "").replace("|", "/")[:60]

        lines.append(f"| {cid} | {verdict} | {ev_str} | {reason} | {follow_up} |")

    return "\n".join(lines)


def cmd_table(args):
    """검증 결과를 5열 verdict 표로 출력한다."""
    results_path = Path(args.results)
    if not results_path.exists():
        print(json.dumps({"error": f"파일 없음: {results_path}"}, ensure_ascii=False))
        sys.exit(1)

    data = json.loads(results_path.read_text(encoding="utf-8"))
    print(format_verdict_table(data))


# ---------------------------------------------------------------------------
# API: 프로그래밍 방식 사용
# ---------------------------------------------------------------------------

def verify_text(text, repo_root, source_path=None):
    """텍스트에서 claim 추출 → 검증 → 결과 반환 (일괄 처리).

    Returns: {"claims": [...], "results": [...], "summary": {...}}
    """
    claims = extract_claims(text, source_path=source_path)
    results = [verify_claim(c, repo_root) for c in claims]
    summary = {v: sum(1 for r in results if r["verdict"] == v) for v in VERDICTS}
    return {
        "claims": claims,
        "results": results,
        "summary": summary,
        "total": len(results),
    }


def verify_batch(items, repo_root):
    """여러 claim/텍스트를 한번에 검증한다.

    Args:
        items: list — 각 원소는 str(자연어 텍스트) 또는 dict(구조화된 claim).
            str이면 extract_claims로 분해, dict이면 직접 claim으로 사용.
        repo_root: 검증 대상 repo 경로

    Returns: {"claims": [...], "results": [...], "summary": {...}, "total": int}
    """
    all_claims = []
    claim_id = 0
    for item in items:
        if isinstance(item, str):
            sub_claims = extract_claims(item)
            for c in sub_claims:
                c["id"] = f"CLM-{claim_id:03d}"
                claim_id += 1
            all_claims.extend(sub_claims)
        elif isinstance(item, dict):
            if "id" not in item:
                item["id"] = f"CLM-{claim_id:03d}"
            if "type" not in item:
                item["type"] = _classify_claim(item.get("text", ""))
            claim_id += 1
            all_claims.append(item)

    results = [verify_claim(c, repo_root) for c in all_claims]
    summary = {v: sum(1 for r in results if r["verdict"] == v) for v in VERDICTS}
    return {
        "claims": all_claims,
        "results": results,
        "summary": summary,
        "total": len(results),
    }


def cmd_batch(args):
    """여러 파일/JSON에서 claim을 일괄 검증한다."""
    items = []
    if args.items:
        for fpath in args.items:
            p = Path(fpath)
            if not p.exists():
                print(json.dumps({"error": f"파일 없음: {p}"}, ensure_ascii=False))
                sys.exit(1)
            text = p.read_text(encoding="utf-8")
            items.append(text)
    elif args.claims_json:
        p = Path(args.claims_json)
        if not p.exists():
            print(json.dumps({"error": f"파일 없음: {p}"}, ensure_ascii=False))
            sys.exit(1)
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and "items" in data:
            items = data["items"]
        else:
            items = [data]

    result = verify_batch(items, args.repo)
    result["command"] = "batch"
    result["verified_at"] = _now_iso()
    print(json.dumps(result, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="claim-verifier — 자연어 claim을 코드/파일 증거로 판정한다"
    )
    sub = parser.add_subparsers(dest="command")

    p_extract = sub.add_parser("extract", help="claim 목록 추출")
    p_extract.add_argument("--input", required=True, help="원본 텍스트/문서 파일")

    p_verify = sub.add_parser("verify", help="claim 증거 검증")
    p_verify.add_argument("--claims", required=True, help="claim 목록 JSON")
    p_verify.add_argument("--repo", required=True, help="검증 대상 repo 경로")

    p_report = sub.add_parser("report", help="검증 결과 보고")
    p_report.add_argument("--results", required=True, help="검증 결과 JSON")

    p_table = sub.add_parser("table", help="verdict 5열 표 출력")
    p_table.add_argument("--results", required=True, help="검증 결과 JSON")

    p_batch = sub.add_parser("batch", help="여러 파일/claim 일괄 검증")
    p_batch_input = p_batch.add_mutually_exclusive_group(required=True)
    p_batch_input.add_argument("--items", nargs="+", help="텍스트 파일 목록")
    p_batch_input.add_argument("--claims-json", help="claim 묶음 JSON 파일")
    p_batch.add_argument("--repo", required=True, help="검증 대상 repo 경로")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "extract": cmd_extract,
        "verify": cmd_verify,
        "report": cmd_report,
        "table": cmd_table,
        "batch": cmd_batch,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
