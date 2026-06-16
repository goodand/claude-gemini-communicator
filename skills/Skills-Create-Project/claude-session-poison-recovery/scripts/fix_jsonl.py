#!/usr/bin/env python3
"""
Fix a Claude session JSONL by removing surrogate code points and NUL bytes.

Default mode is dry-run. Use --apply to write changes in place after creating
`<file>.bak`.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


def sanitize_path(path: str) -> Path:
    return Path(path).expanduser().resolve()


def sanitize_obj(obj: Any) -> Any:
    if isinstance(obj, str):
        cleaned = "".join(ch for ch in obj if not (0xD800 <= ord(ch) <= 0xDFFF))
        return cleaned.replace("\x00", "")
    if isinstance(obj, dict):
        return {key: sanitize_obj(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [sanitize_obj(item) for item in obj]
    if isinstance(obj, tuple):
        return [sanitize_obj(item) for item in obj]
    return obj


def fix_line(line: str) -> tuple[str | None, bool, str | None]:
    parse_failed = False
    try:
        obj = json.loads(line)
    except Exception as exc:
        parse_failed = True
        cleaned_line = "".join(ch for ch in line if not (0xD800 <= ord(ch) <= 0xDFFF)).replace("\x00", "")
        try:
            obj = json.loads(cleaned_line)
        except Exception as exc2:
            return None, False, f"json parse failed before={exc!r} after={exc2!r}"
    cleaned_obj = sanitize_obj(obj)
    if not parse_failed and cleaned_obj == obj:
        return line, False, None
    fixed = json.dumps(cleaned_obj, ensure_ascii=False, separators=(",", ":")) + "\n"
    return fixed, True, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix Claude session JSONL surrogate/NUL issues")
    parser.add_argument("session_jsonl", help="Path to the Claude session JSONL")
    parser.add_argument("--apply", action="store_true", help="Overwrite the target after creating a .bak backup")
    parser.add_argument("--output", help="Write fixed output to a separate path")
    args = parser.parse_args()

    session_path = sanitize_path(args.session_jsonl)
    if not session_path.exists():
        print(f"[fix-jsonl] missing: {session_path}")
        return 1

    fixed_lines: list[str] = []
    changed = 0
    failed: list[dict[str, Any]] = []

    with session_path.open("r", encoding="utf-8", errors="surrogatepass") as handle:
        for line_no, line in enumerate(handle, 1):
            fixed, modified, error = fix_line(line)
            if error is not None or fixed is None:
                failed.append({"line": line_no, "error": error})
                fixed_lines.append(line)
                continue
            if modified:
                changed += 1
            fixed_lines.append(fixed)

    print(f"[fix-jsonl] target={session_path}")
    print(f"[fix-jsonl] changed_lines={changed}")
    print(f"[fix-jsonl] failed_lines={len(failed)}")
    if failed:
        print(f"[fix-jsonl] failed_preview={failed[:5]}")

    output_path: Path | None = None
    if args.output:
        output_path = sanitize_path(args.output)
    elif args.apply:
        output_path = session_path
    else:
        output_path = session_path.with_suffix(session_path.suffix + ".fixed")

    if args.apply:
        backup_path = session_path.with_suffix(session_path.suffix + ".bak")
        shutil.copy2(session_path, backup_path)
        print(f"[fix-jsonl] backup={backup_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        handle.writelines(fixed_lines)

    mode = "applied" if args.apply else "written_copy"
    print(f"[fix-jsonl] {mode}={output_path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
