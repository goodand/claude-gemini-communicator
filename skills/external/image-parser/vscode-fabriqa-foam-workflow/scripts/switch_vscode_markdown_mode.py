#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


FABRIQA_VIEW_TYPE = "fabriqa.markdownEditor"


def strip_jsonc(text: str) -> str:
    out = []
    i = 0
    in_string = False
    in_line_comment = False
    in_block_comment = False
    escaped = False

    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""

        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
                out.append(ch)
            i += 1
            continue

        if in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
                i += 2
            else:
                i += 1
            continue

        if in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue

        if ch == "/" and nxt == "/":
            in_line_comment = True
            i += 2
            continue

        if ch == "/" and nxt == "*":
            in_block_comment = True
            i += 2
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def load_settings(path: Path) -> dict:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    cleaned = strip_jsonc(raw).strip()
    if not cleaned:
        return {}
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Could not parse settings JSONC: {path}: {exc}")
    if not isinstance(data, dict):
        raise SystemExit(f"Settings root must be an object: {path}")
    return data


def save_settings(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Switch workspace markdown editor mode for VS Code.")
    parser.add_argument("--workspace", required=True, help="Workspace folder path")
    parser.add_argument("--mode", required=True, choices=["fabriqa", "text", "clear"])
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    settings_path = workspace / ".vscode" / "settings.json"
    data = load_settings(settings_path)

    associations = data.get("workbench.editorAssociations")
    if associations is None:
        associations = {}
    if not isinstance(associations, dict):
        raise SystemExit(
            "workbench.editorAssociations is not an object. "
            "Normalize it manually before using this script."
        )

    if args.mode == "fabriqa":
        associations["*.md"] = FABRIQA_VIEW_TYPE
    elif args.mode == "text":
        associations["*.md"] = "default"
    elif args.mode == "clear":
        associations.pop("*.md", None)

    if associations:
        data["workbench.editorAssociations"] = associations
    else:
        data.pop("workbench.editorAssociations", None)

    save_settings(settings_path, data)
    print(f"workspace={workspace}")
    print(f"settings={settings_path}")
    print(f"mode={args.mode}")
    print(
        "note=existing open markdown tabs may need close/reopen or 'Reopen Editor With...' "
        "before the new association is reflected"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
