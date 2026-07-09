#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

from PIL import Image


ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.alpha_component_lib import (  # noqa: E402
    DEFAULT_ALPHA_THRESHOLD,
    DEFAULT_MIN_COMPONENTS_FOR_SUCCESS,
    DEFAULT_MIN_PIXELS,
    DEFAULT_PADDING,
    run_alpha_split,
)


@dataclass(frozen=True)
class CorrectionPacket:
    source_image: str
    current_result: str | None
    issues: list[str]
    target_description: str | None
    route: str
    route_reason: str
    recommended_next_tools: list[str]
    recommended_actions: list[str]
    imagegen_prompt: str | None
    notes: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the object-isolation correction worker. "
            "This worker tries alpha connected-components first, then optionally "
            "falls back to ImageSorcery and emits a bounded imagegen request."
        )
    )
    parser.add_argument("--packet-json", required=True, help="Absolute path to a correction packet JSON.")
    parser.add_argument("--output-dir", required=True, help="Absolute path to the bounded worker output directory.")
    parser.add_argument(
        "--alpha-threshold",
        type=int,
        default=DEFAULT_ALPHA_THRESHOLD,
        help="Alpha threshold for foreground detection. Pixels above this value are foreground.",
    )
    parser.add_argument(
        "--min-pixels",
        type=int,
        default=DEFAULT_MIN_PIXELS,
        help="Ignore connected components smaller than this many foreground pixels.",
    )
    parser.add_argument(
        "--padding",
        type=int,
        default=DEFAULT_PADDING,
        help="Padding in pixels around exported crops.",
    )
    parser.add_argument(
        "--min-components-for-success",
        type=int,
        default=DEFAULT_MIN_COMPONENTS_FOR_SUCCESS,
        help="If alpha split finds at least this many components, the split is considered sufficient.",
    )
    parser.add_argument(
        "--imagesorcery-launcher",
        help="Optional launcher path. Defaults to scripts/mcp/start-imagesorcery-mcp.sh under the repo root.",
    )
    parser.add_argument(
        "--skip-alpha-split",
        action="store_true",
        help="Skip alpha connected-components and go directly to the fallback path.",
    )
    parser.add_argument(
        "--skip-imagesorcery-fallback",
        action="store_true",
        help="Skip ImageSorcery fallback even if alpha split is insufficient.",
    )
    return parser.parse_args()


def repo_root_from_script() -> Path:
    return ROOT_DIR


def default_imagesorcery_launcher() -> Path:
    return repo_root_from_script() / "scripts" / "mcp" / "start-imagesorcery-mcp.sh"


def load_packet(packet_json: Path) -> CorrectionPacket:
    data = json.loads(packet_json.read_text(encoding="utf-8"))
    return CorrectionPacket(
        source_image=data["source_image"],
        current_result=data.get("current_result"),
        issues=list(data.get("issues", [])),
        target_description=data.get("target_description"),
        route=data["route"],
        route_reason=data["route_reason"],
        recommended_next_tools=list(data.get("recommended_next_tools", [])),
        recommended_actions=list(data.get("recommended_actions", [])),
        imagegen_prompt=data.get("imagegen_prompt"),
        notes=list(data.get("notes", [])),
    )



def _normalize_tool_result(result: Any) -> Any:
    structured = getattr(result, "structured_content", None)
    if structured not in (None, {}):
        if isinstance(structured, dict) and set(structured.keys()) == {"result"}:
            return structured["result"]
        return structured
    data = getattr(result, "data", None)
    if data is not None:
        if isinstance(data, dict) and set(data.keys()) == {"result"}:
            return data["result"]
        return data
    return result


def _pad_bbox(bbox: list[float] | list[int], width: int, height: int, padding: int) -> list[int]:
    x1, y1, x2, y2 = [int(round(value)) for value in bbox]
    return [
        max(0, x1 - padding),
        max(0, y1 - padding),
        min(width, x2 + padding),
        min(height, y2 + padding),
    ]


async def run_imagesorcery_fallback(
    packet: CorrectionPacket,
    source_image: Path,
    output_dir: Path,
    launcher: Path,
    padding: int,
) -> dict[str, Any]:
    try:
        from fastmcp import Client
        from fastmcp.client.transports import StdioTransport
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "fastmcp is not available in this interpreter. "
            "Run this worker with IMAGESORCERY_PYTHON=<REPO_ROOT>/vendor/mcp/imagesorcery-mcp/{.venv|venv}/bin/python "
            "or another interpreter that has fastmcp installed."
        ) from exc

    fallback_dir = output_dir / "imagesorcery"
    fallback_dir.mkdir(parents=True, exist_ok=True)
    image = Image.open(source_image)
    width, height = image.size

    env = os.environ.copy()
    launcher_command = str(launcher)
    launcher_args: list[str] = []
    if launcher.suffix == ".sh" or not os.access(launcher, os.X_OK):
        launcher_command = "bash"
        launcher_args = [str(launcher)]
    transport = StdioTransport(
        command=launcher_command,
        args=launcher_args,
        env=env,
        cwd=str(repo_root_from_script()),
    )

    async with Client(transport, timeout=120) as client:
        if packet.target_description:
            tool_name = "find"
            call_args: dict[str, Any] = {
                "input_path": str(source_image),
                "description": packet.target_description,
                "confidence": 0.25,
                "model_name": "yoloe-11s-seg.pt",
                "return_all_matches": True,
                "return_geometry": False,
            }
        else:
            tool_name = "detect"
            call_args = {
                "input_path": str(source_image),
                "confidence": 0.25,
                "model_name": "yoloe-11l-seg-pf.pt",
                "return_geometry": True,
                "geometry_format": "mask",
            }

        try:
            tool_result = _normalize_tool_result(await client.call_tool(tool_name, call_args))
        except Exception as exc:
            error_path = fallback_dir / f"{tool_name}_error.txt"
            error_path.write_text(str(exc) + "\n", encoding="utf-8")
            return {
                "attempted": True,
                "tool": tool_name,
                "error": str(exc),
                "error_path": str(error_path),
                "raw_result_path": None,
                "object_count": 0,
                "crops": [],
                "sufficient": False,
            }
        objects = tool_result.get("found_objects") if tool_name == "find" else tool_result.get("detections")
        objects = objects or []
        crops: list[dict[str, Any]] = []

        for index, obj in enumerate(objects[:5], start=1):
            bbox = _pad_bbox(obj["bbox"], width=width, height=height, padding=padding)
            isolate_path = fallback_dir / f"imagesorcery_isolated_{index:02d}.png"
            crop_path = fallback_dir / f"imagesorcery_crop_{index:02d}.png"

            area: dict[str, Any]
            if obj.get("mask_path"):
                area = {"mask_path": obj["mask_path"], "color": None}
            elif obj.get("polygon"):
                area = {"polygon": obj["polygon"], "color": None}
            else:
                area = {
                    "x1": bbox[0],
                    "y1": bbox[1],
                    "x2": bbox[2],
                    "y2": bbox[3],
                    "color": None,
                }

            fill_result = _normalize_tool_result(
                await client.call_tool(
                    "fill",
                    {
                        "input_path": str(source_image),
                        "areas": [area],
                        "invert_areas": True,
                        "output_path": str(isolate_path),
                    },
                )
            )
            crop_result = _normalize_tool_result(
                await client.call_tool(
                    "crop",
                    {
                        "input_path": str(isolate_path),
                        "x1": bbox[0],
                        "y1": bbox[1],
                        "x2": bbox[2],
                        "y2": bbox[3],
                        "output_path": str(crop_path),
                    },
                )
            )
            crops.append(
                {
                    "index": index,
                    "label": obj.get("match") or obj.get("class") or packet.target_description,
                    "confidence": obj.get("confidence"),
                    "bbox": bbox,
                    "mask_path": obj.get("mask_path"),
                    "isolated_path": str(fill_result),
                    "crop_path": str(crop_result),
                }
            )

    raw_result_path = fallback_dir / f"{tool_name}_result.json"
    raw_result_path.write_text(json.dumps(tool_result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "attempted": True,
        "tool": tool_name,
        "raw_result_path": str(raw_result_path),
        "object_count": len(objects),
        "crops": crops,
        "sufficient": bool(crops),
    }


def build_imagegen_request(packet: CorrectionPacket, worker_result: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    if not packet.imagegen_prompt and packet.route not in {"imagegen-first", "hybrid"}:
        return {"written": False}

    request_dir = output_dir / "imagegen"
    request_dir.mkdir(parents=True, exist_ok=True)

    preferred_input = packet.current_result or packet.source_image
    fallback = worker_result.get("imagesorcery_fallback", {})
    crops = fallback.get("crops") or []
    if crops:
        preferred_input = crops[0]["crop_path"]

    prompt = packet.imagegen_prompt or (
        "Use the provided image as the source. Keep only the intended object, preserve identity, "
        "and return a clean transparent-background cutout."
    )
    payload = {
        "preferred_input_image": preferred_input,
        "source_image": packet.source_image,
        "current_result": packet.current_result,
        "route": packet.route,
        "issues": packet.issues,
        "target_description": packet.target_description,
        "prompt": prompt,
        "notes": packet.notes,
    }

    markdown_lines = [
        "# imagegen Correction Request",
        "",
        f"- preferred_input_image: `{preferred_input}`",
        f"- source_image: `{packet.source_image}`",
        f"- current_result: `{packet.current_result or 'n/a'}`",
        f"- route: `{packet.route}`",
        f"- issues: `{', '.join(packet.issues)}`",
        f"- target_description: `{packet.target_description or 'n/a'}`",
        "",
        "## Prompt",
        "",
        f"> {prompt}",
        "",
        "## Notes",
        "",
    ]
    if packet.notes:
        for note in packet.notes:
            markdown_lines.append(f"- {note}")
    else:
        markdown_lines.append("- n/a")

    markdown_path = request_dir / "IMAGEGEN_REQUEST.md"
    json_path = request_dir / "IMAGEGEN_REQUEST.json"
    markdown_path.write_text("\n".join(markdown_lines).rstrip() + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "written": True,
        "markdown_path": str(markdown_path),
        "json_path": str(json_path),
        "preferred_input_image": preferred_input,
    }


def render_report(worker_result: dict[str, Any]) -> str:
    packet = worker_result["packet"]
    alpha = worker_result["alpha_split"]
    fallback = worker_result["imagesorcery_fallback"]
    imagegen = worker_result["imagegen_request"]

    lines = [
        "# Object Isolation Correction Worker Report",
        "",
        "## Inputs",
        "",
        f"- packet_json: `{worker_result['packet_json']}`",
        f"- source_image: `{packet['source_image']}`",
        f"- route: `{packet['route']}`",
        f"- target_description: `{packet['target_description'] or 'n/a'}`",
        f"- issues: `{', '.join(packet['issues'])}`",
        "",
        "## Alpha Split",
        "",
        f"- attempted: `{alpha['attempted']}`",
        f"- sufficient: `{alpha['sufficient']}`",
        f"- reason: {alpha['reason']}",
        f"- component_count: `{alpha.get('component_count', 0)}`",
    ]
    for component in alpha.get("components", []):
        lines.append(
            f"- alpha_component_{component['index']:02d}: bbox=`{component['bbox']}` pixels=`{component['pixel_count']}` path=`{component['output_path']}`"
        )

    lines.extend(["", "## ImageSorcery Fallback", ""])
    lines.append(f"- attempted: `{fallback.get('attempted', False)}`")
    lines.append(f"- sufficient: `{fallback.get('sufficient', False)}`")
    lines.append(f"- tool: `{fallback.get('tool', 'n/a')}`")
    lines.append(f"- object_count: `{fallback.get('object_count', 0)}`")
    if fallback.get("error"):
        lines.append(f"- error: {fallback['error']}")
    if fallback.get("error_path"):
        lines.append(f"- error_path: `{fallback['error_path']}`")
    if fallback.get("raw_result_path"):
        lines.append(f"- raw_result_path: `{fallback['raw_result_path']}`")
    for crop in fallback.get("crops", []):
        lines.append(
            f"- fallback_crop_{crop['index']:02d}: label=`{crop['label']}` confidence=`{crop['confidence']}` bbox=`{crop['bbox']}` crop=`{crop['crop_path']}`"
        )

    lines.extend(["", "## imagegen Request", ""])
    lines.append(f"- written: `{imagegen.get('written', False)}`")
    if imagegen.get("written"):
        lines.append(f"- markdown_path: `{imagegen['markdown_path']}`")
        lines.append(f"- json_path: `{imagegen['json_path']}`")
        lines.append(f"- preferred_input_image: `{imagegen['preferred_input_image']}`")

    return "\n".join(lines).rstrip() + "\n"


async def async_main() -> int:
    args = parse_args()
    packet_json = Path(args.packet_json).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    packet = load_packet(packet_json)

    source_image = Path(packet.source_image).resolve()
    if not source_image.is_file():
        raise SystemExit(f"Source image not found: {source_image}")

    alpha_result: dict[str, Any]
    if args.skip_alpha_split:
        alpha_result = {
            "attempted": False,
            "sufficient": False,
            "reason": "Alpha split was explicitly skipped by the caller.",
            "component_count": 0,
            "components": [],
        }
    else:
        alpha_result = run_alpha_split(
            source_image=source_image,
            output_dir=output_dir,
            alpha_threshold=args.alpha_threshold,
            min_pixels=args.min_pixels,
            padding=args.padding,
            min_components_for_success=args.min_components_for_success,
        )

    fallback_result: dict[str, Any]
    if alpha_result["sufficient"] or args.skip_imagesorcery_fallback:
        fallback_result = {
            "attempted": False,
            "sufficient": False,
            "reason": (
                "Skipped because alpha split was sufficient."
                if alpha_result["sufficient"]
                else "ImageSorcery fallback was explicitly skipped by the caller."
            ),
            "tool": None,
            "object_count": 0,
            "crops": [],
        }
    else:
        launcher = Path(args.imagesorcery_launcher).resolve() if args.imagesorcery_launcher else default_imagesorcery_launcher().resolve()
        if not launcher.is_file():
            raise SystemExit(f"ImageSorcery launcher not found: {launcher}")
        fallback_result = await run_imagesorcery_fallback(
            packet=packet,
            source_image=source_image,
            output_dir=output_dir,
            launcher=launcher,
            padding=args.padding,
        )

    worker_result = {
        "packet_json": str(packet_json),
        "packet": {
            "source_image": packet.source_image,
            "current_result": packet.current_result,
            "issues": packet.issues,
            "target_description": packet.target_description,
            "route": packet.route,
            "route_reason": packet.route_reason,
        },
        "alpha_split": alpha_result,
        "imagesorcery_fallback": fallback_result,
    }
    worker_result["imagegen_request"] = build_imagegen_request(packet, worker_result, output_dir)

    result_json = output_dir / "worker_result.json"
    result_md = output_dir / "worker_report.md"
    result_json.write_text(json.dumps(worker_result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result_md.write_text(render_report(worker_result), encoding="utf-8")
    return 0


def main() -> int:
    return asyncio.run(async_main())


if __name__ == "__main__":
    raise SystemExit(main())
