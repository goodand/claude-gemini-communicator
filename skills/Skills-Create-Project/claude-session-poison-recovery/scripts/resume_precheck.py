#!/usr/bin/env python3
"""
Precheck a Claude session JSONL before attempting `claude --resume <session-id>`.

Checks:
- file exists
- full line-by-line JSON parse success
- tail region parse success
- surrogate codepoint scan
- optional sessions-index presence/entry
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any


def sanitize_path(path: str) -> Path:
    return Path(path).expanduser().resolve()


def collect_surrogates(obj: Any, *, path: str = "$", out: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    if out is None:
        out = []
    if isinstance(obj, str):
        for idx, ch in enumerate(obj):
            code = ord(ch)
            if 0xD800 <= code <= 0xDFFF:
                out.append({"path": path, "index": idx, "codepoint": f"U+{code:04X}"})
        return out
    if isinstance(obj, list):
        for idx, item in enumerate(obj):
            collect_surrogates(item, path=f"{path}[{idx}]", out=out)
        return out
    if isinstance(obj, dict):
        for key, value in obj.items():
            collect_surrogates(value, path=f"{path}.{key}", out=out)
        return out
    return out


def check_sessions_index(session_path: Path) -> dict[str, Any]:
    project_dir = session_path.parent
    index_path = project_dir / "sessions-index.json"
    result: dict[str, Any] = {
        "path": str(index_path),
        "exists": index_path.exists(),
        "entry_found": False,
        "entry_count": None,
    }
    if not index_path.exists():
        return result
    try:
        obj = json.loads(index_path.read_text(encoding="utf-8"))
        entries = obj.get("entries", []) if isinstance(obj, dict) else []
        result["entry_count"] = len(entries) if isinstance(entries, list) else None
        session_id = session_path.stem
        if isinstance(entries, list):
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                if entry.get("sessionId") == session_id:
                    result["entry_found"] = True
                    break
    except Exception as exc:
        result["error"] = repr(exc)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Claude resume precheck")
    parser.add_argument("session_jsonl", help="Path to the Claude session JSONL")
    parser.add_argument("--tail-lines", type=int, default=50, help="Tail region line count to validate")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args()

    session_path = sanitize_path(args.session_jsonl)
    report: dict[str, Any] = {
        "session_path": str(session_path),
        "session_id": session_path.stem,
        "exists": session_path.exists(),
    }
    if not session_path.exists():
        report["status"] = "missing"
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(f"[resume-precheck] missing: {session_path}")
        return 1

    total_lines = 0
    parse_errors: list[dict[str, Any]] = []
    tail_buffer: deque[tuple[int, str]] = deque(maxlen=max(1, args.tail_lines))
    surrogate_hits: list[dict[str, Any]] = []
    typed_messages = 0

    with session_path.open("r", encoding="utf-8", errors="surrogatepass") as handle:
        for line_no, line in enumerate(handle, 1):
            total_lines += 1
            tail_buffer.append((line_no, line))
            try:
                obj = json.loads(line)
            except Exception as exc:
                parse_errors.append({"line": line_no, "error": repr(exc)})
                continue

            if isinstance(obj, dict) and obj.get("type") in {"user", "assistant"}:
                typed_messages += 1

            hits = collect_surrogates(obj)
            if hits:
                for hit in hits[:10]:
                    surrogate_hits.append({"line": line_no, **hit})

    tail_parse_errors: list[dict[str, Any]] = []
    for line_no, line in tail_buffer:
        try:
            json.loads(line)
        except Exception as exc:
            tail_parse_errors.append({"line": line_no, "error": repr(exc)})

    file_size = session_path.stat().st_size
    report.update(
        {
            "file_size_bytes": file_size,
            "total_lines": total_lines,
            "typed_messages": typed_messages,
            "full_parse_ok": len(parse_errors) == 0,
            "tail_parse_ok": len(tail_parse_errors) == 0,
            "parse_error_count": len(parse_errors),
            "tail_parse_error_count": len(tail_parse_errors),
            "surrogate_hit_count": len(surrogate_hits),
            "surrogate_hits_preview": surrogate_hits[:20],
            "sessions_index": check_sessions_index(session_path),
        }
    )

    critical_fail = (
        not report["full_parse_ok"]
        or not report["tail_parse_ok"]
        or report["surrogate_hit_count"] > 0
    )
    report["status"] = "fail" if critical_fail else "pass"
    report["resume_hint"] = (
        f"claude --resume {session_path.stem}"
        if not critical_fail
        else f"fix first, then retry: claude --resume {session_path.stem}"
    )

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"[resume-precheck] session: {session_path}")
        print(f"[resume-precheck] lines={total_lines} typed_messages={typed_messages} size={file_size}")
        print(f"[resume-precheck] full_parse_ok={report['full_parse_ok']} tail_parse_ok={report['tail_parse_ok']}")
        print(f"[resume-precheck] surrogate_hit_count={report['surrogate_hit_count']}")
        idx = report["sessions_index"]
        print(
            "[resume-precheck] sessions_index "
            f"exists={idx.get('exists')} entry_found={idx.get('entry_found')} path={idx.get('path')}"
        )
        if parse_errors:
            print(f"[resume-precheck] parse_errors_preview={parse_errors[:5]}")
        if tail_parse_errors:
            print(f"[resume-precheck] tail_parse_errors_preview={tail_parse_errors[:5]}")
        if surrogate_hits:
            print(f"[resume-precheck] surrogate_hits_preview={surrogate_hits[:5]}")
        print(f"[resume-precheck] status={report['status']}")
        print(f"[resume-precheck] hint={report['resume_hint']}")

    return 1 if critical_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
