#!/usr/bin/env python3
"""Reference implementation: classification rules are hardcoded for
vscode-markdown-review-surface (src/decision/*, src/extension.*).

To reuse for a different repo, replace the path-matching rules below
or extract them into an external JSON/YAML config file.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def classify_review_file(path: str) -> str:
    normalized = path.replace("\\", "/")
    name = Path(normalized).name

    if normalized == "package.json" or normalized.startswith("src/extension."):
        return "host_entry"
    if "src/decision/" in normalized and any(
        token in name for token in ("session-config", "decision-contract", "feedback-ledger")
    ):
        return "data_contract"
    if "src/decision/" in normalized and (name.startswith("slide-") or "decision-slides" in name):
        return "feature_seam"
    if "src/decision/" in normalized and name.startswith("webview-"):
        return "webview_render"
    if "src/decision/" in normalized and (
        name.startswith("host-") or name.startswith("mode-router")
    ):
        return "host_state"
    if "/test/" in normalized or "/tests/" in normalized or ".test." in name:
        return "tests"
    return "unclassified"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Classify review files into canonical product-review buckets.")
    parser.add_argument("paths", nargs="+", help="Repo-relative file paths to classify.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    payload = {path: classify_review_file(path) for path in args.paths}
    print(json.dumps(payload, indent=2, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
