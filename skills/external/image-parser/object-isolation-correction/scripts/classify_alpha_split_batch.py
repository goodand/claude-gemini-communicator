#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M")


def default_input_root() -> Path:
    return repo_root_from_script() / "control" / "project_domain" / "runs" / "pptx_jobs"


def default_output_root() -> Path:
    return repo_root_from_script() / "control" / "project_domain" / "runs" / "object_isolation" / "alpha_split_batch"


def default_manifest_jsonl() -> Path:
    return repo_root_from_script() / "control" / "project_domain" / "runs" / "manifests" / "phase0_alpha_split_batch_classification_manifest.jsonl"


def default_summary_json() -> Path:
    return repo_root_from_script() / "control" / "project_domain" / "runs" / "manifests" / "phase0_alpha_split_batch_classification_summary.json"


def default_report_md() -> Path:
    return repo_root_from_script() / "control" / "project_domain" / "runs" / "reports" / f"REPORT_phase0_alpha_split_batch_classification-at{timestamp_slug()}.md"


def default_worker_python() -> Path:
    env_python = os.environ.get("IMAGESORCERY_PYTHON")
    if env_python:
        return Path(env_python).expanduser()
    repo_root = repo_root_from_script()
    candidates = [
        repo_root / "vendor" / "mcp" / "imagesorcery-mcp" / ".venv" / "bin" / "python",
        repo_root / "vendor" / "mcp" / "imagesorcery-mcp" / "venv" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def default_worker_script() -> Path:
    return repo_root_from_script() / "skills" / "object-isolation-correction" / "scripts" / "run_object_isolation_correction_worker.py"


def runtime_path(raw: str) -> Path:
    return Path(raw).expanduser()


@dataclass(frozen=True)
class ClassificationRow:
    image_id: str
    dataset: str
    file: str
    source_image_path: str
    extension: str
    status: str
    classification: str
    alpha_component_count: int
    alpha_split_sufficient: bool
    alpha_reason: str
    packet_json_path: str | None
    worker_result_path: str | None
    worker_report_path: str | None
    alpha_manifest_path: str | None
    alpha_component_paths: list[str]
    notes: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the object-isolation correction worker in alpha-split-only mode "
            "across PPT-extracted images and classify which files are already "
            "good candidates for deterministic alpha split."
        )
    )
    parser.add_argument(
        "--input-root",
        default=str(default_input_root()),
        help="Root directory containing pptx_jobs/<dataset>/media/* inputs.",
    )
    parser.add_argument(
        "--output-root",
        default=str(default_output_root()),
        help="Root directory for per-image worker outputs.",
    )
    parser.add_argument(
        "--manifest-jsonl",
        default=str(default_manifest_jsonl()),
        help="JSONL manifest for per-image classification rows.",
    )
    parser.add_argument(
        "--summary-json",
        default=str(default_summary_json()),
        help="Summary JSON output path.",
    )
    parser.add_argument(
        "--report-md",
        default=str(default_report_md()),
        help="Markdown report output path.",
    )
    parser.add_argument(
        "--worker-python",
        default=str(default_worker_python()),
        help="Python interpreter used to run the worker.",
    )
    parser.add_argument(
        "--worker-script",
        default=str(default_worker_script()),
        help="Worker script path.",
    )
    parser.add_argument("--alpha-threshold", type=int, default=1)
    parser.add_argument("--min-pixels", type=int, default=32)
    parser.add_argument("--padding", type=int, default=4)
    parser.add_argument("--min-components-for-success", type=int, default=2)
    parser.add_argument("--limit", type=int, help="Optional max number of images.")
    return parser.parse_args()


def discover_images(input_root: Path) -> list[Path]:
    media_paths = sorted(input_root.glob("*/media/*"))
    return [path.resolve() for path in media_paths if path.is_file()]


def image_id_for(input_root: Path, image_path: Path) -> tuple[str, str]:
    relative = image_path.resolve().relative_to(input_root.resolve())
    dataset = relative.parts[0]
    return dataset, f"{dataset}:{image_path.name}"


def build_packet_payload(image_path: Path) -> dict[str, Any]:
    return {
        "source_image": str(image_path.resolve()),
        "current_result": None,
        "issues": ["split_decision_needed"],
        "target_description": None,
        "route": "imagesorcery-first",
        "route_reason": "Batch alpha-split sufficiency classification only.",
        "recommended_next_tools": [],
        "recommended_actions": [
            "Run alpha connected-components only and classify whether deterministic split is sufficient.",
        ],
        "imagegen_prompt": None,
        "notes": ["batch alpha split classification"],
    }


def classify_row_from_worker_result(
    *,
    image_id: str,
    dataset: str,
    image_path: Path,
    packet_json_path: Path | None,
    worker_dir: Path,
    worker_result: dict[str, Any] | None,
    error: str | None = None,
) -> ClassificationRow:
    if error is not None:
        return ClassificationRow(
            image_id=image_id,
            dataset=dataset,
            file=image_path.name,
            source_image_path=str(image_path),
            extension=image_path.suffix.lower(),
            status="worker_error",
            classification="worker_error",
            alpha_component_count=0,
            alpha_split_sufficient=False,
            alpha_reason=error,
            packet_json_path=str(packet_json_path) if packet_json_path else None,
            worker_result_path=None,
            worker_report_path=None,
            alpha_manifest_path=None,
            alpha_component_paths=[],
            notes=[error],
        )

    alpha = (worker_result or {}).get("alpha_split", {})
    components = alpha.get("components", []) or []
    component_count = int(alpha.get("component_count") or len(components))
    sufficient = bool(alpha.get("sufficient"))

    if sufficient:
        classification = "alpha_split_sufficient"
    elif image_path.suffix.lower() not in {".png", ".webp", ".gif"}:
        classification = "non_alpha_source_or_opaque_surface"
    elif component_count == 0:
        classification = "no_alpha_components"
    elif component_count == 1:
        classification = "single_component_only"
    else:
        classification = "alpha_split_insufficient"

    return ClassificationRow(
        image_id=image_id,
        dataset=dataset,
        file=image_path.name,
        source_image_path=str(image_path),
        extension=image_path.suffix.lower(),
        status="completed",
        classification=classification,
        alpha_component_count=component_count,
        alpha_split_sufficient=sufficient,
        alpha_reason=str(alpha.get("reason") or ""),
        packet_json_path=str(packet_json_path) if packet_json_path else None,
        worker_result_path=str((worker_dir / "worker_result.json").resolve()),
        worker_report_path=str((worker_dir / "worker_report.md").resolve()),
        alpha_manifest_path=alpha.get("manifest_path"),
        alpha_component_paths=[item["output_path"] for item in components if isinstance(item, dict) and item.get("output_path")],
        notes=[],
    )


def write_jsonl(path: Path, rows: list[ClassificationRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(asdict(row), ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def build_summary(rows: list[ClassificationRow]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    datasets: dict[str, int] = {}
    sufficient: list[dict[str, Any]] = []
    for row in rows:
        counts[row.classification] = counts.get(row.classification, 0) + 1
        datasets[row.dataset] = datasets.get(row.dataset, 0) + 1
        if row.classification == "alpha_split_sufficient":
            sufficient.append(
                {
                    "image_id": row.image_id,
                    "source_image_path": row.source_image_path,
                    "alpha_component_count": row.alpha_component_count,
                    "alpha_manifest_path": row.alpha_manifest_path,
                }
            )
    return {
        "experiment": "phase0_alpha_split_batch_classification",
        "saved_at": utc_timestamp(),
        "total_images": len(rows),
        "classification_counts": counts,
        "dataset_counts": datasets,
        "alpha_split_sufficient_images": sufficient,
        "recommended_next_step": (
            "Use the alpha_split_sufficient subset as the only immediate deterministic object-isolation candidate set. "
            "Keep all other images on the full-image + standalone OCR baseline unless a reviewed selection gate is added."
        ),
    }


def render_report(args: argparse.Namespace, rows: list[ClassificationRow], summary: dict[str, Any]) -> str:
    sufficient = [row for row in rows if row.classification == "alpha_split_sufficient"]
    single_component = [row for row in rows if row.classification == "single_component_only"]
    non_alpha = [row for row in rows if row.classification == "non_alpha_source_or_opaque_surface"]
    no_components = [row for row in rows if row.classification == "no_alpha_components"]
    worker_errors = [row for row in rows if row.classification == "worker_error"]

    lines = [
        "# Phase0 Alpha Split Batch Classification Report",
        "",
        "## Purpose",
        "",
        "Classify which PPT-extracted images are already good enough for deterministic alpha split without ImageSorcery fallback.",
        "",
        "## Batch Surface",
        "",
        f"- input_root: `{Path(args.input_root).resolve()}`",
        f"- worker_script: `{Path(args.worker_script).resolve()}`",
        f"- worker_python: `{runtime_path(args.worker_python)}`",
        f"- alpha_threshold: `{args.alpha_threshold}`",
        f"- min_pixels: `{args.min_pixels}`",
        f"- padding: `{args.padding}`",
        f"- min_components_for_success: `{args.min_components_for_success}`",
        "",
        "## Summary",
        "",
        f"- total_images: `{summary['total_images']}`",
    ]
    for key, value in sorted(summary["classification_counts"].items()):
        lines.append(f"- {key}: `{value}`")

    lines.extend(["", "## Alpha-Split-Sufficient Candidates", ""])
    if sufficient:
        for row in sufficient:
            lines.append(
                f"- `{row.image_id}` components=`{row.alpha_component_count}` manifest=`{row.alpha_manifest_path or 'n/a'}`"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Single-Component-Only Cases", ""])
    if single_component:
        for row in single_component[:20]:
            lines.append(f"- `{row.image_id}` reason: {row.alpha_reason}")
    else:
        lines.append("- none")

    lines.extend(["", "## Non-Alpha Or Opaque-Surface Cases", ""])
    if non_alpha:
        for row in non_alpha[:20]:
            lines.append(f"- `{row.image_id}` extension=`{row.extension}` reason: {row.alpha_reason}")
    else:
        lines.append("- none")

    lines.extend(["", "## No-Component Cases", ""])
    if no_components:
        for row in no_components[:20]:
            lines.append(f"- `{row.image_id}` reason: {row.alpha_reason}")
    else:
        lines.append("- none")

    lines.extend(["", "## Worker Errors", ""])
    if worker_errors:
        for row in worker_errors:
            lines.append(f"- `{row.image_id}` error: {row.alpha_reason}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            "- only the `alpha_split_sufficient` subset should move forward as deterministic split candidates",
            "- keep all other images on the full-image + standalone OCR baseline",
            "- do not turn on automatic object-isolation batch fanout for the insufficient subset yet",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def run_worker_for_image(
    *,
    worker_python: Path,
    worker_script: Path,
    image_path: Path,
    worker_dir: Path,
    alpha_threshold: int,
    min_pixels: int,
    padding: int,
    min_components_for_success: int,
) -> tuple[Path, dict[str, Any] | None, str | None]:
    worker_dir.mkdir(parents=True, exist_ok=True)
    packet_json_path = worker_dir / "packet.json"
    packet_json_path.write_text(
        json.dumps(build_packet_payload(image_path), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    command = [
        str(worker_python),
        "-B",
        str(worker_script),
        "--packet-json",
        str(packet_json_path),
        "--output-dir",
        str(worker_dir),
        "--alpha-threshold",
        str(alpha_threshold),
        "--min-pixels",
        str(min_pixels),
        "--padding",
        str(padding),
        "--min-components-for-success",
        str(min_components_for_success),
        "--skip-imagesorcery-fallback",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        error_text = completed.stderr.strip() or completed.stdout.strip() or f"Worker exited with {completed.returncode}"
        (worker_dir / "worker_subprocess_error.txt").write_text(error_text + "\n", encoding="utf-8")
        return packet_json_path, None, error_text
    result_path = worker_dir / "worker_result.json"
    if not result_path.is_file():
        return packet_json_path, None, "worker_result.json was not produced."
    worker_result = json.loads(result_path.read_text(encoding="utf-8"))
    return packet_json_path, worker_result, None


def main() -> int:
    args = parse_args()
    input_root = Path(args.input_root).resolve()
    output_root = Path(args.output_root).resolve() / timestamp_slug()
    manifest_jsonl = Path(args.manifest_jsonl).resolve()
    summary_json = Path(args.summary_json).resolve()
    report_md = Path(args.report_md).resolve()
    worker_python = runtime_path(args.worker_python)
    worker_script = Path(args.worker_script).resolve()

    if not input_root.is_dir():
        raise SystemExit(f"Input root not found: {input_root}")
    if not worker_python.is_file():
        raise SystemExit(f"Worker python not found: {worker_python}")
    if not worker_script.is_file():
        raise SystemExit(f"Worker script not found: {worker_script}")

    images = discover_images(input_root)
    if args.limit is not None:
        images = images[: args.limit]
    if not images:
        raise SystemExit("No input images found.")

    rows: list[ClassificationRow] = []
    for image_path in images:
        dataset, image_id = image_id_for(input_root, image_path)
        worker_dir = output_root / dataset / image_path.stem
        if image_path.suffix.lower() in {".emf", ".wmf", ".svg"}:
            rows.append(
                ClassificationRow(
                    image_id=image_id,
                    dataset=dataset,
                    file=image_path.name,
                    source_image_path=str(image_path),
                    extension=image_path.suffix.lower(),
                    status="skipped",
                    classification="unsupported_source_format",
                    alpha_component_count=0,
                    alpha_split_sufficient=False,
                    alpha_reason="Source format is not routed through the alpha-split worker.",
                    packet_json_path=None,
                    worker_result_path=None,
                    worker_report_path=None,
                    alpha_manifest_path=None,
                    alpha_component_paths=[],
                    notes=[],
                )
            )
            continue

        packet_json_path, worker_result, error = run_worker_for_image(
            worker_python=worker_python,
            worker_script=worker_script,
            image_path=image_path,
            worker_dir=worker_dir,
            alpha_threshold=args.alpha_threshold,
            min_pixels=args.min_pixels,
            padding=args.padding,
            min_components_for_success=args.min_components_for_success,
        )
        rows.append(
            classify_row_from_worker_result(
                image_id=image_id,
                dataset=dataset,
                image_path=image_path,
                packet_json_path=packet_json_path,
                worker_dir=worker_dir,
                worker_result=worker_result,
                error=error,
            )
        )

    summary = build_summary(rows)
    report_text = render_report(args, rows, summary)

    write_jsonl(manifest_jsonl, rows)
    summary_json.parent.mkdir(parents=True, exist_ok=True)
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_md.parent.mkdir(parents=True, exist_ok=True)
    report_md.write_text(report_text, encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "completed",
                "total_images": len(rows),
                "classification_counts": summary["classification_counts"],
                "output_root": str(output_root),
                "manifest_jsonl": str(manifest_jsonl),
                "summary_json": str(summary_json),
                "report_md": str(report_md),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
