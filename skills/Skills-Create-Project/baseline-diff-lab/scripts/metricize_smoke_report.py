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


def _load_report(path: Path) -> dict[str, object]:
    if not path.is_file():
        _err(f"파일 없음: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        _err("raw smoke report 형식이 dict가 아님")
    return payload


def _count_list(payload: dict[str, object], key: str) -> int:
    raw = payload.get(key, [])
    if not isinstance(raw, list):
        _err(f"{key} 형식이 list가 아님")
    return len(raw)


def _metricize(payload: dict[str, object], source: str) -> dict[str, object]:
    missing_in_code_count = _count_list(payload, "missing_in_code")
    missing_in_doc_count = _count_list(payload, "missing_in_doc")
    mismatch_count = _count_list(payload, "mismatch")
    typed_mismatch_count = _count_list(payload, "typed_mismatch")
    total_finding_count = (
        missing_in_code_count
        + missing_in_doc_count
        + mismatch_count
        + typed_mismatch_count
    )

    return {
        "status": "metricized",
        "source_type": "raw_smoke_report",
        "measured_at": _now_iso(),
        "source": source,
        "scope": payload.get("scope"),
        "rule_kind": payload.get("rule_kind"),
        "pair": payload.get("pair"),
        "metrics": {
            "missing_in_code_count": missing_in_code_count,
            "missing_in_doc_count": missing_in_doc_count,
            "mismatch_count": mismatch_count,
            "typed_mismatch_count": typed_mismatch_count,
            "total_finding_count": total_finding_count,
            "zero_drift_pair_rate": 1.0 if total_finding_count == 0 else 0.0,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert raw smoke report into baseline-diff metric artifact")
    parser.add_argument("--input", required=True, help="raw smoke report path")
    parser.add_argument("--output-json", help="optional output metric artifact path")
    args = parser.parse_args()

    input_path = Path(args.input)
    raw_payload = _load_report(input_path)
    metricized = _metricize(raw_payload, str(input_path))

    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(metricized, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(metricized, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
