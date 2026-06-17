#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


KST = timezone(timedelta(hours=9))
TIMESTAMP_RE = re.compile(r"-at\d{4}-\d{2}-\d{2}-\d{2}-\d{2}$")


def _err(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.exit(1)


def _now_stamp() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d-%H-%M")


def _normalize_experiment_name(name: str) -> str:
    stem = TIMESTAMP_RE.sub("", name)
    for suffix in ("-post-fix-smoke-report", "-pre-fix-smoke-report", "-smoke-report", "-baseline-measure"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    return stem.strip("-") or "baseline-diff"


def _derive_experiment_name(pre_path: Path, explicit: str | None) -> str:
    if explicit:
        return explicit.strip()
    return _normalize_experiment_name(pre_path.stem)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan baseline diff artifacts and handoff steps")
    parser.add_argument("--skill", required=True, help="upstream skill name")
    parser.add_argument("--pre", required=True, help="pre-fix baseline artifact path")
    parser.add_argument("--post", required=True, help="post-fix baseline artifact path")
    parser.add_argument(
        "--debug",
        action="append",
        default=[],
        help="debug evidence path (repeatable)",
    )
    parser.add_argument(
        "--metric",
        action="append",
        required=True,
        help="metric name to carry into diff planning (repeatable)",
    )
    parser.add_argument("--experiment", help="optional explicit experiment name")
    args = parser.parse_args()

    pre_path = Path(args.pre)
    post_path = Path(args.post)
    debug_paths = [Path(item) for item in args.debug]

    if not pre_path.is_file():
        _err(f"pre-fix artifact 없음: {pre_path}")
    if not post_path.is_file():
        _err(f"post-fix artifact 없음: {post_path}")
    for debug_path in debug_paths:
        if not debug_path.is_file():
            _err(f"debug evidence 없음: {debug_path}")

    experiment = _derive_experiment_name(pre_path, args.experiment)
    stamp = _now_stamp()

    payload = {
        "status": "planned",
        "skill": args.skill,
        "experiment": experiment,
        "inputs": {
            "pre_fix": str(pre_path),
            "post_fix": str(post_path),
            "debug_evidence": [str(path) for path in debug_paths],
            "metrics": args.metric,
        },
        "suggested_outputs": {
            "diff_json": f"references/{experiment}-fix-diff-at{stamp}.json",
            "diff_md": f"references/{experiment}-fix-diff-at{stamp}.md",
        },
        "next_actions": [
            "validate pre/post metric key alignment",
            "compute delta and reduction metrics",
            "write before/after diff json",
            "write before/after diff markdown",
        ],
        "notes": [
            "pre-fix artifact 없이 diff 단계로 넘어가지 않는다",
            "before와 after는 같은 metric set을 사용해야 한다",
            "debug evidence는 diff 해석 입력으로 유지한다",
        ],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
