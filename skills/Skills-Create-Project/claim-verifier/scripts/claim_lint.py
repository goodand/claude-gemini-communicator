#!/usr/bin/env python3
"""claim-verifier 중간 산출물 lint.

claims.json / results.json 품질 검사 + follow-up skeleton 생성.

Usage:
    python3 claim_lint.py claims --input claims.json
    python3 claim_lint.py results --input results.json
    python3 claim_lint.py all --claims claims.json --results results.json
    python3 claim_lint.py follow-up --input results.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

VALID_TYPES = {"implementation", "state", "artifact", "boundary", "consistency"}
VALID_VERDICTS = {"true", "false", "partial", "unverifiable"}
REQUIRED_RESULT_FIELDS = ("claim_id", "verdict", "evidence", "reason", "follow_up")

# ---------------------------------------------------------------------------
# Claims lint
# ---------------------------------------------------------------------------

def lint_claims(data):
    """claims.json 품질 검사.

    Checks:
        C1  compound claim 잔존 (분리 안 된 복합 문장)
        C2  type 누락 또는 알 수 없는 type
        C3  텍스트가 너무 짧아 검증 불가
        C4  id 형식 불일치 (CLM-NNN 아님)
        C5  id 중복
    """
    warnings = []
    claims = _extract_claims_list(data)
    seen_ids = set()

    for c in claims:
        cid = c.get("id", "?")
        text = c.get("text", "")
        ctype = c.get("type", "")

        # C1: compound claim 잔존
        if re.search(r"[,;]\s*(그리고|또한|및|and)\s+", text):
            warnings.append(_w(cid, "C1", "warn",
                f"compound pattern 잔존: {text[:60]}"))

        # C2: type 누락/이상
        if not ctype:
            warnings.append(_w(cid, "C2", "error", "claim type 비어 있음"))
        elif ctype not in VALID_TYPES:
            warnings.append(_w(cid, "C2", "error",
                f"알 수 없는 claim type: {ctype}"))

        # C3: 너무 짧음
        if len(text) < 5:
            warnings.append(_w(cid, "C3", "warn",
                f"claim 텍스트 너무 짧음: '{text}'"))

        # C4: id 형식
        if not re.match(r"^CLM-\d{3,}$", cid):
            warnings.append(_w(cid, "C4", "warn",
                f"id 형식 불일치: {cid}"))

        # C5: id 중복
        if cid in seen_ids:
            warnings.append(_w(cid, "C5", "error",
                f"id 중복: {cid}"))
        seen_ids.add(cid)

    return warnings


# ---------------------------------------------------------------------------
# Results lint
# ---------------------------------------------------------------------------

def lint_results(data):
    """results.json 구조 검사.

    Checks:
        R1  evidence 없는 true verdict
        R2  false/partial/unverifiable에 follow_up 누락
        R3  file evidence만 있는 true (keyword 없음)
        R4  keyword_match evidence에 line 번호 없음
        R5  알 수 없는 verdict
        R6  필수 필드 누락
        R7  line evidence 비율 (전체 기준)
        R8  follow_up 문구 반복 (3회 이상 동일)
    """
    warnings = []
    results = data.get("results", [])

    total_evidence = 0
    line_evidence = 0
    follow_ups = []

    for r in results:
        rid = r.get("claim_id", "?")
        verdict = r.get("verdict", "")
        evidence = r.get("evidence", [])
        follow_up = r.get("follow_up", "")

        # R6: 필수 필드 누락
        for field in REQUIRED_RESULT_FIELDS:
            if field not in r:
                warnings.append(_w(rid, "R6", "error",
                    f"필수 필드 누락: {field}"))

        # R5: verdict 유효성
        if verdict not in VALID_VERDICTS:
            warnings.append(_w(rid, "R5", "error",
                f"알 수 없는 verdict: {verdict}"))

        # R1: evidence 없는 true
        if verdict == "true" and not evidence:
            warnings.append(_w(rid, "R1", "error",
                "true verdict인데 evidence 없음"))

        # R2: non-true에 follow_up 누락
        if verdict in ("false", "partial", "unverifiable") and not follow_up:
            warnings.append(_w(rid, "R2", "error",
                f"{verdict} verdict인데 follow_up 누락"))

        # R3: file-only true
        if verdict == "true" and evidence:
            has_kw = any(e.get("type") == "keyword_match" for e in evidence)
            has_file = any(
                e.get("type") in ("file_exists", "dir_exists") for e in evidence
            )
            if has_file and not has_kw:
                warnings.append(_w(rid, "R3", "warn",
                    "true verdict인데 file evidence만 (keyword 없음)"))

        # R4: keyword_match에 line 없음
        for e in evidence:
            total_evidence += 1
            if e.get("line") is not None:
                line_evidence += 1
            if e.get("type") == "keyword_match" and e.get("line") is None:
                warnings.append(_w(rid, "R4", "warn",
                    f"keyword_match에 line 없음: {e.get('file', '?')}"))

        if follow_up:
            follow_ups.append(follow_up)

    # R7: line evidence 비율
    if total_evidence > 0:
        ratio = line_evidence / total_evidence
        warnings.append(_w("GLOBAL", "R7", "info",
            f"line evidence 비율: {line_evidence}/{total_evidence} ({ratio:.0%})"))

    # R8: follow_up 반복
    for text, count in Counter(follow_ups).items():
        if count >= 3:
            warnings.append(_w("GLOBAL", "R8", "info",
                f"follow_up 반복 {count}회: '{text[:60]}'"))

    return warnings


# ---------------------------------------------------------------------------
# Follow-up skeleton
# ---------------------------------------------------------------------------

def generate_follow_up_skeleton(data):
    """follow_up이 비었거나 반복인 결과에 skeleton을 제안한다.

    Returns: list of {"claim_id", "verdict", "current", "suggested"}
    """
    suggestions = []
    results = data.get("results", [])

    for r in results:
        rid = r.get("claim_id", "?")
        verdict = r.get("verdict", "")
        current = r.get("follow_up", "")
        text = r.get("claim_text", "")
        evidence = r.get("evidence", [])

        suggested = _suggest_follow_up(verdict, text, evidence)
        if not suggested:
            continue

        # 비어있거나, 기존과 다를 때만 제안
        if not current or current != suggested:
            suggestions.append({
                "claim_id": rid,
                "verdict": verdict,
                "current": current,
                "suggested": suggested,
            })

    return suggestions


def _suggest_follow_up(verdict, text, evidence):
    """verdict + claim 내용 기반 follow-up skeleton 생성."""
    if verdict == "true":
        return ""

    # claim에서 대상 추출
    target = _extract_target(text)

    if verdict == "false":
        if target:
            return f"수정 대상: {target}"
        return "수정 대상 명시 필요"

    if verdict == "partial":
        missing = _infer_missing(text, evidence)
        if missing:
            return f"누락 항목: {missing}"
        return "추가 증거 수집 필요"

    if verdict == "unverifiable":
        if target:
            return f"추가 탐색: {target}"
        return "수동 탐색 필요"

    return ""


def _extract_target(text):
    """claim 텍스트에서 핵심 대상(파일, 함수, 모듈)을 추출한다."""
    # 파일 경로
    paths = re.findall(
        r"[\w./\-]+\.[a-zA-Z0-9]{1,5}(?=[\s가-힣,;.\)\]\"']|$)", text
    )
    if paths:
        return ", ".join(paths[:2])
    # 따옴표 키워드
    quoted = re.findall(r"['\"`]([^'\"`]+)['\"`]", text)
    if quoted:
        return ", ".join(quoted[:2])
    # identifier
    ids = re.findall(r"[a-zA-Z_]\w{3,}", text)
    if ids:
        return ids[0]
    return text[:40]


def _infer_missing(text, evidence):
    """evidence에서 누락된 것을 추론한다."""
    types = {e.get("type") for e in evidence}
    missing_parts = []
    if "keyword_match" not in types:
        missing_parts.append("keyword 증거")
    if "file_exists" not in types and "dir_exists" not in types:
        missing_parts.append("파일 증거")
    if missing_parts:
        return ", ".join(missing_parts)
    return ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_claims_list(data):
    """data에서 claims list를 추출한다."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("claims", [])
    return []


def _w(id_, check, severity, message):
    return {"id": id_, "check": check, "severity": severity, "message": message}


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _format_warnings(warnings, fmt="text"):
    if fmt == "json":
        return json.dumps(warnings, indent=2, ensure_ascii=False)

    if not warnings:
        return "OK — 경고 없음"

    lines = []
    errors = [w for w in warnings if w["severity"] == "error"]
    warns = [w for w in warnings if w["severity"] == "warn"]
    infos = [w for w in warnings if w["severity"] == "info"]

    for w in errors + warns + infos:
        icon = {"error": "[E]", "warn": "[W]", "info": "[I]"}[w["severity"]]
        lines.append(f"{icon} {w['check']} {w['id']}: {w['message']}")

    lines.append("")
    lines.append(
        f"총 {len(warnings)}건 (error={len(errors)}, warn={len(warns)}, info={len(infos)})"
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="claim-verifier 중간 산출물 lint"
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="출력 형식 (default: text)"
    )
    sub = parser.add_subparsers(dest="command")

    p_claims = sub.add_parser("claims", help="claims.json 품질 검사")
    p_claims.add_argument("--input", required=True, help="claims.json 경로")

    p_results = sub.add_parser("results", help="results.json 구조 검사")
    p_results.add_argument("--input", required=True, help="results.json 경로")

    p_all = sub.add_parser("all", help="claims + results 전체 검사")
    p_all.add_argument("--claims", required=True, help="claims.json 경로")
    p_all.add_argument("--results", required=True, help="results.json 경로")

    p_follow = sub.add_parser("follow-up", help="follow-up skeleton 제안")
    p_follow.add_argument("--input", required=True, help="results.json 경로")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "claims":
        data = _load(args.input)
        warnings = lint_claims(data)
        print(_format_warnings(warnings, args.format))
        sys.exit(1 if any(w["severity"] == "error" for w in warnings) else 0)

    elif args.command == "results":
        data = _load(args.input)
        warnings = lint_results(data)
        print(_format_warnings(warnings, args.format))
        sys.exit(1 if any(w["severity"] == "error" for w in warnings) else 0)

    elif args.command == "all":
        claims_data = _load(args.claims)
        results_data = _load(args.results)
        warnings = lint_claims(claims_data) + lint_results(results_data)
        print(_format_warnings(warnings, args.format))
        sys.exit(1 if any(w["severity"] == "error" for w in warnings) else 0)

    elif args.command == "follow-up":
        data = _load(args.input)
        suggestions = generate_follow_up_skeleton(data)
        if args.format == "json":
            print(json.dumps(suggestions, indent=2, ensure_ascii=False))
        else:
            if not suggestions:
                print("OK — follow-up 제안 없음")
            else:
                for s in suggestions:
                    current = f" (현재: '{s['current']}')" if s["current"] else ""
                    print(f"{s['claim_id']} [{s['verdict']}]{current}")
                    print(f"  → {s['suggested']}")


if __name__ == "__main__":
    main()
