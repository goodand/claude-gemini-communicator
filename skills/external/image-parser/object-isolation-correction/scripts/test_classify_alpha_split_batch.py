#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from classify_alpha_split_batch import ClassificationRow, build_summary, classify_row_from_worker_result, runtime_path


def test_classify_sufficient() -> None:
    row = classify_row_from_worker_result(
        image_id="dataset:image1.png",
        dataset="dataset",
        image_path=Path("/tmp/image1.png"),
        packet_json_path=Path("/tmp/packet.json"),
        worker_dir=Path("/tmp/worker"),
        worker_result={
            "alpha_split": {
                "sufficient": True,
                "component_count": 3,
                "reason": "Alpha split found 3 component(s) at or above the pixel threshold.",
                "components": [
                    {"output_path": "/tmp/a.png"},
                    {"output_path": "/tmp/b.png"},
                    {"output_path": "/tmp/c.png"},
                ],
                "manifest_path": "/tmp/alpha_components.json",
            }
        },
    )
    assert row.classification == "alpha_split_sufficient"
    assert row.alpha_component_count == 3
    assert row.alpha_manifest_path == "/tmp/alpha_components.json"


def test_classify_single_component_png() -> None:
    row = classify_row_from_worker_result(
        image_id="dataset:image2.png",
        dataset="dataset",
        image_path=Path("/tmp/image2.png"),
        packet_json_path=Path("/tmp/packet.json"),
        worker_dir=Path("/tmp/worker"),
        worker_result={
            "alpha_split": {
                "sufficient": False,
                "component_count": 1,
                "reason": "Alpha split found 1 component(s) at or above the pixel threshold.",
                "components": [{"output_path": "/tmp/a.png"}],
            }
        },
    )
    assert row.classification == "single_component_only"


def test_classify_non_alpha_jpeg() -> None:
    row = classify_row_from_worker_result(
        image_id="dataset:image3.jpeg",
        dataset="dataset",
        image_path=Path("/tmp/image3.jpeg"),
        packet_json_path=Path("/tmp/packet.json"),
        worker_dir=Path("/tmp/worker"),
        worker_result={
            "alpha_split": {
                "sufficient": False,
                "component_count": 1,
                "reason": "Alpha split found 1 component(s) at or above the pixel threshold.",
                "components": [{"output_path": "/tmp/a.png"}],
            }
        },
    )
    assert row.classification == "non_alpha_source_or_opaque_surface"


def test_build_summary_counts() -> None:
    rows = [
        ClassificationRow(
            image_id="a",
            dataset="d1",
            file="a.png",
            source_image_path="/tmp/a.png",
            extension=".png",
            status="completed",
            classification="alpha_split_sufficient",
            alpha_component_count=2,
            alpha_split_sufficient=True,
            alpha_reason="ok",
            packet_json_path="/tmp/p1.json",
            worker_result_path="/tmp/r1.json",
            worker_report_path="/tmp/w1.md",
            alpha_manifest_path="/tmp/m1.json",
            alpha_component_paths=["/tmp/a1.png", "/tmp/a2.png"],
            notes=[],
        ),
        ClassificationRow(
            image_id="b",
            dataset="d2",
            file="b.jpeg",
            source_image_path="/tmp/b.jpeg",
            extension=".jpeg",
            status="completed",
            classification="non_alpha_source_or_opaque_surface",
            alpha_component_count=1,
            alpha_split_sufficient=False,
            alpha_reason="opaque",
            packet_json_path="/tmp/p2.json",
            worker_result_path="/tmp/r2.json",
            worker_report_path="/tmp/w2.md",
            alpha_manifest_path=None,
            alpha_component_paths=[],
            notes=[],
        ),
    ]
    summary = build_summary(rows)
    assert summary["total_images"] == 2
    assert summary["classification_counts"]["alpha_split_sufficient"] == 1
    assert summary["classification_counts"]["non_alpha_source_or_opaque_surface"] == 1
    assert summary["alpha_split_sufficient_images"][0]["image_id"] == "a"


def test_venv_python_path_must_not_be_resolved() -> None:
    worker_python = runtime_path("/repo/vendor/tool/.venv/bin/python")
    assert str(worker_python) == "/repo/vendor/tool/.venv/bin/python"


def main() -> int:
    test_classify_sufficient()
    test_classify_single_component_png()
    test_classify_non_alpha_jpeg()
    test_build_summary_counts()
    test_venv_python_path_must_not_be_resolved()
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
