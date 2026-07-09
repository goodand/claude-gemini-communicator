#!/usr/bin/env python3
"""dependency-slice-planner v0.1.

Usage:
    python3 dependency_slice_planner.py emit-slice-manifest-contract
    python3 dependency_slice_planner.py validate-slice-manifest --input-manifest <file>
    python3 dependency_slice_planner.py emit-handoff-packet-contract
    python3 dependency_slice_planner.py validate-handoff-packet --input-packet <file>
    python3 dependency_slice_planner.py emit-inventory-snapshot-contract
    python3 dependency_slice_planner.py validate-inventory-snapshot --input-snapshot <file>
    python3 dependency_slice_planner.py emit-slice-seed-candidates-contract
    python3 dependency_slice_planner.py validate-slice-seed-candidates --input-candidates <file>
    python3 dependency_slice_planner.py emit-static-dependency-overlay-contract
    python3 dependency_slice_planner.py validate-static-dependency-overlay --input-overlay <file>
    python3 dependency_slice_planner.py emit-runtime-overlay-contract
    python3 dependency_slice_planner.py validate-runtime-overlay --input-runtime-overlay <file>
    python3 dependency_slice_planner.py emit-unobserved-path-register-contract
    python3 dependency_slice_planner.py build-unobserved-path-register --input-runtime-overlay <file>
    python3 dependency_slice_planner.py validate-unobserved-path-register --input-unobserved-path-register <file>
    python3 dependency_slice_planner.py emit-inventory-path-index-contract
    python3 dependency_slice_planner.py validate-inventory-path-index --input-path-index <file>
    python3 dependency_slice_planner.py emit-seed-refinement-report-contract
    python3 dependency_slice_planner.py build-seed-refinement-report --input-snapshot <file> --input-candidates <file> --input-overlay <file> [--input-runtime-overlay <file>]
    python3 dependency_slice_planner.py emit-stop-rule-evaluation-contract
    python3 dependency_slice_planner.py evaluate-stop-rules --input-refinement-report <file>
    python3 dependency_slice_planner.py emit-final-slice-proposal-contract
    python3 dependency_slice_planner.py build-final-slice-proposal --input-stop-rule-evaluation <file> [--input-path-index <file>]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


KST = timezone(timedelta(hours=9))
CLASSIFICATION_ENUM = ["write_safe", "analysis_only"]
TOP_LEVEL_REQUIRED = ["slice_count", "slices"]
SLICE_REQUIRED_FIELDS = [
    "slice_id",
    "root_dirs",
    "files",
    "entrypoints",
    "classification",
    "reason",
]
HANDOFF_PACKET_REQUIRED_FIELDS = [
    "slice_id",
    "root_dirs",
    "files",
    "entrypoints",
    "allowed_paths",
    "non_goals",
    "upstream_artifacts",
]
INVENTORY_SNAPSHOT_REQUIRED_FIELDS = [
    "root_path",
    "file_count",
    "total_bytes",
    "language_buckets",
    "manifest_files",
    "known_entrypoints",
]
SEED_ACTION_ENUM = ["keep", "merge_candidate", "split_candidate", "stop_candidate"]
SEED_TOP_LEVEL_REQUIRED = ["candidate_count", "candidates"]
SEED_REQUIRED_FIELDS = [
    "candidate_id",
    "root_dir",
    "file_count",
    "total_bytes",
    "max_depth",
    "seed_action",
    "tags",
    "reason",
]
STATIC_OVERLAY_TOP_LEVEL_REQUIRED = ["overlay_count", "overlays"]
STATIC_OVERLAY_REQUIRED_FIELDS = [
    "overlay_id",
    "root_path",
    "source_import_edges",
    "manifest_edges",
    "wrapper_path_edges",
    "cross_region_edges",
    "shared_hubs",
    "anomaly_ledger",
    "reason",
]
RUNTIME_OVERLAY_TOP_LEVEL_REQUIRED = ["runtime_overlay_count", "runtime_overlays", "unobserved_path_count", "unobserved_paths"]
RUNTIME_OVERLAY_REQUIRED_FIELDS = [
    "overlay_id",
    "root_path",
    "observed_runtime_edges",
    "probe_entrypoints",
    "confidence_adjustments",
    "reason",
]
UNOBSERVED_PATH_REGISTER_TOP_LEVEL_REQUIRED = [
    "status",
    "generated_at",
    "algorithm_family",
    "version",
    "input_artifacts",
    "register_count",
    "registers",
    "next_candidate",
]
UNOBSERVED_PATH_REGISTER_REQUIRED_FIELDS = [
    "root_path",
    "unobserved_paths",
    "suggested_probe_entrypoints",
    "reason",
]
UNOBSERVED_PATH_REGISTER_MAX_PATHS = 8
UNOBSERVED_PATH_REGISTER_MAX_SUGGESTIONS = 4
UNOBSERVED_PATH_REGISTER_SIGNAL = "unobserved_path_register"
PATH_INDEX_TOP_LEVEL_REQUIRED = ["root_path", "file_record_count", "file_records"]
PATH_INDEX_REQUIRED_FIELDS = ["path", "is_entrypoint"]
PATH_INDEX_OPTIONAL_FIELDS = ["language", "byte_count"]
REFINEMENT_RECOMMENDATION_ENUM = [
    "keep_seed",
    "merge_with_neighbor",
    "re_cut_with_dependency_overlay",
    "mark_analysis_only",
    "stop_split",
]
REFINEMENT_REPORT_TOP_LEVEL_REQUIRED = [
    "status",
    "generated_at",
    "algorithm_family",
    "version",
    "input_artifacts",
    "runtime_overlay_used",
    "recommendation_count",
    "recommendations",
    "next_candidate",
]
REFINEMENT_REPORT_REQUIRED_FIELDS = [
    "candidate_id",
    "root_dir",
    "seed_action",
    "recommendation",
    "target_candidate_ids",
    "scores",
    "signal_counts",
    "risk_signals",
    "reason",
]
STOP_RULE_DECISION_ENUM = ["write_safe", "analysis_only", "do_not_split"]
STOP_RULE_TRIGGER_ENUM = [
    "single_large_hub_file",
    "wrapper_indirection_uncertainty",
    "high_cross_edge_density",
    "path_order_runtime_dependence",
    "coordination_cost_increase",
]
STOP_RULE_EVALUATION_TOP_LEVEL_REQUIRED = [
    "status",
    "generated_at",
    "algorithm_family",
    "version",
    "input_artifacts",
    "evaluation_count",
    "decision_summary",
    "evaluations",
    "next_candidate",
]
STOP_RULE_EVALUATION_REQUIRED_FIELDS = [
    "candidate_id",
    "root_dir",
    "refinement_recommendation",
    "stop_decision",
    "triggered_stop_rules",
    "scores",
    "signal_counts",
    "reason",
]
FINAL_SLICE_PROPOSAL_TOP_LEVEL_REQUIRED = [
    "status",
    "generated_at",
    "algorithm_family",
    "version",
    "input_artifacts",
    "parallel_slice_count",
    "write_safe_slice_count",
    "analysis_only_slice_count",
    "do_not_split_count",
    "parallel_slices",
    "write_safe_slices",
    "analysis_only_slices",
    "do_not_split_regions",
    "slice_manifest",
    "handoff_packet_count",
    "handoff_packets",
    "next_candidate",
]
FINAL_SLICE_REQUIRED_FIELDS = [
    "slice_id",
    "root_dirs",
    "files",
    "entrypoints",
    "classification",
    "source_candidate_id",
    "reason",
]
FINAL_SLICE_OPTIONAL_FIELDS = [
    "language_buckets",
    "total_bytes",
]
DO_NOT_SPLIT_REQUIRED_FIELDS = [
    "candidate_id",
    "root_dir",
    "triggered_stop_rules",
    "reason",
]


def _now_iso() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


def _err(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    raise SystemExit(1)


def _relative_or_str(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _load_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        _err(f"파일이 없습니다: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        _err(f"JSON artifact가 dict가 아닙니다: {path}")
    return payload


def emit_slice_manifest_contract() -> dict[str, object]:
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "slice_manifest_contract",
        "version": "v0.1.0",
        "required_top_level_fields": TOP_LEVEL_REQUIRED,
        "slice_required_fields": SLICE_REQUIRED_FIELDS,
        "classification_enum": CLASSIFICATION_ENUM,
        "top_level_schema": {
            "slice_count": "int",
            "slices": "list[dict]",
        },
        "slice_field_schema": {
            "slice_id": "str",
            "root_dirs": "list[str]",
            "files": "list[str]",
            "entrypoints": "list[str]",
            "classification": "enum(write_safe|analysis_only)",
            "reason": "str",
        },
    }


def emit_handoff_packet_contract() -> dict[str, object]:
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "handoff_packet_contract",
        "version": "v0.1.0",
        "required_fields": HANDOFF_PACKET_REQUIRED_FIELDS,
        "field_schema": {
            "slice_id": "str",
            "root_dirs": "list[str]",
            "files": "list[str]",
            "entrypoints": "list[str]",
            "allowed_paths": "list[str]",
            "non_goals": "list[str]",
            "upstream_artifacts": "list[str]",
        },
    }


def emit_inventory_snapshot_contract() -> dict[str, object]:
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "inventory_snapshot_contract",
        "version": "v0.1.0",
        "required_fields": INVENTORY_SNAPSHOT_REQUIRED_FIELDS,
        "field_schema": {
            "root_path": "str",
            "file_count": "int",
            "total_bytes": "int",
            "language_buckets": "dict[str,int]",
            "manifest_files": "list[str]",
            "known_entrypoints": "list[str]",
        },
    }


def emit_slice_seed_candidates_contract() -> dict[str, object]:
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "slice_seed_candidates_contract",
        "version": "v0.1.0",
        "required_top_level_fields": SEED_TOP_LEVEL_REQUIRED,
        "candidate_required_fields": SEED_REQUIRED_FIELDS,
        "seed_action_enum": SEED_ACTION_ENUM,
        "top_level_schema": {
            "candidate_count": "int",
            "candidates": "list[dict]",
        },
        "candidate_field_schema": {
            "candidate_id": "str",
            "root_dir": "str",
            "file_count": "int",
            "total_bytes": "int",
            "max_depth": "int",
            "seed_action": "enum(keep|merge_candidate|split_candidate|stop_candidate)",
            "tags": "list[str]",
            "reason": "str",
        },
    }


def emit_static_dependency_overlay_contract() -> dict[str, object]:
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "static_dependency_overlay_contract",
        "version": "v0.1.0",
        "required_top_level_fields": STATIC_OVERLAY_TOP_LEVEL_REQUIRED,
        "overlay_required_fields": STATIC_OVERLAY_REQUIRED_FIELDS,
        "top_level_schema": {
            "overlay_count": "int",
            "overlays": "list[dict]",
        },
        "overlay_field_schema": {
            "overlay_id": "str",
            "root_path": "str",
            "source_import_edges": "list[str]",
            "manifest_edges": "list[str]",
            "wrapper_path_edges": "list[str]",
            "cross_region_edges": "list[str]",
            "shared_hubs": "list[str]",
            "anomaly_ledger": "list[str]",
            "reason": "str",
        },
        "signal_fields": [
            "source_import_edges",
            "manifest_edges",
            "wrapper_path_edges",
            "cross_region_edges",
            "shared_hubs",
            "anomaly_ledger",
        ],
    }


def emit_runtime_overlay_contract() -> dict[str, object]:
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "runtime_overlay_contract",
        "version": "v0.1.0",
        "required_top_level_fields": RUNTIME_OVERLAY_TOP_LEVEL_REQUIRED,
        "overlay_required_fields": RUNTIME_OVERLAY_REQUIRED_FIELDS,
        "top_level_schema": {
            "runtime_overlay_count": "int",
            "runtime_overlays": "list[dict]",
            "unobserved_path_count": "int",
            "unobserved_paths": "list[str]",
        },
        "overlay_field_schema": {
            "overlay_id": "str",
            "root_path": "str",
            "observed_runtime_edges": "list[str]",
            "probe_entrypoints": "list[str]",
            "confidence_adjustments": "list[str]",
            "reason": "str",
        },
        "signal_fields": [
            "observed_runtime_edges",
            "probe_entrypoints",
            "confidence_adjustments",
            "unobserved_paths",
        ],
    }


def emit_unobserved_path_register_contract() -> dict[str, object]:
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": UNOBSERVED_PATH_REGISTER_SIGNAL,
        "version": "v0.1.0",
        "required_top_level_fields": UNOBSERVED_PATH_REGISTER_TOP_LEVEL_REQUIRED,
        "register_required_fields": UNOBSERVED_PATH_REGISTER_REQUIRED_FIELDS,
        "top_level_schema": {
            "status": "enum(ok|invalid_inputs)",
            "generated_at": "str",
            "algorithm_family": "str",
            "version": "str",
            "input_artifacts": "dict[str,str]",
            "register_count": "int",
            "registers": "list[dict]",
            "next_candidate": "str|None",
        },
        "register_field_schema": {
            "root_path": "str",
            "unobserved_paths": f"list[str] (<= {UNOBSERVED_PATH_REGISTER_MAX_PATHS} after bound)",
            "suggested_probe_entrypoints": f"list[str] (<= {UNOBSERVED_PATH_REGISTER_MAX_SUGGESTIONS} after bound)",
            "reason": "str",
        },
        "bounding_rules": {
            "max_paths_per_register": UNOBSERVED_PATH_REGISTER_MAX_PATHS,
            "max_suggested_probe_entrypoints": UNOBSERVED_PATH_REGISTER_MAX_SUGGESTIONS,
        },
    }


def emit_inventory_path_index_contract() -> dict[str, object]:
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "inventory_path_index_contract",
        "version": "v0.1.0",
        "required_top_level_fields": PATH_INDEX_TOP_LEVEL_REQUIRED,
        "record_required_fields": PATH_INDEX_REQUIRED_FIELDS,
        "record_optional_fields": PATH_INDEX_OPTIONAL_FIELDS,
        "top_level_schema": {
            "root_path": "str",
            "file_record_count": "int",
            "file_records": "list[dict]",
        },
        "record_field_schema": {
            "path": "str",
            "is_entrypoint": "bool",
            "language": "str|omitted",
            "byte_count": "int|omitted",
        },
    }


def emit_seed_refinement_report_contract() -> dict[str, object]:
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "seed_refinement_report_contract",
        "version": "v0.1.0",
        "required_top_level_fields": REFINEMENT_REPORT_TOP_LEVEL_REQUIRED,
        "recommendation_required_fields": REFINEMENT_REPORT_REQUIRED_FIELDS,
        "recommendation_enum": REFINEMENT_RECOMMENDATION_ENUM,
        "top_level_schema": {
            "status": "enum(ok|invalid_inputs)",
            "generated_at": "str",
            "algorithm_family": "str",
            "version": "str",
            "input_artifacts": "dict[str,str|None]",
            "runtime_overlay_used": "bool",
            "recommendation_count": "int",
            "recommendations": "list[dict]",
            "next_candidate": "str|None",
        },
        "recommendation_field_schema": {
            "candidate_id": "str",
            "root_dir": "str",
            "seed_action": "str",
            "recommendation": "enum(keep_seed|merge_with_neighbor|re_cut_with_dependency_overlay|mark_analysis_only|stop_split)",
            "target_candidate_ids": "list[str]",
            "scores": "dict[str,float]",
            "signal_counts": "dict[str,int]",
            "risk_signals": "list[str]",
            "reason": "str",
        },
    }


def emit_stop_rule_evaluation_contract() -> dict[str, object]:
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "stop_rule_evaluation_contract",
        "version": "v0.1.0",
        "required_top_level_fields": STOP_RULE_EVALUATION_TOP_LEVEL_REQUIRED,
        "evaluation_required_fields": STOP_RULE_EVALUATION_REQUIRED_FIELDS,
        "decision_enum": STOP_RULE_DECISION_ENUM,
        "trigger_enum": STOP_RULE_TRIGGER_ENUM,
        "top_level_schema": {
            "status": "enum(ok|invalid_inputs)",
            "generated_at": "str",
            "algorithm_family": "str",
            "version": "str",
            "input_artifacts": "dict[str,str]",
            "evaluation_count": "int",
            "decision_summary": "dict[str,int]",
            "evaluations": "list[dict]",
            "next_candidate": "str|None",
        },
        "evaluation_field_schema": {
            "candidate_id": "str",
            "root_dir": "str",
            "refinement_recommendation": "str",
            "stop_decision": "enum(write_safe|analysis_only|do_not_split)",
            "triggered_stop_rules": "list[str]",
            "scores": "dict[str,float]",
            "signal_counts": "dict[str,int]",
            "reason": "str",
        },
    }


def emit_final_slice_proposal_contract() -> dict[str, object]:
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "final_slice_proposal_contract",
        "version": "v0.1.0",
        "required_top_level_fields": FINAL_SLICE_PROPOSAL_TOP_LEVEL_REQUIRED,
        "slice_required_fields": FINAL_SLICE_REQUIRED_FIELDS,
        "slice_optional_fields": FINAL_SLICE_OPTIONAL_FIELDS,
        "do_not_split_required_fields": DO_NOT_SPLIT_REQUIRED_FIELDS,
        "classification_enum": CLASSIFICATION_ENUM,
        "top_level_schema": {
            "status": "enum(ok|invalid_inputs)",
            "generated_at": "str",
            "algorithm_family": "str",
            "version": "str",
            "input_artifacts": "dict[str,str]",
            "parallel_slice_count": "int",
            "write_safe_slice_count": "int",
            "analysis_only_slice_count": "int",
            "do_not_split_count": "int",
            "parallel_slices": "list[dict]",
            "write_safe_slices": "list[dict]",
            "analysis_only_slices": "list[dict]",
            "do_not_split_regions": "list[dict]",
            "slice_manifest": "dict",
            "handoff_packet_count": "int",
            "handoff_packets": "list[dict]",
            "next_candidate": "null",
        },
        "slice_field_schema": {
            "slice_id": "str",
            "root_dirs": "list[str]",
            "files": "list[str]",
            "entrypoints": "list[str]",
            "classification": "enum(write_safe|analysis_only)",
            "source_candidate_id": "str",
            "reason": "str",
            "language_buckets": "dict[str,int]|omitted",
            "total_bytes": "int|omitted",
        },
        "do_not_split_field_schema": {
            "candidate_id": "str",
            "root_dir": "str",
            "triggered_stop_rules": "list[str]",
            "reason": "str",
        },
    }


def _validate_list_of_strings(value: object, field_name: str, errors: list[str], prefix: str) -> None:
    if not isinstance(value, list):
        errors.append(f"{prefix}{field_name} must be list[str]")
        return
    if not all(isinstance(item, str) and item.strip() for item in value):
        errors.append(f"{prefix}{field_name} must contain non-empty strings")


def _validate_dict_of_nonnegative_ints(value: object, field_name: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{field_name} must be dict[str,int]")
        return
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            errors.append(f"{field_name} keys must be non-empty strings")
            return
        if not isinstance(item, int) or item < 0:
            errors.append(f"{field_name} values must be non-negative int")
            return


def validate_slice_manifest(input_path: Path, payload: dict[str, object]) -> dict[str, object]:
    errors: list[str] = []

    for field in TOP_LEVEL_REQUIRED:
        if field not in payload:
            errors.append(f"missing top-level field: {field}")

    slice_count = payload.get("slice_count")
    if not isinstance(slice_count, int):
        errors.append("slice_count must be int")

    raw_slices = payload.get("slices")
    if not isinstance(raw_slices, list):
        errors.append("slices must be list[dict]")
        raw_slices = []

    classifications: list[str] = []
    for index, raw_slice in enumerate(raw_slices, start=1):
        prefix = f"slices[{index}]."
        if not isinstance(raw_slice, dict):
            errors.append(f"{prefix[:-1]} must be dict")
            continue
        for field in SLICE_REQUIRED_FIELDS:
            if field not in raw_slice:
                errors.append(f"missing field: {prefix}{field}")
        if "slice_id" in raw_slice and not isinstance(raw_slice.get("slice_id"), str):
            errors.append(f"{prefix}slice_id must be str")
        _validate_list_of_strings(raw_slice.get("root_dirs"), "root_dirs", errors, prefix)
        _validate_list_of_strings(raw_slice.get("files"), "files", errors, prefix)
        _validate_list_of_strings(raw_slice.get("entrypoints"), "entrypoints", errors, prefix)
        classification = raw_slice.get("classification")
        if not isinstance(classification, str) or classification not in CLASSIFICATION_ENUM:
            errors.append(f"{prefix}classification must be one of {CLASSIFICATION_ENUM}")
        else:
            classifications.append(classification)
        if "reason" in raw_slice and not isinstance(raw_slice.get("reason"), str):
            errors.append(f"{prefix}reason must be str")

    if isinstance(slice_count, int) and isinstance(raw_slices, list) and slice_count != len(raw_slices):
        errors.append("slice_count must match len(slices)")

    return {
        "status": "valid" if not errors else "invalid",
        "generated_at": _now_iso(),
        "contract_family": "slice_manifest_validation",
        "input_manifest": _relative_or_str(input_path),
        "error_count": len(errors),
        "errors": errors,
        "manifest_summary": {
            "slice_count": slice_count if isinstance(slice_count, int) else None,
            "observed_slice_count": len(raw_slices),
            "classifications": classifications,
        },
    }


def validate_handoff_packet(input_path: Path, payload: dict[str, object]) -> dict[str, object]:
    errors: list[str] = []

    for field in HANDOFF_PACKET_REQUIRED_FIELDS:
        if field not in payload:
            errors.append(f"missing field: {field}")

    if "slice_id" in payload and not isinstance(payload.get("slice_id"), str):
        errors.append("slice_id must be str")

    for list_field in ["root_dirs", "files", "entrypoints", "allowed_paths", "non_goals", "upstream_artifacts"]:
        _validate_list_of_strings(payload.get(list_field), list_field, errors, "")

    return {
        "status": "valid" if not errors else "invalid",
        "generated_at": _now_iso(),
        "contract_family": "handoff_packet_validation",
        "input_packet": _relative_or_str(input_path),
        "error_count": len(errors),
        "errors": errors,
        "packet_summary": {
            "slice_id": payload.get("slice_id") if isinstance(payload.get("slice_id"), str) else None,
            "allowed_path_count": len(payload.get("allowed_paths", [])) if isinstance(payload.get("allowed_paths"), list) else None,
            "upstream_artifact_count": len(payload.get("upstream_artifacts", [])) if isinstance(payload.get("upstream_artifacts"), list) else None,
        },
    }


def validate_inventory_snapshot(input_path: Path, payload: dict[str, object]) -> dict[str, object]:
    errors: list[str] = []

    for field in INVENTORY_SNAPSHOT_REQUIRED_FIELDS:
        if field not in payload:
            errors.append(f"missing field: {field}")

    root_path = payload.get("root_path")
    if "root_path" in payload and (not isinstance(root_path, str) or not root_path.strip()):
        errors.append("root_path must be non-empty str")

    file_count = payload.get("file_count")
    if "file_count" in payload and (not isinstance(file_count, int) or file_count < 0):
        errors.append("file_count must be non-negative int")

    total_bytes = payload.get("total_bytes")
    if "total_bytes" in payload and (not isinstance(total_bytes, int) or total_bytes < 0):
        errors.append("total_bytes must be non-negative int")

    _validate_dict_of_nonnegative_ints(payload.get("language_buckets"), "language_buckets", errors)
    _validate_list_of_strings(payload.get("manifest_files"), "manifest_files", errors, "")
    _validate_list_of_strings(payload.get("known_entrypoints"), "known_entrypoints", errors, "")

    return {
        "status": "valid" if not errors else "invalid",
        "generated_at": _now_iso(),
        "contract_family": "inventory_snapshot_validation",
        "input_snapshot": _relative_or_str(input_path),
        "error_count": len(errors),
        "errors": errors,
        "snapshot_summary": {
            "root_path": root_path if isinstance(root_path, str) and root_path.strip() else None,
            "file_count": file_count if isinstance(file_count, int) and file_count >= 0 else None,
            "manifest_file_count": len(payload.get("manifest_files", [])) if isinstance(payload.get("manifest_files"), list) else None,
            "entrypoint_count": len(payload.get("known_entrypoints", [])) if isinstance(payload.get("known_entrypoints"), list) else None,
            "language_bucket_count": len(payload.get("language_buckets", {})) if isinstance(payload.get("language_buckets"), dict) else None,
        },
    }


def validate_slice_seed_candidates(input_path: Path, payload: dict[str, object]) -> dict[str, object]:
    errors: list[str] = []

    for field in SEED_TOP_LEVEL_REQUIRED:
        if field not in payload:
            errors.append(f"missing top-level field: {field}")

    candidate_count = payload.get("candidate_count")
    if not isinstance(candidate_count, int) or candidate_count < 0:
        errors.append("candidate_count must be non-negative int")

    raw_candidates = payload.get("candidates")
    if not isinstance(raw_candidates, list):
        errors.append("candidates must be list[dict]")
        raw_candidates = []

    seed_actions: list[str] = []
    for index, raw_candidate in enumerate(raw_candidates, start=1):
        prefix = f"candidates[{index}]."
        if not isinstance(raw_candidate, dict):
            errors.append(f"{prefix[:-1]} must be dict")
            continue
        for field in SEED_REQUIRED_FIELDS:
            if field not in raw_candidate:
                errors.append(f"missing field: {prefix}{field}")
        candidate_id = raw_candidate.get("candidate_id")
        if "candidate_id" in raw_candidate and (not isinstance(candidate_id, str) or not candidate_id.strip()):
            errors.append(f"{prefix}candidate_id must be non-empty str")
        root_dir = raw_candidate.get("root_dir")
        if "root_dir" in raw_candidate and (not isinstance(root_dir, str) or not root_dir.strip()):
            errors.append(f"{prefix}root_dir must be non-empty str")
        for int_field in ["file_count", "total_bytes", "max_depth"]:
            value = raw_candidate.get(int_field)
            if int_field in raw_candidate and (not isinstance(value, int) or value < 0):
                errors.append(f"{prefix}{int_field} must be non-negative int")
        seed_action = raw_candidate.get("seed_action")
        if not isinstance(seed_action, str) or seed_action not in SEED_ACTION_ENUM:
            errors.append(f"{prefix}seed_action must be one of {SEED_ACTION_ENUM}")
        else:
            seed_actions.append(seed_action)
        _validate_list_of_strings(raw_candidate.get("tags"), "tags", errors, prefix)
        reason = raw_candidate.get("reason")
        if "reason" in raw_candidate and (not isinstance(reason, str) or not reason.strip()):
            errors.append(f"{prefix}reason must be non-empty str")

    if isinstance(candidate_count, int) and candidate_count >= 0 and candidate_count != len(raw_candidates):
        errors.append("candidate_count must match len(candidates)")

    return {
        "status": "valid" if not errors else "invalid",
        "generated_at": _now_iso(),
        "contract_family": "slice_seed_candidates_validation",
        "input_candidates": _relative_or_str(input_path),
        "error_count": len(errors),
        "errors": errors,
        "candidate_summary": {
            "candidate_count": candidate_count if isinstance(candidate_count, int) and candidate_count >= 0 else None,
            "observed_candidate_count": len(raw_candidates),
            "seed_actions": seed_actions,
        },
    }


def validate_static_dependency_overlay(input_path: Path, payload: dict[str, object]) -> dict[str, object]:
    errors: list[str] = []

    for field in STATIC_OVERLAY_TOP_LEVEL_REQUIRED:
        if field not in payload:
            errors.append(f"missing top-level field: {field}")

    overlay_count = payload.get("overlay_count")
    if not isinstance(overlay_count, int) or overlay_count < 0:
        errors.append("overlay_count must be non-negative int")

    raw_overlays = payload.get("overlays")
    if not isinstance(raw_overlays, list):
        errors.append("overlays must be list[dict]")
        raw_overlays = []

    observed_signal_fields = {
        "source_import_edges": 0,
        "manifest_edges": 0,
        "wrapper_path_edges": 0,
        "cross_region_edges": 0,
        "shared_hubs": 0,
        "anomaly_ledger": 0,
    }

    for index, raw_overlay in enumerate(raw_overlays, start=1):
        prefix = f"overlays[{index}]."
        if not isinstance(raw_overlay, dict):
            errors.append(f"{prefix[:-1]} must be dict")
            continue
        for field in STATIC_OVERLAY_REQUIRED_FIELDS:
            if field not in raw_overlay:
                errors.append(f"missing field: {prefix}{field}")
        overlay_id = raw_overlay.get("overlay_id")
        if "overlay_id" in raw_overlay and (not isinstance(overlay_id, str) or not overlay_id.strip()):
            errors.append(f"{prefix}overlay_id must be non-empty str")
        root_path = raw_overlay.get("root_path")
        if "root_path" in raw_overlay and (not isinstance(root_path, str) or not root_path.strip()):
            errors.append(f"{prefix}root_path must be non-empty str")
        for list_field in [
            "source_import_edges",
            "manifest_edges",
            "wrapper_path_edges",
            "cross_region_edges",
            "shared_hubs",
            "anomaly_ledger",
        ]:
            value = raw_overlay.get(list_field)
            _validate_list_of_strings(value, list_field, errors, prefix)
            if isinstance(value, list):
                observed_signal_fields[list_field] += len(value)
        reason = raw_overlay.get("reason")
        if "reason" in raw_overlay and (not isinstance(reason, str) or not reason.strip()):
            errors.append(f"{prefix}reason must be non-empty str")

    if isinstance(overlay_count, int) and overlay_count >= 0 and overlay_count != len(raw_overlays):
        errors.append("overlay_count must match len(overlays)")

    return {
        "status": "valid" if not errors else "invalid",
        "generated_at": _now_iso(),
        "contract_family": "static_dependency_overlay_validation",
        "input_overlay": _relative_or_str(input_path),
        "error_count": len(errors),
        "errors": errors,
        "overlay_summary": {
            "overlay_count": overlay_count if isinstance(overlay_count, int) and overlay_count >= 0 else None,
            "observed_overlay_count": len(raw_overlays),
            "signal_fields": observed_signal_fields,
        },
    }


def validate_runtime_overlay(input_path: Path, payload: dict[str, object]) -> dict[str, object]:
    errors: list[str] = []

    for field in RUNTIME_OVERLAY_TOP_LEVEL_REQUIRED:
        if field not in payload:
            errors.append(f"missing top-level field: {field}")

    runtime_overlay_count = payload.get("runtime_overlay_count")
    if not isinstance(runtime_overlay_count, int) or runtime_overlay_count < 0:
        errors.append("runtime_overlay_count must be non-negative int")

    unobserved_path_count = payload.get("unobserved_path_count")
    if not isinstance(unobserved_path_count, int) or unobserved_path_count < 0:
        errors.append("unobserved_path_count must be non-negative int")

    raw_overlays = payload.get("runtime_overlays")
    if not isinstance(raw_overlays, list):
        errors.append("runtime_overlays must be list[dict]")
        raw_overlays = []

    unobserved_paths = payload.get("unobserved_paths")
    if not isinstance(unobserved_paths, list):
        errors.append("unobserved_paths must be list[str]")
        unobserved_paths = []
    else:
        _validate_list_of_strings(unobserved_paths, "unobserved_paths", errors, "")

    observed_runtime_edges = 0
    probe_entrypoints = 0
    confidence_adjustments = 0

    for index, raw_overlay in enumerate(raw_overlays, start=1):
        prefix = f"runtime_overlays[{index}]."
        if not isinstance(raw_overlay, dict):
            errors.append(f"{prefix[:-1]} must be dict")
            continue
        for field in RUNTIME_OVERLAY_REQUIRED_FIELDS:
            if field not in raw_overlay:
                errors.append(f"missing field: {prefix}{field}")
        overlay_id = raw_overlay.get("overlay_id")
        if "overlay_id" in raw_overlay and (not isinstance(overlay_id, str) or not overlay_id.strip()):
            errors.append(f"{prefix}overlay_id must be non-empty str")
        root_path = raw_overlay.get("root_path")
        if "root_path" in raw_overlay and (not isinstance(root_path, str) or not root_path.strip()):
            errors.append(f"{prefix}root_path must be non-empty str")
        for list_field in ["observed_runtime_edges", "probe_entrypoints", "confidence_adjustments"]:
            value = raw_overlay.get(list_field)
            _validate_list_of_strings(value, list_field, errors, prefix)
            if isinstance(value, list):
                if list_field == "observed_runtime_edges":
                    observed_runtime_edges += len(value)
                elif list_field == "probe_entrypoints":
                    probe_entrypoints += len(value)
                else:
                    confidence_adjustments += len(value)
        reason = raw_overlay.get("reason")
        if "reason" in raw_overlay and (not isinstance(reason, str) or not reason.strip()):
            errors.append(f"{prefix}reason must be non-empty str")

    if isinstance(runtime_overlay_count, int) and runtime_overlay_count >= 0 and runtime_overlay_count != len(raw_overlays):
        errors.append("runtime_overlay_count must match len(runtime_overlays)")
    if isinstance(unobserved_path_count, int) and unobserved_path_count >= 0 and unobserved_path_count != len(unobserved_paths):
        errors.append("unobserved_path_count must match len(unobserved_paths)")

    return {
        "status": "valid" if not errors else "invalid",
        "generated_at": _now_iso(),
        "contract_family": "runtime_overlay_validation",
        "input_runtime_overlay": _relative_or_str(input_path),
        "error_count": len(errors),
        "errors": errors,
        "runtime_overlay_summary": {
            "runtime_overlay_count": runtime_overlay_count if isinstance(runtime_overlay_count, int) and runtime_overlay_count >= 0 else None,
            "observed_runtime_overlay_count": len(raw_overlays),
            "unobserved_path_count": unobserved_path_count if isinstance(unobserved_path_count, int) and unobserved_path_count >= 0 else None,
            "observed_unobserved_path_count": len(unobserved_paths),
            "observed_runtime_edges": observed_runtime_edges,
            "probe_entrypoints": probe_entrypoints,
            "confidence_adjustments": confidence_adjustments,
        },
    }


def _path_is_under_root(path_value: str, root_dir: str) -> bool:
    if not path_value or not root_dir:
        return False
    normalized_path = path_value.rstrip("/")
    normalized_root = root_dir.rstrip("/")
    return (
        normalized_path == normalized_root
        or normalized_path.startswith(normalized_root + "/")
    )


def _suggest_probe_entrypoints(
    root_path: str,
    overlay_probe_entrypoints: list[str],
    unobserved_paths: list[str],
) -> list[str]:
    candidates: list[str] = []
    for entrypoint in overlay_probe_entrypoints:
        if not isinstance(entrypoint, str) or not entrypoint.strip():
            continue
        if _path_is_under_root(entrypoint, root_path):
            candidates.append(entrypoint)
    for path_value in unobserved_paths:
        if not isinstance(path_value, str) or not path_value.strip():
            continue
        if not _path_is_under_root(path_value, root_path):
            continue
        parent = Path(path_value).parent.as_posix()
        if parent and parent != ".":
            candidates.append(parent)
        else:
            candidates.append(path_value)
    return _dedupe_preserve_order(candidates)[:UNOBSERVED_PATH_REGISTER_MAX_SUGGESTIONS]


def build_unobserved_path_register(
    runtime_overlay_path: Path,
    runtime_overlay_payload: dict[str, object],
) -> tuple[dict[str, object], int]:
    runtime_overlay_validation = validate_runtime_overlay(runtime_overlay_path, runtime_overlay_payload)
    if runtime_overlay_validation["status"] != "valid":
        return (
            {
                "status": "invalid_inputs",
                "generated_at": _now_iso(),
                "algorithm_family": UNOBSERVED_PATH_REGISTER_SIGNAL,
                "version": "v0.1.0",
                "input_artifacts": {
                    "runtime_overlay": _relative_or_str(runtime_overlay_path),
                },
                "register_count": 0,
                "registers": [],
                "invalid_inputs": ["runtime_overlay"],
                "error_count": runtime_overlay_validation["error_count"],
                "errors": runtime_overlay_validation["errors"],
                "next_candidate": "seed_to_refinement_report",
            },
            1,
        )

    raw_unobserved_paths = runtime_overlay_payload.get("unobserved_paths", [])
    if not isinstance(raw_unobserved_paths, list):
        raw_unobserved_paths = []

    registers: list[dict[str, object]] = []
    seen_root_paths: set[str] = set()
    for raw_overlay in runtime_overlay_payload.get("runtime_overlays", []):
        if not isinstance(raw_overlay, dict):
            continue
        root_path = str(raw_overlay.get("root_path", ""))
        if not root_path or root_path in seen_root_paths:
            continue
        seen_root_paths.add(root_path)
        scoped_paths = [path for path in raw_unobserved_paths if _path_is_under_root(path, root_path)]
        bounded_paths = _dedupe_preserve_order([path for path in scoped_paths if isinstance(path, str)])
        if len(bounded_paths) > UNOBSERVED_PATH_REGISTER_MAX_PATHS:
            bounded_paths = bounded_paths[:UNOBSERVED_PATH_REGISTER_MAX_PATHS]
        suggested = _suggest_probe_entrypoints(
            root_path,
            [value for value in raw_overlay.get("probe_entrypoints", []) if isinstance(value, str)],
            scoped_paths,
        )
        reason_parts = [f"unobserved_count={len(scoped_paths)}", f"suggested_count={len(suggested)}"]
        if len(scoped_paths) > len(bounded_paths):
            reason_parts.append(f"bounded_to={UNOBSERVED_PATH_REGISTER_MAX_PATHS}")
        reason = ", ".join(reason_parts)
        registers.append(
            {
                "root_path": root_path,
                "unobserved_paths": bounded_paths,
                "suggested_probe_entrypoints": suggested,
                "reason": reason,
            }
        )

    return (
        {
            "status": "ok",
            "generated_at": _now_iso(),
            "algorithm_family": UNOBSERVED_PATH_REGISTER_SIGNAL,
            "version": "v0.1.0",
            "input_artifacts": {
                "runtime_overlay": _relative_or_str(runtime_overlay_path),
            },
            "register_count": len(registers),
            "registers": registers,
            "next_candidate": "seed_to_refinement_report",
        },
        0,
    )


def validate_unobserved_path_register(
    input_path: Path,
    payload: dict[str, object],
) -> dict[str, object]:
    errors: list[str] = []

    for field in UNOBSERVED_PATH_REGISTER_TOP_LEVEL_REQUIRED:
        if field not in payload:
            errors.append(f"missing top-level field: {field}")

    register_count = payload.get("register_count")
    if not isinstance(register_count, int) or register_count < 0:
        errors.append("register_count must be non-negative int")

    raw_registers = payload.get("registers")
    if not isinstance(raw_registers, list):
        errors.append("registers must be list[dict]")
        raw_registers = []

    input_runtime_overlay = payload.get("input_artifacts", {})
    if not isinstance(input_runtime_overlay, dict):
        errors.append("input_artifacts must be dict[str,str]")
    elif not isinstance(input_runtime_overlay.get("runtime_overlay"), str) or not input_runtime_overlay.get("runtime_overlay", "").strip():
        errors.append("input_artifacts.runtime_overlay must be non-empty str")

    for index, raw_register in enumerate(raw_registers, start=1):
        prefix = f"registers[{index}]."
        if not isinstance(raw_register, dict):
            errors.append(f"{prefix[:-1]} must be dict")
            continue
        for field in UNOBSERVED_PATH_REGISTER_REQUIRED_FIELDS:
            if field not in raw_register:
                errors.append(f"missing field: {prefix}{field}")
        root_path = raw_register.get("root_path")
        if "root_path" in raw_register and (not isinstance(root_path, str) or not root_path.strip()):
            errors.append(f"{prefix}root_path must be non-empty str")
        if "reason" in raw_register and (not isinstance(raw_register.get("reason"), str) or not raw_register.get("reason", "").strip()):
            errors.append(f"{prefix}reason must be non-empty str")
        _validate_list_of_strings(raw_register.get("unobserved_paths"), "unobserved_paths", errors, prefix)
        _validate_list_of_strings(raw_register.get("suggested_probe_entrypoints"), "suggested_probe_entrypoints", errors, prefix)
        if isinstance(raw_register.get("unobserved_paths"), list) and len(raw_register["unobserved_paths"]) > UNOBSERVED_PATH_REGISTER_MAX_PATHS:
            errors.append(f"{prefix}unobserved_paths must contain <= {UNOBSERVED_PATH_REGISTER_MAX_PATHS} items")
        if (
            isinstance(raw_register.get("suggested_probe_entrypoints"), list)
            and len(raw_register["suggested_probe_entrypoints"]) > UNOBSERVED_PATH_REGISTER_MAX_SUGGESTIONS
        ):
            errors.append(
                f"{prefix}suggested_probe_entrypoints must contain <= {UNOBSERVED_PATH_REGISTER_MAX_SUGGESTIONS} items"
            )

    if isinstance(register_count, int) and isinstance(raw_registers, list) and register_count != len(raw_registers):
        errors.append("register_count must match len(registers)")

    return {
        "status": "valid" if not errors else "invalid",
        "generated_at": _now_iso(),
        "contract_family": "unobserved_path_register_validation",
        "input_unobserved_path_register": _relative_or_str(input_path),
        "error_count": len(errors),
        "errors": errors,
    }


def validate_inventory_path_index(input_path: Path, payload: dict[str, object]) -> dict[str, object]:
    errors: list[str] = []

    for field in PATH_INDEX_TOP_LEVEL_REQUIRED:
        if field not in payload:
            errors.append(f"missing top-level field: {field}")

    root_path = payload.get("root_path")
    if "root_path" in payload and (not isinstance(root_path, str) or not root_path.strip()):
        errors.append("root_path must be non-empty str")

    file_record_count = payload.get("file_record_count")
    if not isinstance(file_record_count, int) or file_record_count < 0:
        errors.append("file_record_count must be non-negative int")

    raw_records = payload.get("file_records")
    if not isinstance(raw_records, list):
        errors.append("file_records must be list[dict]")
        raw_records = []

    seen_paths: set[str] = set()
    entrypoint_count = 0
    language_buckets: dict[str, int] = {}
    total_bytes = 0
    metadata_record_count = 0
    for index, raw_record in enumerate(raw_records, start=1):
        prefix = f"file_records[{index}]."
        if not isinstance(raw_record, dict):
            errors.append(f"{prefix[:-1]} must be dict")
            continue
        for field in PATH_INDEX_REQUIRED_FIELDS:
            if field not in raw_record:
                errors.append(f"missing field: {prefix}{field}")
        path_value = raw_record.get("path")
        if not isinstance(path_value, str) or not path_value.strip():
            errors.append(f"{prefix}path must be non-empty str")
        elif path_value in seen_paths:
            errors.append(f"{prefix}path must be unique")
        else:
            seen_paths.add(path_value)
        is_entrypoint = raw_record.get("is_entrypoint")
        if not isinstance(is_entrypoint, bool):
            errors.append(f"{prefix}is_entrypoint must be bool")
        elif is_entrypoint:
            entrypoint_count += 1

        record_has_metadata = False
        language = raw_record.get("language")
        if "language" in raw_record:
            if not isinstance(language, str) or not language.strip():
                errors.append(f"{prefix}language must be non-empty str when present")
            else:
                record_has_metadata = True
                language_buckets[language] = language_buckets.get(language, 0) + 1

        byte_count = raw_record.get("byte_count")
        if "byte_count" in raw_record:
            if not isinstance(byte_count, int) or isinstance(byte_count, bool) or byte_count < 0:
                errors.append(f"{prefix}byte_count must be non-negative int when present")
            else:
                record_has_metadata = True
                total_bytes += byte_count
        if record_has_metadata:
            metadata_record_count += 1

    if isinstance(file_record_count, int) and file_record_count != len(raw_records):
        errors.append("file_record_count must match len(file_records)")

    return {
        "status": "valid" if not errors else "invalid",
        "generated_at": _now_iso(),
        "contract_family": "inventory_path_index_validation",
        "input_path_index": _relative_or_str(input_path),
        "error_count": len(errors),
        "errors": errors,
        "path_index_summary": {
            "root_path": root_path if isinstance(root_path, str) and root_path.strip() else None,
            "file_record_count": file_record_count if isinstance(file_record_count, int) and file_record_count >= 0 else None,
            "entrypoint_count": entrypoint_count,
            "metadata_record_count": metadata_record_count,
            "language_buckets": language_buckets,
            "total_bytes": total_bytes,
        },
    }


def _candidate_matches_overlay(candidate_root: str, overlay_root: str) -> bool:
    if not candidate_root or not overlay_root:
        return False
    normalized_candidate = candidate_root.rstrip("/")
    normalized_overlay = overlay_root.rstrip("/")
    return (
        normalized_candidate == normalized_overlay
        or normalized_candidate.startswith(normalized_overlay + "/")
        or normalized_overlay.startswith(normalized_candidate + "/")
    )


def _count_matching_signals(candidate_root: str, overlay_root: str, values: list[str], exact_match_only: bool = False) -> int:
    if not values or not _candidate_matches_overlay(candidate_root, overlay_root):
        return 0
    if exact_match_only:
        return sum(1 for value in values if candidate_root in value)
    return len(values)


def _compute_size_score(candidate: dict[str, object], inventory: dict[str, object]) -> float:
    inventory_file_count = max(int(inventory.get("file_count", 0) or 0), 1)
    inventory_total_bytes = max(int(inventory.get("total_bytes", 0) or 0), 1)
    candidate_file_count = max(int(candidate.get("file_count", 0) or 0), 0)
    candidate_total_bytes = max(int(candidate.get("total_bytes", 0) or 0), 0)
    max_depth = max(int(candidate.get("max_depth", 0) or 0), 0)

    file_ratio = min(candidate_file_count / inventory_file_count, 2.0)
    byte_ratio = min(candidate_total_bytes / inventory_total_bytes, 2.0)
    score = 1.0

    if max(file_ratio, byte_ratio) > 0.75:
        score -= 0.25
    if min(file_ratio, byte_ratio) < 0.08:
        score -= 0.25
    if max_depth > 5:
        score -= 0.10

    return round(max(0.0, score), 4)


def _build_candidate_signal_counts(
    candidate_root: str,
    static_overlay: dict[str, object],
    runtime_overlay: dict[str, object] | None,
) -> dict[str, int]:
    signal_counts = {
        "source_import_edge_count": 0,
        "manifest_edge_count": 0,
        "wrapper_path_edge_count": 0,
        "cross_region_edge_count": 0,
        "shared_hub_count": 0,
        "anomaly_count": 0,
        "observed_runtime_edge_count": 0,
        "probe_entrypoint_count": 0,
        "confidence_adjustment_count": 0,
        "unobserved_path_count": 0,
    }

    for raw_overlay in static_overlay.get("overlays", []):
        if not isinstance(raw_overlay, dict):
            continue
        overlay_root = str(raw_overlay.get("root_path", ""))
        signal_counts["source_import_edge_count"] += _count_matching_signals(
            candidate_root,
            overlay_root,
            raw_overlay.get("source_import_edges", []),
            exact_match_only=True,
        )
        signal_counts["manifest_edge_count"] += _count_matching_signals(
            candidate_root,
            overlay_root,
            raw_overlay.get("manifest_edges", []),
        )
        signal_counts["wrapper_path_edge_count"] += _count_matching_signals(
            candidate_root,
            overlay_root,
            raw_overlay.get("wrapper_path_edges", []),
            exact_match_only=True,
        )
        signal_counts["cross_region_edge_count"] += _count_matching_signals(
            candidate_root,
            overlay_root,
            raw_overlay.get("cross_region_edges", []),
            exact_match_only=True,
        )
        signal_counts["shared_hub_count"] += _count_matching_signals(
            candidate_root,
            overlay_root,
            raw_overlay.get("shared_hubs", []),
        )
        signal_counts["anomaly_count"] += _count_matching_signals(
            candidate_root,
            overlay_root,
            raw_overlay.get("anomaly_ledger", []),
        )

    if runtime_overlay is not None:
        for raw_overlay in runtime_overlay.get("runtime_overlays", []):
            if not isinstance(raw_overlay, dict):
                continue
            overlay_root = str(raw_overlay.get("root_path", ""))
            signal_counts["observed_runtime_edge_count"] += _count_matching_signals(
                candidate_root,
                overlay_root,
                raw_overlay.get("observed_runtime_edges", []),
                exact_match_only=True,
            )
            signal_counts["probe_entrypoint_count"] += _count_matching_signals(
                candidate_root,
                overlay_root,
                raw_overlay.get("probe_entrypoints", []),
                exact_match_only=True,
            )
            signal_counts["confidence_adjustment_count"] += _count_matching_signals(
                candidate_root,
                overlay_root,
                raw_overlay.get("confidence_adjustments", []),
                exact_match_only=True,
            )
            signal_counts["unobserved_path_count"] += _count_matching_signals(
                candidate_root,
                overlay_root,
                runtime_overlay.get("unobserved_paths", []),
            )

    return signal_counts


def _compute_refinement_scores(signal_counts: dict[str, int], candidate: dict[str, object], inventory: dict[str, object]) -> dict[str, float]:
    total_static_edges = (
        signal_counts["source_import_edge_count"]
        + signal_counts["manifest_edge_count"]
        + signal_counts["wrapper_path_edge_count"]
        + signal_counts["cross_region_edge_count"]
    )
    cross_edge_ratio = round(
        signal_counts["cross_region_edge_count"] / max(total_static_edges, 1),
        4,
    )
    shared_hub_penalty = round(
        min(1.0, signal_counts["shared_hub_count"] / 2.0),
        4,
    )
    runtime_risk = signal_counts["wrapper_path_edge_count"] + signal_counts["unobserved_path_count"]
    runtime_support = signal_counts["observed_runtime_edge_count"] + signal_counts["confidence_adjustment_count"]
    runtime_condition_penalty = round(
        min(1.0, runtime_risk / max(runtime_risk + runtime_support, 1)),
        4,
    )
    ownership_conflict_penalty = round(
        min(
            1.0,
            (
                signal_counts["manifest_edge_count"]
                + signal_counts["cross_region_edge_count"]
            )
            / max(total_static_edges, 1),
        ),
        4,
    )
    size_score = _compute_size_score(candidate, inventory)
    internal_cohesion_score = round(
        max(
            0.0,
            1.0
            - (
                cross_edge_ratio
                + shared_hub_penalty
                + runtime_condition_penalty
                + ownership_conflict_penalty
            )
            / 4.0,
        ),
        4,
    )
    return {
        "size_score": size_score,
        "internal_cohesion_score": internal_cohesion_score,
        "cross_edge_ratio": cross_edge_ratio,
        "shared_hub_penalty": shared_hub_penalty,
        "runtime_condition_penalty": runtime_condition_penalty,
        "ownership_conflict_penalty": ownership_conflict_penalty,
    }


def _recommend_refinement_action(candidate: dict[str, object], scores: dict[str, float]) -> tuple[str, list[str]]:
    tags = [tag for tag in candidate.get("tags", []) if isinstance(tag, str)]
    seed_action = str(candidate.get("seed_action", ""))
    risk_signals: list[str] = []

    if "large_single_file" in tags or seed_action == "stop_candidate":
        risk_signals.append("large_single_file")
        return ("stop_split", risk_signals)
    if scores["shared_hub_penalty"] >= 0.5:
        risk_signals.append("shared_hub_penalty")
    if scores["runtime_condition_penalty"] >= 0.5:
        risk_signals.append("runtime_condition_penalty")
    if scores["cross_edge_ratio"] >= 0.35:
        risk_signals.append("cross_edge_ratio")
    if scores["ownership_conflict_penalty"] >= 0.35:
        risk_signals.append("ownership_conflict_penalty")

    if scores["shared_hub_penalty"] >= 0.75 or scores["runtime_condition_penalty"] >= 0.75:
        return ("mark_analysis_only", risk_signals)
    if seed_action == "merge_candidate" or scores["cross_edge_ratio"] >= 0.35 or scores["ownership_conflict_penalty"] > 0.5:
        return ("merge_with_neighbor", risk_signals)
    if seed_action == "split_candidate":
        return ("re_cut_with_dependency_overlay", risk_signals)
    return ("keep_seed", risk_signals)


def _count_edge_touch_between_roots(edge_text: str, root_a: str, root_b: str) -> int:
    if not edge_text or not root_a or not root_b:
        return 0
    if root_a == root_b:
        return 0
    return 1 if root_a in edge_text and root_b in edge_text else 0


def _select_merge_target_ids(
    current_candidate: dict[str, object],
    all_candidates: list[dict[str, object]],
    static_overlay_payload: dict[str, object],
) -> list[str]:
    current_id = str(current_candidate.get("candidate_id", ""))
    current_root = str(current_candidate.get("root_dir", ""))
    if not current_id or not current_root:
        return []

    touch_scores: dict[str, int] = {}
    edge_fields = [
        "source_import_edges",
        "manifest_edges",
        "wrapper_path_edges",
        "cross_region_edges",
    ]

    for other_candidate in all_candidates:
        if not isinstance(other_candidate, dict):
            continue
        other_id = str(other_candidate.get("candidate_id", ""))
        other_root = str(other_candidate.get("root_dir", ""))
        if not other_id or not other_root or other_id == current_id:
            continue
        touch_scores[other_id] = 0

    for raw_overlay in static_overlay_payload.get("overlays", []):
        if not isinstance(raw_overlay, dict):
            continue
        for field in edge_fields:
            values = raw_overlay.get(field, [])
            if not isinstance(values, list):
                continue
            for edge_text in values:
                if not isinstance(edge_text, str):
                    continue
                for other_candidate in all_candidates:
                    if not isinstance(other_candidate, dict):
                        continue
                    other_id = str(other_candidate.get("candidate_id", ""))
                    other_root = str(other_candidate.get("root_dir", ""))
                    if other_id not in touch_scores:
                        continue
                    touch_scores[other_id] += _count_edge_touch_between_roots(edge_text, current_root, other_root)

    ranked = sorted(
        (
            (other_id, score)
            for other_id, score in touch_scores.items()
            if score > 0
        ),
        key=lambda item: (-item[1], item[0]),
    )
    if not ranked:
        return []
    top_score = ranked[0][1]
    return [other_id for other_id, score in ranked if score == top_score][:1]


def build_seed_refinement_report(
    snapshot_path: Path,
    snapshot_payload: dict[str, object],
    candidates_path: Path,
    candidates_payload: dict[str, object],
    overlay_path: Path,
    overlay_payload: dict[str, object],
    runtime_overlay_path: Path | None,
    runtime_overlay_payload: dict[str, object] | None,
) -> tuple[dict[str, object], int]:
    snapshot_validation = validate_inventory_snapshot(snapshot_path, snapshot_payload)
    candidates_validation = validate_slice_seed_candidates(candidates_path, candidates_payload)
    overlay_validation = validate_static_dependency_overlay(overlay_path, overlay_payload)
    runtime_validation = None
    if runtime_overlay_path is not None and runtime_overlay_payload is not None:
        runtime_validation = validate_runtime_overlay(runtime_overlay_path, runtime_overlay_payload)

    validation_bundle = {
        "inventory_snapshot": snapshot_validation,
        "slice_seed_candidates": candidates_validation,
        "static_dependency_overlay": overlay_validation,
    }
    if runtime_validation is not None:
        validation_bundle["runtime_overlay"] = runtime_validation

    invalid_inputs = [name for name, payload in validation_bundle.items() if payload["status"] != "valid"]
    if invalid_inputs:
        errors: list[str] = []
        for payload in validation_bundle.values():
            errors.extend(payload["errors"])
        return (
            {
                "status": "invalid_inputs",
                "generated_at": _now_iso(),
                "algorithm_family": "seed_to_refinement_report",
                "version": "v0.1.0",
                "input_artifacts": {
                    "inventory_snapshot": _relative_or_str(snapshot_path),
                    "slice_seed_candidates": _relative_or_str(candidates_path),
                    "static_dependency_overlay": _relative_or_str(overlay_path),
                    "runtime_overlay": _relative_or_str(runtime_overlay_path) if runtime_overlay_path is not None else None,
                },
                "runtime_overlay_used": runtime_overlay_payload is not None,
                "invalid_inputs": invalid_inputs,
                "error_count": len(errors),
                "errors": errors,
                "next_candidate": None,
            },
            1,
        )

    recommendations: list[dict[str, object]] = []
    recommendation_summary = {name: 0 for name in REFINEMENT_RECOMMENDATION_ENUM}
    overlay_summary = overlay_validation["overlay_summary"]
    runtime_overlay_summary = runtime_validation["runtime_overlay_summary"] if runtime_validation is not None else None
    all_candidates = [
        raw_candidate
        for raw_candidate in candidates_payload.get("candidates", [])
        if isinstance(raw_candidate, dict)
    ]

    for raw_candidate in all_candidates:
        candidate_root = str(raw_candidate.get("root_dir", ""))
        signal_counts = _build_candidate_signal_counts(candidate_root, overlay_payload, runtime_overlay_payload)
        scores = _compute_refinement_scores(signal_counts, raw_candidate, snapshot_payload)
        recommendation, risk_signals = _recommend_refinement_action(raw_candidate, scores)
        target_candidate_ids = []
        if recommendation == "merge_with_neighbor":
            target_candidate_ids = _select_merge_target_ids(raw_candidate, all_candidates, overlay_payload)
        recommendation_summary[recommendation] += 1
        reason_parts = [
            f"seed_action={raw_candidate.get('seed_action')}",
            f"size_score={scores['size_score']}",
            f"cross_edge_ratio={scores['cross_edge_ratio']}",
        ]
        if target_candidate_ids:
            reason_parts.append("target_candidate_ids=" + ",".join(target_candidate_ids))
        if risk_signals:
            reason_parts.append("risk_signals=" + ",".join(risk_signals))
        recommendations.append(
            {
                "candidate_id": raw_candidate.get("candidate_id"),
                "root_dir": candidate_root,
                "seed_action": raw_candidate.get("seed_action"),
                "recommendation": recommendation,
                "target_candidate_ids": target_candidate_ids,
                "scores": scores,
                "signal_counts": signal_counts,
                "risk_signals": risk_signals,
                "reason": "; ".join(reason_parts),
            }
        )

    return (
        {
            "status": "ok",
            "generated_at": _now_iso(),
            "algorithm_family": "seed_to_refinement_report",
            "version": "v0.1.0",
            "input_artifacts": {
                "inventory_snapshot": _relative_or_str(snapshot_path),
                "slice_seed_candidates": _relative_or_str(candidates_path),
                "static_dependency_overlay": _relative_or_str(overlay_path),
                "runtime_overlay": _relative_or_str(runtime_overlay_path) if runtime_overlay_path is not None else None,
            },
            "runtime_overlay_used": runtime_overlay_payload is not None,
            "inventory_summary": snapshot_validation["snapshot_summary"],
            "global_signal_summary": {
                "static_overlay": overlay_summary,
                "runtime_overlay": runtime_overlay_summary,
            },
            "recommendation_count": len(recommendations),
            "recommendation_summary": recommendation_summary,
            "recommendations": recommendations,
            "next_candidate": "stop_rule_evaluator",
        },
        0,
    )


def validate_seed_refinement_report(input_path: Path, payload: dict[str, object]) -> dict[str, object]:
    errors: list[str] = []

    for field in REFINEMENT_REPORT_TOP_LEVEL_REQUIRED:
        if field not in payload:
            errors.append(f"missing top-level field: {field}")

    if payload.get("status") != "ok":
        errors.append("status must be ok for downstream algorithm stages")
    if payload.get("algorithm_family") != "seed_to_refinement_report":
        errors.append("algorithm_family must be seed_to_refinement_report")

    recommendation_count = payload.get("recommendation_count")
    if not isinstance(recommendation_count, int) or recommendation_count < 0:
        errors.append("recommendation_count must be non-negative int")

    raw_recommendations = payload.get("recommendations")
    if not isinstance(raw_recommendations, list):
        errors.append("recommendations must be list[dict]")
        raw_recommendations = []

    seen_candidate_ids: set[str] = set()
    for index, raw_item in enumerate(raw_recommendations, start=1):
        prefix = f"recommendations[{index}]."
        if not isinstance(raw_item, dict):
            errors.append(f"{prefix[:-1]} must be dict")
            continue
        for field in REFINEMENT_REPORT_REQUIRED_FIELDS:
            if field not in raw_item:
                errors.append(f"missing field: {prefix}{field}")
        candidate_id = raw_item.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            errors.append(f"{prefix}candidate_id must be non-empty str")
        elif candidate_id in seen_candidate_ids:
            errors.append(f"{prefix}candidate_id must be unique")
        else:
            seen_candidate_ids.add(candidate_id)
        root_dir = raw_item.get("root_dir")
        if not isinstance(root_dir, str) or not root_dir.strip():
            errors.append(f"{prefix}root_dir must be non-empty str")
        recommendation = raw_item.get("recommendation")
        if not isinstance(recommendation, str) or recommendation not in REFINEMENT_RECOMMENDATION_ENUM:
            errors.append(f"{prefix}recommendation must be one of {REFINEMENT_RECOMMENDATION_ENUM}")
        _validate_list_of_strings(raw_item.get("target_candidate_ids"), "target_candidate_ids", errors, prefix)
        risk_signals = raw_item.get("risk_signals")
        _validate_list_of_strings(risk_signals, "risk_signals", errors, prefix)
        signal_counts = raw_item.get("signal_counts")
        _validate_dict_of_nonnegative_ints(signal_counts, f"{prefix}signal_counts", errors)
        scores = raw_item.get("scores")
        if not isinstance(scores, dict):
            errors.append(f"{prefix}scores must be dict[str,float]")
        else:
            for score_name in [
                "size_score",
                "internal_cohesion_score",
                "cross_edge_ratio",
                "shared_hub_penalty",
                "runtime_condition_penalty",
                "ownership_conflict_penalty",
            ]:
                score_value = scores.get(score_name)
                if not isinstance(score_value, (int, float)) or score_value < 0 or score_value > 1:
                    errors.append(f"{prefix}scores.{score_name} must be float in [0,1]")
        reason = raw_item.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{prefix}reason must be non-empty str")

    if isinstance(recommendation_count, int) and recommendation_count != len(raw_recommendations):
        errors.append("recommendation_count must match len(recommendations)")

    return {
        "status": "valid" if not errors else "invalid",
        "generated_at": _now_iso(),
        "contract_family": "seed_refinement_report_validation",
        "input_refinement_report": _relative_or_str(input_path),
        "error_count": len(errors),
        "errors": errors,
    }


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _evaluate_stop_rules_for_item(item: dict[str, object]) -> tuple[str, list[str]]:
    recommendation = str(item.get("recommendation", ""))
    scores = item.get("scores", {}) if isinstance(item.get("scores"), dict) else {}
    signal_counts = item.get("signal_counts", {}) if isinstance(item.get("signal_counts"), dict) else {}
    risk_signals = item.get("risk_signals", []) if isinstance(item.get("risk_signals"), list) else []
    seed_action = str(item.get("seed_action", ""))

    shared_hub_penalty = float(scores.get("shared_hub_penalty", 0.0) or 0.0)
    cross_edge_ratio = float(scores.get("cross_edge_ratio", 0.0) or 0.0)
    runtime_condition_penalty = float(scores.get("runtime_condition_penalty", 0.0) or 0.0)
    wrapper_path_edge_count = int(signal_counts.get("wrapper_path_edge_count", 0) or 0)

    triggered: list[str] = []

    if recommendation == "stop_split" or seed_action == "stop_candidate":
        if "large_single_file" in risk_signals or seed_action == "stop_candidate":
            triggered.append("single_large_hub_file")
        if shared_hub_penalty >= 0.75 or cross_edge_ratio >= 0.35:
            triggered.append("coordination_cost_increase")
        if not triggered:
            triggered.append("coordination_cost_increase")
        return ("do_not_split", _dedupe_preserve_order(triggered))

    if wrapper_path_edge_count > 0 and runtime_condition_penalty >= 0.5:
        triggered.append("wrapper_indirection_uncertainty")
    if runtime_condition_penalty >= 0.5:
        triggered.append("path_order_runtime_dependence")
    if cross_edge_ratio >= 0.35:
        triggered.append("high_cross_edge_density")
    if recommendation == "merge_with_neighbor" or shared_hub_penalty >= 0.75:
        triggered.append("coordination_cost_increase")

    if recommendation in {"mark_analysis_only", "re_cut_with_dependency_overlay"}:
        return ("analysis_only", _dedupe_preserve_order(triggered or ["coordination_cost_increase"]))
    if triggered:
        return ("analysis_only", _dedupe_preserve_order(triggered))
    return ("write_safe", [])


def evaluate_stop_rules(refinement_report_path: Path, refinement_report_payload: dict[str, object]) -> tuple[dict[str, object], int]:
    validation = validate_seed_refinement_report(refinement_report_path, refinement_report_payload)
    if validation["status"] != "valid":
        return (
            {
                "status": "invalid_inputs",
                "generated_at": _now_iso(),
                "algorithm_family": "stop_rule_evaluator",
                "version": "v0.1.0",
                "input_artifacts": {
                    "seed_refinement_report": _relative_or_str(refinement_report_path),
                },
                "invalid_inputs": ["seed_refinement_report"],
                "error_count": validation["error_count"],
                "errors": validation["errors"],
                "next_candidate": None,
            },
            1,
        )

    evaluations: list[dict[str, object]] = []
    decision_summary = {
        "write_safe": 0,
        "analysis_only": 0,
        "do_not_split": 0,
    }
    triggered_rule_summary = {name: 0 for name in STOP_RULE_TRIGGER_ENUM}

    for raw_item in refinement_report_payload.get("recommendations", []):
        if not isinstance(raw_item, dict):
            continue
        stop_decision, triggered_stop_rules = _evaluate_stop_rules_for_item(raw_item)
        decision_summary[stop_decision] += 1
        for rule in triggered_stop_rules:
            triggered_rule_summary[rule] += 1
        evaluations.append(
            {
                "candidate_id": raw_item.get("candidate_id"),
                "root_dir": raw_item.get("root_dir"),
                "refinement_recommendation": raw_item.get("recommendation"),
                "stop_decision": stop_decision,
                "triggered_stop_rules": triggered_stop_rules,
                "scores": raw_item.get("scores"),
                "signal_counts": raw_item.get("signal_counts"),
                "reason": (
                    f"refinement_recommendation={raw_item.get('recommendation')}; "
                    f"stop_decision={stop_decision}; "
                    f"triggered_stop_rules={','.join(triggered_stop_rules) or 'none'}"
                ),
            }
        )

    return (
        {
            "status": "ok",
            "generated_at": _now_iso(),
            "algorithm_family": "stop_rule_evaluator",
            "version": "v0.1.0",
            "input_artifacts": {
                "seed_refinement_report": _relative_or_str(refinement_report_path),
            },
            "evaluation_count": len(evaluations),
            "decision_summary": decision_summary,
            "triggered_rule_summary": triggered_rule_summary,
            "evaluations": evaluations,
            "next_candidate": "final_slice_proposal_generator",
        },
        0,
    )


def validate_stop_rule_evaluation(input_path: Path, payload: dict[str, object]) -> dict[str, object]:
    errors: list[str] = []

    for field in STOP_RULE_EVALUATION_TOP_LEVEL_REQUIRED:
        if field not in payload:
            errors.append(f"missing top-level field: {field}")

    if payload.get("status") != "ok":
        errors.append("status must be ok for downstream final proposal generation")
    if payload.get("algorithm_family") != "stop_rule_evaluator":
        errors.append("algorithm_family must be stop_rule_evaluator")

    evaluation_count = payload.get("evaluation_count")
    if not isinstance(evaluation_count, int) or evaluation_count < 0:
        errors.append("evaluation_count must be non-negative int")

    raw_evaluations = payload.get("evaluations")
    if not isinstance(raw_evaluations, list):
        errors.append("evaluations must be list[dict]")
        raw_evaluations = []

    seen_candidate_ids: set[str] = set()
    for index, raw_item in enumerate(raw_evaluations, start=1):
        prefix = f"evaluations[{index}]."
        if not isinstance(raw_item, dict):
            errors.append(f"{prefix[:-1]} must be dict")
            continue
        for field in STOP_RULE_EVALUATION_REQUIRED_FIELDS:
            if field not in raw_item:
                errors.append(f"missing field: {prefix}{field}")
        candidate_id = raw_item.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            errors.append(f"{prefix}candidate_id must be non-empty str")
        elif candidate_id in seen_candidate_ids:
            errors.append(f"{prefix}candidate_id must be unique")
        else:
            seen_candidate_ids.add(candidate_id)
        root_dir = raw_item.get("root_dir")
        if not isinstance(root_dir, str) or not root_dir.strip():
            errors.append(f"{prefix}root_dir must be non-empty str")
        recommendation = raw_item.get("refinement_recommendation")
        if not isinstance(recommendation, str) or recommendation not in REFINEMENT_RECOMMENDATION_ENUM:
            errors.append(f"{prefix}refinement_recommendation must be one of {REFINEMENT_RECOMMENDATION_ENUM}")
        decision = raw_item.get("stop_decision")
        if not isinstance(decision, str) or decision not in STOP_RULE_DECISION_ENUM:
            errors.append(f"{prefix}stop_decision must be one of {STOP_RULE_DECISION_ENUM}")
        _validate_list_of_strings(raw_item.get("triggered_stop_rules"), "triggered_stop_rules", errors, prefix)
        _validate_dict_of_nonnegative_ints(raw_item.get("signal_counts"), f"{prefix}signal_counts", errors)
        scores = raw_item.get("scores")
        if not isinstance(scores, dict):
            errors.append(f"{prefix}scores must be dict[str,float]")
        reason = raw_item.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{prefix}reason must be non-empty str")

    if isinstance(evaluation_count, int) and evaluation_count != len(raw_evaluations):
        errors.append("evaluation_count must match len(evaluations)")

    return {
        "status": "valid" if not errors else "invalid",
        "generated_at": _now_iso(),
        "contract_family": "stop_rule_evaluation_validation",
        "input_stop_rule_evaluation": _relative_or_str(input_path),
        "error_count": len(errors),
        "errors": errors,
    }


def build_final_slice_proposal(stop_rule_evaluation_path: Path, stop_rule_evaluation_payload: dict[str, object]) -> tuple[dict[str, object], int]:
    return build_final_slice_proposal_with_path_index(stop_rule_evaluation_path, stop_rule_evaluation_payload, None, None)


def _path_belongs_to_root(path_value: str, root_dir: str) -> bool:
    if not path_value or not root_dir:
        return False
    normalized_path = path_value.rstrip("/")
    normalized_root = root_dir.rstrip("/")
    return normalized_path == normalized_root or normalized_path.startswith(normalized_root + "/")


def _materialize_slice_paths(
    root_dir: str,
    path_index_payload: dict[str, object] | None,
) -> tuple[list[str], list[str], dict[str, int], int]:
    if path_index_payload is None:
        return ([], [], {}, 0)
    files: list[str] = []
    entrypoints: list[str] = []
    language_buckets: dict[str, int] = {}
    total_bytes = 0
    for raw_record in path_index_payload.get("file_records", []):
        if not isinstance(raw_record, dict):
            continue
        path_value = raw_record.get("path")
        if not isinstance(path_value, str):
            continue
        if not _path_belongs_to_root(path_value, root_dir):
            continue
        files.append(path_value)
        if raw_record.get("is_entrypoint") is True:
            entrypoints.append(path_value)
        language = raw_record.get("language")
        if isinstance(language, str) and language.strip():
            language_buckets[language] = language_buckets.get(language, 0) + 1
        byte_count = raw_record.get("byte_count")
        if isinstance(byte_count, int) and not isinstance(byte_count, bool) and byte_count >= 0:
            total_bytes += byte_count
    return (
        _dedupe_preserve_order(files),
        _dedupe_preserve_order(entrypoints),
        dict(sorted(language_buckets.items())),
        total_bytes,
    )


def build_final_slice_proposal_with_path_index(
    stop_rule_evaluation_path: Path,
    stop_rule_evaluation_payload: dict[str, object],
    path_index_path: Path | None,
    path_index_payload: dict[str, object] | None,
) -> tuple[dict[str, object], int]:
    validation = validate_stop_rule_evaluation(stop_rule_evaluation_path, stop_rule_evaluation_payload)
    path_index_validation = None
    if path_index_path is not None and path_index_payload is not None:
        path_index_validation = validate_inventory_path_index(path_index_path, path_index_payload)

    if validation["status"] != "valid":
        return (
            {
                "status": "invalid_inputs",
                "generated_at": _now_iso(),
                "algorithm_family": "final_slice_proposal_generator",
                "version": "v0.1.0",
                "input_artifacts": {
                    "stop_rule_evaluation": _relative_or_str(stop_rule_evaluation_path),
                    "inventory_path_index": _relative_or_str(path_index_path) if path_index_path is not None else None,
                },
                "invalid_inputs": ["stop_rule_evaluation"],
                "error_count": validation["error_count"],
                "errors": validation["errors"],
                "next_candidate": None,
            },
            1,
        )
    if path_index_validation is not None and path_index_validation["status"] != "valid":
        return (
            {
                "status": "invalid_inputs",
                "generated_at": _now_iso(),
                "algorithm_family": "final_slice_proposal_generator",
                "version": "v0.1.0",
                "input_artifacts": {
                    "stop_rule_evaluation": _relative_or_str(stop_rule_evaluation_path),
                    "inventory_path_index": _relative_or_str(path_index_path),
                },
                "invalid_inputs": ["inventory_path_index"],
                "error_count": path_index_validation["error_count"],
                "errors": path_index_validation["errors"],
                "next_candidate": None,
            },
            1,
        )

    parallel_slices: list[dict[str, object]] = []
    write_safe_slices: list[dict[str, object]] = []
    analysis_only_slices: list[dict[str, object]] = []
    do_not_split_regions: list[dict[str, object]] = []
    handoff_packets: list[dict[str, object]] = []
    manifest_slices: list[dict[str, object]] = []

    slice_index = 1
    for raw_item in stop_rule_evaluation_payload.get("evaluations", []):
        if not isinstance(raw_item, dict):
            continue
        candidate_id = str(raw_item.get("candidate_id", ""))
        root_dir = str(raw_item.get("root_dir", ""))
        stop_decision = str(raw_item.get("stop_decision", ""))
        triggered_stop_rules = raw_item.get("triggered_stop_rules", [])
        reason = str(raw_item.get("reason", ""))

        if stop_decision == "do_not_split":
            do_not_split_regions.append(
                {
                    "candidate_id": candidate_id,
                    "root_dir": root_dir,
                    "triggered_stop_rules": triggered_stop_rules,
                    "reason": reason,
                }
            )
            continue

        slice_id = f"slice_{slice_index:02d}"
        slice_index += 1
        files, entrypoints, language_buckets, total_bytes = _materialize_slice_paths(root_dir, path_index_payload)
        slice_entry = {
            "slice_id": slice_id,
            "root_dirs": [root_dir],
            "files": files,
            "entrypoints": entrypoints,
            "language_buckets": language_buckets,
            "total_bytes": total_bytes,
            "classification": stop_decision,
            "source_candidate_id": candidate_id,
            "reason": reason,
        }
        parallel_slices.append(slice_entry)
        manifest_slices.append(
            {
                "slice_id": slice_id,
                "root_dirs": [root_dir],
                "files": files,
                "entrypoints": entrypoints,
                "language_buckets": language_buckets,
                "total_bytes": total_bytes,
                "classification": stop_decision,
                "reason": reason,
            }
        )
        handoff_packets.append(
            {
                "slice_id": slice_id,
                "root_dirs": [root_dir],
                "files": files,
                "entrypoints": entrypoints,
                "language_buckets": language_buckets,
                "total_bytes": total_bytes,
                "allowed_paths": [root_dir],
                "non_goals": ["do not modify paths outside allowed_paths"],
                "upstream_artifacts": [_relative_or_str(stop_rule_evaluation_path)],
            }
        )
        if stop_decision == "write_safe":
            write_safe_slices.append(slice_entry)
        elif stop_decision == "analysis_only":
            analysis_only_slices.append(slice_entry)

    slice_manifest = {
        "slice_count": len(manifest_slices),
        "slices": manifest_slices,
    }

    return (
        {
            "status": "ok",
            "generated_at": _now_iso(),
            "algorithm_family": "final_slice_proposal_generator",
            "version": "v0.1.0",
            "input_artifacts": {
                "stop_rule_evaluation": _relative_or_str(stop_rule_evaluation_path),
                "inventory_path_index": _relative_or_str(path_index_path) if path_index_path is not None else None,
            },
            "parallel_slice_count": len(parallel_slices),
            "write_safe_slice_count": len(write_safe_slices),
            "analysis_only_slice_count": len(analysis_only_slices),
            "do_not_split_count": len(do_not_split_regions),
            "parallel_slices": parallel_slices,
            "write_safe_slices": write_safe_slices,
            "analysis_only_slices": analysis_only_slices,
            "do_not_split_regions": do_not_split_regions,
            "slice_manifest": slice_manifest,
            "handoff_packet_count": len(handoff_packets),
            "handoff_packets": handoff_packets,
            "next_candidate": None,
        },
        0,
    )


def render_contract_markdown(payload: dict[str, object]) -> str:
    title = "slice_manifest contract"
    required_fields = payload.get("required_top_level_fields", [])
    section_title = "Required Top-Level Fields"
    if payload["contract_family"] == "handoff_packet_contract":
        title = "handoff_packet contract"
        required_fields = payload["required_fields"]
        section_title = "Required Fields"
    elif payload["contract_family"] == "inventory_snapshot_contract":
        title = "inventory_snapshot contract"
        required_fields = payload["required_fields"]
        section_title = "Required Fields"
    elif payload["contract_family"] == "slice_seed_candidates_contract":
        title = "slice_seed_candidates contract"
        required_fields = payload["required_top_level_fields"]
        section_title = "Required Top-Level Fields"
    elif payload["contract_family"] == "static_dependency_overlay_contract":
        title = "static_dependency_overlay contract"
        required_fields = payload["required_top_level_fields"]
        section_title = "Required Top-Level Fields"
    elif payload["contract_family"] == "runtime_overlay_contract":
        title = "runtime_overlay contract"
        required_fields = payload["required_top_level_fields"]
        section_title = "Required Top-Level Fields"
    elif payload["contract_family"] == "unobserved_path_register":
        title = "unobserved_path_register contract"
        required_fields = payload["required_top_level_fields"]
        section_title = "Required Top-Level Fields"
    elif payload["contract_family"] == "inventory_path_index_contract":
        title = "inventory_path_index contract"
        required_fields = payload["required_top_level_fields"]
        section_title = "Required Top-Level Fields"
    elif payload["contract_family"] == "seed_refinement_report_contract":
        title = "seed_refinement_report contract"
        required_fields = payload["required_top_level_fields"]
        section_title = "Required Top-Level Fields"
    elif payload["contract_family"] == "stop_rule_evaluation_contract":
        title = "stop_rule_evaluation contract"
        required_fields = payload["required_top_level_fields"]
        section_title = "Required Top-Level Fields"
    elif payload["contract_family"] == "final_slice_proposal_contract":
        title = "final_slice_proposal contract"
        required_fields = payload["required_top_level_fields"]
        section_title = "Required Top-Level Fields"
    lines = [
        f"# dependency-slice-planner {title}",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- contract_family: `{payload['contract_family']}`",
        f"- version: `{payload['version']}`",
        "",
        f"## {section_title}",
        "",
    ]
    for field in required_fields:
        lines.append(f"- `{field}`")
    if payload["contract_family"] == "slice_manifest_contract":
        lines.extend(["", "## Slice Required Fields", ""])
        for field in payload["slice_required_fields"]:
            lines.append(f"- `{field}`")
    elif payload["contract_family"] == "slice_seed_candidates_contract":
        lines.extend(["", "## Candidate Required Fields", ""])
        for field in payload["candidate_required_fields"]:
            lines.append(f"- `{field}`")
    elif payload["contract_family"] == "static_dependency_overlay_contract":
        lines.extend(["", "## Overlay Required Fields", ""])
        for field in payload["overlay_required_fields"]:
            lines.append(f"- `{field}`")
        lines.extend(["", "## Signal Fields", ""])
        for field in payload["signal_fields"]:
            lines.append(f"- `{field}`")
    elif payload["contract_family"] == "runtime_overlay_contract":
        lines.extend(["", "## Overlay Required Fields", ""])
        for field in payload["overlay_required_fields"]:
            lines.append(f"- `{field}`")
        lines.extend(["", "## Signal Fields", ""])
        for field in payload["signal_fields"]:
            lines.append(f"- `{field}`")
    elif payload["contract_family"] == "unobserved_path_register":
        lines.extend(["", "## Register Required Fields", ""])
        for field in payload["register_required_fields"]:
            lines.append(f"- `{field}`")
        lines.extend(["", "## Bounding Rules", ""])
        for field, value in payload["bounding_rules"].items():
            lines.append(f"- `{field}`: `{value}`")
    elif payload["contract_family"] == "inventory_path_index_contract":
        lines.extend(["", "## Record Required Fields", ""])
        for field in payload["record_required_fields"]:
            lines.append(f"- `{field}`")
        if payload.get("record_optional_fields"):
            lines.extend(["", "## Record Optional Fields", ""])
            for field in payload["record_optional_fields"]:
                lines.append(f"- `{field}`")
    elif payload["contract_family"] == "seed_refinement_report_contract":
        lines.extend(["", "## Recommendation Required Fields", ""])
        for field in payload["recommendation_required_fields"]:
            lines.append(f"- `{field}`")
        lines.extend(["", "## Recommendation Enum", ""])
        for field in payload["recommendation_enum"]:
            lines.append(f"- `{field}`")
    elif payload["contract_family"] == "stop_rule_evaluation_contract":
        lines.extend(["", "## Evaluation Required Fields", ""])
        for field in payload["evaluation_required_fields"]:
            lines.append(f"- `{field}`")
        lines.extend(["", "## Decision Enum", ""])
        for field in payload["decision_enum"]:
            lines.append(f"- `{field}`")
        lines.extend(["", "## Trigger Enum", ""])
        for field in payload["trigger_enum"]:
            lines.append(f"- `{field}`")
    elif payload["contract_family"] == "final_slice_proposal_contract":
        lines.extend(["", "## Slice Required Fields", ""])
        for field in payload["slice_required_fields"]:
            lines.append(f"- `{field}`")
        if payload.get("slice_optional_fields"):
            lines.extend(["", "## Slice Optional Fields", ""])
            for field in payload["slice_optional_fields"]:
                lines.append(f"- `{field}`")
        lines.extend(["", "## Do-Not-Split Required Fields", ""])
        for field in payload["do_not_split_required_fields"]:
            lines.append(f"- `{field}`")
    return "\n".join(lines) + "\n"


def render_validation_markdown(payload: dict[str, object]) -> str:
    title = "slice_manifest validation"
    input_label = "input_manifest"
    if payload["contract_family"] == "handoff_packet_validation":
        title = "handoff_packet validation"
        input_label = "input_packet"
    elif payload["contract_family"] == "inventory_snapshot_validation":
        title = "inventory_snapshot validation"
        input_label = "input_snapshot"
    elif payload["contract_family"] == "slice_seed_candidates_validation":
        title = "slice_seed_candidates validation"
        input_label = "input_candidates"
    elif payload["contract_family"] == "static_dependency_overlay_validation":
        title = "static_dependency_overlay validation"
        input_label = "input_overlay"
    elif payload["contract_family"] == "runtime_overlay_validation":
        title = "runtime_overlay validation"
        input_label = "input_runtime_overlay"
    elif payload["contract_family"] == "unobserved_path_register_validation":
        title = "unobserved_path_register validation"
        input_label = "input_unobserved_path_register"
    elif payload["contract_family"] == "inventory_path_index_validation":
        title = "inventory_path_index validation"
        input_label = "input_path_index"
    lines = [
        f"# dependency-slice-planner {title}",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- {input_label}: `{payload[input_label]}`",
        f"- status: `{payload['status']}`",
        f"- error_count: `{payload['error_count']}`",
        "",
        "## Errors",
        "",
    ]
    if payload["contract_family"] == "inventory_path_index_validation" and payload.get("path_index_summary"):
        summary = payload["path_index_summary"]
        lines = lines[:-2] + [
            "## Summary",
            "",
            f"- root_path: `{summary.get('root_path')}`",
            f"- file_record_count: `{summary.get('file_record_count')}`",
            f"- entrypoint_count: `{summary.get('entrypoint_count')}`",
            f"- metadata_record_count: `{summary.get('metadata_record_count')}`",
            f"- total_bytes: `{summary.get('total_bytes')}`",
            f"- language_buckets: `{summary.get('language_buckets')}`",
            "",
            "## Errors",
            "",
        ]
    if payload["errors"]:
        for error in payload["errors"]:
            lines.append(f"- {error}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def render_seed_refinement_report_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# dependency-slice-planner seed_to_refinement_report",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- status: `{payload['status']}`",
        f"- algorithm_family: `{payload['algorithm_family']}`",
        f"- runtime_overlay_used: `{payload.get('runtime_overlay_used')}`",
        f"- recommendation_count: `{payload.get('recommendation_count')}`",
        f"- next_candidate: `{payload.get('next_candidate')}`",
        "",
    ]
    if payload["status"] != "ok":
        lines.extend(["## Errors", ""])
        for error in payload.get("errors", []):
            lines.append(f"- {error}")
        if not payload.get("errors"):
            lines.append("- none")
        return "\n".join(lines) + "\n"

    lines.extend(["## Recommendation Summary", ""])
    for key, value in payload.get("recommendation_summary", {}).items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Recommendations", ""])
    for item in payload.get("recommendations", []):
        if not isinstance(item, dict):
            continue
        lines.extend(
            [
                f"### {item.get('candidate_id')}",
                f"- root_dir: `{item.get('root_dir')}`",
                f"- seed_action: `{item.get('seed_action')}`",
                f"- recommendation: `{item.get('recommendation')}`",
                f"- scores: `size={item.get('scores', {}).get('size_score')}`, `cohesion={item.get('scores', {}).get('internal_cohesion_score')}`, `cross_edge_ratio={item.get('scores', {}).get('cross_edge_ratio')}`",
                f"- risk_signals: `{', '.join(item.get('risk_signals', [])) or 'none'}`",
                f"- reason: {item.get('reason')}",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def render_stop_rule_evaluation_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# dependency-slice-planner stop_rule_evaluator",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- status: `{payload['status']}`",
        f"- algorithm_family: `{payload['algorithm_family']}`",
        f"- evaluation_count: `{payload.get('evaluation_count')}`",
        f"- next_candidate: `{payload.get('next_candidate')}`",
        "",
    ]
    if payload["status"] != "ok":
        lines.extend(["## Errors", ""])
        for error in payload.get("errors", []):
            lines.append(f"- {error}")
        if not payload.get("errors"):
            lines.append("- none")
        return "\n".join(lines) + "\n"

    lines.extend(["## Decision Summary", ""])
    for key, value in payload.get("decision_summary", {}).items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Evaluations", ""])
    for item in payload.get("evaluations", []):
        if not isinstance(item, dict):
            continue
        lines.extend(
            [
                f"### {item.get('candidate_id')}",
                f"- root_dir: `{item.get('root_dir')}`",
                f"- refinement_recommendation: `{item.get('refinement_recommendation')}`",
                f"- stop_decision: `{item.get('stop_decision')}`",
                f"- triggered_stop_rules: `{', '.join(item.get('triggered_stop_rules', [])) or 'none'}`",
                f"- reason: {item.get('reason')}",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def render_final_slice_proposal_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# dependency-slice-planner final_slice_proposal_generator",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- status: `{payload['status']}`",
        f"- algorithm_family: `{payload['algorithm_family']}`",
        f"- parallel_slice_count: `{payload.get('parallel_slice_count')}`",
        f"- do_not_split_count: `{payload.get('do_not_split_count')}`",
        f"- next_candidate: `{payload.get('next_candidate')}`",
        "",
    ]
    if payload["status"] != "ok":
        lines.extend(["## Errors", ""])
        for error in payload.get("errors", []):
            lines.append(f"- {error}")
        if not payload.get("errors"):
            lines.append("- none")
        return "\n".join(lines) + "\n"

    lines.extend(["## Parallel Slices", ""])
    for item in payload.get("parallel_slices", []):
        if not isinstance(item, dict):
            continue
        lines.extend(
            [
                f"### {item.get('slice_id')}",
                f"- source_candidate_id: `{item.get('source_candidate_id')}`",
                f"- classification: `{item.get('classification')}`",
                f"- root_dirs: `{', '.join(item.get('root_dirs', []))}`",
                f"- total_bytes: `{item.get('total_bytes')}`",
                f"- language_buckets: `{item.get('language_buckets')}`",
                f"- reason: {item.get('reason')}",
                "",
            ]
        )
    lines.extend(["## Do Not Split Regions", ""])
    if payload.get("do_not_split_regions"):
        for item in payload.get("do_not_split_regions", []):
            if not isinstance(item, dict):
                continue
            lines.append(f"- `{item.get('candidate_id')}` -> `{item.get('root_dir')}` ({', '.join(item.get('triggered_stop_rules', [])) or 'none'})")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def cmd_emit_slice_manifest_contract(args: argparse.Namespace) -> int:
    payload = emit_slice_manifest_contract()
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_contract_markdown(payload), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0


def cmd_emit_handoff_packet_contract(args: argparse.Namespace) -> int:
    payload = emit_handoff_packet_contract()
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_contract_markdown(payload), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0


def cmd_emit_inventory_snapshot_contract(args: argparse.Namespace) -> int:
    payload = emit_inventory_snapshot_contract()
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_contract_markdown(payload), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0


def cmd_emit_slice_seed_candidates_contract(args: argparse.Namespace) -> int:
    payload = emit_slice_seed_candidates_contract()
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_contract_markdown(payload), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0


def cmd_validate_slice_manifest(args: argparse.Namespace) -> int:
    input_path = Path(args.input_manifest)
    payload = _load_json(input_path)
    validation = validate_slice_manifest(input_path, payload)
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(validation, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_validation_markdown(validation), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0 if validation["status"] == "valid" else 1


def cmd_validate_handoff_packet(args: argparse.Namespace) -> int:
    input_path = Path(args.input_packet)
    payload = _load_json(input_path)
    validation = validate_handoff_packet(input_path, payload)
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(validation, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_validation_markdown(validation), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0 if validation["status"] == "valid" else 1


def cmd_validate_inventory_snapshot(args: argparse.Namespace) -> int:
    input_path = Path(args.input_snapshot)
    payload = _load_json(input_path)
    validation = validate_inventory_snapshot(input_path, payload)
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(validation, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_validation_markdown(validation), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0 if validation["status"] == "valid" else 1


def cmd_validate_slice_seed_candidates(args: argparse.Namespace) -> int:
    input_path = Path(args.input_candidates)
    payload = _load_json(input_path)
    validation = validate_slice_seed_candidates(input_path, payload)
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(validation, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_validation_markdown(validation), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0 if validation["status"] == "valid" else 1


def cmd_emit_static_dependency_overlay_contract(args: argparse.Namespace) -> int:
    payload = emit_static_dependency_overlay_contract()
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_contract_markdown(payload), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0


def cmd_validate_static_dependency_overlay(args: argparse.Namespace) -> int:
    input_path = Path(args.input_overlay)
    payload = _load_json(input_path)
    validation = validate_static_dependency_overlay(input_path, payload)
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(validation, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_validation_markdown(validation), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0 if validation["status"] == "valid" else 1


def cmd_emit_runtime_overlay_contract(args: argparse.Namespace) -> int:
    payload = emit_runtime_overlay_contract()
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_contract_markdown(payload), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0


def cmd_emit_inventory_path_index_contract(args: argparse.Namespace) -> int:
    payload = emit_inventory_path_index_contract()
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_contract_markdown(payload), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0


def cmd_emit_unobserved_path_register_contract(args: argparse.Namespace) -> int:
    payload = emit_unobserved_path_register_contract()
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_contract_markdown(payload), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0


def cmd_emit_seed_refinement_report_contract(args: argparse.Namespace) -> int:
    payload = emit_seed_refinement_report_contract()
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_contract_markdown(payload), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0


def cmd_emit_stop_rule_evaluation_contract(args: argparse.Namespace) -> int:
    payload = emit_stop_rule_evaluation_contract()
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_contract_markdown(payload), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0


def cmd_emit_final_slice_proposal_contract(args: argparse.Namespace) -> int:
    payload = emit_final_slice_proposal_contract()
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_contract_markdown(payload), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0


def cmd_validate_runtime_overlay(args: argparse.Namespace) -> int:
    input_path = Path(args.input_runtime_overlay)
    payload = _load_json(input_path)
    validation = validate_runtime_overlay(input_path, payload)
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(validation, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_validation_markdown(validation), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0 if validation["status"] == "valid" else 1


def cmd_validate_unobserved_path_register(args: argparse.Namespace) -> int:
    input_path = Path(args.input_unobserved_path_register)
    payload = _load_json(input_path)
    validation = validate_unobserved_path_register(input_path, payload)
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(validation, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_validation_markdown(validation), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0 if validation["status"] == "valid" else 1


def cmd_build_unobserved_path_register(args: argparse.Namespace) -> int:
    runtime_overlay_path = Path(args.input_runtime_overlay)
    runtime_overlay_payload = _load_json(runtime_overlay_path)
    report, exit_code = build_unobserved_path_register(
        runtime_overlay_path,
        runtime_overlay_payload,
    )
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return exit_code


def cmd_validate_inventory_path_index(args: argparse.Namespace) -> int:
    input_path = Path(args.input_path_index)
    payload = _load_json(input_path)
    validation = validate_inventory_path_index(input_path, payload)
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(validation, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_validation_markdown(validation), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return 0 if validation["status"] == "valid" else 1


def cmd_build_seed_refinement_report(args: argparse.Namespace) -> int:
    snapshot_path = Path(args.input_snapshot)
    snapshot_payload = _load_json(snapshot_path)
    candidates_path = Path(args.input_candidates)
    candidates_payload = _load_json(candidates_path)
    overlay_path = Path(args.input_overlay)
    overlay_payload = _load_json(overlay_path)
    runtime_overlay_path = Path(args.input_runtime_overlay) if args.input_runtime_overlay else None
    runtime_overlay_payload = _load_json(runtime_overlay_path) if runtime_overlay_path is not None else None

    report, exit_code = build_seed_refinement_report(
        snapshot_path,
        snapshot_payload,
        candidates_path,
        candidates_payload,
        overlay_path,
        overlay_payload,
        runtime_overlay_path,
        runtime_overlay_payload,
    )
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_seed_refinement_report_markdown(report), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return exit_code


def cmd_evaluate_stop_rules(args: argparse.Namespace) -> int:
    refinement_report_path = Path(args.input_refinement_report)
    refinement_report_payload = _load_json(refinement_report_path)
    report, exit_code = evaluate_stop_rules(refinement_report_path, refinement_report_payload)
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_stop_rule_evaluation_markdown(report), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return exit_code


def cmd_build_final_slice_proposal(args: argparse.Namespace) -> int:
    stop_rule_evaluation_path = Path(args.input_stop_rule_evaluation)
    stop_rule_evaluation_payload = _load_json(stop_rule_evaluation_path)
    path_index_path = Path(args.input_path_index) if args.input_path_index else None
    path_index_payload = _load_json(path_index_path) if path_index_path is not None else None
    report, exit_code = build_final_slice_proposal_with_path_index(
        stop_rule_evaluation_path,
        stop_rule_evaluation_payload,
        path_index_path,
        path_index_payload,
    )
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_final_slice_proposal_markdown(report), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)
    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emit and validate dependency-slice-planner contract artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    emit_parser = subparsers.add_parser(
        "emit-slice-manifest-contract",
        help="Emit the canonical contract for slice_manifest.json.",
    )
    emit_parser.add_argument("--output-json", help="Optional output path for contract JSON.")
    emit_parser.add_argument("--output-md", help="Optional output path for contract markdown summary.")
    emit_parser.set_defaults(func=cmd_emit_slice_manifest_contract)

    emit_handoff_parser = subparsers.add_parser(
        "emit-handoff-packet-contract",
        help="Emit the canonical contract for handoff_packet.json.",
    )
    emit_handoff_parser.add_argument("--output-json", help="Optional output path for contract JSON.")
    emit_handoff_parser.add_argument("--output-md", help="Optional output path for contract markdown summary.")
    emit_handoff_parser.set_defaults(func=cmd_emit_handoff_packet_contract)

    emit_inventory_parser = subparsers.add_parser(
        "emit-inventory-snapshot-contract",
        help="Emit the canonical contract for inventory_snapshot.json.",
    )
    emit_inventory_parser.add_argument("--output-json", help="Optional output path for contract JSON.")
    emit_inventory_parser.add_argument("--output-md", help="Optional output path for contract markdown summary.")
    emit_inventory_parser.set_defaults(func=cmd_emit_inventory_snapshot_contract)

    emit_seed_parser = subparsers.add_parser(
        "emit-slice-seed-candidates-contract",
        help="Emit the canonical contract for slice_seed_candidates.json.",
    )
    emit_seed_parser.add_argument("--output-json", help="Optional output path for contract JSON.")
    emit_seed_parser.add_argument("--output-md", help="Optional output path for contract markdown summary.")
    emit_seed_parser.set_defaults(func=cmd_emit_slice_seed_candidates_contract)

    emit_overlay_parser = subparsers.add_parser(
        "emit-static-dependency-overlay-contract",
        help="Emit the canonical contract for static_dependency_overlay.json.",
    )
    emit_overlay_parser.add_argument("--output-json", help="Optional output path for contract JSON.")
    emit_overlay_parser.add_argument("--output-md", help="Optional output path for contract markdown summary.")
    emit_overlay_parser.set_defaults(func=cmd_emit_static_dependency_overlay_contract)

    emit_runtime_overlay_parser = subparsers.add_parser(
        "emit-runtime-overlay-contract",
        help="Emit the canonical contract for runtime_overlay.json.",
    )
    emit_runtime_overlay_parser.add_argument("--output-json", help="Optional output path for contract JSON.")
    emit_runtime_overlay_parser.add_argument("--output-md", help="Optional output path for contract markdown summary.")
    emit_runtime_overlay_parser.set_defaults(func=cmd_emit_runtime_overlay_contract)

    emit_unobserved_path_register_parser = subparsers.add_parser(
        "emit-unobserved-path-register-contract",
        help="Emit the canonical contract for unobserved_path_register.json.",
    )
    emit_unobserved_path_register_parser.add_argument("--output-json", help="Optional output path for contract JSON.")
    emit_unobserved_path_register_parser.add_argument("--output-md", help="Optional output path for contract markdown summary.")
    emit_unobserved_path_register_parser.set_defaults(func=cmd_emit_unobserved_path_register_contract)

    emit_path_index_parser = subparsers.add_parser(
        "emit-inventory-path-index-contract",
        help="Emit the canonical contract for inventory_path_index.json.",
    )
    emit_path_index_parser.add_argument("--output-json", help="Optional output path for contract JSON.")
    emit_path_index_parser.add_argument("--output-md", help="Optional output path for contract markdown summary.")
    emit_path_index_parser.set_defaults(func=cmd_emit_inventory_path_index_contract)

    emit_refinement_report_parser = subparsers.add_parser(
        "emit-seed-refinement-report-contract",
        help="Emit the canonical contract for seed_to_refinement_report output.",
    )
    emit_refinement_report_parser.add_argument("--output-json", help="Optional output path for contract JSON.")
    emit_refinement_report_parser.add_argument("--output-md", help="Optional output path for contract markdown summary.")
    emit_refinement_report_parser.set_defaults(func=cmd_emit_seed_refinement_report_contract)

    emit_stop_rule_evaluation_parser = subparsers.add_parser(
        "emit-stop-rule-evaluation-contract",
        help="Emit the canonical contract for stop_rule_evaluator output.",
    )
    emit_stop_rule_evaluation_parser.add_argument("--output-json", help="Optional output path for contract JSON.")
    emit_stop_rule_evaluation_parser.add_argument("--output-md", help="Optional output path for contract markdown summary.")
    emit_stop_rule_evaluation_parser.set_defaults(func=cmd_emit_stop_rule_evaluation_contract)

    emit_final_slice_proposal_parser = subparsers.add_parser(
        "emit-final-slice-proposal-contract",
        help="Emit the canonical contract for final_slice_proposal_generator output.",
    )
    emit_final_slice_proposal_parser.add_argument("--output-json", help="Optional output path for contract JSON.")
    emit_final_slice_proposal_parser.add_argument("--output-md", help="Optional output path for contract markdown summary.")
    emit_final_slice_proposal_parser.set_defaults(func=cmd_emit_final_slice_proposal_contract)

    validate_parser = subparsers.add_parser(
        "validate-slice-manifest",
        help="Validate a slice_manifest.json artifact against the canonical contract.",
    )
    validate_parser.add_argument("--input-manifest", required=True, help="Path to slice_manifest JSON.")
    validate_parser.add_argument("--output-json", help="Optional output path for validation JSON.")
    validate_parser.add_argument("--output-md", help="Optional output path for validation markdown summary.")
    validate_parser.set_defaults(func=cmd_validate_slice_manifest)

    validate_handoff_parser = subparsers.add_parser(
        "validate-handoff-packet",
        help="Validate a handoff_packet.json artifact against the canonical contract.",
    )
    validate_handoff_parser.add_argument("--input-packet", required=True, help="Path to handoff_packet JSON.")
    validate_handoff_parser.add_argument("--output-json", help="Optional output path for validation JSON.")
    validate_handoff_parser.add_argument("--output-md", help="Optional output path for validation markdown summary.")
    validate_handoff_parser.set_defaults(func=cmd_validate_handoff_packet)

    validate_inventory_parser = subparsers.add_parser(
        "validate-inventory-snapshot",
        help="Validate an inventory_snapshot.json artifact against the canonical contract.",
    )
    validate_inventory_parser.add_argument("--input-snapshot", required=True, help="Path to inventory_snapshot JSON.")
    validate_inventory_parser.add_argument("--output-json", help="Optional output path for validation JSON.")
    validate_inventory_parser.add_argument("--output-md", help="Optional output path for validation markdown summary.")
    validate_inventory_parser.set_defaults(func=cmd_validate_inventory_snapshot)

    validate_seed_parser = subparsers.add_parser(
        "validate-slice-seed-candidates",
        help="Validate a slice_seed_candidates.json artifact against the canonical contract.",
    )
    validate_seed_parser.add_argument("--input-candidates", required=True, help="Path to slice_seed_candidates JSON.")
    validate_seed_parser.add_argument("--output-json", help="Optional output path for validation JSON.")
    validate_seed_parser.add_argument("--output-md", help="Optional output path for validation markdown summary.")
    validate_seed_parser.set_defaults(func=cmd_validate_slice_seed_candidates)

    validate_overlay_parser = subparsers.add_parser(
        "validate-static-dependency-overlay",
        help="Validate a static_dependency_overlay.json artifact against the canonical contract.",
    )
    validate_overlay_parser.add_argument("--input-overlay", required=True, help="Path to static_dependency_overlay JSON.")
    validate_overlay_parser.add_argument("--output-json", help="Optional output path for validation JSON.")
    validate_overlay_parser.add_argument("--output-md", help="Optional output path for validation markdown summary.")
    validate_overlay_parser.set_defaults(func=cmd_validate_static_dependency_overlay)

    validate_runtime_overlay_parser = subparsers.add_parser(
        "validate-runtime-overlay",
        help="Validate a runtime_overlay.json artifact against the canonical contract.",
    )
    validate_runtime_overlay_parser.add_argument("--input-runtime-overlay", required=True, help="Path to runtime_overlay JSON.")
    validate_runtime_overlay_parser.add_argument("--output-json", help="Optional output path for validation JSON.")
    validate_runtime_overlay_parser.add_argument("--output-md", help="Optional output path for validation markdown summary.")
    validate_runtime_overlay_parser.set_defaults(func=cmd_validate_runtime_overlay)

    validate_unobserved_path_register_parser = subparsers.add_parser(
        "validate-unobserved-path-register",
        help="Validate an unobserved_path_register artifact against the canonical contract.",
    )
    validate_unobserved_path_register_parser.add_argument(
        "--input-unobserved-path-register",
        required=True,
        help="Path to unobserved_path_register JSON.",
    )
    validate_unobserved_path_register_parser.add_argument("--output-json", help="Optional output path for validation JSON.")
    validate_unobserved_path_register_parser.add_argument("--output-md", help="Optional output path for validation markdown summary.")
    validate_unobserved_path_register_parser.set_defaults(func=cmd_validate_unobserved_path_register)

    validate_path_index_parser = subparsers.add_parser(
        "validate-inventory-path-index",
        help="Validate an inventory_path_index.json artifact against the canonical contract.",
    )
    validate_path_index_parser.add_argument("--input-path-index", required=True, help="Path to inventory_path_index JSON.")
    validate_path_index_parser.add_argument("--output-json", help="Optional output path for validation JSON.")
    validate_path_index_parser.add_argument("--output-md", help="Optional output path for validation markdown summary.")
    validate_path_index_parser.set_defaults(func=cmd_validate_inventory_path_index)

    build_refinement_report_parser = subparsers.add_parser(
        "build-seed-refinement-report",
        help="Build the first algorithm-phase seed_to_refinement_report artifact.",
    )
    build_refinement_report_parser.add_argument("--input-snapshot", required=True, help="Path to inventory_snapshot JSON.")
    build_refinement_report_parser.add_argument("--input-candidates", required=True, help="Path to slice_seed_candidates JSON.")
    build_refinement_report_parser.add_argument("--input-overlay", required=True, help="Path to static_dependency_overlay JSON.")
    build_refinement_report_parser.add_argument("--input-runtime-overlay", help="Optional path to runtime_overlay JSON.")
    build_refinement_report_parser.add_argument("--output-json", help="Optional output path for refinement report JSON.")
    build_refinement_report_parser.add_argument("--output-md", help="Optional output path for refinement report markdown summary.")
    build_refinement_report_parser.set_defaults(func=cmd_build_seed_refinement_report)

    build_unobserved_path_register_parser = subparsers.add_parser(
        "build-unobserved-path-register",
        help="Build unobserved_path_register artifacts from runtime_overlay observations.",
    )
    build_unobserved_path_register_parser.add_argument(
        "--input-runtime-overlay",
        required=True,
        help="Path to runtime_overlay JSON.",
    )
    build_unobserved_path_register_parser.add_argument("--output-json", help="Optional output path for register JSON.")
    build_unobserved_path_register_parser.add_argument("--output-md", help="Optional output path for register markdown summary.")
    build_unobserved_path_register_parser.set_defaults(func=cmd_build_unobserved_path_register)

    evaluate_stop_rules_parser = subparsers.add_parser(
        "evaluate-stop-rules",
        help="Evaluate stop rules against a seed_to_refinement_report artifact.",
    )
    evaluate_stop_rules_parser.add_argument("--input-refinement-report", required=True, help="Path to seed_to_refinement_report JSON.")
    evaluate_stop_rules_parser.add_argument("--output-json", help="Optional output path for stop rule evaluation JSON.")
    evaluate_stop_rules_parser.add_argument("--output-md", help="Optional output path for stop rule evaluation markdown summary.")
    evaluate_stop_rules_parser.set_defaults(func=cmd_evaluate_stop_rules)

    build_final_slice_proposal_parser = subparsers.add_parser(
        "build-final-slice-proposal",
        help="Build the final planner outputs from stop_rule_evaluator results.",
    )
    build_final_slice_proposal_parser.add_argument("--input-stop-rule-evaluation", required=True, help="Path to stop_rule_evaluation JSON.")
    build_final_slice_proposal_parser.add_argument("--input-path-index", help="Optional path to inventory_path_index JSON.")
    build_final_slice_proposal_parser.add_argument("--output-json", help="Optional output path for final slice proposal JSON.")
    build_final_slice_proposal_parser.add_argument("--output-md", help="Optional output path for final slice proposal markdown summary.")
    build_final_slice_proposal_parser.set_defaults(func=cmd_build_final_slice_proposal)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
