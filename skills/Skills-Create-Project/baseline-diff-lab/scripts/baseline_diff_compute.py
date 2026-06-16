#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


KST = timezone(timedelta(hours=9))


def _err(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.exit(1)


def _now_iso() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


def _load_json(path: Path) -> object:
    if not path.is_file():
        _err(f"파일 없음: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_metric_value(payload: object, metric_name: str) -> float | int | None:
    if not isinstance(payload, dict):
        _err("metric payload 형식이 dict가 아님")

    metrics = payload.get("metrics")
    if not isinstance(metrics, dict):
        _err("metrics dict가 없음")
    if metric_name not in metrics:
        _err(f"metric 없음: {metric_name}")

    raw = metrics[metric_name]
    if isinstance(raw, (int, float)) or raw is None:
        return raw
    if isinstance(raw, dict):
        value = raw.get("value")
        if isinstance(value, (int, float)) or value is None:
            return value
    _err(f"metric 값 형식이 지원되지 않음: {metric_name}")
    raise AssertionError("unreachable")


def _metric_entry(pre_payload: object, post_payload: object, metric_name: str) -> dict[str, object]:
    before = _extract_metric_value(pre_payload, metric_name)
    after = _extract_metric_value(post_payload, metric_name)
    delta = None
    relative_change = None
    reduction_after_fix = None

    if isinstance(before, (int, float)) and isinstance(after, (int, float)):
        delta = after - before
        if before != 0:
            relative_change = (after - before) / abs(before)
            reduction_after_fix = (before - after) / before

    return {
        "before": before,
        "after": after,
        "delta": delta,
        "relative_change": relative_change,
        "reduction_after_fix": reduction_after_fix,
        "formula": {
            "delta": "after - before",
            "relative_change": "(after - before) / abs(before)",
            "reduction_after_fix": "(before - after) / before",
        },
    }


def _load_plan(path: Path) -> dict[str, object]:
    payload = _load_json(path)
    if not isinstance(payload, dict):
        _err("plan JSON 형식이 잘못됨")
    return payload


def _resolve_from_plan(plan: dict[str, object]) -> tuple[str, Path, Path, list[str], list[str], str | None, str | None]:
    inputs = plan.get("inputs")
    outputs = plan.get("suggested_outputs")
    if not isinstance(inputs, dict):
        _err("plan.inputs 없음")
    if not isinstance(outputs, dict):
        _err("plan.suggested_outputs 없음")

    pre = inputs.get("pre_fix")
    post = inputs.get("post_fix")
    metrics = inputs.get("metrics")
    debug = inputs.get("debug_evidence", [])
    experiment = plan.get("experiment")
    diff_json = outputs.get("diff_json")
    diff_md = outputs.get("diff_md")

    if not isinstance(pre, str) or not isinstance(post, str):
        _err("plan pre/post 경로 형식이 잘못됨")
    if not isinstance(metrics, list) or not all(isinstance(item, str) for item in metrics):
        _err("plan metrics 형식이 잘못됨")
    if not isinstance(debug, list) or not all(isinstance(item, str) for item in debug):
        _err("plan debug_evidence 형식이 잘못됨")

    return (
        str(experiment or "baseline-diff"),
        Path(pre),
        Path(post),
        list(metrics),
        list(debug),
        diff_json if isinstance(diff_json, str) else None,
        diff_md if isinstance(diff_md, str) else None,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Baseline Diff Report",
        "",
        f"- experiment: `{payload['experiment']}`",
        f"- computed_at: `{payload['computed_at']}`",
        f"- pre_fix: `{payload['inputs']['pre_fix']}`",
        f"- post_fix: `{payload['inputs']['post_fix']}`",
        "",
        "## Metrics",
        "",
    ]

    metrics = payload["metrics"]
    assert isinstance(metrics, dict)
    for name, entry in metrics.items():
        assert isinstance(entry, dict)
        lines.append(f"- `{name}`")
        lines.append(f"  - before: `{entry['before']}`")
        lines.append(f"  - after: `{entry['after']}`")
        lines.append(f"  - delta: `{entry['delta']}`")
        lines.append(f"  - relative_change: `{entry['relative_change']}`")
        lines.append(f"  - reduction_after_fix: `{entry['reduction_after_fix']}`")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute before/after baseline diff metrics")
    parser.add_argument("--plan", help="planner output JSON")
    parser.add_argument("--experiment", help="explicit experiment name")
    parser.add_argument("--pre", help="pre-fix baseline artifact path")
    parser.add_argument("--post", help="post-fix baseline artifact path")
    parser.add_argument("--metric", action="append", default=[], help="metric name (repeatable)")
    parser.add_argument("--debug", action="append", default=[], help="debug evidence path (repeatable)")
    parser.add_argument("--output-json", help="output diff json path")
    parser.add_argument("--output-md", help="output diff markdown path")
    args = parser.parse_args()

    if args.plan:
        plan = _load_plan(Path(args.plan))
        experiment, pre_path, post_path, metrics, debug_evidence, planned_json, planned_md = _resolve_from_plan(plan)
        output_json = args.output_json or planned_json
        output_md = args.output_md or planned_md
        if args.experiment:
            experiment = args.experiment
    else:
        if not args.pre or not args.post or not args.metric:
            _err("--plan 또는 (--pre, --post, --metric...) 중 하나가 필요함")
        experiment = args.experiment or Path(args.pre).stem
        pre_path = Path(args.pre)
        post_path = Path(args.post)
        metrics = args.metric
        debug_evidence = args.debug
        output_json = args.output_json
        output_md = args.output_md

    pre_payload = _load_json(pre_path)
    post_payload = _load_json(post_path)

    metric_entries = {metric: _metric_entry(pre_payload, post_payload, metric) for metric in metrics}
    payload = {
        "status": "computed",
        "experiment": experiment,
        "computed_at": _now_iso(),
        "inputs": {
            "pre_fix": str(pre_path),
            "post_fix": str(post_path),
            "debug_evidence": debug_evidence,
            "metrics": metrics,
        },
        "metrics": metric_entries,
    }

    if output_json:
        _write(Path(output_json), json.dumps(payload, indent=2, ensure_ascii=False))
    if output_md:
        _write(Path(output_md), _render_markdown(payload))

    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
