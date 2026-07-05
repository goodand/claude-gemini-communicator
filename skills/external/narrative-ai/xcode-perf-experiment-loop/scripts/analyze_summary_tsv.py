#!/usr/bin/env python3
import argparse
import csv
import json
import math
import re
from pathlib import Path

NUMERIC_KEYS = {
    "launch_to_carousel_ms",
    "launch_path_network_calls",
    "native_fetch_ms",
    "native_fetch_measured_ms",
    "album_scan_ms",
    "album_collection_fetch_ms",
    "album_asset_fetch_ms",
    "album_enumerate_ms",
    "album_set_insert_ms",
    "asset_query_ms",
    "payload_build_ms",
    "payload_location_ms",
    "payload_resource_lookup_ms",
    "payload_dict_assembly_ms",
    "fetch_total_count",
    "fetch_result_count",
    "js_ranking_ms",
    "ranked_asset_count",
    "target_asset_count",
    "total_count",
    "daily_items_count",
    "render_shell_ms",
    "current_thumbnail_roundtrip_ms",
    "current_thumbnail_base64_chars",
    "current_geocode_ms",
    "current_photo_detail_ms",
    "paint_finalize_ms",
    "items",
    "current_index",
}

BOOL_KEYS = {"current_geocode_cache_hit"}
KV_RE = re.compile(r"([A-Za-z0-9_]+)=([^\s]+)")


def parse_perf_line(perf_line: str) -> dict:
    values = {}
    for key, raw in KV_RE.findall(perf_line or ""):
        if key in NUMERIC_KEYS:
            try:
                values[key] = float(raw)
            except ValueError:
                continue
        elif key in BOOL_KEYS:
            values[key] = raw.lower() == "true"
        else:
            values[key] = raw
    return values


def nearest_rank(values, pct: float) -> float:
    ordered = sorted(values)
    idx = max(0, math.ceil(pct * len(ordered)) - 1)
    return ordered[idx]


def avg(rows, key: str):
    vals = [row[key] for row in rows if key in row and isinstance(row[key], (int, float))]
    if not vals:
        return None
    return sum(vals) / len(vals)


def pct_share(part, whole):
    if part is None or whole in (None, 0):
        return None
    return (part / whole) * 100.0


def detect_amplified_delay(rows: list[dict]) -> list[str]:
    findings = []
    geocode_like = 0
    thumb_like = 0
    for row in rows:
        detail = row.get("current_photo_detail_ms")
        geo = row.get("current_geocode_ms")
        thumb = row.get("current_thumbnail_roundtrip_ms")
        if detail is None:
            continue
        if geo is not None and abs(detail - geo) <= 5:
            geocode_like += 1
        if thumb is not None and abs(detail - thumb) <= 5:
            thumb_like += 1
    if geocode_like == len(rows) and rows:
        findings.append("current_geocode_ms dominates current_photo_detail_ms across all runs")
    elif geocode_like >= max(3, len(rows) - 1):
        findings.append("current_geocode_ms dominates current_photo_detail_ms in most runs")
    if thumb_like == len(rows) and rows:
        findings.append("current_thumbnail_roundtrip_ms dominates current_photo_detail_ms across all runs")
    if avg(rows, "launch_path_network_calls") not in (None, 0):
        findings.append("launch path still contains external network calls")
    return findings


def build_report(rows: list[dict], target_ms: float) -> dict:
    launch_values = [row["launch_to_carousel_ms"] for row in rows if "launch_to_carousel_ms" in row]
    if not launch_values:
        raise ValueError("No launch_to_carousel_ms values found")

    p50 = nearest_rank(launch_values, 0.50)
    p95 = nearest_rank(launch_values, 0.95)
    max_v = max(launch_values)

    launch_avg = avg(rows, "launch_to_carousel_ms")
    native_avg = avg(rows, "native_fetch_ms")
    native_measured_avg = avg(rows, "native_fetch_measured_ms")
    album_scan_avg = avg(rows, "album_scan_ms")
    album_collection_fetch_avg = avg(rows, "album_collection_fetch_ms")
    album_asset_fetch_avg = avg(rows, "album_asset_fetch_ms")
    album_enumerate_avg = avg(rows, "album_enumerate_ms")
    album_set_insert_avg = avg(rows, "album_set_insert_ms")
    asset_query_avg = avg(rows, "asset_query_ms")
    payload_build_avg = avg(rows, "payload_build_ms")
    payload_location_avg = avg(rows, "payload_location_ms")
    payload_resource_lookup_avg = avg(rows, "payload_resource_lookup_ms")
    payload_dict_assembly_avg = avg(rows, "payload_dict_assembly_ms")
    detail_avg = avg(rows, "current_photo_detail_ms")
    geocode_avg = avg(rows, "current_geocode_ms")
    thumb_avg = avg(rows, "current_thumbnail_roundtrip_ms")
    paint_avg = avg(rows, "paint_finalize_ms")
    js_avg = avg(rows, "js_ranking_ms")

    cumulative = {
        "native_fetch_share_pct": pct_share(native_avg, launch_avg),
        "album_scan_share_pct": pct_share(album_scan_avg, launch_avg),
        "album_collection_fetch_share_pct": pct_share(album_collection_fetch_avg, launch_avg),
        "album_asset_fetch_share_pct": pct_share(album_asset_fetch_avg, launch_avg),
        "album_enumerate_share_pct": pct_share(album_enumerate_avg, launch_avg),
        "album_set_insert_share_pct": pct_share(album_set_insert_avg, launch_avg),
        "asset_query_share_pct": pct_share(asset_query_avg, launch_avg),
        "payload_build_share_pct": pct_share(payload_build_avg, launch_avg),
        "payload_location_share_pct": pct_share(payload_location_avg, launch_avg),
        "payload_resource_lookup_share_pct": pct_share(payload_resource_lookup_avg, launch_avg),
        "payload_dict_assembly_share_pct": pct_share(payload_dict_assembly_avg, launch_avg),
        "photo_detail_share_pct": pct_share(detail_avg, launch_avg),
        "paint_share_pct": pct_share(paint_avg, launch_avg),
        "js_ranking_share_pct": pct_share(js_avg, launch_avg),
    }

    critical = []
    candidates = {
        "native_fetch_ms": native_avg,
        "native_fetch_measured_ms": native_measured_avg,
        "album_scan_ms": album_scan_avg,
        "album_collection_fetch_ms": album_collection_fetch_avg,
        "album_asset_fetch_ms": album_asset_fetch_avg,
        "album_enumerate_ms": album_enumerate_avg,
        "album_set_insert_ms": album_set_insert_avg,
        "asset_query_ms": asset_query_avg,
        "payload_build_ms": payload_build_avg,
        "payload_location_ms": payload_location_avg,
        "payload_resource_lookup_ms": payload_resource_lookup_avg,
        "payload_dict_assembly_ms": payload_dict_assembly_avg,
        "current_photo_detail_ms": detail_avg,
        "current_geocode_ms": geocode_avg,
        "current_thumbnail_roundtrip_ms": thumb_avg,
        "paint_finalize_ms": paint_avg,
        "js_ranking_ms": js_avg,
    }
    for key, value in sorted(candidates.items(), key=lambda item: (item[1] is None, -(item[1] or 0))):
        if value is not None:
            critical.append({"metric": key, "avg_ms": round(value, 1)})

    return {
        "runs": len(rows),
        "p50_ms": round(p50, 1),
        "p95_ms": round(p95, 1),
        "max_ms": round(max_v, 1),
        "target_ms": target_ms,
        "pass": p95 <= target_ms,
        "averages_ms": {
            "launch_to_carousel_ms": round(launch_avg, 1) if launch_avg is not None else None,
            "native_fetch_ms": round(native_avg, 1) if native_avg is not None else None,
            "native_fetch_measured_ms": round(native_measured_avg, 1) if native_measured_avg is not None else None,
            "album_scan_ms": round(album_scan_avg, 1) if album_scan_avg is not None else None,
            "album_collection_fetch_ms": round(album_collection_fetch_avg, 1)
            if album_collection_fetch_avg is not None
            else None,
            "album_asset_fetch_ms": round(album_asset_fetch_avg, 1)
            if album_asset_fetch_avg is not None
            else None,
            "album_enumerate_ms": round(album_enumerate_avg, 1) if album_enumerate_avg is not None else None,
            "album_set_insert_ms": round(album_set_insert_avg, 1) if album_set_insert_avg is not None else None,
            "asset_query_ms": round(asset_query_avg, 1) if asset_query_avg is not None else None,
            "payload_build_ms": round(payload_build_avg, 1) if payload_build_avg is not None else None,
            "payload_location_ms": round(payload_location_avg, 1) if payload_location_avg is not None else None,
            "payload_resource_lookup_ms": round(payload_resource_lookup_avg, 1)
            if payload_resource_lookup_avg is not None
            else None,
            "payload_dict_assembly_ms": round(payload_dict_assembly_avg, 1)
            if payload_dict_assembly_avg is not None
            else None,
            "current_photo_detail_ms": round(detail_avg, 1) if detail_avg is not None else None,
            "current_geocode_ms": round(geocode_avg, 1) if geocode_avg is not None else None,
            "current_thumbnail_roundtrip_ms": round(thumb_avg, 1) if thumb_avg is not None else None,
            "paint_finalize_ms": round(paint_avg, 1) if paint_avg is not None else None,
            "js_ranking_ms": round(js_avg, 1) if js_avg is not None else None,
            "launch_path_network_calls": round(avg(rows, "launch_path_network_calls"), 1)
            if avg(rows, "launch_path_network_calls") is not None
            else None,
        },
        "cumulative_delay": {
            key: round(value, 1) if value is not None else None
            for key, value in cumulative.items()
        },
        "amplified_delay_findings": detect_amplified_delay(rows),
        "critical_path_candidates": critical,
    }


def load_rows(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row.get("status") != "ok":
                continue
            parsed = parse_perf_line(row.get("perf_line", ""))
            if row.get("launch_to_carousel_ms"):
                parsed.setdefault("launch_to_carousel_ms", float(row["launch_to_carousel_ms"]))
            rows.append(parsed)
    return rows


def print_text(report: dict):
    print(f"runs={report['runs']}")
    print(f"p50_ms={report['p50_ms']}")
    print(f"p95_ms={report['p95_ms']}")
    print(f"max_ms={report['max_ms']}")
    print(f"target_ms={report['target_ms']}")
    print(f"pass={str(report['pass']).lower()}")
    print("averages_ms:")
    for key, value in report["averages_ms"].items():
        print(f"  {key}={value}")
    print("cumulative_delay_share_pct:")
    for key, value in report["cumulative_delay"].items():
        print(f"  {key}={value}")
    print("critical_path_candidates:")
    for item in report["critical_path_candidates"]:
        print(f"  {item['metric']}={item['avg_ms']}")
    print("amplified_delay_findings:")
    for finding in report["amplified_delay_findings"]:
        print(f"  - {finding}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("summary_tsv", type=Path)
    parser.add_argument("--target-ms", type=float, default=2000.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    rows = load_rows(args.summary_tsv)
    report = build_report(rows, args.target_ms)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text(report)


if __name__ == "__main__":
    main()
